"""First-principles checks of the competition metric and its exact marginal rule."""

from __future__ import annotations

import numpy as np
import pytest

from gemsdoe33 import metric


def _grid(dots, truth, shape=(31, 31), value=1.0):
    p = np.zeros(shape, dtype=np.float32)
    for y, x in dots:
        p[y, x] = value
    g = np.zeros(shape, dtype=bool)
    for y, x in truth:
        g[y, x] = True
    return p, g


def slow_dti(p, g, valid=None):
    """Literal O(H*W*|G|) reference for small test arrays."""
    p = np.asarray(p, float)
    g = np.asarray(g, bool)
    active = np.ones(g.shape, bool) if valid is None else np.asarray(valid, bool)
    gt = np.argwhere(g & active)
    pred = np.argwhere((p > 0) & active)
    tp = 0.0
    for gy, gx in gt:
        best = 0.0
        for py, px in pred:
            d = float(np.hypot(py - gy, px - gx))
            best = max(best, float(p[py, px]) * max(1.0 - d / 3.0, 0.0))
        tp += best
    fp = 0.0
    for py, px in pred:
        nearest = min((float(np.hypot(py - gy, px - gx)) for gy, gx in gt), default=np.inf)
        fp += float(p[py, px]) * (1.0 - max(1.0 - nearest / 3.0, 0.0))
    fn = len(gt) - tp
    score = tp / (tp + 0.2 * fp + 0.8 * fn + 1e-7) if gt.size else 0.0
    return {"TPw": tp, "FPw": fp, "FNw": fn, "dti": score}


def test_kernel_is_triangular_and_zero_at_support():
    assert metric.kernel_from_distance(0) == pytest.approx(1.0)
    assert metric.kernel_from_distance(1.5) == pytest.approx(0.5)
    assert metric.kernel_from_distance(3) == pytest.approx(0.0)
    assert metric.kernel_from_distance(5) == pytest.approx(0.0)


def test_binary_metric_matches_literal_reference():
    p, g = _grid([(10, 10), (10, 13), (20, 20), (23, 23)], [(10, 11), (20, 21), (5, 5)])
    expected = slow_dti(p, g)
    got = metric.dti_binary(p, g)
    assert got["TPw"] == pytest.approx(expected["TPw"])
    assert got["FPw"] == pytest.approx(expected["FPw"])
    assert got["FNw"] == pytest.approx(expected["FNw"])
    assert got["dti"] == pytest.approx(expected["dti"])


def test_soft_metric_matches_literal_reference_and_is_not_thresholded():
    p = np.zeros((25, 25), dtype=np.float32)
    p[10, 10] = 0.4
    p[10, 12] = 0.8
    p[20, 20] = 0.6
    g = np.zeros_like(p, dtype=bool)
    g[10, 11] = True
    g[20, 22] = True
    expected = slow_dti(p, g)
    got = metric.dti_exact(p, g)
    assert got["TPw"] == pytest.approx(expected["TPw"])
    assert got["FPw"] == pytest.approx(expected["FPw"])
    assert got["FNw"] == pytest.approx(expected["FNw"])
    assert got["dti"] == pytest.approx(expected["dti"])


def test_empty_prediction_empty_truth_and_far_prediction():
    p, g = _grid([], [(10, 10)])
    assert metric.dti_binary(p, g)["dti"] == 0.0
    p, g = _grid([(10, 10)], [])
    assert metric.dti_binary(p, g)["dti"] == 0.0
    p, g = _grid([(10, 13)], [(10, 10)])
    assert metric.dti_binary(p, g)["TPw"] == pytest.approx(0.0)
    assert metric.dti_binary(p, g)["FPw"] == pytest.approx(1.0)


def test_masked_known_pixels_do_not_contribute():
    p, g = _grid([(10, 10), (20, 20)], [(10, 10), (20, 20)])
    known = np.zeros_like(g)
    known[10, 10] = True
    r = metric.dti_binary(p, g, known=known)
    assert r["n_truth"] == 1
    assert r["n_emitted"] == 1
    assert r["dti"] == pytest.approx(1.0)


def test_nonfinite_and_out_of_range_inside_active_domain_rejected():
    g = np.zeros((10, 10), bool)
    g[5, 5] = True
    for bad in (np.nan, np.inf, -0.01, 1.01):
        p = np.zeros((10, 10), dtype=float)
        p[5, 5] = bad
        with pytest.raises(ValueError):
            metric.dti_exact(p, g)


def test_nonfinite_outside_valid_domain_is_ignored():
    p = np.zeros((10, 10), dtype=float)
    p[5, 5] = 1.0
    p[0, 0] = np.nan
    g = np.zeros((10, 10), bool)
    g[5, 5] = True
    valid = np.zeros_like(g)
    valid[5, 5] = True
    assert metric.dti_exact(p, g, valid=valid)["dti"] == pytest.approx(1.0)


def test_isolated_dot_point_rule_and_general_ratio_rule_are_distinct():
    s = 0.26
    assert metric.isolated_dot_bar(s) == pytest.approx(0.052)
    assert metric.ratio_bar(s) == pytest.approx(0.2 * s / (1 - 0.2 * s))
    assert metric.ratio_bar(s) > metric.isolated_dot_bar(s)


def test_overlapping_addition_uses_incremental_tp_not_raw_kernel():
    # The first dot already gives full credit to this truth; the second dot's k=2/3
    # does not add TP because the max is already 1.0. The raw k is therefore not its dTP.
    base, truth = _grid([(10, 10)], [(10, 10)])
    add = np.zeros_like(truth)
    add[10, 11] = True
    out = metric.marginal_gain(base, add, truth)
    assert out["dTP"] == pytest.approx(0.0)
    assert out["dFP"] > 0
    assert out["dti_union"] < out["dti_base"]


def test_marginal_gain_matches_full_union_metric():
    base, truth = _grid([(10, 10)], [(10, 12), (20, 20)])
    add = np.zeros_like(truth)
    add[20, 19] = True
    out = metric.marginal_gain(base, add, truth)
    expected = metric.dti_binary((base.astype(bool) | add).astype(float), truth)["dti"]
    assert out["dti_union"] == pytest.approx(expected)
