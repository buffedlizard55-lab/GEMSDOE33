#!/usr/bin/env python3
"""Run the preregistered G33-DPPS campaign (3 experiments, fail-closed gates).

Exp 1: quadrant screen. Exp 2: diagonal-wedge confirmation. Exp 3: production
build + uniqueness + saved-byte format audit. Writes evidence, a run card and
the downloadable GeoTIFF pair. Never uploads anything and never authorizes a
slot unless every preregistered gate passes.

Contract: evidence/dpps_preregistration_20261026.json
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe33 import analog_invariant, csht_transfer, dpps, emission, grid, novelty  # noqa: E402
from gemsdoe33.paths import CACHE, DATA  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
from vendor.gems24_template.validator import sha256_file  # noqa: E402

PREREG = ROOT / "evidence" / "dpps_preregistration_20261026.json"
MANIFEST21 = ROOT / "registry" / "focus_rasters_20261026.json"
EXTRA_LOCAL = [
    ("G33-a33-r2-csht-0b78c04d5fad", "GEMSDOE33", "docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif"),
    ("G33-g33-171b8b87dbf7", "GEMSDOE33", "docs/downloads/gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7-zeros.tif"),
    ("G33-r3-da-hgcm-a6a8552e", "GEMSDOE33", "docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif"),
    ("G33-h33r3-40f15a687381", "GEMSDOE33", "docs/downloads/gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-zeros.tif"),
]
FULL_BUDGET = 37_654
MIN_SPACING_PX = 2.8
CATALOGUE_EXCLUSION_PX = 2.0
DATE = "20261026"


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def _emit(score: np.ndarray, eligible: np.ndarray, budget: int) -> np.ndarray:
    dots = emission.dot_thin(eligible, MIN_SPACING_PX, priority=score, max_dots=budget)
    if int(dots.sum()) != budget:
        raise RuntimeError(f"Emission underfilled: {int(dots.sum())} != {budget}")
    return dots


def _fold_preds(holdout, surface, ctrl_surface, b1_arrays, *, include_random: bool, seed_base: int):
    preds: dict[str, list[np.ndarray]] = {"DPPS": [], "CTRL_PIXEL": [], "B1_regional": []}
    if include_random:
        preds["matched_random"] = []
    reports = []
    n_fp = int(holdout.footprint.sum())
    for fold in holdout.folds:
        f_id = int(fold["id"])
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        if (train & valid).any() or (visible & fold["truth"]).any():
            raise RuntimeError(f"Leakage invariant violated in fold {fold['name']}")
        d_vis = distance_transform_edt(~visible)
        eligible = valid & (d_vis > CATALOGUE_EXCLUSION_PX)
        budget = int(round(FULL_BUDGET * int(valid.sum()) / n_fp))
        t0 = time.time()
        preds["DPPS"].append(
            csht_transfer.celf_emit_300m(surface, eligible, budget, min_self_spacing_px=2.5).astype(np.uint8)
        )
        preds["CTRL_PIXEL"].append(
            csht_transfer.celf_emit_300m(ctrl_surface, eligible, budget, min_self_spacing_px=2.5).astype(np.uint8)
        )
        reg = analog_invariant.fit_regional_expert(
            b1_arrays, train, visible, d_vis, seed=seed_base + 100 * f_id + 1
        )
        reg_s = analog_invariant.predict(reg, b1_arrays, valid)
        preds["B1_regional"].append(_emit(reg_s, eligible, budget).astype(np.uint8))
        if include_random:
            rng = np.random.default_rng(seed_base + 50 * f_id)
            preds["matched_random"].append(
                _emit(rng.random(holdout.footprint.shape, dtype=np.float32), eligible, budget).astype(np.uint8)
            )
        reports.append({
            "fold": fold["name"], "dot_budget": budget,
            "eligible_cells": int(eligible.sum()),
            "withheld_positives": int(fold["truth"].sum()),
            "seconds": round(time.time() - t0, 1),
        })
        print(f"  fold {fold['name']}: budget={budget} done in {reports[-1]['seconds']}s", flush=True)
    return preds, reports


def _registry_entries() -> list[dict]:
    entries = []
    for e in json.loads(MANIFEST21.read_text())["rasters"]:
        rel = e.get("local_path", e.get("dest", ""))
        entries.append({"id": e["id"], "site": e["site"], "path": rel, "pinned_sha256": e["sha256"]})
    for rid, site, rel in EXTRA_LOCAL:
        entries.append({"id": rid, "site": site, "path": rel, "pinned_sha256": None})
    return entries


def _uniqueness(surface, preview_dots, final_dots, footprint, *, seed=20261026, sample_pixels=250_000):
    import rasterio

    fp = np.asarray(footprint, bool)
    rng = np.random.default_rng(seed)
    fp_flat = np.flatnonzero(fp)
    sample_idx = np.sort(rng.choice(fp_flat, size=min(sample_pixels, fp_flat.size), replace=False))
    surf_ranks = rankdata(np.asarray(surface, np.float64).ravel()[sample_idx], method="average")
    surf_c = surf_ranks - surf_ranks.mean()
    surf_norm = float(np.linalg.norm(surf_c))
    if surf_norm == 0:
        raise ValueError("Constant surface cannot pass uniqueness guard")
    yy, xx = np.mgrid[-3:4, -3:4]
    disk = yy * yy + xx * xx <= 9
    surf_rows, final_rows = [], []
    for entry in _registry_entries():
        rpath = ROOT / entry["path"]
        if not rpath.is_file():
            raise FileNotFoundError(f"Missing registry raster: {rpath}")
        actual = sha256_file(rpath)
        if entry["pinned_sha256"] and actual != entry["pinned_sha256"]:
            raise ValueError(f"Registry SHA mismatch for {entry['id']}")
        with rasterio.open(rpath) as ds:
            arr = ds.read(1)
        other = (np.where(np.isfinite(arr), arr, 0.0) > 0.0) & fp
        near = binary_dilation(other, structure=disk)
        o_ranks = rankdata(other.ravel()[sample_idx].astype(np.float64), method="average")
        o_c = o_ranks - o_ranks.mean()
        o_norm = float(np.linalg.norm(o_c))
        rho = float(np.dot(surf_c, o_c) / (surf_norm * o_norm)) if o_norm else None
        prev = novelty.binary_comparison(preview_dots, other, fp, near_other=near)
        fin = novelty.binary_comparison(final_dots, other, fp, near_other=near)
        surf_rows.append({
            "registry_id": entry["id"], "site": entry["site"], "raster_sha256": actual,
            "registry_dots": int(other.sum()), "spearman_rho": rho,
            "fraction_candidate_within_3px": prev["fraction_candidate_within_3px"],
            "duplicate": bool((rho is not None and abs(rho) > 0.90) or prev["fraction_candidate_within_3px"] > 0.70),
        })
        final_rows.append({
            "registry_id": entry["id"], "site": entry["site"], "raster_sha256": actual,
            "registry_dots": int(other.sum()), "spearman_rho": fin["spearman_rho"],
            "fraction_candidate_within_3px": fin["fraction_candidate_within_3px"],
            "candidate_dots_within_3px": fin["candidate_dots_within_3px"],
            "candidate_dots": fin["candidate_dots"],
            "duplicate": bool(fin["duplicate_trigger"]),
        })
        del arr, other, near
    surface_sha = csht_transfer.sha256_array(np.asarray(surface, dtype=np.float32))
    return {
        "registry_count": len(surf_rows),
        "registry_manifest": "registry/focus_rasters_20261026.json + 4 local newer zeros twins",
        "registry_manifest_sha256": sha256_file(MANIFEST21),
        "surface_sha256": surface_sha,
        "surface": {
            "stage": "surface_before_placement", "surface_sha256": surface_sha,
            "sample_pixels": int(sample_idx.size), "spearman_stop_gt": 0.90, "overlap_stop_gt": 0.70,
            "passed": not any(r["duplicate"] for r in surf_rows),
            "max_abs_spearman_rho": float(max(abs(r["spearman_rho"]) for r in surf_rows if r["spearman_rho"] is not None)),
            "max_preview_fraction_within_3px": float(max(r["fraction_candidate_within_3px"] for r in surf_rows)),
            "comparisons": surf_rows,
        },
        "final_dots": {
            "stage": "final_dots", "spearman_stop_gt": 0.90, "overlap_stop_gt": 0.70,
            "passed": not any(r["duplicate"] for r in final_rows),
            "max_abs_spearman_rho": float(max(abs(r["spearman_rho"]) for r in final_rows if r["spearman_rho"] is not None)),
            "max_fraction_within_3px": float(max(r["fraction_candidate_within_3px"] for r in final_rows)),
            "comparisons": final_rows,
        },
    }


def main() -> int:
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    expected_sha = (ROOT / "evidence" / "dpps_preregistration_20261026.sha256").read_text().strip()
    actual_sha = sha256_file(PREREG)
    if actual_sha != expected_sha:
        raise SystemExit(f"Frozen DPPS preregistration changed: {actual_sha} != {expected_sha}")
    prior = ROOT / "evidence" / "dpps_experiment_20261026.json"
    if prior.exists():
        raise SystemExit("DPPS campaign already recorded; rerun/retuning is forbidden by the preregistration.")

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    arrays = dpps.load_input_arrays()
    b1_arrays = analog_invariant.load_feature_arrays()

    print("[0/5] Building frozen DPPS + CTRL-PIXEL surfaces (label-free)", flush=True)
    surface, ctrl_surface, surf_report = dpps.build_surfaces(arrays, footprint)
    np.save(CACHE / "dpps_surface.npy", surface)
    np.save(CACHE / "dpps_ctrl_pixel_surface.npy", ctrl_surface)
    print(f"  {surf_report}", flush=True)

    screen_holdout = SegmentHoldout(footprint, catalogue, buffer_px=15)
    confirm_holdout = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=20)

    print("[1/5] Leakage canaries (9 channels)", flush=True)
    canary_bundle = screen_holdout.canary(arrays)
    canary_rows = []
    for fname, fmeta in canary_bundle["features"].items():
        canary_rows.append({
            "feature": fname,
            "pooled_auc_two_sided": float(max(fmeta["pooled_auc"], 1 - fmeta["pooled_auc"])),
            "max_fold_auc_two_sided": float(max(max(d["auc"], 1 - d["auc"]) for d in fmeta["folds"])),
            "raw_pooled_auc": float(fmeta["pooled_auc"]),
            "leakage_suspect": bool(fmeta["leakage_suspected"]),
        })
    print(f"  passed={canary_bundle['passed']} rows={canary_rows}", flush=True)
    if not canary_bundle["passed"]:
        _write_json(prior, {"status": "ABORTED_LEAKAGE_CANARY", "canary": canary_rows})
        raise SystemExit("LEAKAGE CANARY TRIPPED (>0.90); campaign aborted before scoring.")

    print("[2/5] Experiment 1/3: quadrant screen", flush=True)
    screen_preds, screen_reports = _fold_preds(
        screen_holdout, surface, ctrl_surface, b1_arrays, include_random=True, seed_base=20261026
    )
    screen_results = {n: screen_holdout.summarize(p, ci_draws=1999) for n, p in screen_preds.items()}
    screen_vs = {
        n: screen_holdout.compare_paired(screen_preds["DPPS"], screen_preds[n], ci_draws=1999, seed=20261026)
        for n in ("B1_regional", "CTRL_PIXEL", "matched_random")
    }
    print(f"  screen DPPS={screen_results['DPPS']['dti']:.6f} B1={screen_results['B1_regional']['dti']:.6f} "
          f"CTRL={screen_results['CTRL_PIXEL']['dti']:.6f} RAND={screen_results['matched_random']['dti']:.6f}", flush=True)

    print("[3/5] Experiment 2/3: diagonal-wedge confirmation", flush=True)
    confirm_preds, confirm_reports = _fold_preds(
        confirm_holdout, surface, ctrl_surface, b1_arrays, include_random=False, seed_base=20261027
    )
    confirm_results = {n: confirm_holdout.summarize(p, ci_draws=1999) for n, p in confirm_preds.items()}
    confirm_vs = {
        n: confirm_holdout.compare_paired(confirm_preds["DPPS"], confirm_preds[n], ci_draws=1999, seed=20261026)
        for n in ("B1_regional", "CTRL_PIXEL")
    }
    print(f"  confirm DPPS={confirm_results['DPPS']['dti']:.6f} B1={confirm_results['B1_regional']['dti']:.6f} "
          f"CTRL={confirm_results['CTRL_PIXEL']['dti']:.6f}", flush=True)

    print("[4/5] Experiment 3/3: production dots + uniqueness (25 rasters)", flush=True)
    d_full = distance_transform_edt(~catalogue)
    full_eligible = footprint & (d_full > CATALOGUE_EXCLUSION_PX)
    elig_flat = np.flatnonzero(full_eligible)
    top_idx = elig_flat[np.argsort(-surface.ravel()[elig_flat], kind="mergesort")[:FULL_BUDGET]]
    preview = np.zeros(footprint.shape, bool)
    preview.ravel()[top_idx] = True
    final_dots = csht_transfer.celf_emit_300m(surface, full_eligible, FULL_BUDGET, min_self_spacing_px=2.5)
    if int(final_dots.sum()) != FULL_BUDGET:
        raise RuntimeError("Production budget mismatch")
    if int((final_dots & catalogue).sum()) != 0:
        raise RuntimeError("Production dots on catalogue")
    uniq = _uniqueness(surface, preview, final_dots, footprint)
    print(f"  surface pass={uniq['surface']['passed']} max3px={uniq['surface']['max_preview_fraction_within_3px']:.4f} "
          f"| final pass={uniq['final_dots']['passed']} max3px={uniq['final_dots']['max_fraction_within_3px']:.4f}", flush=True)

    gates = {
        "all_feature_canaries": bool(canary_bundle["passed"]),
        "screen_beats_b1_pooled": bool(screen_results["DPPS"]["dti"] > screen_results["B1_regional"]["dti"]),
        "screen_beats_ctrl_pooled": bool(screen_results["DPPS"]["dti"] > screen_results["CTRL_PIXEL"]["dti"]),
        "screen_paired_ci_vs_b1_positive": bool(screen_vs["B1_regional"]["ci95_strictly_positive"]),
        "screen_fold_wins_vs_b1_ge_3": bool(screen_vs["B1_regional"]["fold_wins"] >= 3),
        "confirm_beats_b1_pooled": bool(confirm_results["DPPS"]["dti"] > confirm_results["B1_regional"]["dti"]),
        "confirm_paired_ci_vs_b1_positive": bool(confirm_vs["B1_regional"]["ci95_strictly_positive"]),
        "confirm_fold_wins_vs_b1_ge_3": bool(confirm_vs["B1_regional"]["fold_wins"] >= 3),
        "surface_not_duplicate": bool(uniq["surface"]["passed"]),
        "final_dots_not_duplicate": bool(uniq["final_dots"]["passed"]),
    }
    prelim_promote = all(gates.values())
    verdict_word = "PROMOTE-ELIGIBLE" if prelim_promote else "NEGATIVE-DO-NOT-SUBMIT"

    print("[5/5] Writing GeoTIFF pair + audits + run card", flush=True)
    note_template = (
        "GEMS33 DPPS dip-projected persistence scarp CELF 37654d | {cid} | "
        + ("gates PASS" if prelim_promote else "gate FAIL")
    )
    receipt = write_pair(
        final_dots.astype(np.float32),
        template=DATA / "sample_submission.tif",
        catalogue=catalogue,
        footprint=footprint,
        outdir=ROOT / "docs" / "downloads",
        family="gemsdoe33",
        hypothesis="dpps-dipproj-persistence-37654",
        date=DATE,
        note_template=note_template,
        scientific_verdict="promote" if prelim_promote else "negative",
    )
    zero_path = ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"]
    fmt = audit_submission(zero_path, DATA / "sample_submission.tif", strict_zero_outside=True)
    nan_path = ROOT / "docs" / "downloads" / receipt["official_text_nan_outside_twin"]["file"]
    fmt_nan = audit_submission(nan_path, DATA / "sample_submission.tif")
    gates["saved_bytes_format_strict_zero"] = bool(fmt["pass"] and fmt["in_range_0_1_whole_array"])
    gates["short_note"] = bool(0 < len(receipt["note"]) <= 140)
    gates["budget_3_experiments"] = True
    promote = all(gates.values())
    failed = [k for k, v in gates.items() if not v]
    elapsed = round(time.monotonic() - started, 2)

    experiment = {
        "schema": 1, "campaign": "G33-DPPS", "started_utc": started_utc,
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": elapsed, "experiments": 3,
        "preregistration_sha256": actual_sha,
        "surface_report": surf_report,
        "canary_rows": canary_rows, "canary_passed": bool(canary_bundle["passed"]),
        "screen": {"split_id": "quadrant-buffered-15px-v1", "folds": screen_reports,
                   "results": screen_results, "comparisons_vs_dpps": screen_vs},
        "confirmation": {"split_id": "diagonal-wedge-buffered-20px-confirm-v1", "folds": confirm_reports,
                         "results": confirm_results, "comparisons_vs_dpps": confirm_vs},
        "uniqueness": uniq, "gates": gates, "failed_gates": failed,
        "promote": promote, "verdict_word": verdict_word,
        "writer_receipt": receipt, "format_audit_zero_strict": fmt, "format_audit_nan": fmt_nan,
    }
    _write_json(prior, experiment)
    _write_json(ROOT / "evidence" / "dpps_uniqueness_20261026.json", uniq)
    _write_json(ROOT / "evidence" / "dpps_validator_20261026.json",
                {"zero_strict": fmt, "nan_twin": fmt_nan, "writer_receipt_file": receipt.get("receipt_file")})

    run_card = {
        "hypothesis": "DPPS: >=1.5 km along-strike scarp persistence + dip-projected gravity support (z*cot60 along +grad depth-to-basement) recovers withheld fault segments better than B1_regional HGB and a pixel-scarp CELF ablation, with a non-duplicate pre-placement surface.",
        "mechanism": "Label-free rank scarp strength (LiDAR, DEM-flexure fallback in void) -> 8-orientation 15px line-mean persistence -> dip-projection warp of iso_grav_anom_hg -> fixed fusion -> 300 m CELF, 37,654 dots, >2px off catalogue. Zero learned weights; zero registry pixels read.",
        "named_non_fault_mimic": "Prograding alluvial-fan toes / Lake Lahontan shoreline benches over buried pediments.",
        "holdout_dti": {
            "label": "HOLDOUT-DTI", "evaluator_version": "gems-segment-pooled-v1",
            "screen": {
                "split_id": "quadrant-buffered-15px-v1",
                "withheld_positives": int(screen_results["DPPS"]["n_withheld_positive_pixels"]),
                "candidate": float(screen_results["DPPS"]["dti"]),
                "candidate_95pct_ci": screen_results["DPPS"]["ci95"]["interval"],
                "b1_regional": float(screen_results["B1_regional"]["dti"]),
                "ctrl_pixel": float(screen_results["CTRL_PIXEL"]["dti"]),
                "matched_random": float(screen_results["matched_random"]["dti"]),
                "paired_delta_vs_b1": float(screen_vs["B1_regional"]["paired_delta_dti"]),
                "paired_delta_vs_b1_95pct_ci": screen_vs["B1_regional"]["paired_delta_ci95"],
                "fold_wins_vs_b1": f"{screen_vs['B1_regional']['fold_wins']}/4",
                "paired_delta_vs_ctrl": float(screen_vs["CTRL_PIXEL"]["paired_delta_dti"]),
                "paired_delta_vs_ctrl_95pct_ci": screen_vs["CTRL_PIXEL"]["paired_delta_ci95"],
            },
            "confirmation": {
                "split_id": "diagonal-wedge-buffered-20px-confirm-v1",
                "withheld_positives": int(confirm_results["DPPS"]["n_withheld_positive_pixels"]),
                "candidate": float(confirm_results["DPPS"]["dti"]),
                "candidate_95pct_ci": confirm_results["DPPS"]["ci95"]["interval"],
                "b1_regional": float(confirm_results["B1_regional"]["dti"]),
                "ctrl_pixel": float(confirm_results["CTRL_PIXEL"]["dti"]),
                "paired_delta_vs_b1": float(confirm_vs["B1_regional"]["paired_delta_dti"]),
                "paired_delta_vs_b1_95pct_ci": confirm_vs["B1_regional"]["paired_delta_ci95"],
                "fold_wins_vs_b1": f"{confirm_vs['B1_regional']['fold_wins']}/4",
            },
            "recorded_context_not_paired": {
                "A33_R2_CSHT_screen": 0.136716, "A33_R2_CSHT_confirm": 0.131169,
                "note": "CSHT was duplicate-blocked on its pre-placement surface vs G30-MSDB1 (owner-reported live 0.1462). No paired comparison is claimed.",
                "GEMSDOE32_B2": "0.2778 OWNER-REPORTED (NOT ORGANIZER-CONFIRMED); deletion-only H27-4 pruning, pixel-exact in repo evidence.",
            },
            "qualification": "Catalogue whole-segment hide-and-recover proxy. NOT the private organizer truth, NOT a competition score, NOT a projection.",
        },
        "correlation_overlap_vs_registry": {
            "scope": "25 rasters: 21 pinned in registry/focus_rasters_20261026.json + 4 local newer zeros twins",
            "surface_max_abs_spearman": uniq["surface"]["max_abs_spearman_rho"],
            "surface_max_3px_overlap": uniq["surface"]["max_preview_fraction_within_3px"],
            "surface_passed": uniq["surface"]["passed"],
            "final_dots_max_abs_spearman": uniq["final_dots"]["max_abs_spearman_rho"],
            "final_dots_max_3px_overlap": uniq["final_dots"]["max_fraction_within_3px"],
            "final_dots_passed": uniq["final_dots"]["passed"],
            "vs_G32_B2_final_3px": next(
                r["fraction_candidate_within_3px"] for r in uniq["final_dots"]["comparisons"]
                if r["registry_id"] == "G32-e5eb6e7e"
            ),
        },
        "leakage_canary": {"tested": len(canary_rows), "passed": bool(canary_bundle["passed"]),
                           "max_two_sided_auc": float(max(r["max_fold_auc_two_sided"] for r in canary_rows))},
        "raster_sha256": receipt["primary_zero_outside"]["sha256"],
        "nan_twin_sha256": receipt["official_text_nan_outside_twin"]["sha256"],
        "surface_sha256": uniq["surface_sha256"],
        "validator_output": {
            "strict_zero_primary_pass": bool(fmt["pass"]),
            "whole_array_finite_in_0_1": bool(fmt["in_range_0_1_whole_array"]),
            "no_nan_anywhere_zero_variant": bool(fmt["nonfinite_count"] == 0),
            "crs_epsg": fmt["epsg"], "shape": fmt["shape"],
            "transform_matches_template": bool(fmt["transform_match"]),
            "dots": int(fmt["emitted_pixels"]), "catalogue_overlap_dots": 0,
            "nan_twin_pass": bool(fmt_nan["pass"]),
        },
        "submission_name": receipt["submission_name"],
        "file": receipt["primary_zero_outside"]["file"],
        "zip": receipt["primary_zero_outside"]["zip"],
        "note": receipt["note"], "note_characters": len(receipt["note"]),
        "gates": gates, "failed_gates": failed,
        "ok_to_download": True,
        "ok_to_submit": bool(promote),
        "verdict": "promote" if promote else "negative",
        "experiments": 3, "elapsed_seconds": elapsed,
        "organizer_receipt": None,
        "slots_spent_by_this_workspace": 0,
    }
    _write_json(ROOT / "evidence" / "dpps_run_card_20261026.json", run_card)
    _write_json(ROOT / "docs" / "data" / "dpps_run_card_20261026.json", run_card)
    print(json.dumps(run_card, indent=2)[:4000], flush=True)
    print(f"VERDICT: {'promote' if promote else 'negative'} failed={failed} elapsed={elapsed}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
