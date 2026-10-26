"""Automated selector: positive control (forged promote card on real bytes) and tamper controls."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence" / "a33_r3_run_card_20261026.json"
TEMPLATE = (ROOT / ".cache" / "gemsdata" / "sample_submission.tif"
            if (ROOT / ".cache" / "gemsdata" / "sample_submission.tif").is_file()
            else ROOT / "data" / "sample_submission.tif")

pytestmark = pytest.mark.skipif(not (CARD.is_file() and TEMPLATE.is_file()),
                                reason="needs restored template and the A33-R3 artifact")


def _selector():
    spec = importlib.util.spec_from_file_location("select_submission", ROOT / "scripts" / "select_submission.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Exercise the same non-default cache location used by restore_data.py in CI/sandboxes.
    mod.TEMPLATE = TEMPLATE
    return mod


def _check(tmp_card: dict):
    sel = _selector()
    p = ROOT / "evidence" / "_pytest_tmp_run_card.json"
    try:
        p.write_text(json.dumps(tmp_card))
        return sel.check_card(p)
    finally:
        p.unlink(missing_ok=True)


def test_real_negative_card_is_blocked_only_by_science_gates():
    row = _check(json.loads(CARD.read_text()))
    failed = {k for k, v in row["checks"].items() if not v}
    assert row["eligible"] is False
    assert failed == {"verdict_promote", "promotion_gates_all_pass"}


def test_positive_control_promote_card_on_valid_bytes_is_eligible():
    card = copy.deepcopy(json.loads(CARD.read_text()))
    card["verdict"] = "promote"
    card["promotion_assessment"]["eligible_for_selector"] = True
    assert _check(card)["eligible"] is True


def test_flat_s33_run_card_locates_saved_bytes_by_sha_and_stays_negative():
    card = json.loads((ROOT / "evidence" / "s33_seisdil_run_card_20261026.json").read_text())
    row = _check(card)
    assert row["eligible"] is False
    assert row["checks"]["verdict_promote"] is False
    assert row["checks"]["file_exists"] is True
    assert row["checks"]["sha256_matches_run_card"] is True
    assert row["checks"]["format_audit_pass_on_saved_bytes"] is True
    assert row["checks"]["zip_single_geotiff_same_bytes"] is True
    assert row["checks"]["note_1_to_140_chars"] is True
    assert {k for k, v in row["checks"].items() if not v} == {"verdict_promote", "promotion_gates_all_pass"}


def test_sha_tamper_and_long_note_fail_closed():
    card = copy.deepcopy(json.loads(CARD.read_text()))
    card["verdict"] = "promote"
    card["promotion_assessment"]["eligible_for_selector"] = True
    card["raster_sha256"] = "0" * 64
    card["submission"]["note"] = "x" * 141
    row = _check(card)
    assert row["eligible"] is False
    assert row["checks"]["sha256_matches_run_card"] is False
    assert row["checks"]["note_1_to_140_chars"] is False
