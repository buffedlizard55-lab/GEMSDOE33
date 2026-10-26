# Focus-site forensics, automatic gates and negative preflight — 2026-10-25

## Executive decision

**No new TIFF; NOT OK TO SUBMIT.** The unique, scientifically validated submission goal is not complete. No new geological experiment, competition-slot selection or upload was performed. Do not rename a reference or failed raster to manufacture compliance. This is a negative preflight plus a reproducible prior-art audit and validation-system repair.

All 17 registered owner-mirror inputs were restored and hash-audited, and the existing preparer built 121 channels. Therefore “data placement is the single remaining blocker” is no longer an accurate diagnosis. Independent analog labels, an explicit current lane and canonical shared-template identity, leakage-safe validation, a comparable holdout best, and an independent confirmation are still missing. The feature cache is not trusted model evidence merely because it exists.

## 1. What was actually reviewed

The requested nine projects were inspected through GitHub, not by polling their Pages sites or DrivenData. The API snapshots were pinned to immutable refs. Source inventory: [`evidence/source_review_20261025.json`](../evidence/source_review_20261025.json). Raster inventory: [`registry/focus_rasters_20261025.json`](../registry/focus_rasters_20261025.json). All large downloads and derived arrays remain under ignored `data/` and `.cache/`.

The source classes must not be conflated:

| Evidence | Authority | What it establishes / does not establish |
|---|---|---|
| [Organizer reference README](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md) and notebook | Organizer-maintained GitHub source, retrieved this session | CPU and GPU workflows exist. The notebook's training uses Tversky-loss weights; it is not a submission-page receipt or independent verification of a local DTI result. |
| [GEMSDOE32 round-4 builder](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/5786b21a1674b26ee525e8e9bf048e2e0f50fc0e/scripts/run_h33_validation.py) | Owner code, retrieved this session | Describes B2 deletion from the H27-4 reference; the source comments' “live-scored” labels and score projections are not authenticated organizer results. |
| [GEMSDOE32 B2 audit](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/5786b21a1674b26ee525e8e9bf048e2e0f50fc0e/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-audit.json) | Owner-generated record | Records a file hash/format and a pruning description, but its aggregate/fold metrics are inconsistent and its projected score is not evidence of organizer performance. |
| [GEMSDOE36 pipeline](https://github.com/buffedlizard55-lab/GEMSDOE36/blob/c9ad59ec6f969ed931d089a03044c1567a633e84/scripts/run_pipeline.py) | Owner code, retrieved this session | Describes fixed heuristic priorities, augmentation of a B2 base, and a live-anchor projection. A “PINN” filename or comment does not prove neural PDE training, fault permeability or vent discovery. No such scientific claim is made here. |
| [Current input audit](../evidence/input_grid_audit.json) | Measurements of local owner mirrors | All 17 pins match. This authenticates the registered mirror bytes, not official origin, licensing or label independence. |
| [Twelve-raster forensic audit](../evidence/focus_raster_audit_20261025.json) | Local measurements, not HOLDOUT-DTI | Grid/range, binary prediction identity, rank correlation and directional Euclidean dot overlap. Not scientific improvement or a score. |
| User's named submission scores | Unverified user/owner reports | Leads for prior-art research only. No ORGANIZER-CONFIRMED score, current leader or exact score-to-file association is established. |

Primary competition links for manual review remain [problem/format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [rules PDF supplied in the request](https://docs.nlr.gov/docs/fy26osti/96647.pdf), and [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). These hosts are outside this session's outbound allowlist; no fresh verification is asserted. The repo's standing no-scraping/no-upload policy also remains in effect. The request supplies conflicting current-high values; neither was adopted as verified.

## 2. Why the reported GEMSDOE32 high scorer might have worked

### Construction is now verified from bytes

Read both pinned owner rasters on the restored template footprint, then compute:

```text
expected_B2 = H27_4_dots AND (Euclidean_distance_to_full_catalogue > 2 pixels)
```

Result: **pixel-exact match**, zero mismatched cells; reference 40,199 dots; B2 37,654 dots; 2,545 deletions; zero additions. No new prediction was written. The literal SHA-256 of the B2 zero-outside file is `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9` and matches the owner audit.

This is an emission-domain restriction on an existing detector, **not** a new geological discovery mechanism. The former review's statement that these remote bytes were unavailable was true then but is superseded by this session's successful retrieval. The score receipt is still absent.

### Metric reasoning: inference, not organizer-score causation

For the repo's local recorded DTI definition, let `T = TPw`, `F = FPw`, `N = withheld positive pixels`, and `S = T / (0.2T + 0.2F + 0.8N + epsilon)`. When deleting predictions, let `t` be the lost true-positive credit and `f` the removed false-positive mass. With the same truth/domain, deletion improves the metric precisely when:

```text
0.2 * T * f > t * (denominator - 0.2 * T)
```

For `f > 0`, this is `t/f < 0.2*S / (1 - 0.2*S)`. This is an algebraic statement, not a score projection. The epsilon is included in `denominator`.

Because truth credit is a maximum over nearby predictions, a dot can be redundant for recovery yet still cost false-positive mass. Pruning near mapped faults might preferentially remove such low-value mass **if** the private missing-fault set gives it little credit. Conversely, it can delete valuable predictions near unmapped parallel splays, segmented fault continuations or imperfect catalogue registration. Only an appropriately hidden/independent truth set can distinguish these cases. The submitted score list alone cannot.

Consequently, the construction is explained, but **why the user-reported organizer result occurred and whether a new method can beat it are not established**. No numeric improvement forecast is justified. Directly optimizing a score-calibrated “live mirror” is not a substitute for the requested buffered hide-and-recover test.

### Source irregularity

The B2 audit lists the same four quadrant values for two differently named instruments, while their recorded aggregate means differ both from one another and from the arithmetic mean of those quadrant values. The accompanying note includes an unverified projection and `UNSCORED`, while another field says `SLOT_ELIGIBLE`. These fields are not a coherent, independent promotion receipt; no score from them was adopted as HOLDOUT-DTI.

## 3. Nine-site comparison and duplicate implications

[`scripts/audit_focus_rasters.py`](../scripts/audit_focus_rasters.py) fetches only explicitly pinned references when `--fetch` is supplied, validates their exact grid/range against the restored template, and records 132 ordered comparisons across 12 requested reference files. All nine named sites are covered, including the additional named GEMSDOE28 variants. This is a focus subset, not the complete global registry.

For these **binary** rasters, average-tied-rank Spearman equals the binary phi/Pearson coefficient exactly. It is computed from contingency counts on the template footprint, with no sample approximation. Constant rasters have undefined correlation and never pass. The directional overlap is the fraction of candidate dots in the exact Euclidean radius-3-pixel disk around registry dots; the reverse fraction is reported separately, not substituted. This diagnostic is not suitable for silently binarizing a continuous pre-placement score surface.

Measured prior-art facts, **not HOLDOUT-DTI**:

- B2 versus H27-4: rank correlation `0.9675873339320898`; candidate overlap `1.0`.
- GEMSDOE25 D2.8 and GEMSDOE30's named Poisson reference have identical binary predictions (44,090 dots); neither is an independent discovery result.
- GEMSDOE28 H27-4 and the exact requested GEMSDOE31 solo reference have identical binary predictions (40,199 dots).
- B2 versus GEMSDOE36's named lead: rank correlation `0.9843213108529583`; B2's candidate overlap `1.0`.

Using a B2-derived edit as a “new lane” would therefore fail the user's stop rule. No such model or placement was built. We did not reconstruct a new continuous surface from a binary reference. There is no new candidate whose full-registry uniqueness has been established.

During the adversarial pass, an ambiguous short-hash lookup was found to select GEMSDOE31's *add-arm* instead of its requested *solo* raster. It was corrected to the exact full filename before finalizing the pinned manifest and rerunning the entire audit. This demonstrates why names, hashes and decoded predictions all matter; a common short suffix is not enough.

## 4. Ranked scientific ideas, before implementing any new method

Four new **planning** hypotheses within the README's historical analog-transfer scope are fully specified in [`registry/analog_hypotheses_20261025.json`](../registry/analog_hypotheses_20261025.json) and rendered on the site's latest-review page:

1. **AT1 — cover-stratified, field-held-out magnetic/gravity edge-normal transfer.** Highest conditional priority, medium-high cost. Independent dense field traces, not the same public catalogue inside field masks, are the essential change.
2. **AT2 — structure-conditioned radiometric alteration residual transfer.** Medium conditional priority, medium-high cost; must distinguish hydrothermal structural alteration from alluvial provenance/lithology.
3. **AT3 — independent-field contrastive cross-section motif transfer.** Medium-to-low priority, high cost; oriented multi-layer profile shapes, not pointwise raw fields or a fixed edge product.
4. **AT4 — resolution-degraded analog motifs that survive topographic-evidence removal.** Low direct upside, high cost; a prespecified falsification test for buried-structure transfer, not a score-seeking ensemble.

Each record names exact predictors, the physical signature, missing-fault rationale, local prior-art difference, non-fault mimic, cost, and official external source. Rankings are qualitative judgments, not measured DTI improvements or global novelty claims.

**None is viable now.** Official independent field-label payloads are required from [DOE GDR 1682](https://gdr.openei.org/submissions/1682) and/or [DOE GDR 207](https://gdr.openei.org/submissions/207). Official GDR/USGS binary hosts are outside the allowed outbound hosts, so current obtainability, licence, geometry/schema and independence cannot be verified here. Historical listings do not clear this requirement. Reusing the regional catalogue as the analog truth would repeat H33-F's failed premise. A domain-classifier AUC is not a Ben-David target-error bound, and unknown joint-label error remains unknown.

The current request does not identify a new single assigned method paragraph or canonical shared-template repo/commit. The historical README analog paragraph is retained only as planning scope. No new lane was selected. The same-named `evaluate_holdout.py`/`submission_writer.py` scripts found in GEMSDOE24 and GEMSDOE31 implement different campaigns; copying one arbitrarily would create exactly the private fork the protocol forbids. **No new evaluator was implemented or run.** The new promotion gate is an evidence-completeness checker, not a replacement metric or evaluator.

## 5. What the automatic system now checks

[`src/gemsdoe33/promotion.py`](../src/gemsdoe33/promotion.py), exposed by [`scripts/check_promotion.py`](../scripts/check_promotion.py), fails closed on missing, malformed or unbound evidence. It requires:

- Exact candidate SHA-256, a named lane, hashes identifying shared-template source manifest/features/evaluator/writer, and comparable current holdout-best identity.
- HOLDOUT-DTI evaluator version, withheld-positive count, whole-segment buffering, all catalogue-derived sources visible-only, exact visible-fault mask, pooled DTI under the requested weights/kernel, and positive paired pooled-delta CI.
- Independent confirmation frozen before screening outcomes, with a different split identity and the same candidate/comparator/evaluator.
- Complete feature-by-feature canaries, AUC no greater than the threshold, and no missing features.
- Complete declared registry, pinned identity, pre-placement and final-dot screens, no exceeded threshold, no undefined metric, and no omitted comparisons.
- A fresh saved-byte format check bound to the same candidate hash, note length and experiment/runtime budget.

Even a pass only makes evidence **eligible for a separate selector**; it never chooses a real competition slot. Its `ok_to_submit` remains false by design. The weekly cap cannot be inferred or invented. This is deterministic project inspection, not an instruction for a human scientific inspector. Authentication and any eventual authorized portal upload are separate from project scientific inspection.

**Important limitation:** a schema checker cannot establish that arbitrary supplied JSON is scientifically truthful. A source-pinned shared evaluator and raw traces are still required. This gate has no demonstrated relationship to private leaderboard performance.

Current machine decision: [`evidence/promotion_gate_20261025.json`](../evidence/promotion_gate_20261025.json), negative, expected CLI exit status 2. The current run card contains null current-holdout/current-raster fields with reasons, rather than repurposing historical scores.

## 6. Format fixes and saved-byte checks

The existing project writer (not a new private writer) was repaired:

- Accept the full aligned 2D array or the exact 1D footprint vector; reject invalid shapes before writing.
- Reject NaN, infinity and out-of-range in-footprint values **before float32 conversion**, rather than rounding/clipping them into apparent compliance.
- Reject non-finite or out-of-range selected weights instead of silently clipping/filling them.
- Reject infinity/nonzero outside; only NaN/null or zero are permitted by the local recorded policy.
- A wrong-shape raster now returns validation failure rather than causing boolean-indexing failure.
- Enforce the requested 140-character note limit before writing.
- Include actual soft values in a weighted package's content ID; the same dots with different probabilities must not reuse an identity.
- Default the validator CLI to the actual restored `data/sample_submission.tif`, not the legacy `.cache/gemsdata/core` layout.

Both **existing** H33-6 variants were reopened against the now-present template; see [`current_research_format_20261025.json`](../evidence/current_research_format_20261025.json) and [`current_research_zero_format_20261025.json`](../evidence/current_research_zero_format_20261025.json). The NaN twin passes footprint policy but is not whole-array finite; the zero twin passes the stricter whole-array finite/range alternative. These measurements do not diagnose the owner's original rejected file or prove portal acceptance. No historical bytes were regenerated.

## 7. Three passes and next-session work

### Pass 1 — implementation and empirical verification

Read repository rules, README and standing brief; restored and audited all 17 inputs; prepared the existing feature cache without training; retrieved pinned primary/owner sources; fetched and measured the exact focus rasters; derived the pruning explanation; specified four blocked hypotheses before model implementation; added automatic evidence gates; repaired writer/validator; updated site and brief. No failed arm rerun and no new experiment.

### Pass 2 — adversarial review

Corrected the ambiguous GEMSDOE31 filename selection and reran the 132-pair audit. Added regression tests for exact tied Spearman, directional Euclidean overlap, constant/soft raster rejection, missing evidence/canaries/registry entries, wrong identity/booleans/NaN/CI estimand, independent-confirmation requirements, budgets, strict pre-rounding range rejection and shape handling. Removed the site's unsupported uniqueness headline and clarified `promote` is not slot clearance. Historical run cards remain immutable context; new current fields explicitly remain unmeasured.

### Pass 3 — original-request reconciliation

The site has first-screen research-download and not-for-submission labels, a latest-audit page with all nine sites and the four hypotheses, automatic failure reasons and downloadable current JSON, plus executive-summary upload instructions. Automated tests, Python compilation, link resolution, site-generation consistency and Git whitespace checks are rerun before the PR. Final test/PR outcomes are recorded separately in `evidence/session_verification_20261025.json`.

**Incomplete requirements are explicit:** no new unique submission TIFF, no fresh top-candidate holdout, no independent official analog data, no canonical shared-template evaluation, no feature canary measurements for these new hypotheses, no full-registry pre-placement/final-candidate audit, no organizer receipt/current leaderboard/weekly-cap verification. None is claimed complete merely because the code/tests pass.

Next steps, in order:

1. Supply/establish the exact lane and canonical template identity through the parallel-run coordinator; do not guess or clone an unrelated evaluator privately.
2. Stage authorized official independent analog-field geometry payloads with licence, CRS, support and catalogue-overlap audit in an environment allowed to reach GDR/USGS. Do not use public catalogue labels twice.
3. Freeze AT1 only after it becomes viable. Keep field-level source/target separation, visible-only features, whole-segment buffered hiding, feature canaries and nuisance/contact controls. Compare with a freshly rebuilt comparable holdout best under the same pinned evaluator.
4. Require pooled paired confidence bounds and independent confirmation, then complete surface/final-dot full-registry checks and strict exact-byte format audit. A negative result ends the arm.
5. Generate a genuinely new TIFF only if the protocol permits continuation; send any promotion to the separate selector. Never derive a numerical private-score forecast from user-reported anchors.

This prioritizes Maximize P(Win) by declining a redundant or unverifiable slot, and Own the Outcome by completing data placement, fixing actual code defects and publishing the remaining blockers rather than disguising them.
