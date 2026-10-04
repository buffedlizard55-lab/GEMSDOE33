"""Feature construction for GEMSDOE33.

This module creates a research feature cache from the owner-mirror rasters. Transform channels are
currently generated for a selected set of fields treated as raw; derivative-labelled source bands
are retained without a second derivative transform. This is a feature-design constraint, not a
claim of measured superiority: no candidate built from these channels has passed an independent
spatially blocked validation against private/new faults.

Gaussian smoothing uses a normalised valid-data mask. The owner-mirror training raster has 3,061
in-footprint template cells with nodata sentinels in 18 bands, plus 12 further cells in band 6;
see ``IR-33-NODATA-01``. These owner-mirror measurements do not authenticate organizer data.
"""

from __future__ import annotations

import json
import numpy as np
from scipy.ndimage import (gaussian_filter, maximum_filter, minimum_filter,
                           uniform_filter, distance_transform_edt)

from . import grid
from .paths import CACHE, CACHE_FEATURES

RAW_FIELDS = ("det_elev", "depth_to_base_surf", "iso_grav_anom", "rtp", "mag_anom",
              "cond_surf", "ieq_n100a15", "tmi")
DERIVED_PRODUCTS = ("tmi_hg", "tmi_vg", "tc", "iso_grav_anom_hg", "iso_grav_anom_vg",
                    "iso_grav_anom_slope", "det_elev_slope")
KINEMATIC = ("geod_2ndinv", "geod_shearrate", "geod_dilaterate")
EXPECTED_CHANNEL_COUNT = 121  # 19 official + 20 external + 80 raw-field transforms + 2 up-continued TMI


# --------------------------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------------------------
def _as_float(arr) -> np.ndarray:
    return np.asarray(arr, dtype=np.float32)


