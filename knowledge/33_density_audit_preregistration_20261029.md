# Deployment-density audit — preregistration (2026-10-29)

**Status:** frozen before any code for this audit ran. Written in response to the
repository-review item "repair the evaluation operating point first"
(`knowledge/31_repo_review_20261028.md`, ranked next work item 1).

## 1. Question

Do the negative matched-random comparisons recorded in the A33-R5/R6/R7 lanes survive when
the holdout emission density is set to the **deployment** density instead of the campaign's
2.5% per-fold density?

- Campaign density (`D_camp`): `BUDGET_FRAC = 0.025` × valid cells per fold
  (`scripts/run_phcong_campaign.py`, `emit_for`).
- Deployment density (`D_dep`): the full-footprint emission budget `37,654` dots divided by the
  template footprint count, applied per fold as `round(D_dep × valid.sum())`.
  Footprint count is read from `grid.template_footprint()` (measured, not authenticated).

Motivation: at `D_camp` a random emitter covers a large share of 300 m kernel neighbourhoods, which
inflates the matched-random control. A candidate can then look worse than random for reasons that
do not apply at deployment density.

## 2. Surface and control (no new candidate)

- Surface: the existing label-free PHCONG surface (`src/gemsdoe33/phcong.py::build_phcong_surface`).
  It reads no catalogue input. It was chosen because its `D_camp` result is already on record
  (`evidence/a33_r7_phcong_experiment_20261028.json`), so the audit can check the harness against it.
- Emitter: `csht_transfer.celf_emit_300m` with `min_self_spacing_px=2.5`, the same call as the campaign.
- Matched control: `celf_emit_300m` on uniform random scores with seed `20261028`, same budget,
  same eligibility mask. Same seed as the campaign so the `D_camp` numbers can be reproduced exactly.
- Holdout: `vendor/gems24_template/holdout.py::SegmentHoldout(buffer_px=15)`, evaluator
  `gems-segment-pooled-v1`, pooled DTI (α 0.2, β 0.8, 300 m triangular kernel), 1,999-draw
  spatial-block bootstrap, paired comparison by `compare_paired`.
- Catalogue-proximity exclusion: eligibility excludes cells within 2 px of the visible catalogue, as
  in the campaign.

## 3. Checks before interpreting the deployment result

1. **Harness reproduction (gate).** At `D_camp`, the audit must reproduce the recorded PHCONG screen
   `0.169316` and matched-random DTI `0.180414` to 1e-6. If not, the harness differs and the audit
   halts without a deployment conclusion.
2. **Leakage canary.** Feature-alone AUC for the PHCONG surface must be ≤ 0.90 (protocol Rule 4).
3. **Format of emitted maps.** Binary `{0,1}` maps on the footprint, zero outside, checked before scoring.

## 4. Decision rule (fixed now)

Let `Δ_dep` be the paired DTI difference, PHCONG minus matched random, at `D_dep`.

- **Density-robust signal:** `Δ_dep` 95% CI strictly > 0 **and** candidate wins in ≥ 3 of 4 quadrant folds.
  Consequence: the negative verdicts are density-sensitive; re-run the affected lanes at `D_dep` before
  any verdict. No slot is implied.
- **Density-robust null:** otherwise. Consequence: the negative PHCONG verdict stands at both densities.
- Either outcome: no slot, no selector promotion, no retuning. Numbers are **HOLDOUT-DTI** with the
  evaluator version, withheld positives (60,988) and 95% CI. Projection is not a leaderboard estimate.

## 5. Budget

This audit is Experiment 1 of the 2026-10-29 session. It does not start another candidate lane.
Budget: 3 experiments or 2 hours, whichever first.

## 6. Out of scope

No DrivenData access. No leaderboard read. No slot or upload. No new geological candidate. No change to
`evaluate_holdout.py`, `vendor/`, or previously written evidence. Preserved evidence is read only.
