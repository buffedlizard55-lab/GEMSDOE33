# Verified data sources and provenance (2026-10-04)

Verification levels: **[B]** bytes downloaded and hash/size-checked in this workspace · **[P]** source page
fetched and read through the research interface · **[S]** located in a search result (title/snippet/DOI)
· **[C]** cited by another verified source. A source listing, mirror hash, or page fetch does not prove
semantic equivalence, map accuracy, or suitability for the hidden competition target.

## Competition rules and score sources

| Source | Link | Level | Notes |
|---|---|---|---|
| GEMS problem description, metric, and submission format | https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ | [P] | DTI α=0.2, β=0.8, 300 m triangular kernel; single-layer float32 GeoTIFF; competition CRS/grid and value range. Consult page for current rules. |
| GEMS overview and GeoDAWN context | https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/ | [P] | Competition background and linked literature. |
| Official public leaderboard | https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ | [P] | Reviewed manually once on 2026-10-04 (America/Los_Angeles) per owner request; did not support the brief's claim that 0.3195 was then the top score. Individual participant rows are not retained or monitored per Terms of Use. |
| Official rules PDF | https://docs.nlr.gov/docs/fy26osti/96647.pdf | [P] | September 2026 edition; all 7 parsed chunks fetched/read 2026-10-04. §§3.2, 3.4–3.5 confirm one single-layer 100 m GeoTIFF, up to three feedback submissions/week, one final selection across both prize phases, and a narrative disclosure of generative-AI extent/use. |
| DrivenData Terms of Use | https://www.drivendata.org/termsofuse/ | [P] | Read 2026-10-04. §Prohibited Uses bars robots/automatic devices for any purpose including monitoring/copying and manual monitoring/copying without prior written consent. No auto-refresh leaderboard feed. |
| DrivenData robots.txt | https://www.drivendata.org/robots.txt | [P] | Read 2026-10-04. Disallows `/accounts/`, competition search, and `leaderboard_partial`; Terms of Use are stricter on monitoring. |
| Reference solution | https://github.com/drivendataorg/gems-prize-reference-solution | [C] | Linked from the problem page. |
| Competition data tab (login-walled) | https://www.drivendata.org/competitions/306/competition-doe-gems/data/ | [C] | Lists official input names; code in this repository does not log in or fetch this page. |

Competition scores in `registry/score_ledger.json` remain owner-reported unless organizer receipts are
archived. Holdout proxy values are not scores. The campaign-feed generator reads only the local ledger and
never scrapes or polls the organizer. Under the Terms of Use reviewed 2026-10-04, the public leaderboard
is a static dated snapshot here; this repo does not promise an automatically current feed without an
authorized API or written permission.

## Competition data mirrors used (owner-supplied, hash-pinned)

| Content | Mirror | Verification / caveat |
|---|---|---|
| `training_features.tif` (19 bands, 418,912,844 bytes) | buffedlizard55-lab/GEMSDOE @ commit `c0c06ac82178f26b94fce3397036ef8f12a2f3a0`, parts 000–004 | [B] SHA-256 `4371c82e…` matched after concat; owner-supplied mirror |
| `labels.tif` (existing catalogue) | GEMSDOE24 @ `07345ea0604953d7efb858d9cfbc21e20c7aca0b` | [B] SHA-256 `7ba308cc…`; owner-supplied mirror |
| `sample_submission.tif` (grid/footprint template) | GEMSDOE24 @ `07345ea0604953d7efb858d9cfbc21e20c7aca0b` | [B] SHA-256 `2176d08e…`; template only, never truth |
| H19-5 ridge emission | GEMSDOE24 input `gems19-h19-5-…-e27054cf-nan.tif` | [B] 1,712,322 bytes; 121,131 nonzero pixels |
| d=2.8 dotted baseline | GEMSDOE24 `…e56ea318af89-nan.tif` | [B] 44,090 dots |
| h27-4-r1-solo baseline (owner-reported 0.2708) | GEMSDOE28 @ `33cc5942220f1440531d7184889c5c6f5d2f0a3e` | [B] Git blob SHA `12b0a4dd…` and full-file SHA-256 pinned; score is not organizer-authenticated |
| Derived SGMC 100 m raster | GEMSDOE24 `data/external/derived_sgmc_faults_100m_u8.tif` | [B] independent P2 proxy; not hidden competition truth |
| INGENIOUS Quaternary fault shapefile components | `jklinck/geothermal_research` @ `56d78de7a989c12e2dce50cd65a4095df57030d2` | [B] CRS parsed as NAD83; 42.5% of sampled vertices lie within 150 m of supplied catalogue in a geometry cross-check. This does not validate every trace or establish target equivalence. GDR #1391 lists v1 and a newer v2 that supersedes v1; this mirror's exact version correspondence has not been verified. A local HEAD request for the GDR v2 ZIP failed TLS. |
| Wells/springs, Qfault attributes, DEM links | GEMSDOE24 `data/external/*` | [B] sizes/hashes in `registry/data_manifest.json`; owner-supplied mirrors |

Hashes establish identity with the pinned mirror bytes, not the organizer's source. See
`registry/data_manifest.json` for file-by-file provenance. The optional unpinned 408 MB research archive
is marked unverified and excluded from the default candidate restore.

### Sample/label anomaly (IR-SAMPLE-LABEL-01)

The restored sample template and catalogue labels share the same grid. On all 5,167,373 finite-template
cells, their values are identical: 60,988 ones and 5,106,385 zeros. The template is nonfinite on the other
7,111,787 cells. The audit is reproducible at `scripts/audit_sample_template_values.py` and recorded in
`evidence/sample_template_label_overlap.json`. This is an irregularity in the owner-supplied mirror, not
proof that the official sample has the same semantics. All production code uses only the template's finite
mask/grid metadata and never reads its values as truth.

