"""Deterministic geodesic Poisson-disk thinning used by the H19-5 baseline.

This is a focused port of the deterministic breadth-first implementation in
GEMSDOE28 ``src/gems27/thinning.py``. It keeps a subset of the input mask and
uses no labels or scores itself; callers control which catalogue labels are
masked before thinning.
"""

from __future__ import annotations

from collections import deque

import numpy as np
from scipy.ndimage import label


def dot_thin(mask: np.ndarray, min_dist: float) -> np.ndarray:
    """Keep input pixels at least ``min_dist`` pixels apart (Euclidean distance).

    Connected components are visited in raster order, using FIFO breadth-first
    traversal. The output is deterministic for the same input and is always a
    subset of it.
    """
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2:
        raise ValueError("dot_thin requires a 2-D mask")
    if not np.isfinite(min_dist) or min_dist < 0:
        raise ValueError("min_dist must be finite and non-negative")
    if min_dist <= 1.0 or not mask.any():
        return mask.copy()

    height, width = mask.shape
    pad = int(np.ceil(min_dist)) + 1
    padded_width = width + 2 * pad
    padded_height = height + 2 * pad
    padded = np.zeros((padded_height, padded_width), dtype=bool)
    padded[pad:pad + height, pad:pad + width] = mask

    flat = bytearray(padded.tobytes())
    n_cells = padded_height * padded_width
    visited = bytearray(n_cells)
    blocked = bytearray(n_cells)
    kept = bytearray(n_cells)

    radius = int(np.ceil(min_dist))
    radius_sq = min_dist * min_dist
    disk_offsets = [
        dy * padded_width + dx
        for dy in range(-radius, radius + 1)
        for dx in range(-radius, radius + 1)
        if dy * dy + dx * dx < radius_sq
    ]
    eight_neighbors = (
        -padded_width - 1, -padded_width, -padded_width + 1,
        -1, 1,
        padded_width - 1, padded_width, padded_width + 1,
    )

    components, _ = label(padded, structure=np.ones((3, 3), dtype=np.int8))
    component_ids = components.ravel()
    nonzero_order = np.flatnonzero(component_ids)
    if nonzero_order.size:
        _, first_positions = np.unique(component_ids[nonzero_order], return_index=True)
        seeds = nonzero_order[np.sort(first_positions)]
    else:
        seeds = np.empty(0, dtype=np.int64)

    for seed in seeds.tolist():
        if visited[seed]:
            continue
        visited[seed] = 1
        queue = deque((seed,))
        while queue:
            cell = queue.popleft()
            if not blocked[cell]:
                kept[cell] = 1
                for offset in disk_offsets:
                    blocked[cell + offset] = 1
            for offset in eight_neighbors:
                neighbor = cell + offset
                if flat[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)

    out = np.frombuffer(bytes(kept), dtype=np.uint8).reshape(padded_height, padded_width).astype(bool)
    return out[pad:pad + height, pad:pad + width]
