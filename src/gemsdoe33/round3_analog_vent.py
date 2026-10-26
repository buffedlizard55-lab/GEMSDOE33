"""Round-3 Bounded Analog-Field Domain Adaptation & Hydrothermal Conduit Discovery.

Implements the preregistered 2026-10-25 Round-3 hypothesis slate
(``knowledge/10_hypothesis_slate_20261025_r3.md``):

* ``H33-R3-1`` (``DA-HGCM-Submod``): Ben-David et al. (2010) divergence-screened
  multi-physics + GDR-1391 geothermometer/vent hydrothermal conduit co-training
  with fold-visible structural continuation features and exact submodular 300 m
  Dinkelbach-CELF Tversky allocation (``vendor/gems57/emit.py``).
* ``H33-R3-2`` (``DA-PurePhys-Submod``): Pure label-free domain-adapted
  geophysical + LiDAR antislope + hydrothermal conduit model (zero network
  context features).
* ``H33-R3-3`` (``DA-LinearVC-Submod``): Explicit finite-VC linear halfspace
  domain-adapted classifier (``vc_dim = d + 1``) with measured empirical
  symmetric-difference divergence ``d_{H Delta H}`` (Ben-David et al., 2010,
  Lemma 2 & Theorem 2).

Hard safety invariants enforced at runtime:
1. ``dist_known_fault_px`` in GDR CSVs is forbidden and never read.
2. ``derived_sgmc_faults_100m_u8.tif``, ``sample_submission.tif`` values, and
   ``h19_5_nan.tif`` are never read during candidate feature construction or
   training.
3. Regional baseline level channels (``det_elev``, ``depth_to_base_surf``,
   ``iso_grav_anom``, ``rtp``, ``mag_anom``, ``tmi``, ``cond_surf``, etc.) are
   excluded from candidate features; only differential/dimensionless descriptors
   that pass BOTH the standalone holdout leakage canary (``AUC <= 0.90``) and
   the spatial-block source-target divergence screen (``|AUC - 0.5| <= 0.20``)
   enter the adapted representation.
4. Visible-network features in ``H33-R3-1`` are computed strictly from the
   supplied ``visible`` fault mask; during training inside LOQO quadrants,
   internal connected-component cross-fitting prevents ``d(x, visible) == 0``
   target self-distance degeneracy.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy import ndimage as ndi
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from .analog import build_analog_masks
from .domain import ben_david_theorem2_bound
from .features import _norm_conv
from .paths import CACHE_FEATURES as CHANNEL_DIR, DATA as DATA_DIR

# Strictly local differential / dimensionless channels from the 121-channel cache.
# Raw regional levels (det_elev, depth_to_base_surf, iso_grav_anom, rtp, mag_anom,
# tmi, cond_surf, ieq_n100a15, deq_n100a15, geod_*, raw rad_*) are intentionally
# excluded to prevent regional basin memorization (IR-33-DA-01 / H33-F failure).
CANDIDATE_CACHED_CHANNELS: tuple[str, ...] = (
    # Official competition local derivatives (7)
    "tmi_hg",
    "tmi_vg",
    "tc",
    "iso_grav_anom_slope",
    "iso_grav_anom_vg",
    "iso_grav_anom_hg",
    "det_elev_slope",
    # External GeoDAWN ordinal ratios & upward-continued magnetic gradients (5)
    "ext_ThK",
    "ext_UK",
    "ext_UTh",
    "ext_TMI_up150_gm2",
    "ext_TMI_up150_ridge",
    # External 1 m 3DEP LiDAR scarp & coherence descriptors (9)
    "lid_ex_max",
    "lid_ex_mean",
    "lid_step_max",
    "lid_lapneg_max",
    "lid_lappos_max",
    "lid_downface_max",
    "lid_upface_max",
    "lid_cross_max",
    "lid_coh100",
    # Multi-scale normalized-convolution local derivatives (21)
    "det_elev_gms1",
    "det_elev_gms2",
    "det_elev_gms4",
    "det_elev_curv2",
    "det_elev_coh",
    "det_elev_ridge",
    "depth_to_base_surf_gms1",
    "depth_to_base_surf_gms2",
    "depth_to_base_surf_gms4",
    "depth_to_base_surf_coh",
    "iso_grav_anom_gms1",
    "iso_grav_anom_gms2",
    "iso_grav_anom_gms4",
    "iso_grav_anom_curv2",
    "iso_grav_anom_coh",
    "rtp_gms1",
    "rtp_gms2",
    "rtp_laps2",
    "rtp_curv2",
    "rtp_coh",
    "cond_surf_gms2",
    "cond_surf_gms4",
    "cond_surf_coh",
)

WELLSPRING_ALLOWED_COLS = frozenset({
    "row",
    "col",
    "temp_c",
    "geothermquartz_c",
    "geothermchalc_c",
    "geothermcat_c",
    "thermalclass",
})
VENT_ALLOWED_COLS = frozenset({"row", "col", "rock_type"})
FORBIDDEN_COLS = frozenset({"dist_known_fault_px"})


def _fast_norm_conv_large_sigma(arr: np.ndarray, valid: np.ndarray, sigma: float) -> np.ndarray:
    """Fast 4x-decimated normalized Gaussian background estimator for sigma >= 12 px."""
    s = 4
    v_sub = valid[::s, ::s].astype(np.float32)
    f_sub = np.where(valid[::s, ::s], arr[::s, ::s], 0.0).astype(np.float32)
    num = ndi.gaussian_filter(f_sub, sigma / s, mode="nearest")
    den = ndi.gaussian_filter(v_sub, sigma / s, mode="nearest")
    bg_sub = num / np.maximum(den, 1e-6)
    H, W = arr.shape
    bg = ndi.zoom(bg_sub, (H / bg_sub.shape[0], W / bg_sub.shape[1]), order=1)
    return bg[:H, :W]


def _robust_z_on_footprint(arr2d: np.ndarray, fp: np.ndarray,
                           *, local_detrend_sigma: float = 30.0) -> np.ndarray:
    """Subtract 3 km regional background mean and scale by footprint MAD."""
    x = np.asarray(arr2d, dtype=np.float32)
    valid = fp & np.isfinite(x)
    clean = np.where(valid, x, 0.0).astype(np.float32)
    if local_detrend_sigma > 0.0:
        if local_detrend_sigma >= 12.0:
            bg = _fast_norm_conv_large_sigma(clean, valid, local_detrend_sigma)
        else:
            masked = np.where(valid, x, np.nan).astype(np.float32)
            bg = _norm_conv(masked, local_detrend_sigma, fp)
        clean = np.where(valid & np.isfinite(bg), clean - bg, 0.0)
    vals = clean[valid]
    if vals.size == 0:
        return np.zeros(int(fp.sum()), dtype=np.float32)
    med = float(np.median(vals))
    mad = float(np.median(np.abs(vals - med))) * 1.4826
    scale = mad if mad > 1e-6 else float(np.std(vals)) + 1e-6
    z_fp = np.clip((clean[fp] - med) / scale, -8.0, 8.0).astype(np.float32)
    z_fp[~np.isfinite(z_fp)] = 0.0
    return z_fp


def _parse_float(val: str | None) -> float:
    if val is None:
        return float("nan")
    s = val.strip()
    if not s or s.lower() in {"nan", "null", "none"}:
        return float("nan")
    try:
        v = float(s)
    except ValueError:
        return float("nan")
    # Filter impossible negative / sentinel readings
    if v < -50.0 or v > 500.0:
        return float("nan")
    return v


def load_hydrothermal_and_vent_grids(
    shape: tuple[int, int],
    fp: np.ndarray,
    data_dir: Path | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Load label-free GDR-1391 thermal enthalpy & Quaternary volcanic vent grids.

    Strictly enforces ``FORBIDDEN_COLS``: ``dist_known_fault_px`` is never read
    into any feature computation.
    """
    d = Path(data_dir) if data_dir is not None else DATA_DIR
    H, W = shape
    enthalpy_grid = np.zeros((H, W), dtype=np.float32)
    high_temp_centers = np.zeros((H, W), dtype=bool)
    vent_grid = np.zeros((H, W), dtype=np.float32)

    ws_path = d / "gdr_wellspring_in_footprint.csv"
    n_ws_rows = 0
    n_thermal_cells = 0
    with ws_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames is not None
        used_cols = WELLSPRING_ALLOWED_COLS & set(reader.fieldnames)
        assert not (used_cols & FORBIDDEN_COLS), "Forbidden column in allowlist"
        for raw_row in reader:
            n_ws_rows += 1
            # Copy ONLY allowlisted columns; drop dist_known_fault_px immediately.
            row = {k: raw_row[k] for k in used_cols}
            assert "dist_known_fault_px" not in row
            r = int(float(row["row"]))
            c = int(float(row["col"]))
            if not (0 <= r < H and 0 <= c < W and fp[r, c]):
                continue
            t_meas = _parse_float(row.get("temp_c"))
            t_qtz = _parse_float(row.get("geothermquartz_c"))
            t_chal = _parse_float(row.get("geothermchalc_c"))
            t_cat = _parse_float(row.get("geothermcat_c"))
            tcls = (row.get("thermalclass") or "").strip().lower()

            scores = [0.0]
            if np.isfinite(t_meas) and t_meas > 20.0:
                scores.append(min(2.0, (t_meas - 20.0) / 60.0))
            if np.isfinite(t_qtz) and t_qtz > 70.0:
                scores.append(min(2.0, (t_qtz - 70.0) / 110.0))
            if np.isfinite(t_chal) and t_chal > 60.0:
                scores.append(min(1.8, (t_chal - 60.0) / 100.0))
            if np.isfinite(t_cat) and t_cat > 70.0:
                scores.append(min(2.0, (t_cat - 70.0) / 120.0))
            if tcls == "hot":
                scores.append(1.25)
            elif tcls == "warm":
                scores.append(0.65)
            tau = float(max(scores))
            if tau > enthalpy_grid[r, c]:
                enthalpy_grid[r, c] = tau
            if (np.isfinite(t_meas) and t_meas >= 50.0) or (np.isfinite(t_qtz) and t_qtz >= 110.0) or tcls == "hot":
                high_temp_centers[r, c] = True

    n_thermal_cells = int((enthalpy_grid > 0).sum())

    vv_path = d / "gdr_volcanic_vents_in_footprint.csv"
    n_vents = 0
    with vv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames is not None
        used_vcols = VENT_ALLOWED_COLS & set(reader.fieldnames)
        assert not (used_vcols & FORBIDDEN_COLS)
        for raw_row in reader:
            row = {k: raw_row[k] for k in used_vcols}
            assert "dist_known_fault_px" not in row
            r = int(float(row["row"]))
            c = int(float(row["col"]))
            if 0 <= r < H and 0 <= c < W and fp[r, c]:
                vent_grid[r, c] = 1.0
                n_vents += 1

    audit_info = {
        "wellspring_rows_scanned": n_ws_rows,
        "unique_thermal_anomaly_cells": n_thermal_cells,
        "high_enthalpy_center_cells": int(high_temp_centers.sum()),
        "volcanic_vent_cells": n_vents,
        "forbidden_columns_excluded": sorted(FORBIDDEN_COLS),
    }
    return enthalpy_grid, high_temp_centers, vent_grid, audit_info


