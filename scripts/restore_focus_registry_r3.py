#!/usr/bin/env python3
"""Restore and SHA-256-verify every raster in the Round 3 duplicate-guard registry.

Registry = the pinned 21-raster ``registry/focus_rasters_20261026.json`` plus this repo's own
2026-10-26 ``A33-R2-CSHT`` artifact (22 rasters total), written to
``registry/focus_rasters_20261026_r3.json``. Remote entries are fetched from pinned public GitHub
commits with ``gh api`` (owner mirrors, NOT organizer-authenticated). Local entries are verified in
place. Comparison-only: these rasters are never used as features, labels or score receipts.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_MANIFEST = ROOT / "registry" / "focus_rasters_20261026.json"
R3_MANIFEST = ROOT / "registry" / "focus_rasters_20261026_r3.json"
R2_LOCAL = {
    "id": "G33-a33-r2-csht-0b78c04d5fad",
    "site": "GEMSDOE33",
    "local_path": "docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif",
    "sha256": "14ab452c22aaf07444cd02e589fce4627d682e99f44c63e78dc1383955e0c602",
    "reported_dti": None,
    "reported_dti_evidence_class": "UNSCORED_LOCAL_RESEARCH_DUPLICATE_BLOCKED",
    "cohort": "local_gemsdoe33_history",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest() -> dict:
    base = json.loads(BASE_MANIFEST.read_text())
    rasters = list(base["rasters"])
    if not any(r["id"] == R2_LOCAL["id"] for r in rasters):
        rasters.append(R2_LOCAL)
    return {
        "schema_version": 3,
        "as_of": "2026-10-26",
        "derived_from": {
            "path": "registry/focus_rasters_20261026.json",
            "sha256": sha256_file(BASE_MANIFEST),
        },
        "scope": base["scope"] + " Round 3 adds this repo's own A33-R2-CSHT artifact (22 rasters).",
        "rasters": rasters,
    }


def restore(entry: dict) -> dict:
    rel = entry.get("local_path") or entry.get("dest")
    path = ROOT / rel
    if "local_path" not in entry and not (path.is_file() and sha256_file(path) == entry["sha256"]):
        path.parent.mkdir(parents=True, exist_ok=True)
        ref = entry.get("ref") or entry.get("commit")
        endpoint = f"repos/{entry['repo']}/contents/{entry['path']}?ref={ref}"
        tmp = path.with_name(path.name + ".partial")
        with tmp.open("wb") as out:
            subprocess.run(["gh", "api", endpoint, "-H", "Accept: application/vnd.github.raw"],
                           stdout=out, check=True)
        tmp.replace(path)
    actual = sha256_file(path)
    if actual != entry["sha256"]:
        raise SystemExit(f"SHA-256 mismatch for {entry['id']}: {actual} != {entry['sha256']}")
    return {"id": entry["id"], "path": rel, "sha256": actual, "status": "verified"}


def main() -> int:
    manifest = build_manifest()
    text = json.dumps(manifest, indent=2) + "\n"
    if not R3_MANIFEST.is_file() or R3_MANIFEST.read_text() != text:
        R3_MANIFEST.write_text(text)
    rows = [restore(e) for e in manifest["rasters"]]
    print(json.dumps({"manifest": str(R3_MANIFEST.relative_to(ROOT)),
                      "manifest_sha256": sha256_file(R3_MANIFEST),
                      "n_rasters": len(rows), "rows": rows}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
