"""H33-6 cross-physics edge-normal consensus candidate.

This module implements the frozen 2026-10-04 H33-6 recipe recorded in
``knowledge/07_hypothesis_slate_20261004.md`` and
``evidence/hypothesis_slate_20261004_preregistered.json``. It is an experimental
candidate builder, not a competition-score model. The feature rasters are
owner-mirror inputs; the fixed H19-5 baseline is not regenerated here.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from scipy.ndimage import gaussian_filter, maximum_filter, distance_transform_edt

EDGE_LAYERS = ("tmi", "iso_grav_anom", "depth_to_base_surf", "cond_surf")
SCORE_Z_CLIP = 6.0
SUPPORT_Z_CAP = 3.0
DEFAULT_SIGMA_PX = 2.0
DEFAULT_REPLACEMENT_FRACTION = 0.05
DEFAULT_MIN_SPACING_PX = 2.8
DEFAULT_CATALOGUE_EXCLUSION_PX = 1.0


def _valid_values(array: np.ndarray, footprint: np.ndarray,
                  nodata: float | int | None = None) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(array, dtype=np.float32)
    if values.ndim != 2 or values.shape != footprint.shape:
        raise ValueError("each feature layer must be a 2-D array matching the footprint")
    valid = footprint & np.isfinite(values) & (values > np.float32(-1.0e30))
    if nodata is not None:
        try:
            if np.isfinite(nodata):
                valid &= values != np.float32(nodata)
        except TypeError:
            pass
    return values, valid


def _normalized_gaussian(values: np.ndarray, valid: np.ndarray, sigma_px: float) -> np.ndarray:
    """Smooth valid samples without treating nodata cells as physical zeros."""
    weights = gaussian_filter(valid.astype(np.float32), sigma=sigma_px, mode="nearest")
    numerator = gaussian_filter(np.where(valid, values, 0.0).astype(np.float32),
                                sigma=sigma_px, mode="nearest")
    smooth = np.zeros(values.shape, dtype=np.float32)
    np.divide(numerator, weights, out=smooth, where=weights > 1e-6)
    return smooth


def _positive_robust_z(values: np.ndarray, valid: np.ndarray) -> tuple[np.ndarray, dict]:
    """Median/MAD standardization of high values, clipped to the frozen range."""
    usable = valid & np.isfinite(values)
    sample = np.asarray(values[usable], dtype=np.float64)
    result = np.zeros(values.shape, dtype=np.float32)
    if sample.size == 0:
        return result, {"valid_cells": 0, "center": None, "scale": None, "dynamic": False}

    center = float(np.median(sample))
    mad = float(np.median(np.abs(sample - center)))
    scale = 1.4826 * mad
    scale_method = "1.4826*MAD"
    if not np.isfinite(scale) or scale <= 1e-12:
        q25, q75 = np.quantile(sample, [0.25, 0.75])
        scale = float((q75 - q25) / 1.349)
        scale_method = "IQR/1.349"
    if not np.isfinite(scale) or scale <= 1e-12:
        return result, {
            "valid_cells": int(sample.size), "center": center, "scale": 0.0,
            "scale_method": scale_method, "dynamic": False,
        }

    z = (values.astype(np.float64) - center) / scale
    z = np.clip(np.maximum(z, 0.0), 0.0, SCORE_Z_CLIP)
    result[usable] = z[usable].astype(np.float32)
    return result, {
        "valid_cells": int(sample.size), "center": center, "scale": float(scale),
        "scale_method": scale_method, "dynamic": True,
        "positive_cells": int(np.count_nonzero(result[usable] > 0)),
        "z_max": float(result[usable].max(initial=0.0)),
    }


def _edge_field(values: np.ndarray, valid: np.ndarray, sigma_px: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    smooth = _normalized_gaussian(values, valid, sigma_px)
    gy, gx = np.gradient(smooth)
    magnitude = np.hypot(gx, gy).astype(np.float32)
    transformed = np.log1p(magnitude)
    edge_z, scale_report = _positive_robust_z(transformed, valid)
    return gx.astype(np.float32), gy.astype(np.float32), edge_z, scale_report


def edge_consensus_score(layers: Mapping[str, np.ndarray], footprint: np.ndarray,
                         *, sigma_px: float = DEFAULT_SIGMA_PX,
                         nodata: Mapping[str, float | int | None] | None = None) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return frozen H33-6 edge score, 3x3 maxima and an audit report.

    The score is the geometric mean of robustly standardized log magnetic and
    gravity gradient magnitudes, multiplied by the absolute dot product of
    their edge-normal unit vectors and by a bounded independent edge-support
    factor from the stronger basement-depth/conductivity gradient.
    """
    if not np.isfinite(sigma_px) or sigma_px <= 0:
        raise ValueError("sigma_px must be positive and finite")
    footprint = np.asarray(footprint, dtype=bool)
    if footprint.ndim != 2:
        raise ValueError("footprint must be a 2-D mask")
    absent = [name for name in EDGE_LAYERS if name not in layers]
    if absent:
        raise ValueError(f"missing required feature layers: {', '.join(absent)}")
    nodata = nodata or {}

    arrays: dict[str, np.ndarray] = {}
    valid: dict[str, np.ndarray] = {}
    edges: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    layer_report: dict[str, dict] = {}
    for name in EDGE_LAYERS:
        arrays[name], valid[name] = _valid_values(layers[name], footprint, nodata.get(name))
        gx, gy, z, z_report = _edge_field(arrays[name], valid[name], sigma_px)
        edges[name] = (gx, gy, z)
        layer_report[name] = {
            "valid_cells": int(valid[name].sum()),
            "gradient_standardization": z_report,
        }

    gx_m, gy_m, z_m = edges["tmi"]
    gx_g, gy_g, z_g = edges["iso_grav_anom"]
    mag_m = np.hypot(gx_m, gy_m)
    mag_g = np.hypot(gx_g, gy_g)
    denominator = mag_m * mag_g
    alignment = np.zeros(footprint.shape, dtype=np.float32)
    aligned_cells = valid["tmi"] & valid["iso_grav_anom"] & (denominator > 1e-12)
    dot = np.zeros(footprint.shape, dtype=np.float32)
    np.divide(np.abs(gx_m * gx_g + gy_m * gy_g), denominator,
              out=dot, where=aligned_cells)
    alignment[aligned_cells] = np.clip(dot[aligned_cells], 0.0, 1.0)

    z_depth = edges["depth_to_base_surf"][2]
    z_cond = edges["cond_surf"][2]
    support_valid = valid["depth_to_base_surf"] | valid["cond_surf"]
    support = np.maximum(
        np.where(valid["depth_to_base_surf"], z_depth, 0.0),
        np.where(valid["cond_surf"], z_cond, 0.0),
    )
    support_factor = 0.5 + 0.5 * np.clip(support / SUPPORT_Z_CAP, 0.0, 1.0)

    score_valid = (valid["tmi"] & valid["iso_grav_anom"] & support_valid &
                   np.isfinite(alignment) & (denominator > 1e-12))
    score = np.zeros(footprint.shape, dtype=np.float32)
    paired = np.sqrt(np.maximum(z_m, 0.0) * np.maximum(z_g, 0.0))
    score[score_valid] = (paired[score_valid] * alignment[score_valid] *
                          support_factor[score_valid]).astype(np.float32)
    score[~footprint] = 0.0
    score[~np.isfinite(score)] = 0.0

    local_max = maximum_filter(score, size=3, mode="constant", cval=0.0)
    maxima = footprint & (score > 0.0) & (score >= local_max)
    values = score[score_valid]
    score_report = {
        "algorithm": "sqrt(z_log1p_tmi_gradient * z_log1p_gravity_gradient) * abs(unit_normal_dot) * (0.5 + 0.5*clip(max(z_depth,z_cond)/3,0,1))",
        "sigma_px": float(sigma_px),
        "z_clip": SCORE_Z_CLIP,
        "support_z_cap": SUPPORT_Z_CAP,
        "valid_score_cells": int(score_valid.sum()),
        "positive_score_cells": int(np.count_nonzero(score > 0)),
        "3x3_local_maxima": int(maxima.sum()),
        "score_min": float(values.min()) if values.size else 0.0,
        "score_median": float(np.median(values)) if values.size else 0.0,
        "score_p95": float(np.quantile(values, 0.95)) if values.size else 0.0,
        "score_max": float(values.max()) if values.size else 0.0,
        "layers": layer_report,
    }
    return score, maxima, score_report


