"""No restored data required: promotion declarations must agree with all gates."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("selector_contract", ROOT / "scripts/select_submission.py")
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)


def assessment():
    return {"eligible_for_selector": True, "failed_gates": [],
            "gates": dict.fromkeys(selector.REQUIRED_GATE_NAMES, True)}


def test_complete_positive_assessment():
    assert selector._promotion_gates_pass(assessment())


@pytest.mark.parametrize("value", [False, None, 1, "true"])
def test_summary_flag_cannot_override_failed_or_nonboolean_gate(value):
    pa = assessment()
    pa["gates"]["independent_confirmation"] = value
    assert not selector._promotion_gates_pass(pa)


@pytest.mark.parametrize("gates", [{}, None, {"independent_confirmation": True}])
def test_incomplete_gate_maps_fail(gates):
    pa = assessment()
    pa["gates"] = gates
    assert not selector._promotion_gates_pass(pa)


def test_contradictory_failed_list_fails():
    pa = assessment()
    pa["failed_gates"] = ["budget"]
    assert not selector._promotion_gates_pass(pa)


def test_underlying_evidence_is_reassessed_and_hash_bound(tmp_path, monkeypatch):
    import hashlib
    import json
    from test_promotion import evidence_fixture, CANDIDATE

    evidence = evidence_fixture()
    directory = tmp_path / "evidence"
    directory.mkdir()
    path = directory / "example.json"
    path.write_text(json.dumps(evidence))
    monkeypatch.setattr(selector, "ROOT", tmp_path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    card = {"promotion_evidence": {"file": path.name, "sha256": digest}}
    fmt = {"pass": True, "sha256": CANDIDATE}
    note = evidence["submission_note"]
    score = evidence["confirmation"]["candidate_pooled_dti"]
    assert selector._reassess_evidence(card, fmt, CANDIDATE, note, score)
    assert not selector._reassess_evidence(card, fmt, CANDIDATE, "different note", score)
    assert not selector._reassess_evidence(card, fmt, CANDIDATE, note, score + .01)
    path.write_text(json.dumps({**evidence, "screen": {**evidence["screen"],
                                                   "candidate_pooled_dti": .1}}))
    assert not selector._reassess_evidence(card, fmt, CANDIDATE, note, score)
    card["promotion_evidence"]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert not selector._reassess_evidence(card, fmt, CANDIDATE, note, score)
    card["promotion_evidence"]["file"] = "../example.json"
    assert not selector._reassess_evidence(card, fmt, CANDIDATE, note, score)


def test_complete_synthetic_card_can_pass_without_flags_alone(tmp_path, monkeypatch):
    import hashlib
    import json
    import zipfile
    from test_promotion import evidence_fixture

    downloads = tmp_path / "downloads"
    evidence_dir = tmp_path / "evidence"
    downloads.mkdir()
    evidence_dir.mkdir()
    tif = downloads / "synthetic.tif"
    tif.write_bytes(b"synthetic bytes, not a real raster")
    sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    with zipfile.ZipFile(downloads / "synthetic.zip", "w") as archive:
        archive.write(tif, tif.name)
    ev = evidence_fixture()
    ev["candidate_sha256"] = sha
    ev["screen"]["candidate_sha256"] = sha
    ev["confirmation"]["candidate_sha256"] = sha
    ev["duplicates"]["final_dots"]["candidate_sha256"] = sha
    ev_path = evidence_dir / "synthetic.json"
    ev_path.write_text(json.dumps(ev))
    card = {"verdict": "promote", "promotion_assessment": assessment(), "raster_sha256": sha,
            "submission": {"name": "synthetic", "file": tif.name, "zip": "synthetic.zip",
                           "note": ev["submission_note"]},
            "promotion_evidence": {"file": ev_path.name,
                "sha256": hashlib.sha256(ev_path.read_bytes()).hexdigest()},
            "holdout_dti": {"confirm_candidate": ev["confirmation"]["candidate_pooled_dti"]}}
    card_path = evidence_dir / "synthetic_run_card.json"
    card_path.write_text(json.dumps(card))
    template = tmp_path / "template.tif"
    template.touch()
    monkeypatch.setattr(selector, "ROOT", tmp_path)
    monkeypatch.setattr(selector, "DOWNLOADS", downloads)
    monkeypatch.setattr(selector, "TEMPLATE", template)
    monkeypatch.setattr(selector, "audit", lambda *_args, **_kwargs: {
        "pass": True, "sha256": sha, "all_finite": True, "in_range_0_1_whole_array": True})
    assert selector.check_card(card_path)["eligible"] is True
    # This exercises code flow only; mocks cannot establish the validity of a real candidate.
