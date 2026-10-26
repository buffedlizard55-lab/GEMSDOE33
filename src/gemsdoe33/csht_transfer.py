"""A33-R2-CSHT: Cover-Stratified Multi-Physics & Hydrothermal-Conduit Analog Transfer
with 300 m Submodular Crest Allocation.

All feature transforms are strictly label-free. Every classifier fit, negative
clearance mask, and visible-catalogue exclusion mask consumes ONLY the caller's
fold-visible catalogue and spatially purged training mask.

Forbidden external CSV columns (e.g. ``dist_known_fault_px``) are never read.
"""
from __future__ import annotations

import csv
import hashlib
import heapq
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation, convolve, distance_transform_edt
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier

from vendor.gems24_template.holdout import (
    MTR_EVALUATOR_VERSION,
    make_quadrant_folds,
    ndi_label,
    pooled_bootstrap,
    pooled_components,
    spatial_bootstrap_ci,
    spatial_components,
)

from . import features, grid, novelty
from .paths import CACHE, CACHE_FEATURES

CACHED_FEATURE_NAMES: tuple[str, ...] = (
    "lid_valid",
    "lid_ex_max",
    "lid_step_max",
    "lid_lapneg_max",
    "lid_coh100",
    "lid_relief",
    "det_elev_slope",
    "det_elev_curv2",
    "det_elev_curv4",
    "det_elev_coh",
    "tmi_hg",
    "tmi_vg",
    "tc",
    "rtp_gms2",
    "rtp_coh",
    "ext_TMI_up150_gm2",
    "iso_grav_anom_hg",
    "iso_grav_anom_vg",
    "iso_grav_anom_slope",
    "iso_grav_anom_gms4",
    "depth_to_base_surf",
    "depth_to_base_surf_gms2",
    "cond_surf",
    "cond_surf_gms2",
    "cond_surf_laps2",
    "ext_ThK",
    "ext_UK",
    "geod_2ndinv",
    "geod_shearrate",
    "geod_dilaterate",
    "ieq_n100a15",
    "deq_n100a15",
)

DERIVED_HYDRO_NAMES: tuple[str, ...] = (
    "hydro_demag_contrast",
    "hydro_upflow_potential",
)

ALL_FEATURE_NAMES: tuple[str, ...] = CACHED_FEATURE_NAMES + DERIVED_HYDRO_NAMES

CONCEALED_FEATURE_NAMES: tuple[str, ...] = (
    "tmi_hg",
    "tmi_vg",
    "tc",
    "rtp_gms2",
    "rtp_coh",
    "ext_TMI_up150_gm2",
    "iso_grav_anom_hg",
    "iso_grav_anom_vg",
    "iso_grav_anom_slope",
    "iso_grav_anom_gms4",
    "depth_to_base_surf",
    "depth_to_base_surf_gms2",
    "cond_surf",
    "cond_surf_gms2",
    "cond_surf_laps2",
    "ext_ThK",
    "ext_UK",
    "geod_2ndinv",
    "geod_shearrate",
    "geod_dilaterate",
    "ieq_n100a15",
    "deq_n100a15",
    "hydro_demag_contrast",
    "hydro_upflow_potential",
)

HYDRO_ANALOG_BASE_NAMES: tuple[str, ...] = (
    "tmi_hg",
    "tc",
    "rtp_gms2",
    "ext_TMI_up150_gm2",
    "iso_grav_anom_hg",
    "iso_grav_anom_slope",
    "depth_to_base_surf_gms2",
    "cond_surf_gms2",
    "cond_surf_laps2",
    "ext_ThK",
    "ext_UK",
    "geod_2ndinv",
    "geod_shearrate",
    "geod_dilaterate",
    "hydro_demag_contrast",
    "det_elev_curv4",
)

FORBIDDEN_CSV_COLUMNS = frozenset({"dist_known_fault_px"})
ALLOWED_WELLSPRING_COLUMNS = ("row", "col", "temp_c", "geothermquartz_c", "thermalclass")
ALLOWED_VENT_COLUMNS = ("row", "col")

HYDRO_CACHE = CACHE / "hydro_features_a33_r2"
QUANTILE_KNOTS = 257


@dataclass
class CSHTBundle:
    full_model: HistGradientBoostingClassifier
    concealed_model: HistGradientBoostingClassifier
    hydro_model: HistGradientBoostingClassifier
    report: dict


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_array(arr: np.ndarray) -> str:
    contig = np.ascontiguousarray(arr)
    h = hashlib.sha256()
    h.update(str(contig.dtype).encode("ascii"))
    h.update(str(contig.shape).encode("ascii"))
    h.update(contig.tobytes())
    return h.hexdigest()


