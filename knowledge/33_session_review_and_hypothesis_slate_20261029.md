# Fresh-checkout revalidation (2026-10-29)

## Decision

**OK TO SUBMIT: NO. No new geological candidate TIFF was generated in this revalidation.** The latest nine-site audit has been rerun from pinned owner-repository blobs; all nine site-best rasters still trigger the duplicate guard and the automatic selector still returns zero eligible candidates. Existing unique research TIFFs remain research-only because none has cleared the applicable holdout gate. Historical scores are **USER/OWNER-REPORTED**, not organizer-confirmed.

This note records the fresh-checkout restore/retest performed on the session branch. It does not supersede or duplicate the separate 2026-10-29 deployment-density experiment recorded in `knowledge/34_density_audit_results_20261029.md` and `evidence/run_card_density_audit_20261029.json`. That deployment-density audit is Experiment 1 of its 3-experiment/2-hour methodological campaign and returned a density-robust null. The older A33-R7-PHCONG campaign remains exhausted at 3/3.

**Update after integrating newer main (PR #46):** a separate preregistered H34-COH lane tested line coherence of magnetic ridges, created a genuinely unique and format-valid research TIFF, and returned a negative holdout result versus B1 on both screen and confirmation. The file is **OK TO DOWNLOAD for research only: YES; OK TO SUBMIT: NO**. This experiment is documented in `knowledge/37_h34_hypothesis_slate_and_prereg_20261029.md` and `knowledge/38_h34_coh_result_and_b2_answer_20261029.md`; do not attribute that TIFF to the fresh-checkout revalidation above, and do not mix H34's 2/3 experiment budget with the separate density audit budget.

## Fresh-checkout reproducibility work (MEASURED)

- Created an isolated `.venv` and installed the pinned requirements; environment files are ignored and not committed.
- `python scripts/restore_data.py --group all`: restored and SHA-256-verified all 17 registered owner-mirror inputs. The largest, `training_features.tif`, is 418,912,844 bytes. This verifies mirror-byte identity, **not** organizer provenance or license.
- `python scripts/prepare_data.py`: rebuilt 121 cached research channels from those pinned bytes; runtime 194.4 seconds. The exact template footprint contains 5,167,373 finite cells. Sample values exactly match the mirrored labels on this footprint and are still forbidden as truth.
- `python scripts/restore_focus_registry_r3.py`: restored and SHA-256-verified 22 pinned comparison rasters.
- `python scripts/nine_site_audit.py`: reran all 38 pinned focus-site and local research TIFFs against each other and the 22-raster registry. Each of the nine site-best files was format-valid but triggered the duplicate guard.
- `python scripts/validate_nine_site_files.py`: 37/38 pass default format checks; 28/38 pass strict-zero-outside checks; 0 are cleared to submit. These are format results only.
- `PATH="$PWD/.venv/bin:$PATH" bash scripts/run_checks.sh` before the parallel-density changes: **197 tests passed**. After merging the density-audit lane and official-source review into this checkout, the complete current suite passed **204 tests**; 17/17 input pins were verified, sample/label overlap reproduced, selector returned no eligible candidate, and compile/diff checks passed.

Evidence: `evidence/input_grid_audit.json`, `evidence/nine_site_audit_20261029.json`, `evidence/nine_site_validator_20261029.json`, `evidence/submission_selection_20261029.json`, and `evidence/run_card_session_20261029.json`.

## Hypotheses and testing boundary

The authoritative ranked hypothesis slate for this date is `knowledge/35_hypothesis_slate_20261029.md`; official-source claims and availability checks are in `knowledge/36_official_verification_20261029.md`. These supersede the preliminary cache-feasible slate written earlier in this branch. The best genuinely distinct candidate in the verified slate is H-MAGDEPTH (a structural step in magnetic source depth), but it is **blocked**: neither the restored owner-mirror 19-band raster nor the official reference notebook's 19-band list contains the described source-depth layer, and the official competition training download requires login unavailable here. A self-derived depth estimate from `tmi` would be a different method and would need fresh preregistration and local validation.

The previously mentioned cross-gradient-coherent magnetics/gravity candidate remains an untested, lower-priority derivative of already-used potential-field evidence; it is not promoted over the official-data gap. No feature-alone canary, surface novelty check, H-MAGDEPTH HOLDOUT-DTI, 95% CI, or candidate TIFF was produced in this revalidation. The session run card uses null for these fields rather than inventing evidence. Do not spend a weekly slot.

## Focus-site scores and B2 interpretation

The exact per-site file links, user-reported values, format results, duplicate findings, and explicit download/submit labels are in `docs/executive-summary.html` and `docs/data/nine_site_audit.json`. No numeric leaderboard estimate is defensible. The cited GEMSDOE32 B2 value **0.2778*** is user/owner-reported and byte-audited as a deletion-only subset of GEMSDOE28/31 H27-4; this does not prove why it earned the reported value. The prompt's 0.3195 and 0.4413 “current high score” values conflict and have no organizer receipt in this repository.

## Three-pass review

1. **Implementation/verification:** restored and hashed all 17 inputs, rebuilt 121 channels, restored 22 registry rasters, reran the 38-file audit/validator, and ran the full test/audit suite.
2. **Adversarial review:** confirmed all nine site-best files remain duplicates; confirmed template/label overlap and no sample-value leakage; checked scores remain owner-reported; confirmed no new geological TIF, DrivenData upload, or selector promotion occurred.
3. **Requirements reconciliation:** nine-site executive table and submission status are present; five hypotheses and official availability checks are in `knowledge/35` and `knowledge/36`; a unique, high-scoring new submission is **not delivered** because the best documented new layer is unavailable and no candidate passed a holdout. The separate density audit provides the relevant measured negative result and is explicitly not a leaderboard estimate.

## Limitations and next actions

- No DrivenData authentication, organizer receipt, live score-to-file identity, or slot count.
- Owner-mirror hashes prove byte identity only; they do not authenticate organizer origin, license, or score pairing.
- The sample template's finite values equal the mirrored catalogue labels; use it only for grid and footprint.
- Local format validation is not portal acceptance; outside-footprint policy and the reported range error remain unresolved.
- Follow `knowledge/35` and `knowledge/36`: first obtain authoritative clarification or locally accessible official bytes for H-MAGDEPTH; otherwise select a genuinely new cache-only lane, preregister it, and test at deployment density versus a matched random control. Apply canaries and surface novelty before placement. No score estimate or submission slot is authorized.
