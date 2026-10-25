#!/usr/bin/env python3
"""Read pinned PRIOR ART, not a new experiment or submission. No DrivenData calls.

Reproduce: restore_data.py --group core; this script --fetch
Only owner-mirror bytes are authenticated by these hashes. No score is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe33.novelty import binary_comparison  # noqa: E402
from restore_data import fetch_to  # noqa: E402
from validate_submission import audit  # noqa: E402

MANIFEST = ROOT / "registry/focus_rasters_20261025.json"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true", help="fetch pinned owner references from GitHub")
    args = ap.parse_args()
    template = ROOT / "data/sample_submission.tif"
    with rasterio.open(template) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        labels = ds.read(1) > 0
    specs = json.loads(MANIFEST.read_text())["rasters"]
    masks, records = {}, []
    for spec in specs:
        path = ROOT / spec.get("local_path", spec.get("dest", ""))
        if not path.exists() and args.fetch and "repo" in spec:
            fetch_to(spec["repo"], spec["ref"], spec["path"], path)
        if sha256(path) != spec["sha256"]:
            raise ValueError(f"Pin mismatch: {path}")
        fmt = audit(path, template)
        if not fmt["pass"]:
            raise ValueError(f"Invalid reference grid/values: {path}: {fmt}")
        with rasterio.open(path) as ds:
            arr = ds.read(1)
        if not np.isin(arr[footprint], (0, 1)).all():
            raise ValueError(f"Binary-only forensic comparison received soft raster: {path}")
        mask = (arr > 0) & footprint
        masks[spec["id"]] = mask
        records.append({"id": spec["id"], "site": spec["site"], "sha256": spec["sha256"],
                        "dots": int(mask.sum()), "on_catalogue": int((mask & labels).sum()),
                        "format": fmt})
    pairs = []
    # One exact <=3-px Euclidean disk, not a square/Chebyshev neighborhood.
    yy, xx = np.mgrid[-3:4, -3:4]
    disk = yy * yy + xx * xx <= 9
    for other_id, other in masks.items():
        near = binary_dilation(other, structure=disk)
        for candidate_id, candidate in masks.items():
            if candidate_id == other_id:
                continue
            cmp = binary_comparison(candidate, other, footprint, near_other=near)
            pairs.append({"candidate": candidate_id, "registry": other_id, **cmp})
    base = masks["G28-8acb75e1f2cc"]
    b2 = masks["G32-e5eb6e7e"]
    expected = base & (distance_transform_edt(~labels) > 2) & footprint
    recipe = {"recipe": "GEMSDOE28 H27-4 dots AND Euclidean distance from full catalogue >2 px",
              "pixel_exact_match": bool(np.array_equal(expected, b2)),
              "disagreement_cells": int((expected ^ b2).sum()),
              "base_dots": int(base.sum()), "b2_dots": int(b2.sum()),
              "deleted_dots": int((base & ~b2).sum()), "added_dots": int((b2 & ~base).sum())}
    report = {"schema_version": 1, "as_of": "2026-10-25", "kind": "PRIOR-ART-FORENSICS, NOT HOLDOUT-DTI",
              "scope": "12 named reference rasters across all nine requested sites; not complete global uniqueness registry",
              "score_receipts": "NONE; no ORGANIZER-CONFIRMED score or causal score explanation",
              "manifest_sha256": sha256(MANIFEST), "footprint_cells": int(footprint.sum()),
              "rasters": records, "b2_recipe": recipe, "ordered_pairs": pairs,
              "new_prediction_surface_built": False, "new_submission_written": False}
    out = ROOT / "evidence/focus_raster_audit_20261025.json"
    out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(recipe, indent=2))
    print(f"Audited {len(records)} references and {len(pairs)} ordered pairs; wrote {out}")
    return 0 if recipe["pixel_exact_match"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
