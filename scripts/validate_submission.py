#!/usr/bin/env python3
"""Exact-file format audit for GEMS competition submissions.

Checks the rules stated on the official problem page
(https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/):
  * single-band GeoTIFF, float32
  * same CRS as training data (EPSG:32611), same 100 m resolution
  * same shape, geotransform and bounds as the sample submission template
  * values in [0, 1]

PLUS the portal behaviour recorded as IR-PORTAL-01 by the owner:
the upload form validates the WHOLE array against [0, 1] and rejects NaN
("Predicted values must be in range [0, 1]"). A submission must therefore be
finite everywhere — zero (never NaN) outside the survey footprint.

This audit is format-only: it is not a score and not an approval.

Usage:
  PYTHONPATH=src python scripts/validate_submission.py --submission <file.tif> \
      [--template <sample_submission.tif>] [--out evidence/format_check.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems33.grid import data_dir


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(submission: Path, template: Path) -> dict:
    checks: dict[str, object] = {"file": str(submission), "sha256": sha256_file(submission),
                                 "bytes": submission.stat().st_size}
    with rasterio.open(template) as tds, rasterio.open(submission) as ds:
        arr = ds.read(1)
        tmpl = tds.read(1)
        footprint = np.isfinite(tmpl)

        checks["bands"] = ds.count
        checks["dtype"] = ds.dtypes[0]
        checks["crs"] = ds.crs.to_string() if ds.crs else None
        checks["template_crs"] = tds.crs.to_string() if tds.crs else None
        checks["shape"] = list(ds.shape)
        checks["template_shape"] = list(tds.shape)
        checks["transform"] = list(ds.transform)[:6]
        checks["template_transform"] = list(tds.transform)[:6]
        checks["bounds"] = list(ds.bounds)
        checks["template_bounds"] = list(tds.bounds)

        finite = np.isfinite(arr)
        inside = arr[footprint]
        checks["all_finite"] = bool(finite.all())
        checks["nan_count"] = int((~finite).sum())
        checks["min"] = float(np.nanmin(arr)) if finite.any() else None
        checks["max"] = float(np.nanmax(arr)) if finite.any() else None
        checks["in_range_0_1_whole_array"] = bool(finite.all() and (arr.min() >= 0.0) and (arr.max() <= 1.0))
        checks["in_range_0_1_footprint"] = bool(np.isfinite(inside).all() and (inside.min() >= 0) and (inside.max() <= 1))
        checks["emitted_pixels"] = int((arr > 0).sum())
        checks["emitted_fraction_of_footprint"] = float((arr > 0).sum() / footprint.sum())
        checks["outside_footprint_all_zero"] = bool((arr[~footprint] == 0).all()) if (~footprint).any() else True

    checks["pass"] = all([
        checks["bands"] == 1,
        checks["dtype"] == "float32",
        checks["crs"] == checks["template_crs"] == "EPSG:32611",
        checks["shape"] == checks["template_shape"],
        checks["transform"] == checks["template_transform"],
        checks["all_finite"],
        checks["in_range_0_1_whole_array"],
    ])
    return checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission", required=True)
    ap.add_argument("--template", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    template = Path(args.template) if args.template else data_dir() / "core" / "sample_submission.tif"
    report = audit(Path(args.submission), template)
    text = json.dumps(report, indent=1)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    print(text)
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
