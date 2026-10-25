# GEMSDOE33 standing brief and operating contract

**Read `README.md` first, then read this entire file at the start of every session.** This is the
complete working specification consolidated from the owner's task and explicit standing corrections
recorded for this repository. It is not presented as a verbatim chat transcript. Update it only when
the owner changes the requirements; record any change and its consequence in the repository.

---

## Mission and values

Build an auditable project for the DOE Geothermal Energy from Management of Subsurface Exploration
(GEMS) fault-discovery competition, DrivenData problem 306. The scientific objective is to maximize
the probability of winning by discovering faults that are genuinely missing from USGS / INGENIOUS,
not merely by reproducing the visible catalogue. The operating values are **Maximize P(Win)** and
**Own the Outcome**: pursue the best-supported course, check assumptions, correct errors, and report
negative results honestly.

Work autonomously. Do not ask the owner for manual input. Do not claim access, downloads, scores,
validation, or submission receipts that are not present. A public leaderboard row identifies a
participant and score; it does not identify a TIFF in this repository. Owner-mirror hashes are not
organizer authentication.

## Competition frame and evidence boundary

The owner's brief describes a GeoDAWN / northwestern Great Basin fault-mapping problem in which the
public USGS / INGENIOUS compilation is incomplete and private expert labels concern additional
faults. It also describes weekly submission slots and Initial / Final prize rounds, with experts
potentially reviewing submissions to expand the mapped set. Treat competition mechanics, deadlines,
slot limits, award terms, target-label construction and outside-data rules as claims to verify against
the **current official competition and rules pages** before relying on them; keep the provided rules
PDF labelled as user-provided unless re-downloaded from an official current source. External data may
only be proposed for use when its source, licence and any share-to-sponsor conditions permit it.

## Required deliverables

1. **Inspect the repository and the entire brief before extending the project.** Keep this file and
   the README as the session starting point.
2. Keep the current file status unmistakable at the top of the project site and provide an
   executive-summary page with exact steps for a **future approved** upload. Only link a TIFF as a
   competition recommendation after it passes all scientific, leakage, duplicate, and exact-grid
   gates. The current H33-6 research TIFF triggered a duplicate stop and failed its conditional
   holdout; it is **NOT OK to submit**. A future candidate must be a single-band `float32` GeoTIFF
   on the official training/sample grid, EPSG:32611, 100 m, matching CRS/shape/transform, with
   finite probability values in `[0,1]` inside the footprint and the outside semantics specified by
   current official instructions. Re-open and validate saved bytes; report whole-array finiteness
   separately when NaN outside is used. Give any future promoted file a unique, evidence-backed
   filename/name and paste-ready note of at most 140 characters. State whether a file is a reference,
   owner-reported historical artifact, or a new model. Do not imply local format checks guarantee
   portal acceptance.
3. Review why the reported H27-4 value of `0.2708` was claimed and distinguish official observations,
   local measurements, model-derived values and owner-reported scores. The official leaderboard was
   reviewed once on 2026-10-04 at the owner's request; that observation did not support the brief's
   claim that 0.3195 was then the highest score. DrivenData Terms of Use restrict automatic and
   manual monitoring/copying without prior written consent. Do not scrape, poll, refresh, or reproduce
   leaderboard rows absent written consent or an authorized API; the repository keeps only a dated
   status note, not a leaderboard table. The page cannot establish a score/file pairing.
4. **Before implementing a candidate**, write and rank 3–5 genuinely new geological hypotheses.
   For each include: exact layers; physical signature; why it may detect faults absent from
   USGS/INGENIOUS; distinction from prior repository work; expected-improvement rank (do not invent
   numeric DTI gains) and implementation cost; a specific free official source if new data are
   needed; and an actual availability/licence/schema/coverage check before calling that source
   viable. Record any historical-order violation honestly; a retrospective list is not a
   preregistration.
5. Validate the best candidate on a valid **spatially blocked** holdout before using a weekly
   submission slot. Generate each held-out prediction without access to held-out truth geometry.
   Compare against the current best under a matched evaluation design and budget, and include a
   matched-random control for any operator that changes dot count or spatial selection. No
   unvalidated or unproven candidate may be slot-approved. If the hidden/private target cannot be
   represented by a valid holdout, say so; do not turn a proxy into proof.