def _fill_nan(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Nearest-valid fill inside the footprint so filters never propagate NaN."""
    out = arr.copy()
    bad = ~np.isfinite(out)
    if not bad.any():
        return out
    idx = distance_transform_edt(bad, return_distances=False, return_indices=True)
    out[bad] = arr[tuple(idx[:, bad])]
    out[~np.isfinite(out)] = 0.0
    return out


def _norm_conv(arr: np.ndarray, sigma: float, footprint: np.ndarray) -> np.ndarray:
    """Gaussian smoothing with normalised convolution over the valid mask."""
    valid = np.isfinite(arr).astype(np.float32)
    filled = np.where(np.isfinite(arr), arr, 0.0)
    num = gaussian_filter(filled, sigma, mode="nearest")
    den = gaussian_filter(valid, sigma, mode="nearest")
    with np.errstate(invalid="ignore", divide="ignore"):
        out = num / np.maximum(den, 1e-6)
    return np.where(footprint, out, np.nan).astype(np.float32)


def _grad(arr: np.ndarray, sigma: float, footprint: np.ndarray):
    """(dy, dx) Gaussian gradient with normalised convolution."""
    s = _norm_conv(arr, sigma, footprint)
    gy = np.zeros_like(s)
    gx = np.zeros_like(s)
    gy[1:-1, :] = (s[2:, :] - s[:-2, :]) / 2.0
    gx[:, 1:-1] = (s[:, 2:] - s[:, :-2]) / 2.0
    return gy, gx


def grad_mag(arr, sigma, footprint) -> np.ndarray:
    gy, gx = _grad(arr, sigma, footprint)
    return np.hypot(gy, gx).astype(np.float32)


def laplacian(arr, sigma, footprint) -> np.ndarray:
    s = _norm_conv(arr, sigma, footprint)
    lap = np.zeros_like(s)
    lap[1:-1, :] += s[2:, :] - 2 * s[1:-1, :] + s[:-2, :]
    lap[:, 1:-1] += s[:, 2:] - 2 * s[:, 1:-1] + s[:, :-2]
    return lap.astype(np.float32)


def curvature_along_gradient(arr, sigma, footprint) -> np.ndarray:
    """Second directional derivative along the gradient direction (profile curvature).

    Positive/negative values describe curvature in the local gradient direction. This is an
    exploratory transform only; no improvement for fault discovery is claimed from its presence.
    """
    gy, gx = _grad(arr, sigma, footprint)
    n = np.hypot(gy, gx) + 1e-9
    uy, ux = gy / n, gx / n
    h = _norm_conv(arr, sigma, footprint)
    hyy = np.zeros_like(h)
    hxx = np.zeros_like(h)
    hxy = np.zeros_like(h)
    hyy[1:-1, :] = h[2:, :] - 2 * h[1:-1, :] + h[:-2, :]
    hxx[:, 1:-1] = h[:, 2:] - 2 * h[:, 1:-1] + h[:, :-2]
    hxy[1:-1, 1:-1] = (h[2:, 2:] - h[2:, :-2] - h[:-2, 2:] + h[:-2, :-2]) / 4.0
    return (uy * uy * hyy + 2 * uy * ux * hxy + ux * ux * hxx).astype(np.float32)


def nms_ridge(field: np.ndarray, width: int = 1) -> np.ndarray:
    """Thin a positive field to its 1-px crest: local max along the gradient direction."""
    f = np.nan_to_num(field, nan=0.0, posinf=0.0, neginf=0.0)
    gy = np.zeros_like(f)
    gx = np.zeros_like(f)
    gy[1:-1, :] = (f[2:, :] - f[:-2, :]) / 2.0
    gx[:, 1:-1] = (f[:, 2:] - f[:, :-2]) / 2.0
    n = np.hypot(gy, gx) + 1e-12
    uy, ux = gy / n, gx / n
    H, W = field.shape
    yy, xx = np.mgrid[0:H, 0:W]
    # sample field one step either side along the gradient direction
    py = np.clip(np.rint(yy + uy).astype(int), 0, H - 1)
    px = np.clip(np.rint(xx + ux).astype(int), 0, W - 1)
    ny = np.clip(np.rint(yy - uy).astype(int), 0, H - 1)
    nx = np.clip(np.rint(xx - ux).astype(int), 0, W - 1)
    a = f[py, xx]
    b = f[yy, px]
    c = f[ny, xx]
    d = f[yy, nx]
    return ((f >= a) & (f >= b) & (f >= c) & (f >= d)).astype(np.float32)


def structure_coherence(field: np.ndarray, sigma: float, footprint: np.ndarray) -> np.ndarray:
    """Anisotropic coherence of the local structure tensor — 1 on a straight lineament, 0 isotropic."""
    gy, gx = _grad(field, sigma, footprint)
    jxx = _norm_conv(gy * gy, sigma * 2, footprint)
    jyy = _norm_conv(gx * gx, sigma * 2, footprint)
    jxy = _norm_conv(gy * gx, sigma * 2, footprint)
    tr = jxx + jyy + 1e-12
    det = jxx * jyy - jxy * jxy
    l1 = tr / 2 + np.sqrt(np.maximum(tr * tr / 4 - det, 0))
    l2 = tr / 2 - np.sqrt(np.maximum(tr * tr / 4 - det, 0))
    return ((l1 - l2) / (l1 + l2 + 1e-12)).astype(np.float32)


def robust_standardise(arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Median/MAD standardisation over a mask — heavy-tailed geophysical fields break z-scores."""
    a = np.asarray(arr, dtype=np.float32)
    vals = a[mask & np.isfinite(a)]
    med = np.median(vals)
    mad = np.median(np.abs(vals - med)) + 1e-9
    out = (a - med) / (1.4826 * mad)
    return np.clip(out, -8, 8).astype(np.float32)


# --------------------------------------------------------------------------------------------
# external layers
# --------------------------------------------------------------------------------------------
def load_external() -> dict:
    """External hash-pinned rasters on the template grid.

    ``geodawn_rad_u8``     K, Th, U, TC        — GeoDAWN airborne radiometrics (4 ch, uint8)
    ``geodawn_extensions`` ThK, UK, UTh, TMI_up150 — owner-mirror, rank/uint8 extension layers.
                           The first three are kept as supplied ordinal channels, not recomputed
                           physical ratios; the 150 m upward-continued TMI is also rank encoded.
    ``lidar_scarp``        ex_max, ex_mean, step_max, lapneg_max, lappos_max, downface_max,
                           upface_max, cross_max, relief, coh100, strike, valid (12 ch, uint8)
    """
    out = {}
    rad, _ = grid.read_raster("geodawn_rad_u8.tif", band=None)
    for i, k in enumerate(("K", "Th", "U", "TC")):
        out[f"rad_{k}"] = rad[i].astype(np.float32)
    ext, _ = grid.read_raster("geodawn_extensions_u8.tif", band=None)
    for i, k in enumerate(("ThK", "UK", "UTh", "TMI_up150")):
        out[f"ext_{k}"] = ext[i].astype(np.float32)
    lid, _ = grid.read_raster("lidar_scarp_features_u8.tif", band=None)
    for i, k in enumerate(("ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max",
                           "downface_max", "upface_max", "cross_max", "relief", "coh100",
                           "strike", "valid")):
        out[f"lid_{k}"] = lid[i].astype(np.float32)
    return out


# --------------------------------------------------------------------------------------------
# channel builder
# --------------------------------------------------------------------------------------------
def build_channels(report: bool = True) -> tuple[list[str], dict]:
    """Build every channel on the full (3730, 3292) grid and cache them as float32 .npy.

    Memory discipline: each channel is written to ``.cache/features`` and dropped from RAM
    immediately.  A 70-channel stack would otherwise need ~3.4 GB; the sandbox has 3 GB.
    """
    footprint = grid.template_footprint()
    names: list[str] = []

    def emit(name: str, arr: np.ndarray, keep: dict | None = None):
        np.save(CACHE_FEATURES / f"{name}.npy", np.asarray(arr, dtype=np.float32))
        names.append(name)
        if keep is not None:
            keep[name] = np.asarray(arr, dtype=np.float32)
        if report:
            print(f"  ch {len(names):3d} {name}", flush=True)
        return arr

    raw: dict[str, np.ndarray] = {}

    # 1. the 19 official bands, sanitised and NaN-filled inside the footprint
    for _idx, key, _desc in grid.BANDS:
        arr = np.load(grid.band_path(key))
        arr = np.where(np.isfinite(arr), arr, np.nan).astype(np.float32)
        emit(key, _fill_nan(arr, footprint), raw if key in RAW_FIELDS else None)

    # 2. external layers
    for key, arr in load_external().items():
        a = np.where(arr > 0, arr, np.nan).astype(np.float32)
        emit(key, _fill_nan(a, footprint), raw if key in RAW_FIELDS else None)

    # 3. multi-scale derivatives on raw fields only
    for key in RAW_FIELDS:
        base = raw.pop(key)
        for sigma in (1.0, 2.0, 4.0):
            tag = f"s{int(sigma)}"
            emit(f"{key}_gm{tag}", grad_mag(base, sigma, footprint))
            emit(f"{key}_lap{tag}", laplacian(base, sigma, footprint))
        for sigma in (2.0, 4.0):
            emit(f"{key}_curv{int(sigma)}", curvature_along_gradient(base, sigma, footprint))
        gm2 = grad_mag(base, 2.0, footprint)
        emit(f"{key}_ridge", nms_ridge(gm2))
        emit(f"{key}_coh", structure_coherence(base, 2.0, footprint))
        del gm2, base

    # IMPORTANT: Do NOT compute physical ratios (K/Th, U/K, K*U/Th, etc.) from the
    # owner-mirror uint8 radiometric channels. Their per-band quantisation/offset metadata is not
    # present in this checkout, so arithmetic on the encoded values is not a physical ratio. The
    # precomputed ``ext_ThK``, ``ext_UK`` and ``ext_UTh`` extension bands are kept as separate
    # ordinal channels, but no new geochemistry transform is made here. See IR-33-RAD-01.

    # 4. deep magnetic contact channel: 150 m upward continuation suppresses shallow noise
    up = np.load(CACHE_FEATURES / "ext_TMI_up150.npy")
    g = grad_mag(up, 2.0, footprint)
    emit("ext_TMI_up150_gm2", g)
    emit("ext_TMI_up150_ridge", nms_ridge(g))
    del up, g

    (CACHE / "channel_names.json").write_text(json.dumps(names, indent=1))
    # Remove channels from older schemas. They must not remain discoverable after the 121-channel
    # revision, even though channel_names.json is authoritative for current consumers.
    keep = set(names)
    for stale in CACHE_FEATURES.glob("*.npy"):
        if stale.stem not in keep:
            stale.unlink()
    if report:
        print(f"built {len(names)} channels; removed stale channel files")
    return names, {"n_channels": len(names), "footprint_cells": int(footprint.sum())}


def load_channel(name: str) -> np.ndarray:
    p = CACHE_FEATURES / f"{name}.npy"
    if not p.exists():
        build_channels(report=False)
    return np.load(p, mmap_mode="r")


def channel_names() -> list[str]:
    p = CACHE / "channel_names.json"
    if not p.exists():
        build_channels(report=False)
    return json.loads(p.read_text())


def stack_matrix(names: list[str], mask: np.ndarray | None = None) -> np.ndarray:
    """Materialise a (n_cells, n_channels) float32 matrix over ``mask`` (default: footprint)."""
    foot = grid.template_footprint() if mask is None else mask
    n = int(foot.sum())
    out = np.empty((n, len(names)), dtype=np.float32)
    for j, name in enumerate(names):
        arr = np.load(CACHE_FEATURES / f"{name}.npy", mmap_mode="r")
        v = np.asarray(arr)[foot]
        v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)
        out[:, j] = v
    return out


def standardised_stack(names: list[str], mask: np.ndarray | None = None) -> np.ndarray:
    foot = grid.template_footprint() if mask is None else mask
    X = stack_matrix(names, foot)
    for j in range(X.shape[1]):
        v = X[:, j]
        med = np.median(v)
        mad = np.median(np.abs(v - med)) + 1e-9
        X[:, j] = np.clip((v - med) / (1.4826 * mad), -8, 8)
    return X
