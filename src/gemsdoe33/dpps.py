"""G33-DPPS: Dip-Projected Persistence Scarp operator (preregistered 2026-10-26).

Deterministic, label-free surface construction. No classifier is fitted and no
catalogue geometry is read here: the caller supplies cached geophysical /
geomorphic channels and the footprint only. Catalogue pixels enter downstream
solely as the (fold-visible) emission exclusion mask.

Frozen contract: ``evidence/dpps_preregistration_20261026.json``.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import map_coordinates
from scipy.stats import rankdata

from . import features
from .paths import CACHE_FEATURES

INPUT_CHANNELS: tuple[str, ...] = (
    "lid_step_max",
    "lid_lapneg_max",
    "lid_ex_max",
    "lid_valid",
    "det_elev_curv4",
    "det_elev_laps4",
    "det_elev_coh",
    "iso_grav_anom_hg",
    "depth_to_base_surf",
)

ORIENTATIONS: tuple[tuple[int, int], ...] = (
    (1, 0), (0, 1), (1, 1), (1, -1), (2, 1), (1, 2), (2, -1), (1, -2),
)
LINE_HALF_STEPS = 7
DIP_DEGREES = 60.0
DIP_CLIP_PX = 15.0
DEPTH_SMOOTH_SIGMA_PX = 3.0
PIXEL_M = 100.0


def load_input_arrays() -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    for name in INPUT_CHANNELS:
        path = CACHE_FEATURES / f"{name}.npy"
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing cached channel {path}; run scripts/prepare_data.py --skip-detector"
            )
        arrays[name] = np.load(path, mmap_mode="r")
    return arrays


def rank_field(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Empirical CDF rank in [0, 1] over finite footprint cells; 0 elsewhere."""
    a = np.asarray(arr, dtype=np.float32)
    fp = np.asarray(footprint, dtype=bool)
    out = np.zeros(a.shape, dtype=np.float32)
    mask = fp & np.isfinite(a)
    if not mask.any():
        return out
    vals = a[mask].astype(np.float64)
    ranks = rankdata(vals, method="average") / float(vals.size)
    out[mask] = ranks.astype(np.float32)
    return out


def scarp_strength(arrays: dict[str, np.ndarray], footprint: np.ndarray) -> np.ndarray:
    """Rank-blended LiDAR scarp strength with a DEM-flexure fallback in the LiDAR void."""
    fp = np.asarray(footprint, dtype=bool)
    lid_names = ("lid_step_max", "lid_lapneg_max", "lid_ex_max")
    scarp = np.zeros(fp.shape, dtype=np.float32)
    for name in lid_names:
        scarp += rank_field(arrays[name], fp)
    scarp /= float(len(lid_names))

    flex = np.zeros(fp.shape, dtype=np.float32)
    for name in ("det_elev_curv4", "det_elev_laps4"):
        flex += rank_field(np.abs(np.asarray(arrays[name], dtype=np.float32)), fp)
    flex /= 2.0

    lid_ok = fp & (np.asarray(arrays["lid_valid"], dtype=np.float32) > 0)
    for name in lid_names:
        lid_ok &= np.isfinite(np.asarray(arrays[name], dtype=np.float32))
    out = np.where(lid_ok, scarp, flex).astype(np.float32)
    out[~fp] = 0.0
    return out


def _orientation_offsets(oy: int, ox: int, half_steps: int = LINE_HALF_STEPS):
    norm = math.hypot(oy, ox)
    uy, ux = oy / norm, ox / norm
    seen: list[tuple[int, int]] = []
    for t in range(-half_steps, half_steps + 1):
        off = (int(round(t * uy)), int(round(t * ux)))
        if off not in seen:
            seen.append(off)
    return seen


