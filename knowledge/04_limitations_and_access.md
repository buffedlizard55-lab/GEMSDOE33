# Limitations and access needs (GEMSDOE33, 2026-10-04)

## Evidence and execution limits

| ID | Limitation | Consequence | Mitigation / next check |
|---|---|---|---|
| IR-NET-01 | Core/candidate binaries are restored from pinned public GitHub mirrors. Official GDR/NBMG/USGS source pages were read, but analog/thermal source files have not been downloaded into this checkout. Direct workspace requests for GDR #207 `GIS_Faults.zip` and the GDR Quaternary Faults v2 ZIP failed at TLS/connection setup. | H33-A and H33-B have not been geolocated, semantically audited, or validated; no analog-transfer result exists. | Use the official downloadable files only through an authorized channel; record byte hashes, CRS, coverage, license, and labels before analysis. A public page listing is not proof that this workspace fetched the file. |
| IR-HOLDOUT-LEAKAGE-01 | The original P1 runner masked labels only at scoring time. C0's one-pixel catalogue prune and C2's catalogue filters used the full label raster; Qfaults-derived candidate features also retained the held-out fault geometries. | The old C2 `+0.000405` P1 result and all old C1–C5 P1 values are withdrawn for promotion. A corrected, fold-specific C0/Qfaults diagnostic gives C2 mean ΔDTI `−0.000722` (0/4 folds); P2 remains `+0.000283`. No new candidate clears a slot. | See `evidence/holdout33_legacy_catalogue_only.json` and corrected `evidence/holdout33.json`. Re-derive/audit the upstream H19-5 surface, preregister a fresh protocol, and rerun before any slot decision. |
| IR-SAMPLE-LABEL-01 | The restored `sample_submission.tif` exactly equals `labels.tif` on its 5,167,373 finite-footprint cells (60,988 ones; 5,106,385 zeros) and is nonfinite outside. | Treating its finite values as a submission example/truth would leak the known catalogue. The official task's sample semantics are not confirmed for these owner-supplied mirror bytes. | Project code may use only the finite footprint/grid metadata. The anomaly is recorded in `evidence/sample_template_label_overlap.json`; do not read the sample values as labels. |
| NO-AUTOMATION | Project policy forbids DrivenData login, upload, scraping, or polling in code. The official [Terms of Use](https://www.drivendata.org/termsofuse/) (read 2026-10-04) prohibit automated monitoring and manual monitoring/copying without prior written consent. | The results feed cannot be automatically kept current under the present access policy; a public-leader value is only a dated snapshot. Submission and any new live score require the human owner. | Keep a static, clearly dated snapshot and link to the official page. Do not add a scheduled fetcher unless DrivenData provides an authorized API/written permission. |
| COMPUTE | Workspace has limited CPU/RAM and no GPU; full 1 m DEM coverage is large. | A supervised 1 m scarp detector is not feasible here; no such model was trained in this session. | Prioritize small, falsifiable proxy experiments and external compute only after data/label checks. |
| TRUTH | Organizer's expert-labelled target is private. | P1 catalogue-hidden and P2 SGMC evaluations are imperfect local proxies. | Report them only as proxies; do not infer live score from their deltas. |
| LABELS | H33-A sources differ in location, mapping method, feature type, and label semantics. GDR #1288 is a geothermal classification dataset with a fault-density input, not fault-trace truth or a 19-band GeoDAWN raster. | A naive analog transfer would conflate geothermal favorability, fault density, and expert fault labels. | Geolocate; audit each source layer; define a genuinely shared, comparable representation; assess label compatibility and spatial holdouts before transfer. |
| NBMG-GIS | The official NBMG OF 03-27 product page lists a free PDF ZIP and a geospatial PDF; it does not confirm a downloadable GIS vector archive. | Do not describe OF 03-27 as a ready-to-use shapefile or fault-vector archive. | Inspect the official PDF/geospatial PDF contents and terms; seek an official GIS layer separately if required. |
| SGMC-2026 | The older SGMC item points to a 2026 replacement DOI 10.5066/P1A3DQZK. | Existing P2 mirror may not reflect the current release or schema. | Audit the replacement data and compare scope, CRS, and trace semantics before updating P2. |
| IR-QFAULTS-02 | GDR #1391 lists Quaternary Faults v1 and a newer v2 that supersedes v1; the pinned community shapefile mirror has not been byte-compared with either archive. A direct GDR v2 ZIP HEAD request failed TLS from the workspace. | C2's fault-vector prior remains mirror-pinned but official version correspondence is not established. | Preserve the passing C2 proxy result as evidence for the current mirror only; compare official archive versions and rerun holdouts before changing the input. |
| IR-EVIDENCE-01 | GEMSDOE29 radiometric result record (seeds 280–289) was not retrieved through the available public GitHub API lookup. | H33-D may be pre-empted; novelty and prior outcome remain uncertain. | Reconcile the original artifact/result record before running or claiming novelty. |
| IR-REPO-31-32 | Public GitHub API lookups for repository names `31GEMSDOE` and `32GEMSDOE` returned HTTP 404. | This does not distinguish private, uncreated, renamed, or elsewhere-hosted projects. The prompt supplied no URLs or result details. | Leave both rows explicitly unscored; do not invent links or results. |

## Specific public sources to inspect before analog work

1. **Dixie Valley fault-map files:** [GDR #207](https://gdr.openei.org/submissions/207), including
   `GIS_Faults.zip` (listed at 15.1 MB; CC BY 4.0 page). The page describes a highly characterized field
   with public-domain geoscience and well data; it does not prove every map trace is drilling-verified or
   equivalent to the GeoDAWN target. Inspect archive layer names, lineage, CRS, and individual terms.
   Separately, GDR #1391 lists Quaternary Faults v1 and v2, with v2 superseding v1; the C2 community
   mirror's exact version is not yet verified. A local TLS-blocked HEAD request prevented checking the
   official v2 ZIP bytes here.
2. **Desert Peak–Brady geologic map:** official
   [NBMG OF 03-27 product page](https://pubs.nbmg.unr.edu/Geol_Desert_Peak_Brady_geotherm_p/of2003-27.htm).
   It lists a free PDF ZIP and a geospatial PDF. A GIS vector archive is not confirmed on that product
   page; verify contents/terms or find an official vector source before expecting direct vector transfer.
3. **Brady/Desert Peak geothermal classification:** [GDR #1288](https://gdr.openei.org/submissions/1288)
   (CC BY 4.0 page; 109.94 MB release). It documents geothermal/non-geothermal classes and multiple
   feature inputs, including fault density. Those labels are not expert fault-trace labels and those
   rasters are not equivalent to the GeoDAWN 19-band training stack. Use only as a separately named
   covariate/classification comparison after geolocation and schema review.
4. **Shallow temperature probes:** [GDR #1391](https://gdr.openei.org/submissions/1391), which lists a
   1.03 MB 2 m probe archive. It is not in the current candidate cache. Do not conflate shallow probe
   temperatures with the USGS conductive heat-flow/well-residual release DOI
   [10.5066/P9BZPVUC](https://www.sciencebase.gov/catalog/item/6297d2fad34ec53d276c5b28).

For H33-A, apply the domain-adaptation bound only after common features and label semantics are defined:
`εT(h) ≤ εS(h) + ½ dHΔH(DS, DT) + λ`. A classifier-two-sample test can estimate a divergence term; it
does not certify the joint-error term λ or target accuracy.

## Next actions ranked by value / cost

1. **No submission slot now:** the old C2 P1 pass is withdrawn. Fold-specific label masking and Qfaults
   source exclusion changed the mean P1 delta from `+0.000405` (3/4 positive, invalid legacy run) to
   `−0.000722` (0/4 positive). P2 remains `+0.000283`, but that cannot override the P1 failure. Keep the
   C2 TIFF as a research artifact only; the C0 TIFF is a reference, not a recommendation to spend a slot.
2. **Audit the baseline provenance before another P1 decision:** the fold-safe diagnostic reconstructs the
   H27-4 base exactly from H19-5 plus fold-visible labels, but the upstream H19-5 raster-generation code is
   not in this checkout. Re-derive it per fold or document/verify its feature-only provenance; preregister
   a fresh spatial/source holdout before using results to consider a slot.
3. **Highest scientific upside, high risk:** obtain and audit Dixie Valley `GIS_Faults.zip` through an
   authorized channel; identify which geometries are authoritative and geolocate them. Investigate NBMG
   OF 03-27 only as its official PDF/geospatial PDF unless a separate official vector layer is found. Audit
   GDR #1288 as geothermal feature/classification data, not fault truth. Then specify common features and
   spatial source holdouts.
4. **Moderate cost:** retrieve the GDR #1391 2 m probe archive through an authorized channel and audit
   season, coordinate, sampling, and bias metadata. Keep it distinct from USGS heat-flow residual products.
5. **P2/novelty hygiene:** inspect the 2026 SGMC replacement release and recover GEMSDOE29's radiometric
   experiment record before refreshing P2 or rerunning H33-D.
6. **Submission compliance:** the official rules require a narrative disclosure of generative-AI use and
   allow three submissions per week but only one final submission across both prize phases. See
   `docs/how-to-submit.html`; the disclosure there is a draft requiring owner review.

## Completed in this workspace

- Restored and hash-verified core grid, labels, 19-band feature stack, H27-4, SGMC proxy, and pinned
  Quaternary-fault shapefile components from public repository mirrors; the optional unpinned archive is
  excluded from the default candidate restore.
- Corrected C2 feature IDs to be deterministic (including a unique fallback for blank source identifiers); rebuilt the 41,139-dot C2 research artifact. Its byte hash remains unchanged.
- Audited the P1 feature/label path. The original P1 run was invalid for promotion because candidate construction used the held-out catalogue and Qfaults geometries. The archived values are explicitly withdrawn.
- Rebuilt C0 per fold from fold-visible catalogue labels, removed whole Qfaults source IDs within a 600 m square holdout buffer plus a 100 m raster guard, and reran the diagnostic: C2 mean P1 ΔDTI `−0.000722`, 0/4 positive; P2 `+0.000283`; no numeric gate pass and no slot clearance. The fixed H19-5 upstream provenance remains an explicit limitation.
- Confirmed the fold-specific C0 rebuild exactly reproduces the pinned 40,199-dot H27-4 control when the full catalogue is visible.
- Rebuilt the standalone C2 format report. The research TIFF is one-band float32, EPSG:32611, 100 m, exact sample grid, finite `[0,1]` whole-array, and zero outside the template footprint. This is not organizer acceptance.
- Added tests for deterministic dot thinning, fold-specific C0 reconstruction, and source-system exclusion, in addition to metric/gate/format/feed/site-link checks.
- Re-read the full official-rules PDF (all 7 parsed chunks) and DrivenData Terms of Use. AI disclosure is required in the narrative; automated/manual leaderboard monitoring/copying without written consent is prohibited under the current Terms of Use. The feed remains static and date-stamped.
- Recorded the sample/label value-copy anomaly in `evidence/sample_template_label_overlap.json`; code uses only the template's finite mask.
