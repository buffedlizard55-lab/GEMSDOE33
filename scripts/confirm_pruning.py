#!/usr/bin/env python3
"""Confirmation run for the targeted-pruning arm — design frozen in
``knowledge/02_preregistration_confirmation.md``, committed before this script is executed.

Budget fixed a priori at "drop the lowest-scoring 10 % of the incumbent's dots" (N = 39,681),
deliberately not the best-of-three figure from the exploratory sweep.
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
SEEDS = (0, 1, 2, 3)
TRIM = 0.10


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=int, nargs="+", default=(3, 4))
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--trim", type=float, default=TRIM)
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "confirmation_pruning.json")
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
    keep_n = int(round(n0 * (1.0 - args.trim)))
    drop = n0 - keep_n
    print(f"incumbent {n0:,} px -> keep {keep_n:,} (drop {drop:,} = {args.trim:.1%})", flush=True)

    p_det = prio[ys, xs]
    p_inc = inc_norm[ys, xs]
    rng = np.random.default_rng(11)

    def subset(score):
        order = np.argsort(score)
        keep = np.ones(n0, bool)
        keep[order[:drop]] = False
        m = np.zeros_like(base)
        m[ys[keep], xs[keep]] = True
        return m

    arms = {
        "base_d280_44090": base,
        "prune_det_inc": subset(p_det * p_inc),
        "prune_det_only": subset(p_det),
        "prune_inc_only": subset(p_inc),
        "prune_random": subset(rng.random(n0)),
    }
    for k, v in arms.items():
        print(f"  {k:20s} {int(v.sum()):>7,d}", flush=True)

    areas = {f: int(((fold_ids == f) & footprint).sum()) for f in FOLDS}
    total = sum(areas.values())
    n_truth = {f: max(1, int(round(holdout.K_HIDDEN_ESTIMATE * areas[f] / total))) for f in FOLDS}
    n_cells = len(args.seeds) * len(FOLDS)

    results = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "preregistration": "knowledge/02_preregistration_confirmation.md",
               "trim": args.trim, "keep_n": keep_n, "seeds": list(args.seeds),
               "radii": list(args.radii), "n_cells": n_cells,
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
                dl = np.array([c["dti"] - bmap[(c["seed"], c["fold"])] for c in cells[k]])
                s["delta_vs_base"] = float(dl.mean())
                s["std_delta"] = float(dl.std(ddof=1)) if dl.size > 1 else 0.0
                s["sem_delta"] = float(dl.std(ddof=1) / np.sqrt(dl.size)) if dl.size > 1 else 0.0
                s["cells_ahead"] = int((dl > 0).sum())
                s["per_cell_delta"] = [{"seed": c["seed"], "fold": c["fold"],
                                        "delta": round(float(x), 6)}
                                       for c, x in zip(cells[k], dl)]
            summary[k] = s
        results["by_radius"][f"radius_{radius}"] = summary
        print(f"\n=== radius {radius} (n={n_cells} cells) ===", flush=True)
        for k in arms:
            s = summary[k]
            extra = f"  delta={s['delta_vs_base']:+.5f} +/-{s['sem_delta']:.5f} " \
                    f"ahead={s['cells_ahead']}/{s['n_cells']}" if "delta_vs_base" in s else ""
            print(f"  {k:20s} dti={s['mean_dti']:.5f}{extra}", flush=True)

    verdict = {}
    for k in arms:
        if k == "base_d280_44090":
            continue
        deltas, cells_ok = [], True
        for radius in args.radii:
            s = results["by_radius"][f"radius_{radius}"][k]
            deltas.append(s["delta_vs_base"])
            if s["cells_ahead"] < 15:
                cells_ok = False
        md = float(np.mean(deltas))
        per_r = {r: results["by_radius"][f"radius_{r}"][k]["delta_vs_base"] for r in args.radii}
        verdict[k] = {
            "mean_delta": md, "per_radius_delta": per_r,
            "C1_direction": md > 0,
            "C2_margin": md >= 0.001,
            "C3_cells": bool(cells_ok),
            "C4_beats_random": all(per_r[r] > results["by_radius"][f"radius_{r}"]["prune_random"]["delta_vs_base"]
                                   for r in args.radii),
            "C5_both_radii": all(x > 0 for x in deltas),
        }
        verdict[k]["PROMOTE"] = bool(all([verdict[k]["C1_direction"], verdict[k]["C2_margin"],
                                          verdict[k]["C3_cells"], verdict[k]["C4_beats_random"],
                                          verdict[k]["C5_both_radii"]]))
    results["verdict"] = verdict
    args.out.write_text(json.dumps(results, indent=2))
    print("\n=== verdict (frozen gate, see knowledge/02) ===", flush=True)
    for k, v in verdict.items():
        print(f"  {k:20s} delta={v['mean_delta']:+.5f} C1={int(v['C1_direction'])} "
              f"C2={int(v['C2_margin'])} C3={int(v['C3_cells'])} C4={int(v['C4_beats_random'])} "
              f"C5={int(v['C5_both_radii'])}  PROMOTE={v['PROMOTE']}", flush=True)
    print(f"\nwrote {args.out} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
