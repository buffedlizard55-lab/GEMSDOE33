#!/usr/bin/env python3
"""Build a format-checked, easy-to-download D2.8 reference submission package.

This intentionally packages the existing 44,090-pixel D2.8 owner-mirror emission rather than
promoting a new strategy. The only purported improvement generated in the first pass was evaluated
with a truth-conditioned, radius-tuned holdout and has been withdrawn (see
``evidence/first_pass_disposition.json`` and ``registry/irregularities.json``). No new strategy is
slot-approved by this session.

The primary ``-nan.tif`` follows the official format literally: one float32 band, EPSG:32611, exact
template grid, finite values in [0,1] on the footprint, NaN outside. The ``-zeros.tif`` is supplied
only as an alternate if the portal's range checker mishandles outside-footprint NaN; it has 0
outside and does not match the literal null/NaN wording as closely.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33 import grid, submission  # noqa: E402

DOWNLOADS = ROOT / "docs" / "downloads"
NAME = "gemsdoe33-d28-reference-20261004"
NOTE = ("GEMSDOE33 D2.8 reference | owner-mirror emission; 0.2600 is owner-reported, "
        "score/file pairing unconfirmed | format-checked, not a new model | id {cid}")


def main() -> int:
    t0 = time.time()
    footprint = grid.template_footprint()
    source, _ = grid.read_raster("dotted_h19_5_d2_8_nan.tif")
    source = np.asarray(source, dtype=np.float32)

    # Strict source checks before repackaging: no sentinel, no internal NaN, no illegal probability.
    if np.isnan(source[footprint]).any() or not np.isfinite(source[footprint]).all():
        raise SystemExit("source D2.8 emission has NaN/Inf inside the template footprint")
    if np.any((source[footprint] < 0) | (source[footprint] > 1)):
        raise SystemExit("source D2.8 emission has values outside [0,1]")
    if np.isfinite(source[~footprint]).any():
        print("warning: source has finite outside-footprint values; writer will null them", flush=True)

    positive = (source > 0) & footprint
    n_positive = int(positive.sum())
    if n_positive != 44090:
        raise SystemExit(f"expected owner-mirror D2.8 count 44,090, found {n_positive:,}")

    # The note uses the mask hash, which the package writer fills before the 200-char check.
    record = submission.build_package(positive, None, NAME, DOWNLOADS, NOTE)
    cid = record["content_id"]
    # Re-read the authoritative receipt after writing.
    receipt_path = DOWNLOADS / f"receipt-{NAME}-{cid}.json"
    receipt = json.loads(receipt_path.read_text())
    for variant in ("nan", "zeros"):
        if not receipt[variant]["pass"]:
            raise SystemExit(f"{variant} TIFF failed validation: {receipt[variant]['errors']}")

    nan_file = Path(receipt["nan"]["file"]).name
    zeros_file = Path(receipt["zeros"]["file"]).name
    note = receipt["note"]
    note_file = DOWNLOADS / f"note-{NAME}-{cid}.txt"
    note_file.write_text(note + "\n")

    manifest = {
        "schema": 1,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "REFERENCE_BASELINE_ONLY — no new candidate passed an independent slot-approval gate",
        "evidence_class": "OWNER-MIRROR for source model and reported 0.2600; organizer score/file pairing unverified",
        "source": {
            "file": "data/dotted_h19_5_d2_8_nan.tif",
            "sha256": "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8",
            "reported_score": 0.2600,
            "reported_score_class": "OWNER-REPORT; no organizer receipt in this repository",
            "note": "the score is not authenticated as the score for these exact bytes"
        },
        "grid": {
            "crs": "EPSG:32611", "shape": [3730, 3292], "pixel_m": 100,
            "transform_gdal": [243350.0, 100.0, 0.0, 4508550.0, 0.0, -100.0],
            "bands": 1, "dtype": "float32", "footprint_cells": int(footprint.sum())
        },
        "name": NAME,
        "note": note,
        "note_chars": len(note),
        "note_file": note_file.name,
        "emitted_pixels": n_positive,
        "recommended": nan_file,
        "recommended_variant": "-nan.tif — official wording says outside data is null or NaN",
        "alternate": zeros_file,
        "alternate_warning": "0.0 outside footprint; provided only as a troubleshooting alternative",
        "artifacts": [
            {"file": nan_file, "zip": f"{Path(nan_file).stem}.zip", "sha256": receipt["nan"]["sha256"],
             "bytes": receipt["nan"]["bytes"], "outside": "NaN", "validation": receipt["nan"]},
            {"file": zeros_file, "zip": f"{Path(zeros_file).stem}.zip", "sha256": receipt["zeros"]["sha256"],
             "bytes": receipt["zeros"]["bytes"], "outside": "0.0", "validation": receipt["zeros"]}
        ],
    }
    (DOWNLOADS / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"primary: {nan_file} ({receipt['nan']['bytes']:,} B; sha256 {receipt['nan']['sha256']})")
    print(f"alternate: {zeros_file} ({receipt['zeros']['bytes']:,} B; sha256 {receipt['zeros']['sha256']})")
    print(f"positive pixels: {n_positive:,}; note: {len(note)}/200 chars")
    print(f"both artifacts: {receipt['all_checks_pass']}; wrote manifest in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
