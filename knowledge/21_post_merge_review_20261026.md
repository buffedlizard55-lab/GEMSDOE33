# Post-merge repository review — 2026-10-26

## Executive decision

**No file is OK TO SUBMIT.** The newest unique generated TIFF in the merged checkout is **S33-SEISDIL**. It is **OK TO DOWNLOAD for research/reproducibility only** and **NOT OK TO SUBMIT**: its preregistered, buffered hide-and-recover comparisons lost to the matched B1 baseline in every fold on both splits. The file was produced by the separate, preregistered parallel-session PR #30 and is preserved here as a negative result; this review did not rerun or retune that experiment. The automatic selector checks 12 run cards and returns zero eligible submissions.

- **Latest unique file:** `docs/downloads/gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros.tif`
- **Submission name:** `gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros`
- **Note (80/140):** `GEMS33 S33-SEISDIL strain-seismicity gate 37654d | gate NEGATIVE | 3463540a7e02`
- **SHA-256:** `5eb9572946fa62356ebc0cbfef22bb54aa2ef094cb8b4a84b52e6b80e120db96`
- **Download:** [GeoTIFF](../docs/downloads/gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros.tif) · [single-TIFF ZIP](../docs/downloads/gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros.zip) · [run card](../evidence/s33_seisdil_run_card_20261026.json) · [uniqueness audit](../evidence/s33_seisdil_uniqueness_20261026.json)

The local saved-byte validator passes this primary zeros-outside raster: one `float32` band, `EPSG:32611`, 3,730 × 3,292, exact owner-mirror template transform, finite whole array in `[0,1]`. The separate surface and final dots passed the recorded duplicate guards vs 22 registry rasters (surface max |Spearman| 0.0934 / max 3-px overlap 58.11%; final max |Spearman| 0.0307 / max overlap 42.92%). These are local audit results, not organizer acceptance, complete global uniqueness, or competition scores. **The format banner must not claim that zero-outside fixes the user's portal error:** the rejected original bytes and organizer diagnosis are absent, and the recorded official-format text says null/NaN outside. Do not upload either variant while the selector says NO.

## HOLDOUT-DTI result — proxy, not a competition score

The frozen S33-SEISDIL run card labels the following measurements **HOLDOUT-DTI**, evaluator `gems-segment-pooled-v1`, with 60,988 withheld positives per split:

| Split | Candidate vs B1 baseline | Paired difference (95% CI) | Fold wins |
|---|---|---|---|
| Screen | 0.114154 vs 0.124612 | −0.010458 `[−0.016294, −0.004865]` | 0/4 |
| Confirmation | 0.117619 vs 0.129488 | −0.011869 `[−0.017655, −0.006164]` | 0/4 |

The stored run card leaves standalone candidate-DTI confidence intervals null; the paired-difference intervals are available and shown above. Do not present these DTI values or differences as organizer results or as an estimate of leaderboard score. Four feature-alone leakage canaries passed (maximum fold AUC 0.5498), but passing canaries/uniqueness/format cannot reverse the negative outcome. Do not retune this lane from its holdout.

## Scientific rationale and review of the target score

S33-SEISDIL preregistered a strain-seismicity corridor-gating hypothesis: geodetic dilatation/shear-rate gradients and earthquake-intensity ridges gate a fold-trained regional HGB prior, followed by 300 m CELF emission. The named non-fault mimic is caldera/aquifer deformation and volcanic seismic swarms without a throughgoing fault. The result is negative against B1 on both holdout splits.

The nine-site table in `README.md` and the generated executive-summary page remain the comparison source for GEMSDOE24/25/27/28/30/31/32/33/36. The highest supplied focus-site value is GEMSDOE32 B2 at **0.2778 USER/OWNER-REPORTED, NOT ORGANIZER-CONFIRMED**. Local byte forensics show it is deletion-only pruning of the GEMSDOE28 H27-4 prediction family. A plausible mechanism is reduced false-positive mass under the competition's asymmetric DTI weights; local evidence does **not** prove why the hidden organizer labels produced the supplied score or that pruning alone caused it. It is prior art and must not be copied, lightly altered, or re-uploaded.

