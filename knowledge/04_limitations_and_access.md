# Limitations and access needs (GEMSDOE33, 2026-10-04)

## Evidence and execution limits

| ID | Limitation | Consequence | Mitigation / next check |
|---|---|---|---|
| IR-NET-01 | Core/candidate binaries are restored from pinned public GitHub mirrors. Official GDR/NBMG/USGS source pages were read through the research interface, but analog/thermal source files have not been downloaded into this checkout. A local HEAD request to the GDR Quaternary Faults v2 ZIP failed with a TLS EOF. | H33-A and H33-B have not been geolocated, semantically audited, or validated; no analog-transfer result exists. | Use the official downloadable files below; record byte hashes, CRS, coverage, license, and labels before analysis. A public page listing is not proof that this workspace fetched the file. |
| NO-AUTOMATION | Project policy forbids DrivenData login, upload, scraping, and polling in code. | Competition submission and any new live score require the human owner. Public leaderboard values can change. | Manually review/upload if desired; save an organizer receipt. The published leaderboard is a static dated snapshot with a live link. |
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

1. **Potential slot:** current C2 has passed both frozen proxies and the exact local format audit. The
   owner may manually review it, but it remains unscored. Do not claim a live improvement absent a receipt.
   Current file: `docs/downloads/gems33-c2-stepover-relay-20261004-01f660dd8656.tif`; paste-ready note is
   on `docs/how-to-submit.html`.
2. **Highest scientific upside, high risk:** obtain and audit Dixie Valley `GIS_Faults.zip`; identify
   which geometries are authoritative and geolocate them. Investigate NBMG OF 03-27 only as its official
   PDF/geospatial PDF unless a separate official vector layer is found. Audit GDR #1288 as geothermal
   feature/classification data, not fault truth. Then specify common features and spatial source holdouts.
3. **Moderate cost:** retrieve the GDR #1391 2 m probe archive and audit season, coordinate, sampling,
   and bias metadata. Keep it distinct from USGS heat-flow residual products.
4. **P2 hygiene:** inspect the 2026 SGMC replacement release and decide whether the current proxy should
   be rebuilt from it.
5. **Novelty hygiene:** recover GEMSDOE29's radiometric experiment record before H33-D is rerun.

## Completed in this workspace

- Restored and hash-verified core grid, labels, 19-band feature stack, H27-4, SGMC proxy, and pinned
  Quaternary-fault shapefile components from public repository mirrors; the optional unpinned archive is
  excluded from the default candidate restore.
- Corrected C2 feature IDs to be deterministic and collision-free; rebuilt the 41,139-dot C2 artifact.
- Re-ran the frozen P1/P2 proxy suite: C2 and C5 pass; C1, C3, and C4 fail. C2 selected for parsimony.
- Rebuilt the current standalone format report. C2 is one-band float32, EPSG:32611, 100 m, exact sample
  grid, finite in [0,1] over the whole array, and zero outside the template footprint.
- Added metric, gate, format, feed, and site-link tests plus a no-DrivenData CI workflow.
- Generated a static campaign feed from the committed ledger. It does not poll or scrape the organizer.
