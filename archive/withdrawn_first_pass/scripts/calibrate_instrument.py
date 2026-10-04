#!/usr/bin/env python3
"""Calibrate the holdout instrument against the three live-scored emissions on disk.

The three emissions in ``data/`` are owner-mirrored copies of submissions that carry
owner-reported live scores:

    h19_5_nan.tif               121,131 px   live 0.1922  [OWNER-REPORT]
    dotted_h19_5_d1_5_nan.tif    60,069 px   live 0.2477  [OWNER-REPORT]
    dotted_h19_5_d2_8_nan.tif    44,090 px   live 0.2600  [OWNER-REPORT]

The live board ranks them 44,090 > 60,069 > 121,131.  A holdout instrument that cannot reproduce
that ordering cannot be used to choose a budget.  This script tests four variants of the
instrument side by side:

    A  whole-catalogue proxy                       (the instrument GEMSDOE32 showed is anti-monotone)
    B  + all catalogue pixels removed from emission domain
    C  + truth size calibrated to |G| ~ 12,226 px
    D  + truth sampled preferentially from poorly-explored ground (H33-1 incompleteness field)

and writes ``evidence/instrument_calibration.json``.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33 import grid, holdout, metric  # noqa: E402

LIVE = {"d280_44090": 0.2600, "d150_60069": 0.2477, "h19_5_121131": 0.1922}
ORDER = ["d280_44090", "d150_60069", "h19_5_121131"]
FILES = {
    "d280_44090": "dotted_h19_5_d2_8_nan.tif",
    "d150_60069": "dotted_h19_5_d1_5_nan.tif",
    "h19_5_121131": "h19_5_nan.tif",
}


def load_emission(name: str, footprint: np.ndarray) -> np.ndarray:
    arr, _ = grid.read_raster(FILES[name])
    return (np.isfinite(arr) & (arr > 0)) & footprint


def main() -> int:
    t0 = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    print(f"footprint {int(footprint.sum()):,}  catalogue {int((labels & footprint).sum()):,}",
          flush=True)

    emissions = {}
    for name, f in FILES.items():
        em = load_emission(name, footprint)
        emissions[name] = em
        print(f"  {name:16s} {int(em.sum()):>7,d} px  (live {LIVE[name]})", flush=True)

    from gemsdoe33.domain import exploration_intensity
    inten = exploration_intensity()
    lo, hi = np.quantile(inten[footprint], [0.05, 0.95])
    incompleteness = np.clip((hi - inten) / max(hi - lo, 1e-9), 0, None)
    np.save(grid.CACHE / "exploration_intensity.npy", inten.astype(np.float32))
    np.save(grid.CACHE / "incompleteness.npy", incompleteness.astype(np.float32))

    results: dict = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     "emissions": {k: {"pixels": int(v.sum()), "live_owner_reported": LIVE[k],
                                       "file": FILES[k]}
                                   for k, v in emissions.items()},
                     "variants": {}}

    # ---- Variant A: whole-catalogue truth, catalogue NOT removed from the domain --------------
    # (this is the historical instrument; kept so the failure mode is reproduced, not asserted)
    dom_full = footprint
    rows = {}
    for name, em in emissions.items():
        r = metric.dti_binary(em.astype(np.float32), labels & footprint, valid=dom_full)
        rows[name] = {"mean_dti": float(r["dti"]), "n_emitted": r["n_emitted"],
                      "n_truth": r["n_truth"]}
    results["variants"]["A_whole_catalogue_truth"] = {
        "description": "truth = all 60,988 catalogue px; emission allowed anywhere in footprint",
        "scores": rows,
        "reproduces_live_ordering": all(rows[a]["mean_dti"] > rows[b]["mean_dti"]
                                        for a, b in zip(ORDER, ORDER[1:])),
    }

    # ---- Variant B: whole-catalogue truth, catalogue-blind domain (hidden = all catalogue) ----
    # With H = the whole catalogue there is no visible catalogue left, so the domain is the whole
    # footprint; this variant isolates the effect of dropping the |G| calibration only.
    dom = footprint
    rows = {}
    for name, em in emissions.items():
        r = metric.dti_binary(em.astype(np.float32), labels & footprint, valid=dom)
        rows[name] = {"mean_dti": float(r["dti"]), "n_emitted": r["n_emitted"],
                      "n_truth": r["n_truth"]}
    results["variants"]["B_catalogue_blind_domain"] = {
        "description": "truth = all 60,988 catalogue px, domain = whole footprint "
                       "(no visible catalogue survives, so nothing is removed)",
        "scores": rows,
        "reproduces_live_ordering": all(rows[a]["mean_dti"] > rows[b]["mean_dti"]
                                        for a, b in zip(ORDER, ORDER[1:])),
    }

    # ---- Variant B2: 80 % visible catalogue removed from the domain, 20 % kept as truth -------
    # Identical to C except the truth is drawn *uniformly* and the visible remainder is removed
    # from the emission domain (dots on visible faults earn nothing) -- isolates that single
    # geometric correction.
    rows = {}
    for seed in (0, 1, 2):
        hidden = holdout.make_hidden_set(labels, footprint, seed,
                                         n_truth=holdout.K_HIDDEN_ESTIMATE)
        dom = holdout.calibrated_domain(footprint, labels, hidden, collar_px=1)
        for name, em in emissions.items():
            r = metric.dti_binary((em & dom).astype(np.float32), hidden, valid=dom)
            rows.setdefault(name, []).append(float(r["dti"]))
    means = {k: float(np.mean(v)) for k, v in rows.items()}
    results["variants"]["B2_visible_removed_uniform_truth"] = {
        "description": "truth = 12,226 uniformly drawn catalogue px; the remaining 48,762 "
                       "visible catalogue px (collared 1 px) are removed from the emission domain",
        "scores": {k: {"mean_dti": v, "n_cells": 3} for k, v in means.items()},
        "reproduces_live_ordering": all(means[a] > means[b] for a, b in zip(ORDER, ORDER[1:])),
    }

    # ---- Variant C: |G| calibrated to 12,226 px, catalogue-blind domain ----------------------
    lad = holdout.calibration_ladder(emissions, labels, footprint, seeds=(0, 1, 2),
                                     n_truth=holdout.K_HIDDEN_ESTIMATE, incompleteness=None)
    results["variants"]["C_calibrated_truth_size"] = {
        "description": "truth = 12,226 catalogue px drawn uniformly; catalogue-blind domain; 3 seeds",
        "scores": {k: {kk: vv for kk, vv in v.items() if kk != "per_cell"} for k, v in lad.items()
                   if k != "_settings"},
        "settings": lad["_settings"],
        "check": holdout.monotone_check(lad, ORDER),
    }

    # ---- Variant D: + incompleteness-weighted truth ------------------------------------------
    lad = holdout.calibration_ladder(emissions, labels, footprint, seeds=(0, 1, 2),
                                     n_truth=holdout.K_HIDDEN_ESTIMATE,
                                     incompleteness=incompleteness)
    results["variants"]["D_incompleteness_weighted"] = {
        "description": "truth = 12,226 catalogue px drawn preferentially from poorly-explored "
                       "ground; catalogue-blind domain; 3 seeds",
        "scores": {k: {kk: vv for kk, vv in v.items() if kk != "per_cell"} for k, v in lad.items()
                   if k != "_settings"},
        "settings": lad["_settings"],
        "check": holdout.monotone_check(lad, ORDER),
    }

    # ---- Variant E: D + quadrant spatial blocking --------------------------------------------
    lad = holdout.calibration_ladder(emissions, labels, footprint, seeds=(0, 1),
                                     n_truth=holdout.K_HIDDEN_ESTIMATE // 4,
                                     incompleteness=incompleteness, quadrant=True)
    results["variants"]["E_quadrant_blocked"] = {
        "description": "as D but the hidden set is drawn per quadrant fold (4 folds x 2 seeds), "
                       "so truth and model never share a quadrant",
        "scores": {k: {kk: vv for kk, vv in v.items() if kk != "per_cell"} for k, v in lad.items()
                   if k != "_settings"},
        "settings": lad["_settings"],
        "check": holdout.monotone_check(lad, ORDER),
    }

    # ---- Variant F: D + catalogue-shadow reconstruction --------------------------------------
    lad = holdout.calibration_ladder(emissions, labels, footprint, seeds=(0, 1, 2),
                                     n_truth=holdout.K_HIDDEN_ESTIMATE,
                                     incompleteness=incompleteness, reconstruct=True)
    results["variants"]["F_shadow_reconstructed"] = {
        "description": "as D plus reconstruction of the catalogue mask on the hidden draw "
                       "(hidden pixels within 2 px of an emitted dot get their dot back)",
        "scores": {k: {kk: vv for kk, vv in v.items() if kk != "per_cell"} for k, v in lad.items()
                   if k != "_settings"},
        "settings": lad["_settings"],
        "check": holdout.monotone_check(lad, ORDER),
    }

    # ---- Variant G: F + quadrant spatial blocking (the promoted instrument) ------------------
    lad = holdout.calibration_ladder(emissions, labels, footprint, seeds=(0, 1),
                                     n_truth=holdout.K_HIDDEN_ESTIMATE // 4,
                                     incompleteness=incompleteness, quadrant=True,
                                     reconstruct=True)
    results["variants"]["G_quadrant_reconstructed"] = {
        "description": "as F with the hidden set drawn per quadrant fold (4 folds x 2 seeds)",
        "scores": {k: {kk: vv for kk, vv in v.items() if kk != "per_cell"} for k, v in lad.items()
                   if k != "_settings"},
        "settings": lad["_settings"],
        "check": holdout.monotone_check(lad, ORDER),
    }

    dest = ROOT / "evidence" / "instrument_calibration.json"
    dest.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {dest}  ({time.time() - t0:.1f}s)")
    for vname, v in results["variants"].items():
        chk = v.get("check", {}).get("reproduces_live_ordering", v.get("reproduces_live_ordering"))
        means = {k: round(x["mean_dti"], 5) for k, x in v["scores"].items()}
        print(f"{vname:34s} live-order={chk}  {means}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
