"""Exact binary rank-correlation and directional dot-overlap diagnostics.

This is a duplicate guard, NOT a uniqueness certificate or geological evaluator.
For binary rasters Spearman (average tied ranks) is exactly Pearson/phi.
Constant rasters have undefined rho and MUST NOT pass the guard.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import binary_dilation


def binary_comparison(candidate, registry, footprint, *, near_other=None):
    a, b, valid = np.asarray(candidate), np.asarray(registry), np.asarray(footprint)
    if a.ndim != 2 or a.shape != b.shape or a.shape != valid.shape:
        raise ValueError("candidate/registry/footprint must be equal-shaped 2D grids")
    if valid.dtype != np.bool_ or not valid.any():
        raise ValueError("footprint must be nonempty boolean mask")
    if not np.isin(a[valid], (0, 1)).all() or not np.isin(b[valid], (0, 1)).all():
        raise ValueError("binary comparison requires finite binary values inside footprint")
    a, b = (a > 0) & valid, (b > 0) & valid
    n, na, nb = int(valid.sum()), int(a.sum()), int(b.sum())
    both = int((a & b).sum())
    denom = math.sqrt(na * (n - na) * nb * (n - nb))
    rho = (n * both - na * nb) / denom if denom else None
    if near_other is None:
        yy, xx = np.mgrid[-3:4, -3:4]
        near_other = binary_dilation(b, structure=yy * yy + xx * xx <= 9)
    elif np.asarray(near_other).shape != a.shape or np.asarray(near_other).dtype != np.bool_:
        raise ValueError("near_other must be a matching boolean mask")
    overlap = int((a & near_other).sum())
    fraction = overlap / na if na else None
    trigger = (rho is not None and rho > 0.90) or (fraction is not None and fraction > 0.70)
    defined = rho is not None and fraction is not None
    return {"spearman_rho": rho, "candidate_dots": na, "registry_dots": nb,
            "candidate_dots_within_3px": overlap, "fraction_candidate_within_3px": fraction,
            "duplicate_trigger": bool(trigger), "guard_pass": bool(defined and not trigger),
            "undefined": not defined}
