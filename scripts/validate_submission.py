#!/usr/bin/env python3
"""Fail-closed local format audit for a GEMS competition submission GeoTIFF.

The official problem wording recorded in the source registry requires one
float32 band on the 100 m EPSG:32611 grid, probabilities in [0, 1], and null/NaN
outside the bounds. This validator checks that the footprint is finite and
in-range, and that outside cells are either null/NaN or zero. The zero variant
is available as an explicit owner-reported troubleshooting alternative; the
reported portal rejection of NaN was never confirmed by the organizer.

This checks local file structure only. It is not a competition score or
organizer approval. Use ``--strict-zero-outside`` only when intentionally
checking the troubleshooting alternative.

Usage:
  PYTHONPATH=src python scripts/validate_submission.py --submission <file.tif> \\
      [--template <sample_submission.tif>] [--out evidence/format_check.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import rasterio

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems33.grid import data_dir  # noqa: E402

TARGET_EPSG = 32611
TARGET_RESOLUTION = (100.0, 100.0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _close_tuple(left, right) -> bool:
    return len(left) == len(right) and all(
        math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1e-9)
        for a, b in zip(left, right)
    )


def audit(submission: Path, template: Path, *, strict_zero_outside: bool = False) -> dict:
    submission = Path(submission)
    template = Path(template)
    try:
        report_path = submission.resolve().relative_to(Path(__file__).resolve().parents[1]).as_posix()
    except ValueError:
        report_path = str(submission)
    checks: dict[str, object] = {
        "file": report_path,
        "sha256": sha256_file(submission),
        "bytes": submission.stat().st_size,
    }

    with rasterio.open(template) as tds, rasterio.open(submission) as ds:
        arr = ds.read(1)
        tmpl = tds.read(1)
        footprint = np.isfinite(tmpl)
        same_shape = ds.shape == tds.shape
        epsg = ds.crs.to_epsg() if ds.crs else None
        template_epsg = tds.crs.to_epsg() if tds.crs else None
        transform = tuple(ds.transform)[:6]
        template_transform = tuple(tds.transform)[:6]
        bounds = tuple(ds.bounds)
        template_bounds = tuple(tds.bounds)
        resolution = tuple(ds.res)
        template_resolution = tuple(tds.res)

        checks.update({
            "bands": ds.count,
            "dtype": ds.dtypes[0],
            "crs": ds.crs.to_string() if ds.crs else None,
            "epsg": epsg,
            "template_crs": tds.crs.to_string() if tds.crs else None,
            "template_epsg": template_epsg,
            "shape": list(ds.shape),
            "template_shape": list(tds.shape),
            "resolution": list(resolution),
            "template_resolution": list(template_resolution),
            "transform": list(transform),
            "template_transform": list(template_transform),
            "bounds": list(bounds),
            "template_bounds": list(template_bounds),
            "shape_match": bool(same_shape),
            "resolution_match": bool(_close_tuple(resolution, TARGET_RESOLUTION)
                                      and _close_tuple(resolution, template_resolution)),
            "transform_match": bool(transform == template_transform),
            "bounds_match": bool(_close_tuple(bounds, template_bounds)),
        })

        finite = np.isfinite(arr)
        finite_values = arr[finite]
        checks["all_finite"] = bool(finite.all())
        checks["nonfinite_count"] = int((~finite).sum())
        checks["min"] = float(finite_values.min()) if finite_values.size else None
        checks["max"] = float(finite_values.max()) if finite_values.size else None
        checks["in_range_0_1_whole_array"] = bool(
            finite.all() and finite_values.size > 0
            and finite_values.min() >= 0.0 and finite_values.max() <= 1.0
        )

        if same_shape:
            inside = arr[footprint]
            outside = arr[~footprint]
            checks["footprint_cells"] = int(footprint.sum())
            checks["in_range_0_1_footprint"] = bool(
                np.isfinite(inside).all() and inside.size > 0
                and inside.min() >= 0.0 and inside.max() <= 1.0
            )
            checks["outside_footprint_all_zero"] = bool(
                np.isfinite(outside).all() and np.all(outside == 0.0)
            )
            checks["outside_is_null_or_zero"] = bool(
                np.all(np.isnan(outside) | (outside == 0.0))
            )
            checks["outside_has_nan"] = bool(np.isnan(outside).any())
        else:
            checks["footprint_cells"] = int(footprint.sum())
            checks["in_range_0_1_footprint"] = False
            checks["outside_footprint_all_zero"] = False
            checks["outside_is_null_or_zero"] = False
            checks["outside_has_nan"] = False
        checks["strict_zero_outside_requested"] = bool(strict_zero_outside)
        checks["outside_policy_pass"] = bool(
            checks["outside_footprint_all_zero"] if strict_zero_outside
            else checks["outside_is_null_or_zero"]
        )

        checks["emitted_pixels"] = int((arr > 0).sum())
        checks["emitted_fraction_of_footprint"] = (
            float((arr > 0).sum() / footprint.sum()) if same_shape and footprint.any() else None
        )

    checks["pass"] = all([
        checks["bands"] == 1,
        checks["dtype"] == "float32",
        checks["epsg"] == checks["template_epsg"] == TARGET_EPSG,
        checks["shape_match"],
        checks["resolution_match"],
        checks["transform_match"],
        checks["bounds_match"],
        checks["in_range_0_1_footprint"],
        checks["outside_policy_pass"],
    ])
    return checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission", required=True)
    ap.add_argument("--template", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--strict-zero-outside", action="store_true",
                    help="require 0.0 outside the footprint (owner-reported troubleshooting policy)")
    args = ap.parse_args()

    template = Path(args.template) if args.template else data_dir() / "core" / "sample_submission.tif"
    report = audit(Path(args.submission), template, strict_zero_outside=args.strict_zero_outside)
    text = json.dumps(report, indent=1)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    print(text)
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