def _disk_offsets(min_spacing_px: float) -> list[tuple[int, int]]:
    radius = int(np.ceil(min_spacing_px))
    return [
        (dy, dx)
        for dy in range(-radius, radius + 1)
        for dx in range(-radius, radius + 1)
        if dy * dy + dx * dx < min_spacing_px * min_spacing_px
    ]


def _greedy_add(shape: tuple[int, int], ordered_flat_indices: np.ndarray,
                count: int, min_spacing_px: float) -> np.ndarray:
    """Choose highest-priority points with deterministic Euclidean spacing."""
    height, width = shape
    offsets = _disk_offsets(min_spacing_px)
    blocked = np.zeros(shape, dtype=bool)
    chosen: list[int] = []
    for flat_index in np.asarray(ordered_flat_indices, dtype=np.int64):
        row, col = divmod(int(flat_index), width)
        if blocked[row, col]:
            continue
        chosen.append(int(flat_index))
        r0, r1 = max(0, row - int(np.ceil(min_spacing_px))), min(height, row + int(np.ceil(min_spacing_px)) + 1)
        c0, c1 = max(0, col - int(np.ceil(min_spacing_px))), min(width, col + int(np.ceil(min_spacing_px)) + 1)
        for dy, dx in offsets:
            rr, cc = row + dy, col + dx
            if 0 <= rr < height and 0 <= cc < width:
                blocked[rr, cc] = True
        if len(chosen) >= count:
            break
    if len(chosen) != count:
        raise RuntimeError(f"could place only {len(chosen)} of {count} requested additions")
    return np.asarray(chosen, dtype=np.int64)


