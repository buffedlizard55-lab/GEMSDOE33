"""Public-site content must distinguish research artifacts from approved submissions."""
from scripts import build_site


def test_overview_exposes_current_no_submit_source_block_and_archival_artifacts():
    page = build_site.build_index()
    assert "Latest source-preflight review — 2026-10-29" in page
    assert "A33-R7 is exhausted at 3/3" in page
    assert "0/3 pass source-payload/schema/license/coverage checks" in page
    assert "This review did not start another experiment or candidate TIFF, select a slot, or upload." in page
    assert "separate H34-COH research TIFF" in page and "negative, research-only result" in page
    assert "gemsdoe33-a33-r7-pcsup-37654-20261028-d1f9cca0af02-zeros.tif" in page
    assert page.index("r7-pcsup") < page.index("a33-r3-llc")
    assert "surface duplicate stop" in page.lower()
    assert "86.08%" in page and "70%" in page
    assert "HOLDOUT-DTI" in page and "0.168298" in page
    assert "Estimated leaderboard score: NOT ESTIMABLE" in page
    assert "portal acceptance" in page.lower()
    assert "fixes the reported" not in page.lower()
    assert "OK TO DOWNLOAD: YES" in page
    assert "OK TO SUBMIT: NO" in page
    assert "no file is ok to submit" in page.lower()
    assert "0.2778" in page
    assert "USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)" in page
    assert "0.3195" in page and "0.4413" in page and "conflict" in page.lower()
    assert "HOLDOUT-DTI is a catalogue proxy, not a leaderboard score estimate" in page
    assert "do not project holdout dti to the leaderboard" not in page.lower()
    assert "A33-R3-LLC" in page
    assert "Data/provenance status" in page
    assert "17 SHA-256-pinned owner-mirror inputs" in page
    assert "121-channel research cache" in page
    assert "knowledge/27_20261028_safety_review.md" in page


def test_pcsup_correction_fails_closed_on_source_surface_measurement():
    import hashlib
    import json
    from pathlib import Path

    correction = json.loads(Path("evidence/a33_r7_pcsup_lane_correction_20261028.json").read_text())
    source = json.loads(Path(correction["source_experiment"]).read_text())
    surface = source["uniqueness"]["surface"]
    final = source["uniqueness"]["final_dots"]
    assert correction["surface_before_placement"]["passed"] is surface["passed"] is False
    assert correction["surface_before_placement"]["max_fraction_within_3px"] == surface["max_preview_fraction_within_3px"]
    assert correction["surface_before_placement"]["max_fraction_within_3px"] > correction["protocol_thresholds"]["max_fraction_within_3px"]
    assert correction["final_dots"]["passed"] is final["passed"] is True
    assert correction["final_dots"]["max_fraction_within_3px"] == final["max_candidate_fraction_within_3px"]
    assert hashlib.sha256(Path(correction["raster"]).read_bytes()).hexdigest() == correction["raster_sha256"]
    assert hashlib.sha256(Path(correction["source_run_card"]).read_bytes()).hexdigest() == correction["source_run_card_sha256"]
    assert "cannot retroactively clear" in Path("knowledge/31_r7_pcsup_lane_correction_20261028.md").read_text()
    page = build_site.build_exec()
    assert "86.08%" in page and "NOT unique under protocol" in page
    assert "estimated leaderboard score is not estimable" in page.lower()


def test_r7_pcsup_surface_novelty_failure_is_visible_and_not_mislabeled_unique():
    from pathlib import Path
    import json

    root = Path(__file__).resolve().parents[1]
    uniqueness = json.loads((root / "evidence/a33_r7_pcsup_uniqueness_20261028.json").read_text())
    surface = uniqueness["surface"]
    assert surface["passed"] is False
    assert surface["max_preview_fraction_within_3px"] > surface["overlap_stop_gt"]
    page = build_site.build_index()
    assert "PRE-PLACEMENT SURFACE DUPLICATE STOP" in page
    assert "86.08%" in page
    assert "not unique under protocol" in page.lower()
    assert "Download unique A33-R7-PCSUP" not in page


def test_s33_seisdil_banner_has_download_and_explicit_negative_verdict():
    page = build_site.build_index()
    assert "gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros.tif" in page
    assert "OK TO DOWNLOAD: YES" in page and "OK TO SUBMIT: NO" in page
    assert "-0.010458" in page and "-0.016294" in page
    assert "-0.011869" in page and "-0.017655" in page
    assert "standalone candidate-DTI CI" in page
    assert "organizer acceptance" in page
    assert "5eb9572946fa62356ebc0cbfef22bb54aa2ef094cb8b4a84b52e6b80e120db96" in page


