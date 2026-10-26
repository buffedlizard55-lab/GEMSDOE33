#!/usr/bin/env python3
"""Run the frozen A33-R3-LLC campaign end to end (one shot, no retuning).

Order of operations is fixed by ``evidence/a33_r3_preregistration_20261026.json``:
canaries -> pre-placement surface uniqueness -> Exp 1 screen -> variant selection ->
Exp 2 confirmation -> full placement -> final-dot uniqueness -> writer -> format audit ->
promotion assessment -> run card. Shared evaluator (vendor/gems24_template/holdout.py),
CSHT models, CELF placement and writer are reused unchanged. No DrivenData access.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe33 import analog_invariant, csht_transfer, emission, grid, promotion  # noqa: E402
from gemsdoe33 import r3_line_localized as llc  # noqa: E402
from submission_writer import write_pair  # noqa: E402  (scripts/submission_writer.py)
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
from vendor.gems24_template.validator import sha256_file  # noqa: E402

PREREG = ROOT / "evidence" / "a33_r3_preregistration_20261026.json"
PREREG_SHA = "79e7564bc0ee08d8216442ff8ae1be3291d6abe389db6d8758f4e963c39a18c8"
MANIFEST = ROOT / "registry" / "focus_rasters_20261026_r3.json"
R2_EVIDENCE = ROOT / "evidence" / "a33_r2_experiment_20261026.json"
OUT = {
    "experiment": ROOT / "evidence" / "a33_r3_experiment_20261026.json",
    "uniqueness": ROOT / "evidence" / "a33_r3_uniqueness_20261026.json",
    "validator": ROOT / "evidence" / "a33_r3_validator_20261026.json",
    "promo_in": ROOT / "evidence" / "a33_r3_promotion_evidence_20261026.json",
    "promo_out": ROOT / "evidence" / "a33_r3_promotion_assessment_20261026.json",
    "card": ROOT / "evidence" / "a33_r3_run_card_20261026.json",
    "docs_card": ROOT / "docs" / "data" / "a33_r3_run_card_20261026.json",
}
DATE = "20261026"
BUDGET = 37_654
EXCL_PX = 2.0
SPACING = 2.5
RECORDED_CSHT_SCREEN = 0.13671594852245653
RECORDED_CSHT_CONFIRM = 0.13116926199526852  # evidence/a33_r2_experiment_20261026.json confirm_results
VARIANTS = {"V1_gamma1": 1.0, "V2_gamma05": 0.5}
SCREEN_SPLIT = "quadrant-buffered-15px-v1"
CONFIRM_SPLIT = "diagonal-wedge-buffered-20px-confirm-v1"
CACHE = ROOT / ".cache" / "r3"


def _w(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)


def _sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _top_level_set(surface: np.ndarray, eligible: np.ndarray, k: int) -> np.ndarray:
    flat = np.flatnonzero(eligible)
    order = np.argsort(-surface.ravel()[flat], kind="mergesort")[:k]
    out = np.zeros(surface.shape, dtype=bool)
    out.ravel()[flat[order]] = True
    return out


def _h19_reference(h19: np.ndarray, eligible: np.ndarray) -> np.ndarray:
    """Informational, NOT fold-safe: fixed external H19-5 ridge cells, B2-style emission per fold."""
    return emission.dot_thin(h19 & eligible, 2.8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="allow rerun only after a crash (logged)")
    args = ap.parse_args()
    if OUT["card"].exists() and not args.force:
        raise SystemExit("A33-R3 already recorded; no rerun or retuning allowed.")
    if sha256_file(PREREG) != PREREG_SHA:
        raise SystemExit("Frozen A33-R3 preregistration was modified.")
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    CACHE.mkdir(parents=True, exist_ok=True)

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    n_fp = int(footprint.sum())
    l1_arrays = analog_invariant.load_feature_arrays()
    base_arrays, contrast_arrays, hydro_dist, _seed_meta = csht_transfer.build_or_load_csht_features(footprint)
    with rasterio.open(ROOT / "data" / "h19_5_nan.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & footprint

    _log("line evidence (label-free)")
    lines = llc.build_line_evidence(footprint)
    l_line = lines["l_line"]
    line_digest = _sha_array(l_line)

    screen = SegmentHoldout(footprint, catalogue, buffer_px=15)
    confirm = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=20)

    # ---- Step 1: leakage canaries on every new channel alone --------------------------------
    _log("[1] leakage canaries")
    canary_features = {
        "r3_e_lid": lines["e_lid"], "r3_e_void": lines["e_void"],
        "r3_ridge_rank": lines["ridge_rank"], "r3_oli_rank": lines["oli_rank"],
        "r3_l_line": l_line,
    }
    can = screen.canary(canary_features)
    canary_rows = []
    for name, meta in can["features"].items():
        max_fold = float(max(max(d["auc"], 1 - d["auc"]) for d in meta["folds"]))
        pooled = float(max(meta["pooled_auc"], 1 - meta["pooled_auc"]))
        canary_rows.append({"feature": name, "holdout_auc": max(max_fold, pooled), "max_fold_auc": max_fold,
                            "pooled_auc": pooled, "raw_pooled_auc": float(meta["pooled_auc"]),
                            "split_id": SCREEN_SPLIT, "visible_only": True,
                            "leakage_suspect": bool(meta["leakage_suspected"])})
        _log(f"    {name}: pooled two-sided AUC {pooled:.4f}, max fold {max_fold:.4f}")
    if not can["passed"]:
        _w(OUT["experiment"], {"verdict": "leakage", "canaries": canary_rows})
        raise SystemExit("LEAKAGE CANARY TRIPPED; stopping.")

    # ---- Step 2: full-footprint surfaces + pre-placement uniqueness -------------------------
    _log("[2] full-footprint CSHT prior + pre-placement surface uniqueness")
    d_full = distance_transform_edt(~catalogue)
    full_elig = footprint & (d_full > EXCL_PX)
    full_bundle = csht_transfer.fit_csht_models(base_arrays, contrast_arrays, hydro_dist, footprint,
                                                catalogue, d_full, seed=20261026 + 9999)
    p_full = csht_transfer.predict_csht_surface(full_bundle, base_arrays, contrast_arrays, footprint)
    surfaces, previews, surface_checks, survivors = {}, {}, {}, []
    for vname, gamma in VARIANTS.items():
        s = llc.fuse(p_full, l_line, footprint, gamma)
        prev = _top_level_set(s, full_elig, BUDGET)
        u = csht_transfer.audit_uniqueness_against_manifest(s, prev, prev, footprint, MANIFEST, root=ROOT)
        surfaces[vname], previews[vname] = s, prev
        surface_checks[vname] = dict(u["surface"])
        worst = max(surface_checks[vname]["comparisons"], key=lambda r: r["fraction_candidate_within_3px"])
        _log(f"    {vname}: surface passed={u['surface']['passed']} worst 3px={worst['fraction_candidate_within_3px']:.4f} "
             f"({worst['registry_id']}), max|rho|={u['surface']['max_abs_spearman_rho']:.4f}")
        if u["surface"]["passed"]:
            survivors.append(vname)
    if not survivors:
        _w(OUT["experiment"], {"verdict": "duplicate", "surface_checks": surface_checks,
                               "canaries": canary_rows, "experiments_run": 0})
        raise SystemExit("All variants failed the pre-placement surface duplicate guard; stopping.")

    # ---- Step 3: Experiment 1/3 screen -------------------------------------------------------
    _log(f"[3] Exp 1/3 screen {SCREEN_SPLIT}; survivors={survivors}")
    names = ["matched_random", "B1_regional", "A33_R2_CSHT", "H19_5_reference_not_fold_safe"] + survivors
    preds = {k: [] for k in names}
    fold_reports = []
    for fold in screen.folds:
        f = int(fold["id"])
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        if (train & valid).any() or (visible & fold["truth"]).any():
            raise RuntimeError("leakage invariant violated")
        d_vis = distance_transform_edt(~visible)
        elig = valid & (d_vis > EXCL_PX)
        budget = int(round(BUDGET * int(valid.sum()) / n_fp))
        rng = np.random.default_rng(20261026 + 50 * f)
        preds["matched_random"].append(emission.dot_thin(elig, 2.8, priority=rng.random(footprint.shape),
                                                         max_dots=budget).astype(np.uint8))
        reg = analog_invariant.fit_regional_expert(l1_arrays, train, visible, d_vis, seed=20261025 + 100 * f + 1)
        reg_s = analog_invariant.predict(reg, l1_arrays, valid)
        preds["B1_regional"].append(emission.dot_thin(elig, 2.8, priority=reg_s, max_dots=budget).astype(np.uint8))
        cb = csht_transfer.fit_csht_models(base_arrays, contrast_arrays, hydro_dist, train, visible, d_vis,
                                           seed=20261026 + 1000 * f)
        cs = csht_transfer.predict_csht_surface(cb, base_arrays, contrast_arrays, valid)
        preds["A33_R2_CSHT"].append(csht_transfer.celf_emit_300m(cs, elig, budget, min_self_spacing_px=SPACING).astype(np.uint8))
        preds["H19_5_reference_not_fold_safe"].append(_h19_reference(h19, elig).astype(np.uint8))
        for vname in survivors:
            sv = llc.fuse(cs, l_line, valid, VARIANTS[vname])
            preds[vname].append(csht_transfer.celf_emit_300m(sv, elig, budget, min_self_spacing_px=SPACING).astype(np.uint8))
        fold_reports.append({"fold": fold["name"], "budget": budget, "eligible": int(elig.sum()),
                             "withheld_positives": int(fold["truth"].sum()),
                             "h19_reference_dots": int(preds["H19_5_reference_not_fold_safe"][-1].sum())})
        _log(f"    fold {fold['name']} done (budget {budget})")
    screen_results = {k: screen.summarize(v, ci_draws=1999) for k, v in preds.items()}
    for k, v in screen_results.items():
        _log(f"    SCREEN {k}: HOLDOUT-DTI {v['dti']:.6f} CI {v['ci95']['interval']}")
    selected = max(survivors, key=lambda k: screen_results[k]["dti"])
    screen_vs_csht = screen.compare_paired(preds[selected], preds["A33_R2_CSHT"], ci_draws=1999, seed=20261026)
    screen_vs_b1 = screen.compare_paired(preds[selected], preds["B1_regional"], ci_draws=1999, seed=20261026)
    screen_vs_h19 = screen.compare_paired(preds[selected], preds["H19_5_reference_not_fold_safe"], ci_draws=1999, seed=20261026)
    _log(f"    selected {selected}: delta vs CSHT {screen_vs_csht['paired_delta_dti']:+.6f} "
         f"CI {screen_vs_csht['paired_delta_ci95']} wins {screen_vs_csht['fold_wins']}/4")

    # ---- Step 4: Experiment 2/3 confirmation -------------------------------------------------
    _log(f"[4] Exp 2/3 confirmation {CONFIRM_SPLIT}")
    cpreds = {"B1_regional": [], "A33_R2_CSHT": [], selected: []}
    for fold in confirm.folds:
        f = int(fold["id"])
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        if (train & valid).any() or (visible & fold["truth"]).any():
            raise RuntimeError("leakage invariant violated")
        d_vis = distance_transform_edt(~visible)
        elig = valid & (d_vis > EXCL_PX)
        budget = int(round(BUDGET * int(valid.sum()) / n_fp))
        reg = analog_invariant.fit_regional_expert(l1_arrays, train, visible, d_vis, seed=20261026 + 300 * f + 1)
        reg_s = analog_invariant.predict(reg, l1_arrays, valid)
        cpreds["B1_regional"].append(emission.dot_thin(elig, 2.8, priority=reg_s, max_dots=budget).astype(np.uint8))
        cb = csht_transfer.fit_csht_models(base_arrays, contrast_arrays, hydro_dist, train, visible, d_vis,
                                           seed=20261026 + 5000 + 1000 * f)
        cs = csht_transfer.predict_csht_surface(cb, base_arrays, contrast_arrays, valid)
        cpreds["A33_R2_CSHT"].append(csht_transfer.celf_emit_300m(cs, elig, budget, min_self_spacing_px=SPACING).astype(np.uint8))
        sv = llc.fuse(cs, l_line, valid, VARIANTS[selected])
        cpreds[selected].append(csht_transfer.celf_emit_300m(sv, elig, budget, min_self_spacing_px=SPACING).astype(np.uint8))
        _log(f"    fold {fold['name']} done")
    confirm_results = {k: confirm.summarize(v, ci_draws=1999) for k, v in cpreds.items()}
    for k, v in confirm_results.items():
        _log(f"    CONFIRM {k}: HOLDOUT-DTI {v['dti']:.6f} CI {v['ci95']['interval']}")
    confirm_vs_csht = confirm.compare_paired(cpreds[selected], cpreds["A33_R2_CSHT"], ci_draws=1999, seed=20261026)
    confirm_vs_b1 = confirm.compare_paired(cpreds[selected], cpreds["B1_regional"], ci_draws=1999, seed=20261026)

    # ---- Step 5: final placement, uniqueness, writer, format, promotion ----------------------
    _log("[5] full placement, final-dot uniqueness, writer, audit")
    s_full = surfaces[selected]
    final = csht_transfer.celf_emit_300m(s_full, full_elig, BUDGET, min_self_spacing_px=SPACING)
    uniq = csht_transfer.audit_uniqueness_against_manifest(s_full, previews[selected], final, footprint,
                                                           MANIFEST, root=ROOT)
    screen_best = max(screen_results["A33_R2_CSHT"]["dti"], RECORDED_CSHT_SCREEN, screen_results["B1_regional"]["dti"])
    confirm_best = max(confirm_results["A33_R2_CSHT"]["dti"], RECORDED_CSHT_CONFIRM)
    sci = {
        "screen_beats_best": screen_results[selected]["dti"] > screen_best,
        "screen_ci_vs_csht_positive": bool(screen_vs_csht["ci95_strictly_positive"]),
        "screen_fold_wins_ge3": screen_vs_csht["fold_wins"] >= 3,
        "confirm_beats_best": confirm_results[selected]["dti"] > confirm_best,
        "confirm_ci_vs_csht_positive": bool(confirm_vs_csht["ci95_strictly_positive"]),
        "confirm_fold_wins_ge3": confirm_vs_csht["fold_wins"] >= 3,
        "surface_unique": bool(uniq["surface"]["passed"]),
        "final_dots_unique": bool(uniq["final_dots"]["passed"]),
    }
    prelim = ("duplicate" if not (sci["surface_unique"] and sci["final_dots_unique"])
              else "promote" if all(sci.values()) else "negative")
    note_t = f"GEMS33 A33-R3-LLC {selected}: scarp line-integral x CSHT prior, CELF300 37654d | {prelim.upper()} | {{cid}}"
    receipt = write_pair(final.astype(np.float32), template=ROOT / "data" / "sample_submission.tif",
                         catalogue=catalogue, footprint=footprint, outdir=ROOT / "docs" / "downloads",
                         family="gemsdoe33", hypothesis="a33-r3-llc-37654", date=DATE,
                         note_template=note_t, scientific_verdict=prelim)
    cand_sha = receipt["primary_zero_outside"]["sha256"]
    zpath = ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"]
    fmt = audit_submission(zpath, ROOT / "data" / "sample_submission.tif", strict_zero_outside=True)
    uniq["final_dots"]["candidate_sha256"] = cand_sha
    uniq["surface"]["surface_sha256"] = _sha_array(s_full)
    _w(OUT["uniqueness"], uniq)
    _w(OUT["validator"], receipt)

    evaluator_sha = sha256_file(ROOT / "vendor" / "gems24_template" / "holdout.py")
    feat_names = sorted(set(csht_transfer.CACHED_FEATURE_NAMES) | set(llc.LIDAR_EVIDENCE_BANDS) | {"lid_valid", llc.VOID_EVIDENCE_BAND})
    cache_map = {k: sha256_file(ROOT / ".cache" / "features" / f"{k}.npy") for k in feat_names}
    cache_map["r3_l_line_array"] = line_digest
    best_sha = sha256_file(R2_EVIDENCE)
    manifest_entries = json.loads(MANIFEST.read_text())["rasters"]
    elapsed = round(time.monotonic() - started, 2)

    def run_block(res, best, vs, split, extra):
        return {"label": "HOLDOUT-DTI", "evaluator_version": res[selected]["evaluator_version"],
                "evaluator_sha256": evaluator_sha, "candidate_sha256": cand_sha, "baseline_sha256": best_sha,
                "withheld_positives": int(res[selected]["n_withheld_positive_pixels"]),
                "whole_segments_with_buffer": True, "all_catalogue_features_visible_only": True,
                "visible_faults_masked_pixel_exactly": True, "alpha": 0.2, "beta": 0.8,
                "kernel": "triangular", "radius_m": 300,
                "candidate_pooled_dti": float(res[selected]["dti"]), "baseline_pooled_dti": float(best),
                "pooled_delta_ci95": [float(v) for v in vs["paired_delta_ci95"]],
                "ci_estimand": "pooled paired delta", "split_id": split,
                "fold_wins": int(vs["fold_wins"]), "n_folds": int(vs["n_folds"]), **extra}

    promo_in = {
        "candidate_sha256": cand_sha, "current_holdout_best_sha256": best_sha,
        "lane": "GEMSDOE33 analog-field / cover-stratified hydrothermal transfer lane (A33-R3-LLC)",
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
        "schema": 3, "campaign": "A33-R3", "hypothesis_id": "A33-R3-LLC", "selected_variant": selected,
        "hypothesis": "Line-localising the fold-trained CSHT cover/hydrothermal prior with label-free, strike-integrated "
                      "1 m LiDAR (or 100 m slope in LiDAR voids) scarp ridges places dots on traces and recovers more "
                      "withheld fault pixels than CSHT at a matched 37,654-dot budget.",
        "mechanism": "S = rank(P_csht)^gamma x L_line; L_line = within-regime rank of a 12-azimuth anisotropic (500 m x 75 m) "
                     "line integral of multi-scale Hessian ridge strength of scarp evidence, 1-px NMS; CELF-300m placement.",
        "named_non_fault_process_that_could_mimic_it": "Pluvial Lake Lahontan wave-cut shorelines/beach ridges (~1318-1341 m), "
                                                         "fluvial terrace risers and linear anthropogenic cuts (roads/canals).",
        "holdout_dti": {
            "screen": {"split_id": SCREEN_SPLIT, **{k: lab(screen_results, k) for k in screen_results},
                       "paired_vs_csht": screen_vs_csht, "paired_vs_b1": screen_vs_b1,
                       "paired_vs_h19_reference_not_fold_safe": screen_vs_h19},
            "confirmation": {"split_id": CONFIRM_SPLIT, **{k: lab(confirm_results, k) for k in confirm_results},
                             "paired_vs_csht": confirm_vs_csht, "paired_vs_b1": confirm_vs_b1},
            "qualification": "Catalogue hide-and-recover proxy; NOT private expert truth and NOT an organizer score.",
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
                           "line_evidence_sha256": line_digest,
                           "regime_cells": {"lidar": int(lines["lid"].sum()), "void": int(lines["void"].sum())},
                           "verdict": verdict, "elapsed_seconds": elapsed})
    _log(f"DONE verdict={verdict} sha={cand_sha} elapsed={elapsed}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
