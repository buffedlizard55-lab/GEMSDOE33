#!/usr/bin/env python3
"""Automated, fail-closed OK-TO-SUBMIT selector (no human inspector).

Reads every run card in ``evidence/*run_card*.json``.  A raster is OK TO SUBMIT only
if ALL of the following are re-verified from bytes on disk in this process:

1. run card verdict == "promote" and promotion_assessment.eligible_for_selector is True
   (screen + independent confirmation beat the in-run and recorded holdout best with a
   strictly positive paired CI, canaries pass, surface + final-dot uniqueness pass);
2. the zero-outside GeoTIFF exists and its sha256 equals the run card's raster_sha256;
3. ``validate_submission.audit(..., strict_zero_outside=True)`` passes on the saved bytes
   (single band, float32, EPSG:32611, template shape/geotransform, all finite, [0,1]);
4. the upload zip contains exactly one .tif whose bytes hash to the same sha256;
5. the submission note is 1..140 characters.

Among eligible rasters the one with the highest confirmation HOLDOUT-DTI is selected.
It never logs in, uploads or polls DrivenData (AGENTS.md / Terms of Use).  The weekly
slot count is not observable from this sandbox and is stated as an owner-side check.

Output: ``evidence/submission_selection_<date>.json`` and ``docs/data/submission_selection.json``.
Exit code 0 always (a NO decision is a valid outcome); 2 on internal error.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_submission import audit, DATA  # noqa: E402

# Follow the same GEMS_DATA_DIR/cache resolution as the validator, rather than
# silently assuming that restored owner-mirror inputs live under repository/data.
TEMPLATE = DATA / "sample_submission.tif"
DOWNLOADS = ROOT / "docs" / "downloads"


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _confirm_dti(card: dict):
    pa = card.get("promotion_assessment") or {}
    try:
        sel = card.get("selected_variant")
        return float(card["holdout_dti"]["confirmation"][sel]["dti"])
    except (KeyError, TypeError, ValueError):
        pass
    return pa.get("confirm_dti")


def check_card(path: Path) -> dict:
    card = json.loads(path.read_text())
    sub = card.get("submission") or {}
    if not sub.get("file"):  # flat run-card schema (e.g. DPPS): file/zip/note at top level
        sub = {**{k: card.get(k) for k in ("file", "zip", "note")}, "name": card.get("submission_name"), **sub}
    row = {"run_card": str(path.relative_to(ROOT)), "campaign": card.get("campaign"),
           "verdict": card.get("verdict"), "submission_name": sub.get("name"),
           "file": sub.get("file"), "checks": {}}
    c = row["checks"]
    pa = card.get("promotion_assessment") or {}
    c["verdict_promote"] = card.get("verdict") == "promote"
    c["promotion_gates_all_pass"] = pa.get("eligible_for_selector") is True
    tif = DOWNLOADS / sub["file"] if sub.get("file") else None
    c["file_exists"] = bool(tif and tif.is_file())
    sha = _sha(tif) if c["file_exists"] else None
    c["sha256_matches_run_card"] = bool(sha) and sha == card.get("raster_sha256")
    if c["file_exists"] and TEMPLATE.is_file():
        fmt = audit(tif, TEMPLATE, strict_zero_outside=True)
        c["format_audit_pass_on_saved_bytes"] = fmt.get("pass") is True and fmt.get("sha256") == sha
        # "Predicted values must be in range [0,1]": demand every cell finite and in [0,1].
        c["all_cells_finite_and_in_0_1"] = (fmt.get("all_finite") is True
                                            and fmt.get("in_range_0_1_whole_array") is True)
        row["format_audit_failures"] = [k for k, v in fmt.items() if v is False]
    else:
        c["format_audit_pass_on_saved_bytes"] = False
        c["all_cells_finite_and_in_0_1"] = False
    zp = DOWNLOADS / sub["zip"] if sub.get("zip") else None
    ok_zip = False
    if zp and zp.is_file():
        with zipfile.ZipFile(zp) as zf:
            tifs = [n for n in zf.namelist() if n.lower().endswith((".tif", ".tiff"))]
            if len(tifs) == 1 and len(zf.namelist()) == 1:
                ok_zip = hashlib.sha256(zf.read(tifs[0])).hexdigest() == sha
    c["zip_single_geotiff_same_bytes"] = ok_zip
    note = sub.get("note")
    c["note_1_to_140_chars"] = isinstance(note, str) and 0 < len(note) <= 140
    row["note"] = note
    row["sha256"] = sha
    row["confirm_holdout_dti"] = _confirm_dti(card)
    row["eligible"] = all(c.values())
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y%m%d"))
    args = ap.parse_args()
    rows = []
    for p in sorted((ROOT / "evidence").glob("*run_card*.json")):
        try:
            rows.append(check_card(p))
        except Exception as exc:  # malformed / legacy cards fail closed
            rows.append({"run_card": str(p.relative_to(ROOT)), "eligible": False,
                         "error": f"{type(exc).__name__}: {exc}"})
    eligible = [r for r in rows if r.get("eligible")]
    eligible.sort(key=lambda r: (r.get("confirm_holdout_dti") or -1), reverse=True)
    chosen = eligible[0] if eligible else None
    out = {
        "schema": 1, "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "selector": "scripts/select_submission.py (automated, fail-closed)",
        "ok_to_submit": chosen is not None,
        "decision": (f"OK TO SUBMIT: {chosen['file']}" if chosen else
                     "NO RASTER IS OK TO SUBMIT: no run card passes every automated gate."),
        "selected": chosen,
        "owner_side_check": "Weekly submission cap and remaining slots are not observable from this sandbox "
                            "(no DrivenData access by rule); confirm a slot is free before uploading.",
        "candidates": rows,
    }
    for dst in (ROOT / "evidence" / f"submission_selection_{args.date}.json",
                ROOT / "docs" / "data" / "submission_selection.json"):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(out, indent=2) + "\n")
    print(out["decision"])
    for r in rows:
        print(f"  {'ELIGIBLE' if r.get('eligible') else 'blocked '}  {r['run_card']}"
              f"  verdict={r.get('verdict')}  failed={[k for k, v in (r.get('checks') or {}).items() if not v]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"selector internal error: {exc}", file=sys.stderr)
        raise SystemExit(2)
