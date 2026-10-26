"""Public-site content must distinguish owner claims, holdouts, downloads, and submissions."""
from scripts import build_site


FOCUS_SITES = (24, 25, 27, 28, 30, 31, 32, 33, 36)


def test_overview_uses_current_negative_decision_and_no_projection():
    page = build_site.build_index()
    assert "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif" in page
    assert "OK TO DOWNLOAD: YES" in page
    assert "OK TO SUBMIT: NO" in page
    assert "NO RASTER IS OK TO SUBMIT" in page
    assert "Competition-score estimate: not available" in page
    assert "no upload was made" in page
    assert "gemsdoe33-g33-tilt-gravity-lidar-coherence" not in page
    assert "H33-6 failed" not in page


def test_executive_summary_has_nine_site_evidence_table_and_clear_download_status():
    page = build_site.build_exec()
    assert "Decision: no TIFF is currently OK to submit" in page
    assert "A33-R3-LLC" in page
    assert "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif" in page
    assert "HOLDOUT-DTI" in page
    assert "gems-segment-pooled-v1" in page
    assert "60,988" in page
    assert "2,545 dots" in page
    assert "not verified score causation" in page
    assert "not a competition-score estimate" in page
    assert "focus_best_artifact_summary_20261026.csv" in page
    assert "focus_best_artifact_summary_20261026.json" in page
    assert "USER/OWNER-REPORTED claim" in page
    assert "ORGANIZER-CONFIRMED" in page
    assert "not a complete global registry" in page
    assert "Official-source discovery link" in page
    assert "no TIFF is currently OK to submit" in page
    assert "raw 1 m DEM tiles are not in the restored data directory" in page
    assert page.count("<tr><td>GEMSDOE") >= 9
    for site in FOCUS_SITES:
        assert f"GEMSDOE{site}" in page
    assert "A33-R4-COULOMB" in page
    assert "A33-R4-CURVTRACE" in page
    assert "A33-R4-PFRT" in page
    assert "A33-R4-PALEOTEMP" in page
    assert "no identifiable single-method lane paragraph" in page
    assert "no new raster" in page


def test_hypothesis_page_ranks_four_untested_geological_mechanisms():
    page = build_site.build_hypotheses()
    assert "planning only" in page
    assert "No new hypothesis was selected or tested" in page
    for hypothesis in (
        "A33-R4-COULOMB",
        "A33-R4-CURVTRACE",
        "A33-R4-PFRT",
        "A33-R4-PALEOTEMP",
    ):
        assert hypothesis in page
    assert "Named non-fault mimic" in page
    assert "Lake Lahontan" in page
    assert "qualitative prior beliefs" in page
    assert "not DTI predictions or competition-score estimates" in page
    assert "original 1 m DEM tile stack is absent" in page
    assert "DOE GDR #1391" in page
    assert "A33-R2-HMDT" in page
    assert "no HOLDOUT-DTI run card/evaluation" in page


def test_research_page_marks_old_campaign_sections_as_archived():
    page = build_site.build_research()
    assert "Current decision: no raster is slot-approved" in page
    assert "read as an archive" in page
    assert "H33-6 Edge-Normal Consensus Research TIFF" in page
    assert "HOLDOUT-DTI" in page
    assert "RESEARCH ONLY" in page


def test_current_hero_and_latest_review_keep_status_and_provenance_clear():
    index = build_site.build_index()
    assert index.index("a33-r3-llc") < index.index("NO RASTER IS OK TO SUBMIT")
    assert "OK TO DOWNLOAD: YES" in index and "OK TO SUBMIT: NO" in index
    hero = build_site.unique_submission_hero()
    assert "A33-R3-LLC" in hero
    assert "OK TO DOWNLOAD: YES" in hero and "OK TO SUBMIT: NO" in hero
    assert "76f9e157d01bb9bec2d98c3c5941b6114e06e0f439272d5f140af6e3584c8825" in hero
    assert "Pre-placement V2 surface" in hero
    assert "67.79%" in hero and "43.25%" in hero
    assert "0.011126" in hero and "0.019359" in hero

    latest = build_site.build_focus_review()
    assert "Current decision: NO RASTER IS OK TO SUBMIT" in latest
    assert "lane paragraph" in latest
    assert "canonical shared-template identity" in latest
    assert "data_preparation_20261026.json" in latest
    assert "focus_best_artifact_summary_20261026.csv" in latest
    assert "no scientifically defensible competition-score estimate" in latest.lower()
    assert latest.count("<tr><td>GEMSDOE") >= 9
    for site in FOCUS_SITES:
        assert f"GEMSDOE{site}" in latest
