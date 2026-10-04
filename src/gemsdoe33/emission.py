"""Emission operators: ridge extraction, Poisson-disk thinning, and priority packing.

All operators are deterministic given their inputs; the packing order is either raster order (the
historical behaviour) or a supplied priority field (higher = emitted first).
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter


def dot_thin(mask: np.ndarray, min_dist: float, priority: np.ndarray | None = None,
             max_dots: int | None = None) -> np.ndarray:
    """Greedy Poisson-disk thinning of a boolean candidate mask.

    Walks candidates in descending ``priority`` (default: ascending raster index) and keeps a pixel
    iff no already-kept pixel is within ``min_dist`` pixels (Euclidean).  Uses a uniform spatial
    hash with cell size ``min_dist`` so the neighbourhood test touches at most 9 cells.

    ``min_dist = 2.828`` reproduces the historical ``d=2.8`` setting: a kept dot blocks everything
    inside a radius of sqrt(8) = 2.83 px = 283 m.
    """
    mask = np.asarray(mask, bool)
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return np.zeros_like(mask)
    if priority is None:
        order = np.arange(ys.size)
    else:
        p = np.asarray(priority, float)[ys, xs]
        order = np.lexsort((np.arange(ys.size), -p))
    cell = max(float(min_dist), 1.0)
    grid: dict[tuple[int, int], list[int]] = {}
    keep = np.zeros(ys.size, bool)
    r2 = min_dist * min_dist
    n_kept = 0
    for oi in order:
        if max_dots is not None and n_kept >= max_dots:
            break
        y = float(ys[oi])
        x = float(xs[oi])
        gy = int(y // cell)
        gx = int(x // cell)
        ok = True
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for j in grid.get((gy + dy, gx + dx), ()):
                    ddx = xs[j] - x
                    ddy = ys[j] - y
                    if ddx * ddx + ddy * ddy < r2:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            keep[oi] = True
            grid.setdefault((gy, gx), []).append(int(oi))
            n_kept += 1
    out = np.zeros_like(mask)
    out[ys[keep], xs[keep]] = True
    return out


def ridge_nms(field: np.ndarray, width: int = 1) -> np.ndarray:
    """Non-maximum suppression: pixels equal to the local max in a (2*width+1)^2 window."""
    f = np.nan_to_num(field, nan=-np.inf)
    mx = maximum_filter(f, size=2 * width + 1, mode="nearest")
    return (f >= mx) & np.isfinite(field)


def topk_mask(score: np.ndarray, domain: np.ndarray, k: int) -> np.ndarray:
    """The k highest-scoring pixels of ``score`` inside ``domain``.

    Ties are broken deterministically by row-major raster order. ``k=0`` returns an empty set;
    negative budgets are rejected rather than invoking NumPy's ``[-0:]`` all-elements edge case.
    """
    score = np.asarray(score)
    domain = np.asarray(domain, bool)
    if score.shape != domain.shape:
        raise ValueError("score and domain shapes must match")
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return np.zeros_like(domain)
    n = int(domain.sum())
    if k >= n:
        return domain.copy()
    flat = np.where(domain, np.nan_to_num(score, nan=-np.inf, posinf=-np.inf, neginf=-np.inf), -np.inf).reshape(-1)
    eligible = np.flatnonzero(domain.reshape(-1))
    # lexsort's last key is primary: descending score, then ascending flat index.
    order = np.lexsort((eligible, -flat[eligible]))
    chosen = eligible[order[:k]]
    out = np.zeros(domain.size, bool)
    out[chosen] = True
    return out.reshape(domain.shape)


def spacing_stats(mask: np.ndarray) -> dict:
    ys, xs = np.nonzero(mask)
    return {"n_dots": int(ys.size)}
