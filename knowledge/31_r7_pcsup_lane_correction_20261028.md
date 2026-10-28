# A33-R7-PCSUP lane correction (2026-10-28)

## Decision

**PCSUP is not unique under the required pre-placement lane guard and is not OK to submit.** Its final emitted dots pass the 3-pixel overlap guard, but its pre-placement surface does not. The surface guard is explicitly an earlier, independent stop condition; a final-dot pass cannot retroactively clear it. This correction supersedes the earlier statement in `knowledge/30_phcong_results_20261028.md` and the PCSUP row in its run-card summary that claimed both stages passed.

No further experiment, placement, tuning, or submission-slot selection was performed after this audit. The A33-R7 budget remains 3/3 experiments. The PCSUP TIFF remains archived as a research artifact only; the link is not a recommendation to use or upload it.

## Evidence re-read (not recomputed)

Source: `evidence/a33_r7_pcsup_experiment_20261028.json`, uniqueness section. Its pre-placement `surface` record explicitly has `passed: false`, `overlap_stop_gt: 0.7`, `max_preview_fraction_within_3px: 0.8608381579646253`, and `max_abs_spearman_rho: 0.10095914928039568`. Therefore the surface exceeds the lane's 70% overlap limit by 16.08 percentage points; Spearman remains below 0.90. The final-dots record has a maximum within-3px overlap of 0.5827534923248526 (58.28%) and passes that stage. The measured TIFF's SHA-256 is `7165ef02ade6eeec17f4fc99b02cf871783d3070704a119c414e8e818fe8cf5e`; the run-card SHA-256 is `e501e7986bd64a6a7f8067bc8f81d98284118d12269bcf4c8cec790c2db1d8d8`.

The run had already continued to final placement and holdout evaluation despite the failed surface guard. This is a process irregularity, not evidence that the surface threshold should be waived. The run-card and experiment JSON are preserved unchanged. HOLDOUT-DTI values in them are retained for audit, but are exploratory diagnostics only under this lane rule; they are not valid promotion evidence, score estimates, or a basis to spend a slot. The separate matched-random gate was also non-positive, independently precluding promotion.

## Consequence

- Log PCSUP as a duplicate/drifted candidate under the requested protocol; stop this branch of work.
- Do not call its raster unique versus the listed GEMSDOE sites, despite final dots passing.
- Do not infer a leaderboard score from its HOLDOUT-DTI.
- Correct the executive summary, site banner, standing decision, and irregularity registry; leave original evidence immutable.
- Next work requires a newly frozen campaign and a pre-placement guard that automatically terminates before placement/evaluation when any registry surface exceeds either threshold. No new lane is selected here, and no fourth A33-R7 experiment is authorized.

See machine-readable correction `evidence/a33_r7_pcsup_lane_correction_20261028.json` and the run card/experiment JSON cited above. The registry is a 21-raster pinned subset, not a complete archive of all possible submissions; even a pass would establish only scoped novelty.
