"""FSML-PU: fold-safe multi-line corroboration with spy-PU experts.

Preregistered in evidence/fsml_preregistration_20261026.json (knowledge/22 §5).
Every catalogue-derived quantity (thermal_orphan, GEO tip lobes, PU training
pools) is built ONLY from the caller's fold-visible catalogue. The forbidden
``dist_known_fault_px`` CSV column is never read.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter, label as ndi_label
from sklearn.ensemble import HistGradientBoostingClassifier

from .csht_transfer import _extract_matrix, _predict_model, _sample_ids, percentile_rank_surface
from .paths import CACHE, CACHE_FEATURES, DATA

EXPERT_CHANNELS: dict[str, tuple[str, ...]] = {
    "S_scarp": ("lid_ex_max", "lid_step_max", "lid_lapneg_max", "lid_cross_max", "lid_relief",
                "lid_coh100", "lid_downface_max", "lid_upface_max", "det_elev_slope",
                "det_elev_curv2", "det_elev_curv4", "det_elev_ridge", "det_elev_coh", "det_elev_laps2"),
    "G_geopot": ("tmi_hg", "tmi_vg", "tc", "rtp_gms2", "rtp_ridge", "rtp_coh", "mag_anom_gms2",
                 "mag_anom_ridge", "ext_TMI_up150_gm2", "ext_TMI_up150_ridge", "iso_grav_anom_hg",
                 "iso_grav_anom_vg", "iso_grav_anom_slope", "iso_grav_anom_ridge", "iso_grav_anom_coh"),
    "C_cover": ("depth_to_base_surf", "depth_to_base_surf_gms2", "depth_to_base_surf_ridge",
                "depth_to_base_surf_coh", "cond_surf", "cond_surf_gms2", "cond_surf_laps2",
                "cond_surf_ridge", "rad_K", "rad_Th", "rad_U", "ext_ThK", "ext_UK", "ext_UTh"),
    "T_therm": ("geod_2ndinv", "geod_shearrate", "geod_dilaterate", "ieq_n100a15",
                "ieq_n100a15_ridge", "deq_n100a15", "hydro_upflow_potential",
                "hydro_demag_contrast", "thermal_density", "thermal_orphan"),
}
HYDRO_CACHE = CACHE / "hydro_features_a33_r2"


def load_arrays() -> dict[str, np.ndarray]:
    """Static (label-free) arrays: cached channels + hydro pair + thermal density."""
    arrays: dict[str, np.ndarray] = {}
    needed = sorted({c for v in EXPERT_CHANNELS.values() for c in v}
                    - {"hydro_upflow_potential", "hydro_demag_contrast", "thermal_density", "thermal_orphan"})
    for name in needed:
        p = CACHE_FEATURES / f"{name}.npy"
        if not p.is_file():
            raise FileNotFoundError(f"Missing cached channel {p}")
        arrays[name] = np.load(p, mmap_mode="r")
    arrays["hydro_upflow_potential"] = np.load(HYDRO_CACHE / "hydro_upflow_potential.npy", mmap_mode="r")
    arrays["hydro_demag_contrast"] = np.load(HYDRO_CACHE / "hydro_demag_contrast.npy", mmap_mode="r")
    return arrays


def thermal_density(footprint: np.ndarray) -> np.ndarray:
    """Temp-weighted Gaussian density of GDR well/spring points (label-free)."""
    path = CACHE / "fsml_thermal_density.npy"
    if path.is_file():
        return np.load(path)
    dens = np.zeros(footprint.shape, dtype=np.float32)
    n = 0
    with open(DATA / "gdr_wellspring_in_footprint.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                r, c = int(row["row"]), int(row["col"])
            except (KeyError, ValueError):
                continue
            if not (0 <= r < dens.shape[0] and 0 <= c < dens.shape[1]) or not footprint[r, c]:
                continue
            try:
                t = float(row.get("temp_c") or 0.0)
            except ValueError:
                t = 0.0
            dens[r, c] += 1.0 + min(max(t, 0.0), 100.0) / 50.0
            n += 1
    if n < 100:
        raise RuntimeError(f"thermal_density: only {n} usable well/spring points")
    out = gaussian_filter(dens, sigma=5.0, mode="nearest").astype(np.float32)
    out[~footprint] = 0.0
    np.save(path, out)
    return out


def thermal_orphan(density: np.ndarray, d_visible: np.ndarray) -> np.ndarray:
    return (density * np.clip((d_visible - 3.0) / 17.0, 0.0, 1.0)).astype(np.float32)


def geo_tip_lobe(visible: np.ndarray, d_visible: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Untrained geometric line: PCA tip-extension lobes + proximity band (visible only)."""
    struct = np.ones((3, 3), dtype=int)
    comp, _ = ndi_label(visible, structure=struct)
    splat = np.zeros(visible.shape, dtype=np.float32)
    H, W = visible.shape
    steps = ((3, 1.0), (6, 0.8), (9, 0.6), (12, 0.4), (15, 0.25))
    yy_all, xx_all = np.nonzero(visible)
    lab_all = comp[visible]
    order = np.argsort(lab_all, kind="mergesort")
    lab_sorted = lab_all[order]
    bounds = np.flatnonzero(np.diff(lab_sorted)) + 1
    starts = np.concatenate([[0], bounds])
    ends = np.concatenate([bounds, [lab_sorted.size]])
    for s0, e0 in zip(starts, ends):
        if e0 - s0 < 15:
            continue
        idx = order[s0:e0]
        pts = np.stack([yy_all[idx], xx_all[idx]], axis=1).astype(np.float64)
        ctr = pts.mean(axis=0)
        cov = np.cov((pts - ctr).T)
        vals, vecs = np.linalg.eigh(cov)
        axis = vecs[:, int(np.argmax(vals))]  # (dy, dx)
        proj = (pts - ctr) @ axis
        for end in (pts[int(np.argmin(proj))], pts[int(np.argmax(proj))]):
            direction = np.sign(float((end - ctr) @ axis)) or 1.0
            for dist, w in steps:
                p = end + axis * direction * dist
                r, c = int(round(p[0])), int(round(p[1]))
                if 0 <= r < H and 0 <= c < W:
                    splat[r, c] += np.float32(w)
    lobe = gaussian_filter(splat, sigma=2.0, mode="nearest")
    band = np.where((d_visible > 2.0) & (d_visible <= 30.0), np.exp(-d_visible / 8.0), 0.0)
    out = (lobe + 0.3 * band).astype(np.float32)
    out[~footprint] = 0.0
    return out


