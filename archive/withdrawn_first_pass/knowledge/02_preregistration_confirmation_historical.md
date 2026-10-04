# WITHDRAWN — first-pass confirmation plan (historical; not a promotion gate)

**Date:** 2026-10-04 · **Session:** `arena/01a104ca-gemsdoe33`
**Status:** this design was committed before its runner, but a subsequent review found the
underlying instrument uses the held-out truth locations to reconstruct predictions and tunes a
reconstruction radius against owner-reported live scores. The confirmation seeds also overlap the
exploratory selection run. Therefore the result in
`archive/withdrawn_first_pass/evidence/confirmation_pruning.json` is withdrawn and MUST NOT be used
to approve a weekly submission slot. See `evidence/first_pass_disposition.json` and
`registry/irregularities.json` (`IR-33-HOLDOUT-01`). The historical file is preserved to make the
review auditable.

## What is being confirmed

`scripts/prune_incumbent.py` (2 seeds x 4 folds = 8 paired cells, two reconstruction radii)
measured the following mean paired ΔDTI against the incumbent `base_d280_44090`
(the live-0.2600 emission, 44,090 px):

| arm | radius 3 | cells ahead | radius 4 | cells ahead | mean Δ |
|---|---:|---:|---:|---:|---:|
| `base_prune_det_40000` | +0.00077 | 4/8 | +0.00110 | 5/8 | +0.00093 |
| `base_prune_inc_40000` | +0.00347 | 6/8 | +0.00434 | 7/8 | +0.00390 |
| **`base_prune_det_inc_40000`** | **+0.00529** | **7/8** | **+0.00686** | **8/8** | **+0.00608** |
| `base_prune_random_40000` (control) | -0.00524 | 0/8 | -0.00172 | 1/8 | **-0.00348** |
| `base_prune_det_inc_35000` | +0.00515 | 6/8 | +0.00584 | 6/8 | +0.00549 |
| `base_prune_random_35000` (control) | -0.00967 | 0/8 | -0.00225 | 2/8 | -0.00596 |

Its pre-declared gate `G3` requires the arm to be ahead in **every** fold x seed cell. With only
8 cells, one dissent is not resolvable — it could be noise or it could be a real quadrant-level
failure. **The correct response to a near-miss is more cells, not a looser criterion.**

The observation that motivated this run, and which is *not* the thing being re-tested here: the
`det x inc` combination beats both of its factors at all three budgets tested
(40k: +0.00608 vs +0.00093 and +0.00390; 35k: +0.00549 vs -0.00009 and -0.01291;
30k: +0.00109 vs -0.00613 and -0.03000). Only the choice of budget among {40k, 35k, 30k} is
selected; the content effect is not.

## Frozen design

* **Budget, chosen a priori and not from the sweep:** drop the lowest-scoring **10 %** of the
  incumbent's 44,090 dots, i.e. `N = 39,681`. This is a round, conservative trim declared now;
  it is deliberately not the best-of-three number from the exploratory sweep.
* **Score:** `detector_oof_probability x (0.5 + 0.5 * normalised incompleteness)`, both fields
  already on disk (`.cache/oof_probability.npy`, `.cache/incompleteness_norm.npy`).
* **Arms:** `prune_det_inc` (primary), `prune_det_only`, `prune_inc_only`,
  `prune_random` (matched-N content-blind control), and `base_d280_44090` (comparator).
* **Cells:** 4 quadrant folds x **4 seeds** (0, 1, 2, 3) = **16 paired cells**, per radius.
* **Radii:** 3 and 4, as before.
* **Instrument:** `calibrated_domain` (visible catalogue removed, hidden draw preserved), hidden
  set size `K x area(fold)/area(footprint)` with `K = 12,226`, incompleteness-weighted draw,
  catalogue shadow reconstructed at radius `r`.

## Frozen gate

| id | criterion | threshold |
|---|---|---|
| **C1** | mean paired ΔDTI across the 16 cells, averaged over both radii | > 0 |
| **C2** | same | >= **+0.001** (tightened from +0.0005: with 16 cells the standard error is smaller) |
| **C3** | cells ahead | >= **15 / 16** at **each** radius |
| **C4** | content control | `prune_det_inc` beats `prune_random` at every radius |
| **C5** | sign consistency | positive at **both** radii |

All five must hold for the arm to be promoted into `docs/downloads/` as the submission candidate.
If it fails, the incumbent is shipped unchanged and this file records a second honest negative.

## What is deliberately *not* claimed

The instrument's hidden set is drawn from the visible catalogue, which is the *mapped* subset of
the fault population and therefore systematically easier than the organiser's private set. A win
here licenses packaging, never a claim about a leaderboard number.
