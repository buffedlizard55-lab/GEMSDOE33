#!/usr/bin/env python3
"""Automated, fail-closed OK-TO-SUBMIT selector (no human inspector).

Reads every run card in ``evidence/*run_card*.json``.  A raster is OK TO SUBMIT only
if ALL of the following are re-verified from bytes on disk in this process:

1. a hash-bound underlying evidence record is reassessed by the shared promotion gate;
   the run card verdict == "promote" and promotion_assessment.eligible_for_selector is True
   (screen + independent confirmation beat the in-run and recorded holdout best with a
   strictly positive paired CI, canaries pass, surface + final-dot uniqueness pass);
2. the zero-outside GeoTIFF exists and its sha256 equals the run card's raster_sha256;
3. ``validate_submission.audit(..., strict_zero_outside=True)`` passes on the saved bytes
   (single band, float32, EPSG:32611, template shape/geotransform, all finite, [0,1]);
4. the upload zip contains exactly one .tif whose bytes hash to the same sha256;
5. the submission note is 1..140 characters.

Among eligible rasters the one with the highest confirmation HOLDOUT-DTI is selected.
Reassessment checks declared evidence consistency, not independent authenticity of claimed measurements.
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
import math
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_submission import audit, DATA  # noqa: E402
from gemsdoe33.promotion import REQUIRED_GATE_NAMES, assess  # noqa: E402

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


def _promotion_gates_pass(pa: dict) -> bool:
    gates = pa.get("gates")
    return (pa.get("eligible_for_selector") is True
            and isinstance(gates, dict)
            and set(gates) == set(REQUIRED_GATE_NAMES)
            and all(value is True for value in gates.values())
            and pa.get("failed_gates") == [])


def _confirm_dti(card: dict):
    pa = card.get("promotion_assessment") or {}
    try:
        sel = card.get("selected_variant")
        return card["holdout_dti"]["confirmation"][sel]["dti"]
    except (KeyError, TypeError, ValueError):
        pass
    holdout = card.get("holdout_dti") or {}
    if "confirm_candidate" in holdout:  # flat S33 schema
        return holdout["confirm_candidate"]
    return pa.get("confirm_dti")


def _locate_tif_by_sha256(digest: str | None) -> Path | None:
    """Find exactly one saved TIFF matching a flat run-card SHA; ambiguity fails closed."""
    if not isinstance(digest, str) or len(digest) != 64:
        return None
    matches = [p for p in DOWNLOADS.glob("*.tif") if _sha(p) == digest]
    return matches[0] if len(matches) == 1 else None


def _locate_zip_for_tif(tif: Path, digest: str) -> Path | None:
    """Find exactly one ZIP containing exactly the same single TIFF bytes."""
    matches = []
    for archive in DOWNLOADS.glob("*.zip"):
        try:
            with zipfile.ZipFile(archive) as zf:
                names = zf.namelist()
                tifs = [n for n in names if n.lower().endswith((".tif", ".tiff"))]
                if len(names) == len(tifs) == 1 and hashlib.sha256(zf.read(tifs[0])).hexdigest() == digest:
                    matches.append(archive)
        except (OSError, zipfile.BadZipFile, KeyError):
            continue
    if len(matches) == 1:
        return matches[0]
    # Prefer the same-stem archive only if the global lookup is ambiguous; check_card
    # still validates its sole member against the raster digest.
    candidate = tif.with_suffix(".zip")
    return candidate if len(matches) > 1 and candidate in matches else None


def _reassess_evidence(card: dict, fmt: dict, digest: str | None, note: str, confirm_dti) -> bool:
    """Re-run the shared gate on a hash-bound evidence file, not card summary flags.

    A complete declared evidence record is still not an independent scientific audit:
    hashes of claimed inputs and measurements require separate verification.
    """
    link = card.get("promotion_evidence")
    if not isinstance(link, dict):
        return False
    name, expected_sha = link.get("file"), link.get("sha256")
    if not isinstance(name, str) or Path(name).name != name or not name.endswith(".json"):
        return False
    evidence_path = ROOT / "evidence" / name
    if not evidence_path.is_file() or _sha(evidence_path) != expected_sha:
        return False
    try:
        def reject_constant(value):
            raise ValueError(f"non-finite JSON: {value}")
        evidence = json.loads(evidence_path.read_text(), parse_constant=reject_constant)
        result = assess(evidence, fmt, digest)
        return (result.get("eligible_for_selector") is True
                and evidence.get("submission_note") == note
                and evidence.get("confirmation", {}).get("candidate_pooled_dti") == confirm_dti)
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def check_card(path: Path) -> dict:
    card = json.loads(path.read_text())
    sub = card.get("submission") or {}
    if not sub.get("file"):  # flat run-card schema (e.g. DPPS): file/zip/note at top level
        sub = {**{k: card.get(k) for k in ("file", "zip", "note")}, "name": card.get("submission_name"), **sub}
    if not sub.get("note"):
        sub["note"] = card.get("submission_note")
    # Some campaign cards retain the raster digest/name but omit a nested submission-file field.
    # Locate bytes only by a unique exact SHA-256 match; never guess from a friendly name.
    located_tif = _locate_tif_by_sha256(card.get("raster_sha256")) if not sub.get("file") else None
    if located_tif is not None:
        sub["file"] = located_tif.name
    if not sub.get("zip") and located_tif is not None:
        located_zip = _locate_zip_for_tif(located_tif, card["raster_sha256"])
        if located_zip is not None:
            sub["zip"] = located_zip.name
    row = {"run_card": str(path.relative_to(ROOT)), "campaign": card.get("campaign"),
           "verdict": card.get("verdict"), "submission_name": sub.get("name"),
           "file": sub.get("file"), "checks": {}}
    c = row["checks"]
    pa = card.get("promotion_assessment") or {}
    c["verdict_promote"] = card.get("verdict") == "promote"
    c["promotion_gates_all_pass"] = _promotion_gates_pass(pa)
    tif = DOWNLOADS / sub["file"] if sub.get("file") else None
    c["file_exists"] = bool(tif and tif.is_file())
    sha = _sha(tif) if c["file_exists"] else None
    c["sha256_matches_run_card"] = bool(sha) and sha == card.get("raster_sha256")
    fmt = {}
    if c["file_exists"] and TEMPLATE.is_file():
        fmt = audit(tif, TEMPLATE, strict_zero_outside=True)
        c["format_audit_pass_on_saved_bytes"] = fmt.get("pass") is True and fmt.get("sha256") == sha
        # "Predicted values must be in range [0,1]": demand every cell finite and in [0,1].
        c["all_cells_finite_and_in_0_1"] = (fmt.get("all_finite") is True
                                            and fmt.get("in_range_0_1_whole_array") is True)
        # False diagnostic fields (e.g. outside_has_nan for a zero raster) are
        # not failed requirements. Report only actual validator predicates.
        required = ("shape_match", "resolution_match", "transform_match", "bounds_match",
                    "in_range_0_1_footprint", "outside_policy_pass", "pass")
        row["format_audit_failures"] = [k for k in required if fmt.get(k) is not True]
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
    confirm_dti = _confirm_dti(card)
    valid_dti = type(confirm_dti) in (int, float) and math.isfinite(confirm_dti) and 0 <= confirm_dti <= 1
    c["confirmation_dti_finite_in_0_1"] = valid_dti
    row["confirm_holdout_dti"] = confirm_dti if valid_dti else None
    c["underlying_evidence_reassessed"] = _reassess_evidence(card, fmt, sha, note, confirm_dti)
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
        dst.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
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
