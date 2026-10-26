"""Round-3 domain-invariant analog co-training and multi-scale physical hypotheses (H33-R3-1..3).

Memory-lean implementation operating on the 5,167,833 in-footprint cells (`X_fp` of shape
`(N_fp, 32)` float32) so peak memory stays well under 1.2 GB.
All models and score surfaces in this module are 100% independent of ``h19_5_nan.tif`` and
``dotted_h19_5_d2_8_nan.tif``. Every catalogue-derived quantity is computed strictly from
the fold-visible fault mask ``visible_faults`` passed into each hide-and-recover fold.
"""
from __future__ import annotations

import csv
import gc
from pathlib import Path

import numpy as np
from scipy.ndimage import (
    convolve,
    distance_transform_edt,
    gaussian_filter,
    uniform_filter,
)
from scipy.spatial import cKDTree
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from . import analog, emission, features, grid

TARGET_BUDGET_DOTS = 37654  # Matches the measured B=2 optimal budget from GEMSDOE32 (0.2778)
POISSON_MIN_DIST_PX = 3.0   # Matches exact 300 m (3.0 px) DTI triangular kernel radius
VISIBLE_PRUNE_PX = 2.0      # B=2 visible-catalogue side-lobe collar prune (200 m)

INVARIANT_FEATURE_CHANNELS = (
    # 1. Topography & 3DEP 1m LiDAR scarp geometry (dimensionless / derivative)
    "det_elev_coh",
    "det_elev_gms2",
    "det_elev_gms4",
    "det_elev_curv2",
    "lid_coh100",
    "lid_step_max",
    "lid_ex_max",
    "lid_lapneg_max",
    # 2. Magnetics (shallow + 150 m upward continuation)
    "tmi_coh",
    "tmi_gms1",
    "tmi_gms2",
    "tmi_gms4",
    "tmi_curv2",
    "ext_TMI_up150_gm2",
    "rtp_gms2",
    # 3. Isostatic gravity
    "iso_grav_anom_coh",
    "iso_grav_anom_gms1",
    "iso_grav_anom_gms2",
    "iso_grav_anom_gms4",
    "iso_grav_anom_curv2",
    # 4. Basement depth & subsurface electrical conductivity
    "depth_to_base_surf_coh",
    "depth_to_base_surf_gms2",
    "depth_to_base_surf_curv2",
    "cond_surf_coh",
    "cond_surf_gms2",
    "cond_surf_curv2",
    # 5. Radiometric ordinal extensions & geodetic strain rates
    "ext_ThK",
    "ext_UTh",
    "geod_dilaterate",
    "geod_shearrate",
)


def local_basin_standardize(arr: np.ndarray, footprint: np.ndarray, window_px: int = 250) -> np.ndarray:
    """Remove regional basin-scale offset/scale via rolling 25 km mean/RMS standardization."""
    a = np.where(footprint & np.isfinite(arr), arr, 0.0).astype(np.float32)
    w = footprint.astype(np.float32)
    mean_w = uniform_filter(w, size=window_px, mode="nearest")
    mean_a = uniform_filter(a, size=window_px, mode="nearest") / np.maximum(mean_w, 1e-6)
    diff = (a - mean_a) * w
    var_a = uniform_filter(diff * diff, size=window_px, mode="nearest") / np.maximum(mean_w, 1e-6)
    std_a = np.sqrt(np.maximum(var_a, 0.0))

    vals = a[footprint]
    global_mad = float(np.median(np.abs(vals - np.median(vals)))) * 1.4826 + 1e-6
    scale = np.maximum(std_a, 0.25 * global_mad)
    z = np.where(footprint, (a - mean_a) / scale, 0.0)
    return np.clip(z, -6.0, 6.0).astype(np.float32)


