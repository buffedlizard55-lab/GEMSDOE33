"""Synthetic evidence tests; these fixtures are NOT project experimental results."""
import pytest

from gemsdoe33.promotion import assess

CANDIDATE, BEST, EVALUATOR, OTHER, REGISTRY = (c * 64 for c in "abcdef"[:5])


def evidence_fixture():
    run = {"label": "HOLDOUT-DTI", "evaluator_version": "synthetic-test-v1",
           "evaluator_sha256": EVALUATOR, "candidate_sha256": CANDIDATE,
           "baseline_sha256": BEST, "withheld_positives": 100,
           "whole_segments_with_buffer": True, "all_catalogue_features_visible_only": True,
           "visible_faults_masked_pixel_exactly": True, "alpha": .2, "beta": .8,
           "kernel": "triangular", "radius_m": 300, "candidate_pooled_dti": .3,
           "baseline_pooled_dti": .2, "pooled_delta_ci95": [.02, .15],
           "ci_estimand": "pooled paired delta", "split_id": "screen"}
    confirmation = {**run, "split_id": "confirmation", "independent_of_screen": True,
                    "frozen_before_screen_results": True}
    comparison = {"raster_sha256": OTHER, "spearman_rho": .7, "fraction_candidate_within_3px": .2}
    duplicate = {"registry_sha256": REGISTRY, "comparisons": [comparison]}
    return {"candidate_sha256": CANDIDATE, "current_holdout_best_sha256": BEST,
            "lane": "synthetic evidence test only", "shared_template": {
                "source_manifest_sha256": "f" * 64, "feature_cache_sha256": "f" * 64,
                "evaluator_sha256": EVALUATOR, "writer_sha256": "f" * 64},
            "screen": run, "confirmation": confirmation,
            "feature_names": ["x"], "feature_canaries": [
                {"feature": "x", "holdout_auc": .7, "split_id": "screen", "visible_only": True}],
            "registry_sha256": REGISTRY, "registry_raster_sha256s": [OTHER], "registry_complete": True,
            "duplicates": {"surface": {**duplicate, "surface_sha256": "f" * 64},
                           "final_dots": {**duplicate, "candidate_sha256": CANDIDATE}},
            "submission_note": "Synthetic test, not a submission", "experiments": 1, "elapsed_seconds": 10}


def check(evidence):
    return assess(evidence, {"pass": True, "sha256": CANDIDATE}, CANDIDATE)


def test_complete_evidence_is_only_eligible_for_separate_selector():
    r = check(evidence_fixture())
    assert r["eligible_for_selector"]
    assert r["verdict"] == "promote"
    assert not r["ok_to_submit"]


def test_missing_evidence_fails_every_relevant_gate():
    r = assess({}, {}, None)
    assert not r["eligible_for_selector"]
    assert not r["ok_to_submit"]
    assert not r["gates"]["identity"]
    assert not r["gates"]["all_feature_canaries"]


@pytest.mark.parametrize("section,key,value", [
    ("screen", "all_catalogue_features_visible_only", False),
    ("screen", "whole_segments_with_buffer", "true"),
    ("screen", "withheld_positives", 0),
    ("screen", "candidate_pooled_dti", float("nan")),
    ("screen", "evaluator_sha256", BEST),
    ("screen", "baseline_sha256", CANDIDATE),
    ("screen", "pooled_delta_ci95", [-.1, .1]),
    ("screen", "ci_estimand", "mean fold delta"),
    ("confirmation", "split_id", "screen"),
    ("confirmation", "frozen_before_screen_results", False),
])
def test_invalid_holdout_cannot_promote(section, key, value):
    e = evidence_fixture()
    e[section][key] = value
    assert check(e)["verdict"] == "negative"


def test_canary_and_duplicate_thresholds_are_strict():
    e = evidence_fixture()
    e["feature_canaries"][0]["holdout_auc"] = .900001
    assert not check(e)["gates"]["all_feature_canaries"]
    e = evidence_fixture()
    e["duplicates"]["surface"]["comparisons"][0]["fraction_candidate_within_3px"] = .700001
    assert not check(e)["gates"]["surface_not_duplicate"]


def test_no_missing_registry_raster_or_canary_allowed():
    e = evidence_fixture()
    e["registry_raster_sha256s"].append(BEST)
    assert not check(e)["gates"]["final_dots_not_duplicate"]
    e = evidence_fixture()
    e["feature_names"].append("unmeasured")
    assert not check(e)["gates"]["all_feature_canaries"]


def test_malformed_types_fail_closed():
    for bad in [None, [], {"screen": []}, {"feature_names": [{}]}, {"shared_template": None}]:
        assert not check(bad)["eligible_for_selector"]


def test_format_pass_is_bound_to_exact_saved_bytes_and_note_budget():
    e = evidence_fixture()
    assert not assess(e, {"pass": True, "sha256": BEST}, CANDIDATE)["eligible_for_selector"]
    assert not assess(e, {"pass": "true", "sha256": CANDIDATE}, CANDIDATE)["eligible_for_selector"]
    e["submission_note"] = "x" * 141
    assert not check(e)["gates"]["short_note"]
    e["experiments"] = 4
    assert not check(e)["gates"]["budget"]


def test_promotion_cli_fails_closed_and_pins_its_sources(tmp_path):
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    evidence, output = tmp_path / "input.json", tmp_path / "gate.json"
    evidence.write_text("{}")
    result = subprocess.run([sys.executable, "scripts/check_promotion.py", "--evidence", str(evidence),
                             "--out", str(output)], cwd=root, capture_output=True, text=True)
    assert result.returncode == 2
    report = json.loads(output.read_text())
    assert report["gate_version"] == "g33-evidence-completeness-v1"
    assert len(report["gate_source_sha256"]) == 64
    assert report["raster_sha256"] is None
    assert report["validator"]["pass"] is False
    assert not report["ok_to_submit"]
    evidence.write_text('{"experiments": NaN}')
    result = subprocess.run([sys.executable, "scripts/check_promotion.py", "--evidence", str(evidence)],
                            cwd=root, capture_output=True, text=True)
    assert result.returncode == 2
    assert json.loads(result.stdout)["verdict"] == "negative"
