# Data restore, feature preparation, and candidate audit — 2026-10-26

## What was actually done

The current checkout did not contain `data/` rasters or a `.cache/` feature stack. I restored the 17 entries in `registry/owner_mirror_input_pins.json` through the repository's GitHub API restore script into the ignored path `.cache/gemsdata/`. Every restored file matched the manifest's byte count and SHA-256. This proves identity with the registered owner mirrors only; it does **not** authenticate a DrivenData download or third-party licence. The small provenance and checksums are summarized in `evidence/prepare_data_audit_20261026.json`; the full grid/input check is `evidence/input_grid_audit.json`.

The preparation script successfully built/reused the cached 121-channel research feature stack and documented-site density. The template footprint is 5,167,373 cells. `sample_submission.tif` on the owner mirror still has the same positive mask as `labels.tif`, so the known warning remains: it is safe here for grid/footprint metadata only, not a target label.

## Defect found and fixed

The first unmodified default invocation built all feature channels, then failed at stage 4 with:

```text
AttributeError: module 'gemsdoe33.detector' has no attribute 'fit_predict_oof'
```

`src/gemsdoe33/detector.py` has no generic quadrant OOF implementation. Moreover, quadrant-only OOF is not a substitute for the required whole-fault-segment holdout with buffer. `scripts/prepare_data.py` now defaults to preparing the shared bands/features and explicitly skips that legacy OOF step. If a caller explicitly requests `--train-detector`, the script fails closed with a clear explanation if no implementation exists. This avoids creating a misleading or protocol-incompatible score surface. No private evaluator was added.

A subsequent default run completed from cache in under 2 seconds. **This was not model training and did not run a new holdout experiment.** The active experiment budget had already been consumed by the recorded campaigns, and the current prompt did not identify a new, unambiguous lane paragraph. No slot was used and no upload was made.

Adversarial review also found that `scripts/select_submission.py` hardcoded the template path as repository `data/`, even when `GEMS_DATA_DIR` pointed to the supported cache path. That made the selector skip format auditing. It now resolves the template from the same `DATA` setting as the validator. The regression suite exercises the cache path; rerunning the selector reports no eligible TIFF, with the extant R3/DPPS files passing saved-byte format, SHA and ZIP checks and remaining blocked by their recorded negative science gates. See `IR-33-SELECTOR-TEMPLATE-01`.

## Current candidate safety check

The three downloaded research artifacts named in the evidence card were re-opened with `scripts/validate_submission.py --strict-zero-outside`, against the hash-pinned owner-mirror sample grid. Each passed local format checks: one float32 band, EPSG:32611, 3730 × 3292, exact matching transform/bounds, finite values in [0,1] over the full array, zero outside the footprint. This is a format result only, not scientific promotion or organizer acceptance. Their holdout cards remain negative, so all are **OK TO DOWNLOAD FOR RESEARCH / NOT OK TO SUBMIT**.

## Next steps

1. Use the existing five-hypothesis Round-4 slate in `knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md` as proposal only; do not silently treat it as a new lane authorization.
2. Before any new experiment, explicitly reconcile the required lane, shared-template/evaluator path and remaining budget. If the lane is clarified, prioritize only a preregistered candidate and use the existing fold-safe holdout, canary, matched controls, surface/final uniqueness checks and validator.
3. Keep the current negative TIFs available as research artifacts, not recommendations. No locally defensible leaderboard score estimate exists: the catalogue hide-and-recover proxy has not been calibrated to the private competition labels.
4. Do not run leaderboard polling. Organizer confirmation requires an authorized submission page receipt, unavailable in this workspace.
