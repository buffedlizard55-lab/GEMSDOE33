#!/usr/bin/env python3
"""Verify the local owner-mirror pins and record grid/footprint/nodata observations.

This audit proves only that local bytes match the registered owner mirrors. It does not authenticate
organizer origin, licence, or portal behavior. Outputs a small JSON receipt suitable for review.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "data_manifest.json"
DATA = ROOT / "data"
SENTINEL = np.float32(-3.4028234663852886e38)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pins = []
    errors = []
    for entry in manifest["files"]:
        path = DATA / entry["dest"]
        if not path.is_file():
            errors.append(f"missing: {entry['id']} ({entry['dest']})")
            continue
        size = path.stat().st_size
        digest = sha256(path)
        passed = size == int(entry["bytes"]) and digest == entry["sha256"]
        pins.append({"id": entry["id"], "path": entry["dest"], "bytes": size,
                     "sha256": digest, "pass": passed})
        if not passed:
            errors.append(f"pin mismatch: {entry['id']}")

    with rasterio.open(DATA / "sample_submission.tif") as sample_src:
        sample = sample_src.read(1)
        sample_meta = {
            "width": sample_src.width, "height": sample_src.height,
            "count": sample_src.count, "dtype": sample_src.dtypes[0],
            "crs": str(sample_src.crs), "transform": list(sample_src.transform)[:6],
        }
    with rasterio.open(DATA / "labels.tif") as label_src:
        labels = label_src.read(1) > 0
    footprint = np.isfinite(sample)
    sample_positive = footprint & (sample > 0)
    label_positive = footprint & labels
    disagreement = sample_positive ^ label_positive

    band_rows = []
    with rasterio.open(DATA / "training_features.tif") as train_src:
        train_meta = {
            "width": train_src.width, "height": train_src.height,
            "count": train_src.count, "dtype": train_src.dtypes[0],
            "crs": str(train_src.crs), "transform": list(train_src.transform)[:6],
            "nodata": train_src.nodata,
            "descriptions": list(train_src.descriptions),
        }
        for index in range(1, train_src.count + 1):
            arr = train_src.read(index)
            sentinel = (arr <= SENTINEL * np.float32(0.999))
            inside_sentinel = footprint & sentinel
            band_rows.append({
                "index": index,
                "description": train_src.descriptions[index - 1],
                "non_sentinel_finite_cells_in_template": int((footprint & np.isfinite(arr) & ~sentinel).sum()),
                "sentinel_cells_in_template": int(inside_sentinel.sum()),
                "nan_or_inf_cells_in_template": int((footprint & ~np.isfinite(arr)).sum()),
                "sentinel_cells_outside_template": int((~footprint & sentinel).sum()),
            })

    report = {
        "schema": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidence_class": "MEASURED from local owner-mirror bytes",
        "provenance_warning": manifest["provenance_warning"],
        "registered_inputs": {"expected": len(manifest["files"]), "verified": sum(p["pass"] for p in pins),
                               "pins": pins},
        "sample_mirror": {
            **sample_meta,
            "finite_footprint_cells": int(footprint.sum()),
            "nan_outside_cells": int((~footprint).sum()),
            "positive_cells": int(sample_positive.sum()),
        },
        "labels_mirror": {"positive_cells_within_template": int(label_positive.sum())},
        "sample_vs_labels": {
            "positive_set_disagreement_cells": int(disagreement.sum()),
            "exact_positive_set_match": bool(not disagreement.any()),
        },
        "training_mirror": {**train_meta, "per_band_coverage": band_rows},
        "errors": errors,
        "pass": not errors and bool(not disagreement.any()),
    }
    out = ROOT / "evidence" / "input_grid_audit.json"
    out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"verified {report['registered_inputs']['verified']}/{report['registered_inputs']['expected']} owner-mirror pins")
    print(f"template finite cells: {report['sample_mirror']['finite_footprint_cells']:,}; "
          f"sample/labels positive-set disagreements: {report['sample_vs_labels']['positive_set_disagreement_cells']:,}")
    print(f"wrote {out}; pass={report['pass']}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
