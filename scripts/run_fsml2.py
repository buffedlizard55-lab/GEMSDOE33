#!/usr/bin/env python3
"""Run the frozen FSML2-CC campaign end to end (one shot, no retuning).

Order fixed by evidence/fsml2_preregistration_20261026.json:
canaries -> full surfaces + pre-placement uniqueness -> Exp1 screen (budgets
37654/25000) -> variant+budget selection -> Exp2 confirmation -> placement ->
final uniqueness -> writer -> audit -> promotion -> run card.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe33 import analog_invariant, csht_transfer, emission, fsml, grid, promotion  # noqa: E402
from gemsdoe33 import r3_line_localized as llc  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
from vendor.gems24_template.validator import sha256_file  # noqa: E402

PREREG = ROOT / "evidence" / "fsml2_preregistration_20261026.json"
PREREG_SHA = "645e1f6e5c6320e6b60a65af516f06e07baaf85ab34d8fd4a6f1984bad8e7b5c"
MANIFEST = ROOT / "registry" / "focus_rasters_20261026_r3.json"
R2_EVIDENCE = ROOT / "evidence" / "a33_r2_experiment_20261026.json"
OUT = {
    "experiment": ROOT / "evidence" / "fsml2_experiment_20261026.json",
    "uniqueness": ROOT / "evidence" / "fsml2_uniqueness_20261026.json",
    "validator": ROOT / "evidence" / "fsml2_validator_20261026.json",
    "promo_in": ROOT / "evidence" / "fsml2_promotion_evidence_20261026.json",
    "promo_out": ROOT / "evidence" / "fsml2_promotion_assessment_20261026.json",
    "card": ROOT / "evidence" / "fsml2_run_card_20261026.json",
    "docs_card": ROOT / "docs" / "data" / "fsml2_run_card_20261026.json",
}
DATE, EXCL_PX, SPACING = "20261026", 2.0, 2.5
BUDGETS = (37_654, 25_000)
RECORDED_CSHT_SCREEN, RECORDED_CSHT_CONFIRM = 0.13671594852245653, 0.13116926199526852
SCREEN_SPLIT, CONFIRM_SPLIT = "quadrant-buffered-15px-v1", "diagonal-wedge-buffered-20px-confirm-v1"
SEED = 20261026


def _w(p: Path, payload: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def _log(m: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {m}", flush=True)


def _sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _top_set(surface, eligible, k):
    flat = np.flatnonzero(eligible)
    order = np.argsort(-surface.ravel()[flat], kind="mergesort")[:k]
    out = np.zeros(surface.shape, dtype=bool)
    out.ravel()[flat[order]] = True
    return out


def _fold_auc(values_by_fold, folds, *, seed):
    """Two-sided AUC of a fold-built feature: withheld pos vs sampled valid negatives."""
    rng = np.random.default_rng(seed)
    aucs = []
    for vals, fold in zip(values_by_fold, folds):
        pos = np.asarray(vals)[fold["truth"]].ravel()
        neg_ids = np.flatnonzero(fold["valid"] & ~fold["truth"] & ~fold["visible"])
        neg_ids = rng.choice(neg_ids, size=min(neg_ids.size, 3 * pos.size), replace=False)
        neg = np.asarray(vals).ravel()[neg_ids]
        y = np.concatenate([np.ones(pos.size), np.zeros(neg.size)])
        s = np.nan_to_num(np.concatenate([pos, neg]).astype(np.float64), nan=0.0)
        aucs.append(float(roc_auc_score(y, s)))
    return aucs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if OUT["card"].exists() and not args.force:
        raise SystemExit("FSML2-CC already recorded; no rerun or retuning allowed.")
    if sha256_file(PREREG) != PREREG_SHA:
        raise SystemExit("Frozen FSML2 preregistration was modified.")
    started, started_utc = time.monotonic(), datetime.now(timezone.utc).isoformat(timespec="seconds")

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    n_fp = int(footprint.sum())
    l1_arrays = analog_invariant.load_feature_arrays()
    base_arrays, contrast_arrays, hydro_dist, _ = csht_transfer.build_or_load_csht_features(footprint)
    arrays_static = fsml.load_arrays()
    density = fsml.thermal_density(footprint)
    worm = fsml.worm_field(footprint)
    l_line = llc.build_line_evidence(footprint)["l_line"]
    with rasterio.open(ROOT / "data" / "h19_5_nan.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & footprint

    screen = SegmentHoldout(footprint, catalogue, buffer_px=15)
    confirm = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=20)

    # ---- 1 canaries ----
    _log("[1] leakage canaries")
    canary_rows = []
    can = screen.canary({"fsml_thermal_density": density})
    meta = can["features"]["fsml_thermal_density"]
    pooled = float(max(meta["pooled_auc"], 1 - meta["pooled_auc"]))
    max_fold = float(max(max(d["auc"], 1 - d["auc"]) for d in meta["folds"]))
    canary_rows.append({"feature": "fsml_thermal_density", "holdout_auc": max(pooled, max_fold),
                        "max_fold_auc": max_fold, "pooled_auc": pooled, "raw_pooled_auc": float(meta["pooled_auc"]),
                        "split_id": SCREEN_SPLIT, "visible_only": True,
                        "leakage_suspect": bool(meta["leakage_suspected"])})
    _log(f"    thermal_density pooled {pooled:.4f} maxfold {max_fold:.4f}")
    can2 = screen.canary({"fsml2_worm": worm, "r3_l_line": l_line})
    for name in ("fsml2_worm", "r3_l_line"):
        m2 = can2["features"][name]
        p2 = float(max(m2["pooled_auc"], 1 - m2["pooled_auc"]))
        f2 = float(max(max(d["auc"], 1 - d["auc"]) for d in m2["folds"]))
        canary_rows.append({"feature": name, "holdout_auc": max(p2, f2), "max_fold_auc": f2,
                            "pooled_auc": p2, "raw_pooled_auc": float(m2["pooled_auc"]),
                            "split_id": SCREEN_SPLIT, "visible_only": True,
                            "leakage_suspect": bool(m2["leakage_suspected"])})
        _log(f"    {name} pooled {p2:.4f} maxfold {f2:.4f}")
    if not (can["passed"] and can2["passed"]) or any(r["leakage_suspect"] for r in canary_rows):
        _w(OUT["experiment"], {"verdict": "leakage", "canaries": canary_rows})
        raise SystemExit("LEAKAGE CANARY TRIPPED; stopping.")

    # ---- 2 full surfaces + pre-placement uniqueness ----
    _log("[2] full-footprint FSML2 surfaces + surface uniqueness")
    d_full = distance_transform_edt(~catalogue)
    full_elig = footprint & (d_full > EXCL_PX)
    v1_full, v2_full, full_report = fsml.fit_predict_fsml2(
        arrays_static, density, worm, l_line, footprint, catalogue, footprint, seed=SEED + 9999)
    surfaces = {"V1_cc6": v1_full, "V2_cc4": v2_full}
    previews, surface_checks, survivors = {}, {}, []
    for vname, s in surfaces.items():
        prev = _top_set(s, full_elig, BUDGETS[0])
        u = csht_transfer.audit_uniqueness_against_manifest(s, prev, prev, footprint, MANIFEST, root=ROOT)
        previews[vname] = prev
        surface_checks[vname] = dict(u["surface"])
        worst = max(u["surface"]["comparisons"], key=lambda r: r["fraction_candidate_within_3px"])
        _log(f"    {vname}: passed={u['surface']['passed']} worst3px={worst['fraction_candidate_within_3px']:.4f}"
             f" ({worst['registry_id']}) max|rho|={u['surface']['max_abs_spearman_rho']:.4f}")
        if u["surface"]["passed"]:
            survivors.append(vname)
    if not survivors:
        _w(OUT["experiment"], {"verdict": "duplicate", "surface_checks": surface_checks,
                               "canaries": canary_rows, "experiments_run": 0})
        raise SystemExit("All variants duplicate at surface guard; stopping.")

    # ---- 3 Exp1 screen ----
    _log(f"[3] Exp 1/3 screen; survivors={survivors}")
    def bkey(b): return f"@{b}"
    names = ["matched_random", "B1_regional", "H19_5_reference_not_fold_safe"]
    names += [f"A33_R2_CSHT{bkey(b)}" for b in BUDGETS]
    names += [f"{v}{bkey(b)}" for v in survivors for b in BUDGETS]
    preds = {k: [] for k in names}
    fold_reports = []
    for fold in screen.folds:
        f = int(fold["id"])
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        if (train & valid).any() or (visible & fold["truth"]).any():
            raise RuntimeError("leakage invariant violated")
        d_vis = distance_transform_edt(~visible)
        elig = valid & (d_vis > EXCL_PX)
        bud = {b: int(round(b * int(valid.sum()) / n_fp)) for b in BUDGETS}
        rng = np.random.default_rng(SEED + 50 * f)
        preds["matched_random"].append(emission.dot_thin(elig, 2.8, priority=rng.random(footprint.shape),
                                                          max_dots=bud[BUDGETS[0]]).astype(np.uint8))
        reg = analog_invariant.fit_regional_expert(l1_arrays, train, visible, d_vis, seed=20261025 + 100 * f + 1)
        reg_s = analog_invariant.predict(reg, l1_arrays, valid)
        preds["B1_regional"].append(emission.dot_thin(elig, 2.8, priority=reg_s, max_dots=bud[BUDGETS[0]]).astype(np.uint8))
        cb = csht_transfer.fit_csht_models(base_arrays, contrast_arrays, hydro_dist, train, visible, d_vis,
                                           seed=SEED + 1000 * f)
        cs = csht_transfer.predict_csht_surface(cb, base_arrays, contrast_arrays, valid)
        for b in BUDGETS:
            preds[f"A33_R2_CSHT{bkey(b)}"].append(
                csht_transfer.celf_emit_300m(cs, elig, bud[b], min_self_spacing_px=SPACING).astype(np.uint8))
        preds["H19_5_reference_not_fold_safe"].append(emission.dot_thin(h19 & elig, 2.8).astype(np.uint8))
        fv1, fv2, rep = fsml.fit_predict_fsml2(arrays_static, density, worm, l_line, train, visible, valid,
                                               seed=SEED + 2000 * f)
        fold_surfaces = {"V1_cc6": fv1, "V2_cc4": fv2}
        for v in survivors:
            for b in BUDGETS:
                preds[f"{v}{bkey(b)}"].append(
                    csht_transfer.celf_emit_300m(fold_surfaces[v], elig, bud[b], min_self_spacing_px=SPACING).astype(np.uint8))
        fold_reports.append({"fold": fold["name"], "budgets": bud, "eligible": int(elig.sum()),
                             "withheld_positives": int(fold["truth"].sum()), "pu_report": rep,
                             "h19_reference_dots": int(preds["H19_5_reference_not_fold_safe"][-1].sum())})
        _log(f"    fold {fold['name']} done")
    screen_results = {k: screen.summarize(v, ci_draws=1999) for k, v in preds.items()}
    for k, v in screen_results.items():
        _log(f"    SCREEN {k}: HOLDOUT-DTI {v['dti']:.6f} CI {v['ci95']['interval']}")
    selected = max(survivors, key=lambda v: screen_results[f"{v}{bkey(BUDGETS[0])}"]["dti"])
    chosen_budget = (25_000 if screen_results[f"{selected}@25000"]["dti"] > screen_results[f"{selected}@37654"]["dti"]
                     else 37_654)
    sk, ck = f"{selected}{bkey(chosen_budget)}", f"A33_R2_CSHT{bkey(chosen_budget)}"
    screen_vs_csht = screen.compare_paired(preds[sk], preds[ck], ci_draws=1999, seed=SEED)
    screen_vs_b1 = screen.compare_paired(preds[sk], preds["B1_regional"], ci_draws=1999, seed=SEED)
    screen_vs_h19 = screen.compare_paired(preds[sk], preds["H19_5_reference_not_fold_safe"], ci_draws=1999, seed=SEED)
    _log(f"    selected {selected} budget {chosen_budget}: ΔvsCSHT {screen_vs_csht['paired_delta_dti']:+.6f} "
         f"CI {screen_vs_csht['paired_delta_ci95']} wins {screen_vs_csht['fold_wins']}/4")

    # ---- 4 Exp2 confirmation ----
    _log("[4] Exp 2/3 confirmation")
    cpreds = {"B1_regional": [], ck: [], sk: []}
    for fold in confirm.folds:
        f = int(fold["id"])
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        if (train & valid).any() or (visible & fold["truth"]).any():
            raise RuntimeError("leakage invariant violated")
        d_vis = distance_transform_edt(~visible)
        elig = valid & (d_vis > EXCL_PX)
        bud = int(round(chosen_budget * int(valid.sum()) / n_fp))
        reg = analog_invariant.fit_regional_expert(l1_arrays, train, visible, d_vis, seed=SEED + 300 * f + 1)
        reg_s = analog_invariant.predict(reg, l1_arrays, valid)
        cpreds["B1_regional"].append(emission.dot_thin(elig, 2.8, priority=reg_s, max_dots=bud).astype(np.uint8))
        cb = csht_transfer.fit_csht_models(base_arrays, contrast_arrays, hydro_dist, train, visible, d_vis,
                                           seed=SEED + 5000 + 1000 * f)
        cs = csht_transfer.predict_csht_surface(cb, base_arrays, contrast_arrays, valid)
        cpreds[ck].append(csht_transfer.celf_emit_300m(cs, elig, bud, min_self_spacing_px=SPACING).astype(np.uint8))
        fv1, fv2, _ = fsml.fit_predict_fsml2(arrays_static, density, worm, l_line, train, visible, valid,
                                             seed=SEED + 7000 + 2000 * f)
        cpreds[sk].append(csht_transfer.celf_emit_300m({"V1_cc6": fv1, "V2_cc4": fv2}[selected],
                                                       elig, bud, min_self_spacing_px=SPACING).astype(np.uint8))
        _log(f"    fold {fold['name']} done")
    confirm_results = {k: confirm.summarize(v, ci_draws=1999) for k, v in cpreds.items()}
    for k, v in confirm_results.items():
        _log(f"    CONFIRM {k}: HOLDOUT-DTI {v['dti']:.6f} CI {v['ci95']['interval']}")
    confirm_vs_csht = confirm.compare_paired(cpreds[sk], cpreds[ck], ci_draws=1999, seed=SEED)
    confirm_vs_b1 = confirm.compare_paired(cpreds[sk], cpreds["B1_regional"], ci_draws=1999, seed=SEED)

    # ---- 5 placement / uniqueness / writer / promotion ----
    _log("[5] placement, uniqueness, writer, audit")
    s_full = surfaces[selected]
    final = csht_transfer.celf_emit_300m(s_full, full_elig, chosen_budget, min_self_spacing_px=SPACING)
    uniq = csht_transfer.audit_uniqueness_against_manifest(s_full, previews[selected], final, footprint, MANIFEST, root=ROOT)
    screen_best = max(screen_results[ck]["dti"], RECORDED_CSHT_SCREEN, screen_results["B1_regional"]["dti"])
    confirm_best = max(confirm_results[ck]["dti"], RECORDED_CSHT_CONFIRM)
    sci = {
        "screen_beats_best": screen_results[sk]["dti"] > screen_best,
        "screen_ci_vs_csht_positive": bool(screen_vs_csht["ci95_strictly_positive"]),
        "screen_fold_wins_ge3": screen_vs_csht["fold_wins"] >= 3,
        "confirm_beats_best": confirm_results[sk]["dti"] > confirm_best,
        "confirm_ci_vs_csht_positive": bool(confirm_vs_csht["ci95_strictly_positive"]),
        "confirm_fold_wins_ge3": confirm_vs_csht["fold_wins"] >= 3,
        "surface_unique": bool(uniq["surface"]["passed"]),
        "final_dots_unique": bool(uniq["final_dots"]["passed"]),
    }
    prelim = ("duplicate" if not (sci["surface_unique"] and sci["final_dots_unique"])
              else "promote" if all(sci.values()) else "negative")
    note_t = f"GEMS33 FSML2-CC {selected} spyPU+worm+line CELF {chosen_budget}d | {prelim.upper()} | {{cid}}"
    receipt = write_pair(final.astype(np.float32), template=ROOT / "data" / "sample_submission.tif",
                         catalogue=catalogue, footprint=footprint, outdir=ROOT / "docs" / "downloads",
                         family="gemsdoe33", hypothesis=f"fsml2-cc-{chosen_budget}", date=DATE,
                         note_template=note_t, scientific_verdict=prelim)
    cand_sha = receipt["primary_zero_outside"]["sha256"]
    zpath = ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"]
    fmt = audit_submission(zpath, ROOT / "data" / "sample_submission.tif", strict_zero_outside=True)
    uniq["final_dots"]["candidate_sha256"] = cand_sha
    uniq["surface"]["surface_sha256"] = _sha_array(s_full)
    _w(OUT["uniqueness"], uniq)
    _w(OUT["validator"], receipt)

    evaluator_sha = sha256_file(ROOT / "vendor" / "gems24_template" / "holdout.py")
    feat_names = sorted({c for v in fsml.EXPERT_CHANNELS.values() for c in v})
    cache_map = {}
    for k in feat_names:
        for cand in (ROOT / ".cache" / "features" / f"{k}.npy",
                     ROOT / ".cache" / "hydro_features_a33_r2" / f"{k}.npy",
                     ROOT / ".cache" / "fsml_thermal_density.npy",
                     ROOT / ".cache" / "fsml2_worm.npy"):
            if cand.is_file():
                cache_map[k] = sha256_file(cand)
                break
    best_sha = sha256_file(R2_EVIDENCE)
    manifest_entries = json.loads(MANIFEST.read_text())["rasters"]
    elapsed = round(time.monotonic() - started, 2)

    def run_block(res, best, vs, split, extra):
        return {"label": "HOLDOUT-DTI", "evaluator_version": res[sk]["evaluator_version"],
                "evaluator_sha256": evaluator_sha, "candidate_sha256": cand_sha, "baseline_sha256": best_sha,
                "withheld_positives": int(res[sk]["n_withheld_positive_pixels"]),
                "whole_segments_with_buffer": True, "all_catalogue_features_visible_only": True,
                "visible_faults_masked_pixel_exactly": True, "alpha": 0.2, "beta": 0.8,
                "kernel": "triangular", "radius_m": 300,
                "candidate_pooled_dti": float(res[sk]["dti"]), "baseline_pooled_dti": float(best),
                "pooled_delta_ci95": [float(v) for v in vs["paired_delta_ci95"]],
                "ci_estimand": "pooled paired delta", "split_id": split,
                "fold_wins": int(vs["fold_wins"]), "n_folds": int(vs["n_folds"]), **extra}

    promo_in = {
        "candidate_sha256": cand_sha, "current_holdout_best_sha256": best_sha,
        "lane": "GEMSDOE33 FSML2-CC corroboration-count multi-line lane (knowledge/22 + fsml2 preregistration)",
        "shared_template": {
            "source_manifest_sha256": sha256_file(ROOT / "vendor" / "gems24_template" / "SOURCE.json"),
            "feature_cache_sha256": hashlib.sha256(json.dumps(cache_map, sort_keys=True).encode()).hexdigest(),
            "evaluator_sha256": evaluator_sha,
            "writer_sha256": sha256_file(ROOT / "vendor" / "gems24_template" / "submission.py"),
        },
        "screen": run_block(screen_results, screen_best, screen_vs_csht, SCREEN_SPLIT, {}),
        "confirmation": run_block(confirm_results, confirm_best, confirm_vs_csht, CONFIRM_SPLIT,
                                  {"independent_of_screen": True, "frozen_before_screen_results": True}),
        "feature_names": [r["feature"] for r in canary_rows],
        "feature_canaries": [{k: r[k] for k in ("feature", "holdout_auc", "max_fold_auc", "pooled_auc",
                                                 "split_id", "visible_only")} for r in canary_rows],
        "registry_sha256": sha256_file(MANIFEST), "registry_complete": True,
        "registry_raster_sha256s": [e["sha256"] for e in manifest_entries],
        "duplicates": {"surface": {**uniq["surface"], "registry_sha256": sha256_file(MANIFEST)},
                       "final_dots": {**uniq["final_dots"], "registry_sha256": sha256_file(MANIFEST)}},
        "submission_note": receipt["note"], "experiments": 2, "elapsed_seconds": elapsed,
    }
    _w(OUT["promo_in"], promo_in)
    assessment = promotion.assess(promo_in, fmt, cand_sha)
    _w(OUT["promo_out"], assessment)
    verdict = "duplicate" if prelim == "duplicate" else ("promote" if (prelim == "promote" and assessment["eligible_for_selector"]) else "negative")

    def lab(res, k):
        r = res[k]
        return {"label": "HOLDOUT-DTI", "dti": r["dti"], "ci95": r["ci95"]["interval"],
                "withheld_positives": r["n_withheld_positive_pixels"], "evaluator_version": r["evaluator_version"],
                "n_emitted": r["n_emitted"], "folds": [{"fold": x["fold"], "dti": x["dti"]} for x in r["folds"]]}

    card = {
        "schema": 3, "campaign": "FSML2-CC", "hypothesis_id": "FSML2-CC",
        "selected_variant": selected, "selected_budget": chosen_budget,
        "hypothesis": "Corroboration-count fusion over 4 fold-safe spy-PU experts + 2 label-free lines (geopotential worms, scarp line evidence) recovers more withheld fault pixels than in-run A33-R2-CSHT at matched dotted CELF emission, with a surface distinct from prior supervised blends.",
        "mechanism": "Per-fold two-step spy-PU HGB experts on disjoint channel groups; surface = count of lines (of 6, V1_cc6; of 4 PU lines, V2_cc4) with percentile rank>=0.90 plus 0.1*mean-rank; CELF-300m emission, d_visible>2px.",
        "named_non_fault_process_that_could_mimic_it": "Lithologic contacts and buried pediment edges where gravity, magnetic, radiometric and topographic edges coincide without a throughgoing Quaternary fault; Lake Lahontan shoreline complexes.",
        "holdout_dti": {
            "screen": {"split_id": SCREEN_SPLIT, **{k: lab(screen_results, k) for k in screen_results},
                       "paired_vs_csht_matched_budget": screen_vs_csht, "paired_vs_b1": screen_vs_b1,
                       "paired_vs_h19_reference_not_fold_safe": screen_vs_h19},
            "confirmation": {"split_id": CONFIRM_SPLIT, **{k: lab(confirm_results, k) for k in confirm_results},
                             "paired_vs_csht_matched_budget": confirm_vs_csht, "paired_vs_b1": confirm_vs_b1},
            "qualification": "Catalogue hide-and-recover proxy; NOT private expert truth and NOT an organizer score. No leaderboard projection (knowledge/22 section 3).",
        },
        "correlation_overlap_vs_registry": {
            "registry": "registry/focus_rasters_20261026_r3.json (22 rasters)",
            "registry_sha256": sha256_file(MANIFEST),
            "surface_checks_all_variants": {k: {"passed": v["passed"], "max_abs_spearman_rho": v["max_abs_spearman_rho"],
                                                "max_preview_fraction_within_3px": v["max_preview_fraction_within_3px"]}
                                            for k, v in surface_checks.items()},
            "final_dots_passed": uniq["final_dots"]["passed"],
            "final_dots_max_abs_spearman": uniq["final_dots"]["max_abs_spearman_rho"],
            "final_dots_max_3px_overlap": uniq["final_dots"]["max_candidate_fraction_within_3px"],
        },
        "raster_sha256": cand_sha,
        "validator_output": {"format_valid": bool(fmt.get("pass")), "audit": fmt,
                             "predicted_positive_dots": int(final.sum()),
                             "catalogue_overlap_dots": int((final & catalogue).sum())},
        "submission": {"name": receipt["submission_name"], "file": receipt["primary_zero_outside"]["file"],
                       "zip": receipt["primary_zero_outside"]["zip"],
                       "nan_twin": receipt["official_text_nan_outside_twin"]["file"],
                       "note": receipt["note"], "note_characters": receipt["note_characters"],
                       "ok_to_download": bool(fmt.get("pass")),
                       "eligible_for_weekly_selector": verdict == "promote"},
        "scientific_gates": sci, "promotion_assessment": assessment, "verdict": verdict,
        "experiments_run": 2, "experiment_budget": 3, "elapsed_seconds": elapsed, "submission_slots_used": 0,
        "started_utc": started_utc, "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _w(OUT["card"], card)
    _w(OUT["docs_card"], card)
    _w(OUT["experiment"], {"schema": 3, "started_utc": started_utc, "preregistration_sha256": PREREG_SHA,
                           "canaries": canary_rows, "surface_checks": surface_checks,
                           "screen_fold_reports": fold_reports, "screen_results": screen_results,
                           "confirm_results": confirm_results, "selected_variant": selected,
                           "selected_budget": chosen_budget, "full_pu_report": full_report,
                           "verdict": verdict, "elapsed_seconds": elapsed})
    _log(f"DONE verdict={verdict} sha={cand_sha} elapsed={elapsed}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