def line_persistence(score: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Max over 8 orientations of the 1.5 km line-mean of ``score`` (edge-padded)."""
    s = np.asarray(score, dtype=np.float32)
    fp = np.asarray(footprint, dtype=bool)
    if s.shape != fp.shape:
        raise ValueError("score/footprint shape mismatch")
    pad = LINE_HALF_STEPS + 2
    padded = np.pad(s, pad, mode="edge")
    h, w = s.shape
    best: np.ndarray | None = None
    for oy, ox in ORIENTATIONS:
        offsets = _orientation_offsets(oy, ox)
        acc = np.zeros((h, w), dtype=np.float32)
        for dy, dx in offsets:
            acc += padded[pad + dy: pad + dy + h, pad + dx: pad + dx + w]
        acc /= float(len(offsets))
        best = acc if best is None else np.maximum(best, acc)
    assert best is not None
    best[~fp] = 0.0
    return best.astype(np.float32)


def dip_projected_gravity(
    arrays: dict[str, np.ndarray], footprint: np.ndarray
) -> np.ndarray:
    """Gravity HG rank field sampled updip-projected: G_proj(y,x) = G(y+d*uy, x+d*ux).

    ``d = clip(z * cot(dip) / 100 m, 0, 15) px`` with ``z`` the smoothed
    depth-to-basement and ``u`` the unit depth gradient (pointing basinward,
    toward increasing depth). A surface trace at ``(y, x)`` therefore receives
    support from the buried basement step basinward of it.
    """
    fp = np.asarray(footprint, dtype=bool)
    g_rank = rank_field(arrays["iso_grav_anom_hg"], fp)

    depth = np.asarray(arrays["depth_to_base_surf"], dtype=np.float32)
    depth = np.where(np.isfinite(depth), np.clip(depth, 0.0, None), np.nan).astype(np.float32)
    z = features._norm_conv(depth, DEPTH_SMOOTH_SIGMA_PX, fp)
    z = np.where(np.isfinite(z), np.clip(z, 0.0, None), 0.0).astype(np.float32)

    gy = np.zeros_like(z)
    gx = np.zeros_like(z)
    gy[1:-1, :] = (z[2:, :] - z[:-2, :]) / 2.0
    gx[:, 1:-1] = (z[:, 2:] - z[:, :-2]) / 2.0
    norm = np.hypot(gy, gx) + 1e-12
    cot = 1.0 / math.tan(math.radians(DIP_DEGREES))
    d_px = np.clip(z * cot / PIXEL_M, 0.0, DIP_CLIP_PX).astype(np.float32)

    h, w = fp.shape
    out = np.zeros((h, w), dtype=np.float32)
    rows_per_chunk = 400
    yy_base, xx_base = np.mgrid[0:h, 0:w]
    for r0 in range(0, h, rows_per_chunk):
        r1 = min(h, r0 + rows_per_chunk)
        ys = (yy_base[r0:r1] + d_px[r0:r1] * (gy[r0:r1] / norm[r0:r1])).astype(np.float32)
        xs = (xx_base[r0:r1] + d_px[r0:r1] * (gx[r0:r1] / norm[r0:r1])).astype(np.float32)
        out[r0:r1] = map_coordinates(
            g_rank, [ys, xs], order=1, mode="nearest"
        ).astype(np.float32)
        del ys, xs
    out[~fp] = 0.0
    return out


def build_surfaces(
    arrays: dict[str, np.ndarray], footprint: np.ndarray
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return ``(dpps_surface, ctrl_pixel_surface, report)``; all finite, in [0, 1]."""
    fp = np.asarray(footprint, dtype=bool)
    s = scarp_strength(arrays, fp)
    persistence = line_persistence(s, fp)
    g_proj = dip_projected_gravity(arrays, fp)

    l_rank = rank_field(persistence, fp)
    g_rank = rank_field(g_proj, fp)
    coh_rank = rank_field(arrays["det_elev_coh"], fp)

    surface = (l_rank * (0.6 + 0.4 * g_rank) * (0.7 + 0.3 * coh_rank)).astype(np.float32)
    surface = np.clip(surface, 0.0, 1.0)
    surface[~fp] = 0.0
    if not np.isfinite(surface).all():
        raise ValueError("DPPS surface must be finite everywhere")

    ctrl = np.clip(s, 0.0, 1.0)
    ctrl[~fp] = 0.0
    if not np.isfinite(ctrl).all():
        raise ValueError("CTRL-PIXEL surface must be finite everywhere")

    lid_ok_frac = float(
        (fp & (np.asarray(arrays["lid_valid"], dtype=np.float32) > 0)).sum()
    ) / float(fp.sum())
    report = {
        "operator": "G33-DPPS frozen 2026-10-26",
        "input_channels": list(INPUT_CHANNELS),
        "orientations": [list(o) for o in ORIENTATIONS],
        "line_half_steps": LINE_HALF_STEPS,
        "dip_degrees": DIP_DEGREES,
        "dip_clip_px": DIP_CLIP_PX,
        "lidar_valid_fraction_of_footprint": lid_ok_frac,
        "surface_min": float(surface.min()),
        "surface_max": float(surface.max()),
        "surface_positive_cells": int((surface > 0).sum()),
        "catalogue_read_in_surface": False,
        "learned_weights": False,
    }
    return surface, ctrl.astype(np.float32), report
