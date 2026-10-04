"""Spatial indexing primitives for catalogue-only out-of-fold feature research.

``quadrant_ids`` is used to exclude one broad raster quadrant while fitting the public-catalogue
research detector. It is **not** a competition holdout, does not produce hidden truth, and does not
validate generalization to faults absent from USGS/INGENIOUS. The previous pseudo-hidden scoring
instrument was withdrawn because it used sampled held-out truth coordinates to reconstruct
predictions; that implementation is preserved under ``archive/withdrawn_first_pass/src`` for audit
only. No active code here constructs pseudo-hidden labels or a leaderboard proxy.
"""
from __future__ import annotations

import numpy as np


def quadrant_ids(footprint: np.ndarray) -> np.ndarray:
    """Return a broad row/column quadrant ID; outside-footprint cells are ``-1``.

    The split is a lightweight spatial grouping convenience, not a fault-system or field-level
    split. It is only used for out-of-fold fitting against the public catalogue and must not be
    described as independent validation of private or unmapped target faults.
    """
    mask = np.asarray(footprint, dtype=bool)
    if mask.ndim != 2:
        raise ValueError("footprint must be a 2D mask")
    rows, cols = np.nonzero(mask)
    if rows.size == 0:
        raise ValueError("footprint contains no valid cells")
    mid_row = int(np.median(rows))
    mid_col = int(np.median(cols))
    yy, xx = np.ogrid[:mask.shape[0], :mask.shape[1]]
    out = np.full(mask.shape, -1, dtype=np.int8)
    out[(yy < mid_row) & (xx < mid_col) & mask] = 0
    out[(yy < mid_row) & (xx >= mid_col) & mask] = 1
    out[(yy >= mid_row) & (xx < mid_col) & mask] = 2
    out[(yy >= mid_row) & (xx >= mid_col) & mask] = 3
    return out
