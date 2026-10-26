#!/usr/bin/env python3
"""Experiment 1/3 — H-A 'tilt-gravity-lidar coherence' catalogue-gap holdout test.

Lane (single method paragraph, declared before results):
  Target faults missing from the USGS/INGENIOUS catalogue with a conjunction of
  three independent physical signatures on cached GeoDAWN/LiDAR channels only:
  (a) near-vertical potential-field contact -> tilt angle (band 6 tc) close to 0,
  (b) density/basement edge -> strong horizontal gravity gradient (band 18
  iso_grav_anom_hg), (c) preserved linear surface break -> LiDAR scarp coherence
  (lid_coh100) and step response (lid_step_max). Each channel is robustly
  z-standardised over the footprint, mapped to [0,1], and combined by product
  (a strict conjunction keeps false-positive mass low). Emission dots are placed
  only >= 2 px outside the *fold-visible* catalogue mask, thinned at 2.8 px, at a
  pre-declared sparse quantile of the score surface. No catalogue-proximate dots,
  no H19-5 surface, no matched-budget reallocation: structurally distinct from
  the H19/H27/D2.8/B2 dotted lineage and from the failed H33-6 edge-normal
  consensus (which used gradient-vector alignment plus reallocation and failed
  P1, mean DeltaDTI -0.002737).

Evaluation (holdout = hide-and-recover, spatially blocked):
  Catalogue pixels are grouped into systems (600 m grouping buffer) and split
  into 2x2 spatial folds by system centroid. Per fold: whole held-out systems
  (+6 px buffer) are hidden; every feature and mask is derived only from the
  visible catalogue; visible faults are masked pixel-exactly through the
  `known` argument; pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel)
  is summed over the four held-out folds. Screen = folds {0,1}; independent
  confirmation = folds {2,3} with the emission quantile frozen from the screen.
  A leakage canary reports stand-alone holdout AUC for each of the four channels
  (AUC > 0.90 means leakage until proven otherwise). A matched-random control
  places the same number of dots per fold at random eligible locations with the
  same 2.8 px spacing, to isolate placement information from dot count.

This is a proxy diagnostic against catalogue withheld systems (not the private
competition truth). No score is projected or claimed. All inputs are owner-mirror
hash-pinned bytes, not organizer-authenticated downloads.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from gems33 import grid as g33_grid  # noqa: E402
from gems33.candidates import rebuild_c0_from_known, h19_5_ridge  # noqa: E402
from gems33.metric import dti_binary  # noqa: E402
from gems33.thinning import dot_thin  # noqa: E402

CACHE_FEATURES = ROOT / ".cache" / "features"

CHANNELS = {
    "tc": "tc.npy",                     # band 6: tilt/total curvature (edge detector)
    "ghg": "iso_grav_anom_hg.npy",      # band 18: gravity horizontal gradient
    "coh": "lid_coh100.npy",            # LiDAR scarp coherence (linear break)
    "step": "lid_step_max.npy",         # LiDAR step response
}

BUFFER_PX = 6          # 600 m grouping buffer for catalogue systems
MASK_PX = 2.0          # emission clearance from visible catalogue (200 m)
THIN_PX = 2.8          # dot min spacing (~280 m)
SCREEN_QUANTILE = 0.995  # pre-declared sparse emission quantile (frozen at screen)
NEGATIVE_SAMPLE = 200_000  # canary negative sample size per fold
RANDOM_SEED = 20261026

FOLDS_SCREEN = (0, 1)
FOLDS_CONFIRM = (2, 3)


def robust_z(arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    v = np.asarray(arr, dtype=np.float64)
    vals = v[mask & np.isfinite(v)]
    med = float(np.median(vals))
    mad = float(np.median(np.abs(vals - med))) + 1e-9
    z = (v - med) / (1.4826 * mad)
    return np.clip(z, -8.0, 8.0).astype(np.float32)


def to_unit(z: np.ndarray, cap: float = 3.0) -> np.ndarray:
    return np.clip(z, 0.0, cap) / cap


def tilt_near_zero(z: np.ndarray, cap: float = 3.0) -> np.ndarray:
    """Tilt angle passes through ~0 over near-vertical contacts/faults."""
    return np.clip(1.0 - np.abs(z) / cap, 0.0, 1.0)


def build_score(tc, ghg, coh, step, footprint):
    z_tc = robust_z(tc, footprint)
    z_ghg = robust_z(ghg, footprint)
    z_coh = robust_z(coh, footprint)
    z_step = robust_z(step, footprint)
    score = (tilt_near_zero(z_tc) * to_unit(z_ghg) * to_unit(z_coh) * to_unit(z_step))
    score = np.where(footprint & np.isfinite(score), score, 0.0).astype(np.float32)
    return score


def random_dots(eligible: np.ndarray, count: int, spacing: float, rng, shape) -> np.ndarray:
    """Same-count random placement with the same min-spacing constraint."""
    ys, xs = np.nonzero(eligible)
    if count == 0 or ys.size == 0:
        return np.zeros(shape, dtype=bool)
    order = rng.permutation(ys.size)
    take = order[: min(ys.size, max(count * 50, count))]
    cand = np.stack([ys[take], xs[take]], axis=1)
    offsets = [
        (dy, dx)
        for dy in range(-int(math.ceil(spacing)), int(math.ceil(spacing)) + 1)
        for dx in range(-int(math.ceil(spacing)), int(math.ceil(spacing)) + 1)
        if dy * dy + dx * dx < spacing * spacing
    ]
    blocked = np.zeros(shape, dtype=bool)
    kept = np.zeros(shape, dtype=bool)
    n = 0
    for y, x in cand:
        if blocked[y, x]:
            continue
        kept[y, x] = True
        n += 1
        if n >= count:
            break
        r0, r1 = max(0, y - int(math.ceil(spacing))), min(shape[0], y + int(math.ceil(spacing)) + 1)
        c0, c1 = max(0, x - int(math.ceil(spacing))), min(shape[1], x + int(math.ceil(spacing)) + 1)
        for dy, dx in offsets:
            rr, cc = y + dy, x + dx
            if 0 <= rr < shape[0] and 0 <= cc < shape[1]:
                blocked[rr, cc] = True
    return kept


def fold_eval(fold_id, hidden, known, truth, score, footprint, quantile):
    d_known = distance_transform_edt(~known) if known.any() else np.full(known.shape, np.inf)
    domain = footprint & (d_known > MASK_PX)
    sdom = np.where(domain, score, np.nan)
    finite = sdom[np.isfinite(sdom)]
    thr = float(np.quantile(finite, quantile)) if finite.size else np.inf
    cand = dot_thin(domain & (score >= thr), THIN_PX)
    m = dti_binary(cand.astype(np.float32), truth, valid=footprint, known=known)
    control_arr, control_report = rebuild_c0_from_known(known, h19_5_ridge())
    control = control_arr > 0
    c = dti_binary(control.astype(np.float32), truth, valid=footprint, known=known)
    return {
        "fold": fold_id,
        "threshold": thr,
        "candidate_dots": int(cand.sum()),
        "control_dots": int(control.sum()),
        "n_truth": int(m["n_truth"]),
        "candidate": {"dti": float(m["dti"]), "TPw": float(m["TPw"]), "FPw": float(m["FPw"]),
                      "FNw": float(m["FNw"])},
        "control": {"dti": float(c["dti"]), "TPw": float(c["TPw"]), "FPw": float(c["FPw"]),
                    "FNw": float(c["FNw"])},
        "delta_dti": float(m["dti"] - c["dti"]),
        "control_report": control_report,
    }


def canary_auc(truth, known, footprint, score_fields, rng):
    """Stand-alone holdout AUC per channel: positives = hidden truth pixels."""
    d_truth = distance_transform_edt(~truth) if truth.any() else np.full(truth.shape, np.inf)
    neg_domain = footprint & ~known & (d_truth > 3.0)
    pos_ys, pos_xs = np.nonzero(truth)
    neg_ys, neg_xs = np.nonzero(neg_domain)
    out = {}
    for name, field in score_fields.items():
        if pos_ys.size == 0 or neg_ys.size == 0:
            out[name] = None
            continue
        n_pos = pos_ys.size
        n_neg = min(neg_ys.size, NEGATIVE_SAMPLE)
        pick = rng.choice(neg_ys.size, size=n_neg, replace=False)
        x_pos = field[pos_ys, pos_xs]
        x_neg = field[neg_ys[pick], neg_xs[pick]]
        y = np.concatenate([np.ones(n_pos), np.zeros(n_neg)])
        x = np.concatenate([x_pos, x_neg])
        try:
            auc = float(roc_auc_score(y, x))
        except ValueError:
            auc = None
        out[name] = {"auc": auc, "n_pos": int(n_pos), "n_neg": int(n_neg)}
    return out


def main() -> int:
    t0 = time.time()
    footprint, grid = g33_grid.load_template()
    catalogue = g33_grid.load_catalogue()
    print(f"grid {grid.width}x{grid.height} footprint={int(footprint.sum()):,} "
          f"catalogue={int(catalogue.sum()):,}", flush=True)

    tc = np.load(CACHE_FEATURES / CHANNELS["tc"])
    ghg = np.load(CACHE_FEATURES / CHANNELS["ghg"])
    coh = np.load(CACHE_FEATURES / CHANNELS["coh"])
    step = np.load(CACHE_FEATURES / CHANNELS["step"])
    for name, arr in (("tc", tc), ("ghg", ghg), ("coh", coh), ("step", step)):
        if arr.shape != footprint.shape:
            raise SystemExit(f"channel {name} shape {arr.shape} != footprint {footprint.shape}")
    score = build_score(tc, ghg, coh, step, footprint)
    print(f"score field built: positive cells={int((score > 0).sum()):,} "
          f"max={float(score.max()):.4f}", flush=True)

    systems = g33_grid.catalogue_systems(catalogue, buffer_px=BUFFER_PX)
    masks = g33_grid.fold_masks(systems, n_folds=4)
    n_systems = int(np.unique(systems[systems > 0]).size)
    print(f"catalogue systems={n_systems}; folds={[int(m.sum()) for m in masks]}", flush=True)

    rng = np.random.default_rng(RANDOM_SEED)
    results = {"screen": [], "confirmation": []}
    for phase, fold_ids in (("screen", FOLDS_SCREEN), ("confirmation", FOLDS_CONFIRM)):
        for fid in fold_ids:
            hidden = np.asarray(masks[fid], dtype=bool) & footprint
            grown = binary_dilation(hidden, structure=np.ones((2 * BUFFER_PX + 1, 2 * BUFFER_PX + 1), bool))
            known = catalogue & ~grown
            truth = hidden & ~known
            res = fold_eval(fid, hidden, known, truth, score, footprint, SCREEN_QUANTILE)
            # matched-random control (same dot count, random eligible locations)
            d_known = distance_transform_edt(~known) if known.any() else np.full(known.shape, np.inf)
            eligible = footprint & ~known & (d_known > MASK_PX)
            rand = random_dots(eligible, res["candidate_dots"], THIN_PX, rng, footprint.shape)
            r = dti_binary(rand.astype(np.float32), truth, valid=footprint, known=known)
            res["matched_random"] = {
                "dots": int(rand.sum()), "dti": float(r["dti"]),
                "TPw": float(r["TPw"]), "FPw": float(r["FPw"]), "FNw": float(r["FNw"]),
                "delta_dti": float(r["dti"]) - float(res["control"]["dti"]),
            }
            res["delta_vs_random"] = float(res["candidate"]["dti"]) - float(r["dti"])
            results[phase].append(res)
            print(f"[{phase}] fold {fid}: truth={res['n_truth']:,} cand_dots={res['candidate_dots']:,} "
                  f"cand_DTI={res['candidate']['dti']:.5f} ctrl_DTI={res['control']['dti']:.5f} "
                  f"dDTI={res['delta_dti']:+.5f} rand_DTI={res['matched_random']['dti']:.5f} "
                  f"dDTI_vs_rand={res['delta_vs_random']:+.5f}", flush=True)

    # leakage canary per channel (screen folds only, to keep canary independent of confirmation)
    canary = []
    for fid in FOLDS_SCREEN:
        hidden = np.asarray(masks[fid], dtype=bool) & footprint
        grown = binary_dilation(hidden, structure=np.ones((2 * BUFFER_PX + 1, 2 * BUFFER_PX + 1), bool))
        known = catalogue & ~grown
        truth = hidden & ~known
        fields = {"tc_z": robust_z(tc, footprint), "ghg_z": robust_z(ghg, footprint),
                  "coh_z": robust_z(coh, footprint), "step_z": robust_z(step, footprint)}
        canary.append({"fold": int(fid), "auc": canary_auc(truth, known, footprint, fields, rng)})
    leak_flag = any(
        entry["auc"][name]["auc"] is not None and entry["auc"][name]["auc"] > 0.90
        for entry in canary for name in entry["auc"]
    )
    print(f"leakage canary: max AUC above 0.90? {leak_flag}", flush=True)

    # pooled DTI (sum weights over folds) for screen and confirmation
    def pooled(phase_rows):
        tp = sum(row["candidate"]["TPw"] for row in phase_rows)
        fp = sum(row["candidate"]["FPw"] for row in phase_rows)
        fn = sum(row["candidate"]["FNw"] for row in phase_rows)
        n_truth = sum(row["n_truth"] for row in phase_rows)
        c_tp = sum(row["control"]["TPw"] for row in phase_rows)
        c_fp = sum(row["control"]["FPw"] for row in phase_rows)
        c_fn = sum(row["control"]["FNw"] for row in phase_rows)
        c_n = sum(row["n_truth"] for row in phase_rows)
        from gems33.metric import ALPHA, BETA, EPS
        dti_c = tp / (tp + ALPHA * fp + BETA * fn + EPS)
        dti_ctrl = c_tp / (c_tp + ALPHA * c_fp + BETA * c_fn + EPS)
        folds = [row["delta_dti"] for row in phase_rows]
        mean_d = float(np.mean(folds)) if folds else None
        if folds and len(folds) > 1:
            sd = float(np.std(folds, ddof=1))
            se = sd / math.sqrt(len(folds))
            tcrit = 3.182  # two-sided 95% Student-t, df=3
            ci = [mean_d - tcrit * se, mean_d + tcrit * se]
        else:
            ci = None
        return {
            "n_folds": len(phase_rows),
            "withheld_positives": int(n_truth),
            "candidate_pooled_dti": float(dti_c),
            "control_pooled_dti": float(dti_ctrl),
            "pooled_delta_dti": float(dti_c - dti_ctrl),
            "mean_fold_delta_dti": mean_d,
            "positive_folds": int(sum(d > 0 for d in folds)),
            "fold_deltas": [float(d) for d in folds],
            "descriptive_t95_ci_df3": ci,
            "candidate_components": {"TPw": float(tp), "FPw": float(fp), "FNw": float(fn)},
            "control_components": {"TPw": float(c_tp), "FPw": float(c_fp), "FNw": float(c_fn)},
        }

    report = {
        "schema": 1,
        "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": 1,
        "hypothesis_id": "G33-HA-tilt-gravity-lidar-coherence",
        "lane": "tilt(gravity)+LiDAR-coherence conjunction, sparse off-catalogue dots; "
                "distinct from dotted-catalogue lineage and H33-6 edge-normal consensus",
        "inputs": {
            "training_features_tif_sha256": hashlib.sha256(
                (ROOT / "data" / "training_features.tif").read_bytes()).hexdigest(),
            "labels_tif_sha256": hashlib.sha256(
                (ROOT / "data" / "labels.tif").read_bytes()).hexdigest(),
            "channels": CHANNELS,
        },
        "grid": {"crs": grid.crs, "width": grid.width, "height": grid.height,
                 "footprint_cells": int(footprint.sum()), "pixel_m": 100},
        "protocol": {
            "catalogue_system_buffer_px": BUFFER_PX,
            "emission_clearance_px": MASK_PX,
            "dot_thin_px": THIN_PX,
            "screen_quantile": SCREEN_QUANTILE,
            "alpha": 0.2, "beta": 0.8, "kernel": "triangular", "radius_m": 300,
            "screen_folds": list(FOLDS_SCREEN),
            "confirmation_folds": list(FOLDS_CONFIRM),
            "catalogue_features_visible_only": True,
            "visible_faults_masked_pixel_exactly": True,
        },
        "screen": results["screen"],
        "confirmation": results["confirmation"],
        "pooled_screen": pooled(results["screen"]),
        "pooled_confirmation": pooled(results["confirmation"]),
        "leakage_canary": canary,
        "leakage_canary_flag_auc_gt_0_90": bool(leak_flag),
        "runtime_seconds": round(time.time() - t0, 1),
    }
    out_path = ROOT / "evidence" / "g33_tilt_gravity_lidar_holdout.json"
    out_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    ps, pc = report["pooled_screen"], report["pooled_confirmation"]
    print(f"POOLED SCREEN:  cand_DTI={ps['candidate_pooled_dti']:.5f} ctrl_DTI={ps['control_pooled_dti']:.5f} "
          f"dDTI={ps['pooled_delta_dti']:+.5f} folds_pos={ps['positive_folds']}/{ps['n_folds']}")
    print(f"POOLED CONFIRM: cand_DTI={pc['candidate_pooled_dti']:.5f} ctrl_DTI={pc['control_pooled_dti']:.5f} "
          f"dDTI={pc['pooled_delta_dti']:+.5f} folds_pos={pc['positive_folds']}/{pc['n_folds']}")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
