#!/usr/bin/env python3
"""Use the calibrated instrument to answer the one question it is now licensed to answer:

    what emission size maximises DTI?

The instrument (variant F: |G| = 12,226 px drawn from the catalogue with incompleteness weighting,
visible catalogue removed from the emission domain, catalogue shadow reconstructed at radius r)
reproduces the three owner-reported live returns to within +7.7 % / -4.4 % at r = 4 and to within
0.79-0.82x at r = 3 (evidence/reconstruction_sweep.json).  A candidate is promoted only if it wins
at **both** radii, so the choice of r cannot be the reason for the result.

Arms
----
``base_d280``  the shipped live-0.2600 emission (44,090 px) — the incumbent, re-scored here
``thin_d*``    the H19-5 support re-thinned at min_dist d in raster order (the historical rule)
``prio_d*``    the same but ordered by the detector probability field when one is supplied
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33 import emission, grid, holdout, metric  # noqa: E402

SPACINGS = (2.0, 2.828, 3.5, 4.5, 6.0)
SEEDS = (0, 1, 2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--priority", type=Path, default=None,
                    help="optional .npy probability field used as the thinning priority")
    ap.add_argument("--radii", type=int, nargs="+", default=(3, 4))
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "budget_sweep.json")
    args = ap.parse_args()

    t0 = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    incompleteness = np.load(grid.CACHE / "incompleteness.npy")

    base_arr, _ = grid.read_raster("dotted_h19_5_d2_8_nan.tif")
    base = (np.isfinite(base_arr) & (base_arr > 0)) & footprint
    support_arr, _ = grid.read_raster("h19_5_nan.tif")
    support = (np.isfinite(support_arr) & (support_arr > 0)) & footprint

    prio = np.load(args.priority) if args.priority else None

    arms: dict[str, np.ndarray] = {"base_d280_44090": base}
    label = "prio" if prio is not None else "thin"
    for d in SPACINGS:
        arms[f"{label}_d{d}"] = emission.dot_thin(support, min_dist=d, priority=prio)
    print(f"support {int(support.sum()):,} px", flush=True)
    for k, v in arms.items():
        print(f"  arm {k:20s} {int(v.sum()):>7,d} px", flush=True)

    results = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "priority_field": str(args.priority) if args.priority else None,
        "spacings": list(SPACINGS), "seeds": list(args.seeds), "radii": list(args.radii),
        "arms": {k: int(v.sum()) for k, v in arms.items()},
        "by_radius": {},
    }

    for radius in args.radii:
        per_arm = {k: [] for k in arms}
        per_arm_emit = {k: [] for k in arms}
        per_arm_tp = {k: [] for k in arms}
        for seed in args.seeds:
            hidden = holdout.make_hidden_set(labels, footprint, seed,
                                             n_truth=holdout.K_HIDDEN_ESTIMATE,
                                             incompleteness=incompleteness)
            dom = holdout.calibrated_domain(footprint, labels, hidden, collar_px=1)
            for k, em in arms.items():
                e = holdout.mask_to_domain(em, dom)
                e = holdout.reconstruct_shadow(e, hidden, radius_px=radius)
                r = metric.dti_binary(e.astype(np.float32), hidden, valid=dom)
                per_arm[k].append(float(r["dti"]))
                per_arm_emit[k].append(r["n_emitted"])
                per_arm_tp[k].append(r["TPw"])
        results["by_radius"][f"radius_{radius}"] = {
            "mean_dti": {k: round(float(np.mean(v)), 6) for k, v in per_arm.items()},
            "std_dti": {k: round(float(np.std(v, ddof=1)), 6) for k, v in per_arm.items()},
            "mean_emitted": {k: round(float(np.mean(v)), 1) for k, v in per_arm_emit.items()},
            "mean_TPw": {k: round(float(np.mean(v)), 1) for k, v in per_arm_tp.items()},
            "best_arm": max(per_arm, key=lambda k: float(np.mean(per_arm[k]))),
            "n_cells": len(args.seeds),
        }
        print(f"\nradius {radius}:", flush=True)
        for k in arms:
            m = float(np.mean(per_arm[k]))
            s = float(np.std(per_arm[k], ddof=1))
            print(f"  {k:20s} dti={m:.5f} +/-{s:.5f}  emitted={np.mean(per_arm_emit[k]):>8,.0f}",
                  flush=True)

    args.out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {args.out} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
