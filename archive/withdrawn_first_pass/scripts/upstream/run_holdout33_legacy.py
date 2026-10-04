#!/usr/bin/env python3
"""Legacy catalogue-only diagnostic; retained for historical reproduction only.

This runner is NOT a valid promotion gate. It masks catalogue labels during
scoring but its candidate/base builders see the full catalogue, and C2's source
vectors include held-out systems. Use ``scripts/run_holdout33_source_audit.py``
for the fold-specific conditional diagnostic. Even that result does not clear a
submission slot because the upstream H19-5 surface is not re-derived per fold.

To reproduce the old, withdrawn numeric report explicitly, pass
``--allow-legacy-diagnostic``. Output defaults to a separate legacy file.
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", default="C1,C2,C3")
    ap.add_argument("--out", default="evidence/holdout33_legacy_reproduced.json")
    ap.add_argument(
        "--allow-legacy-diagnostic", action="store_true",
        help="explicitly run a known source-leaking diagnostic; never use it for slot decisions",
    )
    args = ap.parse_args()
    if not args.allow_legacy_diagnostic:
        ap.error(
            "this catalogue-only runner is invalid for promotion; use "
            "scripts/run_holdout33_source_audit.py instead"
        )

    control = c0_control()
    footprint, grid = load_template()
    catalogue = load_catalogue()
    report = {
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "status": "LEGACY_INVALID_FOR_SLOT_DECISIONS",
        "protocol_validity": {
            "status": "WITHDRAWN",
            "reason": "full-catalogue base/candidate construction and Qfaults source geometries are not fold-masked",
            "replacement": "evidence/holdout33.json",
        },
        "protocol": "Legacy P1 catalogue-hidden 4-fold + P2 SGMC off-catalogue; paired vs C0",
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
        "legacy_numeric_gate": {},
        "gate": {"pass": False, "slot_cleared": False, "reason": "legacy P1 validity failure"},
    }
    arrays = {"C0": control}
    for name in [c.strip().upper() for c in args.candidates.split(",") if c.strip()]:
        if name not in BUILDERS:
            ap.error(f"unknown candidate: {name}")
        builder = BUILDERS[name]
        print(f"[legacy build] {name} ...", flush=True)
        arr, build_report = builder()
        report["candidates"][name] = {
            "build": build_report,
            "dots": int(arr.sum()),
            "added_vs_control": int(arr.sum() - control.sum()),
        }
        arrays[name] = arr

    for name, arr in arrays.items():
        if name == "C0":
            continue
        print(f"[legacy score] {name} ...", flush=True)
        rep = evaluate_proxy(arr, control)
        verdict = gate_summary(rep)
        report["candidates"][name]["proxy"] = rep
        report["legacy_numeric_gate"][name] = verdict

    best = max(
        [n for n in report["legacy_numeric_gate"] if report["legacy_numeric_gate"][n]["pass"]] or ["C0"],
        key=lambda n: (report["candidates"].get(n, {}).get("proxy", {}).get("p1_mean_d_dti") or 0.0),
    )
    report["legacy_numeric_best"] = best
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "legacy_numeric_best": best,
        "promotion": "WITHDRAWN",
        "legacy_numeric_gate": report["legacy_numeric_gate"],
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
