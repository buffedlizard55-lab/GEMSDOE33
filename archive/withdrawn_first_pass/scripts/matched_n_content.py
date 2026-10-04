#!/usr/bin/env python3
"""Matched-N content test: same dot count, different *which* dots.

The previous sweep could not separate content from size, because priority-ordered thinning
produces a different count than raster-ordered thinning at the same ``min_dist``.  Here every arm
is capped at exactly the same N by thinning the same support at ``min_dist = 2.0`` with a hard
``max_dots`` cap, so only the ordering differs.

Arms
----
``raster_N``       raster order (the historical H19-5 emission rule) — control
``prio_N``         descending detector out-of-fold probability
``prio_inc_N``     H33-A: detector probability x (0.5 + 0.5 * normalised incompleteness)
``prio_inc_only_N`` H33-A ablation: incompleteness weight alone (no detector)

Gate: identical to scripts/run_blocked_holdout.py — G1..G4, with the incumbent
``base_d280_44090`` (the live 0.2600 emission) as the comparator.
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

FOLDS = (0, 1, 2, 3)
BUDGETS = (44090, 40000, 35000, 30000)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=int, nargs="+", default=(3, 4))
    ap.add_argument("--seeds", type=int, nargs="+", default=(0, 1))
    ap.add_argument("--inc-floor", type=float, default=0.5,
                    help="weight = inc_floor + (1-inc_floor)*normalised incompleteness")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "matched_n_content.json")
    args = ap.parse_args()

    t0 = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    incompleteness = np.load(grid.CACHE / "incompleteness.npy").astype(np.float32)
    fold_ids = holdout.quadrant_ids(footprint)
    prio = np.load(grid.CACHE / "oof_probability.npy").astype(np.float32)

    inc = incompleteness[footprint]
    inc = (inc - inc.min()) / max(inc.max() - inc.min(), 1e-9)
    inc_full = np.zeros(footprint.shape, dtype=np.float32)
    inc_full[footprint] = inc
    weight_inc = args.inc_floor + (1.0 - args.inc_floor) * inc_full
    np.save(grid.CACHE / "incompleteness_norm.npy", inc_full)

    base_arr, _ = grid.read_raster("dotted_h19_5_d2_8_nan.tif")
    base = (np.isfinite(base_arr) & (base_arr > 0)) & footprint
    sup_arr, _ = grid.read_raster("h19_5_nan.tif")
    support = (np.isfinite(sup_arr) & (sup_arr > 0)) & footprint

    arms: dict[str, np.ndarray] = {"base_d280_44090": base}
    for N in BUDGETS:
        arms[f"raster_{N}"] = emission.dot_thin(support, min_dist=2.0, max_dots=N)
        arms[f"prio_{N}"] = emission.dot_thin(support, min_dist=2.0, priority=prio, max_dots=N)
        arms[f"prio_inc_{N}"] = emission.dot_thin(support, min_dist=2.0,
                                                  priority=prio * weight_inc, max_dots=N)
        arms[f"prio_inc_only_{N}"] = emission.dot_thin(support, min_dist=2.0,
                                                       priority=weight_inc, max_dots=N)
    print("arms (matched N):", flush=True)
    for k, v in arms.items():
        print(f"  {k:22s} {int(v.sum()):>7,d} px", flush=True)

    areas = {f: int(((fold_ids == f) & footprint).sum()) for f in FOLDS}
    total = sum(areas.values())
    n_truth = {f: max(1, int(round(holdout.K_HIDDEN_ESTIMATE * areas[f] / total))) for f in FOLDS}

    results = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gate": "G1 mean delta > 0; G2 mean delta >= +0.0005; G3 ahead in every fold/seed cell; "
                "G4 ahead at every reconstruction radius",
        "budgets": list(BUDGETS), "inc_floor": args.inc_floor,
        "seeds": list(args.seeds), "radii": list(args.radii),
        "arms": {k: int(v.sum()) for k, v in arms.items()},
        "n_truth_per_fold": n_truth,
        "by_radius": {},
    }

    for radius in args.radii:
        cells = {k: [] for k in arms}
        for seed in args.seeds:
            for f in FOLDS:
                region = (fold_ids == f) & footprint
                hidden = holdout.make_hidden_set(labels, footprint, seed, n_truth=n_truth[f],
                                                 incompleteness=incompleteness,
                                                 folds=fold_ids, fold=f)
                dom = holdout.calibrated_domain(footprint, labels, hidden, collar_px=1) & region
                for k, em in arms.items():
                    e = holdout.reconstruct_shadow(holdout.mask_to_domain(em, dom), hidden,
                                                   radius_px=radius)
                    r = metric.dti_binary(e.astype(np.float32), hidden & region, valid=dom)
                    cells[k].append({"seed": int(seed), "fold": int(f), "dti": float(r["dti"]),
                                     "TPw": float(r["TPw"]), "n_emitted": int(r["n_emitted"])})
        base_map = {(c["seed"], c["fold"]): c["dti"] for c in cells["base_d280_44090"]}
        summary = {}
        for k in arms:
            d = np.array([c["dti"] for c in cells[k]])
            s = {"mean_dti": float(d.mean()),
                 "std_dti": float(d.std(ddof=1)) if d.size > 1 else 0.0,
                 "n_cells": int(d.size),
                 "mean_emitted": float(np.mean([c["n_emitted"] for c in cells[k]])),
                 "mean_TPw": float(np.mean([c["TPw"] for c in cells[k]]))}
            if k != "base_d280_44090":
                dl = [c["dti"] - base_map[(c["seed"], c["fold"])] for c in cells[k]]
                s["delta_vs_base"] = float(np.mean(dl))
                s["std_delta"] = float(np.std(dl, ddof=1)) if len(dl) > 1 else 0.0
                s["cells_ahead"] = int(sum(1 for x in dl if x > 0))
            summary[k] = s
        results["by_radius"][f"radius_{radius}"] = summary
        print(f"\n=== radius {radius} ===", flush=True)
        for k in arms:
            s = summary[k]
            extra = f"  delta={s['delta_vs_base']:+.5f} ahead={s['cells_ahead']}/{s['n_cells']}" \
                if "delta_vs_base" in s else ""
            print(f"  {k:22s} dti={s['mean_dti']:.5f}{extra}", flush=True)

    verdict = {}
    for k in arms:
        if k == "base_d280_44090":
            continue
        deltas, all_cells = [], True
        for radius in args.radii:
            s = results["by_radius"][f"radius_{radius}"][k]
            deltas.append(s["delta_vs_base"])
            if s["cells_ahead"] < s["n_cells"]:
                all_cells = False
        md = float(np.mean(deltas))
        verdict[k] = {"mean_delta": md,
                      "per_radius_delta": {r: results["by_radius"][f"radius_{r}"][k]["delta_vs_base"]
                                           for r in args.radii},
                      "G1_direction": md > 0, "G2_margin": md >= 0.0005,
                      "G3_all_cells": all_cells, "G4_all_radii": all(x > 0 for x in deltas)}
        verdict[k]["PROMOTE"] = bool(all([verdict[k]["G1_direction"], verdict[k]["G2_margin"],
                                          verdict[k]["G3_all_cells"], verdict[k]["G4_all_radii"]]))
    results["verdict"] = verdict
    args.out.write_text(json.dumps(results, indent=2))
    print("\n=== verdict ===", flush=True)
    for k, v in verdict.items():
        print(f"  {k:22s} delta={v['mean_delta']:+.5f} G1={int(v['G1_direction'])} "
              f"G2={int(v['G2_margin'])} G3={int(v['G3_all_cells'])} G4={int(v['G4_all_radii'])} "
              f"PROMOTE={v['PROMOTE']}", flush=True)
    print(f"\nwrote {args.out} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
