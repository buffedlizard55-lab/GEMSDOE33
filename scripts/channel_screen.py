#!/usr/bin/env python3
"""Exploratory per-channel ranking against owner-mirrored SGMC map faults.

This computes descriptive pixel-level ROC AUCs for the public State Geologic Map Compilation (SGMC)
rasters versus a spatially distant background sample. SGMC map traces are not the competition's
private, expert-mapped new faults and include older/bedrock structures. Spatial pixels are
correlated; this screen has no independent blocked split, no confidence intervals, and no DTI
interpretation. It must not be used to license transfer, claim a candidate win, or approve a weekly
submission slot. See ``IR-33-RAD-01`` and ``IR-33-SGMC-01``.

The earlier report was generated with an inconsistent hand-coded tie-rank AUC routine and an older
feature schema. It has been moved to ``archive/withdrawn_first_pass/evidence`` and is not reused.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33 import features, grid  # noqa: E402

N_BACKGROUND = 100_000
SEED = 7


def auc(pos: np.ndarray, bg: np.ndarray) -> float:
    """Tie-correct descriptive AUC via scikit-learn, with per-channel finite filtering."""
    from sklearn.metrics import roc_auc_score

    pos = np.asarray(pos, dtype=np.float64)
    bg = np.asarray(bg, dtype=np.float64)
    pos = pos[np.isfinite(pos)]
    bg = bg[np.isfinite(bg)]
    if not pos.size or not bg.size:
        return float("nan")
    labels = np.concatenate((np.ones(pos.size, dtype=np.uint8), np.zeros(bg.size, dtype=np.uint8)))
    values = np.concatenate((pos, bg))
    return float(roc_auc_score(labels, values))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "evidence" / "sgmc_channel_screen_exploratory.json")
    parser.add_argument("--background", type=int, default=N_BACKGROUND)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    if args.background <= 0:
        parser.error("--background must be positive")

    started = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    sgmc, _ = grid.read_raster("derived_sgmc_faults_100m_u8.tif")
    sgmc = (sgmc > 0) & footprint
    catalogue = labels & footprint
    sgmc_off_catalogue = sgmc & ~catalogue
    exclusion = binary_dilation(catalogue | sgmc, iterations=3,
                                structure=np.ones((3, 3), dtype=bool))
    background_mask = footprint & ~exclusion
    pool = np.flatnonzero(background_mask.reshape(-1))
    rng = np.random.default_rng(args.seed)
    pick = rng.choice(pool, size=min(args.background, pool.size), replace=False)
    bg_rows, bg_cols = np.unravel_index(pick, footprint.shape)

    results = []
    names = features.channel_names()
    pos_mask = sgmc_off_catalogue
    for i, name in enumerate(names):
        arr = np.load(features.CACHE_FEATURES / f"{name}.npy", mmap_mode="r")
        positive = np.asarray(arr[pos_mask])
        background = np.asarray(arr[bg_rows, bg_cols])
        auc_value = auc(positive, background)
        results.append({
            "channel": name,
            "auc_sgmc_off_catalogue_vs_sampled_background": auc_value if np.isfinite(auc_value) else None,
            "n_positive_finite": int(np.isfinite(positive).sum()),
            "n_background_finite": int(np.isfinite(background).sum()),
        })
        if (i + 1) % 25 == 0:
            print(f"screened {i + 1}/{len(names)} channels", flush=True)

    results.sort(key=lambda row: (
        row["auc_sgmc_off_catalogue_vs_sampled_background"] is None,
        -(row["auc_sgmc_off_catalogue_vs_sampled_background"] or 0.0),
    ))
    report = {
        "schema": 2,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "EXPLORATORY_ONLY_NOT_PROMOTION_EVIDENCE",
        "evidence_class": "computed from owner-mirror rasters; not organizer-authenticated",
        "label_proxy": "owner-mirrored SGMC bedrock/geologic-map faults outside the owner-mirrored catalogue",
        "background": {
            "sampling": "uniform random footprint cells after 3-pixel dilation of catalogue or SGMC traces",
            "pool_cells": int(background_mask.sum()),
            "sampled_cells": int(pick.size),
            "seed": int(args.seed),
        },
        "counts": {
            "template_footprint_cells": int(footprint.sum()),
            "catalogue_cells": int(catalogue.sum()),
            "sgmc_off_catalogue_cells": int(sgmc_off_catalogue.sum()),
        },
        "metric": "descriptive pixel-level ROC AUC; computed with sklearn roc_auc_score tie handling",
        "limitations": [
            "SGMC traces are not the competition's private expert-mapped new-fault labels and include older/bedrock structures.",
            "Spatial pixels and fault traces are autocorrelated; the sampled background does not make this an independent test.",
            "No confidence intervals, DTI estimate, field transfer result, or spatially blocked confirmation is produced.",
            "No result from this screen can approve a weekly submission slot or establish private-leaderboard performance.",
        ],
        "channels": results,
        "elapsed_seconds": round(time.time() - started, 2),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote exploratory report: {args.out}")
    print("status: EXPLORATORY_ONLY_NOT_PROMOTION_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
