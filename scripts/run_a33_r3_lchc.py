#!/usr/bin/env python3
"""Run the one frozen A33-R3-LCHC (Least-Cost Hydrothermal Connectivity) experiment.

Reuses the shared evaluator/writer/validator exactly as A33-R2-CSHT did (no private fork);
see evidence/a33_r3_lchc_preregistration_20261026.json for the frozen method paragraph,
decision rule and budget. This script performs no DrivenData upload and cannot spend a
weekly slot; it only ever writes a research/candidate GeoTIFF to docs/downloads/.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe33 import analog_invariant, csht_transfer, grid, lchc, promotion  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
from vendor.gems24_template.validator import sha256_file  # noqa: E402

PREREG = ROOT / "evidence" / "a33_r3_lchc_preregistration_20261026.json"
PREREG_SHA = "bc4ecef34e3b81e19f41c9422fba60d99ed4c8a6c06eadb4617198753dd63a6e"
MANIFEST = ROOT / "registry" / "focus_rasters_20261026.json"
MANIFEST_SHA = "6e71453c77dd4b2bbb5f1d7e36db74f6641f9a47f6ecfb87b099db21ea8f1500"

EVIDENCE = ROOT / "evidence" / "a33_r3_lchc_experiment_20261026.json"
UNIQUENESS = ROOT / "evidence" / "a33_r3_lchc_uniqueness_20261026.json"
VALIDATOR = ROOT / "evidence" / "a33_r3_lchc_validator_20261026.json"
PROMO_INPUT = ROOT / "evidence" / "a33_r3_lchc_promotion_evidence_20261026.json"
PROMO_ASSESS = ROOT / "evidence" / "a33_r3_lchc_promotion_assessment_20261026.json"
RUN_CARD = ROOT / "evidence" / "a33_r3_lchc_run_card_20261026.json"
DOCS_CARD = ROOT / "docs" / "data" / "a33_r3_lchc_run_card_20261026.json"

DATE = "20261026"
FULL_DOT_BUDGET = 37_654  # matched to every prior lane comparison in this repo
MIN_SPACING_PX = 2.5
CATALOGUE_EXCLUSION_PX = 2.0
SCREEN_BUFFER_PX = 15
CONFIRM_BUFFER_PX = 20
RECORDED_B1_REGIONAL = 0.11324405875705776  # same recorded A33-L1 ceiling used by A33-R2-CSHT

CANARY_SOURCE_NAMES = (
    "cond_surf", "cond_surf_gms2", "iso_grav_anom_hg", "iso_grav_anom_slope",
    "geod_shearrate", "geod_dilaterate", "depth_to_base_surf",
    "lid_coh100", "lid_relief", "tmi_hg",
)


def _json_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def _verify_preregistration() -> None:
    actual = sha256_file(PREREG)
    if actual != PREREG_SHA:
        raise SystemExit(f"Frozen A33-R3 preregistration changed: {actual} != {PREREG_SHA}")
    actual_manifest = sha256_file(MANIFEST)
    if actual_manifest != MANIFEST_SHA:
        raise SystemExit(f"Pinned 21-raster manifest modified: {actual_manifest} != {MANIFEST_SHA}")


def _restore_registry() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "fetch_focus_registry.py"),
         "--manifest", str(MANIFEST)],
        cwd=ROOT, check=True,
    )


def _emit(score: np.ndarray, eligible: np.ndarray, budget: int) -> np.ndarray:
    dots = csht_transfer.celf_emit_300m(score, eligible, budget, min_self_spacing_px=MIN_SPACING_PX)
    if int(dots.sum()) != budget:
        raise RuntimeError(f"Emission underfilled: {int(dots.sum())} != {budget}")
    return dots


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    if EVIDENCE.exists() or RUN_CARD.exists():
        raise SystemExit("A33-R3-LCHC is already recorded; no rerun/post-hoc tuning allowed.")
    _verify_preregistration()

    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _restore_registry()

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    l1_arrays = analog_invariant.load_feature_arrays()

    print("[0/6] Loading catalogue-free thermal/volcanic seeds (DOE GDR #1391)", flush=True)
    thermal_seed, vent_seed, seed_meta = csht_transfer.load_thermal_vent_seeds(footprint)
    seed_mask = thermal_seed | vent_seed
    print(f"      {seed_meta}", flush=True)

    screen_holdout = SegmentHoldout(footprint, catalogue, buffer_px=SCREEN_BUFFER_PX)
    confirm_holdout = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=CONFIRM_BUFFER_PX)

    # 1. Per-feature leakage canary (cost/corroboration/basement-edge inputs + final surface)
    print("[1/6] Leakage canaries for 10 LCHC source channels + 1 derived basement edge", flush=True)
    canary_arrays = {name: np.asarray(np.load(ROOT / ".cache" / "features" / f"{name}.npy"))
                      for name in CANARY_SOURCE_NAMES}
    canary_arrays["basement_edge"] = lchc.basement_structure_edge(canary_arrays["depth_to_base_surf"], footprint)
    canary_bundle = screen_holdout.canary(canary_arrays)
    canary_rows = []
    for fname, fmeta in canary_bundle["features"].items():
        max_f = float(max(max(d["auc"], 1.0 - d["auc"]) for d in fmeta["folds"]))
        two_sided_pooled = float(max(fmeta["pooled_auc"], 1.0 - fmeta["pooled_auc"]))
        canary_rows.append({"feature": fname, "max_fold_auc": max_f, "pooled_auc": two_sided_pooled,
                             "leakage_suspect": bool(fmeta["leakage_suspected"])})
    leakage_hit = not bool(canary_bundle["passed"])
    if leakage_hit:
        raise SystemExit("LEAKAGE CANARY TRIPPED on input channels; halting A33-R3-LCHC.")

    n_fp = int(footprint.sum())

    # 2. Primary screen
    print("[2/6] Experiment 1/3: Primary screen (quadrant-buffered-15px-v1)", flush=True)
    screen_preds = {"B1_regional": [], "A33_R3_LCHC": []}
    screen_fold_reports = []
    lchc_screen_bundles = []
    for fold in screen_holdout.folds:
        f_id = int(fold["id"])
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        if (train & valid).any() or (visible & fold["truth"]).any():
            raise RuntimeError(f"Leakage invariant violated in screen fold {fold['name']}")
        d_vis = distance_transform_edt(~visible)
        eligible = valid & (d_vis > CATALOGUE_EXCLUSION_PX)
        budget = int(round(FULL_DOT_BUDGET * int(valid.sum()) / n_fp))

        reg_m = analog_invariant.fit_regional_expert(l1_arrays, train, visible, d_vis,
                                                       seed=20261027 + 100 * f_id + 1)
        reg_s = analog_invariant.predict(reg_m, l1_arrays, valid)
        screen_preds["B1_regional"].append(_emit(reg_s, eligible, budget).astype(np.uint8))

        lchc_surface, bundle = lchc.fit_lchc_surface(footprint, train, seed_mask=seed_mask)
        lchc_dots = _emit(lchc_surface, eligible, budget)
        screen_preds["A33_R3_LCHC"].append(lchc_dots.astype(np.uint8))
        lchc_screen_bundles.append(bundle)
        screen_fold_reports.append({
            "fold": fold["name"], "dot_budget": budget, "eligible_cells": int(eligible.sum()),
            "withheld_positives": int(fold["truth"].sum()),
            "lchc_connect_report": {k: v for k, v in bundle.connect_report.items() if k != "edges"},
        })
        print(f"      fold {fold['name']}: budget={budget} connect={bundle.connect_report['n_mst_edges_kept']}"
              f"/{bundle.connect_report['n_mst_edges_total']} kept", flush=True)

    screen_results = {name: screen_holdout.summarize(preds, ci_draws=1999)
                       for name, preds in screen_preds.items()}
    screen_vs_b1 = screen_holdout.compare_paired(
        screen_preds["A33_R3_LCHC"], screen_preds["B1_regional"], ci_draws=1999, seed=20261027
    )
    print(f"  screen A33_R3_LCHC={screen_results['A33_R3_LCHC']['dti']:.6f} vs "
          f"B1_regional={screen_results['B1_regional']['dti']:.6f}", flush=True)

    # 3. Independent confirmation
    print("[3/6] Experiment 2/3: Independent confirmation (diagonal-wedge-buffered-20px-confirm-v1)", flush=True)
    confirm_preds = {"B1_regional": [], "A33_R3_LCHC": []}
    confirm_fold_reports = []
    for fold in confirm_holdout.folds:
        f_id = int(fold["id"])
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        if (train & valid).any() or (visible & fold["truth"]).any():
            raise RuntimeError(f"Leakage invariant violated in confirm fold {fold['name']}")
        d_vis = distance_transform_edt(~visible)
        eligible = valid & (d_vis > CATALOGUE_EXCLUSION_PX)
        budget = int(round(FULL_DOT_BUDGET * int(valid.sum()) / n_fp))

        reg_m = analog_invariant.fit_regional_expert(l1_arrays, train, visible, d_vis,
                                                       seed=20261027 + 300 * f_id + 1)
        reg_s = analog_invariant.predict(reg_m, l1_arrays, valid)
        confirm_preds["B1_regional"].append(_emit(reg_s, eligible, budget).astype(np.uint8))

        lchc_surface, bundle = lchc.fit_lchc_surface(footprint, train, seed_mask=seed_mask)
        confirm_preds["A33_R3_LCHC"].append(_emit(lchc_surface, eligible, budget).astype(np.uint8))
        confirm_fold_reports.append({
            "fold": fold["name"], "dot_budget": budget, "eligible_cells": int(eligible.sum()),
            "withheld_positives": int(fold["truth"].sum()),
            "lchc_connect_report": {k: v for k, v in bundle.connect_report.items() if k != "edges"},
        })

    confirm_results = {name: confirm_holdout.summarize(preds, ci_draws=1999)
                        for name, preds in confirm_preds.items()}
    confirm_vs_b1 = confirm_holdout.compare_paired(
        confirm_preds["A33_R3_LCHC"], confirm_preds["B1_regional"], ci_draws=1999, seed=20261027
    )
    print(f"  confirm A33_R3_LCHC={confirm_results['A33_R3_LCHC']['dti']:.6f} vs "
          f"B1_regional={confirm_results['B1_regional']['dti']:.6f}", flush=True)

    # 4. Full-footprint deployment, placement & uniqueness
    print("[4/6] Experiment 3/3: Full-footprint surface, CELF-300m placement & 21-raster uniqueness", flush=True)
    full_surface, full_bundle = lchc.fit_lchc_surface(footprint, footprint, seed_mask=seed_mask)
    canary_arrays_final = dict(canary_arrays)
    canary_arrays_final["lchc_full_surface"] = full_surface
    final_surface_canary = screen_holdout.canary({"lchc_full_surface": full_surface})
    fmeta = final_surface_canary["features"]["lchc_full_surface"]
    max_f = float(max(max(d["auc"], 1.0 - d["auc"]) for d in fmeta["folds"]))
    two_sided_pooled = float(max(fmeta["pooled_auc"], 1.0 - fmeta["pooled_auc"]))
    canary_rows.append({"feature": "lchc_full_surface", "max_fold_auc": max_f,
                         "pooled_auc": two_sided_pooled, "leakage_suspect": bool(fmeta["leakage_suspected"])})
    if fmeta["leakage_suspected"]:
        raise SystemExit("LEAKAGE CANARY TRIPPED on final LCHC surface; halting.")

    d_full_cat = distance_transform_edt(~catalogue)
    full_eligible = footprint & (d_full_cat > CATALOGUE_EXCLUSION_PX)
    elig_flat = np.flatnonzero(full_eligible)
    elig_scores = full_surface.ravel()[elig_flat]
    top_idx = elig_flat[np.argsort(-elig_scores, kind="mergesort")[:FULL_DOT_BUDGET]]
    surface_preview_dots = np.zeros(footprint.shape, dtype=bool)
    surface_preview_dots.ravel()[top_idx] = True

    final_dots = _emit(full_surface, full_eligible, FULL_DOT_BUDGET)

    uniq = csht_transfer.audit_uniqueness_against_manifest(
        full_surface, surface_preview_dots, final_dots, footprint, MANIFEST, root=ROOT,
    )

    incumbent_best = float(max(screen_results["B1_regional"]["dti"], RECORDED_B1_REGIONAL))
    confirm_baseline_ceil = float(max(confirm_results["B1_regional"]["dti"], RECORDED_B1_REGIONAL))
    screen_split_id = "quadrant-buffered-15px-v1"
    confirm_split_id = confirm_results["A33_R3_LCHC"]["split_id"]

    prelim_promote = (
        screen_results["A33_R3_LCHC"]["dti"] > incumbent_best
        and screen_vs_b1["ci95_strictly_positive"] and screen_vs_b1["fold_wins"] >= 3
        and confirm_results["A33_R3_LCHC"]["dti"] > confirm_baseline_ceil
        and confirm_vs_b1["ci95_strictly_positive"] and confirm_vs_b1["fold_wins"] >= 3
        and uniq["surface"]["passed"] and uniq["final_dots"]["passed"]
        and not leakage_hit
    )
    prelim_verdict = (
        "duplicate" if not (uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
        else ("promote" if prelim_promote else "negative")
    )

    print("[5/6] GeoTIFF emission, saved-byte format audit & promotion gate check", flush=True)
    note_template = (
        "GEMS33 A33-R3-LCHC: thermal/vent least-cost connectivity graph 37654d | gate "
        + ("PROMOTE" if prelim_verdict == "promote" else prelim_verdict.upper())
        + " | {cid}"
    )
    receipt = write_pair(
        final_dots.astype(np.float32), template=ROOT / "data" / "sample_submission.tif",
        catalogue=catalogue, footprint=footprint, outdir=ROOT / "docs" / "downloads",
        family="gemsdoe33", hypothesis="a33-r3-lchc-connectivity-37654", date=DATE,
        note_template=note_template, scientific_verdict=prelim_verdict,
    )

    cand_sha = receipt["primary_zero_outside"]["sha256"]
    zero_path = ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"]
    fmt_audit = audit_submission(zero_path, ROOT / "data" / "sample_submission.tif")
    zval = receipt["primary_zero_outside"]["validator"]
    elapsed = round(time.monotonic() - started, 2)
    manifest_entries = json.loads(MANIFEST.read_text())["rasters"]

    uniq["final_dots"]["candidate_sha256"] = cand_sha
    _json_write(UNIQUENESS, uniq)
    _json_write(VALIDATOR, receipt)

    evaluator_sha = sha256_file(ROOT / "vendor" / "gems24_template" / "holdout.py")
    writer_sha = sha256_file(ROOT / "vendor" / "gems24_template" / "submission.py")
    source_manifest_sha = sha256_file(ROOT / "vendor" / "gems24_template" / "SOURCE.json")
    best_sha = sha256_file(ROOT / "evidence" / "a33_r2_experiment_20261026.json")
    cache_hash_map = {k: sha256_file(ROOT / ".cache" / "features" / f"{k}.npy")
                      for k in CANARY_SOURCE_NAMES}
    feature_cache_digest = csht_transfer.sha256_bytes(json.dumps(cache_hash_map, sort_keys=True).encode("utf-8"))

    promo_evidence = {
        "candidate_sha256": cand_sha,
        "current_holdout_best_sha256": best_sha,
        "lane": "GEMSDOE33 analog-field and hydrothermal-conduit structural transfer",
        "shared_template": {
            "source_manifest_sha256": source_manifest_sha,
            "feature_cache_sha256": feature_cache_digest,
            "evaluator_sha256": evaluator_sha,
            "writer_sha256": writer_sha,
        },
        "screen": {
            "label": "HOLDOUT-DTI", "evaluator_version": screen_results["A33_R3_LCHC"]["evaluator_version"],
            "evaluator_sha256": evaluator_sha, "candidate_sha256": cand_sha, "baseline_sha256": best_sha,
            "withheld_positives": int(screen_results["A33_R3_LCHC"]["n_withheld_positive_pixels"]),
            "whole_segments_with_buffer": True, "all_catalogue_features_visible_only": True,
            "visible_faults_masked_pixel_exactly": True, "alpha": 0.2, "beta": 0.8,
            "kernel": "triangular", "radius_m": 300,
            "candidate_pooled_dti": float(screen_results["A33_R3_LCHC"]["dti"]),
            "baseline_pooled_dti": incumbent_best,
            "in_run_b1_regional_dti": float(screen_results["B1_regional"]["dti"]),
            "pooled_delta_ci95": [float(v) for v in screen_vs_b1["paired_delta_ci95"]],
            "ci_estimand": "pooled paired delta", "split_id": screen_split_id,
            "fold_wins": int(screen_vs_b1["fold_wins"]), "n_folds": int(screen_vs_b1["n_folds"]),
        },
        "confirmation": {
            "label": "HOLDOUT-DTI", "evaluator_version": confirm_results["A33_R3_LCHC"]["evaluator_version"],
            "evaluator_sha256": evaluator_sha, "candidate_sha256": cand_sha, "baseline_sha256": best_sha,
            "withheld_positives": int(confirm_results["A33_R3_LCHC"]["n_withheld_positive_pixels"]),
            "whole_segments_with_buffer": True, "all_catalogue_features_visible_only": True,
            "visible_faults_masked_pixel_exactly": True, "alpha": 0.2, "beta": 0.8,
            "kernel": "triangular", "radius_m": 300,
            "candidate_pooled_dti": float(confirm_results["A33_R3_LCHC"]["dti"]),
            "baseline_pooled_dti": confirm_baseline_ceil,
            "in_run_confirm_b1_regional_dti": float(confirm_results["B1_regional"]["dti"]),
            "pooled_delta_ci95": [float(v) for v in confirm_vs_b1["paired_delta_ci95"]],
            "ci_estimand": "pooled paired delta", "split_id": confirm_split_id,
            "independent_of_screen": True, "frozen_before_screen_results": True,
            "fold_wins": int(confirm_vs_b1["fold_wins"]), "n_folds": int(confirm_vs_b1["n_folds"]),
        },
        "feature_names": [r["feature"] for r in canary_rows],
        "feature_canaries": [
            {"feature": r["feature"], "holdout_auc": float(max(r["max_fold_auc"], r["pooled_auc"])),
             "max_fold_auc": float(r["max_fold_auc"]), "pooled_auc": float(r["pooled_auc"]),
             "split_id": screen_split_id, "visible_only": True}
            for r in canary_rows
        ],
        "registry_sha256": MANIFEST_SHA, "registry_complete": True,
        "registry_raster_sha256s": [e["sha256"] for e in manifest_entries],
        "duplicates": {"surface": uniq["surface"], "final_dots": uniq["final_dots"]},
        "submission_note": receipt["note"], "experiments": 3, "elapsed_seconds": elapsed,
    }
    _json_write(PROMO_INPUT, promo_evidence)
    assessment = promotion.assess(promo_evidence, fmt_audit, cand_sha)
    _json_write(PROMO_ASSESS, assessment)

    final_verdict = (
        "duplicate" if not (uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
        else assessment["verdict"]
    )
    eligible_for_selector = bool(assessment["eligible_for_selector"] and final_verdict == "promote")

    run_card = {
        "schema": 2, "campaign": "A33-R3", "hypothesis": (
            "A33-R3-LCHC: Least-Cost Hydrothermal Connectivity -- a minimum-cost graph (Dijkstra + "
            "minimum spanning tree) threading independently documented DOE GDR #1391 hot-spring and "
            "volcanic-vent manifestation points through a label-free conductivity/gravity/geodetic-"
            "strain/basement-edge resistance surface recovers blind connecting fault segments better "
            "than the B1_regional incumbent."
        ),
        "mechanism": (
            "Percentile-rank-average conductivity, gravity horizontal-gradient/slope, geodetic shear/"
            "dilatation rate, and basement-depth edge into a cost surface (fit stats restricted to the "
            "fold-visible TRAIN region only); downsample to 300 m; multi-source Dijkstra among up to 90 "
            "merged thermal/vent clusters; minimum-spanning-tree the pairwise cost-distance matrix, "
            "keep the shortest 85% of edges, trace each kept path weighted by a directness ratio "
            "(straight-line / cost-weighted length); upsample, blend with LiDAR/TMI corroboration, and "
            "place 37,654 dots via the shared 300 m triangular-kernel CELF submodular operator."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Buried plutonic/caldera intrusive margins, Lake Lahontan paleo-shoreline benches, and "
            "conductive sedimentary basin fill can all produce a low-cost corridor between two "
            "hydrologically connected but non-tectonic points."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "primary_screen": {
                "evaluator_version": screen_results["A33_R3_LCHC"]["evaluator_version"],
                "split_id": screen_split_id,
                "withheld_positives": screen_results["A33_R3_LCHC"]["n_withheld_positive_pixels"],
                "candidate": screen_results["A33_R3_LCHC"]["dti"],
                "candidate_95pct_ci": screen_results["A33_R3_LCHC"]["ci95"]["interval"],
                "incumbent_b1_regional": screen_results["B1_regional"]["dti"],
                "incumbent_95pct_ci": screen_results["B1_regional"]["ci95"]["interval"],
                "recorded_a33_l1_b1_regional": RECORDED_B1_REGIONAL,
                "paired_delta_vs_b1": screen_vs_b1["paired_delta_dti"],
                "paired_delta_95pct_ci": screen_vs_b1["paired_delta_ci95"],
                "fold_wins_vs_b1": f"{screen_vs_b1['fold_wins']}/{screen_vs_b1['n_folds']}",
            },
            "independent_confirmation": {
                "evaluator_version": confirm_results["A33_R3_LCHC"]["evaluator_version"],
                "split_id": confirm_split_id, "frozen_before_screen_results": True,
                "withheld_positives": confirm_results["A33_R3_LCHC"]["n_withheld_positive_pixels"],
                "candidate": confirm_results["A33_R3_LCHC"]["dti"],
                "candidate_95pct_ci": confirm_results["A33_R3_LCHC"]["ci95"]["interval"],
                "incumbent_b1_regional": confirm_results["B1_regional"]["dti"],
                "incumbent_95pct_ci": confirm_results["B1_regional"]["ci95"]["interval"],
                "paired_delta_vs_b1": confirm_vs_b1["paired_delta_dti"],
                "paired_delta_95pct_ci": confirm_vs_b1["paired_delta_ci95"],
                "fold_wins_vs_b1": f"{confirm_vs_b1['fold_wins']}/{confirm_vs_b1['n_folds']}",
            },
            "qualification": (
                "Mapped-catalogue whole-segment hide-and-recover proxy (HOLDOUT-DTI), NOT private "
                "organizer expert truth and NOT an ORGANIZER-CONFIRMED competition score."
            ),
        },
        "correlation_overlap_vs_registry": {
            "scope": "21 SHA-256-pinned focus-site and local GEMSDOE33 rasters (registry/focus_rasters_20261026.json)",
            "registry_sha256": MANIFEST_SHA,
            "surface_max_abs_spearman": uniq["surface"]["max_abs_spearman_rho"],
            "surface_max_3px_overlap": uniq["surface"]["max_preview_fraction_within_3px"],
            "surface_passed": uniq["surface"]["passed"],
            "final_dots_max_abs_spearman": uniq["final_dots"]["max_abs_spearman_rho"],
            "final_dots_max_3px_overlap": uniq["final_dots"]["max_candidate_fraction_within_3px"],
            "final_dots_passed": uniq["final_dots"]["passed"],
        },
        "raster_sha256": cand_sha,
        "validator_output": {
            "format_valid": bool(zval["format_valid"] and fmt_audit.get("pass")),
            "hard_failures": zval["hard_failures"],
            "no_nan_inside_footprint": bool(zval["checks"]["footprint_all_finite"]["pass"]),
            "values_in_0_1": bool(zval["checks"]["footprint_range_0_1"]["pass"]),
            "whole_array_all_finite_0_1": bool(zval["checks"]["variant_strict_whole_array_no_nan_allowed"]["pass"]),
            "crs_matches_epsg_32611": bool(zval["checks"]["crs_epsg_32611"]["pass"]),
            "shape_matches_3730x3292": bool(zval["checks"]["shape_matches_template"]["pass"]),
            "geotransform_matches_template": bool(zval["checks"]["geotransform_matches_template"]["pass"]),
            "predicted_positive_dots": int(final_dots.sum()),
            "catalogue_overlap_dots": int((final_dots & catalogue).sum()),
        },
        "submission": {
            "name": receipt["submission_name"], "file": receipt["primary_zero_outside"]["file"],
            "zip": receipt["primary_zero_outside"]["zip"],
            "nan_twin": receipt["official_text_nan_outside_twin"]["file"],
            "nan_twin_zip": receipt["official_text_nan_outside_twin"]["zip"],
            "note": receipt["note"], "note_characters": receipt["note_characters"],
            "ok_to_download": bool(zval["format_valid"] and fmt_audit.get("pass")),
            "eligible_for_weekly_selector": eligible_for_selector, "ok_to_submit": False,
            "selector_notice": (
                "PROMOTE TO WEEKLY SELECTOR: all automated scientific, confirmation, canary, "
                "uniqueness & GeoTIFF format gates PASSED; ok_to_submit remains False in automated "
                "tooling until the separate human/cross-lane weekly-slot selector runs."
                if eligible_for_selector else
                f"DO NOT SUBMIT: failed automated promotion gates {assessment['failed_gates']}."
            ),
        },
        "promotion_assessment": assessment, "verdict": final_verdict, "experiments_run": 3,
        "elapsed_seconds": elapsed, "submission_slots_used": 0,
    }
    _json_write(RUN_CARD, run_card)
    _json_write(DOCS_CARD, run_card)

    full_report = {
        "schema": 2, "started_utc": started_utc,
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED", "campaign": "A33-R3", "hypothesis_id": "A33-R3-LCHC",
        "preregistration": str(PREREG.relative_to(ROOT)), "preregistration_sha256": PREREG_SHA,
        "thermal_vent_seed_metadata": seed_meta,
        "lchc_full_deployment_report": {
            "seed_report": full_bundle.seed_report, "cost_report": full_bundle.cost_report,
            "graph_report": full_bundle.graph_report,
            "connect_report": {k: v for k, v in full_bundle.connect_report.items() if k != "edges"},
        },
        "feature_canary_summary": {
            "tested_channels": len(canary_rows), "stop_threshold_two_sided_auc": 0.90,
            "max_pooled_auc": float(max(r["pooled_auc"] for r in canary_rows)),
            "max_fold_auc": float(max(r["max_fold_auc"] for r in canary_rows)),
            "any_leakage_suspect": leakage_hit, "rows": canary_rows,
        },
        "screen_fold_reports": screen_fold_reports, "screen_results": screen_results,
        "screen_paired_vs_b1": screen_vs_b1,
        "confirm_fold_reports": confirm_fold_reports, "confirm_results": confirm_results,
        "confirm_paired_vs_b1": confirm_vs_b1,
        "uniqueness_summary": {
            "manifest": str(MANIFEST.relative_to(ROOT)), "registry_sha256": MANIFEST_SHA,
            "registry_count": len(manifest_entries),
            "surface_passed": uniq["surface"]["passed"],
            "surface_max_abs_spearman": uniq["surface"]["max_abs_spearman_rho"],
            "surface_max_3px_overlap": uniq["surface"]["max_preview_fraction_within_3px"],
            "final_dots_passed": uniq["final_dots"]["passed"],
            "final_dots_max_abs_spearman": uniq["final_dots"]["max_abs_spearman_rho"],
            "final_dots_max_3px_overlap": uniq["final_dots"]["max_candidate_fraction_within_3px"],
        },
        "submission_receipt": receipt, "promotion_assessment": assessment, "verdict": final_verdict,
        "experiments_run": 3, "elapsed_seconds": elapsed, "submission_slots_used": 0,
    }
    _json_write(EVIDENCE, full_report)

    print(json.dumps({
        "verdict": final_verdict, "eligible_for_selector": eligible_for_selector,
        "failed_gates": assessment["failed_gates"],
        "file": receipt["primary_zero_outside"]["file"], "sha256": cand_sha,
        "screen_HOLDOUT_DTI": screen_results["A33_R3_LCHC"]["dti"],
        "screen_B1_regional": screen_results["B1_regional"]["dti"],
        "screen_paired_delta_ci95": screen_vs_b1["paired_delta_ci95"],
        "screen_fold_wins": screen_vs_b1["fold_wins"],
        "confirm_HOLDOUT_DTI": confirm_results["A33_R3_LCHC"]["dti"],
        "confirm_B1_regional": confirm_results["B1_regional"]["dti"],
        "confirm_paired_delta_ci95": confirm_vs_b1["paired_delta_ci95"],
        "confirm_fold_wins": confirm_vs_b1["fold_wins"],
        "max_final_abs_spearman": uniq["final_dots"]["max_abs_spearman_rho"],
        "max_final_3px_overlap": uniq["final_dots"]["max_candidate_fraction_within_3px"],
        "elapsed_seconds": elapsed,
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
