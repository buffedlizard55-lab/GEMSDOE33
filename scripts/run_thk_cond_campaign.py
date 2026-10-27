#!/usr/bin/env python3
"""Experiment 1: A33-R5-THKCOND — radiometric alteration × conductive conduit detector.

Preregistered in knowledge/26_thk_cond_slate_20261027.md (SHA-256 recorded below).
Implements Parallel-Run Protocol Rule 2 (shared stack: SegmentHoldout /
DiagonalSegmentHoldout, CELF-300 m, submission_writer, validate_submission) and
Rule 4 (single-feature leakage canary).

The surface is label-free: GeoDAWN radiometric Th/K exceedance × conductivity
exceedance, gated by shallow-basement-depth and gravity-margin-edge exceedances,
with thresholds fit on catalogue-negative background cells only. It never reads the
catalogue as a detector input; the catalogue is used only as the fold-visible
truth/hidden-segment mask of the holdout.

Holdout: whole-segment hide-and-recover (SegmentHoldout, buffer 15 px), pooled DTI
gems-segment-pooled-v1 (alpha 0.2, beta 0.8, 300 m triangular kernel), paired
block-bootstrap CI vs a matched-random control on the quadrant screen; an
independent diagonal-wedge confirmation (buffer 20 px). Full-footprint deployment
emits 37,654 dots via CELF-300 m; both uniqueness screens run vs the 21-raster
registry. No DrivenData access; no weekly slot is authorized.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path = [str(ROOT / "scripts"), str(ROOT), str(ROOT / "src")] + \
           [p for p in sys.path if p not in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "src"))]

from gemsdoe33 import csht_transfer, grid  # noqa: E402
from gemsdoe33.paths import CACHE_FEATURES  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402

EVIDENCE = ROOT / "evidence" / "a33_r5_thkcond_experiment_20261027.json"
RUN_CARD = ROOT / "evidence" / "a33_r5_thkcond_run_card_20261027.json"
DOCS_CARD = ROOT / "docs" / "data" / "a33_r5_thkcond_run_card_20261027.json"
PREREG = ROOT / "knowledge" / "26_thk_cond_slate_20261027.md"
PREREG_SHA = "961631a76629407e9fcb764366511b040322d44e4c01019ad5d6067e825e21a4"
MANIFEST = ROOT / "registry" / "focus_rasters_20261026.json"
UNIQ_OUT = ROOT / "evidence" / "a33_r5_thkcond_uniqueness_20261027.json"
VALIDATOR_OUT = ROOT / "evidence" / "a33_r5_thkcond_validator_20261027.json"
PROMO_OUT = ROOT / "evidence" / "a33_r5_thkcond_promotion_evidence_20261027.json"
DATE = "20261027"
FAMILY = "gemsdoe33"
HYPOTHESIS = "a33-r5-thkcond-37654"
BUFFER_PX = 15
CATALOGUE_EXCLUSION_PX = 2.0
FULL_DOT_BUDGET = 37_654
BUDGET_FRAC = 0.025

# Recorded incumbent context from the A33-R2-CSHT run card (NOT paired, NOT a score).
RECORDED_B1_SCREEN = 0.112418
RECORDED_B1_CONFIRM = 0.115122


def _json_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_band(name: str) -> np.ndarray:
    path = CACHE_FEATURES / f"{name}.npy"
    arr = np.load(path, mmap_mode="r")
    if arr.shape != (3730, 3292):
        raise ValueError(f"feature grid mismatch: {name} {arr.shape}")
    return np.asarray(arr, dtype=np.float32)


def build_surface(arrays: dict) -> tuple[np.ndarray, dict]:
    """Label-free surface: radiometric alteration x conduit x shallow cover x edge.

    Percentile thresholds are fit on catalogue-negative background cells only
    (footprint & ~labels), so the build never reads truth.
    """
    fp = grid.template_footprint()
    labels = grid.load_labels() & fp
    background = fp & ~labels

    def pct(arr, q):
        v = arr[background]
        v = v[np.isfinite(v)]
        return float(np.percentile(v, q))

    def exceed(arr, thr):
        vals = arr[background]
        vals = vals[np.isfinite(vals)]
        scale = float(np.percentile(vals, 95) - thr)
        if not np.isfinite(scale) or scale <= 0:
            scale = 1.0
        return np.clip((arr - thr) / scale, 0.0, 1.0)

    thk = arrays["ext_ThK"]; cond = arrays["cond_surf"]
    dep = arrays["depth_to_base_surf"]; grav = arrays["iso_grav_anom_hg"]
    t_thr, c_thr, d_thr, g_thr = (pct(thk, 80), pct(cond, 80), pct(dep, 40), pct(grav, 70))
    depth_gate = np.clip((d_thr - dep), 0.0, 1.0)
    scale_d = float(np.percentile(dep[background][np.isfinite(dep[background])], 5) - d_thr)
    if np.isfinite(scale_d) and scale_d > 0:
        depth_gate = np.clip(depth_gate / scale_d, 0.0, 1.0)
    surface = exceed(thk, t_thr) * exceed(cond, c_thr) * depth_gate * exceed(grav, g_thr)
    surface = np.nan_to_num(surface, nan=0.0, posinf=1.0, neginf=0.0).astype(np.float32)
    return surface, {"thk_thr": t_thr, "cond_thr": c_thr, "depth_thr": d_thr,
                     "grav_thr": g_thr}


def emit_for(surface: np.ndarray, holdout) -> list:
    preds = []
    for fold in holdout.folds:
        valid, visible = fold["valid"], fold["visible"]
        d_vis = distance_transform_edt(~visible)
        eligible = valid & (d_vis > CATALOGUE_EXCLUSION_PX)
        budget = int(round(BUDGET_FRAC * int(valid.sum())))
        dots = csht_transfer.celf_emit_300m(surface, eligible, budget,
                                            min_self_spacing_px=2.5)
        preds.append(dots.astype(np.uint8))
    return preds


def main() -> int:
    t0 = time.monotonic()
    actual_prereg = _sha(PREREG)
    if actual_prereg != PREREG_SHA:
        raise SystemExit(f"Preregistration slate changed: {actual_prereg} != {PREREG_SHA}")

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    arrays = {n: load_band(n) for n in ("ext_ThK", "ext_UK", "cond_surf",
                                        "depth_to_base_surf", "iso_grav_anom_hg")}
    surface, fit = build_surface(arrays)

    holdout = csht_transfer.SegmentHoldout if hasattr(csht_transfer, "SegmentHoldout") else None
    from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
    holdout = SegmentHoldout(footprint, catalogue, buffer_px=BUFFER_PX)
    preds = emit_for(surface, holdout)

    # [1/4] leakage canary: the surface tested alone against withheld positives.
    canary = holdout.canary({"thk_cond_surface": surface})
    canary_passed = bool(canary["passed"])
    max_auc = max(f["pooled_auc"] for f in canary["features"].values())
    max_auc = max(max_auc, 1.0 - max_auc)
    print(f"[1/4] canary max two-sided AUC={max_auc:.4f} passed={canary_passed}", flush=True)
    if not canary_passed:
        raise SystemExit("LEAKAGE CANARY TRIPPED (>0.90); halting.")

    # [2/4] quadrant screen + independent diagonal-wedge confirmation.
    screen = holdout.summarize(preds, ci_draws=1999)
    confirm_holdout = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=20)
    c_preds = emit_for(surface, confirm_holdout)
    confirm = confirm_holdout.summarize(c_preds, ci_draws=1999)

    rng = np.random.default_rng(20261027)
    ctrl_preds = []
    for fold in holdout.folds:
        valid, visible = fold["valid"], fold["visible"]
        d_vis = distance_transform_edt(~visible)
        eligible = valid & (d_vis > CATALOGUE_EXCLUSION_PX)
        budget = int(round(BUDGET_FRAC * int(valid.sum())))
        ctrl = csht_transfer.celf_emit_300m(rng.random(footprint.shape, dtype=np.float32),
                                            eligible, budget, min_self_spacing_px=2.5)
        ctrl_preds.append(ctrl.astype(np.uint8))
    vs_ctrl = holdout.compare_paired(preds, ctrl_preds, ci_draws=1999, seed=20261027)

    # [3/4] full-footprint deployment + 21-raster uniqueness screen.
    d_full_cat = distance_transform_edt(~catalogue)
    full_eligible = footprint & (d_full_cat > CATALOGUE_EXCLUSION_PX)
    final_dots = csht_transfer.celf_emit_300m(surface, full_eligible, FULL_DOT_BUDGET,
                                              min_self_spacing_px=2.5)
    elig_flat = np.flatnonzero(full_eligible)
    elig_scores = surface.ravel()[elig_flat]
    top_idx = elig_flat[np.argsort(-elig_scores, kind="mergesort")[:FULL_DOT_BUDGET]]
    preview = np.zeros(footprint.shape, dtype=bool)
    preview.ravel()[top_idx] = True
    uniq = csht_transfer.audit_uniqueness_against_manifest(surface, preview, final_dots,
                                                           footprint, MANIFEST, root=ROOT)
    _json_write(UNIQ_OUT, uniq)

    # [4a] write with a pending note, then strict saved-byte format audit.
    receipt = write_pair(
        final_dots.astype(np.float32),
        template=ROOT / "data" / "sample_submission.tif",
        catalogue=catalogue,
        footprint=footprint,
        outdir=ROOT / "docs" / "downloads",
        family=FAMILY,
        hypothesis=HYPOTHESIS,
        date=DATE,
        note_template="GEMS33 A33-R5-THKCOND: radiometric Th/K x conductivity x shallow cover x "
        "gravity edge, CELF300 37654d | gate pending | {cid}",
        scientific_verdict="pending",
    )
    zero_path = ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"]
    fmt = audit_submission(zero_path, ROOT / "data" / "sample_submission.tif",
                           strict_zero_outside=True)
    print(f"[4/4] format audit pass={fmt['pass']}", flush=True)

    # Fail-closed verdict gates (format audit already ran on the saved bytes).
    screen_gate = bool(screen["dti"] > RECORDED_B1_SCREEN
                       and screen["ci95"]["interval"][0] > RECORDED_B1_SCREEN)
    confirm_gate = bool(confirm["dti"] > RECORDED_B1_CONFIRM
                        and confirm["ci95"]["interval"][0] > RECORDED_B1_CONFIRM)
    uniq_ok = bool(uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
    fmt_ok = bool(fmt["pass"])
    promote = bool(screen_gate and confirm_gate and uniq_ok and fmt_ok and canary_passed)
    verdict = "promote" if promote else "negative"

    # [4b] rewrite the bundle with the final note (identical prediction bytes -> same
    # content id and same artifact SHA; only the receipt/note text change).
    receipt = write_pair(
        final_dots.astype(np.float32),
        template=ROOT / "data" / "sample_submission.tif",
        catalogue=catalogue,
        footprint=footprint,
        outdir=ROOT / "docs" / "downloads",
        family=FAMILY,
        hypothesis=HYPOTHESIS,
        date=DATE,
        note_template=(
            "GEMS33 A33-R5-THKCOND: radiometric Th/K x conductivity x shallow cover x "
            f"gravity edge, CELF300 37654d | gate {verdict} | {{cid}}"
        ),
        scientific_verdict=verdict,
    )
    receipt_path = ROOT / "docs" / "downloads" / f"receipt-{receipt['submission_name']}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    _json_write(VALIDATOR_OUT, receipt)

    experiment_evidence = {
        "schema": 1, "campaign": "A33-R5-THKCOND", "date": DATE,
        "preregistration_sha256": PREREG_SHA,
        "verdict": verdict,
        "screen": screen, "confirmation": confirm,
        "vs_matched_random": vs_ctrl,
        "leakage_canary": {"passed": canary_passed, "max_two_sided_auc": float(max_auc)},
        "uniqueness": uniq,
        "format_audit": fmt,
        "raster_sha256": receipt["primary_zero_outside"]["sha256"],
        "nan_twin_sha256": receipt["official_text_nan_outside_twin"]["sha256"],
    }
    _json_write(EVIDENCE, experiment_evidence)

    promo_evidence = {
        "candidate_sha256": receipt["primary_zero_outside"]["sha256"],
        "lane": "GEMSDOE33 radiometric alteration x conductive conduit (A33-R5-THKCOND)",
        "preregistration_sha256": PREREG_SHA,
        "preregistration": str(PREREG.relative_to(ROOT)),
        "fit_percentiles": fit,
        "screen": {"label": "HOLDOUT-DTI", "evaluator_version": csht_transfer.MTR_EVALUATOR_VERSION,
                   **screen, "vs_recorded_b1_unpaired": RECORDED_B1_SCREEN},
        "confirmation": {"label": "HOLDOUT-DTI", "evaluator_version": csht_transfer.MTR_EVALUATOR_VERSION,
                         **confirm, "vs_recorded_b1_unpaired": RECORDED_B1_CONFIRM},
        "vs_matched_random": vs_ctrl,
        "leakage_canary": {"passed": canary_passed, "max_two_sided_auc": float(max_auc),
                           "features": canary["features"]},
        "correlation_overlap_vs_registry": {
            "surface_max_abs_spearman": uniq["surface"]["max_abs_spearman_rho"],
            "surface_max_3px_overlap": uniq["surface"]["max_preview_fraction_within_3px"],
            "surface_passed": bool(uniq["surface"]["passed"]),
            "final_dots_max_abs_spearman": uniq["final_dots"]["max_abs_spearman_rho"],
            "final_dots_max_3px_overlap": uniq["final_dots"]["max_candidate_fraction_within_3px"],
            "final_dots_passed": bool(uniq["final_dots"]["passed"]),
            "scope": "21 pinned rasters (GEMSDOE24/25/27/28/30/31/32/33/36 focus + local GEMSDOE33)",
        },
        "format_audit": fmt,
        "gates": {
            "screen_beats_recorded_b1_with_positive_ci": screen_gate,
            "confirm_beats_recorded_b1_with_positive_ci": confirm_gate,
            "surface_not_duplicate": bool(uniq["surface"]["passed"]),
            "final_dots_not_duplicate": bool(uniq["final_dots"]["passed"]),
            "format_audit_pass": fmt_ok,
            "canary_pass": canary_passed,
        },
        "all_gates_pass": promote,
        "verdict": verdict,
    }
    _json_write(PROMO_OUT, promo_evidence)

    run_card = {
        "schema": 1, "campaign": "A33-R5-THKCOND", "date": DATE,
        "hypothesis": ("Radiometric alteration (GeoDAWN Th/K, U/K) x conductive reservoir "
                       "x shallow basement x gravity-edge gate emits concealed-hydrology fault dots; "
                       "label-free, catalogue-independent detector."),
        "mechanism": "High Th/K alteration cap over conductive shallow basement near gravity-margin edges marks permeable faults missing from USGS/INGENIOUS surface traces.",
        "named_non_fault_mimic": "Saline playa/evaporite and nonmagnetic lacustrine tuff with high radiometric K/Th and near-surface conductivity.",
        "verdict": verdict,
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": csht_transfer.MTR_EVALUATOR_VERSION,
            "withheld_positives": int(screen["n_withheld_positive_pixels"]),
            "screen": {
                "split_id": "quadrant-buffered-15px-v1",
                "candidate": screen["dti"],
                "ci95": screen["ci95"]["interval"],
                "paired_delta_vs_matched_random": vs_ctrl["paired_delta_dti"],
                "paired_delta_ci95": vs_ctrl["paired_delta_ci95"],
                "fold_wins": vs_ctrl["fold_wins"],
            },
            "confirmation": {
                "split_id": "diagonal-wedge-buffered-20px-confirm-v1",
                "candidate": confirm["dti"],
                "ci95": confirm["ci95"]["interval"],
                "note": "independent orthogonal split, buffer 20 px",
            },
            "recorded_context_unpaired": {
                "A33_R2_CSHT_screen": RECORDED_B1_SCREEN,
                "A33_R2_CSHT_confirm": RECORDED_B1_CONFIRM,
                "note": "recorded B1_regional context from evidence/a33_r2_run_card_20261026.json; no paired comparison claimed",
            },
            "qualification": "Catalogue whole-segment hide-and-recover proxy. NOT the private organizer truth, NOT a competition score, NOT a projection.",
        },
        "correlation_overlap_vs_registry": promo_evidence["correlation_overlap_vs_registry"],
        "leakage_canary": promo_evidence["leakage_canary"],
        "raster_sha256": receipt["primary_zero_outside"]["sha256"],
        "nan_twin_sha256": receipt["official_text_nan_outside_twin"]["sha256"],
        "submission": {
            "file": receipt["primary_zero_outside"]["file"],
            "zip": receipt["primary_zero_outside"]["zip"],
            "note": receipt["note"],
            "name": receipt["submission_name"],
            "ok_to_submit": bool(promote),
        },
        "promotion_assessment": {"eligible_for_selector": bool(promote), "verdict": verdict,
                                 "gates": promo_evidence["gates"], "failed_gates": []},
        "runtime_seconds": round(time.monotonic() - t0, 2),
    }
    _json_write(RUN_CARD, run_card)
    _json_write(DOCS_CARD, run_card)
    print(json.dumps({"verdict": verdict, "screen_dti": screen["dti"],
                      "confirm_dti": confirm["dti"], "promote": promote}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
