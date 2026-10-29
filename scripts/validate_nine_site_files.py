"""Run the project validator on every file in the 2026-10-29 nine-site manifest.

Inputs: git-blob cache under data/nine_site/ (written by scripts/nine_site_audit.py) and
data/sample_submission.tif. Each blob is re-hashed (git blob SHA-1) before it is validated.
Output: evidence/nine_site_validator_20261029.json. No network access, no DrivenData access.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from nine_site_audit import git_blob_sha1  # noqa: E402

MANIFEST = ROOT / "registry" / "nine_site_best_files_20261029.json"
CACHE = ROOT / "data" / "nine_site"
TEMPLATE = ROOT / "data" / "sample_submission.tif"
OUT = ROOT / "evidence" / "nine_site_validator_20261029.json"
# Gate values the validator must report for a pass (mirrors the `pass` expression in validate_submission.py).
GATES = {"bands": 1, "dtype": "float32", "epsg": 32611, "shape_match": True, "resolution_match": True,
         "transform_match": True, "bounds_match": True, "in_range_0_1_footprint": True,
         "outside_policy_pass": True}


def run_validator(path: Path, strict: bool) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.json"
        cmd = [sys.executable, str(ROOT / "scripts" / "validate_submission.py"),
               "--submission", str(path), "--template", str(TEMPLATE), "--out", str(report)]
        if strict:
            cmd.append("--strict-zero-outside")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        payload = json.loads(report.read_text()) if report.exists() else {}
        failed = [k for k, want in GATES.items() if payload.get(k) != want]
        return {"exit_code": proc.returncode,
                "pass": bool(payload.get("pass", False)) and proc.returncode == 0,
                "failed_gates": failed,
                "stderr_tail": proc.stderr.strip().splitlines()[-1:] if proc.stderr.strip() else []}


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    rows = []
    for entry in manifest["entries"]:
        blob = CACHE / f"{entry['blob_sha1']}.bin"
        row = {"site": entry["site"], "role": entry["role"], "name": entry["user_reported_name"],
               "blob_sha1": entry["blob_sha1"], "cached": blob.exists()}
        if not blob.exists():
            row["error"] = "blob missing from data/nine_site cache; run scripts/nine_site_audit.py"
            rows.append(row)
            continue
        data = blob.read_bytes()
        row["blob_verified"] = git_blob_sha1(data) == entry["blob_sha1"] and len(data) == entry["bytes"]
        if not row["blob_verified"]:
            row["error"] = "cached blob does not match manifest SHA-1/bytes"
            rows.append(row)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            tif = Path(tmp) / (Path(entry["path"]).stem + ".tif")
            shutil.copyfile(blob, tif)
            row["validator_default"] = run_validator(tif, strict=False)
            row["validator_strict_zero_outside"] = run_validator(tif, strict=True)
        rows.append(row)
    summary = {
        "schema": 1,
        "evidence_class": "MEASURED: in-project validator on owner-repo git blobs; no organizer validation",
        "files": len(rows),
        "blobs_verified": sum(1 for r in rows if r.get("blob_verified")),
        "pass_default": sum(1 for r in rows if r.get("validator_default", {}).get("pass")),
        "pass_strict_zero_outside": sum(1 for r in rows if r.get("validator_strict_zero_outside", {}).get("pass")),
        "ok_to_submit": 0,
        "note": "Validator pass is a format check only. OK TO SUBMIT also requires the duplicate guard and the holdout gate, see evidence/nine_site_audit_20261029.json and evidence/submission_selection_20261029.json.",
    }
    OUT.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
