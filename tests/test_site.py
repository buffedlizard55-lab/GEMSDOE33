"""Public-site copy must be honest and keep the reference download prominent."""
from scripts import build_site


def test_overview_promotes_only_the_format_checked_reference():
    page = build_site.build_index()
    assert "gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif" in page
    assert "0.3195" in page
    assert "was not supported" in page
    assert "Terms of Use" in page
    assert "prior written consent" in page
    assert "nchuzhoy" not in page
    assert "0.3262" not in page
    assert "D2.8 reference only" in page
    assert "No weekly submission slot is approved" in page
    assert "+0.00601" not in page
    assert "transfer licensed" not in page
    assert "calibrated to the live" not in page


def test_executive_summary_has_exact_name_note_and_upload_caveat():
    page = build_site.build_exec()
    assert "gemsdoe33-d28-reference-20261004" in page
    assert "GEMSDOE33 D2.8 reference | owner-mirror emission" in page
    assert "Paste the note" in page
    assert "NaN" in page
    assert "No upload or score is asserted" in page
    assert "portal acceptance" in page


def test_research_page_blocks_unvalidated_transfer_and_hypothesis_claims():
    page = build_site.build_research()
    assert "BLOCKED_NOT_ESTIMATED" in page
    assert "retrospective" in page
    assert "No new candidate has been demonstrated" in page
    assert "A generic two-sample AUC is not by itself that bound" in page
    assert "+0.00601" not in page
    assert "AUC 0.913" not in page
