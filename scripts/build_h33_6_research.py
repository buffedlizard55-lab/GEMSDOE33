#!/usr/bin/env python3
"""Rebuild a unique H33-6 research TIFF from the frozen, failed-screen recipe.

This artifact is deliberately kept under docs/downloads/research/ with a
prominent non-submission label. It is not a slot recommendation. The script
rechecks the preregistered hash, owner-mirror input hash, and exact H27-4
reconstruction before emitting the candidate.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems33.candidates import c0_control, h19_5_ridge, rebuild_c0_from_known  # noqa: E402
from gems33.grid import data_dir, load_catalogue, load_template  # noqa: E402
from gems33.hypotheses import edge_consensus_score, read_feature_layers, reallocate_edge_budget  # noqa: E402
from gemsdoe33 import grid as package_grid  # noqa: E402
from gemsdoe33 import submission as package_submission  # noqa: E402

EXPECTED_PREREG_SHA256 = "8662553ddd8d01438ecc1e6fe3ff8dd518674b922acc7a66b70d8059bd4edf1a"
EXPECTED_FEATURE_SHA256 = "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5"
EXPECTED_H19_SHA256 = "ec1f9b56b83ce33cad781ceb9f104b18fb4f2ff785263a4e89616af4aabdee8d"
NAME = "GEMSDOE33-H33-6-edge-consensus-research-20261004"
NOTE = (
    "GEMSDOE33 H33-6 edge consensus | P1 delta DTI -0.002737 (2/4), P2 +0.000159 | "
    "RESEARCH ONLY; gate failed, not slot-approved | id {cid}"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    prereg_path = ROOT / "evidence" / "hypothesis_slate_20261004_preregistered.json"
    if sha256(prereg_path) != EXPECTED_PREREG_SHA256:
        raise SystemExit("preregistration hash mismatch; refusing to build a changed experiment")
    feature_path = data_dir() / "core" / "training_features.tif"
    h19_path = data_dir() / "models" / "h19_5_nan.tif"
    if sha256(feature_path) != EXPECTED_FEATURE_SHA256:
        raise SystemExit("training_features.tif hash mismatch; refusing to use changed mirror bytes")
    if sha256(h19_path) != EXPECTED_H19_SHA256:
        raise SystemExit("H19-5 hash mismatch; refusing to use changed mirror bytes")

    footprint, _ = load_template()
    catalogue = load_catalogue()
    reference = c0_control() > 0
    rebuilt, rebuild_report = rebuild_c0_from_known(catalogue, h19_5_ridge() > 0)
    rebuilt = rebuilt > 0
    if not np.array_equal(reference, rebuilt):
        raise SystemExit("local H27-4 reconstruction no longer exactly matches its owner-mirror reference")

    layers, nodata, band_metadata = read_feature_layers(feature_path, footprint)
    score, maxima, edge_report = edge_consensus_score(layers, footprint, sigma_px=2.0, nodata=nodata)
    candidate, build_report = reallocate_edge_budget(reference, catalogue, footprint, score, maxima)
    if int(candidate.sum()) != int(reference.sum()):
        raise SystemExit("matched-budget candidate unexpectedly changed the dot count")

    # gems33 uses the owner-mirror cache root; the package writer historically
    # expects flat files under data/. Point its reader at the verified core
    # directory without changing either library's default configuration.
    package_grid.DATA = data_dir() / "core"
    outdir = ROOT / "docs" / "downloads" / "research"
    receipt = package_submission.build_package(candidate > 0, None, NAME, outdir, NOTE)
    if not receipt["all_checks_pass"]:
        raise SystemExit("research TIFF failed the package grid/value audit")
    nan_path = Path(receipt["nan"]["path"])
    audit_path = ROOT / "evidence" / f"format_check_h33_6_{receipt['content_id']}.json"
    audit_process = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_submission.py"),
         "--submission", str(nan_path), "--out", str(audit_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    try:
        format_audit = json.loads(audit_process.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"format validator did not return JSON: {audit_process.stderr}") from exc
    if audit_process.returncode != 0 or not format_audit.get("pass"):
        raise SystemExit("research TIFF failed the official-format local audit")

    holdout_path = ROOT / "evidence" / "holdout_h33_6.json"
    holdout = json.loads(holdout_path.read_text(encoding="utf-8"))
    if holdout.get("numeric_gate", {}).get("pass") is not False or holdout.get("slot_cleared") is not False:
        raise SystemExit("the recorded H33-6 result is not a failed, non-slot-cleared screen")

    artifacts = []
    for variant in ("nan", "zeros"):
        item = receipt[variant]
        zip_item = receipt[f"zip_{variant}"]
        file_path = Path(item["path"])
        zip_path = Path(zip_item["path"])
        validation = dict(item)
        for path_key in ("path", "file"):
            if path_key in validation:
                validation[path_key] = Path(validation[path_key]).resolve().relative_to(ROOT).as_posix()
        artifacts.append({
            "variant": variant,
            "file": file_path.relative_to(ROOT).as_posix(),
            "zip": zip_path.relative_to(ROOT).as_posix(),
            "sha256": item["sha256"],
            "bytes": int(item["bytes"]),
            "zip_sha256": zip_item["sha256"],
            "zip_bytes": int(zip_item["bytes"]),
            "outside": "NaN" if variant == "nan" else "0.0",
            "validation": validation,
        })
    record = {
        "schema": 1,
        "built_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "status": "RESEARCH_ONLY_FAILED_HOLDOUT_NOT_SLOT_APPROVED",
        "recommended_for_upload": False,
        "slot_cleared": False,
        "name": NAME,
        "note": receipt["note"],
        "note_chars": receipt["note_chars"],
        "content_id": receipt["content_id"],
        "emitted_pixels": receipt["emitted_pixels"],
        "holdout_evidence": "evidence/holdout_h33_6.json",
        "holdout_status": holdout["status"],
        "p1_mean_delta_dti": holdout["p1"]["mean_delta_dti"],
        "p1_fold_deltas": holdout["p1"]["fold_deltas"],
        "p2_delta_dti": holdout["p2"]["delta_dti"],
        "matched_random_mean_delta_dti": holdout["p1"]["matched_random_mean_delta_dti"],
        "preregistration_sha256": EXPECTED_PREREG_SHA256,
        "training_features_sha256": EXPECTED_FEATURE_SHA256,
        "h19_5_sha256": EXPECTED_H19_SHA256,
        "baseline_reconstruction": rebuild_report,
        "feature_bands": band_metadata,
        "edge_score_summary": edge_report,
        "full_data_candidate_build": build_report,
        "format_audit_path": audit_path.relative_to(ROOT).as_posix(),
        "format_audit": format_audit,
        "artifact_warning": "Do not submit: the preregistered P1 gate failed and all local metrics are catalogue/SGMC proxy diagnostics, not competition scores.",
        "artifacts": artifacts,
    }
    manifest_path = outdir / "h33-6-research-manifest.json"
    manifest_path.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"name: {NAME}")
    print(f"content id: {receipt['content_id']}; pixels: {receipt['emitted_pixels']:,}")
    print(f"note: {receipt['note']} ({receipt['note_chars']}/200)")
    for item in artifacts:
        print(f"{item['file']} ({item['bytes']:,} bytes; sha256 {item['sha256']}; local checks {item['validation']['pass']})")
    print(f"research manifest: {manifest_path.relative_to(ROOT)}; not for upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
