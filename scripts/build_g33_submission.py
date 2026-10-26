#!/usr/bin/env python3
"""Experiment 3/3 — build the unique GEMSDOE33 submission GeoTIFF package.

Candidate: G33-HA "tilt-gravity-lidar coherence" (same recipe as Experiment 1,
emission quantile 0.995 frozen from the holdout screen), built on the full
catalogue-visible grid. This is the deliverable unique TIF: it is
format-valid (single-band float32, EPSG:32611, 3730x3292, 100 m, exact template
geotransform, finite [0,1] in footprint, NaN outside) and is screened for
lane duplication against all 12 pinned focus-site registry rasters
(Spearman rho <= 0.90 AND <= 70% of candidate dots within 3 px of any one
registry raster).

STATUS: the catalogue-proxy holdout gate FAILED (pooled dDTI -0.0907, 0/4 folds
positive; see evidence/g33_tilt_gravity_lidar_holdout.json). This TIFF is
therefore a research/format artifact and is NOT cleared for a competition slot.
It is published so the status is obvious: OK to download for inspection, NOT OK
to submit until a fresh candidate passes the holdout gate and an organizer
receipt exists. No DrivenData upload is made from this workspace.

Inputs are hash-pinned owner-mirror bytes (not organizer-authenticated).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from gems33 import grid as g33_grid  # noqa: E402
from gems33.holdout import catalogue_systems, fold_masks  # noqa: E402
from gems33.metric import dti_binary  # noqa: E402
from gems33.thinning import dot_thin  # noqa: E402
from gemsdoe33 import grid, submission  # noqa: E402

CACHE_FEATURES = ROOT / ".cache" / "features"
DOWNLOADS = ROOT / "docs" / "downloads"
REGISTRY_DIR = ROOT / "data" / "focus_registry"
REGISTRY_MANIFEST = ROOT / "registry" / "focus_rasters_20261025.json"

NAME = "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026"
NOTE = ("GEMSDOE33 G33 tilt-gravity-lidar coherence TIFF; proxy holdout FAILED "
        "dDTI -0.0907 0/4 folds; NOT cleared to submit. id {cid}")
BUFFER_PX = 6
MASK_PX = 2.0
THIN_PX = 2.8
QUANTILE = 0.995  # frozen from Experiment 1 screen


def robust_z(arr, mask):
    v = np.asarray(arr, dtype=np.float64)
    vals = v[mask & np.isfinite(v)]
    med = float(np.median(vals))
    mad = float(np.median(np.abs(vals - med))) + 1e-9
    z = (v - med) / (1.4826 * mad)
    return np.clip(z, -8.0, 8.0).astype(np.float32)


def to_unit(z, cap=3.0):
    return np.clip(z, 0.0, cap) / cap


def tilt_near_zero(z, cap=3.0):
    return np.clip(1.0 - np.abs(z) / cap, 0.0, 1.0)


def main() -> int:
    t0 = time.time()
    footprint, g33 = g33_grid.load_template()
    catalogue = g33_grid.load_catalogue()
    print(f"grid {g33.width}x{g33.height} footprint={int(footprint.sum()):,} "
          f"catalogue={int(catalogue.sum()):,}", flush=True)

    tc = np.load(CACHE_FEATURES / "tc.npy")
    ghg = np.load(CACHE_FEATURES / "iso_grav_anom_hg.npy")
    coh = np.load(CACHE_FEATURES / "lid_coh100.npy")
    step = np.load(CACHE_FEATURES / "lid_step_max.npy")
    score = (tilt_near_zero(robust_z(tc, footprint)) *
             to_unit(robust_z(ghg, footprint)) *
             to_unit(robust_z(coh, footprint)) *
             to_unit(robust_z(step, footprint)))
    score = np.where(footprint & np.isfinite(score), score, 0.0).astype(np.float32)
    print(f"score: positive={int((score > 0).sum()):,} max={float(score.max()):.4f}", flush=True)

    # --- full-data production candidate (catalogue-visible mask only) ----------
    d_cat = distance_transform_edt(~catalogue) if catalogue.any() else np.full(catalogue.shape, np.inf)
    domain = footprint & (d_cat > MASK_PX)
    sdom = np.where(domain, score, np.nan)
    finite = sdom[np.isfinite(sdom)]
    thr = float(np.quantile(finite, QUANTILE))
    surface = domain & (score >= thr)  # pre-thinning surface for the surface check
    cand = dot_thin(surface, THIN_PX)
    print(f"threshold={thr:.6f} surface_cells={int(surface.sum()):,} candidate_dots={int(cand.sum()):,}",
          flush=True)

    # --- uniqueness vs the 12 pinned focus-site registry rasters -------------
    manifest = json.loads(REGISTRY_MANIFEST.read_text())
    comparisons = []
    surface_comparisons = []
    for entry in manifest["rasters"]:
        path = REGISTRY_DIR / Path(entry.get("dest") or entry.get("local_path")).name
        with rasterio.open(path) as src:
            reg = (src.read(1) > 0)
            reg_transform = src.transform
        if reg.shape != footprint.shape:
            raise ValueError(f"{entry['id']} shape {reg.shape} != footprint {footprint.shape}")
        if tuple(reg_transform)[:6] != tuple(g33.transform)[:6]:
            raise ValueError(f"{entry['id']} transform mismatch")
        from gemsdoe33.novelty import binary_comparison
        comp = binary_comparison(cand.astype(np.uint8), reg.astype(np.uint8), footprint)
        comp_surf = binary_comparison(surface.astype(np.uint8), reg.astype(np.uint8), footprint)
        comparisons.append({"raster_id": entry["id"], "site": entry["site"],
                            "raster_sha256": entry["sha256"], **comp})
        surface_comparisons.append({"raster_id": entry["id"], "site": entry["site"],
                                    **comp_surf})
        print(f"  vs {entry['id']} ({entry['site']}): rho={comp['spearman_rho']} "
              f"frac3px={comp['fraction_candidate_within_3px']:.4f} trigger={comp['duplicate_trigger']} | "
              f"surface frac3px={comp_surf['fraction_candidate_within_3px']:.4f}", flush=True)

    duplicate = any(c["duplicate_trigger"] for c in comparisons)
    worst_rho = max((c["spearman_rho"] for c in comparisons if c["spearman_rho"] is not None), default=None)
    worst_frac = max((c["fraction_candidate_within_3px"] for c in comparisons), default=0.0)
    worst_site = comparisons[int(np.argmax([c["fraction_candidate_within_3px"] for c in comparisons]))]["raster_id"] if comparisons else None

    # --- package the TIFs ------------------------------------------------------
    mask = cand.astype(np.uint8) & np.asarray(footprint, np.uint8)
    receipt = submission.build_package(mask, None, NAME, DOWNLOADS, NOTE)
    cid = receipt["content_id"]
    note = receipt["note"]
    assert len(note) <= 140, f"note too long: {len(note)}"

    # --- independent CLI validator re-open of the saved bytes ------------------
    import subprocess
    nan_tif = Path(receipt["nan"]["file"])
    val = subprocess.run(
        [".venv/bin/python", "scripts/validate_submission.py", "--submission", str(nan_tif),
         "--template", str(grid.DATA / "sample_submission.tif")],
        capture_output=True, text=True, cwd=ROOT)
    validation = json.loads(val.stdout)
    validation_pass = bool(validation.get("pass"))

    holdout = json.loads((ROOT / "evidence" / "g33_tilt_gravity_lidar_holdout.json").read_text())
    ps = holdout["pooled_screen"]; pc = holdout["pooled_confirmation"]

    report = {
        "schema": 1,
        "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": 3,
        "hypothesis_id": "G33-HA-tilt-gravity-lidar-coherence",
        "lane": "tilt(gravity)+LiDAR-coherence conjunction, sparse off-catalogue dots; "
                "distinct from dotted-catalogue lineage and H33-6 edge-normal consensus",
        "holdout_verdict": "NEGATIVE",
        "holdout": {
            "pooled_screen_dti": ps["candidate_pooled_dti"], "pooled_control_dti": ps["control_pooled_dti"],
            "pooled_screen_delta_dti": ps["pooled_delta_dti"], "screen_positive_folds": ps["positive_folds"],
            "pooled_confirmation_dti": pc["candidate_pooled_dti"], "pooled_confirmation_control_dti": pc["control_pooled_dti"],
            "pooled_confirmation_delta_dti": pc["pooled_delta_dti"],
            "confirmation_positive_folds": pc["positive_folds"],
            "fold_deltas": ps["fold_deltas"] + pc["fold_deltas"],
            "evidence": "evidence/g33_tilt_gravity_lidar_holdout.json",
        },
        "leakage_canary": "no channel AUC > 0.90 (no signal; not leakage)",
        "registry_check": {
            "registry_rasters": 12,
            "duplicate_trigger": bool(duplicate),
            "worst_spearman_rho": worst_rho,
            "worst_fraction_within_3px": float(worst_frac),
            "worst_raster": worst_site,
            "comparisons": comparisons,
            "surface_comparisons": surface_comparisons,
        },
        "grid": {"crs": "EPSG:32611", "width": g33.width, "height": g33.height,
                 "pixel_m": 100, "footprint_cells": int(footprint.sum())},
        "candidate": {"dots": int(cand.sum()), "threshold": thr,
                      "domain_cells": int(domain.sum())},
        "submission": {
            "name": NAME, "content_id": cid, "note": note, "note_chars": len(note),
            "recommended": receipt["nan"]["file"],
            "nan": receipt["nan"], "zeros": receipt["zeros"],
            "zip_nan": receipt["zip_nan"], "zip_zeros": receipt["zip_zeros"],
            "all_checks_pass": bool(receipt["all_checks_pass"]),
            "validator_pass": validation_pass,
            "validator": validation,
            "ok_to_download": True,
            "ok_to_submit": False,
            "verdict": "negative",
        },
        "inputs": {
            "training_features_tif_sha256": hashlib.sha256(
                (ROOT / "data" / "training_features.tif").read_bytes()).hexdigest(),
            "labels_tif_sha256": hashlib.sha256((ROOT / "data" / "labels.tif").read_bytes()).hexdigest(),
        },
        "runtime_seconds": round(time.time() - t0, 1),
    }
    out_path = ROOT / "evidence" / "g33_submission_build.json"
    out_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"candidate dots={int(cand.sum()):,} duplicate={duplicate} worst_rho={worst_rho} "
          f"worst_frac3px={worst_frac:.4f} vs {worst_site}")
    print(f"validator pass={validation_pass}")
    print(f"note ({len(note)} chars): {note}")
    print(f"primary: {Path(receipt['nan']['file']).name} sha256={receipt['nan']['sha256']}")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
