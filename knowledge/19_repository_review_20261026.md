# Repository review — 2026-10-26 (current checkout)

## Executive decision

- **No new candidate or TIFF was generated in this review.** The standing parallel-run rule requires a single assigned method lane; the current task does not name one. The previous Round-4 slate is retained, but this review does not silently select a different lane.
- **No file is OK TO SUBMIT.** The latest committed selector snapshot says `ok_to_submit: false`. The strongest listed site artifact remains GEMSDOE32 B2 at **0.2778 (OWNER-REPORTED; not ORGANIZER-CONFIRMED)**. Existing GEMSDOE33 research TIFFs are not a replacement recommendation because their recorded scientific verdicts are negative or duplicate-blocked.
- The latest README has distinct download and submission status and points the user to the existing A33-R3-LLC research artifact. Its **OK TO DOWNLOAD** label must not be read as **OK TO SUBMIT**.

## Review findings, ordered by impact

### Blocking: experiment cannot be independently reproduced from this checkout

At review time, `data/` contains only `README.md` and the tracked artifact manifest; the 17 restored input rasters and `.cache` feature arrays described in the prior Round-4 report are absent. `data/README.md` identifies `scripts/restore_data.py --group all` and `scripts/prepare_data.py` as the restore/prepare path and documents the owner-mirror provenance limitation. Consequently, this checkout cannot rerun the current template-dependent strict validator, spatial holdout, per-feature leakage canaries, or pre-placement uniqueness checks. The earlier receipts and run cards remain historical evidence; the missing local files prevent this review from independently reproducing those measurements.

### Blocking: the requested lane is unspecified

The parallel-run protocol says to stay inside one single method paragraph. None is designated in the current request. The previous feasibility audit lists COULOMB and CURVTRACE as blocked by missing/unusable inputs, PFRT as cache-only but unrun, HMDT as previously tried without a reproducible fold-safe runner, and PALEOTEMP as lacking its required payload. Selecting PFRT merely because it is locally feasible would violate the stated lane constraint. No top-candidate HOLDOUT-DTI or projected score is supplied.

### High: historical leaderboard associations are not receipts

The nine-site table and byte-forensic evidence support a comparison of named artifacts, but the listed competition score pairings remain owner-reported. In particular, B2's documented pixel relationship to the H27-4 pruning family supports a plausible false-positive-pruning explanation; it does **not** prove why an organizer's hidden labels assigned a particular score or establish that a new submission can exceed it. No organizer receipt or DrivenData access is present.

### High: format validity is separate from promotion and portal acceptance

The committed A33-R3-LLC zero-outside and NaN-outside files were checked against their stored receipts in this checkout. Each receipt SHA-256 and byte count matches the downloaded file; both variants report a single `float32` band, EPSG:32611, shape `3730×3292`, 100 m pixel size, and the same transform. The zero-outside variants are finite throughout and their raster values are within `[0,1]`; the NaN-outside twins intentionally are not finite throughout. These are checks of saved bytes and receipt consistency only. Without `sample_submission.tif` now present, this review could not independently confirm the footprint mask or re-run the template comparison. The A33-R3-LLC receipt explicitly marks its scientific verdict negative and `weekly_slot_authorized: false`; neither file is promoted by this review.

## Nine-site executive comparison

Use the table in the README for each site's top named artifact and the evidence links. In this review the high-value conclusion is that the reported maximum, GEMSDOE32 B2, is not an independent novel surface: local forensic evidence records it as a deletion-only pruning of GEMSDOE28/31 H27-4. Its reported `0.2778` is **OWNER-REPORTED**, not an organizer receipt. All nine score-to-file associations need the same caveat. The conflicting `0.3195` and `0.4413` claims remain unverified; this review did not access or refresh the competition leaderboard.

## Verification passes

1. **Pass 1 — inspection:** read `standing_prompt.md`, `AGENTS.md`, `README.md`, current Round-4 feasibility records, selector/validator, focused receipts and test configuration. Confirmed the README already contains the nine-site comparison, submission instructions, status labels, sources, and no-slot decision.
2. **Pass 2 — adversarial checks:** confirmed the current checkout is missing the ignored source rasters and cache, so no fresh holdout, leakage canary, grid-vs-template audit, or uniqueness computation can honestly be claimed. Reopened the existing zero/NaN TIFF bytes with Rasterio and verified their recorded hashes and geometry properties against the committed receipts. This does not prove the receipts' source provenance or organizer acceptance.
3. **Pass 3 — software/site checks:** installed project dependencies in the ignored `.venv`, ran `PYTHON=.venv/bin/python bash scripts/run_checks.sh`; static site build and compile checks passed, and pytest reported **146 passed, 3 skipped**. The script explicitly skipped the optional local input-pin audit because the data files are absent. `git diff --check` passed before this review note was added; it is rerun after changes. No model experiment, submission generation, upload, or slot selection was performed.

## Recommended next work

1. Restore and verify the 17 registered owner-mirror files, then rebuild the shared cache; keep the owner-mirror limitation visible and do not treat the cache as official-source authentication.
2. In the next authorized single-method session, freeze the lane before code. The previous Round-4 slate's cache-only PFRT idea is a possible candidate only if that is the explicitly assigned method; test its individual features on the holdout first, then follow the shared hide-and-recover evaluator, surface uniqueness guard, matched confirmation, final-dot guard, and saved-byte validator. Stop immediately on a duplicate condition or a negative gate.
3. Keep all submission slots unused unless the automated selector identifies an eligible candidate; a format-valid download alone is not slot approval.
4. Continue to distinguish HOLDOUT-DTI proxies from organizer-confirmed competition scores. Do not scrape or poll the leaderboard without an authorized API or written permission.

## Run card for this review (no candidate run)

```json
{
  "hypothesis": "No new geological candidate was selected or run because the assigned single-method lane is unspecified.",
  "mechanism": "Repository, selector, receipts, and saved-artifact review only; no new raster generation or score projection.",
  "named_non_fault_process_that_could_mimic_it": "No new candidate surface exists to mimic a fault; for the prior PFRT idea, prograding fan toes and buried pediments are named non-fault mimics in the Round-4 feasibility audit.",
  "holdout_dti": null,
  "holdout_dti_evaluator_version": null,
  "withheld_positives": null,
  "holdout_ci95": null,
  "reason_unmeasured": "No experiment was run; current checkout lacks the restored data/cache and the method lane is unspecified.",
  "correlation_overlap_vs_registry": null,
  "correlation_overlap_reason": "No new surface or final dots were generated.",
  "raster_sha256": null,
  "validator_output": "No new raster. Existing receipts match current TIFF bytes, but template/footprint comparison could not be rerun because sample_submission.tif is absent.",
  "submission_name": null,
  "submission_note": null,
  "verdict": "negative"
}
```