The prompt's `0.3195` and `0.4413` leaderboard claims conflict and were not authenticated here. No official leaderboard refresh, DrivenData login, upload, or organizer receipt occurred. **No score above 0.2778 or any leaderboard value is projected.** The S33 holdout is far below B1; it provides no evidence for beating the reported 0.2778.

## Ranked hypotheses and data feasibility

The 3–5 candidate geology slate, named layers/signatures, non-fault mimics, official-source links, expected qualitative priority, costs, and availability are retained in [`knowledge/18_round4_feasibility_audit_20261026.md`](18_round4_feasibility_audit_20261026.md) and [`docs/hypotheses.html`](../docs/hypotheses.html). In brief:

1. **COULOMB stress transfer** — quaternary fault geometry and slip attributes; blocked because the CSV lacks vertices/strike and companion vector coordinates have no declared CRS/target-grid alignment.
2. **CURVTRACE** — raw 1 m USGS 3DEP scarp morphology; blocked because raw tiles are unstaged.
3. **PFRT** — local cached basement-depth/gravity-gradient directional projection; feasible to preregister, but untested and high-duplicate-risk.
4. **HMDT** — not genuinely untried; old TIFF lacks a reproducible fold-safe runner/card.
5. **PALEOTEMP** — DOE GDR #1391 temperature/paleosinter payload absent; schema, coverage and payload were not audited here.