6. Apply Ben-David, Blitzer, Crammer, Kulesza, Pereira & Vaughan (2010), *A theory of learning from
   different domains*, responsibly when considering field-to-field label transfer (e.g. Dixie
   Valley, Desert Peak, Brady). Establish named source/target domains, source-label quality, common
   feature layers and sampling, spatial structure, and a suitable shared hypothesis class before
   interpreting a domain discriminator. A formal target-error bound needs source error, empirical
   `HΔH` divergence, a justified finite-sample/class-complexity term, and the joint-label error
   `lambda`; an arbitrary two-sample AUC is not the bound. Treat analog faults as independent
   validation only with spatial/geographic separation and a documented label policy. If source
   data cannot be obtained or assumptions cannot be defended, block transfer rather than fabricate a
   result.
7. Conduct deep, contrarian-but-grounded research into geothermal vent / fault discovery and preserve
   reusable knowledge for future projects. Look for overlooked data sources, but verify their
   official availability, semantics, spatial coverage, licence and permitted sharing before treating
   them as actionable.
8. Preserve research provenance, source links, methods, limitations and irregularities in machine-
   readable evidence/registries and readable project pages. Keep withdrawn/invalid first-pass work
   clearly marked and archived; never reuse its scores as promotion evidence.
9. Run multiple passes: implementation and verification; adversarial review for bugs, leakage,
   assumptions and edge cases; final review against this entire brief. Run relevant tests, regenerate
   derived outputs after schema changes, rebuild the site and inspect generated pages for stale claims.
10. Create a pull request from the session branch, check its status, and merge it to `main` when the
    checks and repository protections allow. Report the PR/merge result and remaining limitations.

## Evidence and provenance rules

- Verify factual claims against official or otherwise trusted primary sources where available; put
  reviewable links beside the claims. Clearly separate `[OFFICIAL]`, `[MEASURED]`, `[MODEL]`, and
  `[OWNER-REPORT]` evidence.
- A SHA-256 match establishes byte identity with the recorded mirror only. It does not establish
  organizer origin, licence, official schema, hidden-label completeness, or score attribution.
- Do not silently fix discrepancies. Record what was observed, what remains unknown and how it affects
  the result in `registry/irregularities.json`.
- Keep prose, generated pages, manifests and evidence records consistent. A JSON value is not
  automatically valid evidence: if its method is invalid, mark it withdrawn and do not promote it.
- Do not rank across artifact families with an evaluation instrument structurally biased between
  them. An operator that drops or repositions pixels needs a matched-random control and a fresh
  validation design.
- A website, local validator, or score estimate must never describe a candidate as winning or
  outperforming unless a valid, independent evaluation supports that statement.
