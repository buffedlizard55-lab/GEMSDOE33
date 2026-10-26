"""Public-site content must distinguish research artifacts from approved submissions."""
from scripts import build_site


def test_overview_marks_unique_tif_research_only_and_not_uploadable():
    page = build_site.build_index()
    assert "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif" in page
    assert "NOT approved for competition upload" in page
    assert "No candidate is slot-cleared" in page
    assert "0.2778" not in page  # no unsupported score claim on landing page
    assert "0.2708" in page
    assert "cannot explain why H27-4" in page
    assert "historical D2.8" in page
    assert "Do not submit" in page


def test_executive_summary_explains_process_and_blocks_failed_candidate():
    page = build_site.build_exec()
    assert "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7" in page
    assert "not approved for competition upload" in page
    assert "not okay to submit" in page
    assert "predicted" not in page.lower() or "score" in page.lower()
    assert "Note (≤140 characters)" in page
    assert "official format instructions" in page
    assert "organizer receipt" in page
    assert "no DrivenData auth" in page


def test_hypothesis_page_has_ranked_prior_art_and_blocked_statuses():
    page = build_site.build_hypotheses()
    assert "H33-6 cross-physics edge-normal consensus" in page
    assert "DOE GDR #1682" in page
    assert "USGS ScienceBase" in page
    assert "ComCat focal-mechanism" in page
    assert "H33-10" in page
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
    assert "gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-zeros.tif" in page
    assert "0 / 22 duplicate triggers" in page


def test_results_page_exposes_focus_sites_forensic_proof_and_round3_holdout():
    page = build_site.build_results()
    assert "GEMSDOE32" in page
    assert "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif" in page
    assert "0.2778" in page
    assert "37,654" in page
    assert "GEMSDOE33-HIDE-AND-RECOVER-v1.0" in page
    assert "0.075943" in page
