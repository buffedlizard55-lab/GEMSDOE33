# G33-DPPS results — 2026-10-26 (verdict: negative; unique TIF generated, do not submit)

Preregistration (frozen before implementation): `knowledge/14_preregistered_dpps_hypotheses_20261026.md`,
`evidence/dpps_preregistration_20261026.json` SHA-256 `4a177248719adea205ea1d5a46f2c33e07d3179ebbdc387dc4a60b475c4ab2bc`.
Runner: `scripts/run_dpps_campaign.py` · Operator: `src/gemsdoe33/dpps.py` ·
Evidence: `evidence/dpps_experiment_20261026.json`, `evidence/dpps_run_card_20261026.json`,
`evidence/dpps_uniqueness_20261026.json`, `evidence/dpps_validator_20261026.json`,
log `evidence/dpps_campaign_20261026.log`. Experiments used: **3/3** (screen, confirmation,
production). Slots spent: **0**. No retuning after results.

## Numbers (all HOLDOUT-DTI unless stated)

Evaluator `gems-segment-pooled-v1`, α=0.2, β=0.8, 300 m triangular kernel, whole-component
hide-and-recover, visible faults masked pixel-exactly, 60,988 withheld positives in each split,
10 km paired block-bootstrap CIs.

| Split | DPPS | B1_regional (in-run) | CTRL-PIXEL ablation | matched_random | Paired Δ vs B1 [95% CI], folds | Paired Δ vs CTRL [95% CI], folds |
|---|---:|---:|---:|---:|---|---|
| Screen `quadrant-buffered-15px-v1` | **0.095407** [0.084971, 0.106370] | 0.111285 | 0.072816 | 0.068107 | −0.015878 [−0.028932, −0.002121], 1/4 | **+0.022590 [+0.016578, +0.028826], 4/4** |
| Confirmation `diagonal-wedge-buffered-20px-confirm-v1` | **0.096015** [0.085295, 0.106776] | 0.114619 | 0.072936 | — | −0.018604 [−0.031369, −0.005925], 0/4 | **+0.023079 [+0.016931, +0.029462], 4/4** |

Per-fold DPPS: NW 0.112461 · NE_LidarGapHeavy 0.104513 · SW 0.080230 · SE 0.095567;
wedges N 0.104440 · E 0.098377 · S 0.095483 · W 0.092360.

- **Leakage canary:** 9/9 channels pass; max two-sided AUC 0.6875 (`det_elev_curv4`) ≤ 0.90.
- **Uniqueness vs 25 rasters** (21 pinned + A33-R2, G33, Round-3, H33-R3 locals):
  surface max |ρ| 0.0674, max preview-within-3px **67.80%** (vs local Round-3 DA-HGCM; vs the
  21 pinned the max is 50.33% `G30-MSDB1`) — pass, but only a 2.2 pp margin (**IR-DPPS-01** below);
  final dots max |ρ| 0.0213, max within-3px 44.62%, **24.0% vs GEMSDOE32 B2** — pass.
- **Format:** strict zeros-primary audit passes on saved bytes: 1 band float32, EPSG:32611,
  3730×3292, template transform, whole-array finite in [0,1] (values {0,1}), 0 NaN anywhere,
  37,654 dots, 0 on-catalogue. NaN twin also passes its audit.
- **Artifact:** `gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235-zeros.tif`
  SHA-256 `449ad2a4a3c746ef960f8e788b01e0b0cedef794a5dab5f22b0ae993b322f62d`; note (82/140):
  `GEMS33 DPPS dip-projected persistence scarp CELF 37654d | 111ae96bb235 | gate FAIL`.
- **Failed gates (6):** screen/confirm pooled > B1, paired CI > 0, ≥3/4 folds — i.e. every
  "beat the incumbent" gate. All other gates passed. ⇒ **verdict negative, OK TO DOWNLOAD: YES,
  OK TO SUBMIT: NO.**

