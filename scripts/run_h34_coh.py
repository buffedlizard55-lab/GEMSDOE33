#!/usr/bin/env python3
"""H34 lane: deployment-density baseline audit (Exp 1) and H34-COH candidate (Exp 2).

Frozen design: knowledge/37_h34_hypothesis_slate_and_prereg_20261029.md
(hash in evidence/h34_coh_preregistration_20261029.sha256).

Shared tools only: analog_invariant (B1 regional expert, percentile surface), csht_transfer
(CELF 300 m emission, uniqueness audit, DiagonalSegmentHoldout), vendor.gems24_template.holdout
(SegmentHoldout, paired bootstrap, canary), submission_writer.write_pair (writer + saved-byte check).

Usage:
  python scripts/run_h34_coh.py --stage baseline   # Exp 1: B1 vs matched-random control
  python scripts/run_h34_coh.py --stage candidate  # Exp 2: B1 vs H34-COH vs matched-random

No DrivenData access, no upload, no slot selection. Outputs are research evidence only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.ndimage import convolve, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe33 import analog_invariant, csht_transfer, grid  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402

MANIFEST = ROOT / "registry" / "focus_rasters_20261026_r3.json"
TEMPLATE = ROOT / "data" / "sample_submission.tif"
CACHE = ROOT / ".cache" / "features"
BUDGET_FULL = 37654
DATE = "20261029"
LINE_PX = 11
N_DIR = 8
RANDOM_SEED = 20261029


def jw(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pct(a: np.ndarray, domain: np.ndarray) -> np.ndarray:
    return analog_invariant.percentile_surface(np.nan_to_num(a).astype(np.float32), domain)


def line_kernel(angle_deg: float, length: int) -> np.ndarray:
    """Normalised line-averaging kernel of odd ``length`` at ``angle_deg`` (pixel-rounded)."""
    half = length // 2
    k = np.zeros((length, length), dtype=np.float32)
    theta = np.deg2rad(angle_deg)
    for t in range(-half, half + 1):
        x = int(round(t * np.cos(theta)))
        y = int(round(t * np.sin(theta)))
        k[y + half, x + half] = 1.0
    return k / k.sum()


def coherence_field(ridge: np.ndarray) -> np.ndarray:
    """H34-COH orientation-coherence: max over orientations of the line-average minus their mean."""
    r = np.nan_to_num(np.asarray(ridge, dtype=np.float32))
    stack = []
    for k in range(N_DIR):
        kern = line_kernel(k * 180.0 / N_DIR, LINE_PX)
        stack.append(convolve(r, kern, mode="constant", cval=0.0))
    a = np.stack(stack, axis=0)
    return (a.max(axis=0) - a.mean(axis=0)).astype(np.float32)


def random_emission(eligible: np.ndarray, budget: int, seed: int) -> np.ndarray:
    """Matched-random control: uniform choice of ``budget`` eligible cells (same count, same domain)."""
    flat = np.flatnonzero(eligible)
    rng = np.random.default_rng(seed)
    pick = rng.choice(flat, size=budget, replace=False)
    out = np.zeros(eligible.shape, dtype=bool)
    out.ravel()[pick] = True
    return out


def canary_rows(ho: SegmentHoldout, features: dict) -> dict:
    canary = ho.canary(features)
    rows = [
        {
            "feature": k,
            "max_fold_auc": float(max(max(d["auc"], 1 - d["auc"]) for d in v["folds"])),
            "pooled_auc": float(max(v["pooled_auc"], 1 - v["pooled_auc"])),
            "leakage_suspect": bool(v["leakage_suspected"]),
        }
        for k, v in canary["features"].items()
    ]
    return {"passed": bool(canary["passed"]), "rows": rows}


def run_holdout(ho, arrays, footprint, gate_surface_fn, seed0: int, label: str, use_candidate: bool):
    """Fit B1 per fold, emit B1 / matched-random (/ H34-COH) dots, and return predictions."""
    names = ["B1", "RANDOM"] + (["H34-COH"] if use_candidate else [])
    preds = {n: [] for n in names}
    reps = []
    nfp = int(footprint.sum())
    for fold in ho.folds:
        valid, train, visible = fold["valid"], fold["train"], fold["visible"]
        fid = int(fold["id"])
        dvis = distance_transform_edt(~visible)
        elig = valid & (dvis > 2.0)
        budget = int(round(BUDGET_FULL * int(valid.sum()) / nfp))
        model = analog_invariant.fit_regional_expert(arrays, train, visible, dvis, seed=seed0 + 100 * fid + 1)
        raw = analog_invariant.predict(model, arrays, valid)
        surfaces = {"B1": raw}
        if use_candidate:
            surfaces["H34-COH"] = gate_surface_fn(raw, valid)
        for name in ["B1", "H34-COH"]:
            if name in surfaces:
                dots = csht_transfer.celf_emit_300m(surfaces[name], elig, budget, min_self_spacing_px=2.5)
                assert int(dots.sum()) == budget, (name, int(dots.sum()), budget)
                preds[name].append(dots.astype(np.uint8))
        rnd = random_emission(elig, budget, RANDOM_SEED + 1000 * fid + seed0 % 997)
        preds["RANDOM"].append(rnd.astype(np.uint8))
        reps.append({"fold": fold["name"], "budget": budget, "withheld_positives": int(fold["truth"].sum()),
                     "eligible_cells": int(elig.sum())})
        print(label, fold["name"], budget, flush=True)
    return preds, reps


def _gate_pass(results, hname) -> dict:
    cmp_b1 = results[hname]["H34-COH_vs_B1"]
    cmp_rnd = results[hname]["H34-COH_vs_RANDOM"]
    return {
        "beats_B1_paired_ci_positive_4fold": bool(
            cmp_b1["paired_delta_dti"] > 0 and cmp_b1["ci95_strictly_positive"] and cmp_b1["fold_wins"] >= 3
        ),
        "beats_random_control": bool(cmp_rnd["paired_delta_dti"] > 0 and cmp_rnd["ci95_strictly_positive"]),
        "screen_or_confirm_dti": {
            "candidate": results[hname]["summary"]["H34-COH"]["dti"],
            "B1": results[hname]["summary"]["B1"]["dti"],
            "random": results[hname]["summary"]["RANDOM"]["dti"],
        },
    }


def decide_and_emit(results, arrays, footprint, catalogue, gate_surface_fn, canary) -> dict:
    """Frozen decision rule (knowledge/37 section 3). Full-deployment emission, uniqueness, writer."""
    screen_g = _gate_pass(results, "screen")
    confirm_g = _gate_pass(results, "confirm")
    dcat = distance_transform_edt(~catalogue)
    elig = footprint & (dcat > 2.0)
    model = analog_invariant.fit_regional_expert(arrays, footprint, catalogue, dcat, seed=20261060)
    raw = analog_invariant.predict(model, arrays, footprint)
    surf = gate_surface_fn(raw, footprint)
    flat = np.flatnonzero(elig)
    top = flat[np.argsort(-surf.ravel()[flat], kind="mergesort")[:BUDGET_FULL]]
    preview = np.zeros(footprint.shape, bool)
    preview.ravel()[top] = True
    dots = csht_transfer.celf_emit_300m(surf, elig, BUDGET_FULL, min_self_spacing_px=2.5)
    assert int(dots.sum()) == BUDGET_FULL
    uniq = csht_transfer.audit_uniqueness_against_manifest(
        surf, preview, dots, footprint, MANIFEST, root=ROOT
    )
    uniq_pass = bool(uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
    gates = {
        "a_screen_beats_B1": screen_g["beats_B1_paired_ci_positive_4fold"],
        "b_confirm_beats_B1": confirm_g["beats_B1_paired_ci_positive_4fold"],
        "c_beats_random_both": bool(screen_g["beats_random_control"] and confirm_g["beats_random_control"]),
        "d_canary_no_leakage": bool(canary["passed"]),
        "e_duplicate_guard_surface_and_dots": uniq_pass,
    }
    promote = all(gates.values())
    if not uniq_pass:
        verdict = "duplicate"
    elif promote:
        verdict = "promote"
    else:
        verdict = "negative"
    note_t = "GEMS33 H34-COH line-coherence gate on B1 37654d | gate " + verdict.upper() + " | {cid}"
    receipt = write_pair(
        dots.astype(np.float32),
        template=TEMPLATE,
        catalogue=catalogue,
        footprint=footprint,
        outdir=ROOT / "docs" / "downloads",
        family="gemsdoe33",
        hypothesis="h34-coh-tmiline-37654",
        date=DATE,
        note_template=note_t,
        scientific_verdict=verdict,
    )
    zero = ROOT / "docs" / "downloads" / receipt["primary_zero_outside"]["file"]
    fmt = audit_submission(zero, TEMPLATE)
    import rasterio

    with rasterio.open(zero) as ds:
        a = ds.read(1)
        arr_ok = bool(np.isfinite(a).all() and a.min() >= 0 and a.max() <= 1)
    ok_fmt = bool(fmt.get("pass", fmt.get("format_valid", False)) and arr_ok)
    card = {
        "schema": 1,
        "campaign": "H34-COH",
        "hypothesis": "A fault is a long, straight ridge set. Gating the B1 regional expert's score by 8-orientation line-coherence of the magnetic NMS ridge map ranks ridge-continuous segments above isolated ridge pixels, so faults absent from the catalogue are recovered.",
        "mechanism": "surface = pct(B1) x (0.2 + 0.8 pct(C)); C = max_k line-mean_k - mean_k line-mean_k (11 px, 8 angles) over tmi_ridge; CELF 300 m triangular emission, 37654 dots, > 2 px off catalogue.",
        "named_non_fault_process_that_could_mimic_it": "Airborne flight-line striping and levelling artefacts in the magnetic channel (stripe-parallel continuous ridges); drainage incision and cultural linears (roads, fences, canal banks).",
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": results["screen"]["summary"]["H34-COH"]["evaluator_version"],
            "withheld_positives": int(results["screen"]["summary"]["H34-COH"]["n_withheld_positive_pixels"]),
            "screen": {k: results["screen"]["summary"][k]["dti"] for k in ["H34-COH", "B1", "RANDOM"]},
            "screen_ci95_H34-COH": results["screen"]["summary"]["H34-COH"]["ci95"]["interval"],
            "confirm": {k: results["confirm"]["summary"][k]["dti"] for k in ["H34-COH", "B1", "RANDOM"]},
            "confirm_ci95_H34-COH": results["confirm"]["summary"]["H34-COH"]["ci95"]["interval"],
            "screen_candidate": results["screen"]["summary"]["H34-COH"]["dti"],
            "screen_B1": results["screen"]["summary"]["B1"]["dti"],
            "confirm_candidate": results["confirm"]["summary"]["H34-COH"]["dti"],
            "confirm_B1": results["confirm"]["summary"]["B1"]["dti"],
            "screen_paired_vs_B1": results["screen"]["H34-COH_vs_B1"],
            "confirm_paired_vs_B1": results["confirm"]["H34-COH_vs_B1"],
            "note": "Local catalogue-proxy holdout estimate. NOT organizer-confirmed and NOT a leaderboard projection.",
        },
        "feature_canaries": canary,
        "gates": gates,
        "gate_detail": {"screen": screen_g, "confirm": confirm_g},
        "correlation_overlap_vs_registry": {
            "surface": uniq["surface"],
            "final_dots": uniq["final_dots"],
        },
        "raster_sha256": receipt["primary_zero_outside"]["sha256"],
        "validator_output": {"format_audit": fmt, "saved_bytes_finite_in_0_1": arr_ok},
        "submission_name": zero.stem,
        "submission_note": receipt["note"],
        "verdict": verdict,
        "ok_to_download": bool(ok_fmt),
        "ok_to_submit": bool(promote and ok_fmt),
        "ok_to_submit_reason": "Requires all preregistered gates AND a separate selector step within the weekly cap; this run spent 0 slots and made no upload.",
        "slots_spent": 0,
        "date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    jw(ROOT / "evidence" / "h34_coh_run_card_20261029.json", card)
    jw(ROOT / "evidence" / "h34_coh_uniqueness_20261029.json", uniq)
    print("VERDICT", verdict, "GATES", gates, "NOTE", receipt["note"], flush=True)
    return {"verdict": verdict, "gates": gates, "submission_name": zero.stem}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["baseline", "candidate"], required=True)
    args = ap.parse_args()
    t0 = time.monotonic()

    footprint = grid.template_footprint()
    catalogue = grid.load_labels() & footprint
    arrays = analog_invariant.load_feature_arrays()
    use_candidate = args.stage == "candidate"

    ridge = np.load(CACHE / "tmi_ridge.npy", mmap_mode="r")
    coh = coherence_field(np.asarray(ridge))
    coh_pct = pct(coh, footprint)

    def gate_surface(raw, valid):
        return (pct(raw, valid) * (0.2 + 0.8 * pct(coh, valid))).astype(np.float32)

    screen = SegmentHoldout(footprint, catalogue, buffer_px=15)
    confirm = csht_transfer.DiagonalSegmentHoldout(footprint, catalogue, buffer_px=20)

    canary_feats = {"tmi_ridge": np.nan_to_num(np.asarray(ridge, dtype=np.float32)), "h34_coh": coh_pct}
    canary = canary_rows(screen, canary_feats)
    print("canary passed:", canary["passed"], flush=True)
    if not canary["passed"]:
        raise SystemExit("LEAKAGE CANARY TRIPPED — stop (protocol rule 4)")

    results = {}
    for hname, ho, seed0 in [("screen", screen, 20261040), ("confirm", confirm, 20261050)]:
        preds, reps = run_holdout(ho, arrays, footprint, gate_surface, seed0, hname, use_candidate)
        summ = {k: ho.summarize(v, ci_draws=1999) for k, v in preds.items()}
        cmp_random = ho.compare_paired(preds["B1"], preds["RANDOM"], ci_draws=1999, seed=seed0)
        entry = {"reps": reps, "summary": summ, "B1_vs_RANDOM": cmp_random}
        if use_candidate:
            entry["H34-COH_vs_B1"] = ho.compare_paired(preds["H34-COH"], preds["B1"], ci_draws=1999, seed=seed0)
            entry["H34-COH_vs_RANDOM"] = ho.compare_paired(preds["H34-COH"], preds["RANDOM"], ci_draws=1999, seed=seed0)
        results[hname] = entry
        print(hname, {k: summ[k]["dti"] for k in summ}, flush=True)

    if use_candidate:
        results["_candidate_gate"] = decide_and_emit(
            results, arrays, footprint, catalogue, gate_surface, canary
        )

    out = {
        "schema": 1,
        "stage": args.stage,
        "date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "preregistration": "knowledge/37_h34_hypothesis_slate_and_prereg_20261029.md",
        "preregistration_sha256": sha256_file(ROOT / "knowledge" / "37_h34_hypothesis_slate_and_prereg_20261029.md"),
        "evaluator": "evaluate_holdout.py / vendor.gems24_template.holdout (shared)",
        "evaluator_sha256": sha256_file(ROOT / "evaluate_holdout.py"),
        "canary": canary,
        "results": results,
        "labels": "HOLDOUT-DTI (local catalogue proxy; not organizer-confirmed; not a leaderboard projection)",
        "elapsed_seconds": round(time.monotonic() - t0, 1),
    }
    out_path = ROOT / "evidence" / f"h34_{args.stage}_experiment_{DATE}.json"
    jw(out_path, out)
    print("wrote", out_path, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
