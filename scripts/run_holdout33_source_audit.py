#!/usr/bin/env python3
"""Re-evaluate C2 with fold-specific catalogue and source-geometry masking.

The first Session-33 P1 run hid labels only during scoring; both its baseline
and C2 constructor still saw the full catalogue, and the C2 source vectors
included the held-out systems. That legacy result is retained separately but
is not a promotion gate. This runner rebuilds the H27-4 base from the labels
visible in each fold and excludes whole Qfaults feature IDs within the held-out
buffer before adding relay bridges.

The legacy H19-5 ridge raster is treated as a fixed feature-derived input.
Its upstream generation code is not present in this checkout, so the result is
still a conditional diagnostic, not an independently preregistered slot gate.
No DrivenData service is contacted.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems33.candidates import (  # noqa: E402
    _qfaults_tip_segments,
    c0_control,
    c2_stepover_bridges,
    exclude_source_fids_near_mask,
    h19_5_ridge,
    rebuild_c0_from_known,
)
from gems33.grid import (  # noqa: E402
    catalogue_systems,
    data_dir,
    fold_masks,
    load_catalogue,
    load_template,
)
from gems33.holdout import gate_summary, sgmc_off_catalogue_truth  # noqa: E402
from gems33.metric import dti_binary  # noqa: E402

FOLD_BUFFER_PX = 6
SOURCE_GUARD_PX = 1
SOURCE_SAMPLE_STEP_M = 50.0


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(out_path: Path) -> dict:
    footprint, grid = load_template()
    catalogue = load_catalogue()
    raw_ridge = h19_5_ridge() > 0
    control_reference = c0_control() > 0

    with rasterio.open(data_dir() / "core" / "sample_submission.tif") as template:
        affine = template.transform

    full_rebuild, full_rebuild_report = rebuild_c0_from_known(catalogue, raw_ridge)
    full_rebuild = full_rebuild > 0
    baseline_match = bool(np.array_equal(full_rebuild, control_reference))
    if not baseline_match:
        raise RuntimeError("fold-safe C0 reconstruction does not reproduce the pinned H27-4 control")

    segments = _qfaults_tip_segments()
    system_ids = catalogue_systems(catalogue, buffer_px=FOLD_BUFFER_PX)
    masks = fold_masks(system_ids, n_folds=4)
    folds = []
    for fold_id, hidden in enumerate(masks):
        hidden = np.asarray(hidden, dtype=bool) & footprint
        grown = binary_dilation(
            hidden,
            structure=np.ones((2 * FOLD_BUFFER_PX + 1, 2 * FOLD_BUFFER_PX + 1), dtype=bool),
        )
        known = catalogue & ~grown
        truth = hidden & footprint & ~known
        control, base_report = rebuild_c0_from_known(known, raw_ridge)

        excluded_fids, source_report = exclude_source_fids_near_mask(
            segments,
            hidden,
            affine,
            buffer_px=FOLD_BUFFER_PX,
            guard_px=SOURCE_GUARD_PX,
            sample_step_m=SOURCE_SAMPLE_STEP_M,
        )
        prediction, build_report = c2_stepover_bridges(
            base=control,
            catalogue_mask=known,
            source_segments=segments,
            excluded_source_fids=excluded_fids,
            source_exclusion_report=source_report,
        )
        candidate_metrics = dti_binary(prediction, truth, valid=footprint, known=known)
        control_metrics = dti_binary(control, truth, valid=footprint, known=known)
        delta = float(candidate_metrics["dti"] - control_metrics["dti"])
        folds.append({
            "fold": fold_id,
            "n_hidden_truth_pixels": int(truth.sum()),
            "n_known_pixels_after_buffer": int(known.sum()),
            "control_rebuild": base_report,
            "candidate_build": build_report,
            "candidate": {
                "dots": int((prediction > 0).sum()),
                "dti": float(candidate_metrics["dti"]),
                "tpw": float(candidate_metrics["TPw"]),
                "fpw": float(candidate_metrics["FPw"]),
            },
            "control": {
                "dots": int((control > 0).sum()),
                "dti": float(control_metrics["dti"]),
                "tpw": float(control_metrics["TPw"]),
                "fpw": float(control_metrics["FPw"]),
            },
            "incremental_contribution": {
                "delta_tpw": float(candidate_metrics["TPw"] - control_metrics["TPw"]),
                "delta_fpw": float(candidate_metrics["FPw"] - control_metrics["FPw"]),
                "added_dots": int((prediction > 0).sum() - (control > 0).sum()),
            },
            "delta_dti": delta,
        })
        print(
            f"[fold {fold_id}] truth={int(truth.sum()):,} "
            f"C0={int((control > 0).sum()):,} C2={int((prediction > 0).sum()):,} "
            f"delta={delta:+.7f} source_excluded={len(excluded_fids):,}",
            flush=True,
        )

    deltas = [row["delta_dti"] for row in folds]
    p1_mean = float(np.mean(deltas)) if deltas else None
    p1_positive = int(sum(value > 0 for value in deltas))
    incremental_tpw = [row["incremental_contribution"]["delta_tpw"] for row in folds]
    incremental_fpw = [row["incremental_contribution"]["delta_fpw"] for row in folds]
    incremental_added_dots = [row["incremental_contribution"]["added_dots"] for row in folds]

    # P2 is an independent SGMC off-catalogue proxy. It uses the production
    # candidate/control built from the catalogue that is available at inference.
    production_candidate, p2_build = c2_stepover_bridges(
        base=control_reference,
        catalogue_mask=catalogue,
        source_segments=segments,
    )
    p2_truth = sgmc_off_catalogue_truth(catalogue=catalogue, footprint=footprint)
    p2_candidate_metrics = dti_binary(production_candidate, p2_truth, valid=footprint, known=catalogue)
    p2_control_metrics = dti_binary(control_reference, p2_truth, valid=footprint, known=catalogue)
    p2_delta = float(p2_candidate_metrics["dti"] - p2_control_metrics["dti"])

    proxy_gate = gate_summary({
        "p1_mean_d_dti": p1_mean,
        "p1_positive_folds": p1_positive,
        "p1_n_folds": len(folds),
        "p2": {"d_dti": p2_delta},
    })

    qfault_shape = data_dir() / "external" / "faults_quaternary_INGENIOUS_regional_data" / "faults_quaternary_regional.shp"
    report = {
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "status": "CONDITIONAL_SOURCE_EXCLUSION_DIAGNOSTIC_NOT_SLOT_CLEARED",
        "protocol": (
            "P1 four spatial folds; rebuild H27-4 from each fold-visible catalogue; "
            "exclude each Qfaults source-system ID within a 600 m square holdout buffer "
            "plus one-pixel raster guard before bridge construction; P2 SGMC off-catalogue"
        ),
        "validity": {
            "previous_full_catalogue_p1_status": "WITHDRAWN_FOR_PROMOTION",
            "withdrawal_reason": (
                "The prior P1 runner masked labels only at scoring time. C0 pruning and C2 source/"
                "catalogue filters still saw full-catalogue geometry, and C2 used Qfaults traces for "
                "the hidden systems."
            ),
            "fold_specific_catalogue_mask_applied": True,
            "fold_specific_qfault_source_exclusion_applied": True,
            "legacy_h19_5_surface_rederived_per_fold": False,
            "legacy_h19_5_surface_provenance": (
                "The fixed H19-5 ridge raster is described in the owner-supplied campaign record as a "
                "scarp/geophysics ensemble; its upstream generation/training code is not in this checkout. "
                "This diagnostic cannot certify that upstream surface as fold-independent."
            ),
            "c2_threshold_preregistration_status": "not_demonstrated_in_repo",
            "slot_cleared": False,
            "slot_blockers": [
                "The legacy H19-5 input is not re-derived per fold and its upstream pipeline is not present.",
                "This corrective source-exclusion run was prompted by the earlier result and is not an independent preregistered confirmation.",
                "The pinned Qfaults community mirror is not byte-authenticated against the current official GDR archive.",
                "A passing local format audit is not portal acceptance or an organizer score.",
            ],
        },
        "grid": {
            "crs": grid.crs,
            "height": grid.height,
            "width": grid.width,
            "footprint_pixels": int(footprint.sum()),
        },
        "inputs": {
            "catalogue_pixels": int(catalogue.sum()),
            "h19_5_pixels": int(raw_ridge.sum()),
            "h19_5_sha256": _sha256_file(data_dir() / "models" / "h19_5_nan.tif"),
            "qfaults_shapefile_sha256": _sha256_file(qfault_shape),
            "qfaults_segments_in_footprint_margin": int(len(segments)),
            "full_label_c0_rebuild": {
                **full_rebuild_report,
                "matches_h27_4_control_exactly": baseline_match,
                "reference_control_dots": int(control_reference.sum()),
            },
        },
        "p1": {
            "fold_buffer_px": FOLD_BUFFER_PX,
            "source_guard_px": SOURCE_GUARD_PX,
            "source_exclusion_sample_step_m": SOURCE_SAMPLE_STEP_M,
            "mean_delta_dti": p1_mean,
            "positive_folds": p1_positive,
            "n_folds": len(folds),
            "fold_deltas": deltas,
            "incremental_contribution_summary": {
                "delta_tpw_total": float(np.sum(incremental_tpw)),
                "delta_fpw_total": float(np.sum(incremental_fpw)),
                "added_dots_total_across_folds": int(np.sum(incremental_added_dots)),
                "no_incremental_true_positive_weight_any_fold": bool(
                    all(abs(value) < 1e-12 for value in incremental_tpw)
                ),
            },
            "folds": folds,
            "status": "CONDITIONAL_DIAGNOSTIC_ONLY",
        },
        "p2": {
            "truth_pixels": int(p2_truth.sum()),
            "candidate_dti": float(p2_candidate_metrics["dti"]),
            "control_dti": float(p2_control_metrics["dti"]),
            "delta_dti": p2_delta,
            "candidate_dots": int((production_candidate > 0).sum()),
            "build": p2_build,
            "status": "INDEPENDENT_COMPILATION_PROXY_NOT_COMPETITION_TRUTH",
        },
        "numeric_proxy_gate": proxy_gate,
        "promotion": "NO SLOT: this run is conditional and not an independent preregistered confirmation.",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({"p1_mean_delta": p1_mean, "p1_positive_folds": p1_positive,
                      "p2_delta": p2_delta, "numeric_proxy_gate": proxy_gate,
                      "slot_cleared": False, "evidence": str(out_path)}, indent=1))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "evidence" / "holdout33.json")
    args = parser.parse_args()
    run(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
