"""Audit artifacts are prior art, not new model evidence."""
import json
from pathlib import Path

from scripts import build_site

ROOT = Path(__file__).resolve().parents[1]


def test_all_nine_sites_and_exact_pruning_recipe_are_retained():
    r = json.loads((ROOT / "evidence/focus_raster_audit_20261025.json").read_text())
    assert {x["site"] for x in r["rasters"]} == {
        f"GEMSDOE{i}" for i in (24, 25, 27, 28, 30, 31, 32, 33, 36)}
    assert len(r["rasters"]) == 12
    assert len(r["ordered_pairs"]) == 132
    assert r["b2_recipe"]["pixel_exact_match"] is True
    assert r["b2_recipe"]["deleted_dots"] == 2545
    assert r["b2_recipe"]["added_dots"] == 0
    assert r["new_submission_written"] is False
    assert all(x["format"]["pass"] for x in r["rasters"])


def test_four_new_hypotheses_are_blocked_not_viable():
    r = json.loads((ROOT / "registry/analog_hypotheses_20261025.json").read_text())
    assert len(r["candidates"]) == 4
    assert all(h["viable_now"] is False for h in r["candidates"])
    assert all(h["official_sources"] and h["non_fault_mimic"] for h in r["candidates"])


def test_site_exposes_current_gates_and_no_false_unique_download_claim():
    hero = build_site.a33_r3_llc_hero()
    assert "OK TO DOWNLOAD: YES" in hero
    assert "OK TO SUBMIT: NO" in hero
    assert "ties the holdout best" in hero
    assert "submission_selection.json" in hero
    assert "do not spend a weekly slot" in hero
    latest = build_site.build_focus_review()
    assert "132 ordered comparisons" in latest
    assert "0.967587" in latest
    assert "NOT a complete global uniqueness registry" in latest
    assert "not a request for a human scientific inspector" in latest
    assert "Round-4 feasibility decision" in latest
    assert "round4-run-card.json" in latest
    for i in (24, 25, 27, 28, 30, 31, 32, 33, 36):
        assert f"GEMSDOE{i}" in latest


def test_current_card_never_reuses_historical_holdout_as_current():
    card = json.loads((ROOT / "evidence/run_card_focus_20261025.json").read_text())
    assert card["verdict"] == "negative"
    assert card["new_raster_generated"] is False
    assert card["experiments"] == card["competition_slots_used"] == 0
    assert card["holdout"]["pooled_dti"] is None
    assert card["raster_sha256"] is None
    assert len(card["submission"]["note"]) <= 140
    assert card["submission"]["ok_to_submit"] is False