def _hgb(seed: int) -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(
        max_iter=150, learning_rate=0.06, max_leaf_nodes=47, min_samples_leaf=60,
        l2_regularization=3.0, early_stopping=False, random_state=seed)


def _fit_pu_expert(arrays, names, train, visible, d_visible, *, seed):
    """Two-step spy-PU fit; returns (step2_model, report)."""
    rng = np.random.default_rng(seed)
    pos_all = _sample_ids(train & visible, 40_000, rng)
    u_all = _sample_ids(train & ~visible & (d_visible > 5.0), 80_000, rng)
    if pos_all.size < 200 or u_all.size < 1000:
        raise RuntimeError(f"PU pools too small: pos={pos_all.size} U={u_all.size}")
    perm = rng.permutation(pos_all.size)
    n_spy = max(50, int(0.2 * pos_all.size))
    spy, pos_tr = pos_all[perm[:n_spy]], pos_all[perm[n_spy:]]

    def fit_xy(pos_ids, neg_ids, mdl_seed):
        ids = np.concatenate([pos_ids, neg_ids])
        y = np.concatenate([np.ones(pos_ids.size, np.uint8), np.zeros(neg_ids.size, np.uint8)])
        w = np.concatenate([np.ones(pos_ids.size, np.float32),
                            np.full(neg_ids.size, pos_ids.size / neg_ids.size, np.float32)])
        m = _hgb(mdl_seed)
        m.fit(_extract_matrix(arrays, names, ids), y, sample_weight=w)
        return m

    m1 = fit_xy(pos_tr, u_all, seed + 11)
    spy_scores = m1.predict_proba(_extract_matrix(arrays, names, spy))[:, 1]
    thr = float(np.quantile(spy_scores, 0.15))
    u_scores = m1.predict_proba(_extract_matrix(arrays, names, u_all))[:, 1]
    rn = u_all[u_scores < thr]
    if rn.size < 20_000:
        rn = u_all[np.argsort(u_scores, kind="mergesort")[:20_000]]
    m2 = fit_xy(pos_all, rn, seed + 22)
    return m2, {"pos": int(pos_all.size), "U": int(u_all.size), "spies": int(spy.size),
                "rn": int(rn.size), "spy_q15": thr}


