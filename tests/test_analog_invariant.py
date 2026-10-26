"""Small deterministic checks for the A33-L1 lane transforms."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gemsdoe33 import analog_invariant as model

ROOT = Path(__file__).resolve().parents[1]


def test_feature_contract_matches_frozen_preregistration():
    prereg = json.loads((ROOT / "evidence/analog_lane_preregistration_20261025.json").read_text())
    selected = next(row for row in prereg["hypotheses_ranked"] if row["id"] == "A33-L1")
    assert list(model.FEATURE_NAMES) == selected["layers"]
    frozen = prereg["frozen_parameters"]
    assert model.QUANTILE_KNOTS == frozen["quantile_knots"]
    assert model.FUSION_TARGET_WEIGHT == frozen["fusion_target_weight"]
    assert model.FUSION_ANALOG_WEIGHT == frozen["fusion_analog_weight"]
    assert model.HGB_CONFIG == {
        "max_iter": 140,
        "learning_rate": 0.08,
        "max_leaf_nodes": 31,
        "l2_regularization": 1.0,
        "early_stopping": False,
    }


def test_quantile_map_moves_source_values_into_target_units():
    source_q = np.array([[0.0, 10.0], [1.0, 20.0], [2.0, 30.0]], dtype=np.float32)
    target_q = np.array([[100.0, -3.0], [200.0, -2.0], [300.0, -1.0]], dtype=np.float32)
    x = np.array([[0.5, 15.0], [1.5, 25.0]], dtype=np.float32)
    mapped = model._map_quantiles(x, source_q, target_q)
    assert np.allclose(mapped, [[150.0, -2.5], [250.0, -1.5]])


def test_quantile_map_is_stable_when_source_feature_is_constant():
    source_q = np.array([[2.0], [2.0], [2.0]], dtype=np.float32)
    target_q = np.array([[4.0], [5.0], [6.0]], dtype=np.float32)
    x = np.array([[1.0], [2.0], [3.0]], dtype=np.float32)
    # The first target knot is the deterministic convention for a degenerate source.
    assert np.array_equal(model._map_quantiles(x, source_q, target_q), np.full((3, 1), 4.0))


def test_rank_fusion_uses_frozen_80_20_weights_and_domain_only():
    domain = np.ones((11, 10), dtype=bool)
    domain[-1] = False
    regional = np.arange(110, dtype=np.float32).reshape(11, 10)
    adapted = -regional
    regional[-1] = 999.0
    adapted[-1] = -999.0
    fused = model.fuse(regional, adapted, domain)
    assert np.all(fused[-1] == 0.0)
    # Opposing ranks reduce to 0.8*r + 0.2*(1-r), so regional still dominates.
    assert np.all(np.diff(fused[:10].ravel()) > 0)
    expected = (
        0.8 * model.percentile_surface(regional, domain)
        + 0.2 * model.percentile_surface(adapted, domain)
    )
    assert np.allclose(fused, np.where(domain, expected, 0.0))