def gdr_geothermometer_upflow_prior(footprint: np.ndarray) -> np.ndarray:
    """Label-free reservoir temperature upflow prior from GDR 1391 spring chemistry."""
    path = grid.DATA / "gdr_wellspring_in_footprint.csv"
    h, w = footprint.shape
    if not path.is_file():
        return np.zeros((h, w), dtype=np.float32)

    site_temps: dict[tuple[int, int], float] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                rr = int(float(row["row"]))
                cc = int(float(row["col"]))
            except (KeyError, TypeError, ValueError):
                continue
            if not (0 <= rr < h and 0 <= cc < w and footprint[rr, cc]):
                continue
            vals = []
            for col_name in ("geothermquartz_c", "geothermchalc_c", "geothermcat_c", "temp_c"):
                raw = row.get(col_name)
                if raw is not None and raw != "":
                    try:
                        v = float(raw)
                        if np.isfinite(v) and 20.0 <= v <= 350.0:
                            vals.append(v)
                    except ValueError:
                        pass
            if vals:
                key = (rr, cc)
                t_max = max(vals)
                if t_max > site_temps.get(key, 0.0):
                    site_temps[key] = t_max

    if not site_temps:
        return np.zeros((h, w), dtype=np.float32)

    pts = np.array(list(site_temps.keys()), dtype=np.float64)
    temps = np.array(list(site_temps.values()), dtype=np.float64)
    strength = np.clip((temps - 60.0) / 140.0, 0.0, 1.0)
    hot = strength > 0.05
    if not np.any(hot):
        return np.zeros((h, w), dtype=np.float32)

    pts_hot = pts[hot]
    str_hot = strength[hot]
    tree = cKDTree(pts_hot)
    fy, fx = np.nonzero(footprint)
    q_pts = np.column_stack([fy.astype(np.float64), fx.astype(np.float64)])
    d, idx = tree.query(q_pts, k=min(6, len(pts_hot)))
    if d.ndim == 1:
        d = d[:, None]
        idx = idx[:, None]
    weights = np.exp(-0.5 * (d / 25.0) ** 2)
    score_fp = (weights * str_hot[idx]).sum(axis=1) / np.maximum(weights.sum(axis=1), 1e-6)
    out = np.zeros((h, w), dtype=np.float32)
    out[fy, fx] = np.clip(score_fp, 0.0, 1.0).astype(np.float32)
    return out


def _pos_unit_1d(z_fp: np.ndarray) -> np.ndarray:
    return np.clip(z_fp / 4.0, 0.0, 1.0).astype(np.float32)


def compute_vertical_persistence_from_fp(
    X_fp: np.ndarray,
    name_to_idx: dict[str, int],
    footprint: np.ndarray,
) -> np.ndarray:
    """H33-R3-2 label-free physical surface computed directly from in-footprint feature columns."""
    def col(n: str) -> np.ndarray:
        return X_fp[:, name_to_idx[n]]

    mag_s1 = _pos_unit_1d(col("tmi_gms1"))
    mag_s2 = _pos_unit_1d(col("tmi_gms2"))
    mag_s4 = _pos_unit_1d(col("tmi_gms4"))
    mag_up = _pos_unit_1d(col("ext_TMI_up150_gm2"))
    mag_persist = ((mag_s1 * mag_s2 * mag_s4 * mag_up) ** 0.25) * col("tmi_coh")

    grav_s1 = _pos_unit_1d(col("iso_grav_anom_gms1"))
    grav_s2 = _pos_unit_1d(col("iso_grav_anom_gms2"))
    grav_s4 = _pos_unit_1d(col("iso_grav_anom_gms4"))
    grav_persist = ((grav_s1 * grav_s2 * grav_s4) ** (1.0 / 3.0)) * col("iso_grav_anom_coh")

    base_edge = _pos_unit_1d(col("depth_to_base_surf_gms2")) * col("depth_to_base_surf_coh")
    cond_edge = _pos_unit_1d(col("cond_surf_gms2")) * col("cond_surf_coh")
    subsurface = np.maximum(base_edge, cond_edge)

    topo_edge = _pos_unit_1d(col("det_elev_gms2")) * col("det_elev_coh")
    lid_edge = np.maximum(_pos_unit_1d(col("lid_step_max")), _pos_unit_1d(col("lid_ex_max")))
    scarp = 0.55 * topo_edge + 0.45 * lid_edge

    families = np.stack([mag_persist, grav_persist, subsurface, scarp], axis=0)
    families.sort(axis=0)
    top1 = families[-1]
    top2 = families[-2]
    top3 = families[-3]
    corroborated = (0.45 * top1 + 0.35 * top2 + 0.20 * top3) * np.sqrt(np.maximum(top2, 1e-4))
    corroborated = corroborated * (1.0 + 0.20 * col("gdr_geotherm_upflow"))

    hi = float(np.percentile(corroborated, 99.8)) if corroborated.size else 1.0
    vp_fp = np.clip(corroborated / max(hi, 1e-6), 0.0, 1.0).astype(np.float32)
    out = np.zeros(footprint.shape, dtype=np.float32)
    out[footprint] = vp_fp
    return out