@dataclass
class BaseFeatureStack:
    names: list[str]
    X_fp: np.ndarray                 # (N_fp, D) float32, locally standardized
    fp: np.ndarray                   # (H, W) bool
    fp_yx: tuple[np.ndarray, np.ndarray]
    analog_source_fp: np.ndarray     # (N_fp,) bool — Source domain D_S
    geophys_strike_rad: np.ndarray   # (H, W) float32 in [0, pi) — label-free lineament strike
    ridge_baseline_score_fp: np.ndarray  # (N_fp,) float32 — label-free H19-5-like control surface
    hydro_audit: dict


def build_base_feature_stack(
    fp: np.ndarray,
    *,
    channel_dir: Path | None = None,
    data_dir: Path | None = None,
) -> BaseFeatureStack:
    """Build the label-free locally-invariant feature stack on ``fp``."""
    cdir = Path(channel_dir) if channel_dir is not None else CHANNEL_DIR
    ddir = Path(data_dir) if data_dir is not None else DATA_DIR
    H, W = fp.shape
    N = int(fp.sum())
    fp_yx = np.nonzero(fp)

    names = list(CANDIDATE_CACHED_CHANNELS) + [
        "scarp_antislope_contrast",
        "hydro_demag_clay_coupling",
        "gdr_geotherm_conduit_1500m",
        "gdr_vent_geotherm_corridor_4000m",
    ]
    D = len(names)
    mmap_dir = cdir.parent / "round3_cache"
    mmap_dir.mkdir(parents=True, exist_ok=True)
    mmap_path = mmap_dir / "X_fp_v1.npy"
    meta_path = mmap_dir / "X_fp_v1_meta.npz"

    if mmap_path.is_file() and meta_path.is_file():
        import json as _json
        meta = np.load(meta_path, allow_pickle=False)
        X_fp = np.load(mmap_path, mmap_mode="r")
        if X_fp.shape == (N, D):
            return BaseFeatureStack(
                names=names,
                X_fp=X_fp,
                fp=fp,
                fp_yx=fp_yx,
                analog_source_fp=meta["analog_source_fp"],
                geophys_strike_rad=meta["geophys_strike_rad"],
                ridge_baseline_score_fp=meta["ridge_baseline_score_fp"],
                hydro_audit=_json.loads(str(meta["hydro_audit_json"])),
            )

    X_fp_w = np.lib.format.open_memmap(mmap_path, mode="w+", dtype=np.float32, shape=(N, D))

    # Keep small footprint vectors needed for the 4 composite physics features
    keep_fp: dict[str, np.ndarray] = {}
    keep_2d_coh = np.zeros((H, W), dtype=np.float32)

    for idx, cname in enumerate(CANDIDATE_CACHED_CHANNELS):
        arr = np.load(cdir / f"{cname}.npy", mmap_mode="r")
        # Channels that already measure local sharpness still benefit from 3 km
        # regional-amplitude centering so basin-vs-range amplitude drift cancels.
        z_fp = _robust_z_on_footprint(arr, fp, local_detrend_sigma=30.0)
        X_fp_w[:, idx] = z_fp
        if cname in {
            "lid_upface_max", "lid_cross_max", "rtp_laps2", "cond_surf_gms2",
            "iso_grav_anom_hg", "ext_TMI_up150_gm2",
            "det_elev_ridge", "det_elev_slope", "tmi_hg", "tc",
        }:
            keep_fp[cname] = z_fp
        if cname in {"iso_grav_anom_coh", "rtp_coh"}:
            a2 = np.asarray(arr, dtype=np.float32)
            keep_2d_coh = np.maximum(keep_2d_coh, np.where(np.isfinite(a2) & fp, np.clip(a2, 0.0, 1.0), 0.0))
        elif cname == "lid_coh100":
            a2 = np.asarray(arr, dtype=np.float32) / 255.0
            keep_2d_coh = np.maximum(keep_2d_coh, np.where(np.isfinite(a2) & fp, np.clip(a2, 0.0, 1.0), 0.0))

    # Label-free geophysical strike orientation (for optional strike alignment with visible strands)
    grav = np.load(cdir / "iso_grav_anom.npy", mmap_mode="r")
    grav_clean = np.where(fp & np.isfinite(grav), np.asarray(grav, np.float32), 0.0)
    gy = ndi.gaussian_filter(grav_clean, sigma=2.0, order=(1, 0))
    gx = ndi.gaussian_filter(grav_clean, sigma=2.0, order=(0, 1))
    # Fault strike is perpendicular to horizontal density gradient: (-gy, gx)
    geophys_strike_rad = np.mod(np.arctan2(-gx, gy), np.pi).astype(np.float32)
    del grav, grav_clean, gy, gx

    # 4 new physics-grounded hydrothermal / scarp differential composites
    base_i = len(CANDIDATE_CACHED_CHANNELS)
    # (1) 1 m LiDAR tectonic antislope vs fluvial channel-bank contrast
    antislope = keep_fp["lid_upface_max"] - 0.5 * keep_fp["lid_cross_max"]
    X_fp_w[:, base_i + 0] = np.clip(antislope, -8.0, 8.0)

    # (2) Hydrothermal magnetite-destruction trough (+rtp_laps2) x clay/brine conductivity edge
    demag_clay = np.maximum(0.0, keep_fp["rtp_laps2"]) * np.maximum(0.0, keep_fp["cond_surf_gms2"])
    m_dc = float(np.median(demag_clay))
    s_dc = float(np.std(demag_clay)) + 1e-6
    X_fp_w[:, base_i + 1] = np.clip((demag_clay - m_dc) / s_dc, -8.0, 8.0)

    # (3) & (4) GDR-1391 geothermometer + Quaternary volcanic vent structural conduits
    enthalpy_grid, high_temp_centers, vent_grid, hydro_audit = load_hydrothermal_and_vent_grids(
        (H, W), fp, data_dir=ddir
    )
    plume_1500m = ndi.gaussian_filter(enthalpy_grid, sigma=15.0)
    conduit_1500m = plume_1500m * (0.25 + keep_2d_coh)
    X_fp_w[:, base_i + 2] = _robust_z_on_footprint(conduit_1500m, fp, local_detrend_sigma=0.0)

    plume_4000m = ndi.gaussian_filter(enthalpy_grid, sigma=40.0) + 1.5 * ndi.gaussian_filter(vent_grid, sigma=30.0)
    deep_edge_fp = np.maximum(0.0, keep_fp["iso_grav_anom_hg"]) + np.maximum(0.0, keep_fp["ext_TMI_up150_gm2"])
    deep_edge_2d = np.zeros((H, W), dtype=np.float32)
    deep_edge_2d[fp_yx] = deep_edge_fp
    corridor_4000m = plume_4000m * (0.25 + deep_edge_2d)
    X_fp_w[:, base_i + 3] = _robust_z_on_footprint(corridor_4000m, fp, local_detrend_sigma=0.0)
    X_fp_w.flush()
    del X_fp_w

    # Label-free H19-5-like multi-physics ridge baseline score (for Control B0)
    ridge_score_fp = (
        0.35 * keep_fp["det_elev_ridge"]
        + 0.20 * keep_fp["det_elev_slope"]
        + 0.20 * keep_fp["iso_grav_anom_hg"]
        + 0.15 * keep_fp["tmi_hg"]
        + 0.10 * keep_fp["tc"]
    ).astype(np.float32)

    # Named Source Domain D_S: Dixie Valley + Brady + Desert Peak + 8 km high-enthalpy centers
    amasks = build_analog_masks(fp)
    d_ht = ndi.distance_transform_edt(~high_temp_centers)
    source_2d = (amasks.analog | (d_ht <= 80.0)) & fp
    analog_source_fp = source_2d[fp]
    hydro_audit["source_domain_fraction_of_footprint"] = float(analog_source_fp.mean())
    hydro_audit["source_domain_pixels"] = int(analog_source_fp.sum())

    import json as _json
    np.savez(
        meta_path,
        analog_source_fp=analog_source_fp,
        geophys_strike_rad=geophys_strike_rad,
        ridge_baseline_score_fp=ridge_score_fp,
        hydro_audit_json=_json.dumps(hydro_audit),
    )
    X_fp = np.load(mmap_path, mmap_mode="r")

    return BaseFeatureStack(
        names=names,
        X_fp=X_fp,
        fp=fp,
        fp_yx=fp_yx,
        analog_source_fp=analog_source_fp,
        geophys_strike_rad=geophys_strike_rad,
        ridge_baseline_score_fp=ridge_score_fp,
        hydro_audit=hydro_audit,
    )


