# Deployment-density audit — results and executive summary (2026-10-29)

**Labels used on this page.** Every local number is **HOLDOUT-DTI** (`gems-segment-pooled-v1`, 60,988 withheld
catalogue positives, 95% spatial-block CI). It is a catalogue hide-and-recover proxy, **not** a leaderboard
estimate. Every historical DrivenData figure is **OWNER/USER-REPORTED (NOT ORGANIZER-CONFIRMED)**; no organizer
receipt is stored in this repository. Preregistration: [`33_density_audit_preregistration_20261029.md`](33_density_audit_preregistration_20261029.md)
(SHA-256 `cd4a2b6a…981f0`). Evidence: [`../evidence/density_audit_20261029.json`](../evidence/density_audit_20261029.json).
Run card: [`../evidence/run_card_density_audit_20261029.json`](../evidence/run_card_density_audit_20261029.json).
Code: [`../scripts/density_audit_20261029.py`](../scripts/density_audit_20261029.py).

## Bottom line

1. **The harness is valid.** At the campaign density (2.5% per fold) it reproduced the recorded PHCONG values exactly:
   screen `0.169316` and matched-random `0.180414` (tolerance 1e-6). Canary max two-sided AUC `0.5224` (≤ 0.90).
2. **The operating point matters more than any surface.** At deployment density (`37,654 / 5,167,373 = 0.7287%`),
   the same kind of emitter scores about **half** as much on the proxy. A matched random emitter scores `0.0737`.
3. **At deployment density PHCONG does not beat random.** Paired Δ `+0.0033`, 95% CI `[−0.0010, +0.0077]`, 3/4 folds.
   The preregistered rule returns **density-robust null**. The CI crosses zero.
4. **Consequence for the repo.** Every HOLDOUT-DTI comparison recorded at 2.5% (the A33-R2 to R7 lanes) needs re-running
   at deployment density before any verdict. Their negative verdicts stand as recorded, but their absolute proxy
   values are not comparable to deployment-density values.
5. **Nothing here is OK TO SUBMIT.** No raster was produced. No slot was used. No upload was made.

## Numbers

| Run | Per-fold emission | Candidate (PHCONG) screen DTI [95% CI] | Matched-random DTI | Paired Δ [95% CI] | Fold wins | Reproduces recorded? |
|---|---|---|---|---|---|---|
| Campaign (A33-R7) | 2.5% of valid cells (129,184 dots total) | 0.169316 [0.162772, 0.175496] | 0.180414 | −0.011098 [−0.016260, −0.006098] | 0/4 | **Yes (exact)** |
| Deployment | 0.7287% of valid cells (37,654 dots total) | 0.076921 [0.073266, 0.080423] | 0.073664 | +0.003258 [−0.000990, +0.007711] | 3/4 | n/a (new) |

Both runs: 60,988 withheld positive pixels; evaluator `gems-segment-pooled-v1`; α 0.2, β 0.8; 300 m triangular kernel.
Format of every emitted map: binary, shape equal to footprint, zero outside footprint. Canary AUC unchanged across runs.

## Executive summary table — what to download, estimated score, uniqueness

| Focus site | Best owner-reported file (score\*) | File to download from THIS repo | Estimated leaderboard score | Local proxy evidence | Unique vs GEMSDOE sites? | OK to submit? |
|---|---|---|---|---|---|---|
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (0.2778\*) | none (do not copy) | **Not estimable** | none | **No** — byte-level deletion of GEMSDOE28/31 `h27-4` (see `knowledge/22`) | **NO** |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-…-9b9ea4e6-zeros` (0.2750\*) | none | **Not estimable** | none | **No** — B2 dots + 1,200 tip dots | **NO** |
| GEMSDOE28 | `h36-1-rung30-blind-r1-…-b531dae0a36f-nan` (0.2710\*) | none | **Not estimable** | none | **No** — same H19-5 emission family | **NO** |
| GEMSDOE31 | `h27-4-solo-d28-…-8acb75e1-nan` (0.2708\*) | none | **Not estimable** | none | **No** — parent of B2 | **NO** |
| GEMSDOE25 | `dotted-h19-5-d2-8-…-e56ea318af89-nan` (0.2600\*) | none | **Not estimable** | none | **No** — pixel-identical to GEMSDOE30 | **NO** |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-…-91eae1ca` (0.2600\*) | none | **Not estimable** | none | **No** — same as GEMSDOE25 | **NO** |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-…-989f59505db1-nan` (0.2477\*) | none | **Not estimable** | none | **No** — H19-5 family | **NO** |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-…-5512495c6bd1` (0.2449\*) | none | **Not estimable** | none | **No** — superset of GEMSDOE24 H25-1 | **NO** |
| GEMSDOE33 (this repo) | `h33d-analog-tip-stepover-r30-…-cb490425926e` (0.2632\*, retired) | `docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` (archive only; no `-zeros` variant in this repo) | **Not estimable** | none | **No** — max 3-px overlap 99.7% vs GEMSDOE27 topo-gap (`evidence/nine_site_audit_20261029.json`, site_verdicts); max Spearman 0.819 vs GEMSDOE31 H27-4; 92.6% of dots within 3 px of B2 (pairwise_nine_vs_all) | **NO** |

