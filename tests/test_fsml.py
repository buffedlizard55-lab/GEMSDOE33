"""FSML/FSML2 unit tests (synthetic, cache-free except where noted)."""
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33 import fsml  # noqa: E402


def test_thermal_orphan_zero_near_visible():
    dens = np.ones((20, 20), dtype=np.float32)
    vis = np.zeros((20, 20), bool)
    vis[10, :] = True
    d = distance_transform_edt(~vis)
    orph = fsml.thermal_orphan(dens, d)
    assert orph[10, 0] == 0.0          # on the fault: not orphan
    assert orph[0, 0] > orph[8, 0]     # grows with distance from visible fault
    assert np.isfinite(orph).all()


def test_geo_tip_lobe_extends_beyond_endpoints():
    fp = np.ones((60, 60), bool)
    vis = np.zeros((60, 60), bool)
    vis[30, 10:40] = True  # one horizontal segment, 30 px
    d = distance_transform_edt(~vis)
    geo = fsml.geo_tip_lobe(vis, d, fp)
    assert geo.shape == fp.shape and np.isfinite(geo).all()
    # lobe mass beyond both tips along strike
    assert geo[30, 44] > 0 and geo[30, 5] > 0
    # far corner untouched by lobes (band limited to d<=30)
    assert geo[0, 59] == 0.0


def test_pu_expert_smoke_synthetic():
    rng = np.random.default_rng(0)
    H = W = 80
    fp = np.ones((H, W), bool)
    signal = np.zeros((H, W), np.float32)
    signal[:, :40] = 1.0
    arrays = {"a": signal + rng.normal(0, 0.1, (H, W)).astype(np.float32),
              "b": rng.normal(0, 1, (H, W)).astype(np.float32)}
    visible = np.zeros((H, W), bool)
    visible[::7, 5:35] = True  # positives only in signal half
    d = distance_transform_edt(~visible)
    model, rep = fsml._fit_pu_expert(arrays, ("a", "b"), fp, visible, d, seed=3)
    assert rep["pos"] >= 200 and rep["rn"] >= 1  # small grid: floor path allowed
    from gemsdoe33.csht_transfer import _predict_model
    p = _predict_model(model, arrays, ("a", "b"), fp)
    assert p[:, :40].mean() > p[:, 40:].mean()


def test_expert_channel_groups_disjoint_and_named():
    seen = []
    for names in fsml.EXPERT_CHANNELS.values():
        assert not (set(names) & set(seen)), "expert channel groups must be disjoint"
        seen += names
    assert set(fsml.EXPERT_CHANNELS) == {"S_scarp", "G_geopot", "C_cover", "T_therm"}
