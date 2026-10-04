#!/usr/bin/env python3
"""Named analog-field transfer: unique emission, fold-safe proxy holdout, package.

This is a research candidate. It does not license a Ben-David bound and does not
spend a weekly submission slot unless the holdout gate in evidence/holdout_analog.json
records a pass. No DrivenData service is contacted.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33 import analog, grid, metric, submission  # noqa: E402
from gemsdoe33.metric import dti_binary  # noqa: E402

EVIDENCE = ROOT / "evidence"
DOWNLOADS = ROOT / "docs" / "downloads"
NAME = "gemsdoe33-h33f-analog-xfer-20261004"
NOTE = (
    "GEMSDOE33 H33-F analog xfer | Dixie/Brady/DesertPeak wells+GeoDAWN | "
    "research not slot-approved | id {cid}"
)
BUFFER_PX = 6


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    t0 = time.time()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(33)

    print("[1] band cache + analog masks", flush=True)
    grid.build_band_cache(force=False)
    footprint = grid.template_footprint()
    catalogue = grid.load_labels()
    masks = analog.build_analog_masks(footprint)
    inventory = analog.analog_inventory(masks, catalogue, footprint)
    print(f"    analog cells={inventory['union_cells']:,} catalogue_in_analog={inventory['union_catalogue']:,}",
          flush=True)

    print("[2] feature stack", flush=True)
    stack, feat_names = analog.load_feature_stack(footprint)
    print(f"    features={feat_names}", flush=True)

    print("[3] exploratory domain discriminator (not a bound)", flush=True)
    disc = analog.domain_discriminator_proxy(stack, masks.analog, footprint, rng)

    print("[4] full analog classifier + unique emission", flush=True)
    fitted = analog.fit_analog_classifier(stack, masks.analog, catalogue, footprint, rng)
    score = analog.predict_chunks(fitted["clf"], stack, footprint)
    pred = analog.emit_from_score(score, footprint, catalogue)
    n_pred = int(pred.sum())
    print(f"    train_auc_in_sample={fitted['train_auc_in_sample']:.4f} emitted={n_pred:,}", flush=True)

    ridge = analog.h19_ridge()
    c0 = analog.rebuild_c0(catalogue, ridge)
    d28 = analog.d28_mask(footprint)
    print(f"    rebuilt C0={int(c0.sum()):,} D2.8={int(d28.sum()):,}", flush=True)

    print("[5] fold-safe P1 catalogue-hidden proxy vs rebuilt C0", flush=True)
    systems = analog.catalogue_systems(catalogue, buffer_px=BUFFER_PX)
    folds = analog.fold_masks(systems, n_folds=4)
    p1 = []
    for fold_id, hidden in enumerate(folds):
        hidden = hidden & footprint
        grown = binary_dilation(hidden, structure=np.ones((2 * BUFFER_PX + 1, 2 * BUFFER_PX + 1), bool))
        known = catalogue & ~grown
        truth = hidden & footprint & ~known
        fold_fit = analog.fit_analog_classifier(stack, masks.analog, known, footprint,
                                                np.random.default_rng(33 + fold_id),
                                                seed=33 + fold_id)
        fold_score = analog.predict_chunks(fold_fit["clf"], stack, footprint)
        fold_pred = analog.emit_from_score(fold_score, footprint, known)
        fold_c0 = analog.rebuild_c0(known, ridge)
        cand_m = dti_binary(fold_pred.astype(np.float32), truth, valid=footprint, known=known)
        ctrl_m = dti_binary(fold_c0.astype(np.float32), truth, valid=footprint, known=known)
        delta = float(cand_m["dti"] - ctrl_m["dti"])
        rec = {
            "fold": fold_id,
            "n_truth": int(truth.sum()),
            "n_known": int(known.sum()),
            "n_pred": int(fold_pred.sum()),
            "n_c0": int(fold_c0.sum()),
            "n_train_pos": fold_fit["n_pos"],
            "candidate": {k: float(cand_m[k]) if k != "n_truth" and k != "n_emitted" else int(cand_m[k])
                          for k in cand_m},
            "control": {k: float(ctrl_m[k]) if k != "n_truth" and k != "n_emitted" else int(ctrl_m[k])
                        for k in ctrl_m},
            "delta_dti": delta,
        }
        p1.append(rec)
        print(f"    fold {fold_id}: ΔDTI={delta:+.6f} pred={rec['n_pred']:,} c0={rec['n_c0']:,} "
              f"truth={rec['n_truth']:,}", flush=True)

    p1_deltas = [r["delta_dti"] for r in p1]
    p1_mean = float(np.mean(p1_deltas))
    p1_pos = int(sum(d > 0 for d in p1_deltas))

    print("[6] P2 SGMC off-catalogue proxy + matched-N random", flush=True)
    sgmc = analog.sgmc_off_catalogue(catalogue, footprint)
    p2_cand = dti_binary(pred.astype(np.float32), sgmc, valid=footprint, known=catalogue)
    p2_c0 = dti_binary(c0.astype(np.float32), sgmc, valid=footprint, known=catalogue)
    p2_d28 = dti_binary(d28.astype(np.float32), sgmc, valid=footprint, known=catalogue)
    # matched-N random off-catalogue control
    off = footprint & ~catalogue
    d_cat = __import__("scipy.ndimage", fromlist=["distance_transform_edt"]).distance_transform_edt(~catalogue)
    off = off & (d_cat > analog.PRUNE_PX)
    ys, xs = np.nonzero(off)
    n_rand = min(n_pred, int(ys.size))
    pick = rng.choice(ys.size, size=n_rand, replace=False)
    rand = np.zeros_like(pred)
    rand[ys[pick], xs[pick]] = True
    p2_rand = dti_binary(rand.astype(np.float32), sgmc, valid=footprint, known=catalogue)
    p2_delta_c0 = float(p2_cand["dti"] - p2_c0["dti"])
    p2_delta_rand = float(p2_cand["dti"] - p2_rand["dti"])

    gate_p1 = bool(p1_mean > 0 and p1_pos >= 3)
    gate_p2 = bool(p2_delta_c0 >= 0)
    slot = bool(gate_p1 and gate_p2)
    print(f"    P1 mean ΔDTI={p1_mean:+.6f} ({p1_pos}/4)  P2 vs C0={p2_delta_c0:+.6f}  "
          f"P2 vs random={p2_delta_rand:+.6f}  slot={slot}", flush=True)

    print("[7] package unique GeoTIFF", flush=True)
    record = submission.build_package(pred, None, NAME, DOWNLOADS, NOTE)
    cid = record["content_id"]
    receipt_path = DOWNLOADS / f"receipt-{NAME}-{cid}.json"
    receipt = json.loads(receipt_path.read_text())
    if not receipt["all_checks_pass"]:
        raise SystemExit(f"unique TIFF failed local checks: {receipt}")

    # Prove uniqueness vs D2.8 bytes
    d28_nan = DOWNLOADS / "gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif"
    unique_nan = Path(receipt["nan"]["file"])
    unique_vs_d28 = None
    if d28_nan.is_file():
        unique_vs_d28 = _sha(unique_nan) != _sha(d28_nan)

    holdout = {
        "schema": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "SLOT_CLEARED" if slot else "NOT_SLOT_CLEARED",
        "proxy_warning": (
            "P1 is catalogue-hidden spatial holdout; P2 is SGMC off-catalogue. "
            "Neither is the private expert-labelled competition truth."
        ),
        "p1_mean_delta_dti": p1_mean,
        "p1_positive_folds": p1_pos,
        "p1_n_folds": 4,
        "p1_folds": p1,
        "p2": {
            "candidate_dti": float(p2_cand["dti"]),
            "c0_dti": float(p2_c0["dti"]),
            "d28_dti": float(p2_d28["dti"]),
            "random_matched_n_dti": float(p2_rand["dti"]),
            "delta_vs_c0": p2_delta_c0,
            "delta_vs_random": p2_delta_rand,
            "n_sgmc_offcat": int(sgmc.sum()),
        },
        "gate": {"p1": gate_p1, "p2": gate_p2, "slot": slot},
        "seconds": round(time.time() - t0, 1),
    }
    (EVIDENCE / "holdout_analog.json").write_text(json.dumps(holdout, indent=2) + "\n")

    da = {
        "schema": 3,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "EXPLORATORY_NOT_LICENSED",
        "source_domains": ["Dixie Valley", "Brady Hot Springs", "Desert Peak"],
        "target_domain": "GeoDAWN competition footprint minus analog masks",
        "inventory": inventory,
        "features": feat_names,
        "domain_discriminator": disc,
        "source_in_sample_auc": fitted["train_auc_in_sample"],
        "n_train_pos": fitted["n_pos"],
        "n_train_neg": fitted["n_neg"],
        "ben_david": {
            "paper": "https://link.springer.com/article/10.1007/s10994-009-5152-4",
            "bound_computed": False,
            "reason": (
                "lambda (joint-label error) is unknown because analog labels are the same "
                "public catalogue, not independent field-verified extra traces; the "
                "discriminator class is not shown to equal the target HΔH class."
            ),
        },
        "external_gis": {
            "gdr_1682": "https://gdr.openei.org/submissions/1682",
            "gdr_207": "https://gdr.openei.org/submissions/207",
            "staged": False,
            "direct_download": "curl TLS SSL_ERROR_SYSCALL / HTTP 000 in this sandbox",
        },
        "decision": (
            "Named analog fields were defined and a unique off-catalogue emission was "
            "built. Transfer is not licensed as a Ben-David bound. Slot follows holdout_analog.json."
        ),
    }
    (EVIDENCE / "domain_adaptation_preflight.json").write_text(json.dumps(da, indent=2) + "\n")

    note = receipt["note"]
    manifest = {
        "schema": 1,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": (
            "UNIQUE_RESEARCH_CANDIDATE — H33-F named analog-field transfer; "
            + ("holdout gate PASS, still not an official score" if slot
               else "holdout gate FAIL; not slot-approved")
        ),
        "evidence_class": "MEASURED local proxies; OWNER-MIRROR inputs; no organizer receipt",
        "hypothesis": "H33-F",
        "source": {
            "builder": "scripts/run_analog_campaign.py",
            "analog_fields": ["dixie_valley", "brady", "desert_peak"],
            "emitted_pixels": n_pred,
            "not_a_copy_of_d28": unique_vs_d28,
        },
        "grid": {
            "crs": "EPSG:32611", "shape": [3730, 3292], "pixel_m": 100,
            "transform_gdal": [243350.0, 100.0, 0.0, 4508550.0, 0.0, -100.0],
            "bands": 1, "dtype": "float32", "footprint_cells": int(footprint.sum()),
        },
        "name": NAME,
        "note": note,
        "note_chars": len(note),
        "note_file": f"note-{NAME}-{cid}.txt",
        "emitted_pixels": n_pred,
        "recommended": Path(receipt["nan"]["file"]).name,
        "recommended_variant": "-nan.tif — official wording says outside data is null or NaN",
        "alternate": Path(receipt["zeros"]["file"]).name,
        "alternate_warning": "0.0 outside footprint; troubleshooting alternative only",
        "holdout_gate": holdout["gate"],
        "artifacts": [
            {"file": Path(receipt["nan"]["file"]).name, "zip": Path(receipt["nan"]["file"]).stem + ".zip",
             "sha256": receipt["nan"]["sha256"], "bytes": receipt["nan"]["bytes"],
             "outside": "NaN", "validation": receipt["nan"]},
            {"file": Path(receipt["zeros"]["file"]).name, "zip": Path(receipt["zeros"]["file"]).stem + ".zip",
             "sha256": receipt["zeros"]["sha256"], "bytes": receipt["zeros"]["bytes"],
             "outside": "0.0", "validation": receipt["zeros"]},
        ],
        "historical_d28_reference": {
            "file": "gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif",
            "role": "historical owner-mirror emission, not the featured unique candidate",
        },
    }
    (DOWNLOADS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"primary: {manifest['recommended']} pixels={n_pred:,} unique_vs_d28={unique_vs_d28} "
          f"slot={slot} in {time.time()-t0:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
