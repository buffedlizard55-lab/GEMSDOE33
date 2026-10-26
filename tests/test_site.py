"""Public-site content must distinguish research artifacts from approved submissions."""
from scripts import build_site


def test_overview_marks_latest_unique_tif_research_only_and_not_uploadable():
    page = build_site.build_index()
    assert "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif" in page
    assert "OK TO DOWNLOAD: YES" in page
    assert "OK TO SUBMIT: NO" in page
    assert "no raster in this project is ok to submit" in page.lower()
    assert "0.2778" in page
    assert "USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)" in page
    assert "0.3195 and 0.4413 conflict" in page
    assert "no score is projected" in page.lower()
    assert "A33-R3-LLC" in page
    assert "Current checkout limitation" in page
    assert "121-channel shared cache was rebuilt without detector training" in page
    assert "knowledge/20_restoration_and_claims_audit_20261026.md" in page


def test_executive_summary_explains_process_and_blocks_failed_candidate():
    page = build_site.build_exec()
    assert "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9" in page
    assert "OK TO SUBMIT: NO" in page
    assert "do not upload any file until its banner says" in page
    assert "predicted" not in page.lower() or "score" in page.lower()
    assert "Note (≤140 characters)" in page
    assert "current official contract" in page
    assert "organizer receipt" in page
    assert "no DrivenData auth" in page
    assert "GEMSDOE32" in page and "0.2778" in page
    assert "HIGHEST owner-reported focus-site value" in page
    assert "A33-R3-LLC, above" in page


def test_hypothesis_page_has_ranked_round4_triage_and_historical_prior_art():
    page = build_site.build_hypotheses()
    assert "A33-R4-COULOMB" in page
    assert "A33-R4-CURVTRACE" in page
    assert "A33-R4-PFRT" in page
    assert "A33-R4-HMDT" in page
    assert "A33-R4-PALEOTEMP" in page
    assert "no standalone lane" in page
    assert "not run" in page
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


def test_a33_r3_hero_is_first_and_blocks_submission():
    page = build_site.build_index()
    assert page.index("a33-r3-llc") < page.index("a33-r2-csht")
    assert "OK TO DOWNLOAD: YES" in page and "OK TO SUBMIT: NO" in page
    assert "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif" in page
    exec_page = build_site.build_exec()
    assert "Exact submission steps" in exec_page and "select_submission.py" in exec_page
    assert "-zeros.tif" in exec_page and "local range check" in exec_page
    assert "No claim is made that zeros or NaN encoding is accepted" in exec_page
    assert exec_page.count("</html>") == 1


def test_source_page_does_not_claim_restored_owner_mirrors_are_absent():
    page = build_site.build_sources()
    assert "17 owner-mirror inputs restored and hash-verified" in page
    assert "git-ignored" in page
    assert "do not authenticate organizer provenance" in page


def test_latest_review_discloses_restoration_and_no_new_candidate():
    page = build_site.build_focus_review()
    assert "Current-checkout verification" in page
    assert "17 registered owner-mirror inputs were restored and hash-verified" in page
    assert "Data/cache remain ignored" in page
    assert "No new candidate was evaluated, and no new TIFF or submission slot was created" in page
    assert "knowledge/20_restoration_and_claims_audit_20261026.md" in page


def test_portal_range_error_is_not_claimed_fixed_by_zero_outside():
    page = build_site.build_exec()
    assert "portal error's cause" in page
    assert "organizer acceptance of zero-outside encoding are unverified" in page
    assert "No claim is made that zeros or NaN encoding is accepted" in page
    assert "cannot trip the portal message" not in page
    irregularities = build_site.build_irregularities()
    assert "IR-33-PORTAL-RANGE-CLAIM-01" in irregularities
    assert "root cause unconfirmed" in irregularities
