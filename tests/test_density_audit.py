"""Regression checks for the 2026-10-29 deployment-density audit (Experiment 1).

These tests read committed evidence only. They do not restore data, run the holdout or touch DrivenData.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "knowledge" / "33_density_audit_preregistration_20261029.md"
EVIDENCE = ROOT / "evidence" / "density_audit_20261029.json"
RUN_CARD = ROOT / "evidence" / "run_card_density_audit_20261029.json"
PREREG_SHA = "cd4a2b6a9b76cba383d1ee000868ddcca486ba5e7aede09407fc0ffac40981f0"
FOOTPRINT_CELLS = 5_167_373
FULL_DOT_BUDGET = 37_654


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_preregistration_is_unchanged_since_freeze():
    assert hashlib.sha256(PREREG.read_bytes()).hexdigest() == PREREG_SHA


def test_deployment_fraction_is_budget_over_footprint():
    ev = _load(EVIDENCE)
    assert ev["footprint_cells"] == FOOTPRINT_CELLS
    assert abs(ev["deployment_fraction"] - FULL_DOT_BUDGET / FOOTPRINT_CELLS) < 1e-12


def test_harness_reproduces_recorded_campaign_values():
    camp = _load(EVIDENCE)["runs"]["campaign_2p5pct"]
    assert abs(camp["candidate_screen_dti"] - 0.16931590667916066) < 1e-6
    assert abs(camp["control_dti"] - 0.1804136278250649) < 1e-6
    assert camp["emitted_dots_candidate_total"] == camp["emitted_dots_control_total"]


def test_verdict_follows_preregistered_rule():
    ev = _load(EVIDENCE)
    dep = ev["runs"]["deployment"]
    robust_signal = dep["paired_delta_ci95"][0] > 0 and dep["fold_wins"] >= 3
    assert robust_signal is False
    assert ev["verdict"].startswith("density-robust null")
    assert all(ev["gates"].values())
    assert ev["no_submission_written"] is True and ev["no_slot_used"] is True


def test_every_emitted_map_is_binary_and_clean_outside_footprint():
    ev = _load(EVIDENCE)
    for run in ev["runs"].values():
        for key in ("format_candidate", "format_control"):
            assert run[key] == {"binary": True, "shape_matches_footprint": True, "zero_outside_footprint": True}


def test_run_card_matches_evidence_numbers():
    ev = _load(EVIDENCE)["runs"]
    card = _load(RUN_CARD)["holdout_dti"]
    dep = ev["deployment"]
    camp = ev["campaign_2p5pct"]
    assert abs(card["deployment_density_0p73pct"]["candidate_screen"] - dep["candidate_screen_dti"]) < 1e-6
    assert abs(card["deployment_density_0p73pct"]["matched_random_control"] - dep["control_dti"]) < 1e-6
    assert abs(card["campaign_density_2p5pct"]["paired_delta_candidate_minus_control"]
               - camp["paired_delta_dti"]) < 1e-6
    assert card["deployment_density_0p73pct"]["fold_wins"] == f"{dep['fold_wins']}/{dep['n_folds']}"


def test_run_card_declares_no_submission_artifact():
    card = _load(RUN_CARD)
    assert card["raster_sha256"].startswith("none")
    assert card["submission_name"].startswith("none")
    assert card["verdict"].startswith("negative")
