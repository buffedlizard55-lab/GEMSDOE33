# GEMSDOE33 — DOE GEMS fault-discovery project (DrivenData #306)

**Start here each session:** read this README and the full [standing brief](standing_prompt.md) before changing code. The complete operative brief is reproduced below in §1. This project is maintained under Arena's core values: **Maximize P(Win)** and **Own the Outcome**.

## Download a format-checked D2.8 reference

> **This is a reference emission, not a new model or a demonstrated leaderboard improvement.** The source is an owner-published mirror. Its claimed `0.2600` score is owner-reported; no organizer receipt ties that score to these exact bytes.

| | Recommended — follows the null/NaN-outside wording | Troubleshooting alternative |
|---|---|---|
| GeoTIFF | [Download the NaN-outside TIFF](docs/downloads/gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif) | [Download the zero-outside TIFF](docs/downloads/gemsdoe33-d28-reference-20261004-426073b6b4ab-zeros.tif) |
| SHA-256 | `c5e07fad5672879562ea43805cf71c7ba7512fd1a37ca460de83971bc6d8abdc` | `29ca0bc2cf249f96f1504b8c0ec5e775e78668f6d0f54f5c1c33c580cce74f73` |
| Bytes | 499,842 | 423,456 |
| Outside footprint | NaN | `0.0` (not as close to the official null/NaN wording) |
| Local file checks | 10/10 passed | 10/10 passed |

Both are single-band `float32`, `EPSG:32611`, `3730 × 3292`, 100 m, on the registered owner-mirror template transform; in-footprint values are within `[0,1]`. These are **local file checks only**, not proof of portal acceptance. The `[manifest](docs/downloads/manifest.json)` records the checks and hashes.

**Unique submission name:** `gemsdoe33-d28-reference-20261004`

**Paste-ready note (158/200 characters):**

> GEMSDOE33 D2.8 reference | owner-mirror emission; 0.2600 is owner-reported, score/file pairing unconfirmed | format-checked, not a new model | id 426073b6b4ab

See the [executive summary and exact upload steps](docs/executive-summary.html). No submission was uploaded from this session.

## Current honest conclusion

