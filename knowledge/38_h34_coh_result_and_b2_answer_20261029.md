# 35 — H34-COH result, the 0.2778 question, and the session decision (2026-10-29)

**Decision: OK TO DOWNLOAD (research only): YES · OK TO SUBMIT: NO. Verdict: negative.** No slot was spent and no upload was made. All numbers below are HOLDOUT-DTI (local catalogue proxy, evaluator `gems-segment-pooled-v1`, 60,988 withheld positives). None is an organizer-confirmed score, and none is a leaderboard projection.

## 1. Why did GEMSDOE32 B2 (0.2778*) score highest, and can we beat it?

`*` = owner/user-reported, not an organizer receipt.

**What the bytes show (measured, `evidence/nine_site_audit_20261029.json` → `b2_forensic_recount`):**
- B2 has 37,654 dots. H27-4 (GEMSDOE28/31) has 40,199 dots. B2 is an **exact subset** of H27-4. It removes **2,545** dots, all at catalogue distance 1–2 px. It adds none, and no B2 dot lies on the catalogue.
- H27-4 belongs to the same H19-5 emission family as the other site-best files. Three D2.8 files have identical dot sets, all 44,090 dots: GEMSDOE25 and GEMSDOE30 (owner-listed) and the repo's own GEMSDOE33 `d28-reference` research file.

**Plausible mechanism (hypothesis, not proof):** a one-pixel-to-two-pixel halo around known faults often contains catalogue-adjacent false positives. If the hidden labels sit more than 2 px from the catalogue, removing that halo lowers the false-positive mass without losing much recall. The `knowledge/01` and `knowledge/22` forensics reach the same conclusion.

**Why this is not an explanation of a score (judgement):**
1. The 0.2778 value is owner-reported. No organizer receipt ties it to these bytes (`IR-33-SCORE-01/02`, `IR-33-20261029-SCORE-CONFLICT-01`).
2. The owner's neighbouring values differ from B2 by 0.007 (0.2708 for H27-4, which is unsupported) and by 0.018 (0.2600 for D2.8). These gaps are owner-reported, and this repo has no measurement that could attribute any of them to a 2,545-dot edit.
3. Our holdout cannot test the B2 prune. Our emission already excludes dots within 2 px of the visible catalogue, so the mechanism is structurally absent from this lane (`IR-33-20261029-B2-MECHANISM-UNTESTABLE-01`).

**Can we beat 0.2778?** Not demonstrated. The one new candidate tested this session lost to its baseline on both holdouts (section 3). No file in this repo has a measured holdout advantage over B1. Any statement that we "beat 0.2778" would be a projection, which the protocol forbids.

## 2. Experiment 1: deployment-density baseline audit (groundwork)

Design: frozen runner `scripts/run_h34_coh.py --stage baseline`; shared `SegmentHoldout` (buffer 15 px) and `DiagonalSegmentHoldout` (buffer 20 px); B1 regional expert per fold; CELF 300 m emission at 37,654 × |fold| / 5,167,373 dots; matched-random control with the same count and eligibility; feature canary on `tmi_ridge` and H34-COH.

| Holdout | B1 HOLDOUT-DTI (95% CI) | Matched-random | Paired Δ B1 − random (95% CI) | Folds |
|---|---|---|---|---|
| Screen (quadrant, buffer 15) | 0.126012 [0.117781, 0.134911] | 0.069819 [0.066684, 0.072843] | +0.056193 [+0.047109, +0.065782] | 4/4 |
| Confirm (diagonal wedge, buffer 20) | 0.130060 [0.121188, 0.138926] | 0.070827 [0.067960, 0.073610] | +0.059233 [+0.048757, +0.069007] | 4/4 |

Reading: the B1 operating point is well above random, so the control is valid. Canary AUCs are about 0.50 (`tmi_ridge` 0.501; H34-COH 0.519), well under 0.90. Exp 1 and Exp 2 reproduce the same B1 numbers exactly (deterministic seeds).

## 3. Experiment 2: H34-COH candidate (one preregistered lane)

Frozen definition and decision rule: [`knowledge/37`](37_h34_hypothesis_slate_and_prereg_20261029.md) (SHA-256 `5d40648deb0039a11465a00ab4e331ad323f22facbdfc25c853e89949e3b2f09`). The decision rule was written before the run, and the code applies it as written.

| Holdout | H34-COH (95% CI) | B1 | Paired Δ vs B1 (95% CI) | Folds vs B1 | Δ vs matched-random |
|---|---|---|---|---|---|
| Screen | 0.104769 [0.097281, 0.112377] | 0.126012 | −0.021243 [−0.028714, −0.014335] | **0/4** | +0.034950, 4/4 |
| Confirm | 0.105973 [0.098748, 0.113560] | 0.130060 | −0.024087 [−0.031118, −0.017497] | **0/4** | +0.035146, 4/4 |

Gates (from the run card): (a) beats B1 on screen ✗; (b) beats B1 on confirm ✗; (c) beats matched-random on both ✓; (d) no canary leakage ✓; (e) duplicate guard on surface and final dots ✓. **Verdict: negative.** The gate is a multiplicative line-coherence factor on the magnetic ridge map. The likely reading (interpretation, not measured) is that it down-weights high-score regional cells that are not line-continuous, and those cells carry more holdout signal than the continuity term adds. The result is preserved and is not retuned.