def load_thermal_vent_seeds(
    footprint: np.ndarray,
    *,
    wellspring_csv: Path | None = None,
    vents_csv: Path | None = None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Build label-free INGENIOUS hot-spring/geothermometer and volcanic-vent seed masks.

    Explicitly ignores ``dist_known_fault_px`` in both CSVs so zero catalogue
    geometry can ever leak into hydrothermal domain construction.
    """
    fp = np.asarray(footprint, dtype=bool)
    h, w = fp.shape
    thermal_seed = np.zeros((h, w), dtype=bool)
    vent_seed = np.zeros((h, w), dtype=bool)

    ws_path = wellspring_csv or (grid.DATA / "gdr_wellspring_in_footprint.csv")
    vt_path = vents_csv or (grid.DATA / "gdr_volcanic_vents_in_footprint.csv")

    n_ws_rows = 0
    with ws_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            n_ws_rows += 1
            # Read ONLY allowed catalogue-free columns; never access dist_known_fault_px.
            try:
                rr = int(row["row"])
                cc = int(row["col"])
            except (KeyError, TypeError, ValueError):
                continue
            if not (0 <= rr < h and 0 <= cc < w and fp[rr, cc]):
                continue
            raw_t = (row.get("temp_c") or "").strip()
            raw_q = (row.get("geothermquartz_c") or "").strip()
            tclass = (row.get("thermalclass") or "").strip().lower()
            temp_c = -999.0
            quartz_c = -999.0
            if raw_t and raw_t.upper() not in ("NULL", "NAN"):
                try:
                    temp_c = float(raw_t)
                except ValueError:
                    temp_c = -999.0
            if raw_q and raw_q.upper() not in ("NULL", "NAN"):
                try:
                    quartz_c = float(raw_q)
                except ValueError:
                    quartz_c = -999.0
            if (np.isfinite(temp_c) and temp_c >= 37.0) or (
                np.isfinite(quartz_c) and quartz_c >= 100.0
            ) or tclass == "hot":
                thermal_seed[rr, cc] = True

    n_vt_rows = 0
    with vt_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            n_vt_rows += 1
            try:
                rr = int(row["row"])
                cc = int(row["col"])
            except (KeyError, TypeError, ValueError):
                continue
            if 0 <= rr < h and 0 <= cc < w and fp[rr, cc]:
                vent_seed[rr, cc] = True

    meta = {
        "wellspring_rows_scanned": n_ws_rows,
        "volcanic_vent_rows_scanned": n_vt_rows,
        "unique_thermal_seed_cells": int(thermal_seed.sum()),
        "unique_vent_seed_cells": int(vent_seed.sum()),
        "union_seed_cells": int((thermal_seed | vent_seed).sum()),
        "forbidden_columns_excluded": sorted(FORBIDDEN_CSV_COLUMNS),
        "allowed_wellspring_columns": list(ALLOWED_WELLSPRING_COLUMNS),
        "allowed_vent_columns": list(ALLOWED_VENT_COLUMNS),
    }
    return thermal_seed, vent_seed, meta


def build_or_load_csht_features(
    footprint: np.ndarray,
    *,
    force: bool = False,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], np.ndarray, dict]:
    """Load the 34 base channels + 16 3-km high-pass hydrothermal contrast channels."""
    fp = np.asarray(footprint, dtype=bool)
    HYDRO_CACHE.mkdir(parents=True, exist_ok=True)

    demag_path = HYDRO_CACHE / "hydro_demag_contrast.npy"
    upflow_path = HYDRO_CACHE / "hydro_upflow_potential.npy"
    dist_path = HYDRO_CACHE / "hydro_seed_distance_px.npy"
    meta_path = HYDRO_CACHE / "hydro_meta.json"

    thermal_seed, vent_seed, seed_meta = load_thermal_vent_seeds(fp)

    if force or not (demag_path.is_file() and upflow_path.is_file() and dist_path.is_file()):
        rtp = np.asarray(np.load(CACHE_FEATURES / "rtp.npy", mmap_mode="r"), dtype=np.float32)
        up150 = np.asarray(
            np.load(CACHE_FEATURES / "ext_TMI_up150.npy", mmap_mode="r"), dtype=np.float32
        )
        rtp_z = features.robust_standardise(rtp, fp)
        up_z = features.robust_standardise(up150, fp)
        raw_diff = (up_z - rtp_z).astype(np.float32)
        smooth_diff = features._norm_conv(raw_diff, 30.0, fp)
        demag = np.where(fp, raw_diff - smooth_diff, np.nan).astype(np.float32)
        np.save(demag_path, demag)

        d_th = distance_transform_edt(~thermal_seed) if thermal_seed.any() else np.full(fp.shape, 1e6)
        d_vt = distance_transform_edt(~vent_seed) if vent_seed.any() else np.full(fp.shape, 1e6)
        pot_th = np.exp(-(d_th * d_th) / (2.0 * 25.0 * 25.0))
        pot_vt = 0.7 * np.exp(-(d_vt * d_vt) / (2.0 * 30.0 * 30.0))
        upflow = np.where(fp, np.maximum(pot_th, pot_vt), np.nan).astype(np.float32)
        np.save(upflow_path, upflow)

        union_seed = thermal_seed | vent_seed
        d_union = (
            distance_transform_edt(~union_seed).astype(np.float32)
            if union_seed.any()
            else np.full(fp.shape, 1e6, dtype=np.float32)
        )
        np.save(dist_path, d_union)

    base_arrays: dict[str, np.ndarray] = {}
    for name in CACHED_FEATURE_NAMES:
        p = CACHE_FEATURES / f"{name}.npy"
        if not p.is_file():
            raise FileNotFoundError(f"Missing cached channel {p}")
        arr = np.load(p, mmap_mode="r")
        if arr.shape != fp.shape:
            raise ValueError(f"Grid mismatch for {name}: {arr.shape} != {fp.shape}")
        base_arrays[name] = arr
    base_arrays["hydro_demag_contrast"] = np.load(demag_path, mmap_mode="r")
    base_arrays["hydro_upflow_potential"] = np.load(upflow_path, mmap_mode="r")
    hydro_dist = np.load(dist_path, mmap_mode="r")

    contrast_arrays: dict[str, np.ndarray] = {}
    for name in HYDRO_ANALOG_BASE_NAMES:
        cpath = HYDRO_CACHE / f"contrast30_{name}.npy"
        if force or not cpath.is_file():
            src = np.asarray(base_arrays[name], dtype=np.float32)
            bg = features._norm_conv(src, 30.0, fp)
            hp = np.where(fp, src - bg, np.nan).astype(np.float32)
            np.save(cpath, hp)
        contrast_arrays[f"contrast30_{name}"] = np.load(cpath, mmap_mode="r")

    return base_arrays, contrast_arrays, hydro_dist, seed_meta


def _extract_matrix(
    arrays: dict[str, np.ndarray],
    names: tuple[str, ...],
    flat_ids: np.ndarray,
) -> np.ndarray:
    ids = np.asarray(flat_ids, dtype=np.int64)
    out = np.empty((ids.size, len(names)), dtype=np.float32)
    for j, name in enumerate(names):
        vals = np.asarray(arrays[name]).ravel()[ids].astype(np.float32, copy=True)
        # Preserve true NaN (e.g. 1 m LiDAR gap where lid_valid == 0) so HistGradientBoosting
        # routes missingness natively; sanitise only +/-inf to NaN.
        vals[np.isinf(vals)] = np.nan
        if not name.startswith("lid_"):
            vals = np.nan_to_num(vals, nan=0.0)
        out[:, j] = vals
    return out


def _sample_ids(mask: np.ndarray, cap: int, rng: np.random.Generator) -> np.ndarray:
    ids = np.flatnonzero(mask)
    if ids.size > cap:
        ids = np.sort(rng.choice(ids, size=cap, replace=False))
    return ids


def fit_csht_models(
    base_arrays: dict[str, np.ndarray],
    contrast_arrays: dict[str, np.ndarray],
    hydro_dist: np.ndarray,
    train: np.ndarray,
    visible: np.ndarray,
    distance_to_visible: np.ndarray,
    *,
    seed: int,
) -> CSHTBundle:
    """Fit the three fold-safe cover- & hydrothermal-stratified experts."""
    rng_a = np.random.default_rng(seed + 101)
    rng_b = np.random.default_rng(seed + 202)
    rng_c = np.random.default_rng(seed + 303)

    # Head A: Full 34-channel regional multi-physics expert (NaN-preserving in LiDAR void)
    pos_a_mask = train & visible
    neg_a_mask = train & ~visible & (distance_to_visible > 5.0)
    pos_a = _sample_ids(pos_a_mask, 45_000, rng_a)
    neg_a = _sample_ids(neg_a_mask, min(2 * pos_a.size, int(neg_a_mask.sum())), rng_a)
    if pos_a.size < 100 or neg_a.size < 100:
        raise RuntimeError(f"Insufficient Head A samples: pos={pos_a.size}, neg={neg_a.size}")
    ids_a = np.concatenate([pos_a, neg_a])
    y_a = np.concatenate([np.ones(pos_a.size, np.uint8), np.zeros(neg_a.size, np.uint8)])
    w_a = np.concatenate(
        [np.ones(pos_a.size, np.float32), np.full(neg_a.size, pos_a.size / neg_a.size, np.float32)]
    )
    model_a = HistGradientBoostingClassifier(
        max_iter=180,
        learning_rate=0.06,
        max_leaf_nodes=63,
        min_samples_leaf=50,
        l2_regularization=2.0,
        early_stopping=False,
        random_state=seed + 101,
    )
    model_a.fit(_extract_matrix(base_arrays, ALL_FEATURE_NAMES, ids_a), y_a, sample_weight=w_a)

    # Head B: Concealed-basin subsurface/kinematic/alteration transfer expert (zero LiDAR/scarp)
    pos_b = _sample_ids(pos_a_mask, 45_000, rng_b)
    neg_b = _sample_ids(neg_a_mask, min(2 * pos_b.size, int(neg_a_mask.sum())), rng_b)
    ids_b = np.concatenate([pos_b, neg_b])
    y_b = np.concatenate([np.ones(pos_b.size, np.uint8), np.zeros(neg_b.size, np.uint8)])
    depth_base = np.asarray(base_arrays["depth_to_base_surf"]).ravel()
    train_depth = depth_base[np.flatnonzero(train)]
    med_depth = float(np.nanmedian(train_depth))
    is_basin = np.nan_to_num(depth_base[ids_b], nan=0.0) > med_depth
    class_w_b = np.concatenate(
        [np.ones(pos_b.size, np.float32), np.full(neg_b.size, pos_b.size / neg_b.size, np.float32)]
    )
    w_b = class_w_b * np.where(is_basin, 2.0, 1.0).astype(np.float32)
    model_b = HistGradientBoostingClassifier(
        max_iter=160,
        learning_rate=0.06,
        max_leaf_nodes=47,
        min_samples_leaf=60,
        l2_regularization=3.0,
        early_stopping=False,
        random_state=seed + 202,
    )
    model_b.fit(_extract_matrix(base_arrays, CONCEALED_FEATURE_NAMES, ids_b), y_b, sample_weight=w_b)

    # Head C: INGENIOUS multi-field hydrothermal-conduit expert on 3 km local contrasts
    hydro_domain = train & (np.asarray(hydro_dist) <= 50.0)
    pos_c_mask = hydro_domain & visible
    # Splay-safe distal clearance (>800 m) inside geothermal fields
    neg_c_mask = hydro_domain & ~visible & (distance_to_visible > 8.0)
    pos_c = _sample_ids(pos_c_mask, 20_000, rng_c)
    neg_c = _sample_ids(neg_c_mask, min(2 * pos_c.size, int(neg_c_mask.sum())), rng_c)
    if pos_c.size < 80 or neg_c.size < 80:
        raise RuntimeError(f"Insufficient Head C hydrothermal samples: pos={pos_c.size}, neg={neg_c.size}")
    ids_c = np.concatenate([pos_c, neg_c])
    y_c = np.concatenate([np.ones(pos_c.size, np.uint8), np.zeros(neg_c.size, np.uint8)])
    w_c = np.concatenate(
        [np.ones(pos_c.size, np.float32), np.full(neg_c.size, pos_c.size / neg_c.size, np.float32)]
    )
    contrast_names = tuple(f"contrast30_{k}" for k in HYDRO_ANALOG_BASE_NAMES)
    model_c = HistGradientBoostingClassifier(
        max_iter=120,
        learning_rate=0.05,
        max_leaf_nodes=31,
        min_samples_leaf=80,
        l2_regularization=4.0,
        early_stopping=False,
        random_state=seed + 303,
    )
    model_c.fit(_extract_matrix(contrast_arrays, contrast_names, ids_c), y_c, sample_weight=w_c)

    return CSHTBundle(
        full_model=model_a,
        concealed_model=model_b,
        hydro_model=model_c,
        report={
            "head_A_full": {"pos": int(pos_a.size), "neg": int(neg_a.size), "n_features": len(ALL_FEATURE_NAMES)},
            "head_B_concealed": {
                "pos": int(pos_b.size),
                "neg": int(neg_b.size),
                "n_features": len(CONCEALED_FEATURE_NAMES),
                "median_depth_to_base_train": med_depth,
            },
            "head_C_hydro_analog": {
                "pos": int(pos_c.size),
                "neg": int(neg_c.size),
                "n_features": len(contrast_names),
                "hydro_train_cells": int(hydro_domain.sum()),
            },
        },
    )


def _predict_model(
    model: HistGradientBoostingClassifier,
    arrays: dict[str, np.ndarray],
    names: tuple[str, ...],
    domain: np.ndarray,
    *,
    chunk: int = 350_000,
) -> np.ndarray:
    out = np.zeros(domain.shape, dtype=np.float32)
    ids = np.flatnonzero(domain)
    for start in range(0, ids.size, chunk):
        batch = ids[start : start + chunk]
        out.ravel()[batch] = model.predict_proba(_extract_matrix(arrays, names, batch))[
            :, 1
        ].astype(np.float32)
    return out


def percentile_rank_surface(score: np.ndarray, domain: np.ndarray) -> np.ndarray:
    vals = np.asarray(score, dtype=np.float32)[domain]
    if vals.size < 100 or not np.isfinite(vals).all():
        raise ValueError("Domain must contain >=100 finite scores")
    q = np.linspace(0.0, 1.0, QUANTILE_KNOTS)
    knots = np.quantile(vals, q)
    uniq, first = np.unique(knots, return_index=True)
    ranks = q[first]
    out = np.zeros(score.shape, dtype=np.float32)
    if uniq.size == 1:
        out[domain] = 0.5
    else:
        out[domain] = np.interp(vals, uniq, ranks).astype(np.float32)
    return out


def predict_csht_surface(
    bundle: CSHTBundle,
    base_arrays: dict[str, np.ndarray],
    contrast_arrays: dict[str, np.ndarray],
    domain: np.ndarray,
) -> np.ndarray:
    """Predict cover- & LiDAR-regime adaptive fused probability surface in [0, 1]."""
    contrast_names = tuple(f"contrast30_{k}" for k in HYDRO_ANALOG_BASE_NAMES)
    p_a = _predict_model(bundle.full_model, base_arrays, ALL_FEATURE_NAMES, domain)
    p_b = _predict_model(bundle.concealed_model, base_arrays, CONCEALED_FEATURE_NAMES, domain)
    p_c = _predict_model(bundle.hydro_model, contrast_arrays, contrast_names, domain)

    r_a = percentile_rank_surface(p_a, domain)
    r_b = percentile_rank_surface(p_b, domain)
    r_c = percentile_rank_surface(p_c, domain)

    lid_valid = np.nan_to_num(np.asarray(base_arrays["lid_valid"], dtype=np.float32), nan=0.0) > 0.0
    fused = np.zeros(domain.shape, dtype=np.float32)
    in_lid = domain & lid_valid
    in_void = domain & ~lid_valid
    fused[in_lid] = 0.50 * r_a[in_lid] + 0.30 * r_b[in_lid] + 0.20 * r_c[in_lid]
    fused[in_void] = 0.30 * r_a[in_void] + 0.50 * r_b[in_void] + 0.20 * r_c[in_void]
    return np.clip(fused, 0.0, 1.0).astype(np.float32)


def celf_emit_300m(
    surface: np.ndarray,
    eligible: np.ndarray,
    budget: int,
    *,
    min_self_spacing_px: float = 2.5,
    crest_alpha: float = 0.35,
    gamma: float = 2.0,
    pool_cap: int = 320_000,
) -> np.ndarray:
    """Lazy-greedy submodular 300 m triangular-kernel coverage (CELF) dot placement."""
    elig = np.asarray(eligible, dtype=bool)
    h, w = elig.shape
    if budget < 0 or int(elig.sum()) < budget:
        raise ValueError(f"Invalid budget {budget} for {int(elig.sum())} eligible cells")
    if budget == 0:
        return np.zeros((h, w), dtype=bool)

    s = np.where(elig, np.clip(np.asarray(surface, dtype=np.float32), 0.0, 1.0), 0.0)
    crest = features.nms_ridge(s)
    weight = np.where(elig, (s ** gamma) * (1.0 + crest_alpha * crest), 0.0).astype(np.float32)

    ker = np.zeros((5, 5), dtype=np.float32)
    offsets: list[tuple[int, int, float]] = []
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            dist = float(np.hypot(dy, dx))
            if dist < 3.0:
                kv = 1.0 - dist / 3.0
                ker[dy + 2, dx + 2] = kv
                offsets.append((dy, dx, kv))

    init_gain = convolve(weight, ker, mode="constant", cval=0.0)
    cand_flat = np.flatnonzero(elig)
    cand_g = init_gain.ravel()[cand_flat]
    cap = min(int(pool_cap), int(cand_flat.size))
    if cap < cand_flat.size:
        top_ix = np.argpartition(cand_g, -cap)[-cap:]
        pool_flat = cand_flat[top_ix]
        pool_g = cand_g[top_ix]
    else:
        pool_flat = cand_flat
        pool_g = cand_g

    # Pad arrays by 3 px on all borders so flat neighbor strides never wrap across rows.
    pad = 3
    hp, wp = h + 2 * pad, w + 2 * pad
    w_pad = np.zeros((hp, wp), dtype=np.float32)
    w_pad[pad : pad + h, pad : pad + w] = weight
    w_pad_flat = w_pad.ravel()
    cov_pad = np.zeros(hp * wp, dtype=np.float32)
    blocked_pad = np.zeros(hp * wp, dtype=bool)

    rows_orig, cols_orig = np.divmod(pool_flat, w)
    pool_pad = (rows_orig + pad) * wp + (cols_orig + pad)

    k_strides = np.array([dy * wp + dx for dy, dx, _ in offsets], dtype=np.int64)
    k_vals = np.array([kv for _, _, kv in offsets], dtype=np.float32)

    r_block = int(np.floor(min_self_spacing_px))
    r2_max = float(min_self_spacing_px * min_self_spacing_px)
    block_strides = np.array(
        [
            dy * wp + dx
            for dy in range(-r_block, r_block + 1)
            for dx in range(-r_block, r_block + 1)
            if (dy * dy + dx * dx) <= r2_max + 1e-9
        ],
        dtype=np.int64,
    )

    order = np.argsort(-pool_g, kind="mergesort")
    heap: list[tuple[float, int, int]] = [
        (-float(pool_g[i]), int(pool_pad[i]), 0) for i in order
    ]
    heapq.heapify(heap)

    selected_pad: list[int] = []
    step = 0
    while heap and len(selected_pad) < budget:
        neg_g, p_idx, last_step = heapq.heappop(heap)
        if blocked_pad[p_idx]:
            continue
        if last_step == step:
            selected_pad.append(p_idx)
            step += 1
            nbrs = p_idx + k_strides
            cov_pad[nbrs] = np.maximum(cov_pad[nbrs], k_vals)
            blocked_pad[p_idx + block_strides] = True
        else:
            nbrs = p_idx + k_strides
            rem = k_vals - cov_pad[nbrs]
            rem[rem < 0.0] = 0.0
            new_g = float(np.dot(w_pad_flat[nbrs], rem))
            if new_g > 0.0:
                heapq.heappush(heap, (-new_g, p_idx, step))

    # Deterministic fallback if candidate pool saturated before reaching budget
    if len(selected_pad) < budget:
        all_r, all_c = np.divmod(cand_flat, w)
        all_pad = (all_r + pad) * wp + (all_c + pad)
        rem_order = np.argsort(-weight.ravel()[cand_flat], kind="mergesort")
        for idx_i in rem_order:
            p_idx = int(all_pad[idx_i])
            if not blocked_pad[p_idx]:
                selected_pad.append(p_idx)
                blocked_pad[p_idx + block_strides] = True
                if len(selected_pad) == budget:
                    break

    if len(selected_pad) != budget:
        raise RuntimeError(f"CELF emission underfilled: {len(selected_pad)} != {budget}")

    sel_arr = np.asarray(selected_pad, dtype=np.int64)
    sel_r = (sel_arr // wp) - pad
    sel_c = (sel_arr % wp) - pad
    out = np.zeros((h, w), dtype=bool)
    out[sel_r, sel_c] = True
    return out


def make_diagonal_wedge_folds(footprint: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """45-degree rotated diagonal wedges orthogonal to the NW/NE/SW/SE quadrant axes."""
    fp = np.asarray(footprint, dtype=bool)
    if fp.ndim != 2 or not fp.any():
        raise ValueError("Nonempty 2D footprint required")
    yy, xx = np.nonzero(fp)
    y_med, x_med = int(np.median(yy)), int(np.median(xx))
    h, w = fp.shape
    gy, gx = np.ogrid[:h, :w]
    u = (gy - y_med) + (gx - x_med)
    v = (gy - y_med) - (gx - x_med)
    fold = np.full((h, w), -1, dtype=np.int8)
    fold[(u < 0) & (v < 0) & fp] = 0
    fold[(u >= 0) & (v < 0) & fp] = 1
    fold[(u >= 0) & (v >= 0) & fp] = 2
    fold[(u < 0) & (v >= 0) & fp] = 3
    return fold, ["N_wedge", "E_wedge", "S_wedge", "W_wedge"]


class DiagonalSegmentHoldout:
    """Orthogonal 45°-rotated whole-component buffered confirmation holdout.

    Delegates all metric, tile-attribution, pooling and block-bootstrap calls
    directly to ``vendor.gems24_template.holdout`` with zero private metric fork.
    """

    def __init__(self, footprint: np.ndarray, labels: np.ndarray, *, buffer_px: int = 20):
        self.footprint = np.asarray(footprint, bool)
        self.labels = np.asarray(labels, bool)
        if (
            self.footprint.shape != self.labels.shape
            or self.footprint.ndim != 2
            or buffer_px < 3
            or np.any(self.labels & ~self.footprint)
            or not self.labels.any()
        ):
            raise ValueError("Aligned nonempty catalogue, footprint and >=3 px collar required")
        self.components, self.n_components = ndi_label(self.labels, structure=np.ones((3, 3), int))
        self.fold_grid, names = make_diagonal_wedge_folds(self.footprint)
        self.folds = []
        for f, name in enumerate(names):
            valid = self.footprint & (self.fold_grid == f)
            if not valid.any():
                raise ValueError(f"Empty diagonal fold: {name}")
            collar = distance_transform_edt(~valid) <= buffer_px
            hidden_ids = np.unique(self.components[collar & self.labels])
            hidden_ids = hidden_ids[hidden_ids > 0]
            hidden = self.labels & np.isin(self.components, hidden_ids)
            visible = self.labels & ~hidden
            truth = hidden & valid
            if not truth.any():
                raise ValueError(f"No withheld positives in diagonal fold: {name}")
            self.folds.append(
                {
                    "id": f,
                    "name": name,
                    "valid": valid,
                    "train": self.footprint
                    & (distance_transform_edt(~(valid | hidden)) > buffer_px),
                    "visible": visible,
                    "truth": truth,
                    "hidden_component_ids": hidden_ids,
                }
            )
        self.buffer_px = buffer_px

    def score_fold(self, prediction: np.ndarray, fold: dict):
        pred = np.asarray(prediction)
        if pred.shape != self.footprint.shape or not np.isin(pred, [0, 1]).all():
            raise ValueError("Finite aligned binary prediction required")
        blocks, reference = spatial_components(
            pred, fold["truth"], fold["valid"], fold["visible"], tile_px=100
        )
        return reference, blocks

    def summarize(self, predictions: list[np.ndarray], *, ci_draws: int = 1999) -> dict:
        if len(predictions) != len(self.folds):
            raise ValueError("One independent prediction per held-out fold required")
        rows, block_rows = [], []
        for pred, fold in zip(predictions, self.folds):
            result, blocks = self.score_fold(pred, fold)
            rows.append({"fold": fold["name"], **result})
            block_rows.append(blocks)
        blocks = np.sum(block_rows, axis=0)
        yy, xx = np.nonzero(self.footprint)
        nx = (self.footprint.shape[1] + 99) // 100
        active_blocks = np.unique((yy // 100) * nx + xx // 100)
        total = pooled_components(rows)
        return {
            "label": "HOLDOUT-DTI",
            "evaluator_version": MTR_EVALUATOR_VERSION,
            "split_id": f"diagonal-wedge-buffered-{self.buffer_px}px-confirm-v1",
            **total,
            "n_withheld_positive_pixels": int(total["n_truth"]),
            "n_unique_withheld_components": self.n_components,
            "ci95": spatial_bootstrap_ci(blocks[active_blocks], draws=ci_draws),
            "folds": rows,
            "protocol": {
                "aggregation": "pooled TPw/FPw/FNw, not mean fold DTI",
                "geometry": "45-degree rotated diagonal wedges (N/E/S/W) orthogonal to NW/NE/SW/SE",
                "buffer_m": self.buffer_px * 100,
                "whole_components_hidden_everywhere": True,
                "visible_fault_mask": "pixel-exact, applied before credit and FP calculation",
                "catalogue_features": "must be constructed from fold.visible only",
                "alpha": 0.2,
                "beta": 0.8,
                "triangular_kernel_radius_m": 300,
            },
        }

    def compare_paired(
        self,
        candidate_predictions: list[np.ndarray],
        baseline_predictions: list[np.ndarray],
        *,
        ci_draws: int = 1999,
        seed: int = 20261026,
    ) -> dict:
        cand_rows, cand_blocks = [], []
        base_rows, base_blocks = [], []
        fold_deltas = []
        for c_pred, b_pred, fold in zip(candidate_predictions, baseline_predictions, self.folds):
            c_res, c_blk = self.score_fold(c_pred, fold)
            b_res, b_blk = self.score_fold(b_pred, fold)
            cand_rows.append({"fold": fold["name"], **c_res})
            base_rows.append({"fold": fold["name"], **b_res})
            cand_blocks.append(c_blk)
            base_blocks.append(b_blk)
            fold_deltas.append(
                {
                    "fold": fold["name"],
                    "candidate_dti": float(c_res["dti"]),
                    "baseline_dti": float(b_res["dti"]),
                    "delta_dti": float(c_res["dti"] - b_res["dti"]),
                    "candidate_wins": bool(c_res["dti"] > b_res["dti"]),
                }
            )
        c_sum = np.sum(cand_blocks, axis=0)
        b_sum = np.sum(base_blocks, axis=0)
        yy, xx = np.nonzero(self.footprint)
        nx = (self.footprint.shape[1] + 99) // 100
        active = np.unique((yy // 100) * nx + xx // 100)
        c_tot = pooled_components(cand_rows)
        b_tot = pooled_components(base_rows)
        delta_ci = pooled_bootstrap(
            c_sum[active], paired=b_sum[active], resamples=ci_draws, seed=seed
        )
        delta = float(c_tot["dti"] - b_tot["dti"])
        wins = int(sum(1 for d in fold_deltas if d["candidate_wins"]))
        return {
            "evaluator_version": MTR_EVALUATOR_VERSION,
            "split_id": f"diagonal-wedge-buffered-{self.buffer_px}px-confirm-v1",
            "candidate_dti": float(c_tot["dti"]),
            "baseline_dti": float(b_tot["dti"]),
            "paired_delta_dti": delta,
            "paired_delta_ci95": delta_ci,
            "ci95_strictly_positive": bool(delta_ci[0] > 0.0),
            "fold_wins": wins,
            "n_folds": len(self.folds),
            "min_fold_delta": float(min(d["delta_dti"] for d in fold_deltas)),
            "folds": fold_deltas,
        }


def audit_uniqueness_against_manifest(
    surface: np.ndarray,
    surface_preview_dots: np.ndarray,
    final_dots: np.ndarray,
    footprint: np.ndarray,
    manifest_path: Path,
    *,
    root: Path,
    sample_pixels: int = 250_000,
    seed: int = 20261026,
) -> dict:
    """Run both pre-placement surface and final-dot duplicate screens vs all manifest rasters."""
    import rasterio

    fp = np.asarray(footprint, dtype=bool)
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha = sha256_bytes(manifest_bytes)
    manifest = __import__("json").loads(manifest_bytes.decode("utf-8"))
    entries = manifest["rasters"]

    rng = np.random.default_rng(seed)
    fp_flat = np.flatnonzero(fp)
    sample_idx = np.sort(rng.choice(fp_flat, size=min(sample_pixels, fp_flat.size), replace=False))
    surf_sample = np.asarray(surface, dtype=np.float64).ravel()[sample_idx]
    surf_ranks = rankdata(surf_sample, method="average")
    surf_centered = surf_ranks - surf_ranks.mean()
    surf_norm = float(np.linalg.norm(surf_centered))
    if surf_norm == 0.0:
        raise ValueError("Constant pre-placement surface cannot pass uniqueness guard")

    yy, xx = np.mgrid[-3:4, -3:4]
    disk = yy * yy + xx * xx <= 9

    surf_rows = []
    final_rows = []
    for entry in entries:
        rel = entry.get("local_path", entry.get("dest", ""))
        rpath = root / rel
        if not rpath.is_file():
            raise FileNotFoundError(f"Missing pinned registry raster: {rpath}")
        actual_sha = hashlib.sha256(rpath.read_bytes()).hexdigest()
        if actual_sha != entry["sha256"]:
            raise ValueError(f"Registry SHA mismatch for {entry['id']}: {actual_sha}")
        with rasterio.open(rpath) as ds:
            arr = ds.read(1)
        other_dots = (np.where(np.isfinite(arr), arr, 0.0) > 0.0) & fp
        near_other = binary_dilation(other_dots, structure=disk)

        other_sample = other_dots.ravel()[sample_idx].astype(np.float64)
        other_ranks = rankdata(other_sample, method="average")
        other_centered = other_ranks - other_ranks.mean()
        other_norm = float(np.linalg.norm(other_centered))
        if other_norm == 0.0:
            raise ValueError(f"Constant registry raster: {entry['id']}")
        surf_rho = float(np.dot(surf_centered, other_centered) / (surf_norm * other_norm))
        prev_cmp = novelty.binary_comparison(surface_preview_dots, other_dots, fp, near_other=near_other)
        surf_dup = bool(
            abs(surf_rho) > 0.90 or prev_cmp["fraction_candidate_within_3px"] > 0.70
        )
        surf_rows.append(
            {
                "registry_id": entry["id"],
                "site": entry["site"],
                "raster_sha256": actual_sha,
                "registry_dots": int(other_dots.sum()),
                "spearman_rho": surf_rho,
                "fraction_candidate_within_3px": prev_cmp["fraction_candidate_within_3px"],
                "duplicate": surf_dup,
            }
        )

        fin_cmp = novelty.binary_comparison(final_dots, other_dots, fp, near_other=near_other)
        fin_dup = bool(
            abs(fin_cmp["spearman_rho"]) > 0.90
            or fin_cmp["fraction_candidate_within_3px"] > 0.70
        )
        final_rows.append(
            {
                "registry_id": entry["id"],
                "site": entry["site"],
                "raster_sha256": actual_sha,
                "registry_dots": int(other_dots.sum()),
                "spearman_rho": fin_cmp["spearman_rho"],
                "fraction_candidate_within_3px": fin_cmp["fraction_candidate_within_3px"],
                "candidate_dots_within_3px": fin_cmp["candidate_dots_within_3px"],
                "candidate_dots": fin_cmp["candidate_dots"],
                "duplicate": fin_dup,
            }
        )

    surf_passed = not any(r["duplicate"] for r in surf_rows)
    final_passed = not any(r["duplicate"] for r in final_rows)
    try:
        rel_manifest = str(manifest_path.resolve().relative_to(root.resolve()))
    except ValueError:
        rel_manifest = str(manifest_path)
    return {
        "manifest": rel_manifest,
        "registry_sha256": manifest_sha,
        "registry_count": len(entries),
        "surface_sha256": sha256_array(np.asarray(surface, dtype=np.float32)),
        "surface": {
            "stage": "surface_before_placement",
            "registry_sha256": manifest_sha,
            "surface_sha256": sha256_array(np.asarray(surface, dtype=np.float32)),
            "registry_count": len(entries),
            "sample_pixels": int(sample_idx.size),
            "spearman_stop_gt": 0.90,
            "overlap_stop_gt": 0.70,
            "passed": surf_passed,
            "max_abs_spearman_rho": float(max(abs(r["spearman_rho"]) for r in surf_rows)),
            "max_preview_fraction_within_3px": float(
                max(r["fraction_candidate_within_3px"] for r in surf_rows)
            ),
            "comparisons": surf_rows,
        },
        "final_dots": {
            "stage": "final_dots",
            "registry_sha256": manifest_sha,
            "registry_count": len(entries),
            "spearman_stop_gt": 0.90,
            "overlap_stop_gt": 0.70,
            "overlap_radius_px": 3,
            "passed": final_passed,
            "max_abs_spearman_rho": float(max(abs(r["spearman_rho"]) for r in final_rows)),
            "max_candidate_fraction_within_3px": float(
                max(r["fraction_candidate_within_3px"] for r in final_rows)
            ),
            "comparisons": final_rows,
        },
    }
