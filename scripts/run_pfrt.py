#!/usr/bin/env python3
"""Run frozen PFRT campaign: canaries -> surface guard -> screen -> confirmation -> placement."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, rasterio
from scipy.ndimage import distance_transform_edt
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
from gemsdoe33 import analog_invariant, csht_transfer, emission, grid, pfrt, promotion  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
from vendor.gems24_template.validator import sha256_file  # noqa: E402

PREREG = ROOT / "evidence" / "pfrt_preregistration_20261027.json"
PREREG_SHA = "3ad1002c130d8cf9a9ba24792597a2dae6ea3df58c755496ae8768d4cfc413a7"
MANIFEST = ROOT / "registry" / "focus_rasters_20261026_r3.json"
R2_EVIDENCE = ROOT / "evidence" / "a33_r2_experiment_20261026.json"
OUT = {k: ROOT / "evidence" / f"pfrt_{k}_20261027.json" for k in ("experiment", "uniqueness", "validator", "promotion_evidence", "promotion_assessment", "run_card")}
OUT["docs_card"] = ROOT / "docs" / "data" / "pfrt_run_card_20261027.json"
DATE, EXCL_PX, SPACING, BUDGET, SEED = "20261027", 2.0, 2.5, 37_654, 20261027
SCREEN_SPLIT, CONFIRM_SPLIT = "quadrant-buffered-15px-v1", "diagonal-wedge-buffered-20px-confirm-v1"

def _w(p, payload):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
def _log(m): print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {m}", flush=True)
def _top_set(surface, eligible, k):
    flat = np.flatnonzero(eligible); order = np.argsort(-surface.ravel()[flat], kind="mergesort")[:k]
    out = np.zeros(surface.shape, dtype=bool); out.ravel()[flat[order]] = True; return out

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--force", action="store_true"); args = ap.parse_args()
    if OUT["run_card"].exists() and not args.force: raise SystemExit("PFRT already recorded; no rerun/retuning.")
    if sha256_file(PREREG) != PREREG_SHA: raise SystemExit("Frozen PFRT preregistration modified.")
    t0, started = time.monotonic(), datetime.now(timezone.utc).isoformat(timespec="seconds")
    footprint = grid.template_footprint(); catalogue = grid.load_labels() & footprint; n_fp = int(footprint.sum())
    layers = pfrt.load_layers()
    l1 = analog_invariant.load_feature_arrays()
    base, contrast, hydro_dist, _ = csht_transfer.build_or_load_csht_features(footprint)
    with rasterio.open(grid.DATA / "h19_5_nan.tif") as ds: h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & footprint
    screen = SegmentHoldout(footprint, catalogue, buffer_px=15)
    confirm = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=20)

    _log("[1] canaries + full surface")
    full_surf, full_rep = pfrt.pfrt_surface(layers, footprint)
    feats = {"pfrt_surface": full_surf, "pfrt_depth_gm": np.nan_to_num(layers["depth_gm"], nan=0.0),
             "pfrt_abs_grav_hg": np.abs(np.nan_to_num(layers["grav_hg"], nan=0.0))}
    can = screen.canary(feats); canary_rows = []
    for name, m in can["features"].items():
        pooled = float(max(m["pooled_auc"], 1 - m["pooled_auc"])); mx = float(max(max(d["auc"], 1 - d["auc"]) for d in m["folds"]))
        canary_rows.append({"feature": name, "holdout_auc": max(pooled, mx), "max_fold_auc": mx, "pooled_auc": pooled,
                            "split_id": SCREEN_SPLIT, "visible_only": True, "leakage_suspect": bool(m["leakage_suspected"])})
        _log(f"  {name} pooled2s={pooled:.4f} maxfold2s={mx:.4f}")
    if not can["passed"] or any(r["leakage_suspect"] for r in canary_rows):
        _w(OUT["experiment"], {"verdict": "leakage", "canaries": canary_rows}); raise SystemExit("LEAKAGE CANARY TRIPPED")

    _log("[2] surface uniqueness")
    d_full = distance_transform_edt(~catalogue); full_elig = footprint & (d_full > EXCL_PX)
    preview = _top_set(full_surf, full_elig, BUDGET)
    uniq_pre = csht_transfer.audit_uniqueness_against_manifest(full_surf, preview, preview, footprint, MANIFEST, root=ROOT)
    _log(f"  surface passed={uniq_pre['surface']['passed']} max3px={uniq_pre['surface']['max_preview_fraction_within_3px']:.4f} maxrho={uniq_pre['surface']['max_abs_spearman_rho']:.4f}")
    if not uniq_pre["surface"]["passed"]:
        _w(OUT["experiment"], {"verdict": "duplicate", "canaries": canary_rows, "surface": uniq_pre["surface"], "experiments_run": 0})
        raise SystemExit("PFRT surface duplicate; stopping per protocol.")

    def run_split(holdout, is_confirm):
        preds = {"matched_random": [], "B1_regional": [], "A33_R2_CSHT@37654": [], "PFRT@37654": []}
        if not is_confirm: preds["H19_5_reference_not_fold_safe"] = []
        for fold in holdout.folds:
            f = int(fold["id"]); valid, train, visible = fold["valid"], fold["train"], fold["visible"]
            if (train & valid).any() or (visible & fold["truth"]).any(): raise RuntimeError("leakage invariant")
            d_vis = distance_transform_edt(~visible); elig = valid & (d_vis > EXCL_PX)
            bud = int(round(BUDGET * int(valid.sum()) / n_fp))
            rng = np.random.default_rng(SEED + 50 * f + (9000 if is_confirm else 0))
            preds["matched_random"].append(emission.dot_thin(elig, 2.8, priority=rng.random(footprint.shape), max_dots=bud).astype(np.uint8))
            reg = analog_invariant.fit_regional_expert(l1, train, visible, d_vis, seed=SEED + 100 * f + 1)
            preds["B1_regional"].append(emission.dot_thin(elig, 2.8, priority=analog_invariant.predict(reg, l1, valid), max_dots=bud).astype(np.uint8))
            cb = csht_transfer.fit_csht_models(base, contrast, hydro_dist, train, visible, d_vis, seed=SEED + 1000 * f + (5000 if is_confirm else 0))
            cs = csht_transfer.predict_csht_surface(cb, base, contrast, valid)
            preds["A33_R2_CSHT@37654"].append(csht_transfer.celf_emit_300m(cs, elig, bud, min_self_spacing_px=SPACING).astype(np.uint8))
            ps, rep = pfrt.pfrt_surface(layers, valid)
            preds["PFRT@37654"].append(csht_transfer.celf_emit_300m(ps, elig, bud, min_self_spacing_px=SPACING).astype(np.uint8))
            if not is_confirm: preds["H19_5_reference_not_fold_safe"].append(emission.dot_thin(h19 & elig, 2.8).astype(np.uint8))
            _log(f"  {'confirm' if is_confirm else 'screen'} fold {fold['name']} done crest={rep['n_crest']}")
        return preds

    _log("[3] Exp1 screen"); sp = run_split(screen, False)
    sres = {k: screen.summarize(v, ci_draws=1999) for k, v in sp.items()}
    for k, v in sres.items(): _log(f"  SCREEN {k}: {v['dti']:.6f} CI {v['ci95']['interval']}")
    s_vs = screen.compare_paired(sp["PFRT@37654"], sp["A33_R2_CSHT@37654"], ci_draws=1999, seed=SEED)
    _log("[4] Exp2 confirmation"); cp = run_split(confirm, True)
    cres = {k: confirm.summarize(v, ci_draws=1999) for k, v in cp.items()}
    for k, v in cres.items(): _log(f"  CONFIRM {k}: {v['dti']:.6f} CI {v['ci95']['interval']}")
    c_vs = confirm.compare_paired(cp["PFRT@37654"], cp["A33_R2_CSHT@37654"], ci_draws=1999, seed=SEED)

    _log("[5] placement/uniqueness/writer")
    final = csht_transfer.celf_emit_300m(full_surf, full_elig, BUDGET, min_self_spacing_px=SPACING)
    uniq = csht_transfer.audit_uniqueness_against_manifest(full_surf, preview, final, footprint, MANIFEST, root=ROOT)
    sci = {"screen_beats_csht": sres["PFRT@37654"]["dti"] > sres["A33_R2_CSHT@37654"]["dti"],
           "screen_ci_positive": bool(s_vs["ci95_strictly_positive"]), "screen_fold_wins_ge3": s_vs["fold_wins"] >= 3,
           "confirm_beats_csht": cres["PFRT@37654"]["dti"] > cres["A33_R2_CSHT@37654"]["dti"],
           "confirm_ci_positive": bool(c_vs["ci95_strictly_positive"]), "confirm_fold_wins_ge3": c_vs["fold_wins"] >= 3,
           "surface_unique": bool(uniq["surface"]["passed"]), "final_dots_unique": bool(uniq["final_dots"]["passed"])}
    prelim = "duplicate" if not (sci["surface_unique"] and sci["final_dots_unique"]) else ("promote" if all(sci.values()) else "negative")
    receipt = write_pair(final.astype(np.float32), template=grid.DATA / "sample_submission.tif", catalogue=catalogue,
                         footprint=footprint, outdir=ROOT / "docs" / "downloads", family="gemsdoe33",
                         hypothesis=f"pfrt-listric-{BUDGET}", date=DATE,
                         note_template=f"GEMS33 PFRT listric dip-proj CELF {BUDGET}d | {{cid}} | {prelim.upper()}", scientific_verdict=prelim)
    cand_sha = receipt["primary_zero_outside"]["sha256"]
    fmt = audit_submission(ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"], grid.DATA / "sample_submission.tif", strict_zero_outside=True)
    uniq["final_dots"]["candidate_sha256"] = cand_sha; uniq["surface"]["surface_sha256"] = hashlib.sha256(np.ascontiguousarray(full_surf).tobytes()).hexdigest()
    _w(OUT["uniqueness"], uniq); _w(OUT["validator"], receipt)
    evaluator_sha = sha256_file(ROOT / "vendor" / "gems24_template" / "holdout.py"); best_sha = sha256_file(R2_EVIDENCE)
    elapsed = round(time.monotonic() - t0, 2)
    def block(res, vs, split, extra):
        return {"label": "HOLDOUT-DTI", "evaluator_version": res["PFRT@37654"]["evaluator_version"], "evaluator_sha256": evaluator_sha,
                "candidate_sha256": cand_sha, "baseline_sha256": best_sha, "withheld_positives": int(res["PFRT@37654"]["n_withheld_positive_pixels"]),
                "whole_segments_with_buffer": True, "all_catalogue_features_visible_only": True, "visible_faults_masked_pixel_exactly": True,
                "alpha": 0.2, "beta": 0.8, "kernel": "triangular", "radius_m": 300,
                "candidate_pooled_dti": float(res["PFRT@37654"]["dti"]), "baseline_pooled_dti": float(res["A33_R2_CSHT@37654"]["dti"]),
                "pooled_delta_ci95": [float(v) for v in vs["paired_delta_ci95"]], "ci_estimand": "pooled paired delta",
                "split_id": split, "fold_wins": int(vs["fold_wins"]), "n_folds": int(vs["n_folds"]), **extra}
    cache_map = {n: sha256_file(ROOT / ".cache" / "features" / f"{n}.npy") for n in ("depth_to_base_surf", "depth_to_base_surf_gms2", "iso_grav_anom_hg")}
    promo_in = {"candidate_sha256": cand_sha, "current_holdout_best_sha256": best_sha,
                "lane": "GEMSDOE33 PFRT listric dip-projection lane (knowledge/24 + pfrt preregistration 20261027)",
                "shared_template": {"source_manifest_sha256": sha256_file(ROOT / "vendor" / "gems24_template" / "SOURCE.json"),
                                    "feature_cache_sha256": hashlib.sha256(json.dumps(cache_map, sort_keys=True).encode()).hexdigest(),
                                    "evaluator_sha256": evaluator_sha, "writer_sha256": sha256_file(ROOT / "vendor" / "gems24_template" / "submission.py")},
                "screen": block(sres, s_vs, SCREEN_SPLIT, {}),
                "confirmation": block(cres, c_vs, CONFIRM_SPLIT, {"independent_of_screen": True, "frozen_before_screen_results": True}),
                "feature_names": [r["feature"] for r in canary_rows],
                "feature_canaries": [{k: r[k] for k in ("feature", "holdout_auc", "max_fold_auc", "pooled_auc", "split_id", "visible_only")} for r in canary_rows],
                "registry_sha256": sha256_file(MANIFEST), "registry_complete": True,
                "registry_raster_sha256s": [e["sha256"] for e in json.loads(MANIFEST.read_text())["rasters"]],
                "duplicates": {"surface": {**uniq["surface"], "registry_sha256": sha256_file(MANIFEST)},
                               "final_dots": {**uniq["final_dots"], "registry_sha256": sha256_file(MANIFEST)}},
                "submission_note": receipt["note"], "experiments": 2, "elapsed_seconds": elapsed}
    _w(OUT["promotion_evidence"], promo_in)
    assessment = promotion.assess(promo_in, fmt, cand_sha); _w(OUT["promotion_assessment"], assessment)
    verdict = "duplicate" if prelim == "duplicate" else ("promote" if (prelim == "promote" and assessment["eligible_for_selector"]) else "negative")
    def lab(res, k):
        r = res[k]; return {"label": "HOLDOUT-DTI", "dti": r["dti"], "ci95": r["ci95"]["interval"], "withheld_positives": r["n_withheld_positive_pixels"],
                            "evaluator_version": r["evaluator_version"], "n_emitted": r["n_emitted"], "folds": [{"fold": x["fold"], "dti": x["dti"]} for x in r["folds"]]}
    card = {"schema": 3, "campaign": "PFRT", "hypothesis_id": "PFRT",
            "hypothesis": "Listric dip-projection of basement-edge crests updip by depth*cot(dip) recovers more withheld fault pixels than A33-R2-CSHT at matched CELF emission, on a surface distinct from prior unshifted gradient classifiers.",
            "mechanism": "Label-free: edge=sqrt(rank(depth_to_base_surf_gms2)*rank(|iso_grav_anom_hg|)); crests (NMS, rank>=0.90) splatted at updip projections for dip 50/60deg, offset clip [1,10]px; gaussian sigma1; CELF-300m, d_visible>2px, 37654 dots.",
            "named_non_fault_mimic": "Prograding alluvial-fan toes and buried pediment edges displacing basement/gravity breaks updip without a throughgoing Quaternary fault.",
            "holdout_dti": {"screen": {"split_id": SCREEN_SPLIT, **{k: lab(sres, k) for k in sres}, "paired_vs_csht": s_vs},
                            "confirmation": {"split_id": CONFIRM_SPLIT, **{k: lab(cres, k) for k in cres}, "paired_vs_csht": c_vs},
                            "qualification": "Catalogue hide-and-recover proxy; NOT private expert truth, NOT an organizer score. No leaderboard projection (knowledge/22 s3)."},
            "correlation_overlap_vs_registry": {"registry": "registry/focus_rasters_20261026_r3.json (22 rasters)", "registry_sha256": sha256_file(MANIFEST),
                                                "surface_passed": uniq["surface"]["passed"], "surface_max_abs_spearman": uniq["surface"]["max_abs_spearman_rho"],
                                                "surface_max_3px": uniq["surface"]["max_preview_fraction_within_3px"],
                                                "final_dots_passed": uniq["final_dots"]["passed"], "final_dots_max_abs_spearman": uniq["final_dots"]["max_abs_spearman_rho"],
                                                "final_dots_max_3px": uniq["final_dots"]["max_candidate_fraction_within_3px"]},
            "raster_sha256": cand_sha,
            "validator_output": {"format_valid": bool(fmt.get("pass")), "audit": fmt, "predicted_positive_dots": int(final.sum()), "catalogue_overlap_dots": int((final & catalogue).sum())},
            "submission": {"name": receipt["submission_name"], "file": receipt["primary_zero_outside"]["file"], "zip": receipt["primary_zero_outside"]["zip"],
                           "nan_twin": receipt["official_text_nan_outside_twin"]["file"], "note": receipt["note"], "note_characters": receipt["note_characters"],
                           "ok_to_download": bool(fmt.get("pass")), "eligible_for_weekly_selector": verdict == "promote"},
            "scientific_gates": sci, "promotion_assessment": assessment, "verdict": verdict,
            "experiments_run": 2, "experiment_budget": 3, "elapsed_seconds": elapsed, "submission_slots_used": 0,
            "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    _w(OUT["run_card"], card); _w(OUT["docs_card"], card)
    _w(OUT["experiment"], {"schema": 3, "preregistration_sha256": PREREG_SHA, "canaries": canary_rows, "full_surface_report": full_rep,
                           "screen_results": sres, "confirm_results": cres, "verdict": verdict, "elapsed_seconds": elapsed})
    _log(f"DONE verdict={verdict} sha={cand_sha} elapsed={elapsed}s")
    return 0

if __name__ == "__main__": raise SystemExit(main())
