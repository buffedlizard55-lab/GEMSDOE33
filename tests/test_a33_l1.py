"""Frozen A33-L1 evidence and deliverable integrity checks."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PREREG_SHA = "fa30ed9c567a9802cd6053ff1831e18ce0556f78a1e62f9f769e812d4ad4a06d"
EXPECTED_TIF_SHA = "2bbbf7e381720f2242959e3efd6f2437f273afe6e7c48540d769524d2b4e8759"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_card() -> dict:
    return json.loads((ROOT / "evidence/a33_l1_run_card.json").read_text())


def test_preregistration_is_still_byte_frozen():
    prereg = ROOT / "evidence/analog_lane_preregistration_20261025.json"
    assert digest(prereg) == EXPECTED_PREREG_SHA
    frozen = (ROOT / "evidence/analog_lane_preregistration_20261025.sha256").read_text()
    assert EXPECTED_PREREG_SHA in frozen


def test_run_card_is_negative_and_uses_required_holdout_label():
    card = load_card()
    result = card["holdout_dti"]
    assert card["verdict"] == "negative"
    assert result["label"] == "HOLDOUT-DTI"
    assert result["evaluator_version"] == "gems-segment-pooled-v1"
    assert result["withheld_positives"] == 60_988
    assert result["candidate"] < result["best_comparable_baseline"]
    assert result["paired_delta"] < 0
    assert result["paired_delta_95pct_ci"][0] < 0 < result["paired_delta_95pct_ci"][1]
    assert result["fold_wins"] == 0
    assert card["submission"]["ok_to_download"] is True
    assert card["submission"]["ok_to_submit"] is False
    assert card["submission"]["note_characters"] <= 140
    assert card["experiments_run"] == 1
    assert card["submission_slots_used"] == 0


def test_primary_tif_hash_grid_dtype_range_and_zip():
    card = load_card()
    path = ROOT / "docs/downloads" / card["submission"]["file"]
    assert digest(path) == EXPECTED_TIF_SHA == card["raster_sha256"]
    with rasterio.open(path) as source:
        values = source.read(1)
        assert source.count == 1
        assert source.dtypes == ("float32",)
        assert source.crs.to_epsg() == 32611
        assert source.shape == (3730, 3292)
        assert tuple(source.transform)[:6] == (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
        assert np.isfinite(values).all()
        assert float(values.min()) == 0.0
        assert float(values.max()) == 1.0
        assert int((values > 0).sum()) == 37_654
    zipped = path.with_suffix(".zip")
    with zipfile.ZipFile(zipped) as archive:
        assert archive.namelist() == [path.name]
        assert hashlib.sha256(archive.read(path.name)).hexdigest() == EXPECTED_TIF_SHA


def test_uniqueness_guards_pass_wide_of_both_stop_thresholds():
    card = load_card()
    screens = card["correlation_overlap_vs_registry"]
    assert screens["surface"]["passed"] is True
    assert screens["surface"]["max_spearman_rho"] < 0.90
    assert screens["final_dots"]["passed"] is True
    assert screens["final_dots"]["max_spearman_rho"] < 0.90
    assert screens["final_dots"]["max_candidate_fraction_within_3px"] < 0.70
    b2 = next(
        row for row in screens["final_dots"]["rows"]
        if row["registry_id"] == "GEMSDOE32-h33-2-b2"
    )
    assert b2["spearman_rho"] < 0.03
    assert b2["candidate_fraction_within_3px"] < 0.38
    canonical = screens["canonical_12_reference_release_guard"]
    assert canonical["registry_count"] == 12
    assert canonical["passed"] is True
    assert canonical["max_preplacement_surface_spearman_rho"] < 0.90
    assert canonical["max_final_binary_spearman_rho"] < 0.90
    assert canonical["max_candidate_fraction_within_3px"] < 0.70
    release = json.loads((ROOT / canonical["evidence"]).read_text())
    assert release["passed"] is True
    assert release["registry_count"] == 12
    assert len(release["rows"]) == 12
    assert release["canonical_registry_manifest_sha256"] == canonical["canonical_manifest_sha256"]


def test_focus_forensics_proves_dependent_subtraction_family():
    evidence = json.loads((ROOT / "evidence/focus_registry_analysis_20261025.json").read_text())
    lineage = evidence["lineage"]
    assert len(evidence["artifacts"]) == 9
    assert len(evidence["pairwise"]) == 36
    assert lineage["gems25_and_gems30_pixel_identical"] is True
    assert lineage["solo_is_exact_subset_of_d2p8"] is True
    assert lineage["d2p8_minus_solo_dots"] == 3_891
    assert lineage["d2p8_minus_solo_all_exactly_1px_from_catalogue"] is True
    assert lineage["b2_is_exact_subset_of_solo"] is True
    assert lineage["solo_minus_b2_dots"] == 2_545
    assert lineage["solo_minus_b2_all_gt1_le2px_from_catalogue"] is True
    assert lineage["b2_is_exact_subset_of_anderson"] is True
    assert lineage["anderson_minus_b2_dots"] == 1_200
    assert all(
        row["reported_dti_evidence_class"]
        == "OWNER_OR_USER_REPORTED_NOT_ORGANIZER_CONFIRMED"
        for row in evidence["artifacts"]
    )


def test_vendored_shared_contract_matches_source_manifest():
    manifest = json.loads((ROOT / "vendor/gems24_template/SOURCE.json").read_text())
    assert manifest["source_commit"] == "fc2bc6f350bf5c6ce8da5d7a2ab03578ea1259d1"
    for record in manifest["files"]:
        assert digest(ROOT / record["local"]) == record["sha256"]
