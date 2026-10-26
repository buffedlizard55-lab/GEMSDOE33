# GEMSDOE33 standing brief and operating contract

**Read this entire file at the start of every session, then read `README.md`.** This is the complete
working specification consolidated from the owner's task and explicit standing corrections recorded
for this repository. It is not presented as a verbatim chat transcript. Update it only when the owner
changes the requirements; record any change and its consequence in the repository.

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
2. Put a valid, readily discoverable submission GeoTIFF at the very top of the project site, and
   provide an executive-summary page with exact upload steps. The recommended file must be a single-
   band `float32` GeoTIFF on the official training/sample grid, EPSG:32611, 100 m, matching bounds
   and transform, with probability values in `[0,1]` and null/NaN outside the footprint as specified
   by the official instructions. Re-open and validate the saved bytes. Give it a unique submission
   filename/name and a concise paste-ready note/comment within the portal limit. State whether the
   file is a reference, owner-reported historical artifact, or a new model. Do not imply local format
   checks guarantee portal acceptance.
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

## Current project decision (2026-10-04)

The top-level recommended download remains a locally format-checked **D2.8 reference emission** from
an owner-mirror. Its `0.2600` association is owner-reported and is not authenticated to the exact file
by an organizer receipt. A separate H33-6 TIFF is provided in the research area only: its preregistered
P1 mean ΔDTI was `−0.002737` (2/4 folds positive), P2 SGMC proxy was `+0.000159`, and the numeric gate
failed. The unique research artifact is explicitly **not slot-approved and not for upload**. A separate earlier
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


## Current outcome addendum (2026-10-25, A33-L1)

The earlier dated project-decision and review sections above remain historical audit records; this
addendum is the current outcome. The analog-transfer lane has now restored and grid-audited all 17
hash-pinned inputs, rebuilt the shared feature cache, restored all nine pinned focus rasters, frozen
five new analog hypotheses, and executed one A33-L1 experiment through the pinned shared evaluator
and writer.

A genuinely new 37,654-dot GeoTIFF is available at
`docs/downloads/gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros.tif`,
with an official-template-profile NaN-outside twin. It passes exact grid, dtype, in-footprint range,
saved-byte and uniqueness checks. Its maximum final registry Spearman is `0.02221` and maximum
candidate-dot fraction within three pixels is `42.25%`. **It is NOT OK TO SUBMIT.** A33-L1
HOLDOUT-DTI (`gems-segment-pooled-v1`, 60,988 withheld positives, spatial-block bootstrap 95% CI)
is `0.108374 [0.097607, 0.119402]`; the fold-safe regional comparator is
`0.113244 [0.102796, 0.124169]`. Paired delta is `−0.004870`, 95% CI
`[−0.010900, +0.001226]`, with 0/4 fold wins. The scientific gate failed, the separate slot selector
was not run, zero competition slots were spent, no upload occurred, and no score is projected.

The nine-site forensic review established byte-level dependence in the reported high-score family:
GEMSDOE25 and 30 are identical; GEMSDOE31 solo is an exact subset after removing 3,891 one-pixel
catalogue-flank dots; GEMSDOE32 B2 is an exact subset after removing another 2,545 dots at one-to-two
pixels; GEMSDOE36 contains all B2 dots plus 1,200. Metric-aware pruning is therefore a plausible
explanation for the owner-reported `0.2778`, not authenticated causal proof. Every historical DTI
value remains **OWNER/USER-REPORTED, NOT ORGANIZER-CONFIRMED** absent a retained receipt.

Current evidence: `evidence/a33_l1_experiment.json`, `evidence/a33_l1_run_card.json`,
`evidence/focus_registry_analysis_20261025.json`, and
`knowledge/11_focus_forensics_and_a33_l1_result_20261025.md`.