**Uniqueness (measured):** against all 22 pinned registry rasters, the surface max |ρ| is 0.078 and the top-N preview 3-px overlap is 67.7% (`IR-33-20261029-H34-UNIQ-MARGIN-01`: passes narrowly). The final dots have max |ρ| 0.029 and max 3-px overlap 46.0%.

**Format (re-opened from disk this session):** one float32 band, EPSG:32611, 3730 × 3292, template transform, finite, whole array in [0, 1], 37,654 dots, 0 dots outside the footprint. SHA-256 of the saved bytes matches the run card.

## 4. Hypothesis ledger (ranked, from `knowledge/37`)

1. H34-COH: **tested, negative.**
2. H34-SPUR (flight-line stripe suppression): not tested. Low cost. Requires a preregistration before use.
3. H34-DEPTH (basement-depth step gradient): not tested. Overlaps the failed BASESTEP/THKCOND family.
4. H34-CURVTRACE (raw 3DEP 1 m curvature): **blocked.** Raw tiles are not staged and were not verified obtainable here.
5. H34-COULOMB (DOE GDR #1391 geometry): **blocked.** Vertices, strike and CRS are not established.

Experiment budget: **2 of 3 used**. The third is held in reserve and was not spent, because the candidate failed and retuning is forbidden.

## 5. Limitations

- All scores are local catalogue proxies. The hidden expert labels are not represented, so none of this is a leaderboard prediction.
- The two evaluators (root `evaluate_holdout.py` vs the vendored template) carry different version labels. This must be reconciled once (`IR-33-20261029-H34-EVALUATOR-VERSION-01`).
- Owner-mirror bytes are SHA-pinned, but that does not authenticate organizer origin.

## 6. Run card (JSON)

```json
{
  "hypothesis": "A fault is a long, straight ridge set. Gating the B1 regional expert's score by 8-orientation line-coherence of the magnetic NMS ridge map ranks ridge-continuous segments above isolated ridge pixels, so faults absent from the catalogue are recovered.",
  "mechanism": "surface = pct(B1) x (0.2 + 0.8 pct(C)); C = max_k line-mean_k - mean_k line-mean_k (11 px, 8 angles) over tmi_ridge; CELF 300 m triangular emission, 37654 dots, > 2 px off catalogue.",
  "named_non_fault_process_that_could_mimic_it": "Airborne flight-line striping and levelling artefacts in the magnetic channel (stripe-parallel continuous ridges); drainage incision and cultural linears (roads, fences, canal banks).",
  "gates": {
    "a_screen_beats_B1": false,
    "b_confirm_beats_B1": false,
    "c_beats_random_both": true,
    "d_canary_no_leakage": true,
    "e_duplicate_guard_surface_and_dots": true
  },
  "verdict": "negative",
  "ok_to_download": true,
  "ok_to_submit": false,
  "slots_spent": 0,
  "submission_name": "gemsdoe33-h34-coh-tmiline-37654-20261029-1181c8712300-zeros",
  "submission_note": "GEMS33 H34-COH line-coherence gate on B1 37654d | gate NEGATIVE | 1181c8712300",
  "raster_sha256": "9fc35db23586d04af2481eb3b32f8912c1d99d029a2bf18bb6cccf63d2caac9d",
  "holdout_dti": {
    "label": "HOLDOUT-DTI",
    "evaluator_version": "gems-segment-pooled-v1",
    "withheld_positives": 60988,
    "screen": {
      "H34-COH": 0.1047692294681379,
      "B1": 0.1260119444838056,
      "RANDOM": 0.0698190828983246
    },
    "screen_ci95_H34-COH": [
      0.0972806497642195,
      0.11237671883126259
    ],
    "confirm": {
      "H34-COH": 0.10597276601254811,
      "B1": 0.13005982956637568,
      "RANDOM": 0.07082684648720312
    },
    "confirm_ci95_H34-COH": [
      0.09874793127227446,
      0.11356042067793629
    ],
    "paired_vs_B1_screen_delta_ci95": [
      -0.0212427150156677,
      [
        -0.028714317620261283,
        -0.014335258189250577
      ]
    ],
    "paired_vs_B1_confirm_delta_ci95": [
      -0.024087063553827573,
      [
        -0.031118140978202397,
        -0.01749697042461069
      ]
    ]
  },
  "correlation_overlap_vs_registry": {
    "registry_count": 22,
    "surface_max_abs_rho": 0.07756631195619108,
    "surface_max_preview_3px_overlap": 0.677378233388219,
    "final_dots_max_abs_rho": 0.029043099327560676,
    "final_dots_max_3px_overlap": 0.4600839220268763
  },
  "validator_output": {
    "bands": 1,
    "dtype": "float32",
    "crs": "EPSG:32611",
    "shape": [
      3730,
      3292
    ],
    "transform_match": true,
    "all_finite": true,
    "min": 0.0,
    "max": 1.0,
    "nonzero_cells": 37654,
    "dots_outside_footprint": 0,
    "saved_bytes_checked": "re-opened with rasterio in this session"
  },
  "canary": {
    "passed": true,
    "max_fold_auc": 0.5192737000000001
  }
}
```
