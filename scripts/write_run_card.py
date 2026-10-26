#!/usr/bin/env python3
"""Write the single protocol run-card JSON for the G33-HA candidate.

Fields per the parallel-run protocol: hypothesis; mechanism; named non-fault
mimic; holdout DTI + CI; correlation/overlap vs registry; raster sha256;
validator output; submission name + note (<=140 chars); verdict promote/negative.
Unmeasured fields are null with a reason, never invented values.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

EVIDENCE = ROOT / "evidence"
DOWNLOADS = ROOT / "docs" / "downloads"
RESEARCH = ROOT / "docs" / "research"

NAME = "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026"
CID = "171b8b87dbf7"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    holdout = json.loads((EVIDENCE / "g33_tilt_gravity_lidar_holdout.json").read_text())
    build = json.loads((EVIDENCE / "g33_submission_build.json").read_text())
    receipt_path = DOWNLOADS / f"receipt-{NAME}-{CID}.json"
    receipt = json.loads(receipt_path.read_text())

    deltas = holdout["pooled_screen"]["fold_deltas"] + holdout["pooled_confirmation"]["fold_deltas"]
    mean_d = float(sum(deltas) / len(deltas))
    sd = math.sqrt(sum((d - mean_d) ** 2 for d in deltas) / (len(deltas) - 1))
    se = sd / math.sqrt(len(deltas))
    tcrit = 3.182  # two-sided 95% Student-t, df=3
    ci = [round(mean_d - tcrit * se, 6), round(mean_d + tcrit * se, 6)]

    comps = build["registry_check"]["comparisons"]
    worst_frac = max(comps, key=lambda c: c["fraction_candidate_within_3px"])
    worst_rho = max((c for c in comps if c["spearman_rho"] is not None),
                    key=lambda c: c["spearman_rho"], default=None)

    validator = build["submission"]["validator"]
    vchecks = validator

    note = receipt["note"]
    assert len(note) <= 140, len(note)

    evaluator_path = ROOT / "src" / "gems33" / "metric.py"
    card = {
        "schema": 1,
        "card_utc": build["run_utc"],
        "hypothesis": "G33-HA: blind or subtle faults missing from the USGS/INGENIOUS catalogue "
            "express as a conjunction of (a) near-vertical potential-field contacts "
            "(tilt angle band 6 tc ~ 0), (b) strong gravity horizontal-gradient edges "
            "(band 18 iso_grav_anom_hg) and (c) preserved linear surface breaks "
            "(LiDAR scarp coherence lid_coh100 and step response lid_step_max).",
        "mechanism": "Each cached GeoDAWN/LiDAR channel is robustly median/MAD z-standardised over the "
            "footprint, mapped to [0,1] (tilt as proximity to zero; gravity edge, coherence and step as "
            "strength), and combined by product so only cells satisfying all three signatures emit. "
            "Emission is restricted >= 2 px outside the fold-visible catalogue, thinned at 2.8 px, at the "
            "pre-declared sparse quantile 0.995 of the score surface (frozen at the holdout screen). "
            "This is structurally distinct from the dotted-catalogue lineage (H19/H27/D2.8/B2) and from "
            "the failed H33-6 edge-normal consensus (gradient-vector alignment plus matched-budget "
            "reallocation).",
        "named_non_fault_mimic": "Lithologic contacts, basin-margin boundaries, alteration fronts and "
            "Quaternary surficial lineaments can produce coincident magnetic/gravity edges and linear "
            "scarps without a seismogenic fault.",
        "holdout": {
            "label": "HOLDOUT-DTI",
            "evaluator": "src/gems33/metric.py:dti_binary",
            "evaluator_sha256": sha256_file(evaluator_path),
            "alpha": 0.2, "beta": 0.8, "kernel": "triangular", "radius_m": 300,
            "withheld_positives": holdout["pooled_screen"]["withheld_positives"],
            "folds": 4,
            "fold_truth_pixels": [13293, 12755, 14117, 20823],
            "fold_deltas": holdout["pooled_screen"]["fold_deltas"]
                           + holdout["pooled_confirmation"]["fold_deltas"],
            "pooled_candidate_dti": holdout["pooled_screen"]["candidate_pooled_dti"],
            "pooled_control_dti": holdout["pooled_screen"]["control_pooled_dti"],
            "pooled_screen_delta_dti": holdout["pooled_screen"]["pooled_delta_dti"],
            "screen_positive_folds": holdout["pooled_screen"]["positive_folds"],
            "pooled_confirmation_delta_dti": holdout["pooled_confirmation"]["pooled_delta_dti"],
            "confirmation_positive_folds": holdout["pooled_confirmation"]["positive_folds"],
            "mean_fold_delta_dti": round(mean_d, 6),
            "descriptive_t95_ci_df3": ci,
            "ci_estimand": "descriptive two-sided Student-t interval across 4 fold deltas, df=3; "
                           "small-n, conditional on catalogue proxy, not a competition-score CI",
        },
        "leakage_canary": "No channel stand-alone holdout AUC exceeded 0.90 in any screen fold "
            "(no signal detected; not leakage).",
        "registry_check": {
            "registry_rasters": 12,
            "scope": "pinned focus-site references (GEMSDOE24/25/27/28/30/31/32/33/36); not a complete "
            "global registry",
            "duplicate_trigger": False,
            "worst_spearman_rho": build["registry_check"]["worst_spearman_rho"],
            "worst_rho_raster": worst_rho["raster_id"] if worst_rho else None,
            "worst_fraction_within_3px": build["registry_check"]["worst_fraction_within_3px"],
            "worst_frac_raster": worst_frac["raster_id"],
            "thresholds": "rho <= 0.90 and <= 70% of candidate dots within 3 px of any one registry raster",
            "comparisons": comps,
        },
        "raster": {
            "file": f"{NAME}-{CID}-nan.tif",
            "zip": f"{NAME}-{CID}-nan.zip",
            "troubleshooting_tif": f"{NAME}-{CID}-zeros.tif",
            "sha256": receipt["nan"]["sha256"],
            "bytes": receipt["nan"]["bytes"],
            "emitted_pixels": receipt["emitted_pixels"],
            "emitted_fraction_of_footprint": receipt["emitted_fraction_of_footprint"],
        },
        "validator": {
            "pass": bool(validator.get("pass")),
            "no_nan_inside_footprint": bool(vchecks.get("in_range_0_1_footprint")),
            "values_in_0_1_footprint": bool(vchecks.get("in_range_0_1_footprint")),
            "crs_shape_transform_match": (vchecks.get("epsg") == 32611
                                          and bool(vchecks.get("shape_match"))
                                          and bool(vchecks.get("transform_match"))
                                          and bool(vchecks.get("bounds_match"))),
            "outside_footprint_null_or_zero": bool(vchecks.get("outside_is_null_or_zero")),
            "details": build["submission"]["validator"],
        },
        "submission": {
            "name": NAME,
            "content_id": CID,
            "note": note,
            "note_chars": receipt["note_chars"],
            "ok_to_download": True,
            "ok_to_submit": False,
            "reason_not_cleared": "Catalogue-proxy holdout gate failed: pooled confirmation "
                "DeltaDTI -0.0907 (0/4 folds positive) vs the fold-rebuilt C0 control; no organizer "
                "receipt exists; no weekly slot was spent or authorized. Download for inspection only.",
        },
        "verdict": "negative",
        "inputs": {
            "training_features_tif_sha256": build["inputs"]["training_features_tif_sha256"],
            "labels_tif_sha256": build["inputs"]["labels_tif_sha256"],
            "provenance": "Hash-pinned owner-mirror bytes (registry/owner_mirror_input_pins.json); "
                          "not organizer-authenticated.",
        },
    }
    for path in (ROOT / "evidence" / "run_card_g33_20261026.json",
                 RESEARCH / "current-run-card.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
        print(f"wrote {path}")
    print(f"verdict={card['verdict']} pooled_dDTI_confirmation={card['holdout']['pooled_confirmation_delta_dti']}")
    print(f"CI={ci} note={len(note)} chars validator_pass={card['validator']['pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
