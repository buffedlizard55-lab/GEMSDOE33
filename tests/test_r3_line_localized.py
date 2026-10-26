"""Synthetic checks for the A33-R3 line-localised evidence (no data needed)."""
import numpy as np

from gemsdoe33 import r3_line_localized as llc


def _line_field(angle_deg=30.0, n=96, seed=0):
    rng = np.random.default_rng(seed)
    f = rng.normal(0.0, 0.3, (n, n)).astype(np.float32)
    yy, xx = np.mgrid[0:n, 0:n]
    a = np.deg2rad(angle_deg)
    dist = np.abs(-(xx - n / 2) * np.sin(a) + (yy - n / 2) * np.cos(a))
    line = dist < 0.7
    f[line] += 2.0
    return f, line, dist


def test_percentile_rank_bounds_and_domain():
    v = np.array([[3.0, 1.0], [2.0, 2.0]], dtype=np.float32)
    d = np.array([[True, True], [True, False]])
    r = llc.percentile_rank(v, d)
    assert r[1, 1] == 0.0 and 0.0 <= r.min() and r.max() <= 1.0
    assert r[0, 0] > r[1, 0] > r[0, 1]


def test_oriented_integral_finds_line_and_nms_thins():
    f, line, dist = _line_field()
    regime = np.ones_like(line)
    ridge = llc.hessian_ridge(f, regime)
    oli, arg = llc.oriented_line_integral(ridge, regime)
    nms = llc.nms_across(oli, arg, regime)
    k = int(line.sum() * 0.6)
    top = np.argsort(oli.ravel())[::-1][:k]
    assert (dist.ravel()[top] <= 1.0).mean() > 0.9
    assert nms.mean() < 0.5


def test_fuse_is_zero_outside_domain_and_in_unit_range():
    rng = np.random.default_rng(1)
    p = rng.random((20, 20)).astype(np.float32)
    l = rng.random((20, 20)).astype(np.float32)
    dom = np.zeros((20, 20), bool)
    dom[5:15, 5:15] = True
    s = llc.fuse(p, l, dom, 0.5)
    assert s[~dom].max() == 0.0 and s.min() >= 0.0 and s.max() <= 1.0