def _pu_ranks(arrays_static, density, train, visible, domain, *, seed):
    """Shared core: percentile ranks of the 4 spy-PU experts on domain."""
    d_visible = distance_transform_edt(~visible)
    arrays = dict(arrays_static)
    arrays["thermal_density"] = density
    arrays["thermal_orphan"] = thermal_orphan(density, d_visible)
    ranks, report = [], {}
    for i, (ename, names) in enumerate(EXPERT_CHANNELS.items()):
        model, rep = _fit_pu_expert(arrays, names, train, visible, d_visible,
                                    seed=seed + 1000 * (i + 1))
        p = _predict_model(model, arrays, names, domain)
        ranks.append(percentile_rank_surface(p, domain))
        report[ename] = rep
    return ranks, report, d_visible


def fit_predict_fsml(arrays_static, density, train, visible, domain, footprint, *, seed):
    """Fit 4 PU experts on (train, visible); return (V1_gate, V2_nogate, report) on domain."""
    ranks, report, d_visible = _pu_ranks(arrays_static, density, train, visible, domain, seed=seed)
    geo = geo_tip_lobe(visible, d_visible, footprint)
    ranks.append(percentile_rank_surface(geo, domain))
    R = np.stack(ranks)  # (5, H, W)
    mean_r = R.mean(axis=0)
    second = np.partition(R, -2, axis=0)[-2]
    v1 = (mean_r * np.clip(second / 0.75, 0.30, 1.0)).astype(np.float32)
    v2 = mean_r.astype(np.float32)
    v1[~domain] = 0.0
    v2[~domain] = 0.0
    return v1, v2, report


def worm_field(footprint: np.ndarray) -> np.ndarray:
    """Label-free multiscale geopotential worm edges (FSML2 preregistration)."""
    from . import features as _features

    path = CACHE / "fsml2_worm.npy"
    if path.is_file():
        return np.load(path)
    acc = np.zeros(footprint.shape, dtype=np.float32)
    n = 0
    for field_name in ("rtp", "ext_TMI_up150", "iso_grav_anom"):
        field = np.asarray(np.load(CACHE_FEATURES / f"{field_name}.npy"), dtype=np.float32)
        for sigma in (1.0, 2.0, 4.0):
            gm = np.nan_to_num(_features.grad_mag(field, sigma, footprint), nan=0.0)
            ridge = np.nan_to_num(gm * _features.nms_ridge(gm), nan=0.0).astype(np.float32)
            acc += percentile_rank_surface(np.where(footprint, ridge, 0.0), footprint)
            n += 1
    out = (acc / n).astype(np.float32)
    out[~footprint] = 0.0
    np.save(path, out)
    return out


def fit_predict_fsml2(arrays_static, density, worm, l_line, train, visible, domain, *, seed):
    """FSML2-CC: corroboration-count fusion. Returns (V1_cc6, V2_cc4, report)."""
    ranks, report, _ = _pu_ranks(arrays_static, density, train, visible, domain, seed=seed)
    r_worm = percentile_rank_surface(np.asarray(worm, dtype=np.float32), domain)
    r_line = percentile_rank_surface(np.asarray(l_line, dtype=np.float32), domain)
    R6 = np.stack(ranks + [r_worm, r_line])
    R4 = np.stack(ranks)
    v1 = ((R6 >= 0.90).sum(axis=0) + 0.1 * R6.mean(axis=0)).astype(np.float32)
    v2 = ((R4 >= 0.90).sum(axis=0) + 0.1 * R4.mean(axis=0)).astype(np.float32)
    v1[~domain] = 0.0
    v2[~domain] = 0.0
    return v1, v2, report
