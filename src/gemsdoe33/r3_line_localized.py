"""A33-R3-LLC: label-free oriented scarp line evidence for line-localising the CSHT prior.

Frozen in ``evidence/a33_r3_preregistration_20261026.json`` before this file was written.

Physics / method (no catalogue access anywhere in this module):

1. Scarp evidence ``e`` per regime.
   * LiDAR regime (``lid_valid > 0``): mean of within-regime percentile ranks of the 1 m-derived
     ``lid_step_max``, ``lid_ex_max`` and ``lid_cross_max`` descriptors.
   * LiDAR-void regime (``lid_valid == 0``): within-regime percentile rank of ``det_elev_slope``.
2. Multi-scale Hessian bright-ridge strength (Steger 1998, doi:10.1109/34.659930; Frangi et al.
   1998, doi:10.1007/BFb0056195): ``R = max_sigma sigma^2 * max(-lambda_min, 0)``, sigma in {1, 2} px.
3. Oriented line integral: ``OLI = max_a (R * K_a)`` over 12 azimuths, ``K_a`` an anisotropic
   unit-sum Gaussian with sigma_long = 5 px (500 m) and sigma_short = 0.75 px.
4. One-pixel non-maximum suppression across the winning azimuth.
5. ``L_line`` = within-regime percentile rank of OLI multiplied by the NMS mask (0 off-line).

The surface fused with the fold-trained CSHT prior is ``S = rank(P_csht)^gamma * L_line``.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.signal import oaconvolve

from .paths import CACHE_FEATURES

N_ANGLES = 12
SIGMA_LONG = 5.0
SIGMA_SHORT = 0.75
HESSIAN_SIGMAS = (1.0, 2.0)
LIDAR_EVIDENCE_BANDS = ("lid_step_max", "lid_ex_max", "lid_cross_max")
VOID_EVIDENCE_BAND = "det_elev_slope"


def _load(name: str) -> np.ndarray:
    return np.asarray(np.load(CACHE_FEATURES / f"{name}.npy", mmap_mode="r"), dtype=np.float32)


def percentile_rank(values: np.ndarray, domain: np.ndarray) -> np.ndarray:
    """Average-tie-free percentile rank in (0, 1] over finite cells of ``domain``; 0 elsewhere.

    Non-finite cells inside ``domain`` receive rank 0 (no evidence), never an imputed value.
    """
    values = np.asarray(values, dtype=np.float64)
    domain = np.asarray(domain, dtype=bool)
    out = np.zeros(values.shape, dtype=np.float32)
    ok = domain & np.isfinite(values)
    n = int(ok.sum())
    if n == 0:
        return out
    v = values[ok]
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = np.arange(1, n + 1, dtype=np.float64)
    # Ties share the maximum rank of their group so the transform is a function of value only.
    sv = v[order]
    _, first, counts = np.unique(sv, return_index=True, return_counts=True)
    group_max = (first + counts).astype(np.float64)
    ranks[order] = np.repeat(group_max, counts)
    out[ok] = (ranks / n).astype(np.float32)
    return out


def regimes(footprint: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    fp = np.asarray(footprint, dtype=bool)
    lid = fp & (np.nan_to_num(_load("lid_valid"), nan=0.0) > 0.5)
    return lid, fp & ~lid


def scarp_evidence(footprint: np.ndarray) -> dict[str, np.ndarray]:
    """Label-free per-regime scarp evidence fields in [0, 1] (0 outside their regime)."""
    lid, void = regimes(footprint)
    parts = [percentile_rank(_load(b), lid) for b in LIDAR_EVIDENCE_BANDS]
    e_lid = np.where(lid, np.mean(parts, axis=0), 0.0).astype(np.float32)
    e_void = percentile_rank(_load(VOID_EVIDENCE_BAND), void)
    return {"e_lid": e_lid, "e_void": e_void, "lid": lid, "void": void}


def hessian_ridge(field: np.ndarray, regime: np.ndarray) -> np.ndarray:
    """Scale-normalised bright-ridge strength; out-of-regime cells filled with the regime median."""
    regime = np.asarray(regime, dtype=bool)
    f = np.asarray(field, dtype=np.float32).copy()
    fill = float(np.median(f[regime])) if regime.any() else 0.0
    f[~regime] = fill
    best = np.zeros(f.shape, dtype=np.float32)
    for s in HESSIAN_SIGMAS:
        hyy = gaussian_filter(f, s, order=(2, 0), mode="nearest")
        hxx = gaussian_filter(f, s, order=(0, 2), mode="nearest")
        hxy = gaussian_filter(f, s, order=(1, 1), mode="nearest")
        half_tr = 0.5 * (hxx + hyy)
        disc = np.sqrt(0.25 * (hxx - hyy) ** 2 + hxy ** 2)
        lam_min = half_tr - disc
        r = (s * s) * np.maximum(-lam_min, 0.0)
        np.maximum(best, r.astype(np.float32), out=best)
        del hyy, hxx, hxy, half_tr, disc, lam_min, r
    return np.where(regime, best, 0.0).astype(np.float32)


def line_kernel(angle_rad: float) -> np.ndarray:
    """Unit-sum anisotropic Gaussian elongated along azimuth ``angle_rad`` (x = col, y = row)."""
    half = int(np.ceil(3.0 * SIGMA_LONG))
    yy, xx = np.mgrid[-half : half + 1, -half : half + 1].astype(np.float64)
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    along = xx * c + yy * s
    across = -xx * s + yy * c
    k = np.exp(-0.5 * ((along / SIGMA_LONG) ** 2 + (across / SIGMA_SHORT) ** 2))
    return (k / k.sum()).astype(np.float32)


def oriented_line_integral(ridge: np.ndarray, regime: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Max over 12 azimuths of the along-strike integral of ridge strength + winning azimuth index."""
    regime = np.asarray(regime, dtype=bool)
    r = np.where(regime, ridge, 0.0).astype(np.float32)
    best = np.full(r.shape, -np.inf, dtype=np.float32)
    arg = np.zeros(r.shape, dtype=np.int8)
    for i in range(N_ANGLES):
        a = np.pi * i / N_ANGLES
        resp = oaconvolve(r, line_kernel(a), mode="same").astype(np.float32)
        better = resp > best
        best[better] = resp[better]
        arg[better] = i
        del resp, better
    best = np.where(regime, best, 0.0).astype(np.float32)
    return best, arg


