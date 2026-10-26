#!/usr/bin/env python3
"""Run the one frozen A33-L1 analog-transfer experiment end to end.

The shared numerical evaluator and writer are pinned template snapshots. This
script adds only the lane-specific feature/model construction and orchestration.
It performs no DrivenData upload and cannot spend a weekly slot.
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

from gemsdoe33 import analog, analog_invariant, emission, grid, novelty  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402
from vendor.gems24_template.validator import sha256_file  # noqa: E402

EVIDENCE = ROOT / "evidence" / "a33_l1_experiment.json"
RUN_CARD = ROOT / "evidence" / "a33_l1_run_card.json"
DOCS_CARD = ROOT / "docs" / "data" / "a33_l1_run_card.json"
PREREG = ROOT / "evidence" / "analog_lane_preregistration_20261025.json"
PREREG_SHA = "fa30ed9c567a9802cd6053ff1831e18ce0556f78a1e62f9f769e812d4ad4a06d"
FULL_DOT_BUDGET = 37_654
MIN_SPACING_PX = 2.8
CATALOGUE_EXCLUSION_PX = 2.0
BUFFER_PX = 15
DATE = "20261025"


def _json_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def _verify_preregistration() -> None:
    actual = sha256_file(PREREG)
    if actual != PREREG_SHA:
        raise SystemExit(
            f"Frozen preregistration changed: {actual} != {PREREG_SHA}; refusing to run"
        )


def _restore_registry() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "cache_focus_registry.py")],
        cwd=ROOT,
        check=True,
    )


def _emit(score: np.ndarray, eligible: np.ndarray, budget: int) -> np.ndarray:
    dots = emission.dot_thin(
        eligible,
        MIN_SPACING_PX,
        priority=score,
        max_dots=budget,
    )
    if int(dots.sum()) != budget:
        raise RuntimeError(f"Emission underfilled: {int(dots.sum())} != {budget}")
    return dots


def _fit_scores(
    arrays: dict[str, np.ndarray],
    masks: analog.AnalogMasks,
    domain: np.ndarray,
    train: np.ndarray,
    visible: np.ndarray,
    *,
    seed: int,
) -> tuple[dict[str, np.ndarray], dict]:
    distance = distance_transform_edt(~visible)
    regional = analog_invariant.fit_regional_expert(
        arrays, train, visible, distance, seed=seed + 1
    )
    raw = analog_invariant.fit_raw_analog_expert(
        arrays, train, visible, distance, masks, seed=seed + 2
    )
    adapted = analog_invariant.fit_adapted_analog_expert(
        arrays, train, visible, distance, masks, seed=seed + 3
    )
    regional_score = analog_invariant.predict(regional, arrays, domain)
    raw_score = analog_invariant.predict(raw, arrays, domain)
    adapted_score = analog_invariant.predict(adapted, arrays, domain)
    candidate = analog_invariant.fuse(regional_score, adapted_score, domain)
    return (
        {
            "B0_raw_analog": raw_score,
            "B1_regional": regional_score,
            "A33_L1": candidate,
        },
        {
            "B0_raw_analog": raw.report,
            "B1_regional": regional.report,
            "A33_L1_adapted_expert": adapted.report,
        },
    )


def _verify_recorded() -> int:
    if not EVIDENCE.is_file() or not RUN_CARD.is_file():
        raise SystemExit("No recorded A33-L1 experiment to verify")
    evidence = json.loads(EVIDENCE.read_text())
    card = json.loads(RUN_CARD.read_text())
    artifact = ROOT / "docs" / "downloads" / card["submission"]["file"]
    checks = {
        "evidence_exists": True,
        "run_card_exists": True,
        "artifact_exists": artifact.is_file(),
        "artifact_sha256_matches": artifact.is_file()
        and sha256_file(artifact) == card["raster_sha256"],
        "preregistration_sha256_matches": sha256_file(PREREG) == PREREG_SHA,
        "recorded_verdict_matches": evidence["verdict"] == card["verdict"],
    }
    print(json.dumps({"checks": checks, "pass": all(checks.values())}, indent=2))
    return 0 if all(checks.values()) else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-recorded", action="store_true")
    args = parser.parse_args()
    if args.verify_recorded:
        return _verify_recorded()
    if EVIDENCE.exists() or RUN_CARD.exists():
        raise SystemExit(
            "A33-L1 is already recorded; no implicit rerun or tuning. Use --verify-recorded."
        )

    started = time.monotonic()
    _verify_preregistration()
    _restore_registry()
    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    arrays = analog_invariant.load_feature_arrays()
    masks = analog.build_analog_masks(footprint)
    context = SegmentHoldout(footprint, catalogue, buffer_px=BUFFER_PX)

    report: dict = {
        "schema": 1,
        "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "RUNNING",
        "experiment_number": 1,
        "maximum_experiments": 3,
        "submission_slots_used": 0,
        "hypothesis": "A33-L1 target-aligned, field-balanced structural transfer",
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_sha256": PREREG_SHA,
        "evaluator": {
            "version": "gems-segment-pooled-v1",
            "source": "vendor/gems24_template/holdout.py",
            "source_manifest": "vendor/gems24_template/SOURCE.json",
        },
        "input_provenance": (
            "SHA-256-pinned GitHub owner mirrors; not independently organizer-authenticated"
        ),
        "feature_names": list(analog_invariant.FEATURE_NAMES),
        "feature_cache_sha256": analog_invariant.feature_source_hashes(),
        "analog_inventory": analog.analog_inventory(masks, catalogue, footprint),
        "fold_integrity": [
            {
                "fold": fold["name"],
                "withheld_positive_pixels": int(fold["truth"].sum()),
                "withheld_components": int(len(fold["hidden_component_ids"])),
                "visible_fault_pixels": int(fold["visible"].sum()),
                "training_pixels": int(fold["train"].sum()),
                "training_validation_overlap": bool((fold["train"] & fold["valid"]).any()),
                "truth_visible_overlap": int((fold["truth"] & fold["visible"]).sum()),
            }
            for fold in context.folds
        ],
    }
    _json_write(EVIDENCE, report)

    print("[1/6] Leakage canaries for all 12 frozen source features", flush=True)
    report["leakage_canary"] = context.canary(arrays)
    _json_write(EVIDENCE, report)
    if not report["leakage_canary"]["passed"]:
        report.update(
            status="STOPPED_LEAKAGE_CANARY",
            verdict="negative",
            verdict_reason="At least one feature-alone AUC exceeded 0.90",
            elapsed_seconds=round(time.monotonic() - started, 2),
        )
        _json_write(EVIDENCE, report)
        raise SystemExit("Leakage canary failed; stopped before surface fitting/placement")

    print("[2/6] Full-data A33-L1 score and pre-placement registry guard", flush=True)
    full_scores, full_fit = _fit_scores(
        arrays,
        masks,
        footprint,
        footprint,
        catalogue,
        seed=3300,
    )
    full_surface = full_scores["A33_L1"]
    np.save(ROOT / ".cache" / "a33_l1_full_surface.npy", full_surface)
    report["full_fit"] = full_fit
    report["surface_duplicate_guard"] = novelty.compare_surface(full_surface, footprint)
    _json_write(EVIDENCE, report)
    if not report["surface_duplicate_guard"]["passed"]:
        report.update(
            status="STOPPED_DUPLICATE_SURFACE",
            verdict="negative",
            verdict_reason="Surface Spearman duplicate threshold exceeded",
            elapsed_seconds=round(time.monotonic() - started, 2),
        )
        _json_write(EVIDENCE, report)
        raise SystemExit("Surface duplicate guard triggered; stopped before placement")

    print("[3/6] Four buffered whole-component folds; matched operators/budgets", flush=True)
    predictions = {"B0_raw_analog": [], "B1_regional": [], "A33_L1": [], "matched_random": []}
    fold_fits = []
    fold_budgets = []
    for fold_index, fold in enumerate(context.folds):
        scores, fits = _fit_scores(
            arrays,
            masks,
            fold["valid"],
            fold["train"],
            fold["visible"],
            seed=3310 + fold_index * 10,
        )
        d_visible = distance_transform_edt(~fold["visible"])
        eligible = fold["valid"] & (d_visible > CATALOGUE_EXCLUSION_PX)
        budget = int(round(FULL_DOT_BUDGET * fold["valid"].sum() / footprint.sum()))
        fold_budgets.append(budget)
        for name in ("B0_raw_analog", "B1_regional", "A33_L1"):
            predictions[name].append(_emit(scores[name], eligible, budget))
        rng = np.random.default_rng(20261025 + fold_index)
        random_score = np.zeros(footprint.shape, dtype=np.float32)
        random_score[eligible] = rng.random(int(eligible.sum()), dtype=np.float32)
        predictions["matched_random"].append(_emit(random_score, eligible, budget))
        fold_fits.append({"fold": fold["name"], "budget": budget, "models": fits})
        print(f"  {fold['name']}: budget={budget:,}", flush=True)
    report["fold_model_fits"] = fold_fits
    report["fold_budgets"] = fold_budgets

    print("[4/6] Pooled HOLDOUT-DTI and paired spatial-block bootstrap", flush=True)
    results = {
        name: context.summarize(preds)
        for name, preds in predictions.items()
    }
    comparisons = {
        name: context.compare_paired(predictions["A33_L1"], predictions[name])
        for name in ("B0_raw_analog", "B1_regional")
    }
    best_baseline = max(
        ("B0_raw_analog", "B1_regional"),
        key=lambda name: results[name]["dti"],
    )
    best_comparison = comparisons[best_baseline]
    scientific_gate = {
        "beats_B0_raw_analog": results["A33_L1"]["dti"] > results["B0_raw_analog"]["dti"],
        "beats_B1_regional": results["A33_L1"]["dti"] > results["B1_regional"]["dti"],
        "best_comparable_baseline": best_baseline,
        "paired_delta_ci95_strictly_positive": best_comparison["ci95_strictly_positive"],
        "fold_wins_at_least_3_of_4": best_comparison["fold_wins"] >= 3,
        "leakage_canary_passed": report["leakage_canary"]["passed"],
        "surface_uniqueness_passed": report["surface_duplicate_guard"]["passed"],
    }
    scientific_gate["passed_before_final_uniqueness"] = all(
        scientific_gate[key]
        for key in (
            "beats_B0_raw_analog",
            "beats_B1_regional",
            "paired_delta_ci95_strictly_positive",
            "fold_wins_at_least_3_of_4",
            "leakage_canary_passed",
            "surface_uniqueness_passed",
        )
    )
    report["holdout_results"] = results
    report["paired_comparisons"] = comparisons
    report["scientific_gate"] = scientific_gate
    _json_write(EVIDENCE, report)
    for name in ("B0_raw_analog", "B1_regional", "A33_L1", "matched_random"):
        row = results[name]
        print(
            f"  {name}: HOLDOUT-DTI ({row['evaluator_version']}, "
            f"n={row['n_withheld_positive_pixels']:,}, 95% CI={row['ci95']['interval']}) "
            f"{row['dti']:.6f}",
            flush=True,
        )

    print("[5/6] Final unique dots and exact registry guard", flush=True)
    d_catalogue = distance_transform_edt(~catalogue)
    final_eligible = footprint & (d_catalogue > CATALOGUE_EXCLUSION_PX)
    final_dots = _emit(full_surface, final_eligible, FULL_DOT_BUDGET)
    np.save(ROOT / ".cache" / "a33_l1_final_dots.npy", final_dots)
    report["final_duplicate_guard"] = novelty.compare_final_dots(final_dots, footprint)
    _json_write(EVIDENCE, report)
    if not report["final_duplicate_guard"]["passed"]:
        report.update(
            status="STOPPED_DUPLICATE_FINAL_DOTS",
            verdict="negative",
            verdict_reason="Final-dot registry duplicate threshold exceeded; no TIFF written",
            elapsed_seconds=round(time.monotonic() - started, 2),
        )
        _json_write(EVIDENCE, report)
        raise SystemExit("Final-dot duplicate guard triggered; stopped without GeoTIFF")

    print("[6/6] Shared writer, saved-byte validation, run card", flush=True)
    promote = bool(scientific_gate["passed_before_final_uniqueness"])
    verdict = "promote" if promote else "negative"
    note_template = (
        "A33-L1 analog-CDF fusion 37654d | holdout gate "
        + ("PASS" if promote else "FAIL")
        + " | research; selector not run | {cid}"
    )
    receipt = write_pair(
        final_dots.astype(np.float32),
        template=ROOT / "data" / "sample_submission.tif",
        catalogue=catalogue,
        footprint=footprint,
        outdir=ROOT / "docs" / "downloads",
        family="gemsdoe33",
        hypothesis="a33-l1-analog-transfer-research-37654",
        date=DATE,
        note_template=note_template,
        scientific_verdict=verdict,
    )
    best = results[best_baseline]
    candidate = results["A33_L1"]
    validator = receipt["primary_zero_outside"]["validator"]
    run_card = {
        "schema": 1,
        "hypothesis": (
            "A33-L1: field-balanced source-CDF alignment plus a regional visible-fault expert "
            "may transfer a portable cross-physics fault signature from named geothermal fields."
        ),
        "mechanism": (
            "Map each source field's structural-feature marginals onto the fold-training target, "
            "equalize field loss, and fuse adapted-analog and regional score ranks at 0.20/0.80."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Lithologic contact or basin-fill boundary can generate coincident magnetic, gravity, "
            "basement-depth and conductivity discontinuities without fault displacement."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": candidate["evaluator_version"],
            "withheld_positives": candidate["n_withheld_positive_pixels"],
            "candidate": candidate["dti"],
            "candidate_95pct_ci": candidate["ci95"],
            "best_comparable_baseline_name": best_baseline,
            "best_comparable_baseline": best["dti"],
            "best_baseline_95pct_ci": best["ci95"],
            "paired_delta": best_comparison["paired_delta_dti"],
            "paired_delta_95pct_ci": best_comparison["paired_delta_ci95"],
            "fold_wins": best_comparison["fold_wins"],
            "qualification": (
                "Mapped-catalogue hide-and-recover proxy, not private expert truth and not an "
                "organizer score. Source labels are not independent field-verified analog labels."
            ),
        },
        "correlation_overlap_vs_registry": {
            "scope": "nine pinned focus-site owner rasters",
            "surface": report["surface_duplicate_guard"],
            "final_dots": report["final_duplicate_guard"],
        },
        "raster_sha256": receipt["primary_zero_outside"]["sha256"],
        "validator_output": {
            "format_valid": validator["format_valid"],
            "hard_failures": validator["hard_failures"],
            "no_nan_inside_footprint": validator["checks"]["footprint_all_finite"]["pass"],
            "values_in_0_1": validator["checks"]["footprint_range_0_1"]["pass"],
            "crs_matches": validator["checks"]["crs_epsg_32611"]["pass"],
            "shape_matches": validator["checks"]["shape_matches_template"]["pass"],
            "transform_matches": validator["checks"]["geotransform_matches_template"]["pass"],
            "whole_array_all_finite_0_1": validator["checks"][
                "variant_strict_whole_array_no_nan_allowed"
            ]["pass"],
            "format_validation_is_not_portal_acceptance": True,
        },
        "submission": {
            "name": receipt["submission_name"],
            "file": receipt["primary_zero_outside"]["file"],
            "nan_twin": receipt["official_text_nan_outside_twin"]["file"],
            "note": receipt["note"],
            "note_characters": receipt["note_characters"],
            "ok_to_download": True,
            "ok_to_submit": False,
            "why_not_submit": (
                "Scientific holdout gate failed; do not spend a slot."
                if not promote
                else "Technical/scientific gate passed, but the required separate weekly-slot selector has not run."
            ),
        },
        "verdict": verdict,
        "scientific_gate": scientific_gate,
        "experiments_run": 1,
        "submission_slots_used": 0,
    }
    _json_write(RUN_CARD, run_card)
    _json_write(DOCS_CARD, run_card)
    report.update(
        status="COMPLETED",
        verdict=verdict,
        run_card=str(RUN_CARD.relative_to(ROOT)),
        submission_receipt=receipt,
        elapsed_seconds=round(time.monotonic() - started, 2),
        completed_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    _json_write(EVIDENCE, report)
    print(
        json.dumps(
            {
                "verdict": verdict,
                "file": receipt["primary_zero_outside"]["file"],
                "sha256": receipt["primary_zero_outside"]["sha256"],
                "ok_to_download": True,
                "ok_to_submit": False,
                "HOLDOUT-DTI": candidate["dti"],
                "HOLDOUT-DTI_95pct_CI": candidate["ci95"]["interval"],
                "withheld_positives": candidate["n_withheld_positive_pixels"],
            },
            indent=2,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
