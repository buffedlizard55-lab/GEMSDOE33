#!/usr/bin/env python3
"""Spatially-blocked holdout: the gate that decides whether a candidate is promoted.

Design (frozen here, before any candidate is scored)
---------------------------------------------------
Folds        four quadrants (NW/NE/SW/SE).  The detector is fit out-of-fold, so every scored arm is
             ranked by a model that never saw a catalogue fault from the quadrant it is scored in.
Truth        per fold, ``n_truth = round(K * area(fold)/area(footprint))`` catalogue pixels, K = 12,226,
             drawn with probability proportional to the exploration-incompleteness field.
Domain       the visible catalogue (collared 1 px) is removed from the emission domain; the hidden
             draw itself is preserved inside it.
Reconstruct  the catalogue shadow is undone at radius r (default 3 px = the kernel support).
Scoring      restricted to the fold, so truth density and emitted density are both the *local*
             ones and the DTI is on the same scale as the global instrument.

Gate (all four must hold, or nothing is promoted)
-------------------------------------------------
G1  direction   mean paired delta vs the incumbent ``base_d280_44090`` > 0
G2  margin      mean paired delta >= +0.0005
G3  stability   the arm is ahead in every fold (4/4)
G4  robustness  the arm is ahead at BOTH reconstruction radii 3 and 4

G4 exists because the reconstruction radius is the instrument's one uncontrolled parameter; an arm
that only wins at one radius is an artefact of that choice, not a result.
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

from gemsdoe33 import detector, emission, features, grid, holdout, metric  # noqa: E402

FOLDS = (0, 1, 2, 3)


def build_arms(support: np.ndarray, prio: np.ndarray | None) -> dict[str, np.ndarray]:
    arms = {}
    spacings = (2.0, 2.828, 3.5)
    for d in spacings:
        arms[f"thin_d{d}"] = emission.dot_thin(support, min_dist=d)
        if prio is not None:
            arms[f"prio_d{d}"] = emission.dot_thin(support, min_dist=d, priority=prio)
    return arms


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=int, nargs="+", default=(3, 4))
    ap.add_argument("--seeds", type=int, nargs="+", default=(0, 1))
    ap.add_argument("--max-iter", type=int, default=150)
    ap.add_argument("--skip-detector", action="store_true")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "blocked_holdout.json")
    args = ap.parse_args()

    t0 = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    incompleteness = np.load(grid.CACHE / "incompleteness.npy")
    fold_ids = holdout.quadrant_ids(footprint)
    channels = features.channel_names()

    base_arr, _ = grid.read_raster("dotted_h19_5_d2_8_nan.tif")
    base = (np.isfinite(base_arr) & (base_arr > 0)) & footprint
    sup_arr, _ = grid.read_raster("h19_5_nan.tif")
    support = (np.isfinite(sup_arr) & (sup_arr > 0)) & footprint

    prio = None
    if not args.skip_detector:
        cache = grid.CACHE / "oof_probability.npy"
        if cache.exists():
            prio = np.load(cache)
            print(f"loaded OOF field from {cache}", flush=True)
        else:
            print("fitting spatially-blocked detector ...", flush=True)
            prio = detector.fit_predict_oof(channels, fold_ids, labels, footprint,
                                            seed=0, max_iter=args.max_iter)
            np.save(cache, prio)
            print("  wrote OOF field", flush=True)

    arms = {"base_d280_44090": base}
    arms.update(build_arms(support, prio))
    print("\narms:", flush=True)
    for k, v in arms.items():
        print(f"  {k:20s} {int(v.sum()):>7,d} px", flush=True)

    # per-fold truth budget, proportional to fold area
    areas = {f: int(((fold_ids == f) & footprint).sum()) for f in FOLDS}
    total = sum(areas.values())
    n_truth = {f: max(1, int(round(holdout.K_HIDDEN_ESTIMATE * areas[f] / total))) for f in FOLDS}
    print(f"\nfold areas {areas} -> truth per fold {n_truth}", flush=True)

    results = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gate": "G1 mean delta > 0; G2 mean delta >= +0.0005; G3 4/4 folds; G4 wins at every radius",
        "fold_areas": areas, "n_truth_per_fold": n_truth,
        "seeds": list(args.seeds), "radii": list(args.radii),
        "detector": None if args.skip_detector else {
            "model": "HistGradientBoostingClassifier", "max_iter": args.max_iter,
            "n_channels": len(channels), "folds": list(FOLDS), "neg_per_pos": detector.NEG_PER_POS,
        },
        "arms": {k: int(v.sum()) for k, v in arms.items()},
        "by_radius": {},
    }

    for radius in args.radii:
        cells: dict[str, list[dict]] = {k: [] for k in arms}
        for seed in args.seeds:
            for f in FOLDS:
                region = (fold_ids == f) & footprint
                hidden = holdout.make_hidden_set(labels, footprint, seed, n_truth=n_truth[f],
                                                 incompleteness=incompleteness,
                                                 folds=fold_ids, fold=f)
                dom = holdout.calibrated_domain(footprint, labels, hidden, collar_px=1) & region
                for k, em in arms.items():
                    e = holdout.mask_to_domain(em, dom)
                    e = holdout.reconstruct_shadow(e, hidden, radius_px=radius)
                    r = metric.dti_binary(e.astype(np.float32), hidden & region, valid=dom)
                    cells[k].append({"seed": int(seed), "fold": int(f), "dti": float(r["dti"]),
                                     "TPw": float(r["TPw"]), "n_emitted": int(r["n_emitted"]),
                                     "n_truth": int(r["n_truth"])})
        summary = {}
        for k in arms:
            d = np.array([c["dti"] for c in cells[k]])
            summary[k] = {"mean_dti": float(d.mean()),
                          "std_dti": float(d.std(ddof=1)) if d.size > 1 else 0.0,
                          "n_cells": int(d.size),
                          "mean_emitted": float(np.mean([c["n_emitted"] for c in cells[k]])),
                          "per_cell": cells[k]}
        base_key = "base_d280_44090"
        base_by_seed_fold = {(c["seed"], c["fold"]): c["dti"] for c in cells[base_key]}
        for k in arms:
            if k == base_key:
                summary[k]["delta_vs_base"] = 0.0
                summary[k]["folds_ahead"] = None
                continue
            deltas = [c["dti"] - base_by_seed_fold[(c["seed"], c["fold"])] for c in cells[k]]
            summary[k]["delta_vs_base"] = float(np.mean(deltas))
            summary[k]["std_delta"] = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0
            summary[k]["folds_ahead"] = int(sum(1 for x in deltas if x > 0))
            summary[k]["n_deltas"] = len(deltas)
        results["by_radius"][f"radius_{radius}"] = {
            "summary": {k: {kk: vv for kk, vv in v.items() if kk != "per_cell"}
                        for k, v in summary.items()},
        }
        print(f"\n=== radius {radius} ===", flush=True)
        for k in arms:
            s = summary[k]
            print(f"  {k:20s} dti={s['mean_dti']:.5f}  delta={s['delta_vs_base']:+.5f}  "
                  f"folds_ahead={s['folds_ahead']}", flush=True)

    # gate across radii
    verdict = {}
    for k in arms:
        if k == "base_d280_44090":
            continue
        deltas, all_folds = [], True
        for radius in args.radii:
            s = results["by_radius"][f"radius_{radius}"]["summary"][k]
            deltas.append(s["delta_vs_base"])
            if s["folds_ahead"] is not None and s["folds_ahead"] < len(args.seeds) * len(FOLDS):
                all_folds = False
        mean_delta = float(np.mean(deltas))
        verdict[k] = {
            "mean_delta": mean_delta,
            "per_radius_delta": {r: results["by_radius"][f"radius_{r}"]["summary"][k]["delta_vs_base"]
                                 for r in args.radii},
            "G1_direction": bool(mean_delta > 0),
            "G2_margin": bool(mean_delta >= 0.0005),
            "G3_all_folds": bool(all_folds),
            "G4_all_radii": bool(all(d > 0 for d in deltas)),
        }
        verdict[k]["PROMOTE"] = bool(verdict[k]["G1_direction"] and verdict[k]["G2_margin"]
                                     and verdict[k]["G3_all_folds"] and verdict[k]["G4_all_radii"])
    results["verdict"] = verdict
    args.out.write_text(json.dumps(results, indent=2))
    print(f"\n=== verdict ===", flush=True)
    for k, v in verdict.items():
        print(f"  {k:20s} delta={v['mean_delta']:+.5f}  G1={v['G1_direction']} G2={v['G2_margin']} "
              f"G3={v['G3_all_folds']} G4={v['G4_all_radii']}  PROMOTE={v['PROMOTE']}", flush=True)
    print(f"\nwrote {args.out} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
