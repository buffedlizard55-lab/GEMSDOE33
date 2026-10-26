# Repository review — 2026-10-26 (post-restore, three-pass audit)

## Executive decision

- **No new experiment or TIFF was generated. No submission slot was used.** The prompt's parallel-run rule requires one assigned geological method lane, but the current request does not name a specific paragraph/lane. Choosing an idea from the slate here would silently select a method; no candidate was run on that basis.
- **No file is OK TO SUBMIT.** The automated selector was run against the restored template and current run cards; it returned `NO RASTER IS OK TO SUBMIT` (0 eligible of 11). Historical focus-site maxima remain owner-reported, not organizer-confirmed. The highest supplied focus-site score is GEMSDOE32 B2 at `0.2778` (USER/OWNER-REPORTED); this does not establish score attribution, causal mechanism, or a prospective score.
- Existing research TIFFs remain available in `docs/downloads/`, but their scientifically negative, duplicate, or unmeasured verdicts stand. The A33-R3-LLC file is independently revalidated below as format-clean against the restored owner-mirror template, **but is not cleared for submission** because the frozen confirmation did not beat the in-project incumbent.

## Pass 1 — repository and prompt review

Read `README.md`, `standing_prompt.md`, `AGENTS.md`, the latest Round-4 feasibility evidence, the candidate slate, selector, evaluator, writer, validator, static-site builder, current focus-site table, and source/irregularity registries. The README already contains the nine-site executive comparison and explains why the reported GEMSDOE32 B2 result is a pruning-family artifact rather than a novel independent surface. Its score and the conflicting `0.3195` / `0.4413` claims are not organizer-confirmed.

The existing untried hypothesis slate is in `knowledge/11_new_hypotheses_20261026.md`; the Round-4 availability slate is in `knowledge/18_round4_feasibility_audit_20261026.md` and `evidence/round4_input_feasibility_20261026.json`. Its five candidates, in feasibility-audit ranking, are:

| Rank | Candidate | Main layers/signature | Why relevant to omitted faults | Status / mimic / cost |
|---|---|---|---|---|
| 1 | COULOMB stress transfer | Quaternary fault geometry, slip/dip/sense; elastic ΔCFS lobes | Synthetic/antithetic splays may be stressed away from mapped traces | Blocked: CSV has no vertices/strike; companion vector mirror has no declared CRS and stored coordinate ranges do not overlap the template. Intrusive/caldera margins or friction heterogeneity can mimic. Moderate if geometry is recovered. |
| 2 | CURVTRACE | Raw 1 m USGS 3DEP DEM; multi-azimuth curvature and orientation-tracked scarp continuity | Trace-scale relief could reveal subtle structures unresolved by 100 m summaries | Blocked: raw 1 m tiles were not restored; official 3DEP is the named source, but raw payload/coverage was not obtained in this workspace. Shoreline benches, terrace risers, roads and canals mimic. High cost. |
| 3 | PFRT | Cached basement-depth, gravity horizontal-gradient and directional updip projection | Basinward flexure may express a concealed basement offset without a mapped surface trace | Cache-only feasible, not tested. Coalescent fan toes and buried pediments mimic; medium cost and high duplicate risk. |
| 4 | HMDT | Conductivity, upward-continued TMI, gravity gradient and dilatation; signed cross-gradient doublet | Alteration contrasts could flag concealed structures | Not genuinely untried: an old TIFF exists, but no reproducible fold-safe runner/card was retained. Saline playa or nonmagnetic lacustrine tuff mimic. Low–medium cost. |
| 5 | PALEOTEMP | DOE GDR #1391 temperature probes/paleosinter plus cached conductivity/geophysical edges | Relict hydrothermal conduits could mark buried faults absent from active-vent inventories | Blocked: required specific probe/sinter payload absent. The official GDR listing is named in the registry; payload/schema/coverage were not fetched in this review. Paleochannel thermal outflow mimics. Medium cost. |

These are qualitative priorities, **not numerical score predictions**. The feasibility report already checks COULOMB's local files and documents the geometry blocker. Because the highest-ranked ideas are blocked and no method lane was assigned, no holdout result is asserted. PFRT is the first locally runnable untested candidate only if explicitly chosen and preregistered later; it must first pass standalone feature canaries, the pre-placement duplicate screen, and the shared hide-and-recover evaluator. H-N1 from the other slate was already tested negative; H-N2 shares fixed H19-5 catalogue-derived input and cannot be trusted as fold-safe unless re-derived using visible faults only.

## Pass 2 — restore, data integrity and adversarial checks

Restored all 17 registered inputs into git-ignored `data/` with `scripts/restore_data.py --group all`. Each fetched object matched both its registered size and SHA-256. **These are owner-maintained GitHub mirrors, not organizer-authenticated downloads**; matching pins prove byte equality to those mirrors only. No DrivenData login, upload or leaderboard polling was used.

Ran `scripts/audit_inputs.py`: 17/17 pins matched; owner-mirror sample template is EPSG:32611, 3,292 × 3,730, 100 m; 5,167,373 finite cells. Re-ran `scripts/audit_sample_template_values.py` against explicit flat `data/sample_submission.tif` and `data/labels.tif` paths: on the finite footprint sample values equal the label raster exactly (60,988 ones and 5,106,385 zeros). Consequently the template is used only for grid/finite-mask metadata and **never as labels or absence truth**.

Ran `scripts/prepare_data.py --skip-detector`. It rebuilt 121 feature channels and the research cache; no detector fit was performed. This preparer does not yield an evaluated submission. The new cache and restored data remain git-ignored and are not part of the GitHub Pages download.

