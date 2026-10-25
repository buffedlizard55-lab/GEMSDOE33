"""Public-site content must distinguish research artifacts from approved submissions."""
from scripts import build_site


def test_overview_marks_h33_6_duplicate_stop_and_reports_unverified_scores():
    page = build_site.build_index()
    assert "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif" in page
    assert "NOT OK to submit" in page
    assert "No candidate is slot-cleared" in page
    assert "duplicate guard" in page.lower()
    assert "7 of 9" in page
    assert "0.2778" in page
    assert "USER/OWNER-REPORT" in page
    assert "0.2708" in page
    assert "0.4413" in page and "0.3195" in page
    assert "historical d2.8" in page.lower()
    assert "Do not upload it" in page
    assert "unique research TIFF" not in page
    assert "cross-site uniqueness was not established" in page


def test_executive_summary_explains_process_and_blocks_failed_candidate():
    page = build_site.build_exec()
    assert "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7" in page
    assert "NOT OK to submit" in page
    assert "not okay" in page.lower() or "NOT OK" in page
    assert "predicted" not in page.lower() or "score" in page.lower()
    assert "140 characters" in page
    assert "current official instructions" in page
    assert "organizer receipt" in page
    assert "no DrivenData auth" in page


def test_hypothesis_page_has_ranked_prior_art_and_blocked_statuses():
    page = build_site.build_hypotheses()
    assert "H33-6 cross-physics edge-normal consensus" in page
    assert "DOE GDR #1682" in page
    assert "USGS ScienceBase" in page
    assert "ComCat focal-mechanism" in page
    assert "H33-10" in page
    assert "H33-11: Paired signed vertical-gradient zero-crossing traces" in page
    assert "H33-12: Matched-window potential-field texture-offset test" in page
    assert "H33-13: Mapped-lithology contact control for potential-field edges" in page
    assert "preflight stopped before experiment" in page
    assert "No untested candidate is promoted" in page


def test_research_page_exposes_failed_gate_duplicate_guard_and_run_card():
    page = build_site.build_research()
    assert "H33-6 failed P1" in page
    assert "no candidate is slot-approved" in page
    assert "−0.00273732" in page
    assert "Download H33-6 research TIFF" in page
    assert "RESEARCH ONLY" in page
    assert "Earlier H33-F analog-field screen" in page
    assert "-0.093072" in page
    assert "duplicate threshold" in page
    assert "60,988" in page
    assert "pre-placement edge surface was not screened" in page
    assert "H33-6 is not eligible for a slot" in page
