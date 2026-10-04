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

The only publicly downloadable recommendation is a locally format-checked **D2.8 reference emission**
from an owner-mirror. Its `0.2600` association is owner-reported and is not authenticated to the exact
file by an organizer receipt. A one-time official leaderboard review on 2026-10-04 did not support
the brief's claim that `0.3195` was then the highest score; detailed rows are intentionally not
retained or republished because of the DrivenData Terms of Use. The claimed H27-4 `0.2708` pairing is
unsupported. The first-pass spatial holdout and domain-transfer promotion claims were withdrawn after
review. No new candidate has been demonstrated to beat the current best; **no candidate is approved
for a weekly slot**. No leaderboard refresh or reproduction is permitted by this project absent prior
written consent or an authorized API. See the README and `evidence/first_pass_disposition.json` before
any future work.
