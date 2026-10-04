#!/usr/bin/env python3
"""GEMSDOE33 proxy gate: evaluate C1/C2/C3 against the scored C0 control.

Protocol (frozen before looking at any result):
  P1 catalogue-hidden 4-fold spatial block holdout, paired DeltaDTI vs C0.
  P2 SGMC off-catalogue DTI (independent state-map compilation, >= 300 m from
     the supplied catalogue), absolute and paired vs C0.
  Gate: P1 mean DeltaDTI > 0, majority of folds positive, P2 not worse than
  -0.001. A pass promotes the candidate to the one-click slot; a fail keeps C0.

Usage:
  PYTHONPATH=src python scripts/run_holdout33.py --candidates C1,C2,C3 \
      --out evidence/holdout33.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems33.candidates import c0_control, c1_h38_corroborated, c2_stepover_bridges, c3_rung30_repack
from gems33.grid import load_catalogue, load_template
from gems33.holdout import evaluate_proxy, gate_summary
from gems33.metric import inclusion_threshold

def c4_repack_plus_corroborated():
    arr, rep = c3_rung30_repack()
    arr2, rep2 = c1_h38_corroborated(arr)
    return arr2, {"stage1": rep, "stage2": rep2}


def c5_bridges_plus_corroborated():
    arr, rep = c2_stepover_bridges()
    arr2, rep2 = c1_h38_corroborated(arr)
    return arr2, {"stage1": rep, "stage2": rep2}


BUILDERS = {
    "C1": c1_h38_corroborated,
    "C2": c2_stepover_bridges,
    "C3": c3_rung30_repack,
    "C4": c4_repack_plus_corroborated,
    "C5": c5_bridges_plus_corroborated,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default="C1,C2,C3")
    ap.add_argument("--out", default="evidence/holdout33.json")
    args = ap.parse_args()

    control = c0_control()
    footprint, grid = load_template()
    catalogue = load_catalogue()
    report = {
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "protocol": "P1 catalogue-hidden 4-fold spatial block + P2 SGMC off-catalogue; paired vs C0",
        "control": {
            "file": "data/artifacts/h27-4-r1-solo-d2-8-8acb75e1f2cc-nan.tif",
            "owner_reported_live_score": 0.2708,
            "dots": int(control.sum()),
        },
        "grid": {"crs": grid.crs, "height": grid.height, "width": grid.width},
        "footprint_cells": int(footprint.sum()),
        "catalogue_pixels": int(catalogue.sum()),
        "live_break_even_at_0.2708": inclusion_threshold(0.2708),
        "candidates": {},
        "gate": {},
    }
    arrays = {"C0": control}
    for name in [c.strip().upper() for c in args.candidates.split(",") if c.strip()]:
        builder = BUILDERS[name]
        print(f"[build] {name} ...", flush=True)
        arr, build_report = builder()
        report["candidates"][name] = {"build": build_report, "dots": int(arr.sum()),
                                      "added_vs_control": int(arr.sum() - control.sum())}
        arrays[name] = arr

    for name, arr in arrays.items():
        if name == "C0":
            continue
        print(f"[gate ] {name} ...", flush=True)
        rep = evaluate_proxy(arr, control)
        verdict = gate_summary(rep)
        report["candidates"][name]["proxy"] = rep
        report["gate"][name] = verdict

    best = max(
        [n for n in report["gate"] if report["gate"][n]["pass"]] or ["C0"],
        key=lambda n: (report["candidates"].get(n, {}).get("proxy", {}).get("p1_mean_d_dti") or 0.0),
    )
    report["promoted"] = best
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps({"promoted": best, "gate": report["gate"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
