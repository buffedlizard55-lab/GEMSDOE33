# Verified official data sources (line-by-line audit, 2026-10-04)

Verification levels: **[B]** bytes downloaded and hash/size-checked this session ·
**[P]** page fetched and read this session · **[S]** located via search-result record
(title + snippet + DOI) this session · **[C]** cited by an already-verified source.

## Competition core (official)

| Source | Link | Level | Notes |
|---|---|---|---|
| GEMS problem description (task, datasets, metric, submission format) | https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ | [P] | DTI α=0.2 β=0.8, 300 m triangular kernel; EPSG:32611; float32 [0,1] |
| GEMS about page (sponsor, GeoDAWN context, literature) | https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/ | [P] | cites Mattéo et al. 2021 and Hermant et al. 2025 |
| GEMS leaderboard | https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ | [C] | public-best 0.3195 is an owner-reported one-off read (2026-10-03) |
| Official rules PDF | https://docs.nlr.gov/docs/fy26osti/96647.pdf | [C] | identity-verified against Dropbox mirror by GEMSDOE repo session 9; not re-fetched here (egress) |
| Reference solution | https://github.com/drivendataorg/gems-prize-reference-solution | [C] | linked from problem page |
| Competition data tab (login-walled) | https://www.drivendata.org/competitions/306/competition-doe-gems/data/ | [C] | training_features.tif / labels.tif / sample_submission.tif / 1m_DEM_links.csv |

## Competition data mirrors used (owner-supplied, hash-pinned)

| Content | Mirror | Level | Hash evidence |
|---|---|---|---|
| training_features.tif (19 bands) | buffedlizard55-lab/GEMSDOE @ c0c06ac, data/bridge parts 000–004 | [B] | sha256 4371c82e… matched after concat this session |
| labels.tif (existing_faults) | buffedlizard55-lab/GEMSDOE24 @ 07345ea, data/bridge/labels.tif | [B] | sha256 7ba308cc… matched (evidence/data_placement.json) |
| sample_submission.tif | buffedlizard55-lab/GEMSDOE24 @ 07345ea, data/bridge/sample_submission.tif | [B] | sha256 2176d08e… matched |
| H19-5 ridge emission | GEMSDOE24 inputs/gems19-h19-5-…-e27054cf-nan.tif | [B] | 1,712,322 B; 121,131 nonzero px |
| dotted d=2.8 base | GEMSDOE24 docs/downloads/…-e56ea318af89-nan.tif | [B] | 44,090 dots |
| h27-4-r1-solo (scored 0.2708) | GEMSDOE28 docs/downloads/gems28-h27-4-r1-solo-…-8acb75e1f2cc-nan.tif | [B] | git blob sha 12b0a4dd… verified at fetch |
| SGMC faults raster 100 m | GEMSDOE24 data/external/derived_sgmc_faults_100m_u8.tif | [B] | 83,593 fault px; P2 proxy truth |
| INGENIOUS Quaternary fault shapefile (NAD83) | codeload jklinck/geothermal_research, faults_quaternary_INGENIOUS_regional_data/ | [B] | CRS validated: 42.5% of sampled vertices within 150 m of catalogue |
| INGENIOUS wells/springs, Qfaults traces, DEM links | GEMSDOE24 data/external/* | [B] | sizes/hashes per registry/data_manifest.json |

Mirrors are NOT organizer-authenticated; hashes prove equality with the mirror only
(provenance policy stated in registry/data_manifest.json).

## Official external sources for hypotheses

| Source | Link | Level | Used by |
|---|---|---|---|
| GeoDAWN survey release (Glen & Earney 2024, DOI 10.5066/P93LGLVQ) | https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7 | [S] | H33-D radiometrics; native grids |
| GeoDAWN landing page | https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and | [S] | same |
| USGS Qfaults database (DOI 10.5066/P9BCVRCK) | https://www.sciencebase.gov/catalog/item/589097b1e4b072a7ac0cae23 | [C] | catalogue scope |
| INGENIOUS regional compilation GDR #1391 (CC BY 4.0) | https://gdr.openei.org/submissions/1391 | [C] | wells/springs/probes/vents lineage |
| Dixie Valley EGS baseline — GIS_Faults.zip (GDR #207, DOI 10.15121/1148837) | https://gdr.openei.org/submissions/207 | [S] | H33-A analog field |
| Desert Peak–Brady's map NBMG OF 03-27 (Faulds & Garside 2003), step-over controls (OSTI 1110517) | https://www.osti.gov/servlets/purl/1110517 | [S] | H33-A analog + C2 physical basis |
| Brady/Desert Peak labelled ML grids (GDR #1288, DOI 10.15121/1773692) | https://gdr.openei.org/submissions/1288 | [S] | H33-A co-training labels |
| Great Basin heat flow (DeAngelo et al. 2022, DOI 10.5066/P9BZPVUC) | https://doi.org/10.5066/P9BZPVUC | [C] | H33-B thermal residual |
| Great Basin MT conductance 5 depth slices (DOI 10.5066/P9TWT2LU) | https://www.sciencebase.gov/catalog/item/62979746d34ec53d276c113b | [C] | future context layer |
| USGS 3DEP 1 m DEM catalog | https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e | [C] | H38-4-style geomorphics (high cost) |
| Domain-adaptation bound: Ben-David et al. 2010, Machine Learning 79:151–175, DOI 10.1007/s10994-009-5152-4 | https://doi.org/10.1007/s10994-009-5152-4 | [S] | H33-A theory |
| Deep-learning fault mapping: Mattéo et al. 2021, DOI 10.1029/2020JB021269 | https://doi.org/10.1029/2020JB021269 | [P] | detector design prior |
| Quaternary fault DL mapping: Hermant et al. 2025 (Stanford SGW) | https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf | [P] | scarp-offset magnitudes |
| Euler deconvolution: Reid et al. 1990, DOI 10.1190/1.1442774 | https://doi.org/10.1190/1.1442774 | [C] | SI=0 contact model |
| Faults & geothermal structure: Faulds & Hinz 2015 (OSTI 1724082) | https://www.osti.gov/servlets/purl/1724082 | [C] | blind systems, step-overs |
| Dixie Valley research overview (GBCGE) | https://gbcge.org/locations/dixie-valley/ | [S] | LiDAR + field-verified traces |

## Campaign sites studied (owner-operated)

| Site | Read this session | Key extraction |
|---|---|---|
| https://buffedlizard55-lab.github.io/GEMSDOE28/ | [P] | 0.2708 lineage; H27-4/H36-1/H37-1/H38-1; LOSFO protocol; live inversion |
| https://buffedlizard55-lab.github.io/GEMSDOE29/docs/index.html | [P] | IR-PORTAL-01 (whole-array [0,1] rule); SGMC off-catalogue proxy; worming FAIL; H41 FAIL |
