#!/usr/bin/env python3
"""Experiment 2: A33-R6-BASESTEP — buried listric-basement sole detector.

Preregistered candidate 4 of knowledge/26_thk_cond_slate_20261027.md
("A33-R5-BASESTEP", rank 4, viable, deferred by Experiment 1's budget). Re-ranked here as
this session's Experiment 2: a genuinely distinct physical axis (depth-to-basement step
as the LEADING term) that no repo lane has used as a primary detector; fully implementable
from SHA-256-verified staged inputs; label-free; low implementation cost.

Surface (label-free; every percentile threshold fit on catalogue-negative background
cells only — footprint & ~labels — so the catalogue is never a detector input):
    exceed(|grad depth_to_base_surf|)
  x exceed(cond_surf)
  x exceed(iso_grav_anom_hg)
  x exceed(ext_TMI_up150)

Physical signature: a sharp basement-depth step (listric fault sole / basement flexure)
coincident with conductive sedimentary cover and a gravity-mapped basin-margin edge, with
magnetic-basement fabric agreement. Blind or cover-buried listric soles have little or no
surface expression, so they are commonly missing from the USGS/INGENIOUS surface-trace
catalogue — this targets faults the catalogue does not map.

Named non-fault mimic: prograding alluvial fan toes, buried pediment fronts and
lithologic contacts can produce basement steps without displacement.

Distinction from prior repo work: CSHT used depth_to_base_surf as one of 34 channels
inside a catalogue-supervised HGB blend; HMDT used cond x TMI-gradient; DPPS used LiDAR
scarp persistence; THKCOND (Experiment 1) used radiometric Th/K as the leading term.
BASESTEP is the first label-free surface whose leading term is basement-depth geometry.

Holdout: whole-segment hide-and-recover (SegmentHoldout buffer 15 px quadrant screen +
DiagonalSegmentHoldout buffer 20 px confirmation), pooled DTI gems-segment-pooled-v1
(alpha 0.2, beta 0.8, 300 m triangular kernel), matched-random control on the screen,
single-feature leakage canary, full-footprint CELF-300 m emission at 37,654 dots,
pre-placement surface + final-dot duplicate screen vs the 21-raster registry, saved-byte
writer plus strict saved-byte format audit. No DrivenData access; no weekly slot
authorized; a negative result is an honest deliverable.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt, sobel

ROOT = Path(__file__).resolve().parents[1]
sys.path = [str(ROOT / "scripts"), str(ROOT), str(ROOT / "src")] + [
    p for p in sys.path if p not in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "src"))
]

from gemsdoe33 import csht_transfer, grid  # noqa: E402
from gemsdoe33.paths import CACHE_FEATURES  # noqa: E402
from submission_writer import write_pair  # noqa: E402

EVIDENCE = ROOT / "evidence" / "a33_r6_basestep_experiment_20261027.json"
RUN_CARD = ROOT / "evidence" / "a33_r6_basestep_run_card_20261027.json"
DOCS_CARD = ROOT / "docs" / "data" / "a33_r6_basestep_run_card_20261027.json"
PREREG = ROOT / "knowledge" / "26_thk_cond_slate_20261027.md"
MANIFEST = ROOT / "registry" / "focus_rasters_20261026.json"
UNIQ_OUT = ROOT / "evidence" / "a33_r6_basestep_uniqueness_20261027.json"
VALIDATOR_OUT = ROOT / "evidence" / "a33_r6_basestep_validator_20261027.json"
PROMO_OUT = ROOT / "evidence" / "a33_r6_basestep_promotion_evidence_20261027.json"
DATE = "20261027"
FAMILY = "gemsdoe33"
HYPOTHESIS = "a33-r6-basestep-37654"
BUFFER_PX = 15
CATALOGUE_EXCLUSION_PX = 2.0
FULL_DOT_BUDGET = 37_654
BUDGET_FRAC = 0.025
# Recorded incumbent context from the A33-R2-CSHT run card (NOT paired, NOT a score).
RECORDED_B1_SCREEN = 0.112418
RECORDED_B1_CONFIRM = 0.115122
PREREG_NOTE = ("A33-R5-BASESTEP (knowledge/26 candidate 4): depth_to_base_surf first "
               "derivative x ext_TMI_up150 x cond_surf x iso_grav_anom_hg")


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


def exceed(arr: np.ndarray, thr: float, bg: np.ndarray) -> np.ndarray:
    """Soft exceedance of ``thr`` scaled by background spread above threshold."""
    vals = arr[bg]
    vals = vals[np.isfinite(vals)]
    scale = float(np.percentile(vals, 95) - thr)
    if not np.isfinite(scale) or scale <= 0:
        scale = 1.0
    return np.clip((arr - thr) / scale, 0.0, 1.0)


def build_surface(arrays: dict) -> tuple[np.ndarray, dict]:
    """Label-free basement-step x conductive-cover x gravity-edge x magnetic-fabric surface."""
    fp = grid.template_footprint()
    labels = grid.load_labels() & fp
    background = fp & ~labels

    def pct(arr, q):
        v = arr[background]
        v = v[np.isfinite(v)]
        return float(np.percentile(v, q))

    d2b = arrays["depth_to_base_surf"]
    grad = np.hypot(sobel(d2b, axis=0), sobel(d2b, axis=1)).astype(np.float32)
    cond = arrays["cond_surf"]
    grav = arrays["iso_grav_anom_hg"]
    tmi = arrays["ext_TMI_up150"]

    t_grad, t_cond, t_grav, t_tmi = (pct(grad, 80), pct(cond, 80), pct(grav, 70), pct(tmi, 65))
    surface = (exceed(grad, t_grad, background) * exceed(cond, t_cond, background)
               * exceed(grav, t_grav, background) * exceed(tmi, t_tmi, background))
    surface = np.nan_to_num(surface, nan=0.0, posinf=1.0, neginf=0.0).astype(np.float32)
    return surface, {
        "grad_thr": t_grad, "cond_thr": t_cond, "grav_thr": t_grav, "tmi_thr": t_tmi,
        "leading_term": "|grad depth_to_base_surf|",
    }


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
    prereg_note_sha = hashlib.sha256(PREREG_NOTE.encode()).hexdigest()
    print(f"[0/6] preregistered candidate note: {PREREG_NOTE} (sha {prereg_note_sha[:12]})",
          flush=True)

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    arrays = {n: load_band(n) for n in ("cond_surf", "depth_to_base_surf",
                                        "iso_grav_anom_hg", "ext_TMI_up150")}
    surface, fit = build_surface(arrays)
    print(f"[1/6] surface built: {fit}", flush=True)

    from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
    holdout = SegmentHoldout(footprint, catalogue, buffer_px=BUFFER_PX)
    preds = emit_for(surface, holdout)

    # [2/6] leakage canary: the surface tested alone against withheld positives.
    canary = holdout.canary({"basement_step_surface": surface})
    canary_passed = bool(canary["passed"])
    two_sided = []
    for f in canary["features"].values():
        two_sided.append(max(f["pooled_auc"], 1.0 - f["pooled_auc"]))
        for d in f["folds"]:
            two_sided.append(max(d["auc"], 1.0 - d["auc"]))
    max_auc = max(two_sided)
    print(f"[2/6] canary max two-sided AUC={max_auc:.4f} passed={canary_passed}", flush=True)
    if not canary_passed:
        raise SystemExit("LEAKAGE CANARY TRIPPED (>0.90); halting.")

    # [3/6] quadrant screen + independent diagonal-wedge confirmation.
    screen = holdout.summarize(preds, ci_draws=1999)
    confirm_holdout = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=20)
    c_preds = emit_for(surface, confirm_holdout)
    confirm = confirm_holdout.summarize(c_preds, ci_draws=1999)

    # Matched-random control on the screen (same budget and eligibility per fold).
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
    print(f"[3/6] screen={screen['dti']:.6f} {screen['ci95']['interval']} "
          f"confirm={confirm['dti']:.6f} vs_ctrl={vs_ctrl['paired_delta_dti']:+.6f}",
          flush=True)

    # [4/6] full-footprint deployment + 21-raster uniqueness screen.
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
    print(f"[4/6] uniqueness surface_passed={uniq['surface']['passed']} "
          f"final_dots_passed={uniq['final_dots']['passed']} "
          f"max_dots_rho={uniq['final_dots']['max_abs_spearman_rho']:.4f} "
          f"max_3px={uniq['final_dots']['max_candidate_fraction_within_3px']:.4f}",
          flush=True)

    # [5/6] write the bundle with a pending note, then rewrite with the final verdict note.
    screen_gate = bool(screen["dti"] > RECORDED_B1_SCREEN
                       and screen["ci95"]["interval"][0] > RECORDED_B1_SCREEN)
    confirm_gate = bool(confirm["dti"] > RECORDED_B1_CONFIRM
                        and confirm["ci95"]["interval"][0] > RECORDED_B1_CONFIRM)
    uniq_ok = bool(uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
    promote = bool(screen_gate and confirm_gate and uniq_ok and canary_passed)
    verdict = "promote" if promote else "negative"

    note_template = ("GEMS33 A33-R6-BASESTEP: basement step x conductive cover x gravity "
                     f"edge, CELF300 37654d | gate {verdict} | {{cid}}")
    receipt = write_pair(
        final_dots.astype(np.float32),
        template=ROOT / "data" / "sample_submission.tif",
        catalogue=catalogue,
        footprint=footprint,
        outdir=ROOT / "docs" / "downloads",
        family=FAMILY,
        hypothesis=HYPOTHESIS,
        date=DATE,
        note_template=note_template,
        scientific_verdict=verdict,
    )
    fmt_ok = bool(receipt["primary_zero_outside"]["validator"]["format_valid"]
                  and receipt["official_text_nan_outside_twin"]["validator"]["format_valid"])
    zero_path = ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"]
    print(f"[5/6] format audit pass={fmt_ok} file={receipt['primary_zero_outside']['file']}",
          flush=True)

    _json_write(VALIDATOR_OUT, receipt)

    experiment_evidence = {
        "schema": 1, "campaign": "A33-R6-BASESTEP", "date": DATE,
        "preregistration_note": PREREG_NOTE,
        "preregistration_note_sha256": prereg_note_sha,
        "verdict": verdict,
        "screen": screen, "confirmation": confirm,
        "vs_matched_random": vs_ctrl,
        "leakage_canary": {"passed": canary_passed, "max_two_sided_auc": float(max_auc),
                           "features": canary["features"]},
        "uniqueness": uniq,
        "format_audit": {
            "zero_outside": receipt["primary_zero_outside"]["validator"],
            "nan_outside": receipt["official_text_nan_outside_twin"]["validator"],
            "all_checks_pass": bool(fmt_ok),
        },
        "raster_sha256": receipt["primary_zero_outside"]["sha256"],
        "nan_twin_sha256": receipt["official_text_nan_outside_twin"]["sha256"],
    }
    _json_write(EVIDENCE, experiment_evidence)

    promo_evidence = {
        "candidate_sha256": receipt["primary_zero_outside"]["sha256"],
        "lane": "GEMSDOE33 buried listric-basement sole detector (A33-R6-BASESTEP)",
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_note": PREREG_NOTE,
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
        "format_audit": experiment_evidence["format_audit"],
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
        "schema": 1, "campaign": "A33-R6-BASESTEP", "date": DATE,
        "hypothesis": ("Buried listric-basement sole detector: basement-depth-step x "
                       "conductive-cover x gravity-edge x magnetic-basement-fabric surface, "
                       "label-free, catalogue-independent; CELF-300 m emission."),
        "mechanism": ("Sharp basement-depth steps at conductive cover above gravity-mapped "
                      "basin-margin edges mark permeable blind faults missing from "
                      "USGS/INGENIOUS surface traces."),
        "named_non_fault_mimic": ("Prograding alluvial fan toes, buried pediment fronts and "
                                  "lithologic basement-contact steps without displacement."),
        "verdict": verdict,
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": csht_transfer.MTR_EVALUATOR_VERSION,
            "withheld_positives": int(screen["n_truth"]),
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
                                 "gates": promo_evidence["gates"],
                                 "failed_gates": [k for k, v in promo_evidence["gates"].items() if not v]},
        "runtime_seconds": round(time.monotonic() - t0, 2),
    }
    _json_write(RUN_CARD, run_card)
    _json_write(DOCS_CARD, run_card)
    print(json.dumps({"verdict": verdict, "screen_dti": screen["dti"],
                      "confirm_dti": confirm["dti"], "promote": promote}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
