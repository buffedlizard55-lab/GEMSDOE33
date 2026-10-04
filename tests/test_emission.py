"""Deterministic, budget-safe emission primitives."""
from __future__ import annotations

import numpy as np
import pytest

from gemsdoe33.emission import dot_thin, topk_mask


def test_topk_zero_is_empty_and_negative_rejected():
    score = np.arange(9).reshape(3, 3)
    domain = np.ones((3, 3), bool)
    assert not topk_mask(score, domain, 0).any()
    with pytest.raises(ValueError):
        topk_mask(score, domain, -1)


def test_topk_returns_correct_count_and_deterministic_tie_break():
    score = np.ones((3, 3))
    domain = np.ones((3, 3), bool)
    out = topk_mask(score, domain, 4)
    assert int(out.sum()) == 4
    assert np.flatnonzero(out.reshape(-1)).tolist() == [0, 1, 2, 3]


def test_topk_rejects_shape_mismatch():
    with pytest.raises(ValueError):
        topk_mask(np.ones((2, 3)), np.ones((3, 2), bool), 1)


def test_dot_thin_respects_minimum_spacing_and_budget():
    candidates = np.ones((12, 12), bool)
    out = dot_thin(candidates, min_dist=3.0, max_dots=10)
    assert out.sum() == 10
    ys, xs = np.nonzero(out)
    for i in range(len(ys)):
        for j in range(i):
            assert np.hypot(ys[i] - ys[j], xs[i] - xs[j]) >= 3.0


def test_dot_thin_priority_changes_selection_deterministically():
    candidates = np.ones((8, 8), bool)
    priority = np.zeros((8, 8), float)
    priority[6, 6] = 100
    first = dot_thin(candidates, min_dist=3.0, priority=priority, max_dots=1)
    second = dot_thin(candidates, min_dist=3.0, priority=priority, max_dots=1)
    assert first[6, 6]
    assert np.array_equal(first, second)