## PhD interpretation

1. **The mechanism is real; the system is not incumbent-beating.** Persistence + dip-projection
   beat an identical-emission pixel-scarp surface by +31–32% relative HOLDOUT-DTI in 8/8 folds
   with CIs excluding zero on both orthogonal splits. That is a measured, ablation-isolated
   effect: pixel scarps are dominated by short cultural/erosional edges, and co-located gravity
   support is genuinely misaligned with surface traces where cover thickens.
2. **The catalogue proxy structurally rewards catalogue mimicry.** Withheld positives are
   *catalogued* segments — disproportionately exposed range-front scarps whose style a
   fold-visible HistGradientBoosting model (B1) can learn directly from neighbouring visible
   segments of the same ranges. DPPS spends part of its fixed 37,654-dot budget on dip-offset
   piedmont/basin lineaments that are, by the hypothesis, *missing from the catalogue* — the
   proxy can only score those dots as FPw. This is the known discovery-vs-proxy tension
   (AGENTS.md §7). It explains the result; it does **not** license overriding the gate: the live
   anchors agree with the proxy's ordering (supervised HGB live reports cluster at
   0.0742–0.2190\*; purely deterministic physics lanes such as G33 and the dozens of 0.01–0.16\*
   sibling detectors never approached 0.2778\*).
3. **Why B2 = 0.2778\* remains unreached by every non-H19-5 lane.** B2 inherits H19-5's
   1 m curvilinear scarp tracing (≈124k px before thinning), then removes only FPw. Its margin
   is trace-detection quality at 1 m, not pixel classification at 100 m. DPPS operates on
   100 m-aggregated LiDAR derivatives; a 15-px line-mean cannot recover sub-100 m scarp
   morphology that H19-5 exploited. Beating 0.2778\* plausibly requires rebuilding the *trace*
   stage (skeletonized, orientation-tracked 1 m scarp polylines, e.g. from the pinned
   3DEP DEM links / GDR #1682 BRIDGE payloads) and adding DPPS-style dip-projected support as a
   trace attribute — a new preregistered campaign, not a DPPS retune.
4. **mimic check.** The named mimic (fan toes / Lahontan benches) cannot be excluded by this
   proxy; DPPS's weakest fold is SW (0.0802), consistent with bench/fan-dominated piedmonts
   absorbing budget there. Recorded as a limitation, not explained away.

## Irregularities flagged

- **IR-DPPS-01 (near-limit uniqueness):** surface-preview 3-px overlap 67.80% vs the local
  Round-3 DA-HGCM raster is within the ≤70% limit but with slim margin. Any future variant of
  this surface must re-screen before placement; do not treat "pass" as headroom.
- **IR-DPPS-02 (proxy ceiling):** HOLDOUT-DTI here measures recovery of *catalogued* segments.
  A discovery lane can be penalized for exactly the dots it exists to place. The gate is kept
  anyway (protocol), and the limitation is stated wherever the numbers appear.
- Historical scores (0.2778\*, 0.2750\*, 0.4413, 0.3195) remain **OWNER-REPORTED (NOT
  ORGANIZER-CONFIRMED)**; conflicting leader values are unresolved and were not re-scraped.

## What to do next (selector / next session)

1. **Submit nothing from this campaign.** DPPS, A33-R2-CSHT and Round-3 all remain download-only.
2. Highest-value next preregistration: **1 m trace-stage rebuild** (skeletonized scarp polylines
   from pinned 3DEP DEM links; verify tile payload egress/licence first) with DPPS
   persistence/dip-projection as per-trace attributes, fold-safe; or execute reserve **HMDT**
   (signed hydrothermal dipole) which is viable on the pinned cache today.
3. If any organizer receipt is obtained for a past upload, add it to `registry/` and relabel
   that one score ORGANIZER-CONFIRMED; all others stay owner-reported.

\* OWNER-REPORTED (NOT ORGANIZER-CONFIRMED).
