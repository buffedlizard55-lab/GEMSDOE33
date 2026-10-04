#!/usr/bin/env python3
"""Per-channel discrimination screen, scored against the population that matters.

Two AUCs are computed for every channel in ``.cache/features``:

``auc_catalogue``   catalogue fault pixels (60,988) vs background
``auc_offcat``      **off-catalogue** SGMC fault pixels (79,615) vs background

The second is the one this programme has never had.  The organiser scores only faults that are
*absent* from the USGS/INGENIOUS catalogue, so a channel whose discrimination is confined to the
catalogue population has no scoring value however good its catalogue AUC looks.  The ratio
``auc_offcat / auc_catalogue`` is the quantity that ranks the hypotheses in registry/hypotheses.json.

Background for both is a fixed, spatially-uniform random sample of footprint cells at least 3 px
from any catalogue or SGMC fault, so neither AUC is inflated by the kernel's 300 m support.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33 import features, grid  # noqa: E402

N_BG = 200_000
SEED = 7


def auc(pos: np.ndarray, bg: np.ndarray) -> float:
    """ROC AUC using scikit-learn's tie-correct implementation.

    The original hand-coded ranks mixed zero-based unique ranks with one-based tied ranks and
    therefore had an inconsistent Mann-Whitney correction. It is not used for any claim here.
    """
    from sklearn.metrics import roc_auc_score
    if pos.size == 0 or bg.size == 0:
        return float("nan")
    y = np.concatenate([np.ones(pos.size, dtype=np.uint8), np.zeros(bg.size, dtype=np.uint8)])
    s = np.concatenate([np.asarray(pos, dtype=np.float64), np.asarray(bg, dtype=np.float64)])
    return float(roc_auc_score(y, s))


def main() -> int:
    t0 = time.time()
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    sgmc, _ = grid.read_raster("derived_sgmc_faults_100m_u8.tif")
    sgmc = (sgmc > 0) & footprint
    offcat = sgmc & ~labels
    cat = labels & footprint
    print(f"catalogue {int(cat.sum()):,}   SGMC off-catalogue {int(offcat.sum()):,}", flush=True)

    excl = binary_dilation(cat | sgmc, iterations=3, structure=np.ones((3, 3), bool))
    bg_mask = footprint & ~excl
    rng = np.random.default_rng(SEED)
    bg_idx = np.flatnonzero(bg_mask.reshape(-1))
    bg_pick = rng.choice(bg_idx, size=min(N_BG, bg_idx.size), replace=False)
    print(f"background pool {int(bg_mask.sum()):,} -> sampled {bg_pick.size:,}", flush=True)

    names = features.channel_names()
    rows = []
    for i, name in enumerate(names):
        arr = np.load(features.CACHE_FEATURES / f"{name}.npy", mmap_mode="r")
        flat = np.asarray(arr).reshape(-1)
        a_cat = auc(np.nan_to_num(flat[cat.reshape(-1)], nan=0.0), flat[bg_pick])
        a_off = auc(np.nan_to_num(flat[offcat.reshape(-1)], nan=0.0), flat[bg_pick])
        rows.append({"channel": name, "auc_catalogue": round(a_cat, 4),
                     "auc_offcat": round(a_off, 4),
                     "offcat_over_catalogue": round(a_off / a_cat, 4) if a_cat > 0 else None,
                     "lift": round(a_off - 0.5, 4)})
        if (i + 1) % 25 == 0:
            print(f"  {i + 1}/{len(names)}", flush=True)

    rows.sort(key=lambda r: -(r["auc_offcat"]))
    dest = ROOT / "evidence" / "channel_screen.json"
    dest.write_text(json.dumps({
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_background": int(bg_pick.size),
        "n_catalogue": int(cat.sum()), "n_offcat": int(offcat.sum()),
        "note": "auc_offcat is the diagnostic that matters: the organiser scores only faults "
                "absent from the USGS/INGENIOUS catalogue.",
        "channels": rows,
    }, indent=2))
    print(f"\nwrote {dest} ({time.time() - t0:.0f}s)\n")
    print(f"{'channel':34s} {'AUC_cat':>8s} {'AUC_off':>8s} {'off/cat':>8s}")
    for r in rows[:30]:
        print(f"{r['channel']:34s} {r['auc_catalogue']:8.4f} {r['auc_offcat']:8.4f} "
              f"{r['offcat_over_catalogue']:8.4f}")
    print("\n--- worst 8 by off-catalogue AUC ---")
    for r in rows[-8:]:
        print(f"{r['channel']:34s} {r['auc_catalogue']:8.4f} {r['auc_offcat']:8.4f} "
              f"{r['offcat_over_catalogue']:8.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
