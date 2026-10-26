"""Public-site content must distinguish research artifacts from approved submissions."""
from scripts import build_site


def test_overview_marks_unique_tif_research_only_and_not_uploadable():
    page = build_site.build_index()
    assert "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7-nan.tif" in page
    assert "OK TO DOWNLOAD" in page
    assert "NOT OK TO SUBMIT" in page
    assert "must not be uploaded to the competition" in page
    assert "no real competition submission is approved" in page.lower()
    assert "0.2778" not in page  # no unsupported score claim on landing page
    assert "0.2708" in page
    assert "cannot explain why H27-4" in page
    assert "historical D2.8" in page


def test_executive_summary_explains_process_and_blocks_failed_candidate():
    page = build_site.build_exec()
    assert "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7" in page
    assert "NOT CLEARED FOR SUBMISSION" in page
    assert "NOT cleared to submit" in page
    assert "must not be uploaded to the competition" in page
    assert "predicted" not in page.lower() or "score" in page.lower()
    assert "Note (≤140 characters)" in page
    assert "official format instructions" in page
    assert "organizer receipt" in page
    assert "no DrivenData auth" in page
    assert "GEMSDOE32" in page and "0.2778" in page  # per-site best table
    assert "OWNER-REPORTED, NOT ORGANIZER-CONFIRMED" in page
    assert "Not defensibly estimable from this holdout" in page
    assert "FAIL —" in page and "exceeds the 70% guard" in page
    assert "focus_raster_audit_20261025.json" in page
    assert r"\n3730" not in page and r"\n<tr>" not in page
    assert page.count("Pinned owner-mirror TIFF (GitHub)") == 8
    assert "Local audited TIFF" in page
    assert "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif" in page


def test_hypothesis_page_has_ranked_prior_art_and_blocked_statuses():
    page = build_site.build_hypotheses()
    assert "H33-6 cross-physics edge-normal consensus" in page
    assert "DOE GDR #1682" in page
    assert "USGS ScienceBase" in page
    assert "ComCat focal-mechanism" in page
    assert "H33-10" in page
    assert "No untested candidate is promoted" in page
    assert "COULOMB" in page and "CURVTRACE" in page and "PFRT" in page and "PALEOTEMP" in page
    assert "no HOLDOUT-DTI result" in page
    assert "this repo has no separate USGS QFFD source record" in page
    assert "not verified as byte-identical to the official USGS QFFD" in page
    assert "Not implemented or holdout-validated" in page
    assert "Blocked: do not implement until a named file is obtainable and audited" in page


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


def test_a33_r3_hero_is_first_and_blocks_submission():
    page = build_site.build_index()
    assert page.index("a33-r3-llc") < page.index("a33-r2-csht")
    assert "OK TO DOWNLOAD: YES" in page and "OK TO SUBMIT: NO" in page
    assert "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif" in page
    exec_page = build_site.build_exec()
    assert "Exact submission steps" in exec_page and "select_submission.py" in exec_page
    assert "-zeros.tif (all cells finite, 0.0 outside)" in exec_page
    assert exec_page.count("</html>") == 1