- The official public leaderboard was reviewed once on **2026-10-04** at the owner's request. That observation did not support the brief's claim that `0.3195` was then the current highest score. The page cannot identify local TIFF bytes or prove an account association. Because the [DrivenData Terms of Use](https://www.drivendata.org/termsofuse/) prohibit automated and manual monitoring/copying without prior written consent, detailed rows are not retained or republished; this project does not poll or refresh the page. See [`registry/leaderboard_review.json`](registry/leaderboard_review.json).
- The claimed H27-4 `0.2708` score/file attribution is unsupported. The [GEMSDOE28 owner page](https://buffedlizard55-lab.github.io/GEMSDOE28/) says **“NO GEMSDOE28 SCORE”** and describes its artifacts as unscored/research-only. No organizer receipt or verified account/file record ties the claim to the owner's TIFF. The D2.8 `0.2600` score/file pairing remains unconfirmed.
- **No new candidate has demonstrated a valid, independent improvement over the current best. No candidate is approved for a weekly submission slot.** The available download is only the D2.8 reference.
- Upstream C2 is preserved as research-only in [`archive/legacy_candidates/`](archive/legacy_candidates/). Its earlier P1 pass was withdrawn for leakage; the corrected conditional source-exclusion diagnostic is P1 mean ΔDTI `−0.000722` (0/4 positive), P2 SGMC proxy `+0.000283`, and still **not slot-cleared** because the fixed H19-5 surface was not re-derived per fold and the diagnostic was not a preregistered independent confirmation. See [`evidence/holdout33.json`](evidence/holdout33.json) and [`IR-33-C2-01`](registry/irregularities.json).
- Initial holdout, reconstruction, pruning and domain-transfer promotion claims were withdrawn after audit. Their scripts/results are retained for provenance in [`archive/withdrawn_first_pass/`](archive/withdrawn_first_pass/); read [`evidence/first_pass_disposition.json`](evidence/first_pass_disposition.json) and [`registry/irregularities.json`](registry/irregularities.json). Do not reuse the archived metrics as evidence.

## Ranked geological research hypotheses

The first-pass implementation preceded this shortlist, contrary to the owner's required ordering. The following hypotheses are therefore a **retrospective research shortlist, not preregistration**. They are not validated models; the availability checks below say what was actually verified.

| Rank | Hypothesis and candidate layers | Physical signature / why it may find faults absent from USGS/INGENIOUS | Prior-art distinction | Expected upside / cost | Official-data check and status |
|---:|---|---|---|---|---|
| 1 | **Field-verified BRIDGE fault-label transfer**. BRIDGE GIS picks plus GeoDAWN `tmi_hg`, `tmi_vg`, `det_elev`, `det_elev_slope`, `iso_grav_anom_hg`, `depth_to_base_surf`. | Multi-scale, orientation-preserving magnetic, gravity, basement and terrain lineaments supervised/tested against field-mapped traces; a separate field label set could test fault signatures outside the regional compilation. BRIDGE is not assumed to be target truth. | Prior emissions use regional catalogue labels and/or LiDAR predictors; no reviewed prior artifact used BRIDGE field-verified picks as independent source labels. | **Highest qualitative upside if transfer gates pass; magnitude unknown. Medium cost.** | [GDR 1682](https://gdr.openei.org/submissions/1682) is public and lists a 3.79 MB GIS archive; its README says picks are field-verified only in Dixie and Gabbs Valleys. Direct download failed TLS/HTTP 000 here; archive contents were not staged or inspected. **Blocked; not viable/validated yet.** |
| 2 | **USGS ComCat focal-mechanism orientation prior**. Event nodal-plane location, strike/dip/rake plus magnetic, terrain and strain-invariant layers. | Test whether independent candidate lineaments align with reviewed active slip-plane orientations; do not treat earthquake density alone as a fault label. May expose active or blind structures absent from surface-trace inventories. | Prior seismic candidate used density/coherence, not per-event focal-plane geometry. | **Moderate, coverage-dependent upside; medium cost.** | [USGS ComCat docs](https://earthquake.usgs.gov/data/comcat/index.php) and [FDSN API](https://earthquake.usgs.gov/fdsnws/event/1/) were checked: count queries returned focal-mechanism products and an example exposed nodal-plane fields. A full extract was not staged; no validation. |
| 3 | **Brady–Desert Peak mineral alteration + structural-edge coincidence**. Candidate GDR 1303 mineral layers (their existence/schema still need inspection) plus magnetic, gravity, terrain and LiDAR scarp features. | Test whether field-supported alteration/contact halos coincide with independent structural edges, a potential indicator of persistent permeability or blind faults rather than a raw radiometric anomaly. | Prior hot-spring/geothermometry and radiometric/Euler experiments did not use a verified mineral-classification/edge conjunction. | **Low-to-moderate upside; high cost and high uncertainty.** | [GDR 1303](https://gdr.openei.org/submissions/1303) lists a public CC BY 4.0, 2.58-GB Brady/Desert Peak/Salton Sea archive. It was not downloaded; hyperspectral/mineral layers, overlap and semantics are **unconfirmed**. Do not treat as available until inspected. |

The full layer lists, prior-art notes, expected-rank rationale and individual blockers are in [`registry/hypotheses.json`](registry/hypotheses.json). The currently preferred research lead (BRIDGE) cannot proceed until its official archive is obtained and inspected. No hypothesis has been implemented as a promoted candidate.

## Domain adaptation decision

The requested analogy—learn from field-mapped faults in Dixie Valley, Desert Peak or Brady—has **not** been completed. The old experiment used GDR well/spring record-density quantiles instead of named field domains, random raster rows despite spatial autocorrelation and duplicate site rows, and an arbitrary discriminator whose class was not shown to match the model's `HΔH` class. It also omitted a defensible joint-label error `lambda` and the finite-sample/class-complexity term. Its AUC and transfer verdict are withdrawn.

The replacement [`scripts/run_domain_adaptation.py`](scripts/run_domain_adaptation.py) is fail-closed: it writes `BLOCKED_NOT_ESTIMATED` and does not fit a classifier, report a divergence, or license transfer. A usable Ben-David et al. (2010) target-error bound requires source error, a justified empirical `HΔH` divergence, a finite-sample/class-complexity term and `lambda` (joint-label error). See the [paper](https://link.springer.com/article/10.1007/s10994-009-5152-4), [`src/gemsdoe33/domain.py`](src/gemsdoe33/domain.py), and [`evidence/preflight.json`](evidence/preflight.json). BRIDGE's official page and license listing were checked, but its GIS payload could not be downloaded in this sandbox. No transfer is licensed, rejected, or slot-approved.

## Provenance and data caveats

- The 17 rasters/sidecar inputs audited for this reference are pinned in [`registry/owner_mirror_input_pins.json`](registry/owner_mirror_input_pins.json); they are owner-published GitHub mirrors, **not organizer-authenticated data**. A matching hash proves byte identity with that mirror only; it does not prove source, license, official schema, or score attribution. The separate [`registry/data_manifest.json`](registry/data_manifest.json) is the upstream C0/C2 candidate-input manifest; its unpinned items remain explicitly unverified.
- The owner-mirrored `sample_submission.tif` is not blank: its 60,988 in-footprint ones match `labels.tif` positives exactly. It is used only for grid/footprint, never as an absence label.
- The owner-mirrored sample has 5,167,373 finite in-footprint cells. The 19-band training mirror has 3,061 template cells carrying the nodata sentinel in each of 18 bands; band 6 has 12 further sentinel cells. Reproduction is in [`evidence/input_grid_audit.json`](evidence/input_grid_audit.json) via `scripts/audit_inputs.py`. This corrects an earlier erroneous 1,521-cell count. None of these rasters was downloaded through an authenticated DrivenData session.
- GDR 1391 (INGENIOUS) and GDR 1682 official source pages were reviewed; local downloads of external archives failed TLS/HTTP 000. The 2.58-GB GDR 1303 archive was not downloaded. USGS ComCat API availability was checked, but no complete extract was staged or used to build the TIFF.
- The recommended NaN-outside file passed 10 local grid/value/format checks, but no portal upload occurred. The zero-outside alternative is offered only for troubleshooting and is less literal to the outside-mask wording.

## Reproduce local artifacts

The model inputs under `data/` and caches under `.cache/` are git-ignored. Restoration uses owner mirrors; see the warning in `data/README.md`.

```bash
python scripts/restore_data.py --group all
python scripts/audit_inputs.py
python scripts/prepare_data.py --force-bands --skip-detector
python scripts/build_submission.py
python scripts/build_site.py
python -m pytest -q
```

`build_submission.py` only repackages the historical D2.8 owner-mirror emission; it does not train a new candidate. The current 121-channel feature cache is research-only. Do not interpret a public-catalogue-trained detector as private hidden-fault validation.

## Site and key records

- [Project overview](docs/index.html)
- [Executive summary / upload steps](docs/executive-summary.html)
- [Research and hypotheses](docs/research.html)
- [Sources](docs/sources.html)
- [Irregularities](docs/irregularities.html)
- [Complete standing brief (HTML)](docs/standing-prompt.html)
- [`AI_DISCLOSURE.md`](AI_DISCLOSURE.md)
- [`evidence/first_pass_disposition.json`](evidence/first_pass_disposition.json)
- [`evidence/holdout33.json`](evidence/holdout33.json) — upstream C2 conditional source-exclusion diagnostic; not slot-cleared
- [`registry/score_ledger.json`](registry/score_ledger.json) — historical owner-reported campaign entries only; H27 claim marked unsupported, no official leaderboard rows
- [`AGENTS.md`](AGENTS.md) — repository operating safeguards

---

## 1. Complete standing brief — read in full every session

The full operative brief is preserved in [`standing_prompt.md`](standing_prompt.md) and repeated below.

---

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
