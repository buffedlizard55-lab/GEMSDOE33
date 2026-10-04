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

- The `0.3195` target remains unverified as current. A prior one-time official-page status note for **2026-10-04** says the spot-check did not support that claim as then-current, while the GEMSDOE28 owner site contains a separate manual summary dated 2026-10-03 that reports it. That conflict is unresolved; neither observation is a score/file receipt. The [DrivenData Terms of Use](https://www.drivendata.org/termsofuse/) restrict manual/automatic monitoring or copying without prior written consent. This project keeps no row-level data and does not refresh the page. See [`registry/leaderboard_review.json`](registry/leaderboard_review.json) and [`IR-33-SCORE-03`](registry/irregularities.json).
- The claimed H27-4 `0.2708` score/file attribution is unsupported. The [GEMSDOE28 owner page](https://buffedlizard55-lab.github.io/GEMSDOE28/) labels H27-4 unscored/research-only and reports no GEMSDOE28 score. No organizer receipt or authenticated file/account record ties the claim to that TIFF. The D2.8 `0.2600` pairing is also owner-reported and unconfirmed.
- **H33-6 failed its preregistered P1 screen:** mean ΔDTI `−0.00273732`, positive in `2/4` folds; P2 SGMC proxy ΔDTI `+0.00015900`. It beat the matched-random mean but not the local H27-4 owner-mirror raster control; that control's score/file pairing is unverified. The arm is stopped; no candidate is approved for a weekly submission slot. See [`knowledge/08_h33_6_result_20261004.md`](knowledge/08_h33_6_result_20261004.md) and [`evidence/holdout_h33_6.json`](evidence/holdout_h33_6.json).
- A unique H33-6 TIFF is available below **for research/reproduction only**. Its matched-count local format checks pass, but its candidate failed the holdout and the diagnostics are conditional proxies; **do not upload it**. The only top-level recommended package remains the D2.8 reference, not a new model.
- Upstream C2 is preserved as research-only in [`archive/legacy_candidates/`](archive/legacy_candidates/). Its earlier P1 pass was withdrawn for leakage; the corrected conditional source-exclusion diagnostic is P1 mean ΔDTI `−0.000722` (0/4 positive), P2 SGMC proxy `+0.000283`, and still not slot-cleared because the fixed H19-5 surface was not re-derived per fold and the diagnostic was not an independent preregistered confirmation. See [`evidence/holdout33.json`](evidence/holdout33.json) and [`IR-33-C2-01`](registry/irregularities.json).
- Initial holdout, reconstruction, pruning and domain-transfer promotion claims were withdrawn after audit. Their scripts/results remain in [`archive/withdrawn_first_pass/`](archive/withdrawn_first_pass/); see [`evidence/first_pass_disposition.json`](evidence/first_pass_disposition.json). Do not reuse the archived metrics as evidence.

## Unique H33-6 TIFF — research only, do not upload

A distinct, reproducible TIFF was generated from the frozen candidate recipe to satisfy the artifact/download requirement. It **failed** its P1 screen and is explicitly **not slot-approved**. Its 10/10 package checks and separate `scripts/validate_submission.py` audit pass under the stated local policy (finite [0,1] inside; NaN or zero outside); this verifies file format only, not science, private-label accuracy, portal acceptance, or a competition score. See [`evidence/format_check_h33_6_6c888d2ce0f7.json`](evidence/format_check_h33_6_6c888d2ce0f7.json).

- **Direct download (NaN outside):** [`GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif`](docs/downloads/research/GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif) · 482,682 bytes · SHA-256 `18604d71f11db269a3f70007433d1dd74e4f09eb195861dc2aeda4d98aa8efe7`.
- [Single-member ZIP](docs/downloads/research/GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.zip) · optional [zero-outside alternate](docs/downloads/research/GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-zeros.tif).
- **Unique research identifier:** `GEMSDOE33-H33-6-edge-consensus-research-20261004` (not an upload recommendation).
- **Paste-ready note (141/200 characters):**

> GEMSDOE33 H33-6 edge consensus | P1 delta DTI -0.002737 (2/4), P2 +0.000159 | RESEARCH ONLY; gate failed, not slot-approved | id 6c888d2ce0f7

See [`h33-6-research-manifest.json`](docs/downloads/research/h33-6-research-manifest.json) for hashes, bands and local format checks. The reproducible builder is `scripts/build_h33_6_research.py`.

## Ranked geological research hypotheses

The round-two five-hypothesis slate and exact H33-6 rule were frozen and SHA-256 recorded **before** its implementation and holdout run. It contains three new concepts (H33-6/7/8) plus the explicitly identified carry-forward/related designs H33-9/10; the prior round's shortlist was retrospective and remains archived separately. Expected improvement is qualitative only; no DTI or contest-score gain is forecast.

| Rank | Hypothesis and exact layers | Physical signature / missing-catalogue rationale | Prior-art difference | Expected upside / cost / official source status |
|---:|---|---|---|---|
| 1 (runnable) | **H33-6 cross-physics edge-normal consensus:** GeoDAWN band 14 `tmi`, 13 `iso_grav_anom`, 15 `depth_to_base_surf`, 17 `cond_surf`. | Coincident magnetic/gravity edge normals with aligned orientation, boosted by the stronger basement/conductivity edge. Concealed basin faults may offset susceptibility/density/basement or fluid conductance without a clear 100 m surface scarp. | Existing primitives build single-layer derivatives/coherence; no local candidate combines aligned raw-field edge normals, separate basement/conductivity support, and matched-budget reallocation. | **Moderate qualitative upside, unknown magnitude; low–medium cost; no new data.** It failed the preregistered P1 screen (mean ΔDTI `−0.00273732`, 2/4 positive), so this arm is stopped. See the [full result](knowledge/08_h33_6_result_20261004.md). |
| 2 (blocked, high ceiling) | **H33-7 BRIDGE field-pick transfer:** official GDR #1682 Dixie/Gabbs LiDAR fault picks plus shared GeoDAWN magnetic, gravity, basement-depth and conductivity bands. | Spatially separate field-mapped source labels could test transferable fault signatures; source picks are not target truth. | No implemented field-specific analog-label transfer in this repo; the prior arbitrary well-density discriminator is withdrawn and is not Ben-David `HΔH`. | **Potentially high, wholly unquantified; medium–high cost.** [Official page](https://gdr.openei.org/submissions/1682) and [README](https://gdr.openei.org/files/1682/BRIDGE_README.pdf) say public CC BY 4.0/3.79 MB and field verification limited to Dixie and Gabbs Valleys; archive bytes were blocked by TLS, so not viable yet. |
| 3 (blocked) | **H33-8 USGS Gabbs 3D surface transfer:** DOI `10.5066/P9BR3681` `AllGabbsFaults.zip`; GeoDAWN bands 3, 9, 13, 14, 15, 18 for edge/geometry checks. | Shallow projection of mapped 3D surfaces may expose subsurface faults missing from Quaternary surface catalogs; the USGS geologic interpretation also uses potential-field evidence. | No 3D-surface projection was implemented locally; differs from BRIDGE's 2D LiDAR picks. | **Moderate–high over narrow footprint; unknown; medium cost.** [USGS source](https://www.sciencebase.gov/catalog/item/62b21845d34e74f0d80f17aa?format=json) lists CC0 1.0 and the 2.91 MB fault ZIP. Catalog bbox lies inside GeoDAWN bbox, but ZIP retrieval failed and no feature overlap was checked. |
| 4 (continued, unimplemented) | **H33-9 ComCat focal-plane orientation:** event location and nodal-plane strike/dip/rake plus GeoDAWN bands 3, 9, 13, 14, 15. | Test candidate lineament azimuths against reviewed active focal mechanisms; retain nodal-plane ambiguity, and do not treat earthquake density as fault geometry. | Earlier H33-2 already described the design; no local extraction/implementation exists, so this is a continuation rather than a new concept. | **Low–moderate, coverage-dependent; medium cost.** Official [USGS ComCat](https://earthquake.usgs.gov/fdsnws/event/1/) count/example checks exist, but no complete extract is staged and local requests fail TLS. |
| 5 (partly pre-empted) | **H33-10 signed strain-lobe boundary:** GeoDAWN bands 7 `geod_shearrate`, 8 `geod_dilaterate`, 17 `cond_surf`, 15 `depth_to_base_surf`, 18 `iso_grav_anom_hg`. | Signed mechanical asymmetry across a conductive/basement boundary, aligned to a gravity edge, could mark a buried permeable fault without a surface scarp. | Prior DILCOND/SRCOH/strain screens are close and owner-reported weak; this edge/sign formulation is distinct but novelty is limited. | **Low qualitative upside; low–medium cost; local owner-mirror layers only.** Not tested this round. |

Full physics rationale, prior-art notes, source checks and freeze criteria are in [`knowledge/07_hypothesis_slate_20261004.md`](knowledge/07_hypothesis_slate_20261004.md) and [`registry/hypotheses.json`](registry/hypotheses.json). H33-7/8 are publicly listed but not locally obtainable/validated; no `HΔH` divergence or transfer claim is made.

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
# The completed H33-6 holdout is frozen in evidence/holdout_h33_6.json; do not rerun or retune it.
PYTHONPATH=src ./.venv/bin/python scripts/build_h33_6_research.py  # rebuilds the failed research-only TIFF; do not upload
python scripts/build_site.py
python -m pytest -q
```

`build_submission.py` only repackages the historical D2.8 owner-mirror emission; it does not train a new candidate. The frozen H33-6 arm failed and must not be retuned from that result. `build_h33_6_research.py` regenerates only the distinctly named, format-checked research TIFF and labels it not for upload. The current 121-channel feature cache is research-only. Do not interpret a public-catalogue-trained detector as private hidden-fault validation.

## Site and key records

- [Project overview](docs/index.html)
- [Executive summary / upload steps](docs/executive-summary.html)
- [Research and hypotheses](docs/research.html)
- [Sources](docs/sources.html)
- [Irregularities](docs/irregularities.html)
- [Complete standing brief (HTML)](docs/standing-prompt.html)
- [`AI_DISCLOSURE.md`](AI_DISCLOSURE.md)
- [`evidence/first_pass_disposition.json`](evidence/first_pass_disposition.json)
- [`knowledge/07_hypothesis_slate_20261004.md`](knowledge/07_hypothesis_slate_20261004.md) and [`evidence/hypothesis_slate_20261004_preregistered.json`](evidence/hypothesis_slate_20261004_preregistered.json) — frozen five-hypothesis round-two slate and hash
- [`evidence/holdout_h33_6.json`](evidence/holdout_h33_6.json) and [`knowledge/08_h33_6_result_20261004.md`](knowledge/08_h33_6_result_20261004.md) — H33-6 negative, conditional proxy diagnostic
- [`docs/downloads/research/h33-6-research-manifest.json`](docs/downloads/research/h33-6-research-manifest.json) — unique H33-6 TIFF hashes and local-only validation; not for upload
- [`evidence/holdout33.json`](evidence/holdout33.json) — upstream C2 conditional source-exclusion diagnostic; not slot-cleared
- [`registry/score_ledger.json`](registry/score_ledger.json) — historical owner-reported campaign entries only; H27 claim marked unsupported, no official leaderboard rows
- [`AGENTS.md`](AGENTS.md) — repository operating safeguards

---

## 1. Complete standing brief — read in full every session

The full operative brief is preserved in [`standing_prompt.md`](standing_prompt.md) and reproduced below.

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

The top-level recommended download remains a locally format-checked **D2.8 reference emission** from
an owner-mirror. Its `0.2600` association is owner-reported and is not authenticated to the exact file
by an organizer receipt. A separate H33-6 TIFF is provided in the research area only: its preregistered
P1 mean ΔDTI was `−0.002737` (2/4 folds positive), P2 SGMC proxy was `+0.000159`, and the numeric gate
failed. The unique research artifact is explicitly **not slot-approved and not for upload**. The H27-4
`0.2708` pairing is unsupported; the GEMSDOE28 owner page describes H27-4 as unscored/research-only.
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
