#!/usr/bin/env python3
"""Verify data placement and publish the grid receipt.

Checks that the core competition mirrors are present with the expected grid
(EPSG:32611, 100 m, 3292 x 3730, aligned bounds) and writes
evidence/data_placement.json. No organiser service is contacted.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems33.grid import data_dir  # noqa: E402

EXPECTED = {
    "crs": "EPSG:32611",
    "width": 3292,
    "height": 3730,
    "res": (100.0, 100.0),
    "bounds": (243350.0, 4135550.0, 572550.0, 4508550.0),
}

CORE = {
    "training_features": ("core/training_features.tif", 19, "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5"),
    "labels": ("core/labels.tif", 1, "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093"),
    "sample_submission": ("core/sample_submission.tif", 1, "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    report = {"checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "data_dir": str(data_dir()), "files": {}, "pass": True}
    for name, (rel, bands, sha) in CORE.items():
        path = data_dir() / rel
        entry: dict = {"path": rel, "present": path.is_file()}
        if path.is_file():
            with rasterio.open(path) as ds:
                entry.update({
                    "crs": ds.crs.to_string() if ds.crs else None,
                    "width": ds.width, "height": ds.height,
                    "res": list(ds.res), "bounds": list(ds.bounds),
                    "bands": ds.count, "dtype": ds.dtypes[0],
                })
            entry["sha256_match"] = sha256_file(path) == sha
            entry["grid_match"] = (
                entry["crs"] == EXPECTED["crs"] and entry["width"] == EXPECTED["width"]
                and entry["height"] == EXPECTED["height"]
                and tuple(entry["res"]) == EXPECTED["res"]
                and tuple(entry["bounds"]) == EXPECTED["bounds"]
                and entry["bands"] == bands)
            entry["ok"] = entry["sha256_match"] and entry["grid_match"]
        else:
            entry["ok"] = False
        report["files"][name] = entry
        report["pass"] = report["pass"] and entry["ok"]
    out = ROOT / "evidence" / "data_placement.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