Sources named in the repository for manual review include [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [USGS 3DEP](https://www.usgs.gov/3d-elevation-program), [DOE GDR #1391](https://gdr.openei.org/submissions/1391), the [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), and the [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution). URLs are for manual review; source pages were not freshly fetched in this review. The current network allowlist excludes these non-GitHub official hosts. Mirror hashes do not authenticate official provenance, licence, or source completeness.

## Three verification passes

1. **Implementation / restoration:** Installed project requirements, restored all 17 registered owner-mirror inputs with size/SHA checks, ran `scripts/audit_inputs.py`, and rebuilt the shared 121-channel cache via `scripts/prepare_data.py --skip-detector`. No detector was trained during this restoration pass. The separate PR #30 campaign supplies the frozen S33-SEISDIL TIFF/run card.
2. **Adversarial review:** Confirmed the sample mirror's finite values exactly equal `labels.tif` on the 5,167,373-cell footprint; it remains grid/footprint metadata only, never training or absence truth. Reopened the S33 primary bytes and its receipt; the output is locally format-valid but scientifically negative. Found a flat-vs-nested input path mismatch: current pins restore to flat `data/`, while the old template-label audit default expected `core/`. Fixed that audit default to `gemsdoe33.paths.DATA`; flagged still-nested legacy entry points in `IR-33-FLAT-INPUT-LAYOUT-01`.
3. **Final checks:** Updated the static site builder to place the newest S33 artifact first, show the negative HOLDOUT-DTI comparison and paired CI, and remove the unsupported assertion that zero-outside “fixes” the portal error. Updated selector handling to locate flat-schema cards only by a unique exact raster SHA-256, then verify the TIFF/ZIP bytes; added regression tests for S33's flat run-card schema. The complete local check script passed: **156 tests passed**, site pages regenerated, all **17/17** registered input pins verified, template/label diagnostic passed on **5,167,373** finite-footprint cells with zero positive-set disagreements, all Python files compiled, and `git diff --check` passed. The selector found **0 eligible of 12** run cards; for S33, the file/hash/format/ZIP/note checks pass while its negative verdict and promotion gates correctly remain false. No candidate experiment or upload was run in this review.

### Tooling change

`scripts/select_submission.py` previously understood a few nested/flat run-card forms but failed to resolve S33's `submission_name`/`submission_note` + raster-hash schema into its actual downloaded bytes. It now discovers a TIFF only by a unique SHA-256 match and a ZIP only when it contains exactly that TIFF, then still requires the card's positive verdict, promotion gates, validator, and note limits. S33 remains blocked by its negative scientific verdict/promotion gates; this is a visibility/verification correction, not promotion.

## Remaining work

- Do not spend a submission slot. The selector presently returns zero eligible files.
- For a future run, freeze one explicit method lane before implementation, use the shared feature cache/evaluator/writer, derive catalogue-based features solely from fold-visible faults, run each feature-alone leakage canary, screen surface uniqueness before placement and final-dot uniqueness afterward, and stop on a duplicate or negative gate within the 3-experiment/2-hour budget.
- Reconcile the legacy nested `gems33.grid.data_dir()/core` entry points before reactivating them. The current active cache code uses flat `gemsdoe33.paths.DATA`.
- Ask the organizer for the correct outside-footprint and range-check interpretation only through an authorized route; no human scientific inspection is substituted for the project's automated gates.
- Obtain valid score-page receipts before calling any leaderboard figure confirmed. Competition score cannot be derived from these catalogue-proxy holdouts.

## Current review run card

```json
{
  "hypothesis": "S33-SEISDIL strain-seismicity corridor gate: geodetic dilatation/shear gradients and earthquake-intensity ridges may mark permeable faults missing from the catalogue.",
  "mechanism": "A fold-trained B1 regional HGB surface gated by the percentile mean of dilatation-gradient, shear-gradient and ieq-ridge channels, followed by 300 m CELF emission at 37,654 dots.",
  "named_non_fault_process_that_could_mimic_it": "Caldera/aquifer deformation and volcanic seismic swarms without a throughgoing fault.",
  "holdout_dti": {
    "label": "HOLDOUT-DTI",
    "evaluator_version": "gems-segment-pooled-v1",
    "withheld_positives": 60988,
    "screen_candidate": 0.11415371619795955,
    "screen_candidate_95pct_ci": null,
    "screen_baseline": 0.12461214544050417,
    "screen_paired_delta": -0.010458429242544615,
    "screen_paired_delta_95pct_ci": [-0.016294166215130843, -0.004864839664105639],
    "screen_fold_wins": "0/4",
    "confirmation_candidate": 0.11761865259662631,
    "confirmation_candidate_95pct_ci": null,
    "confirmation_baseline": 0.12948780002598545,
    "confirmation_paired_delta": -0.011869147429359142,
    "confirmation_paired_delta_95pct_ci": [-0.01765515580455952, -0.00616426931741835],
    "confirmation_fold_wins": "0/4",
    "leaderboard_score_projection": null
  },
  "feature_canaries": "PASS; maximum fold AUC 0.5497848565; no AUC above 0.90",
  "correlation_overlap_vs_registry": {
    "registry_count": 22,
    "surface_max_abs_spearman": 0.09337241778406684,
    "surface_max_3px_fraction": 0.5811334785148988,
    "final_dots_max_abs_spearman": 0.030701757172981164,
    "final_dots_max_3px_fraction": 0.4292239868274287
  },
  "raster_sha256": "5eb9572946fa62356ebc0cbfef22bb54aa2ef094cb8b4a84b52e6b80e120db96",
  "validator_output": {
    "local_format_pass": true,
    "single_band_float32": true,
    "crs": "EPSG:32611",
    "shape": [3730, 3292],
    "transform_matches_template": true,
    "no_nan_inside_footprint": true,
    "whole_array_values_in_0_1": true,
    "outside_zero": true,
    "portal_acceptance": "unverified"
  },
  "submission_name": "gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros",
  "submission_note": "GEMS33 S33-SEISDIL strain-seismicity gate 37654d | gate NEGATIVE | 3463540a7e02",
  "verdict": "negative"
}
```