def reallocate_edge_budget(control: np.ndarray, known: np.ndarray, footprint: np.ndarray,
                           score: np.ndarray, local_maxima: np.ndarray, *,
                           replacement_fraction: float = DEFAULT_REPLACEMENT_FRACTION,
                           min_spacing_px: float = DEFAULT_MIN_SPACING_PX,
                           catalogue_exclusion_px: float = DEFAULT_CATALOGUE_EXCLUSION_PX,
                           random_seed: int | None = None) -> tuple[np.ndarray, dict]:
    """Replace a frozen fraction of low-score baseline dots with edge or random dots.

    If ``random_seed`` is ``None``, additions are the highest-score eligible
    3x3 maxima. Otherwise, additions are a content-blind random sample from all
    eligible cells. Removal is identical in both modes so the random controls
    isolate the information in the added locations.
    """
    control = np.asarray(control) > 0
    known = np.asarray(known, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    score = np.asarray(score, dtype=np.float32)
    local_maxima = np.asarray(local_maxima, dtype=bool)
    shape = footprint.shape
    if any(array.shape != shape for array in (control, known, score, local_maxima)):
        raise ValueError("control, known, score and maxima must match the footprint shape")
    if not 0.0 <= replacement_fraction <= 1.0:
        raise ValueError("replacement_fraction must be in [0, 1]")
    if not np.isfinite(min_spacing_px) or min_spacing_px <= 0:
        raise ValueError("min_spacing_px must be positive and finite")
    if not np.isfinite(catalogue_exclusion_px) or catalogue_exclusion_px < 0:
        raise ValueError("catalogue_exclusion_px must be non-negative and finite")

    control &= footprint
    base_indices = np.flatnonzero(control)
    replace_count = int(np.floor(replacement_fraction * base_indices.size))
    remaining = control.copy()
    safe_score = np.where(np.isfinite(score), score, 0.0)
    # np.lexsort's final key is primary: score ascends, then row-major flat index.
    removal_order = np.lexsort((base_indices, safe_score.ravel()[base_indices]))
    removed_indices = base_indices[removal_order[:replace_count]]
    remaining.ravel()[removed_indices] = False

    if replace_count == 0:
        return remaining.astype(np.float32), {
            "control_dots": int(base_indices.size), "replacement_count": 0,
            "removed_dots": 0, "added_dots": 0,
            "candidate_pool_cells": 0, "random_seed": random_seed,
            "mode": "edge_consensus" if random_seed is None else "matched_random",
        }

    distance_from_remaining = distance_transform_edt(~remaining) if remaining.any() else np.full(shape, np.inf)
    distance_from_known = distance_transform_edt(~known) if known.any() else np.full(shape, np.inf)
    eligible = (footprint & ~known & ~remaining &
                (distance_from_known > catalogue_exclusion_px) &
                (distance_from_remaining >= min_spacing_px))

    if random_seed is None:
        candidate_mask = eligible & local_maxima & (safe_score > 0.0)
        candidate_indices = np.flatnonzero(candidate_mask)
        if candidate_indices.size:
            order = np.lexsort((candidate_indices, -safe_score.ravel()[candidate_indices]))
            candidate_indices = candidate_indices[order]
        chosen_indices = _greedy_add(shape, candidate_indices, replace_count, min_spacing_px)
        mode = "edge_consensus"
        pool_cells = int(candidate_mask.sum())
    else:
        eligible_indices = np.flatnonzero(eligible)
        if eligible_indices.size < replace_count:
            raise RuntimeError("not enough eligible cells for matched-random additions")
        rng = np.random.default_rng(int(random_seed))
        # Uniform sample without replacement; grow the sample deterministically
        # if spatial spacing leaves too few accepted points.
        sample_size = min(eligible_indices.size, max(100_000, replace_count * 100))
        chosen_indices = np.empty(0, dtype=np.int64)
        while True:
            sample = rng.choice(eligible_indices, size=sample_size, replace=False)
            try:
                chosen_indices = _greedy_add(shape, sample, replace_count, min_spacing_px)
                break
            except RuntimeError:
                if sample_size >= eligible_indices.size:
                    raise
                sample_size = min(eligible_indices.size, sample_size * 2)
        mode = "matched_random"
        pool_cells = int(eligible_indices.size)

    result = remaining.copy()
    result.ravel()[chosen_indices] = True
    report = {
        "mode": mode,
        "control_dots": int(base_indices.size),
        "replacement_count": int(replace_count),
        "removed_dots": int(removed_indices.size),
        "added_dots": int(chosen_indices.size),
        "candidate_pool_cells": int(pool_cells),
        "random_seed": random_seed,
        "remaining_control_dots": int(remaining.sum()),
        "candidate_dots": int(result.sum()),
        "removed_score_mean": float(np.mean(safe_score.ravel()[removed_indices])) if removed_indices.size else None,
        "added_score_mean": float(np.mean(safe_score.ravel()[chosen_indices])) if random_seed is None else None,
        "added_score_min": float(np.min(safe_score.ravel()[chosen_indices])) if random_seed is None else None,
        "added_score_max": float(np.max(safe_score.ravel()[chosen_indices])) if random_seed is None else None,
        "added_edge_maxima": int(np.count_nonzero(local_maxima.ravel()[chosen_indices])) if random_seed is None else None,
    }
    return result.astype(np.float32), report


def read_feature_layers(path, footprint: np.ndarray,
                        bands: Mapping[str, int] | None = None) -> tuple[dict[str, np.ndarray], dict, dict]:
    """Read the four frozen layers by index from a multiband GeoTIFF.

    Band indexes are explicit in the registry and also checked against the
    stored descriptions to prevent silent positional drift.
    """
    import rasterio

    expected = bands or {"tmi": 14, "iso_grav_anom": 13, "depth_to_base_surf": 15, "cond_surf": 17}
    expected_descriptions = {
        "tmi": "Total magnetic intensity",
        "iso_grav_anom": "Isostatic gravity anomaly -",
        "depth_to_base_surf": "Depth to basement surface",
        "cond_surf": "Conductivity surface",
    }
    arrays: dict[str, np.ndarray] = {}
    nodata: dict[str, float | int | None] = {}
    metadata: dict[str, dict] = {}
    with rasterio.open(path) as dataset:
        if dataset.shape != footprint.shape:
            raise ValueError("training feature grid does not match the template footprint")
        for name, index in expected.items():
            if not 1 <= int(index) <= dataset.count:
                raise ValueError(f"band {index} for {name} is outside the raster")
            description = dataset.descriptions[int(index) - 1] or ""
            if expected_descriptions[name].casefold() not in description.casefold():
                raise ValueError(f"band description mismatch for {name}: {description!r}")
            arrays[name] = dataset.read(int(index))
            nodata[name] = dataset.nodata
            metadata[name] = {"index": int(index), "description": description,
                              "dtype": dataset.dtypes[int(index) - 1], "nodata": dataset.nodata}
    return arrays, nodata, metadata