VISIBLE_NET_NAMES: tuple[str, ...] = (
    "vis_dist_log",
    "vis_tip_aniso_cone",
    "vis_stepover_bridge",
    "vis_strike_geophys_align",
)


def compute_visible_network_features(
    visible_mask: np.ndarray,
    fp: np.ndarray,
    geophys_strike_rad: np.ndarray,
) -> np.ndarray:
    """Compute 4 continuation features strictly from ``visible_mask`` (shape ``(N_fp, 4)``).

    Never accesses ``catalogue`` or ``truth``; caller passes only the fold-safe
    visible fault mask (or internal sub-fold ``V_ctx`` during LOQO training).
    """
    V = np.asarray(visible_mask, dtype=bool) & fp
    H, W = fp.shape
    N = int(fp.sum())
    out = np.zeros((N, 4), dtype=np.float32)
    if not V.any():
        return out

    # 1. Log distance to visible strands + nearest-strand indices
    d_vis, idx = ndi.distance_transform_edt(~V, return_indices=True)
    d_clip = np.minimum(d_vis[fp], 150.0).astype(np.float32)
    out[:, 0] = (np.log1p(d_clip) - 3.2) / 1.2

    # 2. Anisotropic tip-propagation cone from degree-1 endpoints of V
    nb_count = ndi.convolve(V.astype(np.uint8), np.ones((3, 3), dtype=np.uint8), mode="constant")
    tips = V & (nb_count <= 2)
    # Local smoothed trace mass gives the inward direction toward the existing strand;
    # negative gradient points outward past the tip into the unmapped continuation gap!
    v_smooth = ndi.gaussian_filter(V.astype(np.float32), sigma=3.0)
    inward_y = ndi.sobel(v_smooth, axis=0)
    inward_x = ndi.sobel(v_smooth, axis=1)
    norm_in = np.hypot(inward_y, inward_x) + 1e-6
    out_uy = np.where(tips, -inward_y / norm_in, 0.0).astype(np.float32)
    out_ux = np.where(tips, -inward_x / norm_in, 0.0).astype(np.float32)
    tip_f = tips.astype(np.float32)

    # Steered offset plume at 6 px (600 m), 14 px (1.4 km), and 24 px (2.4 km) ahead of tips
    ty, tx = np.nonzero(tips)
    tip_cone = np.zeros((H, W), dtype=np.float32)
    if ty.size > 0:
        uy_t = out_uy[ty, tx]
        ux_t = out_ux[ty, tx]
        for step_px, weight in ((5.0, 1.0), (11.0, 0.8), (18.0, 0.55), (26.0, 0.35)):
            py = np.clip(np.rint(ty + step_px * uy_t).astype(np.int32), 0, H - 1)
            px = np.clip(np.rint(tx + step_px * ux_t).astype(np.int32), 0, W - 1)
            np.add.at(tip_cone, (py, px), weight)
        # Also include weak symmetric tip proximity for curved splays
        tip_cone += 0.35 * tip_f
        tip_cone = ndi.gaussian_filter(tip_cone, sigma=4.5)
    out[:, 1] = np.clip(tip_cone[fp] * 6.0, 0.0, 8.0)

    # 3. Voronoi inter-component medial stepover / gap bridge
    comp_v, _ = ndi.label(V, structure=np.ones((3, 3), dtype=np.uint8))
    nearest_comp = comp_v[idx[0], idx[1]]
    bridge = np.zeros((H, W), dtype=bool)
    bridge[:-1, :] |= nearest_comp[:-1, :] != nearest_comp[1:, :]
    bridge[:, :-1] |= nearest_comp[:, :-1] != nearest_comp[:, 1:]
    bridge_weighted = np.where(bridge & (d_vis <= 30.0), np.exp(-d_vis / 12.0), 0.0).astype(np.float32)
    bridge_smooth = ndi.gaussian_filter(bridge_weighted, sigma=3.0)
    out[:, 2] = np.clip(bridge_smooth[fp] * 10.0, 0.0, 8.0)

    # 4. Along-strike alignment between nearest visible strand and local geophysical strike
    vy = ndi.gaussian_filter(V.astype(np.float32), sigma=2.0, order=(1, 0))
    vx = ndi.gaussian_filter(V.astype(np.float32), sigma=2.0, order=(0, 1))
    vis_strike = np.mod(np.arctan2(-vx, vy), np.pi)
    near_strike = vis_strike[idx[0], idx[1]]
    align = np.cos(2.0 * (near_strike - geophys_strike_rad)) * np.exp(-d_vis / 25.0)
    out[:, 3] = align[fp].astype(np.float32)

    return out


