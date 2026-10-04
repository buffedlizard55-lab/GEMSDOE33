#!/usr/bin/env python3
"""Targeted pruning of the incumbent emission — the lever the metric analysis says is largest.

From §3 of the README: at the live operating point the incumbent spends 44,090 dots to buy
T = 4,791 of weighted credit, i.e. **~95 % of emitted mass earns ~0 credit**.  A dot is worth
removing whenever its exclusive credit is below the marginal bar `alpha * DTI` = 0.0520.  The
question this script answers is whether any *observable* ranking identifies those dots well enough
to come out ahead after the credit they carry is given up.

Arms (all are strict subsets of the incumbent's 44,090 dots, so the emission geometry is
preserved and only the worthless tail is dropped):

    base_prune_det_N        drop the lowest detector-probability dots
    base_prune_inc_N        drop the dots in the best-mapped ground (H33-A, alone)
    base_prune_det_inc_N    drop the lowest detector x incompleteness dots (H33-A, combined)
    base_prune_random_N     drop uniformly at random — the matched-N content-blind control

Gate: G1 mean delta > 0 · G2 mean delta >= +0.0005 · G3 ahead in every fold x seed cell ·
G4 ahead at both reconstruction radii (3 and 4).
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

from gemsdoe33 import grid, holdout, metric  # noqa: E402

FOLDS = (0, 1, 2, 3)
BUDGETS = (40000, 35000, 30000)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=int, nargs="+", default=(3, 4))
    ap.add_argument("--seeds", type=int, nargs="+", default=(0, 1))
    ap.add_argument("--budgets", type=int, nargs="+", default=list(BUDGETS))
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "prune_incumbent.json")
    args = ap.parse_args()

    t0 = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    incompleteness = np.load(grid.CACHE / "incompleteness.npy").astype(np.float32)
    fold_ids = holdout.quadrant_ids(footprint)
    prio = np.load(grid.CACHE / "oof_probability.npy").astype(np.float32)
    inc_norm = np.load(grid.CACHE / "incompleteness_norm.npy").astype(np.float32)

    base_arr, _ = grid.read_raster("dotted_h19_5_d2_8_nan.tif")
    base = (np.isfinite(base_arr) & (base_arr > 0)) & footprint
    ys, xs = np.nonzero(base)
    n0 = ys.size

    p_det = prio[ys, xs]
    p_inc = inc_norm[ys, xs]
    rng = np.random.default_rng(11)

    arms: dict[str, np.ndarray] = {"base_d280_44090": base}
    for N in args.budgets:
        if N >= n0:
            continue
        drop = n0 - N
        for name, score in (("det", p_det), ("inc", p_inc), ("det_inc", p_det * p_inc)):
            order = np.argsort(score)          # ascending: worst first
            keep = np.ones(n0, bool)
            keep[order[:drop]] = False
            m = np.zeros_like(base)
            m[ys[keep], xs[keep]] = True
            arms[f"base_prune_{name}_{N}"] = m
        rand_order = rng.permutation(n0)
        keep = np.ones(n0, bool)
        keep[rand_order[:drop]] = False
        m = np.zeros_like(base)
        m[ys[keep], xs[keep]] = True
        arms[f"base_prune_random_{N}"] = m

    print(f"incumbent {n0:,} px", flush=True)
    for k, v in arms.items():
        print(f"  {k:28s} {int(v.sum()):>7,d}", flush=True)

    areas = {f: int(((fold_ids == f) & footprint).sum()) for f in FOLDS}
    total = sum(areas.values())
    n_truth = {f: max(1, int(round(holdout.K_HIDDEN_ESTIMATE * areas[f] / total))) for f in FOLDS}

    results = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "gate": "G1 >0; G2 >= +0.0005; G3 ahead in every cell; G4 ahead at both radii",
               "budgets": list(args.budgets), "seeds": list(args.seeds),
               "radii": list(args.radii), "incumbent_px": int(n0),
               "arms": {k: int(v.sum()) for k, v in arms.items()}, "by_radius": {}}

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
        bmap = {(c["seed"], c["fold"]): c["dti"] for c in cells["base_d280_44090"]}
        summary = {}
        for k in arms:
            d = np.array([c["dti"] for c in cells[k]])
            s = {"mean_dti": float(d.mean()),
                 "std_dti": float(d.std(ddof=1)) if d.size > 1 else 0.0,
                 "n_cells": int(d.size),
                 "mean_emitted": float(np.mean([c["n_emitted"] for c in cells[k]])),
                 "mean_TPw": float(np.mean([c["TPw"] for c in cells[k]]))}
            if k != "base_d280_44090":
                dl = [c["dti"] - bmap[(c["seed"], c["fold"])] for c in cells[k]]
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
            print(f"  {k:28s} dti={s['mean_dti']:.5f}{extra}", flush=True)

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
        print(f"  {k:28s} delta={v['mean_delta']:+.5f} G1={int(v['G1_direction'])} "
              f"G2={int(v['G2_margin'])} G3={int(v['G3_all_cells'])} "
              f"G4={int(v['G4_all_radii'])} PROMOTE={v['PROMOTE']}", flush=True)
    print(f"\nwrote {args.out} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
