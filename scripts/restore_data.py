#!/usr/bin/env python3
"""Restore hash-pinned public mirrors into the local data directory.

This script NEVER contacts DrivenData. It only pulls public GitHub blobs
(owner-supplied mirrors) and verifies SHA-256 where a pin exists. A hash match
proves equality with the registered mirror — it does not authenticate the
mirror against the competition organizer.

Default data dir: $GEMS_DATA_DIR or <repo>/.cache/gemsdata (snapshot-excluded).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "data_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gh_blob(repo: str, ref: str, remote_path: str, out: Path) -> None:
    """Download a file via the GitHub API (works even where raw.githubusercontent is blocked)."""
    import base64

    if shutil.which("gh"):
        try:
            args = ["gh", "api", f"repos/{repo}/contents/{remote_path}", "--jq", ".sha"]
            if ref and ref != "main":
                args += ["-f", f"ref={ref}"]
            git_sha = subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()
            raw = subprocess.run(["gh", "api", f"repos/{repo}/git/blobs/{git_sha}", "--jq", ".content"],
                                 check=True, capture_output=True, text=True).stdout
            out.write_bytes(base64.b64decode(raw))
            return
        except subprocess.CalledProcessError:
            pass
    import urllib.request
    url = f"https://raw.githubusercontent.com/{repo}/{ref or 'main'}/{remote_path}"
    req = urllib.request.Request(url, headers={"User-Agent": "GEMSDOE33-research/1.0"})
    with urllib.request.urlopen(req, timeout=600) as resp, out.open("wb") as fh:
        shutil.copyfileobj(resp, fh, length=1 << 20)


def restore(entry: dict, data_dir: Path) -> dict:
    dest = data_dir / entry["dest"]
    expected_bytes = int(entry.get("bytes", 0))
    if dest.is_file() and dest.stat().st_size == expected_bytes:
        expected = entry.get("sha256")
        if expected in (None, "", "unverified-this-session", "refetch-verify"):
            return {"id": entry["id"], "status": "present-size-ok", "sha256_pinned": False}
        if sha256_file(dest) == expected:
            return {"id": entry["id"], "status": "already-verified"}
        dest.unlink()

    dest.parent.mkdir(parents=True, exist_ok=True)
    if "parts" in entry:
        tmp = dest.with_name(dest.name + ".assembling")
        with tmp.open("wb") as out_fh:
            for part in entry["parts"]:
                part_file = dest.with_name(Path(part["path"]).name + ".partial")
                gh_blob(part["repo"], part["ref"], part["path"], part_file)
                if part_file.stat().st_size != part["bytes"]:
                    raise RuntimeError(f"part size mismatch: {part['path']}")
                with part_file.open("rb") as pf:
                    shutil.copyfileobj(pf, out_fh, length=1 << 20)
                part_file.unlink()
        tmp.replace(dest)
    elif "blob" in entry and entry["blob"].get("sha") not in (None, "sha:unpinned"):
        gh_blob(entry["blob"]["repo"], entry["blob"]["ref"], entry["blob"]["path"], dest)
    elif "blob" in entry:
        gh_blob(entry["blob"]["repo"], entry["blob"]["ref"], entry["blob"]["path"], dest)
    elif "url" in entry:
        import urllib.request
        req = urllib.request.Request(entry["url"], headers={"User-Agent": "GEMSDOE33-research/1.0"})
        with urllib.request.urlopen(req, timeout=1800) as resp, dest.open("wb") as fh:
            shutil.copyfileobj(resp, fh, length=1 << 20)
    else:
        raise RuntimeError(f"no source for {entry['id']}")

    result = {"id": entry["id"], "status": "fetched", "bytes": dest.stat().st_size}
    expected = entry.get("sha256")
    if expected not in (None, "", "unverified-this-session", "refetch-verify"):
        actual = sha256_file(dest)
        result["sha256"] = actual
        if actual != expected:
            dest.unlink()
            raise RuntimeError(f"sha256 mismatch for {entry['id']}: {actual} != {expected}")
        result["status"] = "fetched-verified"
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--only", default=None, help="comma-separated ids")
    ap.add_argument("--group", default=None, help="'core' for training/labels/template only")
    args = ap.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else ROOT / ".cache" / "gemsdata"
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    ids = set(args.only.split(",")) if args.only else None
    if args.group == "core":
        ids = {"training_features", "labels", "sample_submission"}
    report = []
    for entry in manifest["files"]:
        if ids and entry["id"] not in ids:
            continue
        try:
            report.append(restore(entry, data_dir))
        except Exception as exc:  # noqa: BLE001 - report and continue
            report.append({"id": entry["id"], "status": "FAILED", "error": str(exc)})
    print(json.dumps(report, indent=1))
    return 0 if all(r["status"] != "FAILED" for r in report) else 1


if __name__ == "__main__":
    sys.exit(main())
