#!/usr/bin/env python3
"""Experiment 1 (2026-10-29): deployment-density audit of the matched-random comparison.

Preregistered in knowledge/33_density_audit_preregistration_20261029.md (SHA-256 pinned below).

Question: does the PHCONG-vs-matched-random comparison recorded at the campaign's 2.5% per-fold
emission density (evidence/a33_r7_phcong_experiment_20261028.json) survive at the deployment
density (37,654 dots / template footprint)?

Shared tools only: vendor/gems24_template/holdout.py::SegmentHoldout (scoring and paired
bootstrap), gemsdoe33.csht_transfer.celf_emit_300m (placement), gemsdoe33.phcong
(label-free surface). The only varied quantity is the per-fold emission fraction.

Gates, in order (any failure halts with no deployment conclusion):
  G1 harness reproduction at 2.5%: screen DTI and matched-random DTI equal the recorded values.
  G2 leakage canary: every single feature AUC <= 0.90 (two-sided).
  G3 emitted maps are binary, zero outside the footprint, and match the footprint shape.

No DrivenData access. No slot. No submission file written.
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
sys.path = [str(ROOT), str(ROOT / "src")] + [p for p in sys.path if p not in (str(ROOT), str(ROOT / "src"))]

from gemsdoe33 import csht_transfer, grid  # noqa: E402
from gemsdoe33.phcong import build_phcong_surface  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402

PREREG = ROOT / "knowledge" / "33_density_audit_preregistration_20261029.md"
PREREG_SHA = "cd4a2b6a9b76cba383d1ee000868ddcca486ba5e7aede09407fc0ffac40981f0"
EVIDENCE = ROOT / "evidence" / "density_audit_20261029.json"
SEED = 20261028  # same seed as the campaign so the 2.5% numbers reproduce exactly
BUFFER_PX = 15
CATALOGUE_EXCLUSION_PX = 2.0
FULL_DOT_BUDGET = 37_654
CAMPAIGN_FRAC = 0.025
# Recorded values from evidence/a33_r7_phcong_experiment_20261028.json (for G1 only).
RECORDED_SCREEN_DTI = 0.16931590667916066
RECORDED_CTRL_DTI = 0.1804136278250649
REPRO_TOL = 1e-6
CANARY_MAX_AUC = 0.90


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def emit_fold_maps(surface: np.ndarray, holdout, frac: float, *, control: bool, footprint: np.ndarray):
    """Per-fold binary emissions at a given per-fold fraction of valid cells."""
    rng = np.random.default_rng(SEED)
    out = []
    for fold in holdout.folds:
        valid, visible = fold["valid"], fold["visible"]
        d_vis = distance_transform_edt(~visible)
        eligible = valid & (d_vis > CATALOGUE_EXCLUSION_PX)
        budget = int(round(frac * int(valid.sum())))
        score = rng.random(footprint.shape, dtype=np.float32) if control else surface
        dots = csht_transfer.celf_emit_300m(score, eligible, budget, min_self_spacing_px=2.5)
        out.append(dots.astype(np.uint8))
    return out


def check_format(maps: list[np.ndarray], footprint: np.ndarray) -> dict:
    ok_binary = all(np.isin(m, [0, 1]).all() for m in maps)
    ok_shape = all(m.shape == footprint.shape for m in maps)
    ok_outside = all(int(m[~footprint].sum()) == 0 for m in maps)
    return {"binary": bool(ok_binary), "shape_matches_footprint": bool(ok_shape),
            "zero_outside_footprint": bool(ok_outside)}


def run_density(label: str, frac: float, surface, parts, holdout, footprint) -> dict:
    t0 = time.monotonic()
    cand = emit_fold_maps(surface, holdout, frac, control=False, footprint=footprint)
    ctrl = emit_fold_maps(surface, holdout, frac, control=True, footprint=footprint)
    fmt_c, fmt_k = check_format(cand, footprint), check_format(ctrl, footprint)
    screen = holdout.summarize(cand, ci_draws=1999)
    ctrl_summary = holdout.summarize(ctrl, ci_draws=1999)
    paired = holdout.compare_paired(cand, ctrl, ci_draws=1999, seed=SEED)
    n_cand = int(sum(int(m.sum()) for m in cand))
    n_ctrl = int(sum(int(m.sum()) for m in ctrl))
    return {
        "label": label,
        "per_fold_fraction_of_valid_cells": frac,
        "emitted_dots_candidate_total": n_cand,
        "emitted_dots_control_total": n_ctrl,
        "format_candidate": fmt_c,
        "format_control": fmt_k,
        "candidate_screen_dti": float(screen["dti"]),
        "candidate_screen_ci95": screen["ci95"]["interval"],
        "control_dti": float(ctrl_summary["dti"]),
        "paired_delta_dti": float(paired["paired_delta_dti"]),
        "paired_delta_ci95": paired["paired_delta_ci95"],
        "fold_wins": int(paired["fold_wins"]),
        "n_folds": int(paired["n_folds"]),
        "evaluator_version": screen.get("evaluator_version"),
        "n_withheld_positive_pixels": int(screen.get("n_withheld_positive_pixels", -1)),
        "seconds": round(time.monotonic() - t0, 1),
    }


def main() -> int:
    actual = _sha(PREREG)
    if actual != PREREG_SHA:
        raise SystemExit(f"Preregistration changed: {actual} != {PREREG_SHA}")

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    n_fp = int(footprint.sum())
    dep_frac = FULL_DOT_BUDGET / n_fp
    print(f"footprint={n_fp} deployment fraction={dep_frac:.6f} campaign fraction={CAMPAIGN_FRAC}", flush=True)

    surface, parts = build_phcong_surface()
    holdout = SegmentHoldout(footprint, catalogue, buffer_px=BUFFER_PX)

    # G2 leakage canary on the surface and its components (single-feature AUC).
    canary = holdout.canary({"phcong_surface": surface, **{k: v for k, v in parts.items()}})
    max_auc = max(f["pooled_auc"] for f in canary["features"].values())
    max_auc_two_sided = max(max(v["pooled_auc"], 1.0 - v["pooled_auc"]) for v in canary["features"].values())
    print(f"[G2] canary max two-sided AUC={max_auc_two_sided:.4f} (max raw={max_auc:.4f})", flush=True)

    camp = run_density("campaign_2p5pct", CAMPAIGN_FRAC, surface, parts, holdout, footprint)
    print(f"[G1] campaign screen={camp['candidate_screen_dti']:.6f} control={camp['control_dti']:.6f}", flush=True)
    reproduces = (abs(camp["candidate_screen_dti"] - RECORDED_SCREEN_DTI) < REPRO_TOL and
                  abs(camp["control_dti"] - RECORDED_CTRL_DTI) < REPRO_TOL)

    dep = run_density("deployment", dep_frac, surface, parts, holdout, footprint)
    print(f"[dep] screen={dep['candidate_screen_dti']:.6f} control={dep['control_dti']:.6f} "
          f"delta={dep['paired_delta_dti']:.6f} CI={dep['paired_delta_ci95']} wins={dep['fold_wins']}/{dep['n_folds']}",
          flush=True)

    gates = {
        "G1_harness_reproduces_recorded_campaign": bool(reproduces),
        "G2_canary_max_two_sided_auc_le_0.90": bool(max_auc_two_sided <= CANARY_MAX_AUC),
        "G3_format_clean": bool(all(dep["format_candidate"].values()) and all(dep["format_control"].values())
                                and all(camp["format_candidate"].values()) and all(camp["format_control"].values())),
    }
    robust_signal = (
        dep["paired_delta_ci95"][0] > 0
        and dep["fold_wins"] >= 3
    )
    verdict = ("density-robust signal: re-run density-sensitive lanes at deployment density before any verdict"
               if robust_signal else
               "density-robust null: negative PHCONG verdict stands at both densities")
    if not all(gates.values()):
        verdict = "HALTED: a gate failed; no deployment conclusion"

    payload = {
        "schema": 1,
        "experiment": "GEMSDOE33 deployment-density audit (Experiment 1, 2026-10-29)",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "preregistration": {"path": str(PREREG.relative_to(ROOT)), "sha256": PREREG_SHA},
        "surface": "PHCONG label-free phase-congruency surface (src/gemsdoe33/phcong.py)",
        "holdout": {"class": "vendor.gems24_template.holdout.SegmentHoldout", "buffer_px": BUFFER_PX,
                    "evaluator_version": camp["evaluator_version"],
                    "n_withheld_positive_pixels": camp["n_withheld_positive_pixels"]},
        "footprint_cells": n_fp,
        "deployment_fraction": dep_frac,
        "campaign_fraction": CAMPAIGN_FRAC,
        "recorded_campaign_values": {"screen_dti": RECORDED_SCREEN_DTI, "control_dti": RECORDED_CTRL_DTI},
        "canary_max_two_sided_auc": max_auc_two_sided,
        "runs": {"campaign_2p5pct": camp, "deployment": dep},
        "gates": gates,
        "verdict": verdict,
        "labels": "HOLDOUT-DTI (gems-segment-pooled-v1; withheld positives in field above; 95% spatial-block CI). "
                  "Proxy only; not a leaderboard estimate.",
        "no_submission_written": True,
        "no_slot_used": True,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"verdict: {verdict}", flush=True)
    print(f"wrote {EVIDENCE.relative_to(ROOT)} sha256={_sha(EVIDENCE)}", flush=True)
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
