"""Public-site content must distinguish a unique artifact from slot approval."""
from scripts import build_site


FILENAME = "gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros.tif"


def test_overview_links_current_unique_tif_and_blocks_upload():
    page = build_site.build_index()
    assert FILENAME in page
    assert "DO NOT SUBMIT" in page
    assert "not OK to submit" in page
    assert "0.2778" in page
    assert "OWNER/USER-REPORTED, NOT ORGANIZER-CONFIRMED" in page
    assert "metric-aware subtraction" in page
    assert "0.108374" in page
    assert "zero competition slots" in page


def test_executive_summary_explains_process_and_blocks_failed_candidate():
    page = build_site.build_exec()
    assert FILENAME in page
    assert "NOT OK TO SUBMIT" in page
    assert "Note (≤140 characters)" in page
    assert "2bbbf7e381720f2242959e3efd6f2437f273afe6e7c48540d769524d2b4e8759" in page
    assert "official problem/format instructions" in page
    assert "organizer receipt" in page
    assert "no DrivenData authentication" in page
    assert "strict whole-array finite [0,1]" in page


def test_hypothesis_page_has_frozen_analog_slate_and_blocked_sources():
    page = build_site.build_hypotheses()
    assert "A33-L1 target-aligned field-balanced structural transfer" in page
    assert "A33-L2 leave-one-field-out consensus ensemble" in page
    assert "A33-L3 matched local-contrast transfer" in page
    assert "A33-L4 CORAL covariance alignment with field holdout" in page
    assert "A33-L5 field-verified BRIDGE/Gabbs supervision" in page
    assert "Tested; negative" in page
    assert "no hypothesis is promoted" in page
    assert "blocked on official archive bytes" in page


def test_research_page_exposes_fold_safe_negative_result_and_run_card():
    page = build_site.build_research()
    assert "A33-L1 complete research record" in page
    assert "NEGATIVE — NOT OK TO SUBMIT" in page
    assert "60,988 pooled" in page
    assert "0.108374" in page
    assert "0.113244" in page
    assert "-0.004870" in page
    assert "0/4 fold wins" in page
    assert "Final max Spearman" in page
    assert "final run card" in page