Adversarial path check found that the template-value audit script's default path used the legacy `gems33.grid` nested `core/` layout, whereas the current pinned restore flow writes flat files in `data/`. The no-argument audit therefore failed before the repair. Its default now uses the current shared `gemsdoe33.paths.DATA` location, and `scripts/run_checks.sh` now runs the pin/template audits when restored data exist rather than always printing that they were skipped. Legacy scripts that still hard-code `data_dir()/core/...` remain historical; they should not be treated as current campaign entry points without a compatibility-path review. The holdout evaluator's array-level helpers were not forked or modified.

Reopened every root-level TIFF in `docs/downloads/`: all 20 are single-band `float32`, shape 3,730 × 3,292, EPSG:32611, with finite values in `[0,1]`; NaN-outside variants have NaNs only outside the finite template footprint, and zero-outside variants are all finite. This scan is a structural audit, not uniqueness/scientific promotion evidence. The A33-R3-LLC zero-outside TIFF SHA-256 is `76f9e157d01bb9bec2d98c3c5941b6114e06e0f439272d5f140af6e3584c8825`; the strict local validator against the restored template passed. Its run-card verdict remains negative.

## Pass 3 — tests, selector, site and final cross-check

- `.venv/bin/python -m pytest -q`: **150 passed** after inputs were restored (no skips).
- `PYTHON=.venv/bin/python bash scripts/run_checks.sh`: static-site build, tests, input pin audit, template/label diagnostic, selector, compile and diff checks passed. The selector reported **0 eligible of 11 run cards**.
- `scripts/select_submission.py --date 20261026`: **NO RASTER IS OK TO SUBMIT**. Existing scientific verdicts remain negative/duplicate/unmeasured; passing a format check does not override them.
- `scripts/validate_submission.py` on the A33-R3-LLC research TIFF against `data/sample_submission.tif --strict-zero-outside`: `pass: true`, one float32 band, EPSG:32611, exact shape and transform, no NaN, min 0, max 1, zero outside. No portal acceptance is inferred.
- Rebuilt all generated site pages after replacing two stale "data absent" notices with the current mirror-restored/cache-present-but-not-published status. Reviewed the updated top-level copy for clarity: it names the owner-mirror provenance limit, no-lane decision, and 0-eligible selector outcome.
- `git diff --check`: pass.

## Nine-site executive decision

The README and `docs/executive-summary.html` already list GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36, the reported filenames/scores, duplicate-family evidence, and a step-by-step future submission workflow. The best **reported** focus-site candidate is GEMSDOE32 B2 (`0.2778` USER/OWNER-REPORTED, NOT ORGANIZER-CONFIRMED). Local forensic evidence says B2 is deletion-only pruning of the GEMSDOE28 H27-4 family. This explains why that family could reduce false-positive cost under the local DTI proxy; it does **not** prove why a competition score occurred or support copying/re-emitting it. No new artifact in this checkout has demonstrated a higher competition score. A local holdout is a mapped-catalogue proxy and is not an estimate of private-label contest performance.

## Current lane / next work

1. Assign exactly one new method paragraph/lane and freeze it before implementation. Do not infer the lane from the broad request or reuse a completed negative arm.
2. Prefer a genuinely untried, locally available idea only after a standalone per-feature holdout leakage canary and pre-placement uniqueness screen. PFRT is a feasible candidate from the stored slate, not a selected or validated result.
3. Use the shared cache, `evaluate_holdout.py`, and `submission_writer.py`; derive catalogue-based features only from fold-visible faults; use whole-segment buffered hide-and-recover, exact visible-fault masking, pooled DTI and the preregistered 95% CI. Respect the 3-experiment / 2-hour cap and stop on either duplicate threshold.
4. Keep slots unused unless an independent confirmation beats the matched incumbent, all canaries and both uniqueness stages pass, strict saved-byte validation passes, and the automated selector promotes the exact TIFF. No score projection is justified.
5. Resolve the official-source authentication/licensing/payload issues for the 17 owner mirrors and obtain organizer clarification on the sample/label overlap and outside-footprint TIFF semantics. Do not claim the earlier `[0,1]` portal error's root cause.

## Review run card (no candidate run)

```json
{
  "hypothesis": "No new hypothesis was selected or evaluated: the request supplies no single assigned method lane. The top Round-4 COULOMB candidate remains blocked by unusable local geometry.",
  "mechanism": "Repository/data review only. Restored and hash-checked 17 owner-mirror inputs, rebuilt the shared 121-channel cache, audited all local download TIFF structures, ran the existing automated tests and selector. No candidate surface or final dot set was created.",
  "named_non_fault_process_that_could_mimic_it": "For the feasible reserve PFRT mechanism, coalescent fan toes and buried pediments are plausible non-fault mimics; PFRT was not run.",
  "holdout_dti": null,
  "holdout_dti_evaluator_version": "not run; shared evaluator is GEMSDOE33-HIDE-AND-RECOVER-v1.0",
  "withheld_positives": null,
  "holdout_ci95": null,
  "reason_unmeasured": "No candidate/lane selected; no performance score or projection is reported.",
  "correlation_overlap_vs_registry": null,
  "correlation_overlap_reason": "No new surface or final dots were created.",
  "raster_sha256": null,
  "validator_output": "No new submission raster. Separately, the pre-existing A33-R3-LLC research TIFF passes local strict-zero-outside checks against the restored owner-mirror template; its scientific verdict is negative and it is not slot-approved.",
  "submission_name": null,
  "submission_note": null,
  "verdict": "negative"
}
```
