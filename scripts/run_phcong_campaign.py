#!/usr/bin/env python3
"""Experiment 1 (2026-10-28): A33-R7-PHCONG — phase-congruency basement-edge detector.

Preregistered in knowledge/27_phcong_slate_20261028.md (SHA-256 recorded below).
Implements Parallel-Run Protocol Rule 2 (shared stack: SegmentHoldout /
DiagonalSegmentHoldout, CELF-300 m, submission_writer, validate_submission) and
Rule 4 (single-feature leakage canary).

The surface is label-free phase congruency (src/gemsdoe33/phcong.py). It never reads
the catalogue as a detector input; the catalogue is used only as the fold-visible
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

EVIDENCE = ROOT / "evidence" / "a33_r7_phcong_experiment_20261028.json"
RUN_CARD = ROOT / "evidence" / "a33_r7_phcong_run_card_20261028.json"
DOCS_CARD = ROOT / "docs" / "data" / "a33_r7_phcong_run_card_20261028.json"
PREREG = ROOT / "knowledge" / "27_phcong_slate_20261028.md"
PREREG_SHA = "f322a3b0c97f4af92d020cdbe13b908f8912a7723571c06a9f5c1a0be4b04d47"
MANIFEST = ROOT / "registry" / "focus_rasters_20261026.json"
UNIQ_OUT = ROOT / "evidence" / "a33_r7_phcong_uniqueness_20261028.json"
VALIDATOR_OUT = ROOT / "evidence" / "a33_r7_phcong_validator_20261028.json"
PROMO_OUT = ROOT / "evidence" / "a33_r7_phcong_promotion_evidence_20261028.json"
DATE = "20261028"
FAMILY = "gemsdoe33"
HYPOTHESIS = "a33-r7-phcong-37654"
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


def build_surface() -> tuple[np.ndarray, dict, dict]:
    from gemsdoe33.phcong import build_phcong_surface
    surface, parts = build_phcong_surface()
    return surface, {"detector": "monogenic phase congruency wl 4/8/16/32px, geomean(tmi,up150,grav) x orientation agreement"}, parts


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
    surface, fit, canary_parts = build_surface()

    holdout = csht_transfer.SegmentHoldout if hasattr(csht_transfer, "SegmentHoldout") else None
    from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
    holdout = SegmentHoldout(footprint, catalogue, buffer_px=BUFFER_PX)
    preds = emit_for(surface, holdout)

    # [1/4] leakage canary: the surface tested alone against withheld positives.
    canary = holdout.canary(canary_parts)
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

    rng = np.random.default_rng(20261028)
    ctrl_preds = []
    for fold in holdout.folds:
        valid, visible = fold["valid"], fold["visible"]
        d_vis = distance_transform_edt(~visible)
        eligible = valid & (d_vis > CATALOGUE_EXCLUSION_PX)
        budget = int(round(BUDGET_FRAC * int(valid.sum())))
        ctrl = csht_transfer.celf_emit_300m(rng.random(footprint.shape, dtype=np.float32),
                                            eligible, budget, min_self_spacing_px=2.5)
        ctrl_preds.append(ctrl.astype(np.uint8))
    vs_ctrl = holdout.compare_paired(preds, ctrl_preds, ci_draws=1999, seed=20261028)

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
        note_template="GEMS33 A33-R7-PHCONG: phase-congruency mag/grav edges x orientation, CELF300 37654d | gate pending | {cid}",
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
            f"GEMS33 A33-R7-PHCONG: phase-congruency mag/grav edges, CELF300 37654d | gate {verdict} | {{cid}}"
        ),
        scientific_verdict=verdict,
    )
    receipt_path = ROOT / "docs" / "downloads" / f"receipt-{receipt['submission_name']}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    _json_write(VALIDATOR_OUT, receipt)

    experiment_evidence = {
        "schema": 1, "campaign": "A33-R7-PHCONG", "date": DATE,
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
        "lane": "GEMSDOE33 phase-congruency potential-field edges (A33-R7-PHCONG)",
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
        "schema": 1, "campaign": "A33-R7-PHCONG", "date": DATE,
        "hypothesis": "Multiscale monogenic phase-congruency of tmi/up150/gravity x orientation agreement emits blind basement fault dots; label-free, catalogue-independent.",
        "mechanism": "Amplitude-invariant phase-coherent step edges in magnetics+gravity mark buried basement faults missing from USGS/INGENIOUS surface traces, where gradient magnitude is weak.",
        "named_non_fault_mimic": "Intrusive plutonic contacts, caldera ring margins and airborne survey line seams (genuine potential-field step edges).",
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
