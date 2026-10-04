#!/usr/bin/env python3
"""Restore sources registered in the data manifest into a local data directory.

This script NEVER contacts DrivenData. It fetches only the public GitHub or
URL mirrors listed in ``registry/data_manifest.json`` and verifies registered
SHA-256 and Git blob SHA-1 values where available. A hash match proves equality
with the registered mirror; it does not authenticate that mirror against the
competition organizer. Sources without a cryptographic pin are explicitly
reported as unpinned and must not be treated as production-verified.

Default data dir: $GEMS_DATA_DIR or <repo>/.cache/gemsdata (snapshot-excluded).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "data_manifest.json"
UNPINNED_SHA256 = {None, "", "unverified-this-session", "refetch-verify"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1(data: bytes) -> str:
    """Return Git's object SHA-1 for a blob payload (header included)."""
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def git_blob_sha1_file(path: Path) -> str:
    """Hash a file as a Git blob without loading the full file into memory."""
    size = path.stat().st_size
    digest = hashlib.sha1()
    digest.update(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _known_git_sha(value: str | None) -> str | None:
    if value and len(value) == 40 and all(c in "0123456789abcdefABCDEF" for c in value):
        return value.lower()
    return None


def gh_blob(repo: str, ref: str, remote_path: str, out: Path,
            expected_git_sha: str | None = None) -> None:
    """Fetch one public GitHub file and verify its registered Git object hash."""
    expected = _known_git_sha(expected_git_sha)
    encoded_path = urllib.parse.quote(remote_path, safe="/")
    data: bytes | None = None

    if shutil.which("gh"):
        endpoint = f"repos/{repo}/contents/{encoded_path}"
        if ref:
            endpoint += "?ref=" + urllib.parse.quote(ref, safe="")
        try:
            object_sha = subprocess.run(
                ["gh", "api", endpoint, "--jq", ".sha"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            if expected and object_sha.lower() != expected:
                raise RuntimeError(
                    f"Git blob SHA mismatch for {repo}:{remote_path}: "
                    f"manifest {expected}, API {object_sha}"
                )
            encoded = subprocess.run(
                ["gh", "api", f"repos/{repo}/git/blobs/{object_sha}", "--jq", ".content"],
                check=True, capture_output=True, text=True,
            ).stdout
            data = base64.b64decode(encoded, validate=False)
        except subprocess.CalledProcessError:
            # Public raw.githubusercontent fallback is useful when the API is
            # rate-limited; integrity is still checked below when pinned.
            data = None

    if data is None:
        url = f"https://raw.githubusercontent.com/{repo}/{ref or 'main'}/{encoded_path}"
        req = urllib.request.Request(url, headers={"User-Agent": "GEMSDOE33-research/1.0"})
        with urllib.request.urlopen(req, timeout=600) as response:
            data = response.read()

    actual_git_sha = git_blob_sha1(data)
    if expected and actual_git_sha != expected:
        raise RuntimeError(
            f"Git blob SHA mismatch for {repo}:{remote_path}: "
            f"manifest {expected}, downloaded {actual_git_sha}"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)


def _check_size(path: Path, entry: dict) -> None:
    expected_bytes = int(entry.get("bytes", 0))
    if expected_bytes and path.stat().st_size != expected_bytes:
        raise RuntimeError(
            f"size mismatch for {entry['id']}: {path.stat().st_size} != {expected_bytes}"
        )


def restore(entry: dict, data_dir: Path) -> dict:
    dest = data_dir / entry["dest"]
    expected_bytes = int(entry.get("bytes", 0))
    expected_sha = entry.get("sha256")
    sha_is_pinned = expected_sha not in UNPINNED_SHA256

    if dest.is_file():
        if not expected_bytes or dest.stat().st_size == expected_bytes:
            actual = sha256_file(dest)
            if sha_is_pinned and actual == expected_sha:
                return {"id": entry["id"], "status": "already-verified", "sha256": actual,
                        "sha256_pinned": True}
            if not sha_is_pinned:
                return {"id": entry["id"], "status": "present-unpinned", "sha256": actual,
                        "sha256_pinned": False}
        dest.unlink()

    dest.parent.mkdir(parents=True, exist_ok=True)
    if "parts" in entry:
        tmp = dest.with_name(dest.name + ".assembling")
        try:
            with tmp.open("wb") as out_fh:
                for part in entry["parts"]:
                    part_file = dest.with_name(Path(part["path"]).name + ".partial")
                    try:
                        gh_blob(part["repo"], part["ref"], part["path"], part_file,
                                expected_git_sha=part.get("sha"))
                        if part_file.stat().st_size != int(part["bytes"]):
                            raise RuntimeError(f"part size mismatch: {part['path']}")
                        if _known_git_sha(part.get("sha")) and git_blob_sha1_file(part_file) != part["sha"].lower():
                            raise RuntimeError(f"part Git blob SHA mismatch: {part['path']}")
                        with part_file.open("rb") as part_fh:
                            shutil.copyfileobj(part_fh, out_fh, length=1 << 20)
                    finally:
                        part_file.unlink(missing_ok=True)
            tmp.replace(dest)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
    elif "blob" in entry:
        blob = entry["blob"]
        gh_blob(blob["repo"], blob["ref"], blob["path"], dest,
                expected_git_sha=blob.get("sha"))
    elif "url" in entry:
        req = urllib.request.Request(entry["url"], headers={"User-Agent": "GEMSDOE33-research/1.0"})
        with urllib.request.urlopen(req, timeout=1800) as response, dest.open("wb") as fh:
            shutil.copyfileobj(response, fh, length=1 << 20)
    else:
        raise RuntimeError(f"no source for {entry['id']}")

    try:
        _check_size(dest, entry)
        actual_sha = sha256_file(dest)
        if sha_is_pinned and actual_sha != expected_sha:
            raise RuntimeError(f"sha256 mismatch for {entry['id']}: {actual_sha} != {expected_sha}")
    except Exception:
        dest.unlink(missing_ok=True)
        raise

    return {
        "id": entry["id"],
        "status": "fetched-verified" if sha_is_pinned else "fetched-unpinned",
        "bytes": dest.stat().st_size,
        "sha256": actual_sha,
        "sha256_pinned": sha_is_pinned,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--only", default=None, help="comma-separated ids")
    ap.add_argument("--group", default=None, choices=("core", "candidate"),
                    help="'core' for the competition rasters; 'candidate' for core plus C1/C2 proxy-gate inputs")
    args = ap.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else ROOT / ".cache" / "gemsdata"
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    ids = set(args.only.split(",")) if args.only else None
    if args.group == "core":
        ids = {"training_features", "labels", "sample_submission"}
    elif args.group == "candidate":
        ids = {
            "training_features", "labels", "sample_submission",
            "h19_5", "h27_4_r1_solo", "derived_sgmc_faults",
            "qfault_shp", "qfault_shx", "qfault_dbf", "qfault_prj",
        }
    report = []
    for entry in manifest["files"]:
        if ids and entry["id"] not in ids:
            continue
        try:
            report.append(restore(entry, data_dir))
        except Exception as exc:  # noqa: BLE001 - report each source independently
            report.append({"id": entry["id"], "status": "FAILED", "error": str(exc)})
    print(json.dumps(report, indent=1))
    return 0 if all(result["status"] != "FAILED" for result in report) else 1


if __name__ == "__main__":
    sys.exit(main())
