"""PFRT: listric dip-projected basement-to-piedmont offset transfer (label-free).

Frozen mechanism (evidence/pfrt_preregistration_20261027.json): basement-edge
crests are displaced updip by depth*cot(dip) before scoring, modelling a blind
listric normal fault whose buried basement break lies downdip of its piedmont
emergence. No labels, catalogue geometry (beyond the caller's exclusion mask),
or supervised fit are used, so the surface is fold-safe by construction.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from . import features
from .paths import CACHE_FEATURES

DIPS_DEG = (50.0, 60.0)
CREST_RANK_MIN = 0.90
OFFSET_MIN_PX, OFFSET_MAX_PX = 1.0, 10.0
CELL_M = 100.0


def _rank(values: np.ndarray, domain: np.ndarray) -> np.ndarray:
    out = np.zeros(values.shape, dtype=np.float32)
    v = np.asarray(values, dtype=np.float64)[domain]
    if v.size == 0:
        return out
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(v.size, dtype=np.float64)
    ranks[order] = (np.arange(v.size, dtype=np.float64) + 0.5) / v.size
    out[domain] = ranks.astype(np.float32)
    return out


def load_layers() -> dict[str, np.ndarray]:
    def load(name):
        return np.asarray(np.load(CACHE_FEATURES / f"{name}.npy", mmap_mode="r"), dtype=np.float32)
    return {
        "depth": load("depth_to_base_surf"),
        "depth_gm": load("depth_to_base_surf_gms2"),
        "grav_hg": load("iso_grav_anom_hg"),
    }


def pfrt_surface(layers: dict[str, np.ndarray], domain: np.ndarray) -> tuple[np.ndarray, dict]:
    domain = np.asarray(domain, bool)
    depth = np.nan_to_num(np.asarray(layers["depth"], dtype=np.float64), nan=0.0)
    depth = np.where(domain, depth, 0.0)
    smooth = gaussian_filter(depth, sigma=2.0, mode="nearest")
    gy, gx = np.gradient(smooth)
    gmag = np.hypot(gy, gx) + 1e-12
    edge = np.sqrt(_rank(np.nan_to_num(layers["depth_gm"], nan=0.0), domain)
                   * _rank(np.abs(np.nan_to_num(layers["grav_hg"], nan=0.0)), domain))
    ridge = features.nms_ridge(edge) > 0
    erank = _rank(edge, domain)
    crest = domain & ridge & (erank >= CREST_RANK_MIN) & (gmag > 0)
    ys, xs = np.nonzero(crest)
    vals = edge[ys, xs].astype(np.float64)
    uy, ux = -gy[ys, xs] / gmag[ys, xs], -gx[ys, xs] / gmag[ys, xs]
    splat = np.zeros(edge.shape, dtype=np.float64)
    tent = [(dy, dx, (1 - abs(dy) / 2) * (1 - abs(dx) / 2)) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    H, W = edge.shape
    for dip in DIPS_DEG:
        off = np.clip(depth[ys, xs] / np.tan(np.deg2rad(dip)) / CELL_M, OFFSET_MIN_PX, OFFSET_MAX_PX)
        ty = np.clip(np.rint(ys + uy * off).astype(int), 0, H - 1)
        tx = np.clip(np.rint(xs + ux * off).astype(int), 0, W - 1)
        for dy, dx, wgt in tent:
            yy = np.clip(ty + dy, 0, H - 1); xx = np.clip(tx + dx, 0, W - 1)
            np.add.at(splat, (yy, xx), vals * wgt / len(DIPS_DEG))
    splat = gaussian_filter(splat, sigma=1.0, mode="nearest")
    surf = _rank(splat, domain)
    surf[~domain] = 0.0
    return surf.astype(np.float32), {"n_crest": int(crest.sum()), "n_splat_positive": int((splat > 0).sum())}
