#!/usr/bin/env python3
"""Build the GEMSDOE33 one-click candidate GeoTIFF.

Emits the frozen candidate (default C2: h27-4 base + stepover relay-bridge
dots that passed the local P1/P2 proxy gate in evidence/holdout33.json) as a
single-band float32 GeoTIFF on the sample grid. The project's conservative
upload-safe policy enforces finite [0, 1] values over the full array and zero
outside the survey footprint. The owner observed a range-validation error for
an earlier NaN-outside file (IR-PORTAL-01); the cause was not confirmed by the
organizer. This local build/audit is not organizer approval.

The file is written to docs/downloads/ with a content-id derived from the
SHA-256 of the emitted array, then format-audited with validate_submission.py.

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default="C2")
    args = ap.parse_args()

    arr, build_report = BUILDERS[args.candidate.upper()]()
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
    name = f"gems33-{args.candidate.lower()}-stepover-relay-{stamp}-{content_id}.tif"
    if args.candidate.upper() == "C0":
        name = f"gems33-c0-scored-reference-{stamp}-{content_id}.tif"
    downloads = ROOT / "docs" / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    out_path = downloads / name
    with rasterio.open(out_path, "w", **profile) as ds:
        ds.write(out_arr, 1)

    receipt = {
        "file": f"docs/downloads/{name}",
        "candidate": args.candidate.upper(),
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
