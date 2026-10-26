"""Audits and site pages must separate prior-art forensics from current model evidence."""
import csv
import json
from pathlib import Path

from scripts import build_site

ROOT = Path(__file__).resolve().parents[1]


def test_all_nine_sites_and_exact_pruning_recipe_are_retained():
    audit = json.loads((ROOT / "evidence/focus_raster_audit_20261025.json").read_text())
    assert {x["site"] for x in audit["rasters"]} == {
        f"GEMSDOE{i}" for i in (24, 25, 27, 28, 30, 31, 32, 33, 36)}
    assert len(audit["rasters"]) == 12
    assert len(audit["ordered_pairs"]) == 132
    assert audit["b2_recipe"]["pixel_exact_match"] is True
    assert audit["b2_recipe"]["deleted_dots"] == 2545
    assert audit["b2_recipe"]["added_dots"] == 0
    assert audit["new_submission_written"] is False
    assert all(x["format"]["pass"] for x in audit["rasters"])


def test_focus_best_artifact_table_is_complete_and_fail_closed():
    summary = json.loads((ROOT / "registry/focus_best_artifact_summary_20261026.json").read_text())
    assert len(summary["artifacts"]) == 9
    assert summary["comparison_count"] == 36
    assert all(x["score_evidence_class"] == "OWNER_OR_USER_REPORTED_NOT_ORGANIZER_CONFIRMED" for x in summary["artifacts"])
    assert all(x["organizer_receipt_in_this_repository"] == "NO" for x in summary["artifacts"])
    assert all(x["competition_score_estimate"] == "NOT_ESTIMABLE" for x in summary["artifacts"])
    assert all(x["uniqueness_status"] == "FAIL" for x in summary["artifacts"])
    assert all(x["ok_to_download"] == "YES_FROM_PINNED_OWNER_MIRROR" for x in summary["artifacts"])
    assert all(x["ok_to_submit"].startswith("NO_") for x in summary["artifacts"])
    with (ROOT / "registry/focus_best_artifact_summary_20261026.csv").open(newline="") as f:
        assert len(list(csv.DictReader(f))) == 9


def test_prior_hypothesis_ledger_kept_but_current_ranked_slate_is_cautious():
    prior = json.loads((ROOT / "registry/analog_hypotheses_20261025.json").read_text())
    assert len(prior["candidates"]) == 4
    assert all(h["viable_now"] is False for h in prior["candidates"])
    assert all(h["official_sources"] and h["non_fault_mimic"] for h in prior["candidates"])

    page = build_site.build_hypotheses()
    for hypothesis in ("A33-R4-COULOMB", "A33-R4-CURVTRACE", "A33-R4-PFRT", "A33-R4-PALEOTEMP"):
        assert hypothesis in page
    assert "No new hypothesis was selected or tested" in page
    assert "not DTI predictions or competition-score estimates" in page
    assert "original 1 m DEM tile stack is absent" in page
    assert "Named non-fault mimic" in page


def test_current_site_exposes_gates_provenance_and_reviewed_inputs():
    latest = build_site.build_focus_review()
    assert "Current decision: NO RASTER IS OK TO SUBMIT" in latest
    assert "No TIFF was generated in this review" in latest
    assert "owner-mirror inputs" in latest
    assert "121 feature channels" in latest
    assert "detector training skipped" in latest
    assert "not organizer-authenticated" in latest
    assert "focus_best_artifact_summary_20261026.csv" in latest
    assert "not a complete global registry" in latest
    assert "DOE GDR #1391" in latest
    assert "no identifiable standalone single-method lane paragraph" in latest
    assert "canonical shared-template identity" in latest
    for i in (24, 25, 27, 28, 30, 31, 32, 33, 36):
        assert f"GEMSDOE{i}" in latest


def test_review_record_does_not_claim_a_new_model_or_submission():
    review = json.loads((ROOT / "evidence/repository_review_20261026.json").read_text())
    assert review["decision"] == "NO_RASTER_OK_TO_SUBMIT"
    assert review["experiments_run"] == 0
    assert review["competition_slots_used"] == 0
    assert review["new_tiff_generated"] is False
    assert review["new_submission_uploaded"] is False
    assert review["current_research_artifact"]["ok_to_submit"] is False
    assert review["current_research_artifact"]["ok_to_download"] is True


def test_data_preparation_record_has_hashes_and_scoped_provenance():
    record = json.loads((ROOT / "evidence/data_preparation_20261026.json").read_text())
    assert record["restore"]["input_count"] == 17
    assert record["restore"]["all_hashes_verified"] is True
    assert record["feature_preparation"]["channel_count"] == 121
    assert record["feature_preparation"]["detector_training"] == "skipped"
    assert record["feature_preparation"]["holdout_evaluation"] == "none"
    assert "NOT organizer-authenticated" in record["sources"]["warning"]
