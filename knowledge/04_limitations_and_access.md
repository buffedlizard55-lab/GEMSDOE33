# Limitations and access needs (GEMSDOE33, updated 2026-10-04)

> This update supersedes the prior ranked-next-actions section below. H33-6 was preregistered and screened in this continuation; it failed P1. No candidate is slot-cleared. See `knowledge/07_hypothesis_slate_20261004.md` and `knowledge/08_h33_6_result_20261004.md`.

## Evidence and execution limits

| ID | Limitation | Consequence | Mitigation / next check |
|---|---|---|---|
| IR-NET-01 | Core/candidate binaries are restored from pinned public GitHub mirrors. Official GDR/NBMG/USGS source pages were read, but analog/thermal source files have not been downloaded into this checkout. Direct workspace requests for GDR #207 `GIS_Faults.zip` and the GDR Quaternary Faults v2 ZIP failed at TLS/connection setup. | H33-A and H33-B have not been geolocated, semantically audited, or validated; no analog-transfer result exists. | Use the official downloadable files only through an authorized channel; record byte hashes, CRS, coverage, license, and labels before analysis. A public page listing is not proof that this workspace fetched the file. |
| IR-HOLDOUT-LEAKAGE-01 | The original P1 runner masked labels only at scoring time. C0's one-pixel catalogue prune and C2's catalogue filters used the full label raster; Qfaults-derived candidate features also retained the held-out fault geometries. | The old C2 `+0.000405` P1 result and all old C1–C5 P1 values are withdrawn for promotion. A corrected, fold-specific C0/Qfaults diagnostic gives C2 mean ΔDTI `−0.000722` (0/4 folds); P2 remains `+0.000283`. No new candidate clears a slot. | See `evidence/holdout33_legacy_catalogue_only.json` and corrected `evidence/holdout33.json`. Re-derive/audit the upstream H19-5 surface, preregister a fresh protocol, and rerun before any slot decision. |
| IR-SAMPLE-LABEL-01 | The restored `sample_submission.tif` exactly equals `labels.tif` on its 5,167,373 finite-footprint cells (60,988 ones; 5,106,385 zeros) and is nonfinite outside. | Treating its finite values as a submission example/truth would leak the known catalogue. The official task's sample semantics are not confirmed for these owner-supplied mirror bytes. | Project code may use only the finite footprint/grid metadata. The anomaly is recorded in `evidence/sample_template_label_overlap.json`; do not read the sample values as labels. |
| NO-AUTOMATION | Project policy forbids DrivenData login, upload, scraping, or polling in code. The official [Terms of Use](https://www.drivendata.org/termsofuse/) (read 2026-10-04) prohibit automated monitoring and manual monitoring/copying without prior written consent. | The `0.3195` target is unverified as current: a prior official-page status note conflicts with a third-party owner-site summary dated one day earlier. No row-level values are retained; submission requires the human owner. | Keep only the conflict-aware dated status note and link to the official page. Do not refresh or copy rows without an authorized API or prior written permission. |
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

1. **No slot for H33-6, H33-F, or C2.** H33-6's preregistered P1 mean ΔDTI is `−0.00273732` (2/4 positive), P2 is `+0.00015900`; it failed and is stopped. The separate earlier H33-F screen has P1 mean `−0.093072` (0/4 positive), P2 `−0.016163` vs C0; its discriminator AUC is not an `HΔH` bound. C2's corrected conditional P1 is `−0.000722` (0/4 positive), P2 `+0.000283`; it is also not slot-cleared. Do not retune or rerun the completed H33-6 screen to repair logging; any new test requires a new preregistered design and independent confirmation. See the relevant evidence JSONs, `knowledge/07_analog_transfer.md`, and `knowledge/08_h33_6_result_20261004.md`.
2. **Obtain one official analog archive before transfer work.** Preferred scientific lead is BRIDGE GDR #1682 (CC BY 4.0 public listing, 3.79 MB; README says field verification is limited to Dixie and Gabbs Valleys). Alternative is USGS Gabbs Valley 3D fault surfaces, DOI 10.5066/P9BR3681 (CC0 1.0, 3.05 MB listed). Both binary retrievals failed from this workspace; Gabbs bbox overlap is not feature overlap. Hash and inspect actual bytes, schemas, CRS, lineage, licenses/share terms, and feature-level overlap before calling either viable.
3. **Do not claim Ben-David transfer from a domain classifier alone.** Only after a named source label set is obtained, define common feature support/processing, source/target spatial blocks, a suitable hypothesis class, and target-label compatibility. A small estimated `HΔH` term would not establish a small joint-label error `lambda` or target success.
4. **Repair the fixed-baseline provenance gap before a new P1 promotion test.** H19-5 upstream generation/training code is absent; per-fold H27-4 rebuilding cannot prove the fixed raster is independent of held-out labels. Re-derive the source per fold or replace it with a fully documented feature-only base, then preregister a fresh candidate/confirmation design.
5. **Keep source/mirror and validation distinctions explicit.** Current raster bytes are owner mirrors, not organizer-authenticated. Check the 2026 SGMC replacement before changing P2; no proxy is hidden-label truth. No leaderboard refresh without permission or authorized API.
6. **Submission compliance:** recheck official rules for AI disclosure, slot frequency, final selection, and external-data/share terms before a human chooses any upload. The executive summary's manual steps are informational; no upload has occurred.

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
- Re-read the full official-rules PDF (all 7 parsed chunks) and DrivenData Terms of Use. AI disclosure is required in the narrative; automated/manual leaderboard monitoring/copying without written consent is prohibited under the current Terms of Use. The results registry keeps no row-level data and is not refreshed.
- Wrote and hash-pinned a five-hypothesis round-two slate before H33-6 code/holdout; screened H33-6 once with 10 matched-random controls per fold. Its negative P1 result is recorded and not retuned.
- Preserved the earlier exploratory H33-F named analog-field screen separately: P1 −0.093072 (0/4 positive), P2 −0.016163 vs C0. Its domain AUC is not `HΔH`; transfer was not licensed. The unique TIFF is not slot-cleared.
- Built a unique H33-6 TIFF as a research-only artifact, with a unique identifier/note, package checks, and a second format audit that allows NaN only outside the footprint. The candidate is not slot-approved.
- Corrected `scripts/validate_submission.py` so its default follows the documented null/NaN-or-zero outside policy, checks finite [0,1] values inside, and offers an explicit strict-zero alternative; the old all-finite default conflicted with the official null/NaN wording and package validator.
- Recorded the sample/label value-copy anomaly in `evidence/sample_template_label_overlap.json`; code uses only the template's finite mask.
