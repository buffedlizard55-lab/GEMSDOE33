# 23. FSML / FSML2-CC results — duplicate, then unique-but-negative (2026-10-26)

Labels: all performance values are **HOLDOUT-DTI** (`gems-segment-pooled-v1`, α=0.2, β=0.8, 300 m
triangular kernel, 60,988 withheld catalogue positives per split, 10 km block-bootstrap 95% CI)
unless marked `*` = USER/OWNER-REPORTED public score. **No leaderboard score is projected**
(knowledge/22 §3: the catalogue proxy anti-ranks the public B2 ladder on the emission axis).

## Executive summary (the requested table)

| File to download | HOLDOUT-DTI screen / confirmation [95% CI] | Public-score estimate | Unique vs 22 registry rasters (incl. all 9 focus sites' best)? | OK TO SUBMIT? |
|---|---|---|---|---|
| `docs/downloads/gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-zeros.tif` (SHA-256 `be5013aad085c23a9317959f85c7d494e28eac5875f61addce8ec81b5bb51de3`) | 0.110427 [0.1009, 0.1203] / 0.103077 [0.0941, 0.1129]; CSHT comparator 0.135672 / 0.132066 | **Not estimable** (no validated transfer function; see §3) | **YES** — surface worst 3-px 65.44% ≤ 70%, final dots 40.68%, max \|ρ\| 0.0191 | **NO** — failed every beat-CSHT gate (0/4 + 0/4 folds). Research only. |
| Every earlier file on the site (S33-SEISDIL, A33-R3-LLC, DPPS, …) | see their run cards | Not estimable | varies | **NO** — selector: 0 eligible of 13 run cards |
| GEMSDOE32 B2 `h33-h33-2-b2-…-zeros` (historical) | — | 0.2778* owner-reported | NO — it *is* the H27-4/H19-5 family (100% within-3-px) | **NO** — already submitted; re-upload = duplicate |

**Best submission to submit today: none.** The honest answer to "can we generate a submission that
scores higher than 0.2778?" is: *not with any fold-safe, unique surface measured in this repository.*
Spending a slot on FSML2-CC would be betting against its own preregistered gate.

## 1. What ran (protocol order, both preregistered and SHA-frozen before code)

1. **FSML-PU** (`evidence/fsml_preregistration_20261026.json`, sha `5faad118…`): 4 spy-PU experts +
   GEO tip-lobe line, gated/ungated rank fusion. Canaries passed (thermal_density pooled two-sided
   AUC 0.5234; GEO fold AUCs 0.501–0.505 → no signal; thermal_orphan ≤0.540). **Both variants failed
   the pre-placement surface duplicate guard** (top-37,654 preview within-3-px: **87.51%** vs
   A33-R2-CSHT, 85.30% vs G30-MSDB1, 80.13% vs G24-gvc1; 52.84% vs G32-B2; max |ρ| 0.104).
   Verdict `duplicate`, 0 experiments, no TIF written. Finding: *catalogue-supervised pixel rankings
   on this channel stack converge to the same ridge network*, PU correction notwithstanding.
2. **FSML2-CC** (`evidence/fsml2_preregistration_20261026.json`, sha `645e1f6e…`): same PU experts,
   GEO dropped (canary ≈ 0.50), + 2 label-free lines (multiscale geopotential worms; R3 scarp
   l_line), corroboration-count fusion. Canaries: worm 0.5003, l_line 0.5074, thermal_density
   0.5234 — all ≤ 0.90. Surface guard: **V1_cc6 passed** (worst 65.44% vs MSDB1), V2_cc4 failed
   (81.85% vs CSHT) → clean ablation: the label-free lines are what buys distinctness.

## 2. Holdout results (Exp 1/3 screen + Exp 2/3 confirmation)

| Surface @ budget | Screen | Confirmation |
|---|---|---|
| FSML2 V1_cc6 @37,654 | 0.110427 [0.1009, 0.1203] | 0.103077 [0.0941, 0.1129] |
| FSML2 V1_cc6 @25,000 | 0.080224 [0.0695, 0.0913] | — |
| A33-R2-CSHT @37,654 (in-run) | 0.135672 [0.1241, 0.1477] | 0.132066 [0.1201, 0.1440] |
| A33-R2-CSHT @25,000 | 0.108873 [0.0983, 0.1202] | — |
| B1_regional @37,654 | 0.111415 | 0.113576 |
| matched_random | 0.073931 | — |
| H19-5 fixed reference (NOT fold-safe) | 0.162036 | — |
| Paired Δ FSML2 − CSHT @37,654 | −0.025246 [−0.0355, −0.0151], 0/4 | −0.028989 [−0.0410, −0.0174], 0/4 |
| Paired Δ FSML2 − H19-5 reference | −0.051609 | — |

Chosen budget by preregistered rule: 37,654. **Uniform budget descent is rejected**: 25,000 dots
hurt both surfaces (−0.030 FSML2, −0.027 CSHT) — the public ladder's gains came from deleting
*specific* catalogue-flank dots, not from emitting fewer dots overall (β=0.8 punishes lost recall).

Final artifact: 37,654 dots, 0 on catalogue, whole array finite in [0,1] (values {0,1}), strict
saved-byte audit pass; final-dot uniqueness pass (max 3-px 40.68%, max |ρ| 0.0191). Verdict
`negative`; selector 0/13 eligible; 0 slots used. Elapsed 1,644 s; experiments 2/3 (third reserved
for tool defects, unused).

## 3. Interpretation

1. **Uniqueness and holdout performance trade off directly on this stack.** The duplicate guard
   (≤70% within 3 px) bans the ridge network every catalogue-supervised model prefers. Adding
   label-free lines moved ~35% of top mass off that network (87.5% → 65.4% preview overlap) and
   cost −0.025 HOLDOUT-DTI. Any future lane must find *new true lineaments*, not re-rank known ones.
2. **The H19-5 gap survives fold-safe re-derivation attempts.** Fixed H19-5 emission (0.1620) still
   beats every fold-safe surface (best CSHT 0.1357). FSML's failure to reproduce it with cached
   channels means its advantage uses information outside this stack (19GEMSDOE reports 1 m DEM
   openness tiles + full-catalogue tip/step-over geometry) and/or is not fold-safe. We cannot
   distinguish those without the 1 m tiles (blocked: host outside sandbox allowlist) — flagged, not
   resolved. This does **not** license copying B2/H19-5 dots: they are prior art and duplicates.
3. **Why corroboration-count lost:** requiring ≥4–6 lines in their top decile concentrates dots on
   multi-physics *contacts* (the named mimic: lithologic/pediment edges where gravity+magnetic+
   topographic edges coincide). Withheld Quaternary faults more often express in 1–2 dominant lines
   (scarp *or* subsurface edge), which CSHT's weighted blend credits and the count gate discards.
4. **Score estimation:** the only defensible estimator remains ordinal (knowledge/22 §3). FSML2 is
   below CSHT on both splits with CIs excluding 0, so there is no evidence it would beat even the
   CSHT-like public reference (MSDB1 0.1462*), let alone 0.2778*. Any numeric "estimated leaderboard
   score" for it would be fabrication.

## 4. Run card (protocol Rule 5)

```json
{
  "hypothesis": "Fold-safe multi-line corroboration (4 spy-PU experts + 2 label-free lines, corroboration-count fusion) recovers more withheld fault pixels than in-run A33-R2-CSHT at matched dotted CELF emission, with a surface distinct from prior supervised blends.",
  "mechanism": "Per-fold two-step spy-PU HGB experts on disjoint channel groups; surface = count of 6 lines with percentile rank>=0.90 plus 0.1*mean-rank (V1_cc6); CELF-300m emission, d_visible>2px, 37654 dots.",
  "named_non_fault_process_that_could_mimic_it": "Lithologic contacts and buried pediment edges where gravity, magnetic, radiometric and topographic edges coincide without a throughgoing Quaternary fault; Lake Lahontan shoreline complexes.",
  "holdout_dti": {
    "label": "HOLDOUT-DTI", "evaluator_version": "gems-segment-pooled-v1", "withheld_positives": 60988,
    "screen_candidate": 0.110427, "screen_candidate_95pct_ci": [0.1009, 0.1203],
    "screen_baseline_csht": 0.135672, "screen_paired_delta": -0.025246,
    "screen_paired_delta_95pct_ci": [-0.035507, -0.015059], "screen_fold_wins": "0/4",
    "confirmation_candidate": 0.103077, "confirmation_candidate_95pct_ci": [0.0941, 0.1129],
    "confirmation_baseline_csht": 0.132066, "confirmation_paired_delta": -0.028989,
    "confirmation_paired_delta_95pct_ci": [-0.040999, -0.017396], "confirmation_fold_wins": "0/4",
    "leaderboard_score_projection": null
  },
  "predecessor_fsml1": {"verdict": "duplicate", "surface_worst_3px": 0.8751, "experiments_run": 0},
  "correlation_overlap_vs_registry": {"registry_count": 22, "surface_max_3px_fraction": 0.6544,
    "final_dots_max_abs_spearman": 0.0191, "final_dots_max_3px_fraction": 0.4068},
  "raster_sha256": "be5013aad085c23a9317959f85c7d494e28eac5875f61addce8ec81b5bb51de3",
  "validator_output": {"local_format_pass": true, "single_band_float32": true, "crs": "EPSG:32611",
    "shape": [3730, 3292], "transform_matches_template": true, "no_nan_inside_footprint": true,
    "whole_array_values_in_0_1": true, "outside_zero": true, "portal_acceptance": "unverified"},
  "submission_name": "gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-zeros",
  "submission_note": "GEMS33 FSML2-CC V1_cc6 spyPU+worm+line CELF 37654d | NEGATIVE | 6fd4410bbaee",
  "verdict": "negative"
}
```

Reproduce: `.venv/bin/python scripts/restore_data.py --group all && .venv/bin/python
scripts/prepare_data.py && .venv/bin/python scripts/restore_focus_registry_r3.py &&
.venv/bin/python scripts/run_fsml2.py` (refuses to rerun; `--force` only after a crash).
Forensics: `scripts/forensic_b2_20261026.py`.