def screen_domain_divergence_and_ben_david(
    base: BaseFeatureStack,
    catalogue_for_source_risk: np.ndarray,
    *,
    max_abs_auc_shift: float = 0.20,
    seed: int = 20261025,
) -> tuple[np.ndarray, dict]:
    """Screen features for spatial-block source-target shift & compute Ben-David diagnostics.

    Uses 20 km (200 px) spatial checkerboard blocks so source-vs-target shift is
    measured out-of-block rather than on adjacent pixels. Also computes exact
    finite-VC linear halfspace empirical ``d_{H Delta H}`` on spatially blocked
    unlabeled samples (Ben-David et al., 2010, Lemma 2 & Theorem 2).
    """
    rng = np.random.default_rng(seed)
    yy, xx = base.fp_yx
    block_parity = ((yy // 200) + (xx // 200)) % 2
    src = base.analog_source_fp

    # Subsample balanced unlabeled pixels in even (train) and odd (test) 20 km blocks
    def _sample_idx(mask: np.ndarray, k: int) -> np.ndarray:
        idx = np.flatnonzero(mask)
        if idx.size <= k:
            return idx
        return rng.choice(idx, size=k, replace=False)

    tr_s = _sample_idx(src & (block_parity == 0), 15_000)
    tr_t = _sample_idx((~src) & (block_parity == 0), 15_000)
    te_s = _sample_idx(src & (block_parity == 1), 15_000)
    te_t = _sample_idx((~src) & (block_parity == 1), 15_000)

    te_idx = np.concatenate([te_s, te_t])
    y_dom_te = np.concatenate([np.ones(te_s.size, np.int8), np.zeros(te_t.size, np.int8)])

    per_feature = []
    keep_mask = np.zeros(len(base.names), dtype=bool)
    for j, name in enumerate(base.names):
        vals = base.X_fp[te_idx, j]
        auc = float(roc_auc_score(y_dom_te, vals)) if np.std(vals) > 1e-8 else 0.5
        shift = abs(auc - 0.5)
        passed = shift <= max_abs_auc_shift
        keep_mask[j] = passed
        per_feature.append({
            "feature": name,
            "domain_auc_source_vs_target": round(auc, 5),
            "abs_auc_shift_from_0_5": round(shift, 5),
            "kept": bool(passed),
        })

    kept_idx = np.flatnonzero(keep_mask)
    tr_idx = np.concatenate([tr_s, tr_t])
    y_dom_tr = np.concatenate([np.ones(tr_s.size, np.int8), np.zeros(tr_t.size, np.int8)])

    # Joint linear domain discriminator on kept features (Lemma 2 proxy for linear HDeltaH)
    clf_dom = LogisticRegression(C=0.25, max_iter=300, solver="lbfgs")
    clf_dom.fit(base.X_fp[tr_idx][:, kept_idx], y_dom_tr)
    p_dom_te = clf_dom.predict_proba(base.X_fp[te_idx][:, kept_idx])[:, 1]
    joint_linear_auc = float(roc_auc_score(y_dom_te, p_dom_te))
    pred_dom_te = (p_dom_te >= 0.5).astype(np.int8)
    # Empirical symmetric-difference divergence d_{H Delta H} = 2 * (1 - 2 * err(domain_clf))
    dom_err = float(np.mean(pred_dom_te != y_dom_te))
    emp_d_h_delta_h = float(max(0.0, 2.0 * (1.0 - 2.0 * dom_err)))

    # Empirical source risk of linear halfspace on source-domain fault classification
    cat_fp = np.asarray(catalogue_for_source_risk, dtype=bool)[base.fp]
    src_pos = _sample_idx(src & cat_fp & (block_parity == 0), 4_000)
    src_neg = _sample_idx(src & (~cat_fp) & (block_parity == 0), 4_000)
    src_te_pos = _sample_idx(src & cat_fp & (block_parity == 1), 2_000)
    src_te_neg = _sample_idx(src & (~cat_fp) & (block_parity == 1), 2_000)
    s_tr = np.concatenate([src_pos, src_neg])
    s_y_tr = np.concatenate([np.ones(src_pos.size, np.int8), np.zeros(src_neg.size, np.int8)])
    s_te = np.concatenate([src_te_pos, src_te_neg])
    s_y_te = np.concatenate([np.ones(src_te_pos.size, np.int8), np.zeros(src_te_neg.size, np.int8)])

    clf_src = LogisticRegression(C=0.25, max_iter=300, solver="lbfgs")
    clf_src.fit(base.X_fp[s_tr][:, kept_idx], s_y_tr)
    src_emp_err = float(np.mean(clf_src.predict(base.X_fp[s_te][:, kept_idx]) != s_y_te))

    vc_dim = int(kept_idx.size + 1)
    m_unlabeled = int(min(te_s.size, te_t.size))
    bounds_by_lambda = {}
    for lam_val in (0.01, 0.05, 0.10):
        bounds_by_lambda[f"lambda_{lam_val:.2f}"] = ben_david_theorem2_bound(
            eps_source=src_emp_err,
            d_hat_hdh=emp_d_h_delta_h,
            lambda_joint=lam_val,
            vc_dim=vc_dim,
            n_unlabeled_per_domain=m_unlabeled,
            delta=0.05,
        )

    report = {
        "total_candidate_base_features": len(base.names),
        "kept_base_features": int(kept_idx.size),
        "dropped_base_features": [p["feature"] for p in per_feature if not p["kept"]],
        "max_abs_auc_shift_threshold": max_abs_auc_shift,
        "historical_h33f_raw_domain_auc": 0.9169,
        "invariant_representation_linear_domain_auc": round(joint_linear_auc, 5),
        "empirical_domain_error_heldout_20km_blocks": round(dom_err, 5),
        "empirical_d_H_Delta_H_linear_halfspace": round(emp_d_h_delta_h, 5),
        "linear_halfspace_vc_dim": vc_dim,
        "heldout_source_empirical_01_error": round(src_emp_err, 5),
        "ben_david_theorem2_upper_bound_sensitivity": bounds_by_lambda,
        "lambda_disclosure": (
            "Joint ideal-hypothesis error lambda is unobservable without complete independent "
            "target truth; bounds are reported as a formal sensitivity curve over assumed lambda."
        ),
        "per_feature": per_feature,
    }
    return kept_idx, report


def run_feature_leakage_canaries(
    base: BaseFeatureStack,
    folds_list: list[list[dict]],
    *,
    max_allowed_auc: float = 0.90,
    seed: int = 20261025,
) -> dict:
    """Rule 4 standalone single-feature holdout leakage canary across all features.

    Evaluates every base feature AND every visible-network feature individually on
    withheld fault segments vs active off-catalogue background inside the buffered
    quadrant holdout. Any feature with ``max(AUC, 1 - AUC) > max_allowed_auc`` fails.
    """
    rng = np.random.default_rng(seed)
    pos_chunks_base, neg_chunks_base = [], []
    pos_chunks_net, neg_chunks_net = [], []

    for folds in folds_list:
        vis = folds[0]["visible"]
        X_net = compute_visible_network_features(vis, base.fp, base.geophys_strike_rad)
        for fold in folds:
            active_2d = fold["region"] & base.fp & (~fold["masked_known"])
            truth_2d = fold["truth"] & active_2d
            neg_2d = active_2d & (~truth_2d)

            t_fp = truth_2d[base.fp]
            n_fp = neg_2d[base.fp]
            pos_idx = np.flatnonzero(t_fp)
            neg_all = np.flatnonzero(n_fp)
            neg_idx = rng.choice(neg_all, size=min(neg_all.size, max(20_000, 4 * pos_idx.size)), replace=False)

            pos_chunks_base.append(base.X_fp[pos_idx])
            neg_chunks_base.append(base.X_fp[neg_idx])
            pos_chunks_net.append(X_net[pos_idx])
            neg_chunks_net.append(X_net[neg_idx])

    Xb_pos = np.vstack(pos_chunks_base)
    Xb_neg = np.vstack(neg_chunks_base)
    yb = np.concatenate([np.ones(Xb_pos.shape[0], np.int8), np.zeros(Xb_neg.shape[0], np.int8)])
    Xb = np.vstack([Xb_pos, Xb_neg])

    Xn_pos = np.vstack(pos_chunks_net)
    Xn_neg = np.vstack(neg_chunks_net)
    Xn = np.vstack([Xn_pos, Xn_neg])

    results = []
    leakers = []
    for j, fname in enumerate(base.names):
        col = Xb[:, j]
        auc = float(roc_auc_score(yb, col)) if np.std(col) > 1e-8 else 0.5
        oriented_auc = max(auc, 1.0 - auc)
        flagged = oriented_auc > max_allowed_auc
        if flagged:
            leakers.append(fname)
        results.append({
            "feature": fname,
            "kind": "label_free_base",
            "raw_holdout_auc": round(auc, 5),
            "oriented_auc": round(oriented_auc, 5),
            "flagged_leakage": bool(flagged),
        })

    for j, fname in enumerate(VISIBLE_NET_NAMES):
        col = Xn[:, j]
        auc = float(roc_auc_score(yb, col)) if np.std(col) > 1e-8 else 0.5
        oriented_auc = max(auc, 1.0 - auc)
        flagged = oriented_auc > max_allowed_auc
        if flagged:
            leakers.append(fname)
        results.append({
            "feature": fname,
            "kind": "fold_visible_network",
            "raw_holdout_auc": round(auc, 5),
            "oriented_auc": round(oriented_auc, 5),
            "flagged_leakage": bool(flagged),
        })

    results_sorted = sorted(results, key=lambda r: -r["oriented_auc"])
    return {
        "max_allowed_auc": max_allowed_auc,
        "n_features_tested": len(results),
        "positive_samples_pooled": int(Xb_pos.shape[0]),
        "negative_samples_pooled": int(Xb_neg.shape[0]),
        "max_oriented_auc": round(float(results_sorted[0]["oriented_auc"]), 5),
        "top_feature": results_sorted[0]["feature"],
        "flagged_leakers": leakers,
        "pass": len(leakers) == 0,
        "per_feature": results_sorted,
    }


def exact_choquet_self_credit(p: np.ndarray) -> np.ndarray:
    """Exact Choquet tail-sum expectation ``E[max_{y in N_3(x)} k(d(x,y)) Y_y]`` in ``[0, 1]``.

    Evaluates the exact distribution of the discrete 6-ring triangular kernel
    maximum under independent marginal pixel probabilities ``p(y)`` in ~0.6 s on
    ``3730 x 3292`` without Jensen sum saturation (``IR-78-EMIT-JENSEN``).
    """
    from vendor.gems57.metric import OFF_DX, OFF_DY, OFF_K

    p_c = np.clip(np.asarray(p, np.float32), 0.0, 1.0)
    H, W = p_c.shape
    levels = sorted({round(float(k), 12) for k in OFF_K}, reverse=True)
    log1mp = np.log1p(-np.minimum(p_c, 1.0 - 1e-7)).astype(np.float32)
    cum_log_surv = np.zeros((H, W), dtype=np.float32)
    out = np.zeros((H, W), dtype=np.float32)

    for idx_l, w_cur in enumerate(levels):
        w_next = levels[idx_l + 1] if idx_l + 1 < len(levels) else 0.0
        ring_mask = np.isclose(OFF_K, w_cur, rtol=0.0, atol=1e-9)
        for dy, dx in zip(OFF_DY[ring_mask], OFF_DX[ring_mask]):
            idy, idx_x = int(dy), int(dx)
            ys0, ys1 = max(0, idy), min(H, H + idy)
            xs0, xs1 = max(0, idx_x), min(W, W + idx_x)
            cum_log_surv[ys0:ys1, xs0:xs1] += log1mp[
                max(0, -idy) : min(H, H - idy),
                max(0, -idx_x) : min(W, W - idx_x),
            ]
        prob_at_least_w = -np.expm1(cum_log_surv)
        out += np.float32(w_cur - w_next) * prob_at_least_w
    return np.clip(out, 0.0, 1.0)


def _build_internal_training_samples(
    base: BaseFeatureStack,
    kept_idx: np.ndarray,
    train_region_2d: np.ndarray,
    visible_2d: np.ndarray,
    *,
    use_visible_network: bool,
    analog_gamma: float,
    d_h_delta_h: float,
    rng: np.random.Generator,
    n_internal_splits: int = 2,
    neg_per_split: int = 50_000,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct internal pseudo-hidden whole-component training samples inside ``train_region_2d``."""
    v_tr = visible_2d & train_region_2d & base.fp
    comp, n_comp = ndi.label(v_tr, structure=np.ones((3, 3), dtype=np.uint8))
    comp_ids = np.arange(1, n_comp + 1)
    perm = rng.permutation(comp_ids)
    # Hold out 20% of V_train components per internal sub-split (matching outer
    # hide_frac=0.20 so V_ctx has the exact same 80% strand density as test V).
    splits = np.array_split(perm, 5)[:n_internal_splits]

    d_v_tr = ndi.distance_transform_edt(~v_tr)
    neg_pool_2d = train_region_2d & base.fp & (d_v_tr > 4.0)
    neg_pool_fp = np.flatnonzero(neg_pool_2d[base.fp])
    del d_v_tr, neg_pool_2d

    X_parts, y_exact_parts, w_parts = [], [], []
    analog_boost = 1.0 + analog_gamma * max(0.1, 1.0 - 0.5 * d_h_delta_h)

    for split_ids in splits:
        if split_ids.size == 0:
            continue
        pseudo_hidden = np.isin(comp, split_ids) & v_tr
        collar = ndi.distance_transform_edt(~pseudo_hidden) <= 3.0
        v_ctx = v_tr & (~collar)
        del collar
        if not pseudo_hidden.any() or not v_ctx.any():
            continue

        X_net_ctx = (
            compute_visible_network_features(v_ctx, base.fp, base.geophys_strike_rad)
            if use_visible_network else None
        )
        pos_exact_fp = np.flatnonzero(pseudo_hidden[base.fp])
        n_neg = min(neg_pool_fp.size, neg_per_split)
        neg_fp = rng.choice(neg_pool_fp, size=n_neg, replace=False)

        sel_fp = np.concatenate([pos_exact_fp, neg_fp])
        Xb_sel = np.asarray(base.X_fp[sel_fp][:, kept_idx], dtype=np.float32)
        X_sel = np.hstack([Xb_sel, X_net_ctx[sel_fp]]) if X_net_ctx is not None else Xb_sel
        del X_net_ctx, Xb_sel

        y_ex = np.zeros(sel_fp.size, dtype=np.int8)
        y_ex[: pos_exact_fp.size] = 1

        is_src = base.analog_source_fp[sel_fp]
        w_sel = np.where(is_src, analog_boost, 1.0).astype(np.float32)

        X_parts.append(X_sel)
        y_exact_parts.append(y_ex)
        w_parts.append(w_sel)

    return (
        np.vstack(X_parts),
        np.concatenate(y_exact_parts),
        np.concatenate(w_parts),
    )


def _calibrate_prevalence(raw_prob: np.ndarray, target_mean_prob: float) -> np.ndarray:
    """Bayes prior-odds recalibration from subsampled training prevalence to true grid prevalence."""
    p = np.clip(np.asarray(raw_prob, dtype=np.float64), 1e-6, 1.0 - 1e-6)
    cur_mean = float(p.mean())
    if cur_mean <= 0.0 or target_mean_prob <= 0.0:
        return p.astype(np.float32)
    odds_scale = (target_mean_prob / (1.0 - target_mean_prob)) / (cur_mean / (1.0 - cur_mean))
    odds = (p / (1.0 - p)) * odds_scale
    cal = odds / (1.0 + odds)
    return np.clip(cal, 0.0, 1.0).astype(np.float32)


def fit_predict_loqo_surfaces(
    base: BaseFeatureStack,
    kept_idx: np.ndarray,
    quad: np.ndarray,
    visible_2d: np.ndarray,
    *,
    arm: str,
    d_h_delta_h: float,
    seed: int = 20261025,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit 4 Leave-One-Quadrant-Out models using ONLY ``visible_2d`` outside test quadrant ``q``.

    Returns ``(p_2d, m_self_credit_2d)``, both ``float32`` arrays in ``[0, 1]`` on
    ``(H, W)`` with ``0.0`` outside ``fp``.

    Supported arms:
    - ``"H33-R3-1"``: Domain-adapted HistGBDT + hydrothermal conduits + visible network
    - ``"H33-R3-2"``: Domain-adapted HistGBDT + hydrothermal conduits, ZERO network features
    - ``"H33-R3-3"``: Explicit finite-VC L2 LogisticHalfspace, ZERO network features
    - ``"CTRL-GBDT"``: Unadapted standard GBDT (analog_gamma=0, standard 19-band derivatives only)
    """
    H, W = base.fp.shape
    N_fp = int(base.fp.sum())
    p_fp = np.zeros(N_fp, dtype=np.float32)
    quad_fp = quad[base.fp]

    use_net = arm == "H33-R3-1"
    analog_gamma = 0.0 if arm == "CTRL-GBDT" else 1.5

    if arm == "CTRL-GBDT":
        ctrl_names = {
            "tmi_hg", "tmi_vg", "tc", "iso_grav_anom_slope", "iso_grav_anom_vg",
            "iso_grav_anom_hg", "det_elev_slope", "det_elev_gms2", "det_elev_ridge",
            "iso_grav_anom_gms2", "rtp_gms2", "depth_to_base_surf_gms2", "cond_surf_gms2",
        }
        feat_idx = np.asarray([i for i, n in enumerate(base.names) if n in ctrl_names], dtype=np.int64)
    else:
        feat_idx = kept_idx

    X_net_full = (
        compute_visible_network_features(visible_2d, base.fp, base.geophys_strike_rad)
        if use_net else None
    )
    target_p_mean = 0.0024

    for q in range(4):
        rng_q = np.random.default_rng(seed + 101 * (q + 1))
        train_region_2d = (quad != q) & base.fp
        X_tr, y_ex, w_tr = _build_internal_training_samples(
            base,
            feat_idx,
            train_region_2d,
            visible_2d,
            use_visible_network=use_net,
            analog_gamma=analog_gamma,
            d_h_delta_h=d_h_delta_h,
            rng=rng_q,
        )

        te_mask_fp = quad_fp == q
        te_idx_all = np.flatnonzero(te_mask_fp)

        if arm == "H33-R3-3":
            clf_p = LogisticRegression(C=0.25, max_iter=400, solver="lbfgs")
            clf_p.fit(X_tr, y_ex, sample_weight=w_tr)
        else:
            clf_p = HistGradientBoostingClassifier(
                max_iter=120,
                learning_rate=0.06,
                max_leaf_nodes=31,
                min_samples_leaf=80,
                l2_regularization=2.0,
                random_state=int(seed + q),
            )
            clf_p.fit(X_tr, y_ex, sample_weight=w_tr)
        del X_tr, y_ex, w_tr

        raw_p = np.empty(te_idx_all.size, dtype=np.float32)
        chunk = 200_000
        for s0 in range(0, te_idx_all.size, chunk):
            s1 = min(s0 + chunk, te_idx_all.size)
            sl_idx = te_idx_all[s0:s1]
            Xb_chunk = np.asarray(base.X_fp[sl_idx][:, feat_idx], dtype=np.float32)
            X_chunk = np.hstack([Xb_chunk, X_net_full[sl_idx]]) if X_net_full is not None else Xb_chunk
            raw_p[s0:s1] = clf_p.predict_proba(X_chunk)[:, 1].astype(np.float32)
            del Xb_chunk, X_chunk

        p_fp[te_idx_all] = _calibrate_prevalence(raw_p, target_p_mean)
        del raw_p, clf_p

    p_2d = np.zeros((H, W), dtype=np.float32)
    p_2d[base.fp_yx] = np.clip(p_fp, 0.0, 1.0)
    # Zero out visible mapped fault pixels before Choquet kernel self-credit so only
    # active off-catalogue truth probability contributes to expected self-credit!
    p_off_vis = np.where(visible_2d, 0.0, p_2d).astype(np.float32)
    m_2d = exact_choquet_self_credit(p_off_vis)
    return p_off_vis, m_2d
