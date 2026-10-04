#!/usr/bin/env python3
"""Build a research candidate GeoTIFF and run its local format audit.

C2 remains reproducible as a research experiment, but its earlier P1 proxy
PASS was withdrawn after a fold/source-leakage audit. The file is not cleared
for a submission slot. This builder checks only the single-band float32 grid
and local value policy; it is not organizer approval. The project's
conservative policy enforces finite [0, 1] values over the full array and zero
outside the survey footprint after the owner observed a range-validation error
for an earlier NaN-outside file (IR-PORTAL-01). The cause was not confirmed by
the organizer.

The file is written to archive/legacy_candidates/ with a content-id derived
from the SHA-256 of the emitted array, then format-audited with validate_submission.py.
It is never written to the recommended docs/downloads/ directory.

Usage:
  PYTHONPATH=src python scripts/build_submission33.py [--candidate C2]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems33.candidates import (c0_control, c1_h38_corroborated, c2_stepover_bridges,  # noqa: E402
                               c3_rung30_repack)
from gems33.grid import data_dir  # noqa: E402

BUILDERS = {
    "C0": lambda: (c0_control(), {"candidate": "C0_scored_reference"}),
    "C1": c1_h38_corroborated,
    "C2": c2_stepover_bridges,
    "C3": c3_rung30_repack,
}
FILE_SLUGS = {
    "C0": "c0-scored-reference",
    "C1": "c1-h38-corroborated",
    "C2": "c2-stepover-relay",
    "C3": "c3-rung30-repack",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default="C2")
    args = ap.parse_args()
    candidate = args.candidate.upper()
    if candidate not in BUILDERS:
        ap.error(f"unknown candidate: {args.candidate}")

    arr, build_report = BUILDERS[candidate]()
    dots = arr > 0
    content_id = hashlib.sha256(dots.tobytes()).hexdigest()[:12]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")

    template_path = data_dir() / "core" / "sample_submission.tif"
    with rasterio.open(template_path) as tds:
        profile = tds.profile.copy()
        footprint = np.isfinite(tds.read(1))

    out_arr = np.zeros(profile["height"] * profile["width"], dtype=np.float32).reshape(profile["height"], profile["width"])
    out_arr[dots & footprint] = 1.0
    n_outside = int((dots & ~footprint).sum())

    profile.update(dtype="float32", count=1, compress="lzw", predictor=3, nodata=None)
    name = f"gems33-{FILE_SLUGS[candidate]}-{stamp}-{content_id}.tif"
    downloads = ROOT / "archive" / "legacy_candidates"
    downloads.mkdir(parents=True, exist_ok=True)
    out_path = downloads / name
    with rasterio.open(out_path, "w", **profile) as ds:
        ds.write(out_arr, 1)

    receipt = {
        "file": f"archive/legacy_candidates/{name}",
        "candidate": candidate,
        "artifact_status": "RESEARCH_BUILD_NOT_SLOT_CLEARED",
        "slot_cleared": False,
        "build": build_report,
        "content_id": content_id,
        "dots_emitted": int(dots.sum()),
        "dots_outside_footprint_dropped": n_outside,
        "sha256": hashlib.sha256(out_path.read_bytes()).hexdigest(),
        "bytes": out_path.stat().st_size,
        "built_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "local_upload_safe_policy": "finite [0,1] whole array; zero outside footprint; conservative policy after owner-observed IR-PORTAL-01, not an organizer-confirmed cause",
    }
    evidence_dir = ROOT / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    build_record = evidence_dir / f"build_{args.candidate.lower()}_{content_id}.json"
    format_record = evidence_dir / f"format_check_{args.candidate.lower()}_{content_id}.json"
    check = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_submission.py"),
         "--submission", str(out_path), "--template", str(template_path),
         "--out", str(format_record)],
        cwd=ROOT, capture_output=True, text=True)
    try:
        receipt["format_audit"] = json.loads(check.stdout)
    except json.JSONDecodeError:
        receipt["format_audit"] = {"output": check.stdout, "error": check.stderr}
    receipt["format_audit_path"] = format_record.relative_to(ROOT).as_posix()
    receipt["format_audit_pass"] = check.returncode == 0
    build_record.write_text(json.dumps(receipt, indent=1) + "\n")
    print(json.dumps(receipt, indent=1))
    return 0 if check.returncode == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