def build_invariant_fp_matrix(
    footprint: np.ndarray,
    canary_fn=None,
    folds=None,
) -> tuple[np.ndarray, list[str], dict[str, np.ndarray], dict[str, dict]]:
    """Build contiguous (N_fp, 32) float32 matrix on in-footprint pixels and run streaming canaries."""
    n_fp = int(footprint.sum())
    names = list(INVARIANT_FEATURE_CHANNELS) + ["gdr_geotherm_upflow", "multiphysics_vertical_persistence"]
    n_feat = len(names)
    X_fp = np.empty((n_fp, n_feat), dtype=np.float32)
    name_to_idx = {n: i for i, n in enumerate(names)}
    canary_results: dict[str, dict] = {}
    saved_2d: dict[str, np.ndarray] = {}

    for i, ch in enumerate(INVARIANT_FEATURE_CHANNELS):
        raw = np.asarray(features.load_channel(ch), dtype=np.float32)
        if ch.endswith("_coh"):
            normed = np.where(footprint & np.isfinite(raw), np.clip(raw, 0.0, 1.0), 0.0).astype(np.float32)
        else:
            normed = local_basin_standardize(raw, footprint, window_px=250)
        X_fp[:, i] = normed[footprint]
        if ch in ("det_elev_gms2", "tmi_gms2", "geod_dilaterate", "geod_shearrate"):
            saved_2d[ch] = normed
        if canary_fn is not None and folds is not None:
            canary_results[ch] = canary_fn(normed, folds, max_neg_per_fold=30000, seed=33 + i)
        del raw, normed

    # Channel 31: GDR geothermometer upflow prior
    upflow = gdr_geothermometer_upflow_prior(footprint)
    i_up = name_to_idx["gdr_geotherm_upflow"]
    X_fp[:, i_up] = upflow[footprint]
    if canary_fn is not None and folds is not None:
        canary_results["gdr_geotherm_upflow"] = canary_fn(upflow, folds, max_neg_per_fold=30000, seed=33 + i_up)
    del upflow

    # Channel 32: Multi-physics vertical-persistence surface
    vp_2d = compute_vertical_persistence_from_fp(X_fp, name_to_idx, footprint)
    i_vp = name_to_idx["multiphysics_vertical_persistence"]
    X_fp[:, i_vp] = vp_2d[footprint]
    saved_2d["multiphysics_vertical_persistence"] = vp_2d
    if canary_fn is not None and folds is not None:
        canary_results["multiphysics_vertical_persistence"] = canary_fn(vp_2d, folds, max_neg_per_fold=30000, seed=33 + i_vp)

    gc.collect()
    return X_fp, names, saved_2d, canary_results


def predict_fp_to_2d(clf, X_fp: np.ndarray, footprint: np.ndarray, chunk: int = 800_000) -> np.ndarray:
    """Predict probabilities on X_fp in chunks and scatter back into a 2D footprint grid."""
    n = X_fp.shape[0]
    p_fp = np.empty(n, dtype=np.float32)
    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        p_fp[start:end] = clf.predict_proba(X_fp[start:end])[:, 1].astype(np.float32)
    out = np.zeros(footprint.shape, dtype=np.float32)
    out[footprint] = p_fp
    return out


