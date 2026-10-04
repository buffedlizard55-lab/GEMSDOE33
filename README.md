# GEMSDOE33 — DOE GEMS fault-discovery project (DrivenData #306)

**Start here each session:** read this README and the full [standing brief](standing_prompt.md) before changing code. The complete operative brief is reproduced below in §1. This project is maintained under Arena's core values: **Maximize P(Win)** and **Own the Outcome**.

## Download a unique format-checked GeoTIFF

> **Unique H33-F analog-field transfer. Research candidate. NOT slot-approved.**
> In-footprint predicted values are in `[0, 1]`. Outside the footprint is NaN on the recommended file.
> Spatially blocked proxy holdout **failed** (P1 mean ΔDTI −0.093072, 0/4 folds vs rebuilt C0).
> Do **not** spend a weekly submission slot on this file. No live score is claimed.

| | Recommended — follows the null/NaN-outside wording | Troubleshooting alternative |
|---|---|---|
| GeoTIFF | [Download the unique NaN-outside TIFF](docs/downloads/gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef-nan.tif) | [Download the unique zero-outside TIFF](docs/downloads/gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef-zeros.tif) |
| SHA-256 | `59a68dcd752fc31d774b856e46fddbb9b0e3a9e9c7ab4abb06f77e99b218b10d` | `05d656cf3f24047d440fe24d42f28d4c64b1da29261c235cca3954953d5d3e27` |
| Bytes | 477,936 | 403,314 |
| Outside footprint | NaN | `0.0` (not as close to the official null/NaN wording) |
| Local file checks | 10/10 passed | 10/10 passed |
| Copy of D2.8? | **No** | **No** |

Both are single-band `float32`, `EPSG:32611`, `3730 × 3292`, 100 m, on the registered owner-mirror template transform; in-footprint values are within `[0,1]`. These are **local file checks only**, not proof of portal acceptance. The [manifest](docs/downloads/manifest.json) records the checks and hashes.

**Unique submission name:** `gemsdoe33-h33f-analog-xfer-20261004`

**Paste-ready note (113/200 characters):**

> GEMSDOE33 H33-F analog xfer | Dixie/Brady/DesertPeak wells+GeoDAWN | research not slot-approved | id d042874b26ef

See the [executive summary and exact upload steps](docs/executive-summary.html). No submission was uploaded from this session.

Historical D2.8 owner-mirror (not featured): [NaN-outside](docs/downloads/gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif) — owner-reported 0.2600, score/file pairing unconfirmed.

## Current honest conclusion

