#!/usr/bin/env python3
"""Final head-to-head: this session's incumbent, the two best prior-session artifacts, and the
validated 10 % targeted prune applied to each.

Artifacts on disk and their provenance:

    dotted_h19_5_d2_8  44,090 px   live 0.2600 [OWNER-REPORT]      — the group's scored anchor
    gems28-h36-1-…     37,660 px   SHA-256 5556aa14… (matches GEMSDOE28 README) — rung-3.0 re-pack
                                   + blind 1-px catalogue-flank prune
    gems28-h38-1-…     37,860 px   SHA-256 81d5b87b… (matches GEMSDOE28 README) — H36-1 plus 200
                                   heat-flow-residual x shallow-Euler corroborated dots

The prune operator is the one promoted by the frozen gate in
``knowledge/02_preregistration_confirmation.md``: drop the lowest-scoring 10 % of an emission's
dots, score = detector out-of-fold probability x (0.5 + 0.5 x normalised incompleteness).

The incumbent for the gate is ``base_d280_44090``. Nothing here re-tunes the prune; it only asks
whether the operator transfers from the emission it was validated on to the other two.
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

PARENTS = {
    "base_d280_44090": ("dotted_h19_5_d2_8_nan.tif", "live 0.2600 [OWNER-REPORT]"),
    "h36_1_rung30": ("gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
                     "GEMSDOE28 H36-1, SHA-256 5556aa14…"),
    "h38_1_hf_euler": ("gems28-h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan.tif",
                       "GEMSDOE28 H38-1, SHA-256 81d5b87b…"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=int, nargs="+", default=(3, 4))
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--trim", type=float, default=TRIM)
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "head_to_head.json")
    args = ap.parse_args()

    t0 = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    incompleteness = np.load(grid.CACHE / "incompleteness.npy").astype(np.float32)
    fold_ids = holdout.quadrant_ids(footprint)
    prio = np.load(grid.CACHE / "oof_probability.npy").astype(np.float32)
    inc_norm = np.load(grid.CACHE / "incompleteness_norm.npy").astype(np.float32)
    rng = np.random.default_rng(11)

    arms: dict[str, np.ndarray] = {}
    meta: dict[str, dict] = {}
    for name, (fname, prov) in PARENTS.items():
        arr, _ = grid.read_raster(fname)
        em = (np.isfinite(arr) & (arr > 0)) & footprint
        arms[name] = em
        meta[name] = {"file": fname, "provenance": prov, "pixels": int(em.sum())}
        ys, xs = np.nonzero(em)
        n0 = ys.size
        drop = int(round(n0 * args.trim))
        score = prio[ys, xs] * inc_norm[ys, xs]
        order = np.argsort(score)
        keep = np.ones(n0, bool)
        keep[order[:drop]] = False
        m = np.zeros_like(em)
        m[ys[keep], xs[keep]] = True
        arms[f"{name}_pruned"] = m
        meta[f"{name}_pruned"] = {"file": fname, "provenance": prov + f"; 10 % targeted prune",
                                  "pixels": int(m.sum())}
        rorder = rng.permutation(n0)
        keepr = np.ones(n0, bool)
        keepr[rorder[:drop]] = False
        mr = np.zeros_like(em)
        mr[ys[keepr], xs[keepr]] = True
        arms[f"{name}_pruned_random"] = mr
        meta[f"{name}_pruned_random"] = {"file": fname,
                                         "provenance": prov + "; 10 % RANDOM prune (control)",
                                         "pixels": int(mr.sum())}

    print("arms:", flush=True)
    for k, v in arms.items():
        print(f"  {k:28s} {int(v.sum()):>7,d} px", flush=True)

    areas = {f: int(((fold_ids == f) & footprint).sum()) for f in FOLDS}
    total = sum(areas.values())
    n_truth = {f: max(1, int(round(holdout.K_HIDDEN_ESTIMATE * areas[f] / total))) for f in FOLDS}
    n_cells = len(args.seeds) * len(FOLDS)

    results = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "trim": args.trim, "seeds": list(args.seeds), "radii": list(args.radii),
               "n_cells": n_cells, "meta": meta,
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
                 "std_dti": float(d.std(ddof=1)) if d.size > 1 else 0.0, "n_cells": int(d.size),
                 "mean_emitted": float(np.mean([c["n_emitted"] for c in cells[k]])),
                 "mean_TPw": float(np.mean([c["TPw"] for c in cells[k]]))}
            if k != "base_d280_44090":
                dl = np.array([c["dti"] - bmap[(c["seed"], c["fold"])] for c in cells[k]])
                s["delta_vs_incumbent"] = float(dl.mean())
                s["sem_delta"] = float(dl.std(ddof=1) / np.sqrt(dl.size)) if dl.size > 1 else 0.0
                s["cells_ahead"] = int((dl > 0).sum())
            summary[k] = s
        results["by_radius"][f"radius_{radius}"] = summary
        print(f"\n=== radius {radius} (n={n_cells}) ===", flush=True)
        for k in arms:
            s = summary[k]
            extra = f"  delta={s['delta_vs_incumbent']:+.5f} +/-{s['sem_delta']:.5f} " \
                    f"ahead={s['cells_ahead']}/{s['n_cells']}" if "delta_vs_incumbent" in s else ""
            print(f"  {k:28s} dti={s['mean_dti']:.5f}{extra}", flush=True)

    # Which arm to ship: mean over radii, must be positive at both.
    ship = {}
    for k in arms:
        per = [results["by_radius"][f"radius_{r}"][k].get("delta_vs_incumbent", 0.0)
               for r in args.radii]
        ship[k] = {"mean_delta": float(np.mean(per)), "per_radius": per,
                   "positive_at_both": bool(all(x > 0 for x in per))}
    results["shipping"] = ship
    args.out.write_text(json.dumps(results, indent=2))
    print("\n=== shipping summary ===", flush=True)
    for k, v in ship.items():
        print(f"  {k:28s} mean_delta={v['mean_delta']:+.5f} both_radii={v['positive_at_both']}",
              flush=True)
    print(f"\nwrote {args.out} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