def compute_domain_importance_weights_fp(
    X_fp: np.ndarray,
    analog_mask: np.ndarray,
    footprint: np.ndarray,
    *,
    seed: int = 33,
) -> tuple[np.ndarray, dict]:
    """Spatial-block domain discriminator on X_fp + importance weights w_fp in [0.6, 1.8]."""
    rng = np.random.default_rng(seed)
    fy, fx = np.nonzero(footprint)
    is_analog_fp = analog_mask[footprint]
    block_even = (((fy // 200) + (fx // 200)) % 2 == 0)

    def sample_idx(mask_1d: np.ndarray, k: int) -> np.ndarray:
        idx = np.flatnonzero(mask_1d)
        if len(idx) <= k:
            return idx
        return rng.choice(idx, size=k, replace=False)

    tr_s = sample_idx(is_analog_fp & block_even, 15000)
    tr_t = sample_idx((~is_analog_fp) & block_even, 15000)
    te_s = sample_idx(is_analog_fp & (~block_even), 15000)
    te_t = sample_idx((~is_analog_fp) & (~block_even), 15000)

    X_tr = np.vstack([X_fp[tr_s], X_fp[tr_t]])
    y_tr = np.concatenate([np.ones(len(tr_s), np.uint8), np.zeros(len(tr_t), np.uint8)])
    X_te = np.vstack([X_fp[te_s], X_fp[te_t]])
    y_te = np.concatenate([np.ones(len(te_s), np.uint8), np.zeros(len(te_t), np.uint8)])

    clf_eval = HistGradientBoostingClassifier(max_iter=60, max_leaf_nodes=15, l2_regularization=2.0, random_state=seed)
    clf_eval.fit(X_tr, y_tr)
    p_te = clf_eval.predict_proba(X_te)[:, 1]
    auc = float(roc_auc_score(y_te, p_te))
    err = float(np.mean((p_te >= 0.5) != y_te))

    # Fit importance-weight discriminator on full footprint sample
    all_s = sample_idx(is_analog_fp, 20000)
    all_t = sample_idx(~is_analog_fp, 20000)
    clf_w = HistGradientBoostingClassifier(max_iter=50, max_leaf_nodes=15, l2_regularization=2.0, random_state=seed)
    clf_w.fit(
        np.vstack([X_fp[all_s], X_fp[all_t]]),
        np.concatenate([np.ones(len(all_s), np.uint8), np.zeros(len(all_t), np.uint8)]),
    )
    n = X_fp.shape[0]
    p_analog_fp = np.empty(n, dtype=np.float32)
    for start in range(0, n, 800_000):
        end = min(start + 800_000, n)
        p_analog_fp[start:end] = clf_w.predict_proba(X_fp[start:end])[:, 1].astype(np.float32)
    w_fp = np.clip((1.0 - p_analog_fp) / np.maximum(p_analog_fp, 0.25), 0.6, 1.8).astype(np.float32)

    diag = {
        "held_out_block_auc": auc,
        "held_out_block_error": err,
        "d_h_delta_h_proxy": float(max(0.0, 2.0 * (1.0 - 2.0 * err))),
        "n_train": int(len(y_tr)),
        "n_test": int(len(y_te)),
    }
    return w_fp, diag


def fit_predict_h33_r3_1_fp(
    X_fp: np.ndarray,
    vp_2d: np.ndarray,
    analog_mask: np.ndarray,
    visible_faults: np.ndarray,
    train_eligible: np.ndarray,
    footprint: np.ndarray,
    w_fp: np.ndarray,
    *,
    seed: int = 33,
) -> tuple[np.ndarray, dict]:
    """H33-R3-1: Co-train on analog-field + fold-visible catalogue with domain importance weights."""
    rng = np.random.default_rng(seed)
    vis = np.asarray(visible_faults, dtype=bool) & train_eligible & footprint
    d_vis = distance_transform_edt(~vis) if vis.any() else np.full(footprint.shape, np.inf)

    vis_fp = vis[footprint]
    elig_fp = (train_eligible & footprint)[footprint]
    analog_fp = analog_mask[footprint]
    d_vis_fp = d_vis[footprint]

    pos_a_idx = np.flatnonzero(vis_fp & analog_fp)
    pos_t_idx = np.flatnonzero(vis_fp & (~analog_fp))
    neg_idx = np.flatnonzero(elig_fp & (d_vis_fp > 3.0))

    if len(pos_a_idx) > 12000:
        pos_a_idx = rng.choice(pos_a_idx, size=12000, replace=False)
    if len(pos_t_idx) > 28000:
        pos_t_idx = rng.choice(pos_t_idx, size=28000, replace=False)
    pos_idx = np.concatenate([pos_a_idx, pos_t_idx])
    n_neg = min(len(neg_idx), len(pos_idx) * 2)
    neg_idx = rng.choice(neg_idx, size=n_neg, replace=False)

    X = np.vstack([X_fp[pos_idx], X_fp[neg_idx]])
    y = np.concatenate([np.ones(len(pos_idx), dtype=np.uint8), np.zeros(len(neg_idx), dtype=np.uint8)])

    w_pos = w_fp[pos_idx].copy()
    w_pos[analog_fp[pos_idx]] *= 1.5
    sample_weight = np.concatenate([w_pos, np.ones(len(neg_idx), dtype=np.float32)])

    clf = HistGradientBoostingClassifier(
        max_iter=120,
        learning_rate=0.06,
        max_leaf_nodes=31,
        min_samples_leaf=40,
        l2_regularization=2.0,
        random_state=seed,
    )
    clf.fit(X, y, sample_weight=sample_weight)
    prob_2d = predict_fp_to_2d(clf, X_fp, footprint)
    surface = np.where(footprint, 0.70 * prob_2d + 0.30 * vp_2d, 0.0).astype(np.float32)
    return surface, {
        "n_pos_analog": int(len(pos_a_idx)),
        "n_pos_target_visible": int(len(pos_t_idx)),
        "n_neg": int(len(neg_idx)),
    }


def visible_fault_tip_lobes(visible_faults: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """H33-R3-3 helper: derive fault-tip and step-over stress zone strictly from ``visible_faults``."""
    vis = np.asarray(visible_faults, dtype=bool) & footprint
    if not vis.any():
        return np.zeros_like(footprint, dtype=np.float32)
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.int8)
    nbrs = convolve(vis.astype(np.int8), kernel, mode="constant", cval=0)
    tips = vis & (nbrs >= 1) & (nbrs <= 2)
    if not tips.any():
        return np.zeros_like(footprint, dtype=np.float32)
    d_tip = distance_transform_edt(~tips)
    d_vis = distance_transform_edt(~vis)
    lobe = np.exp(-0.5 * (d_tip / 12.0) ** 2) * ((d_vis > 2.0) & (d_vis <= 25.0) & footprint)
    return lobe.astype(np.float32)


def compute_h33_r3_3_surface(
    saved_2d: dict[str, np.ndarray],
    visible_faults: np.ndarray,
    footprint: np.ndarray,
) -> np.ndarray:
    """H33-R3-3: Transtensional step-over & dilatational strain-gradient relay bridge surface."""
    vp = saved_2d["multiphysics_vertical_persistence"]
    dil = np.where(footprint, np.clip(saved_2d["geod_dilaterate"] / 4.0, 0.0, 1.0), 0.0)
    shr = np.where(footprint, np.clip(saved_2d["geod_shearrate"] / 4.0, 0.0, 1.0), 0.0)
    strain_boost = 0.5 * dil + 0.5 * shr
    tip_lobe = visible_fault_tip_lobes(visible_faults, footprint)
    raw = vp * (1.0 + 0.35 * strain_boost + 0.65 * tip_lobe)
    vals = raw[footprint]
    hi = float(np.percentile(vals, 99.8)) if vals.size else 1.0
    out = np.zeros_like(raw, dtype=np.float32)
    out[footprint] = np.clip(raw[footprint] / max(hi, 1e-6), 0.0, 1.0)
    return out


def emit_sparse_dots(
    surface: np.ndarray,
    visible_faults: np.ndarray,
    footprint: np.ndarray,
    *,
    budget_dots: int = TARGET_BUDGET_DOTS,
    min_dist_px: float = POISSON_MIN_DIST_PX,
    prune_vis_px: float = VISIBLE_PRUNE_PX,
) -> np.ndarray:
    """Emit priority-ordered Poisson-disk dots on surface ridge crests outside visible B=2 collar."""
    vis = np.asarray(visible_faults, dtype=bool) & footprint
    d_vis = distance_transform_edt(~vis) if vis.any() else np.full(footprint.shape, np.inf)
    eligible = footprint & (d_vis > prune_vis_px) & np.isfinite(surface)
    if not eligible.any():
        return np.zeros(footprint.shape, dtype=bool)

    smooth = gaussian_filter(np.where(footprint, surface, 0.0).astype(np.float32), sigma=1.0, mode="nearest")
    crest = emission.ridge_nms(np.where(eligible, smooth, np.nan), width=1) & eligible
    vals = smooth[eligible]
    q88 = float(np.quantile(vals, 0.88))
    cand = eligible & ((crest & (smooth >= float(np.quantile(vals, 0.65)))) | (smooth >= q88))
    return emission.dot_thin(cand, min_dist_px, priority=smooth, max_dots=budget_dots)