\* Owner-reported, not organizer-confirmed. These are the nine site-best values in the brief; they were not re-scored here.

**Why no estimate is given.** The only quantitative local tool is a catalogue hide-and-recover proxy. Its values sit on a
different scale from the leaderboard (≈0.07 to 0.17 here, ≈0.27 owner-reported elsewhere), and no validated mapping
between the two exists. A projected leaderboard score would therefore be invented, which the protocol forbids.

**The one local anchor that is measured.** At deployment density, an emitter with no spatial preference scores
**0.0737 HOLDOUT-DTI**. Any future candidate must beat that matched-random floor, with a paired CI above zero, at deployment density.

## Unique downloadable TIFFs in this repo (all research only)

No file in this repo is OK TO SUBMIT. Per the recorded selector output (`docs/data/submission_selection.json`, 19 run cards),
0 are eligible. The unique, format-valid files are listed in [`../docs/executive-summary.html`](../docs/executive-summary.html)
with their gate status. The surface audited here is `A33-R7-PHCONG`, whose research TIFF is `docs/downloads/gemsdoe33-a33-r7-phcong-37654-20261028-45958ee5a5bc-zeros.tif`. At deployment density its proxy does not beat its matched-random control, so it has no measured research advantage there.

## Irregularities recorded this session (see `registry/irregularities.json`)

- **IR-33-20261029-DENSITY-01**: all prior HOLDOUT-DTI comparisons use 2.5% emission. Deployment is 0.73%. The random floor drops from 0.1804 to 0.0737.
- **IR-33-20261029-BAND-DEPTH-01**: the official problem page lists a "top-of-crustal magnetic source depth estimate". Neither the owner-mirror 19-band file nor the organizer's own reference-notebook band listing contains a band with that description. See [`36_official_verification_20261029.md`](36_official_verification_20261029.md).
- **IR-33-20261029-BAND-EQ-01** (wording only): the official page says "density of earthquakes"; the organizer's notebook and the mirror both say "distance to earthquake" for band 10 and "intensity or density" for band 16.
- **IR-33-20261029-METRIC-MASK-01**: the official metric text does not state that visible catalogue pixels are masked from false-positive cost. The repository's evaluator assumes they are.
- **IR-33-20261029-ALLFAULTS-01**: the official submission-format text asks for predictions for "all faults in the region", while the metric section scores against newly identified faults. Interpretation needs organizer confirmation.
- **IR-33-20261029-OUTSIDE-01**: the official format allows "null or nan" outside the bounds. Several repository files use zero outside. The organizer's reference notebook itself writes finite zeros in unpredicted cells (`y_out = np.zeros`). Acceptance of either encoding is unconfirmed. The "[0, 1]" portal error is still unexplained.

## What would change this verdict

1. A candidate whose paired Δ over its matched random control at deployment density has a 95% CI strictly above 0, with at least 3/4 fold wins, on the same holdout.
2. Organizer confirmation of the metric's catalogue-masking rule (IR-33-20261029-METRIC-MASK-01). If the catalogue is scored, the current evaluator is misspecified and every holdout number here changes.
3. Access to the official magnetic source-depth band (IR-33-20261029-BAND-DEPTH-01). See the hypothesis slate.
