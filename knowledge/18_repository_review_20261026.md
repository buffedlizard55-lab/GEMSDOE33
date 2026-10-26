# Repository review — 2026-10-26

## Scope and evidence boundary

Reviewed `standing_prompt.md`, `README.md`, the fail-closed selector, the generated executive summary/results pages, the nine-site forensic record, and the latest A33-R3 experiment reports. Repository state was clean at review start. User-supplied historical competition scores remain **OWNER-REPORTED**, not organizer-confirmed; this checkout contains no submission receipt tying a leaderboard score to a TIFF.

## Executive decision

- **OK TO DOWNLOAD:** yes for the current unique A33-R3-LLC *research artifact* only. Its file and saved-byte validator receipt are linked from the README and the executive-summary page.
- **OK TO SUBMIT:** **no**. Do not spend a competition slot. Its current recorded verdict is negative because it did not beat the comparison baseline on both the screen and the frozen confirmation. The selector has no eligible candidate.
- **Highest reported focus-site score:** GEMSDOE32 B2 at **0.2778 (OWNER-REPORTED; not organizer-confirmed)**. Its TIFF was measured to be a deletion-only pruning of GEMSDOE28 H27-4, not an independent new fault-discovery surface. Its reported score is not proof that a new method can reproduce or exceed it.
- The brief also mentions leaderboard values `0.3195` and `0.4413`; neither is verified by this repository, and no score projection is represented as a score.

## Nine-site comparison

The following scores are copied from the user-provided research ledger and are therefore **OWNER-REPORTED**. Raster identities/overlaps are measured locally as documented in `evidence/nine_site_forensics_20261025.json`.

| Site | Highest named submission in the supplied comparison | Reported score | Unique among the focus-site rasters? | Assessment |
|---|---|---:|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5` | 0.2477 | No | Dotted-pruning family; user score unconfirmed. |
| GEMSDOE25 | `dotted-h19-5-d2-8` | 0.2600 | No | Pixel-identical prediction reported/measured against GEMSDOE30. |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5` | 0.2449 | Yes within listed focus set by exact identity; exact-neighbor uniqueness thresholds must use full raster audit | Reported only; not an organizer receipt. |
| GEMSDOE28 | `h36-1-rung30-blind-r1` | 0.2710 | No | Shares near-identical H27-4/B2 lineage; do not treat as distinct evidence. |
| GEMSDOE30 | `d28-poisson300m-offcat-44090` | 0.2600 | No | Same 44,090-dot prediction as GEMSDOE25. |
| GEMSDOE31 | `h27-4-solo-d28` | 0.2708 | No | Pixel-identical to GEMSDOE28 H27-4 per repository forensics. |
| GEMSDOE32 | `h33-h33-2-b2` | **0.2778** | No | Highest supplied score; pixel-exact deletion-only pruning of H27-4; duplicate lane. |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30` | 0.2632 | Yes within the listed focus set, subject to a registry-wide guard | Owner-reported historical result. |
| GEMSDOE36 | `anderson-geothermal-pinn-38854` | 0.2750 | No | Strict superset of B2 plus 1,200 dots in recorded comparison. |

“Unique” in this table means the recorded exact/raster-neighborhood evidence does not establish a copy, not proof of uniqueness against every possible private or unpinned submission. The detailed execution-time registry guard must remain authoritative for a new candidate.

## Existing candidate hypothesis slate and next step

The repository already records a ranked five-hypothesis slate in `knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md`. It is not newly preregistered by this review. Its leading two research ideas are:

1. **A33-R4-COULOMB:** calculate elastic Coulomb stress transfer from the locally pinned QFFD fault attributes. This is a new physical mechanism relative to geometry-only tip/stepover features; moderate implementation cost. First verify equations, units, fault geometry, sign convention, and spatial holdout leakage before any candidate raster is emitted.
2. **A33-R4-CURVTRACE:** a multi-azimuth, 1 m LiDAR morphology/curvature trace-continuity detector with explicit LiDAR void masking. It targets sub-100 m scarp morphology, unlike the repository's regional 100 m geophysical surfaces; higher implementation and geomorphic-mimic risk.

The existing slate also identifies **HMDT** as a reserve with a concurrent unvalidated artifact; do not assume it has a holdout result. `PALEOTEMP` is explicitly blocked until the named additional data product from DOE GDR submission #1391 is obtained and pinned. Do not spend a slot on these candidates without their own preregistration, feature-alone leakage canaries, paired spatial holdout evaluation, final surface and dot uniqueness guards, and fail-closed promotion selection.

## Verification passes

1. **Implementation/review:** confirmed README directs contributors to the standing brief; inspected the submission writer/selector and generated site content. The existing strict selector requires positive screen and independent confirmation gates, byte hashes, saved-byte format checks, a one-TIFF zip, and a 1–140 character note. It does not upload or access DrivenData.
2. **Adversarial review:** confirmed all historic scores are explicitly distinguished from measured raster facts; the leaderboard is not refreshed or scraped. Confirmed the research TIFF is not labeled as recommended for submission. Identified the absent competition training/template rasters in `data/` (only a README and manifest/artifact metadata are present at the root-level listing), so full local fresh raster regeneration and a live template re-audit could not be run in this checkout.
3. **Final checks:** `scripts/build_site.py` completed. Test suite: **143 passed, 3 skipped** after installing the declared project dependencies in a temporary local virtual environment. `compileall` and `git diff --check` passed. The initial stock-environment `scripts/run_checks.sh` invocation failed because system Python had no `pytest`; the tests themselves passed after installing dependencies. No new submission was generated in this review, consistent with the three-experiment limit and the existing selector's no-promotion decision.

## Limitations / follow-up

- No DrivenData authentication or authorized download capability is available here; no competition upload, submission receipt, or score confirmation can be created.
- Competition source rasters are absent from this checkout, blocking an independent rerun of the spatial holdout and strict grid validation from raw inputs.
- User-supplied scores and GitHub Pages artifacts may change; do not claim a current live leaderboard feed. Refresh only through an allowed, documented source.
- Next session: validate/prove A33-R4-COULOMB's mechanics and data semantics, preregister before running, use the cached features and required whole-segment buffered holdout, and stop if its surface violates the registry correlation/overlap guard. Keep the submission slot unused until the selector returns eligible.

## Run card for this review (not a candidate submission)

```json
{
  "hypothesis": "No new submission hypothesis was run; next candidate is the preregistered A33-R4-COULOMB slate item.",
  "mechanism": "Repository-level review only; no new raster generation or score projection.",
  "named_non_fault_mimic": "Regional gravity/geophysical gradients from lithologic contacts can mimic stress-associated corridors.",
  "holdout_dti": null,
  "holdout_ci95": null,
  "correlation_overlap_vs_registry": "Not measured for this review; no new raster. Use candidate-specific surface and final-dot checks.",
  "raster_sha256": null,
  "validator_output": "Not applicable: no raster generated. Existing README marks A33-R3-LLC OK TO DOWNLOAD and NOT OK TO SUBMIT.",
  "submission_name": null,
  "note": "No submission generated or slot used.",
  "verdict": "negative"
}
```
