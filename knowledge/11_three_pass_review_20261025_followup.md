# 2026-10-25 follow-up: three-pass implementation, adversarial, and acceptance review

## Decision at close

**No new candidate was implemented or evaluated; no new TIFF was generated; no submission is okay to download for competition use or submit.** The preflight stopped before experiment because the prompt does not identify its required single-method lane, core competition rasters/cache and registry TIFFs are absent, and the available legacy holdout routine does not rebuild source/candidate features by fold. H33-6 remains research-only and fails both its conditional proxy gate and the local duplicate guard. No weekly slot was spent.

The user-provided H33-2 B2 `0.2778` and the reported `0.2708`, `0.3195`, and `0.4413` values are not organizer-confirmed in this checkout. The two alleged current-high values conflict. No leaderboard scrape, poll, or refresh was performed. The owner-site summary across GEMSDOE24/25/27/28/30/31/32/33/36 remains a review of retained/user-provided material, not independent receipt verification or proof of the remote raster bytes.

## Pass 1 — implement and verify

- Frozen three repository-distinct, unimplemented candidates before any candidate code: H33-11 paired signed vertical-gradient zero crossings, H33-12 matched-window potential-field texture offset, and H33-13 lithology-contact control. Layers, signatures, omitted-catalogue rationale, non-fault mimics, prior-art distinctions, qualitative priority/cost, and data/source gates are recorded in `knowledge/10_hypothesis_slate_20261025.md` and `evidence/hypothesis_slate_20261025.json`. No numeric DTI projections were invented. H33-13 is blocked: the SGMC 2026 DOI is identified from repository notes, but payload availability, schema, CRS, licensing, semantics, and coverage are unaudited.
- Created `evidence/preflight_run_card_20261025.json` with a negative verdict, named mimic, null raster hash/metrics, unavailable duplicate checks, no submission name/note, and an explicit NOT-RUN holdout/validator status. This records a blocked preflight, not a completed geological experiment.
- Hardened the shared `src/gemsdoe33/submission.py` path: fail closed on complex, non-finite, or out-of-range emitted probabilities; validate masks and safe identifiers; cap notes at 140 characters; refuse to overwrite existing package outputs; enforce outside values as NaN/null or zero; and distinguish footprint requirements from whole-array finiteness diagnostics.
- Updated regression tests for allowed NaN-outside diagnostics, rejected outside infinity, invalid/complex predictions, empty footprints, filename/note limits, no output overwrite, and the synthetic NaN-outside package case.
- Updated `README.md`, `standing_prompt.md`, site source, generated pages, and irregularity records. The H33-6 TIFF is explicitly **NOT OK TO SUBMIT** and is linked only for inspection; the previous “unique” wording and historical D2.8 download recommendation are withdrawn. The score-conflict caveat and fresh slate are visible on the site.
- Changed CI push matching from one stale Arena branch name to `arena/**`, so the session branch can run the same checks as `main`.

## Pass 2 — adversarial review and fixes

- Reproduced the earlier “all checks fail” symptom with a synthetic official-sized grid. For the NaN-outside variant, the only false whole-array fields were `whole_array_finite` and `whole_array_finite_and_in_range_0_1`; footprint finiteness/range, outside-mask policy, grid, dtype and band checks passed. The validator now keeps these whole-array fields as diagnostics while preserving hard failures for any invalid footprint value or invalid outside value. The synthetic package test confirms NaN-outside can pass local footprint policy while still visibly reporting `whole_array_finite == false`.
- Checked the separate `scripts/validate_submission.py` path: its `pass` decision uses footprint range/finiteness and the NaN-or-zero outside policy; it reports whole-array finiteness/range separately and rejects outside infinity. This does not identify the historical organizer portal error's cause.
- Exercised fail-closed cases for NaN, positive/negative infinity, values outside `[0,1]`, complex values, empty footprints, unsafe names, long notes and attempts to overwrite an existing package. No test created an output in its rejected case.
- Re-read active README, standing prompt, generated site text, hypothesis slates and registry irregularities for stale assertions. Corrected old use of “unique” for H33-6/H33-F, the prior D2.8 “recommended download” language, and stale upload prompts; preserved the older material as historical context with an explicit later duplicate-stop qualification.
- Verified the duplicate and lane gates remain fail-closed: H33-6 final dots triggered against 7/9 local same-grid TIFFs; external registry rasters and the pre-placement feature surface remain unavailable. No placement or new duplicate screen was attempted for H33-11.
- Did not fetch an external source in this follow-up. The SGMC candidate remains not viable until an official payload and its license/schema/coverage are verified. The absence of access/data is recorded rather than guessed around.

## Pass 3 — final acceptance review

- `PYTHON=.venv/bin/python bash scripts/run_checks.sh`: **81 passed**. The site builder regenerated the static pages. The optional input-pin audit reported it needs local `data/` files, which are absent.
- `git diff --check`: passed.
- `.venv/bin/python -m compileall -q src scripts tests`: passed.
- JSON parsing passed for `registry/irregularities.json`, `evidence/hypothesis_slate_20261025.json`, and `evidence/preflight_run_card_20261025.json`.
- Generated overview, executive summary, results, hypotheses, research, irregularities, and standing-prompt pages were inspected. Current pages identify all scores as reports without receipts, identify the `0.4413`/`0.3195` conflict, show three blocked hypotheses, and state plainly that no TIFF is upload-cleared.
- Saved-byte and duplicate evidence in `evidence/saved_bytes_audit_20261025.json` and `evidence/duplicate_guard_run_card_20261025.json` was not re-created: the task did not generate a new raster. No new score, organizer receipt, slot selection or upload exists.

## Remaining blockers

1. One explicit method lane is missing from the task; do not guess it.
2. Official core training/labels/sample rasters and shared feature cache are absent from this checkout.
3. The available proxy evaluator scores prebuilt arrays and cannot construct fold-specific candidate/source features; a protocol-compliant whole-fault buffered evaluator is not present.
4. External GEMSDOE registry TIFF bytes are not staged, so no cross-site duplicate clearance can be given.
5. User/owner score claims lack byte-identifiable organizer receipts; `0.4413` and `0.3195` conflict.
6. No candidate, including H33-6, has passed feature-alone leakage canaries and independent fold-safe confirmation.

## Pull request / merge status

Pending final branch publication and repository-protection check. Merge only if the current branch’s checks and protections permit it; no alternate branch or direct `main` push is authorized.