def nms_across(oli: np.ndarray, arg: np.ndarray, regime: np.ndarray) -> np.ndarray:
    """Keep cells that are >= both neighbours along the normal of their winning azimuth."""
    h, w = oli.shape
    pad = np.pad(oli, 1, mode="constant", constant_values=0.0)
    keep = np.zeros((h, w), dtype=bool)
    for i in range(N_ANGLES):
        a = np.pi * i / N_ANGLES
        ny, nx = int(np.rint(np.cos(a))), int(np.rint(-np.sin(a)))  # normal = (-sin, cos) in (x, y)
        # normal vector in (row, col) = (cos a, -sin a)
        sel = arg == i
        if not sel.any():
            continue
        plus = pad[1 + ny : 1 + ny + h, 1 + nx : 1 + nx + w]
        minus = pad[1 - ny : 1 - ny + h, 1 - nx : 1 - nx + w]
        keep |= sel & (oli >= plus) & (oli >= minus)
    return keep & np.asarray(regime, dtype=bool) & (oli > 0)


def build_line_evidence(footprint: np.ndarray) -> dict[str, np.ndarray]:
    """Full label-free line-evidence bundle; deterministic and catalogue-free."""
    ev = scarp_evidence(footprint)
    out: dict[str, np.ndarray] = {"e_lid": ev["e_lid"], "e_void": ev["e_void"]}
    l_line = np.zeros(footprint.shape, dtype=np.float32)
    oli_all = np.zeros(footprint.shape, dtype=np.float32)
    ridge_all = np.zeros(footprint.shape, dtype=np.float32)
    nms_all = np.zeros(footprint.shape, dtype=bool)
    for key, regime in (("e_lid", ev["lid"]), ("e_void", ev["void"])):
        if not regime.any():
            continue
        ridge = hessian_ridge(ev[key], regime)
        oli, arg = oriented_line_integral(ridge, regime)
        nms = nms_across(oli, arg, regime)
        rank = percentile_rank(oli, regime)
        l_line = np.where(regime, rank * nms, l_line).astype(np.float32)
        oli_all = np.where(regime, rank, oli_all).astype(np.float32)
        ridge_all = np.where(regime, percentile_rank(ridge, regime), ridge_all).astype(np.float32)
        nms_all |= nms
        del ridge, oli, arg, nms, rank
    out.update({"ridge_rank": ridge_all, "oli_rank": oli_all, "l_line": l_line, "nms": nms_all,
                "lid": ev["lid"], "void": ev["void"]})
    return out


def fuse(p_csht: np.ndarray, l_line: np.ndarray, domain: np.ndarray, gamma: float) -> np.ndarray:
    """S = rank(P_csht)^gamma * L_line inside ``domain`` (0 elsewhere), values in [0, 1]."""
    rp = percentile_rank(p_csht, domain)
    s = np.where(domain, np.power(rp, gamma, dtype=np.float32) * l_line, 0.0)
    return np.clip(s, 0.0, 1.0).astype(np.float32)
