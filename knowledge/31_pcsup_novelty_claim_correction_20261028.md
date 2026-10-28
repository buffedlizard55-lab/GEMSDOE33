# Repository review: PCSUP pre-placement novelty claim correction (2026-10-28)

## Finding

The A33-R7-PCSUP uniqueness evidence was inconsistent with the executive summary and overview page. The machine-readable record `evidence/a33_r7_pcsup_uniqueness_20261028.json` declares `surface.passed: false`; the surface's maximum fraction of sampled candidate pixels within 3 px of a registry raster is `0.8608381579646253` (86.0838%), above the recorded stop threshold `overlap_stop_gt: 0.7`. The maximum absolute Spearman rho is only `0.100959`, but passing the correlation criterion does not negate the failed overlap criterion. The final-dot record passes (max overlap 58.2753%); it cannot cure a required pre-placement surface failure.

The previous executive table and public overview described surface and dots as passing / called the artifact unique. Those statements were wrong. The correction now labels the TIFF as a research artifact, explicitly reports that the surface gate failed, preserves the final-dot result as a separate fact, and says it is **not OK to submit**. The TIFF was not regenerated; this review uses the existing evidence and does not spend an experiment or submission slot.

## Changes

- Corrected the A33-R7 PCSUP summary and JSON run-card description in `knowledge/30_phcong_results_20261028.md`.
- Corrected the primary README status and public overview in `scripts/build_site.py` / `docs/index.html`.
- Added a regression test requiring the saved uniqueness JSON to report a failed surface gate and the rendered page to show the warning without calling PCSUP unique.

## Verification

- Rebuilt the static pages using `python scripts/build_site.py`.
- `python -m compileall -q scripts src tests`: passed.
- `.venv/bin/python -m pytest -q`: **173 passed, 12 skipped** after adding the regression test. (A prior run before the new test was 172 passed, 12 skipped.)
- Independent JSON check confirms `surface.passed == false`, overlap 0.860838 > 0.7. Local format validity does not grant uniqueness or organizer acceptance.

## Scope and remaining risk

The recorded uniqueness audit covers 21 pinned rasters only; it cannot establish global uniqueness against every other submission worldwide. The owner-mirror registry provenance is not organizer-authenticated. No valid candidate is slot-approved, and the A33-R7 experiment budget is already exhausted. A future run requires a fresh session/preregistration, a clearly specified single method lane, pre-placement novelty pass before any emission, deployment-matched holdout density, per-feature canaries, and a new independent confirmation. No leaderboard score is estimated from catalogue HOLDOUT-DTI.
