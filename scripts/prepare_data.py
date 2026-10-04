"""Build git-ignored inputs/features and an out-of-fold research score field.

This script does NOT create or promote a competition submission. The learned score is supervised
on the incomplete public catalogue, so it is a research surface only until an independent
field-specific validation is available.

Stages::

    1. restore_data.py verifies the owner-mirror input hashes (run separately)
    2. sanitise all 19 bands and set the authoritative template footprint
    3. build shared feature channels (derived grids stay under .cache/)
    4. optionally train quadrant-out-of-fold catalogue detector (research only)

Usage::

    python scripts/restore_data.py --group all
    python scripts/prepare_data.py
    python scripts/prepare_data.py --skip-detector
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np  # noqa: E402
from gemsdoe33 import detector, domain, features, grid, holdout, paths  # noqa: E402


def stage_bands(force=False):
    print("[1/4] sanitise bands + exact submission-template footprint", flush=True)
    report = grid.build_band_cache(force=force)
    print(f"      template footprint={report['n_footprint']:,}; "
          f"template cells with missing core band="
          f"{report['n_template_cells_missing_any_core_band']:,}", flush=True)


def stage_channels():
    print(f"[2/4] build {features.EXPECTED_CHANNEL_COUNT} research channels", flush=True)
    names, summary = features.build_channels(report=True)
    malformed = [n for n in names if np.load(paths.CACHE_FEATURES / f"{n}.npy", mmap_mode="r").shape != (3730, 3292)]
    if len(names) != features.EXPECTED_CHANNEL_COUNT or malformed:
        raise SystemExit(f"channel schema mismatch: {len(names)} names; malformed={malformed}")
    # Old model scores were fit on a different channel set and are not reusable.
    for stale in (grid.CACHE / "oof_probability.npy", grid.CACHE / "oof_probability_signature.json"):
        stale.unlink(missing_ok=True)
    print(f"      {summary}", flush=True)


def stage_site_density():
    print("[3/4] unique GDR well/spring-cell density (descriptive only)", flush=True)
    density = domain.documented_site_density()
    np.save(grid.CACHE / "documented_site_density.npy", density.astype(np.float32))
    print("      saved unique-cell density; NOT treated as fault-catalogue completeness", flush=True)


def stage_oof():
    print("[4/4] train quadrant-out-of-fold research detector", flush=True)
    footprint = grid.template_footprint()
    labels = grid.load_labels()
    fold_ids = holdout.quadrant_ids(footprint)
    names = features.channel_names()
    pred = detector.fit_predict_oof(names, fold_ids, labels, footprint, seed=0)
    np.save(grid.CACHE / "oof_probability.npy", pred)
    (grid.CACHE / "oof_probability_signature.json").write_text(
        json.dumps({"channels": names, "seed": 0, "folds": "quadrants",
                    "status": "research-only supervised on incomplete catalogue; not a submission probability"}, indent=2)
    )
    if not np.isfinite(pred[footprint]).all() or np.any((pred[footprint] < 0) | (pred[footprint] > 1)):
        raise SystemExit("OOF output failed finite [0,1] checks")
    print("      OOF field cached, range/finite checks pass; not an independent hidden-fault validation", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-detector", action="store_true")
    ap.add_argument("--force-bands", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    if args.force_bands or not (grid.CACHE / "footprint.npy").exists():
        stage_bands(force=args.force_bands)
    else:
        print("[1/4] bands + footprint — cached", flush=True)
    names_file = grid.CACHE / "channel_names.json"
    cached_names = features.channel_names() if names_file.exists() else []
    channel_files_exist = all((paths.CACHE_FEATURES / f"{n}.npy").exists() for n in cached_names)
    if len(cached_names) != features.EXPECTED_CHANNEL_COUNT or not channel_files_exist:
        stage_channels()
    else:
        print(f"[2/4] {len(cached_names)} channels — cached", flush=True)
    if not (grid.CACHE / "documented_site_density.npy").exists():
        stage_site_density()
    else:
        print("[3/4] documented site density — cached", flush=True)
    if args.skip_detector:
        print("[4/4] OOF detector — skipped", flush=True)
    elif not (grid.CACHE / "oof_probability.npy").exists():
        stage_oof()
    else:
        print("[4/4] OOF detector — cached (check signature before using)", flush=True)
    print(f"prepare_data complete in {time.time()-t0:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
