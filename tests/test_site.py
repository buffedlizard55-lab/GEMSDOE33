"""Public-site copy must be honest and keep the unique download prominent."""
from scripts import build_site


def test_overview_promotes_unique_analog_tif_and_not_a_slot():
    page = build_site.build_index()
    assert "gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef-nan.tif" in page
    assert "Download the unique format-checked GeoTIFF" in page
    assert "NOT SLOT-APPROVED" in page
    assert "Predicted values" in page or "[0, 1]" in page
    assert "0.3195" in page
    assert "was not supported" in page
    assert "Terms of Use" in page
    assert "prior written consent" in page
    assert "nchuzhoy" not in page
    assert "0.3262" not in page
    assert "No weekly submission" in page and "slot is approved" in page
    assert "+0.00601" not in page
    assert "transfer licensed" not in page
    assert "calibrated to the live" not in page


def test_executive_summary_has_exact_name_note_and_upload_caveat():
    page = build_site.build_exec()
    assert "gemsdoe33-h33f-analog-xfer-20261004" in page
    assert "GEMSDOE33 H33-F analog xfer | Dixie/Brady/DesertPeak wells+GeoDAWN" in page
    assert "Paste the note" in page
    assert "NaN" in page
    assert "No upload or score is asserted" in page
    assert "portal acceptance" in page
    assert "[0,1]" in page or "[0, 1]" in page


def test_research_page_blocks_unvalidated_transfer_and_hypothesis_claims():
    page = build_site.build_research()
    assert "EXPLORATORY_NOT_LICENSED" in page
    assert "retrospective" in page
    assert "No new candidate has been demonstrated" in page
    assert "A generic two-sample AUC is not by itself that bound" in page
    assert "H33-F" in page
    assert "+0.00601" not in page
    assert "AUC 0.913" not in page
