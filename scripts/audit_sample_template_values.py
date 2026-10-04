#!/usr/bin/env python3
"""Record whether the restored sample template unexpectedly mirrors labels.

This audit is diagnostic only. Production code must use sample_submission.tif
for its finite footprint/grid metadata and must never treat its values as truth.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems33.grid import data_dir  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(template_path: Path, labels_path: Path) -> dict:
    with rasterio.open(template_path) as sample_ds, rasterio.open(labels_path) as label_ds:
        sample = sample_ds.read(1)
        labels = label_ds.read(1)
        same_grid = (
            sample_ds.shape == label_ds.shape
            and sample_ds.transform == label_ds.transform
            and sample_ds.crs == label_ds.crs
        )
    finite = np.isfinite(sample)
    finite_values = sample[finite]
    label_on_footprint = labels[finite] if same_grid else np.asarray([], dtype=labels.dtype)
    exact_match = bool(same_grid and finite.any() and np.array_equal(finite_values, label_on_footprint))
    return {
        "checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "template": str(template_path.relative_to(ROOT) if template_path.is_relative_to(ROOT) else template_path),
        "labels": str(labels_path.relative_to(ROOT) if labels_path.is_relative_to(ROOT) else labels_path),
        "template_sha256": sha256_file(template_path),
        "labels_sha256": sha256_file(labels_path),
        "same_grid": bool(same_grid),
        "template_finite_footprint_pixels": int(finite.sum()),
        "template_nonfinite_pixels": int((~finite).sum()),
        "template_finite_value_counts": {
            str(value): int(count) for value, count in zip(*np.unique(finite_values, return_counts=True))
        },
        "labels_values_on_template_footprint": {
            str(value): int(count) for value, count in zip(*np.unique(label_on_footprint, return_counts=True))
        },
        "sample_equals_labels_on_finite_footprint": exact_match,
        "warning": (
            "The sample template is an anomalous exact value-copy of the label raster on its finite footprint. "
            "Use it only for the finite-mask/grid metadata; never use sample values as training truth, holdout truth, "
            "or candidate-selection labels."
            if exact_match else "No exact sample/label equality found on the finite footprint."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, default=data_dir() / "core" / "sample_submission.tif")
    parser.add_argument("--labels", type=Path, default=data_dir() / "core" / "labels.tif")
    parser.add_argument("--out", type=Path, default=ROOT / "evidence" / "sample_template_label_overlap.json")
    args = parser.parse_args()
    report = audit(args.template, args.labels)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
