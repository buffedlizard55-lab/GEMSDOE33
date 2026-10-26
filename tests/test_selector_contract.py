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