- Follow the DrivenData [Terms of Use](https://www.drivendata.org/termsofuse/): no automated or
  manual monitoring/copying of leaderboard material without prior written consent. Do not introduce
  polling, scraping, scheduled refresh, or a copied leaderboard table. A one-time check does not
  authorize recurring access or public reproduction; use only an authorized API or written consent.
- Include a concise AI/data provenance disclosure and make clear whether any competition upload was
  actually performed. No DrivenData account/session is available in this workspace unless a verified
  receipt is explicitly added.

## Historical project decision (2026-10-04; superseded by the 2026-10-25 review)

At the time of the 2026-10-04 snapshot, the top-level card linked a locally format-checked **D2.8 reference emission** from an owner-mirror. That historical recommendation is superseded: the current project status is **no TIFF cleared for competition download or upload**. Its `0.2600` association is owner-reported and is not authenticated to the exact file by an organizer receipt. A separate H33-6 TIFF is provided in the research area only: its preregistered
P1 mean ΔDTI was `−0.002737` (2/4 folds positive), P2 SGMC proxy was `+0.000159`, and the numeric gate
failed. The research artifact is explicitly **not slot-approved and not for upload**; its cross-site uniqueness is not established. A separate earlier
H33-F analog-field experiment also failed its local proxies (P1 mean ΔDTI `−0.093072`, 0/4 positive;
P2 `−0.016163` vs C0); its exploratory discriminator AUC `0.917` is not `HΔH`, and no transfer bound
is licensed. Its TIFF is a distinct research artifact, not a recommendation. The H27-4 `0.2708`
pairing is unsupported; the GEMSDOE28 owner page describes H27-4 as unscored/research-only.
The target `0.3195` is user-supplied and not independently confirmed as current here. A prior one-time
official-page status note dated 2026-10-04 did not support treating it as current/top, while the
GEMSDOE28 owner site contains a separate manual summary dated 2026-10-03 that reports the claim; this
conflict is unresolved and neither observation links a score to a local TIFF. Detailed rows are not
retained, and no official-page refresh or reproduction is permitted absent prior written consent or
an authorized API.

The first-pass spatial holdout and domain-transfer promotion claims were withdrawn after review.
Upstream C2's earlier P1 pass was also withdrawn for source/label leakage; its corrected conditional
source-exclusion diagnostic is P1 mean ΔDTI `−0.000722` (0/4 positive) and P2 SGMC proxy `+0.000283`,
still not slot-cleared because H19-5 was not re-derived per fold and the correction was not an
independent preregistered confirmation. H33-6 likewise uses fixed H19-5 and owner-mirror features, so
its diagnostics remain conditional. **No candidate is approved for a weekly slot.** See
`knowledge/07_hypothesis_slate_20261004.md`, `knowledge/08_h33_6_result_20261004.md`,
`evidence/first_pass_disposition.json`, `evidence/holdout33.json`, and `evidence/holdout_h33_6.json`.

## Review addendum (2026-10-25)

This session compared the existing H33-6 final raster against all same-grid TIFFs available in the checkout. Seven of nine comparisons exceeded the run protocol's correlation/3-pixel proximity threshold; no new placement or TIFF build was made. The pre-placement score surface and remote GEMSDOE registry rasters were unavailable, so the uniqueness screen is incomplete and remains a stop. H33-6 is **NOT OK TO SUBMIT**: its P1 mean delta was negative, its retained baseline was not re-derived per fold, its feature-alone canary is absent, and its final dots trigger the duplicate guard. See `evidence/duplicate_guard_run_card_20261025.json`, `knowledge/09_20261025_review.md`, and `registry/irregularities.json` entry `IR-33-DUP-20261025`. Treat all scores listed in the user brief as user/owner reports unless an organizer receipt is retained.

## Parallel-run protocol addendum (2026-10-25; mandatory)

1. **Lane:** the latest prompt says to use one “single method paragraph below,” but no unique method paragraph/lane is identified. Do not select a candidate surface or place dots until the lane is explicit.
2. **Duplicate stop:** screen the surface before placement and final dots against all accessible registry rasters. Stop and log if any rank-correlation exceeds `0.90` or more than `70%` of dots fall within `3 px` of a registry raster. Missing external registry TIFFs mean uniqueness is unverified, not passed.
3. **Reuse:** use the cached feature stack, a shared holdout evaluator that hides whole fault systems with buffer, fold-visible catalogue-derived feature construction, exact masking of visible faults, and the shared writer. `src/gemsdoe33/metric.py` and `submission.py` provide metric/writer primitives; `src/gemsdoe33/holdout.py` only provides quadrant IDs, and legacy `src/gems33/holdout.py:evaluate_proxy` scores prebuilt arrays without fold-specific candidate/source reconstruction. No current orchestration satisfies the full protocol.
4. **Reporting:** every reported score must say HOLDOUT-DTI (evaluator content hash/version, withheld-positive count, and 95% CI) or ORGANIZER-CONFIRMED (copied from a receipt). User/owner scores are not organizer-confirmed. Feature-alone AUC `>0.90` is a leakage canary until resolved. No projection may be presented as a score.
5. **TIF/notes:** do not emit a new TIFF until scientific and duplicate gates pass. A future note is capped at `140` characters. Validate finite `[0,1]` probabilities inside footprint, CRS/shape/affine match, and outside-mask policy from the current official instructions. A local validator is not portal acceptance.
6. **Budget/selection:** stop after `3` experiments or `2` hours. Weekly-slot promotion is a separate selector step under the current competition cap. The 2026-10-25 preflight ran `0` geological experiments, wrote no candidate TIFF, and spent no slot.
7. **Score provenance:** latest user prompt reports H33-2 B2 `0.2778` as a high owner-site result, but no receipt/file pairing is in this checkout. It also reports both `0.4413` and `0.3195` as current competition highs; the conflict is unresolved. Do not scrape, poll, or refresh DrivenData without prior written consent or an authorized API.
8. **New slate and stop record:** three unimplemented hypotheses are preserved in `knowledge/10_hypothesis_slate_20261025.md` and `evidence/hypothesis_slate_20261025.json`. The negative run card is `evidence/preflight_run_card_20261025.json`. Current data/cache absence, ambiguous lane, and missing registry rasters prevent validation; there is no new submission-ready TIF.
9. **Writer guard fix:** the shared `src/gemsdoe33/submission.py` writer now rejects invalid emitted probabilities rather than clipping/zero-filling them, refuses to overwrite package outputs, limits notes to `140` characters, and its validator rejects outside infinities while separately reporting whole-array finiteness. This does not diagnose the historical portal error or establish portal acceptance.
