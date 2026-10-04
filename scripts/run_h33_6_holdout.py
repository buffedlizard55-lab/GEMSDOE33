#!/usr/bin/env python3
"""Run the frozen H33-6 spatial proxy diagnostic; never contacts DrivenData.

The source H19-5 emission is a fixed owner-mirror feature raster. The runner
rebuilds the H27-4 control from each fold-visible catalogue, freezes the H33-6
edge score, and compares a matched-count location intervention with the
control and 10 content-blind random-location controls. Because the upstream
H19-5 surface is not re-derived per fold, every result is conditional and
cannot clear a weekly submission slot.
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

from gems33.candidates import c0_control, h19_5_ridge, rebuild_c0_from_known  # noqa: E402
from gems33.grid import (  # noqa: E402
    catalogue_systems,
    data_dir,
    fold_masks,
    load_catalogue,
    load_template,
)
from gems33.holdout import gate_summary, sgmc_off_catalogue_truth  # noqa: E402
from gems33.hypotheses import edge_consensus_score, read_feature_layers, reallocate_edge_budget  # noqa: E402
from gems33.metric import dti_binary  # noqa: E402

FOLD_BUFFER_PX = 6
SOURCE_GUARD_PX = 1
N_RANDOM_CONTROLS = 10
RANDOM_SEED_BASE = 20261004


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _metrics(prediction: np.ndarray, truth: np.ndarray, footprint: np.ndarray,
             known: np.ndarray) -> dict:
    measured = dti_binary(prediction, truth, valid=footprint, known=known)
    return {
        "dots": int((np.asarray(prediction) > 0).sum()),
        "dti": float(measured["dti"]),
        "tpw": float(measured["TPw"]),
        "fpw": float(measured["FPw"]),
        "fnw": float(measured["FNw"]),
        "n_truth": int(measured["n_truth"]),
    }


def run(out_path: Path) -> dict:
    footprint, grid = load_template()
    catalogue = load_catalogue()
    raw_ridge = h19_5_ridge() > 0
    control_reference = c0_control() > 0
    template_path = data_dir() / "core" / "sample_submission.tif"
    feature_path = data_dir() / "core" / "training_features.tif"
    prereg_path = ROOT / "evidence" / "hypothesis_slate_20261004_preregistered.json"
    with rasterio.open(template_path) as template:
        affine = template.transform
    with rasterio.open(feature_path) as feature_ds:
        feature_grid = {
            "width": feature_ds.width,
            "height": feature_ds.height,
            "crs": feature_ds.crs.to_string() if feature_ds.crs else None,
            "transform": list(feature_ds.transform)[:6],
        }

    full_rebuild, full_rebuild_report = rebuild_c0_from_known(catalogue, raw_ridge)
    full_rebuild = full_rebuild > 0
    baseline_match = bool(np.array_equal(full_rebuild, control_reference))
    if not baseline_match:
        raise RuntimeError("fold-safe C0 reconstruction does not reproduce the pinned H27-4 control")
    if np.any(control_reference & ~footprint):
        raise RuntimeError("H27-4 reference emits outside the template footprint")

    layers, nodata, band_metadata = read_feature_layers(feature_path, footprint)
    score, local_maxima, score_report = edge_consensus_score(
        layers, footprint, sigma_px=2.0, nodata=nodata,
    )
    # Release the multi-band source arrays before fold masks and distance grids
    # add to memory pressure. The score and its pixel-level summary are frozen.
    del layers

    systems = catalogue_systems(catalogue, buffer_px=FOLD_BUFFER_PX)
    masks = fold_masks(systems, n_folds=4)
    folds = []
    all_random_deltas: list[float] = []

    for fold_id, fold_mask in enumerate(masks):
        hidden = np.asarray(fold_mask, dtype=bool) & footprint
        grown = binary_dilation(
            hidden,
            structure=np.ones((2 * FOLD_BUFFER_PX + 1, 2 * FOLD_BUFFER_PX + 1), dtype=bool),
        )
        known = catalogue & ~grown
        truth = hidden & ~known
        control, control_build = rebuild_c0_from_known(known, raw_ridge)
        control = control > 0
        candidate, candidate_build = reallocate_edge_budget(
            control, known, footprint, score, local_maxima,
        )
        candidate_metrics = _metrics(candidate, truth, footprint, known)
        control_metrics = _metrics(control, truth, footprint, known)
        candidate_delta = candidate_metrics["dti"] - control_metrics["dti"]

        random_rows = []
        for sample_id in range(N_RANDOM_CONTROLS):
            seed = RANDOM_SEED_BASE + fold_id * 100 + sample_id
            random_prediction, random_build = reallocate_edge_budget(
                control, known, footprint, score, local_maxima, random_seed=seed,
            )
            random_metrics = _metrics(random_prediction, truth, footprint, known)
            delta = random_metrics["dti"] - control_metrics["dti"]
            all_random_deltas.append(float(delta))
            random_rows.append({
                "sample": sample_id,
                "seed": seed,
                "build": random_build,
                "metrics": random_metrics,
                "delta_dti_vs_control": float(delta),
            })

        folds.append({
            "fold": fold_id,
            "heldout_truth_pixels": int(truth.sum()),
            "known_pixels_after_buffer": int(known.sum()),
            "control_rebuild": control_build,
            "candidate_build": candidate_build,
            "candidate": candidate_metrics,
            "control": control_metrics,
            "candidate_delta_dti": float(candidate_delta),
            "matched_random_controls": random_rows,
            "matched_random_mean_delta_dti": float(np.mean([r["delta_dti_vs_control"] for r in random_rows])),
            "candidate_beats_random_mean": bool(
                candidate_delta > np.mean([r["delta_dti_vs_control"] for r in random_rows])
            ),
        })
        print(
            f"[fold {fold_id}] truth={int(truth.sum()):,} "
            f"control={control_metrics['dots']:,} H33-6={candidate_metrics['dots']:,} "
            f"delta={candidate_delta:+.7f} random_mean="
            f"{folds[-1]['matched_random_mean_delta_dti']:+.7f}",
            flush=True,
        )

    p1_deltas = [row["candidate_delta_dti"] for row in folds]
    p1_mean = float(np.mean(p1_deltas)) if p1_deltas else None
    p1_positive = int(sum(delta > 0.0 for delta in p1_deltas))
    random_mean = float(np.mean(all_random_deltas)) if all_random_deltas else None

    production_candidate, production_build = reallocate_edge_budget(
        control_reference, catalogue, footprint, score, local_maxima,
    )
    p2_truth = sgmc_off_catalogue_truth(catalogue=catalogue, footprint=footprint)
    p2_candidate = _metrics(production_candidate, p2_truth, footprint, catalogue)
    p2_control = _metrics(control_reference, p2_truth, footprint, catalogue)
    p2_delta = float(p2_candidate["dti"] - p2_control["dti"])

    numeric = gate_summary({
        "p1_mean_d_dti": p1_mean,
        "p1_positive_folds": p1_positive,
        "p1_n_folds": len(folds),
        "p2": {"d_dti": p2_delta},
    })
    random_beaten = bool(random_mean is not None and p1_mean is not None and p1_mean > random_mean)
    numeric["mean_p1_beats_matched_random"] = random_beaten
    numeric["pass"] = bool(numeric.get("pass") and random_beaten)

    feature_description = "owner-mirror training_features.tif; band identities checked by embedded descriptions"
    report = {
        "schema": 1,
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "candidate": "H33-6 cross-physics edge-normal consensus with matched-budget reallocation",
        "status": "CONDITIONAL_NUMERIC_PASS_NOT_SLOT_CLEARED" if numeric["pass"] else "CONDITIONAL_GATE_FAIL_NOT_SLOT_CLEARED",
        "slot_cleared": False,
        "promotion_decision": "NO_SLOT; conditional diagnostics cannot establish fold independence of the fixed H19-5 source or validate on private expert labels",
        "protocol": {
            "preregistration": "evidence/hypothesis_slate_20261004_preregistered.json",
            "preregistration_sha256": _sha256(prereg_path),
            "input_data_provenance": "owner-published mirror; hashes establish mirror-byte identity only, not organizer origin",
            "p1": "four 2x2 spatial folds of 600 m buffered catalogue systems; rebuild H27-4 from fold-visible catalogue; candidate model sees no held-out fold mask; score on held-out catalogue pixels only",
            "p1_buffer_pixels": FOLD_BUFFER_PX,
            "source_raster_guard_pixels": SOURCE_GUARD_PX,
            "p2": "SGMC compiled fault pixels at least 3 px from supplied catalogue, evaluated against full-data candidate/control",
            "matched_random_controls_per_fold": N_RANDOM_CONTROLS,
            "matched_random_seed_base": RANDOM_SEED_BASE,
            "edge_recipe": score_report["algorithm"],
            "edge_sigma_pixels": 2.0,
            "replacement_fraction": 0.05,
            "replacement_count_rule": "floor(0.05 * in-footprint control dots)",
            "addition_spacing_pixels": 2.8,
            "tie_break": "row-major cell index for score ties",
            "official_score_claim": "No score claim; all results are catalogue/SGMC proxy diagnostics only.",
        },
        "validity": {
            "full_data_control_rebuilt": baseline_match,
            "fold_specific_catalogue_mask_applied": True,
            "candidate_uses_heldout_catalogue_mask": False,
            "fixed_h19_5_surface_rederived_per_fold": False,
            "fixed_h19_5_sha256": _sha256(data_dir() / "models" / "h19_5_nan.tif"),
            "h19_5_upstream_code_present": False,
            "h19_5_caveat": "H19-5 is an owner-mirror feature-derived raster with unavailable upstream model/provenance; it could encode catalogue information. The fold rebuilding cannot certify it as independent of held-out labels.",
            "independent_confirmation_run": False,
            "candidate_p1_beats_current_comparable_control": bool(p1_mean is not None and p1_mean > 0),
            "slot_blockers": [
                "The fixed H19-5 emission surface is not re-derived per fold and its upstream model/training code is absent.",
                "Owner-mirror input provenance is not organizer-authenticated.",
                "The P1 catalogue and P2 SGMC layers are proxy labels, not private expert truth.",
                "A single preregistered screen is not an independent fresh-seed confirmation.",
                "A local GeoTIFF format check cannot prove portal acceptance or a score/file association.",
            ],
        },
        "grid": {
            "crs": grid.crs,
            "height": grid.height,
            "width": grid.width,
            "footprint_pixels": int(footprint.sum()),
            "feature_grid": feature_grid,
        },
        "inputs": {
            "catalogue_pixels": int(catalogue.sum()),
            "h19_5_pixels": int(raw_ridge.sum()),
            "h19_5_sha256": _sha256(data_dir() / "models" / "h19_5_nan.tif"),
            "training_features_sha256": _sha256(feature_path),
            "feature_data_source": feature_description,
            "bands": band_metadata,
            "baseline_reconstruction": {
                **full_rebuild_report,
                "matches_reference_exactly": baseline_match,
                "reference_dots": int(control_reference.sum()),
                "outside_footprint_dots": int((control_reference & ~footprint).sum()),
            },
        },
        "edge_score": score_report,
        "p1": {
            "mean_delta_dti": p1_mean,
            "positive_folds": p1_positive,
            "n_folds": len(folds),
            "fold_deltas": p1_deltas,
            "matched_random_mean_delta_dti": random_mean,
            "candidate_mean_delta_exceeds_random_mean": random_beaten,
            "folds": folds,
        },
        "p2": {
            "truth_pixels": int(p2_truth.sum()),
            "candidate": p2_candidate,
            "control": p2_control,
            "delta_dti": p2_delta,
            "production_candidate_build": production_build,
        },
        "numeric_gate": numeric,
        "artifacts": {
            "research_prediction": "not built by this holdout runner",
            "recommended_submission": None,
            "slot_spent": False,
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"P1 mean ΔDTI={p1_mean:+.7f}; P2 ΔDTI={p2_delta:+.7f}; numeric_gate={numeric['pass']}")
    resolved_out = out_path.resolve()
    try:
        display_out = resolved_out.relative_to(ROOT).as_posix()
    except ValueError:
        display_out = str(resolved_out)
    print(f"wrote {display_out}; slot_cleared=False")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "evidence" / "holdout_h33_6.json"))
    args = parser.parse_args()
    report = run(Path(args.out))
    return 0 if report["numeric_gate"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
