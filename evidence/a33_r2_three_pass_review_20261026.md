# Three-Pass Release Review & Reconciliation (`A33-R2-CSHT`, 2026-10-26)

## Pass 1 — Implementation & Verification
1. **Repository & 9-Site Forensic Audit:** Audited all 12 canonical focus rasters (`registry/focus_rasters_20261025.json`), all 5 newly user-reported 2026-10-25 focus rasters (`G24-gvc1`, `G25-h66`, `G27-h29`, `G28-s18`, `G30-MSDB1`), and all 4 local `GEMSDOE33` rasters into the 21-raster SHA-256-pinned manifest `registry/focus_rasters_20261026.json` (`SHA-256: 6e71453c77dd4b2bbb5f1d7e36db74f6641f9a47f6ecfb87b099db21ea8f1500`).
2. **Shared Feature-Stack Fix (`IR-33-LIDAR-VOID-01`):** Fixed `src/gemsdoe33/features.py` so `lid_valid == 0` (`1,272,913` in-footprint 3DEP LiDAR void cells, `24.63%`) preserves exact `0.0` and `lid_*` preserve `np.nan` instead of Voronoi-extrapolating `260,733` phantom scarps across `NE_LidarGapHeavy`.
3. **Preregistration Before Implementation:** Formulated and SHA-256-froze 5 untried geological hypotheses (`knowledge/12_preregistered_a33_r2_hypotheses_20261026.md`, `evidence/a33_r2_preregistration_20261026.json`, `SHA-256: f6144c2b6e0cd5bddb0966d9321697be3bb5a070808559a94f38eddcd2a70268`).
4. **One-Shot Execution:** Ran `scripts/evaluate_holdout.py --run-a33-r2` (`A33-R2-CSHT`):
   - `50 / 50` feature leakage canaries passed (`max fold two-sided AUC = 0.7685 <= 0.90`).
   - Primary screen (`quadrant-buffered-15px-v1`): `HOLDOUT-DTI = 0.136716` vs `B1_regional = 0.112418` (`0.113244` recorded), paired $\Delta = +0.024298$ `[+0.012427, +0.035833]`, **`4 / 4` fold wins**.
   - Frozen orthogonal confirmation (`diagonal-wedge-buffered-20px-confirm-v1`): `HOLDOUT-DTI = 0.131169` vs `B1_regional = 0.115122`, paired $\Delta = +0.016047$ `[+0.003817, +0.028030]`, **`4 / 4` fold wins**.
   - Emitted `gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif` (`.zip` & `-nan.tif` twin) via shared `scripts/submission_writer.py`, verified `pass = True` via `scripts/validate_submission.py --strict-zero-outside`.

## Pass 2 — Adversarial Review & Fixes
1. **Leakage Audit (`IR-33-CSV-DIST-FAULT-01`):** Verified `gdr_wellspring_in_footprint.csv` and `gdr_volcanic_vents_in_footprint.csv` contain `dist_known_fault_px`; hard-blocked that column in `src/gemsdoe33/csht_transfer.py` and locked with regression test `test_csv_loader_ignores_forbidden_dist_known_fault_px_column`.
2. **Border Wrap & Self-Spacing Audit:** Verified 3-px border padding in `celf_emit_300m` prevents flat-stride wrap across image columns and enforces pairwise spacing strictly `> 2.5 px` (`test_celf_emit_300m_enforces_spacing_and_no_border_wrap`).
3. **Uniqueness & Gate Denominator Integrity (`IR-33-SPEARMAN-SPARSE-CEILING-01` & `IR-33-A33-R2-20261026`):**
   - Proved mathematically that continuous-vs-binary Spearman rank correlation at `0.73%–0.85%` dot prevalence is bounded above by $\sqrt{3p(1-p)} \approx 0.148\text{–}0.159$.
   - Verified `final_dots` (`37,654` `CELF-300m` dots) passed `21 / 21` registry rasters (`max |Spearman| = 0.0416`, `max 3-px overlap = 0.6934 <= 0.70` vs `G30-MSDB1`, `0.3586` vs `G32-B2`).
   - Verified pre-placement continuous surface peaks exceeded `70%` 3-px overlap (`91.11%` unthinned / `77.82%` matched-37k 1-px NMS crests) against 2026-10-25 sibling HGB `G30-MSDB1` (user-reported `0.1462`); refused to dilute the gate denominator (`NMS >= 0.80` `101,799` pixels would have masked `0.778` down to `0.607`), preserving the fail-closed `verdict = "duplicate"` (`ok_to_download = True`, `ok_to_submit = False`).
4. **Frozen Historical Evidence Restoration:** Restored `evidence/focus_raster_audit_20261025.json` and `evidence/input_grid_audit.json` so all `2026-10-25` artifacts remain byte-identical, fixed relative-path handling in `audit_uniqueness_against_manifest`, eliminated `rasterio.transform.from_origin` deprecation warning, and stripped trailing whitespace across Markdown files.

## Pass 3 — Final Reconciliation Against Prompt & Standing Contract
- **Unique `.tif` & `.zip` generated (`[0, 1]`, `EPSG:32611`, `3730×3292`, `<= 140`-char note):** Verified on disk (`SHA-256: 14ab452c22aaf07444cd02e589fce4627d682e99f44c63e78dc1383955e0c602`).
- **Obvious Download vs Submit Verdict:** Top of `README.md`, `docs/index.html`, and `docs/how-to-submit.html` (`docs/executive-summary.html`) display `OK TO DOWNLOAD: YES` and `OK TO SUBMIT: NO — DO NOT SPEND A WEEKLY SLOT`.
- **9-Site Executive Summary & `GEMSDOE32` `0.2778` Analysis:** Published in `README.md`, `docs/results.html`, and `knowledge/13_focus_forensics_g32_proof_and_a33_r2_results_20261026.md`, with all historical values labeled `USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)` and all local metrics labeled `HOLDOUT-DTI`.
- **Automated Checks (`scripts/run_checks.sh`):** Site build, `126` unit/regression tests (`0` warnings), all local HTML link checks, recorded `A33-L1` & `A33-R2` verifiers, and `git diff --check` pass cleanly.
