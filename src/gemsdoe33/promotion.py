"""Fail-closed evidence-completeness gate; never selects or uploads a slot.

This checks a run's declared evidence contract, not the truth of arbitrary JSON.
Evaluator/writer results must come from a pinned shared template, not a private
fork. Format validity alone must never enable a submit button.
"""
from __future__ import annotations

import math
import re

# Public schema contract shared with the slot selector; empty/partial gate maps are not proof.
REQUIRED_GATE_NAMES = (
    "identity", "explicit_lane", "shared_template", "baseline_identity",
    "screen_beats_current_best", "independent_confirmation", "all_feature_canaries",
    "surface_not_duplicate", "final_dots_not_duplicate", "saved_bytes_format",
    "short_note", "budget",
)

_SHA = re.compile(r"[0-9a-f]{64}\Z")


def _number(x):
    return type(x) in (int, float) and math.isfinite(x)


def _sha(x):
    return isinstance(x, str) and bool(_SHA.fullmatch(x))


def _holdout(run, candidate_sha, best_sha, evaluator_sha):
    if not isinstance(run, dict):
        return False
    ci = run.get("pooled_delta_ci95")
    baseline, candidate = run.get("baseline_pooled_dti"), run.get("candidate_pooled_dti")
    return all((
        run.get("label") == "HOLDOUT-DTI",
        bool(run.get("evaluator_version")),
        run.get("evaluator_sha256") == evaluator_sha,
        run.get("candidate_sha256") == candidate_sha,
        run.get("baseline_sha256") == best_sha,
        type(run.get("withheld_positives")) is int and run["withheld_positives"] > 0,
        run.get("whole_segments_with_buffer") is True,
        run.get("all_catalogue_features_visible_only") is True,
        run.get("visible_faults_masked_pixel_exactly") is True,
        run.get("alpha") == 0.2, run.get("beta") == 0.8,
        run.get("kernel") == "triangular", run.get("radius_m") == 300,
        _number(candidate) and 0 <= candidate <= 1,
        _number(baseline) and 0 <= baseline <= 1,
        _number(candidate) and _number(baseline) and candidate > baseline,
        isinstance(ci, list) and len(ci) == 2 and all(_number(v) for v in ci)
        and 0 < ci[0] <= ci[1] <= 1,
        run.get("ci_estimand") == "pooled paired delta",
    ))


def _assess(evidence, format_audit, raster_sha256):
    """Return every gate + reasons; missing, null, NaN and string booleans fail."""
    shared = evidence.get("shared_template", {})
    candidate = evidence.get("candidate_sha256")
    best = evidence.get("current_holdout_best_sha256")
    evaluator_sha = shared.get("evaluator_sha256")
    screen, confirm = evidence.get("screen", {}), evidence.get("confirmation", {})
    gates = {}
    gates["identity"] = _sha(candidate) and candidate == raster_sha256
    gates["explicit_lane"] = isinstance(evidence.get("lane"), str) and bool(evidence["lane"].strip())
    gates["shared_template"] = all(_sha(shared.get(k)) for k in (
        "source_manifest_sha256", "feature_cache_sha256", "evaluator_sha256", "writer_sha256"))
    gates["baseline_identity"] = _sha(best)
    gates["screen_beats_current_best"] = _holdout(screen, candidate, best, evaluator_sha)
    gates["independent_confirmation"] = (
        _holdout(confirm, candidate, best, evaluator_sha)
        and confirm.get("frozen_before_screen_results") is True
        and bool(screen.get("split_id")) and bool(confirm.get("split_id"))
        and screen.get("split_id") != confirm.get("split_id")
        and confirm.get("independent_of_screen") is True
    )
    expected_features = evidence.get("feature_names", [])
    canaries = evidence.get("feature_canaries", [])
    gates["all_feature_canaries"] = (
        isinstance(expected_features, list) and bool(expected_features)
        and all(isinstance(f, str) for f in expected_features)
        and len(expected_features) == len(set(expected_features))
        and isinstance(canaries, list) and all(isinstance(c, dict) for c in canaries)
        and len(canaries) == len(expected_features)
        and {c.get("feature") for c in canaries} == set(expected_features)
        and all(_number(c.get("holdout_auc")) and 0 <= c["holdout_auc"] <= 0.90
                and c.get("split_id") == screen.get("split_id")
                and c.get("visible_only") is True for c in canaries)
    )
    registry = evidence.get("registry_sha256")
    expected = evidence.get("registry_raster_sha256s", [])
    for phase in ("surface", "final_dots"):
        record = evidence.get("duplicates", {}).get(phase, {})
        comparisons = record.get("comparisons", [])
        gates[f"{phase}_not_duplicate"] = (
            _sha(registry) and record.get("registry_sha256") == registry
            and evidence.get("registry_complete") is True
            and isinstance(expected, list) and bool(expected) and all(_sha(s) for s in expected)
            and len(expected) == len(set(expected))
            and isinstance(comparisons, list) and all(isinstance(c, dict) for c in comparisons)
            and len(comparisons) == len(expected)
            and {c.get("raster_sha256") for c in comparisons} == set(expected)
            and all(_number(c.get("spearman_rho")) and -1 <= c["spearman_rho"] <= 0.90
                    and _number(c.get("fraction_candidate_within_3px"))
                    and 0 <= c["fraction_candidate_within_3px"] <= 0.70 for c in comparisons)
            and (record.get("candidate_sha256") == candidate if phase == "final_dots"
                 else _sha(record.get("surface_sha256")))
        )
    gates["saved_bytes_format"] = format_audit.get("pass") is True and format_audit.get("sha256") == candidate
    note = evidence.get("submission_note")
    gates["short_note"] = isinstance(note, str) and 0 < len(note) <= 140
    count = evidence.get("experiments")
    elapsed = evidence.get("elapsed_seconds")
    gates["budget"] = type(count) is int and 0 <= count <= 3 and _number(elapsed) and 0 <= elapsed <= 7200
    gates = {k: bool(v) for k, v in gates.items()}
    eligible = all(gates.values())
    return {"schema_version": 1, "gates": gates,
            "failed_gates": [k for k, v in gates.items() if not v],
            "verdict": "promote" if eligible else "negative",
            "eligible_for_selector": eligible,
            "ok_to_submit": False,
            "slot_policy": "Separate selector and verified weekly-cap check required; this tool never uploads.",
            "qualification": "Evidence completeness/arithmetic only; cannot authenticate arbitrary supplied receipts."}


def assess(evidence, format_audit, raster_sha256):
    """Fail closed even on malformed or adversarial JSON types."""
    try:
        return _assess(evidence, format_audit, raster_sha256)
    except (TypeError, AttributeError, ValueError, KeyError):
        return {"schema_version": 1, "gates": {"well_formed_evidence": False},
                "failed_gates": ["well_formed_evidence"], "verdict": "negative",
                "eligible_for_selector": False, "ok_to_submit": False,
                "qualification": "Malformed evidence; no slot or artifact authorization."}