def test_executive_summary_has_one_current_per_site_table_and_blocks_submission():
    page = build_site.build_exec()
    assert "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9" in page
    assert "Current decision — 2026-10-29" in page
    assert "NO FILE IS OK TO SUBMIT" in page
    assert "no identifiable current method paragraph" in page.lower()
    assert "0/3 hypotheses pass" in page
    assert "do not upload any file until its banner says" in page
    assert "predicted" not in page.lower() or "score" in page.lower()
    assert "Note (≤140 characters)" in page
    assert "current official contract" in page
    assert "organizer receipt" in page
    assert "no DrivenData auth" in page
    assert "GEMSDOE32" in page and "0.2778" in page
    assert page.count("Not estimable from evidence") == 9
    assert "GEMSDOE32 B2" in page and "deletion-only" in page
    assert "A33-R7-PCSUP" in page
    assert "pre-placement surface" in page
    assert "86.08%" in page
    assert "not unique under protocol" in page.lower()
    assert "Current ranked hypotheses and source preflight (proposal only)" in page
    assert "Priority 1" in page


def test_hypothesis_page_preserves_historical_round4_prior_art():
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


def test_current_hypothesis_slate_is_ranked_but_none_is_viable():
    import json
    from pathlib import Path

    page = build_site.build_hypotheses()
    slate = json.loads(Path("evidence/hypothesis_slate_20261029.json").read_text())
    preflight = json.loads(Path("evidence/source_preflight_20261029.json").read_text())
    assert "Current ranked hypotheses — proposal slate only (2026-10-29)" in page
    for candidate_id in ("H33-HYDRO-MIX-01", "H33-MT-DEPTHWALL-01", "H33-3DEP-CHANNEL-KINK-01"):
        assert candidate_id in page
    assert "0/3 pass" in page and "NOT VIABLE NOW" in page
    assert "expected leaderboard rank/score is not estimable" in page
    assert len(slate["hypotheses"]) == 3
    assert not any(item["viable_now"] for item in slate["hypotheses"])
    assert slate["decision"]["holdout_experiments_run"] == 0
    assert slate["decision"]["candidate_tif_created"] is False
    assert preflight["decision"]["hypotheses_declared_viable"] == 0
    assert preflight["sources"][0]["spatial_spot_checks"][0]["api_total_products"] == 4


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


def test_holdout_component_count_metadata_bug_is_disclosed():
    page = build_site.build_irregularities()
    assert "IR-33-20261029-HOLDOUT-COUNT-01" in page
    assert "3,199" in page
    assert "metadata, not a DTI input" in page


def test_source_page_separates_catalog_pages_from_verified_payloads():
    page = build_site.build_sources()
    assert "All 17 registered owner-mirror inputs were restored and hash-verified" in page
    assert "121-channel research cache" in page
    assert "git-ignored" in page
    assert "do not authenticate organizer provenance" in page
    assert "no candidate-required official binary is fully verified" in page
    assert "GDR #1391/#1682 archive fetches returned HTTP 500" in page
    assert "two finite-footprint sample cells" in page
    assert "USGS Electrical Conductance Maps" in page
    assert "source_preflight_20261029.json" in page


def test_latest_review_discloses_restoration_and_parallel_negative_candidate():
    page = build_site.build_focus_review()
    assert "Current-checkout verification" in page
    assert "17 registered owner-mirror inputs were restored and hash-verified" in page
    assert "S33-SEISDIL candidate was later evaluated and generated on parallel PR #30" in page
    assert "NOT OK TO SUBMIT" in page
    assert "knowledge/21_post_merge_review_20261026.md" in page


def test_portal_range_error_is_not_claimed_fixed_by_zero_outside():
    page = build_site.build_exec()
    assert "portal error's cause" in page
    assert "organizer acceptance of zero-outside encoding are unverified" in page
    assert "No claim is made that zeros or NaN encoding is accepted" in page
    assert "cannot trip the portal message" not in page
    irregularities = build_site.build_irregularities()
    assert "IR-33-PORTAL-RANGE-CLAIM-01" in irregularities
    assert "root cause unconfirmed" in irregularities


def test_current_focus_table_has_nine_scores_and_no_stale_duplicate_table():
    page = build_site.build_exec()
    assert "Estimated score" in page
    assert page.count("Not estimable from evidence") == 9
    focus_sites = (
        "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
        "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
    )
    for site in focus_sites:
        assert f"<b>{site}</b>" in page
    assert page.count("owner-reported</span>") >= 9
    assert "OK to submit?</th>" in page
    assert "Which focus-site submission is the best to submit?" not in page
    assert "the single current per-site inventory" in page
    assert "GEMSDOE32" in page and "0.2778" in page
    assert "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif" in page
    assert "0.3195" in page and "0.4413" in page and "conflict" in page.lower()