- A **unique** analog-field transfer GeoTIFF was generated this session from named Dixie Valley, Brady Hot Springs and Desert Peak domains (GDR 1391 well/spring names + official centroids) and shared GeoDAWN/LiDAR layers. It is not a copy of a previous submission.
- Exploratory 20 km-block domain-discriminator AUC = **0.917**. Ben-David et al. (2010) target-error bound is **not licensed** (λ unknown; analog labels are the same public catalogue, not independent BRIDGE GIS — GDR 1682/207 TLS-failed).
- Fold-safe P1 mean ΔDTI vs rebuilt C0 = **−0.093072** (0/4 folds). P2 SGMC vs C0 = **−0.016163**; vs matched-N random = **+0.001234**. **No weekly submission slot is approved.**
- The official public leaderboard was reviewed once on **2026-10-04** at the owner's request. That observation did not support the brief's claim that `0.3195` was then the current highest score. DrivenData [Terms of Use](https://www.drivendata.org/termsofuse/) prohibit automated and manual monitoring/copying without prior written consent. See [`registry/leaderboard_review.json`](registry/leaderboard_review.json).
- The claimed H27-4 `0.2708` score/file attribution is unsupported. The [GEMSDOE28 owner page](https://buffedlizard55-lab.github.io/GEMSDOE28/) says **“NO GEMSDOE28 SCORE”**.
- Upstream C2 remains research-only (P1 −0.000722, not slot-cleared). First-pass promotion claims remain withdrawn.

## Ranked geological research hypotheses

Five leads. Rank 1 (the requested analog transfer) was implemented and failed its proxy gate. Ranks 2–5 are unrun. Full records: [`registry/hypotheses.json`](registry/hypotheses.json).

| Rank | Hypothesis | Layers / signature | Why it may catch omitted faults | vs prior art | Upside / cost | Official source check |
|---:|---|---|---|---|---|---|
| 1 | **H33-F named analog-field transfer** (IMPLEMENTED, holdout FAIL) | Dixie/Brady/Desert Peak well-cell + centroid masks; GeoDAWN mag/grav/geodetic/conductivity + LiDAR scarps; off-catalogue analog-score ridges, d=2.8 | Signature of densely explored geothermal fields applied to under-mapped ground. Source labels are still the public catalogue inside those fields. | No prior emission used these named fields as source domains | Highest a priori; **measured P1 −0.093** | [GDR 1391](https://gdr.openei.org/submissions/1391), [OpenEI Dixie](https://openei.org/wiki/Dixie_Valley_Geothermal_Area), [USGS MRDS Brady](https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10221999), [OpenEI Desert Peak II](https://openei.org/wiki/Desert_Peak_II_Geothermal_Facility). GDR 1682/207 GIS TLS-failed. |
| 2 | **H33-G cond_surf edges × gravity HG** | Band 17 conductivity gradient ∩ band 18 iso_grav_anom_hg; catalogue as exclusion only | Blind fluid-filled conductors without a Quaternary scarp | cond_surf not previously a standalone conjunction | Moderate / low cost | Problem page layers; already restored. **Not run.** |
| 3 | **H33-H dilatation-rate edges × mag HG, strike-discordant** | geod_dilaterate ∩ tmi_hg with catalogue-azimuth gate | Active strain vs geologic surface-trace inventory | Not C2 relays; not generic H19-5 ensemble use | Moderate / low-medium | Restored bands 3 and 8. **Not run.** |
| 4 | **H33-J LiDAR upface residual** | upface_max after suppressing catalogue-parallel strikes | Antislope scarps the catalogue-shaped H19-5 emission is least likely to have spent | Not H27-4 1-px prune | Low-moderate / medium | Owner-mirror lidar_scarp_features. **Not run.** |
| 5 | **H33-I volcanic-vent alignments** | 21 GDR 1391 vents; mag/grav ridges in corridors | Magmatic alignments independent of Qfault compilations | Not H35 springs; not H33-F wells | Low / low; n=21 | CSV restored. **Not run.** |

## Domain adaptation decision

Named analog fields **were** defined and a unique emission **was** built. Transfer is **EXPLORATORY_NOT_LICENSED**. See [`evidence/domain_adaptation_preflight.json`](evidence/domain_adaptation_preflight.json), [`evidence/holdout_analog.json`](evidence/holdout_analog.json), [`knowledge/07_analog_transfer.md`](knowledge/07_analog_transfer.md), and [Ben-David et al. 2010](https://link.springer.com/article/10.1007/s10994-009-5152-4).

## Provenance and data caveats

- The 17 rasters/sidecar inputs are pinned in [`registry/owner_mirror_input_pins.json`](registry/owner_mirror_input_pins.json); they are owner-published GitHub mirrors, **not organizer-authenticated data**.
- The owner-mirrored `sample_submission.tif` is not blank: its 60,988 in-footprint ones match `labels.tif` positives exactly. Grid/footprint only.
- GDR 1682 and GDR 207 official pages were reviewed; local downloads failed TLS (`curl: (35)`). USGS ComCat TLS also failed. No analog GIS vectors were used.
- The unique NaN-outside file passed 10 local grid/value/format checks. No portal upload occurred.

## Reproduce local artifacts

```bash
python scripts/restore_data.py --group all
python scripts/run_analog_campaign.py
python scripts/build_site.py
python -m pytest -q
```

`run_analog_campaign.py` trains the analog-field classifier, writes the unique GeoTIFF, and records the fold-safe proxy holdout. It does not contact DrivenData.

## Site and key records

- [Project overview — unique download](docs/index.html)
- [Executive summary / upload steps](docs/executive-summary.html)
- [Research and hypotheses](docs/research.html)
- [Sources](docs/sources.html)
- [Irregularities](docs/irregularities.html)
- [Complete standing brief (HTML)](docs/standing-prompt.html)
- [`AI_DISCLOSURE.md`](AI_DISCLOSURE.md)
- [`AGENTS.md`](AGENTS.md)

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

## Current project decision (2026-10-04, session arena/01a107c2)

The featured download is a **unique H33-F analog-field transfer GeoTIFF**
(`gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef-nan.tif`): single-band float32, EPSG:32611,
100 m, template grid, in-footprint values in `[0,1]`, NaN outside. It is **not** a copy of D2.8.
Named Dixie Valley / Brady / Desert Peak source masks were built from GDR 1391 well/spring names
plus official centroids. An exploratory 20 km-block domain discriminator AUC was 0.917. The
Ben-David (2010) bound was **not** licensed (λ unknown; analog labels are the same public
catalogue). Fold-safe P1 mean ΔDTI vs rebuilt C0 was **−0.093072** (0/4 folds); P2 vs C0
**−0.016163**. **NOT slot-approved. Do not spend a weekly submission slot.** Historical D2.8
remains in `docs/downloads/` as a non-featured reference. A one-time official leaderboard review
on 2026-10-04 did not support the brief's claim that `0.3195` was then the highest score; detailed
rows are not retained because of the DrivenData Terms of Use. The claimed H27-4 `0.2708` pairing is
unsupported. C2 remains not slot-cleared. See `evidence/holdout_analog.json`,
`evidence/domain_adaptation_preflight.json`, and `knowledge/07_analog_transfer.md`.
