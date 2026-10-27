"""Public pages must reflect current, fail-closed research status and provenance."""
import json
from pathlib import Path

from scripts import build_site


FSML2_TIF = "gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-zeros.tif"


def test_overview_puts_current_no_submit_decision_first():
    page = build_site.build_index()
    assert page.index("Current decision · 2026-10-27") < page.index(FSML2_TIF)
    assert "NO RASTER IS OK TO SUBMIT" in page
    assert "0 eligible of 13" in page
    assert "no experiment" in page.lower()
    assert "generated 2026-10-26; not generated in this review" in page
    assert "OK TO DOWNLOAD: YES" in page
    assert "OK TO SUBMIT: NO" in page
    assert "USER/OWNER-REPORTED, not ORGANIZER-CONFIRMED" in page
    assert "0.3195 and 0.4413 conflict" in page
    assert "No public-score estimate is made" in page
    assert "knowledge/24_repository_review_20261027.md" in page


def test_fsml2_hero_labels_holdout_and_not_public_score():
    page = build_site.fsml2_hero()
    assert FSML2_TIF in page
    assert "gems-segment-pooled-v1" in page
    assert "60,988 withheld positives" in page
    assert "screen 0.1104" in page
    assert "confirmation 0.1031" in page
    assert "HOLDOUT GATE FAILED" in page
    assert "0 eligible of 13" in page
    assert "Portal acceptance" in page
    assert "not global uniqueness proof" in page
    assert "DO NOT SPEND A SLOT" in page


def test_executive_summary_compares_all_nine_and_explains_b2_cautiously():
    page = build_site.build_exec()
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in page
    assert page.count("<td>Not estimable</td>") == 9
    for value in ("0.2477", "0.2600", "0.2449", "0.2710", "0.2708", "0.1462",
                  "0.2778", "0.2632", "0.2750", "0.2250", "0.0206", "0.0963", "0.1647"):
        assert value in page
    assert "2,545 deletions, zero additions" in page
    assert "plausible mechanism, not a causal demonstration" in page
    assert "0 eligible of 13" in page
    assert "Not estimable" in page
    assert "no weekly slot" in page.lower() or "no slot" in page.lower()
    assert "Outside-footprint convention remains unresolved" in page
    assert "organizer" in page.lower()


def test_hypothesis_page_uses_current_three_item_proposal_slate():
    page = build_site.build_hypotheses()
    assert "H27-PHASEEDGE" in page
    assert "H27-BIFURCATION" in page
    assert "H27-CATCHMENT-PROFILE" in page
    assert "Rank 1" in page and "Rank 2" in page and "Rank 3" in page
    assert "no identifiable assigned method paragraph" in page
    assert "not a lane assignment" in page
    assert "USGS GeoDAWN" in page
    assert "USGS 3DEP" in page
    assert "blocked" in page.lower() and "not viable" in page.lower()
    assert "Named non-fault mimic" in page
    assert "AUC &gt; 0.90" in page
    assert "more than 70%" in page


def test_latest_review_reports_restoration_selector_and_three_passes():
    page = build_site.build_focus_review()
    assert "2026-10-27 repository review — three passes" in page
    assert "17 of 17" in page
    assert "121 cached channels" in page
    assert "0 eligible of 13" in page
    assert "No experiment" in page
    assert "no new TIFF" in page
    assert "SHA-256-pinned owner-mirror inputs" in page
    assert "not organizer" in page.lower()
    assert "FSML2-CC" in page
    assert "177 passed" in page
    assert "NOT OK TO SUBMIT" in page


def test_results_page_does_not_project_holdout_to_score():
    page = build_site.build_results()
    assert "HOLDOUT-DTI" in page
    assert "gems-segment-pooled-v1" in page
    assert "60,988 withheld positives" in page
    assert "95% CI" in page
    assert "No numeric leaderboard-score projection" in page
    assert "No organizer-confirmed score" in page
    assert "0 eligible of 13" in page


def test_source_page_preserves_owner_mirror_provenance_caveat():
    page = build_site.build_sources()
    assert "17 owner-mirror inputs restored and hash-verified" in page
    assert "2026-10-27 working session" in page
    assert "git-ignored" in page
    assert "do not authenticate organizer provenance" in page


def test_site_no_longer_claims_stale_current_selector_count():
    pages = [
        build_site.build_index(),
        build_site.build_exec(),
        build_site.build_results(),
        build_site.build_hypotheses(),
        build_site.build_focus_review(),
    ]
    for page in pages:
        assert "0 eligible of 12" not in page
        assert "0 of 12 run cards" not in page


def test_site_build_publishes_current_review_assets_as_valid_json():
    build_site.main()
    for filename in (
        "20261027_review_card.json",
        "submission_selection_20261027.json",
        "hypotheses_20261027.json",
    ):
        path = Path(__file__).resolve().parents[1] / "docs" / "data" / filename
        assert json.loads(path.read_text(encoding="utf-8"))