## Official and research sources for hypotheses

| Source | Link | Verification / meaning | Use and limits |
|---|---|---|---|
| INGENIOUS regional compilation, GDR #1391, DOI 10.15121/1881483 | https://gdr.openei.org/submissions/1391 | [P] Public page, CC BY 4.0. Lists 2 m temperature probes, Quaternary faults, heat flow, gravity, springs/wells, and other layers. The page lists the 2 m archive as a 1.03 MB download and says Quaternary Faults v2 supersedes v1. | Official source listing for fault mirror/probe archive; the community mirror's v1/v2 correspondence is not verified. H33-B archive is listed but not restored here. The heat-flow product is separate from 2 m probe temperatures. |
| Dixie Valley EGS baseline, GDR #207, DOI 10.15121/1148837 | https://gdr.openei.org/submissions/207 | [P] Public page, CC BY 4.0; describes a highly characterized field with public-domain geoscience and well data; lists `GIS_Faults.zip` (15.1 MB). Workspace requests to the archive failed TLS/connection setup; no bytes were fetched. | Candidate H33-A source, not currently runnable. The page does not show that every fault trace is drilling-verified or equivalent to the competition target. Audit file-level provenance/CRS if an authorized download becomes available. |
| Desert Peak–Brady preliminary geologic map, NBMG OF 03-27 | https://pubs.nbmg.unr.edu/Geol_Desert_Peak_Brady_geotherm_p/of2003-27.htm | [P] Official NBMG product page; title identifies the preliminary geologic map. It lists a free PDF ZIP and a geospatial PDF. | H33-A map/context source. No GIS vector archive is confirmed on this product page; inspect the downloads and terms before expecting direct fault-vector transfer. |
| Faulds & Hinz, 2015, favorable tectonic/structural settings of Great Basin geothermal systems, OSTI 1724082 | https://www.osti.gov/biblio/1724082 | [P] 2015 paper; describes step-overs/relay ramps as favorable settings in a regional geothermal-system inventory. It is **not** NBMG OF 03-27. | C2 structural context, not a map download or confirmation of any emitted trace. |
| Faulds, Hinz & Coolbaugh, 2010, structural investigations of Great Basin geothermal fields, OSTI 1110517 | https://www.osti.gov/biblio/1110517 | [P] Bibliographic record identifies a 2010 conference paper; it is **not** NBMG OF 03-27. | Separate regional context, not a map download. |
| Brady/Desert Peak geothermal AI dataset, GDR #1288, DOI 10.15121/1773692 | https://gdr.openei.org/submissions/1288 | [P] Public page, CC BY 4.0; labels are geothermal/non-geothermal. Inputs include mineral alteration, land-surface temperature, fault density, and other layers. | H33-A context only. Its geothermal labels are not expert fault labels, and its layers are not the GeoDAWN 19-band raster. Do not imply bandwise transfer. |
| GeoDAWN magnetic/radiometric release, DOI 10.5066/P93LGLVQ | https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7 | [S] | H33-D source metadata; check actual band descriptions before feature engineering. |
| USGS GeoDAWN landing page | https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and | [S] | GeoDAWN context. |
| USGS Qfaults, DOI 10.5066/P9BCVRCK | https://www.sciencebase.gov/catalog/item/589097b1e4b072a7ac0cae23 | [C] | Catalogue scope. |
| USGS Great Basin conductive heat-flow release, DOI 10.5066/P9BZPVUC | https://www.sciencebase.gov/catalog/item/6297d2fad34ec53d276c5b28 | [P] | Multiple weighted background heat-flow maps and well-point/residual data; not the GDR 2 m temperature-probe archive. |
| USGS State Geologic Map Compilation (SGMC) original item | https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d | [P] | Page notes a 2026 replacement release; audit before treating an old mirror as current. |
| SGMC 2026 replacement, DOI 10.5066/P1A3DQZK | https://doi.org/10.5066/P1A3DQZK | [P] Replacement release identified; contents, CRS, schema, and map semantics still need audit. | Future P2 proxy refresh. |
| Great Basin MT conductance, DOI 10.5066/P9TWT2LU | https://www.sciencebase.gov/catalog/item/62979746d34ec53d276c113b | [C] | Potential future context. |
| USGS 3DEP 1 m DEM catalog | https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e | [C] | High-cost future geomorphics; not used by C2. |
| Ben-David et al. (2010), domain-adaptation bound, DOI 10.1007/s10994-009-5152-4 | https://doi.org/10.1007/s10994-009-5152-4 | [S] | H33-A theory. The bound includes source error, a divergence term, and joint-error λ. |
| Mattéo et al. (2021), deep-learning fault mapping, DOI 10.1029/2020JB021269 | https://doi.org/10.1029/2020JB021269 | [P] | Detector-design prior. |
| Hermant et al. (2025), Quaternary fault mapping | https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf | [P] | Scarp-offset context. |
| Reid et al. (1990), Euler deconvolution, DOI 10.1190/1.1442774 | https://doi.org/10.1190/1.1442774 | [C] | Potential-field method context. |

## Campaign-site reads (owner-operated)

| Site | Read status | Key extraction |
|---|---|---|
| https://buffedlizard55-lab.github.io/GEMSDOE28/ | [P] | 0.2708 lineage; H27-4/H36-1/H37-1/H38-1; holdout/inversion notes; score remains owner-reported |
| https://buffedlizard55-lab.github.io/GEMSDOE29/docs/index.html | [P] | Owner-observed IR-PORTAL-01 message, SGMC proxy notes, worming/H41 results; portal error diagnosis remains unconfirmed |
