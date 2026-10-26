#!/usr/bin/env python3
"""Fetch the 12 pinned focus-site reference rasters for the uniqueness screen.

Sources are the pinned owner Pages/GitHub mirrors recorded in
registry/focus_rasters_20261025.json (hashes authenticate mirror bytes only;
none are organizer-authenticated). Fetches go through api.github.com raw
endpoints; no DrivenData contact is made. Previously fetched files are skipped
when their recorded SHA-256 matches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REGISTRY = ROOT / "registry" / "focus_rasters_20261025.json"
DEST = ROOT / "data" / "focus_registry"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--manifest",
        type=Path,
        default=REGISTRY,
        help="Registry manifest to restore (default: the 12-raster 2026-10-25 manifest). "
        "Each entry's own 'dest' path is honoured verbatim so newer manifests (e.g. the "
        "21-raster registry/focus_rasters_20261026.json, which stores five entries under "
        "'.cache/focus_registry_20261026/') resolve correctly without a private fork.",
    )
    args = ap.parse_args()
    args.manifest = args.manifest.resolve()
    manifest = json.loads(args.manifest.read_text())
    results = []
    for entry in manifest["rasters"]:
        dest_rel = entry.get("dest") or entry.get("local_path")
        dest = ROOT / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        expected = entry["sha256"]
        status = ""
        if dest.is_file():
            actual = sha256_file(dest)
            expected_bytes = entry.get("bytes", dest.stat().st_size)
            if actual == expected and dest.stat().st_size == expected_bytes:
                status = "already-verified"
            else:
                dest.unlink()
                status = "hash-mismatch-refetch"
        if status != "already-verified":
            if "repo" in entry:
                url = f"https://api.github.com/repos/{entry['repo']}/contents/{entry['path']}?ref={entry['ref']}"
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_name(dest.name + ".partial")
                try:
                    subprocess.run(
                        ["gh", "api", url, "-H", "Accept: application/vnd.github.raw"],
                        stdout=open(tmp, "wb"),
                        check=True,
                    )
                    if tmp.stat().st_size == 0:
                        raise RuntimeError(f"empty object for {entry['id']}")
                    actual_bytes = tmp.stat().st_size
                    actual = sha256_file(tmp)
                    if actual_bytes != entry["bytes"] or actual != expected:
                        raise ValueError(
                            f"pin mismatch for {entry['id']}: bytes {actual_bytes}/{entry['bytes']}; "
                            f"sha256 {actual}/{expected}"
                        )
                    tmp.replace(dest)
                    status = "fetched-and-verified"
                finally:
                    tmp.unlink(missing_ok=True)
            else:
                # Local entry (e.g. G33-h33d, or any GEMSDOE33-local history raster already
                # checked into docs/downloads/): verify the pinned local path in place.
                src = ROOT / entry.get("local_path", dest_rel)
                actual = sha256_file(src)
                actual_bytes = src.stat().st_size
                status = ("local-verified" if (actual == expected and actual_bytes == entry.get("bytes", actual_bytes))
                          else "local-mismatch")
                if status == "local-verified" and src.resolve() != dest.resolve():
                    import shutil
                    shutil.copy2(src, dest)
                    status = "local-copied-and-verified"
        results.append({"id": entry["id"], "site": entry["site"], "file": dest.name,
                        "bytes": dest.stat().st_size, "sha256": sha256_file(dest), "status": status})
        print(f"{entry['id']} ({entry['site']}): {status} ({dest.stat().st_size:,} B)", flush=True)
    receipt_dir = args.manifest.parent.parent / ".cache"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    (receipt_dir / f"fetch_receipt_{args.manifest.stem}.json").write_text(
        json.dumps({"fetched_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
                    "manifest": str(args.manifest.relative_to(ROOT)),
                    "files": results}, indent=2) + "\n")
    fails = [r for r in results if not r["status"].endswith("verified")]
    print(f"registry rasters: {len(results)} total, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
