#!/usr/bin/env python3
"""Restore and verify the nine focus-site duplicate-guard rasters.

The files are pinned public GitHub owner artifacts, not organizer-authenticated
submissions. They are comparison-only: never features, labels, or score receipts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import rasterio

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "focus_rasters_20261025.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(entry: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".partial")
    partial.unlink(missing_ok=True)
    try:
        if entry["repo"] == "buffedlizard55-lab/GEMSDOE33":
            source = ROOT / entry["path"]
            if not source.is_file():
                raise FileNotFoundError(source)
            shutil.copyfile(source, partial)
        else:
            endpoint = (
                f"repos/{entry['repo']}/contents/{entry['path']}?ref={entry['commit']}"
            )
            with partial.open("wb") as output:
                subprocess.run(
                    ["gh", "api", endpoint, "-H", "Accept: application/vnd.github.raw"],
                    stdout=output,
                    check=True,
                )
        actual = sha256_file(partial)
        if actual != entry["sha256"]:
            raise ValueError(
                f"SHA-256 mismatch for {entry['id']}: {actual} != {entry['sha256']}"
            )
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)


def verify_grid(path: Path, template: Path) -> dict:
    with rasterio.open(template) as target, rasterio.open(path) as source:
        same = (
            source.count == 1
            and source.shape == target.shape
            and source.crs == target.crs
            and source.transform == target.transform
        )
        return {
            "single_band": source.count == 1,
            "shape": list(source.shape),
            "crs": str(source.crs),
            "transform": list(source.transform)[:6],
            "matches_template_grid": bool(same),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    template = ROOT / "data" / "sample_submission.tif"
    if not template.is_file():
        raise SystemExit("Missing data/sample_submission.tif; run restore_data.py first")
    rows = []
    for entry in manifest["rasters"]:
        path = ROOT / entry["cache_path"]
        status = "verified-existing"
        if not path.is_file() or sha256_file(path) != entry["sha256"]:
            if args.verify_only:
                raise SystemExit(f"Missing or mismatched cache file: {path}")
            fetch(entry, path)
            status = "restored-and-verified"
        grid = verify_grid(path, template)
        if not grid["matches_template_grid"]:
            raise SystemExit(f"Grid mismatch: {path}")
        rows.append(
            {
                "id": entry["id"],
                "path": entry["cache_path"],
                "sha256": sha256_file(path),
                "status": status,
                "grid": grid,
            }
        )
        print(f"{entry['id']}: {status}", flush=True)
    receipt = {
        "schema": 1,
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "scope": "owner-published focus rasters; duplicate guard only",
        "score_authentication": "not performed",
        "rasters": rows,
        "pass": True,
    }
    out = ROOT / ".cache" / "focus_registry" / "restore_receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"verified": len(rows), "pass": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
