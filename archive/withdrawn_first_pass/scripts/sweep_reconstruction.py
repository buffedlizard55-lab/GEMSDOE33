#!/usr/bin/env python3
"""Sweep the catalogue-shadow reconstruction radius and test the instrument against live values.

If the calibrated instrument can reproduce not just the *ordering* but the *magnitude* of the
three owner-reported live scores (0.2600 / 0.2477 / 0.1922), it becomes a scale-calibrated
instrument: local decisions about emission size and content can then be read directly.
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
FILES = {"d280_44090": "dotted_h19_5_d2_8_nan.tif",
         "d150_60069": "dotted_h19_5_d1_5_nan.tif",
         "h19_5_121131": "h19_5_nan.tif"}


def main() -> int:
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    incompleteness = np.load(grid.CACHE / "incompleteness.npy")
    emissions = {}
    for k, f in FILES.items():
        arr, _ = grid.read_raster(f)
        emissions[k] = (np.isfinite(arr) & (arr > 0)) & footprint

    out = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "sweep": {}}
    for radius in (2, 3, 4, 5):
        t0 = time.time()
        per_em = {k: [] for k in emissions}
        extra = {k: [] for k in emissions}
        for seed in (0, 1, 2):
            hidden = holdout.make_hidden_set(labels, footprint, seed,
                                             n_truth=holdout.K_HIDDEN_ESTIMATE,
                                             incompleteness=incompleteness)
            dom = holdout.calibrated_domain(footprint, labels, hidden, collar_px=1)
            for k, em in emissions.items():
                e = holdout.mask_to_domain(em, dom)
                e2 = holdout.reconstruct_shadow(e, hidden, radius_px=radius)
                r = metric.dti_binary(e2.astype(np.float32), hidden, valid=dom)
                per_em[k].append(float(r["dti"]))
                extra[k].append(int((e2 & hidden).sum()))
        means = {k: float(np.mean(v)) for k, v in per_em.items()}
        recov = {k: float(np.mean(v) / holdout.K_HIDDEN_ESTIMATE) for k, v in extra.items()}
        ratio = {k: round(means[k] / LIVE[k], 3) for k in means}
        out["sweep"][f"radius_{radius}"] = {
            "mean_dti": {k: round(v, 5) for k, v in means.items()},
            "hidden_recovered_fraction": {k: round(v, 4) for k, v in recov.items()},
            "proxy_over_live": ratio,
            "live_ordering": bool(all(means[a] > means[b] for a, b in zip(ORDER, ORDER[1:]))),
            "seconds": round(time.time() - t0, 1),
        }
        print(f"radius {radius}: dti={ {k: round(v,4) for k,v in means.items()} } "
              f"recov={ {k: round(v,3) for k,v in recov.items()} } "
              f"proxy/live={ratio} order="
              f"{all(means[a] > means[b] for a, b in zip(ORDER, ORDER[1:]))}", flush=True)

    dest = ROOT / "evidence" / "reconstruction_sweep.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
