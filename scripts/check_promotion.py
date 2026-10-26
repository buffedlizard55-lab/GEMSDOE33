#!/usr/bin/env python3
"""Check promotion evidence automatically; never choose or upload a weekly slot.

Exit 0: evidence eligible for the separate selector. Exit 2: blocked/negative.
No raster means no format pass. No template means no grid-validation pass.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe33 import promotion  # noqa: E402
from gemsdoe33.promotion import assess  # noqa: E402
from validate_submission import audit, sha256_file  # noqa: E402


def reject_nonfinite_json(value):
    raise ValueError(f"Non-finite JSON number is not evidence: {value}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence", required=True, type=Path)
    ap.add_argument("--raster", type=Path)
    ap.add_argument("--template", type=Path, default=ROOT / "data/sample_submission.tif")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    try:
        data = json.loads(args.evidence.read_text(), parse_constant=reject_nonfinite_json)
        if args.raster is None:
            fmt, digest = {"pass": False, "reason": "No new candidate raster"}, None
        else:
            digest = sha256_file(args.raster)
            fmt = audit(args.raster, args.template)
        result = assess(data, fmt, digest)
        result["validator"] = fmt
        result["raster_sha256"] = digest
    except (ValueError, OSError) as exc:
        result = {"verdict": "negative", "eligible_for_selector": False, "ok_to_submit": False,
                  "error": f"{type(exc).__name__}: {exc}"}
    result["gate_version"] = "g33-evidence-completeness-v1"
    result["gate_source_sha256"] = sha256_file(Path(promotion.__file__))
    result["evidence_sha256"] = sha256_file(args.evidence) if args.evidence.is_file() else None
    result["validator_source_sha256"] = sha256_file(ROOT / "scripts/validate_submission.py")
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    print(text, end="")
    return 0 if result["eligible_for_selector"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
