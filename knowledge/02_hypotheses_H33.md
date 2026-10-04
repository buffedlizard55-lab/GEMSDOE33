# Historical GEMSDOE33 hypothesis register — superseded (2026-10-04)

> This was the retrospective first-round register, not a preregistration or current ranking. Its H27-4 `0.2708` attribution was unsupported. Use `knowledge/07_hypothesis_slate_20261004.md` and `registry/hypotheses.json` for the frozen round-two slate and current status.

Five research candidates, ordered by qualitative expected scientific upside per implementation cost
(machine-readable copy: `registry/hypotheses.json`). C2 is implemented but its earlier P1 PASS is withdrawn
because the test used full-catalogue labels and Qfaults source geometries. The corrected conditional
source-exclusion diagnostic is negative; no candidate is cleared for a weekly slot. Numerical score priors
are withheld where source data, label compatibility, or a validated transfer estimate is missing. Proxies
are not competition scores.

## Rank 1 — H33-C2 stepover relay-bridge faults — IMPLEMENTED, CORRECTED P1 DIAGNOSTIC FAIL, NOT SLOT-CLEARED

- **Layers:** Quaternary-fault vectors from the INGENIOUS GDR #1391 compilation, retrieved from a pinned
  community mirror; the hash authenticates those mirror bytes, not official accuracy. GDR #1391 lists
  Quaternary Faults v2 as superseding v1, but this mirror's exact version correspondence has not been
  verified; the C2 result applies only to the pinned mirror input. Band 18 `iso_grav_anom_hg`; h27-4
  H27-4 owner-mirror baseline raster (the `0.2708` score/file pairing is unsupported).
- **Physical signature:** distinct fault-vector tip pairs separated by 300–2,500 m and differing by at
  most 30° in strike; add sparse bridge dots at about 283 m spacing where band 18 exceeds the local
  in-footprint 80th percentile within 200 m.
- **Why it may capture an omitted feature:** relay connectors are a structural hypothesis. Faulds & Hinz's
  2015 regional structural-settings study discusses relays and other favorable settings
  (<https://www.osti.gov/biblio/1724082>); it is not the NBMG OF 03-27 map report and does not certify any
  emitted bridge as an unmapped fault. Test the proposed connectors against the independent proxies.
- **Difference from prior work:** GEMSDOE27 T-v2 filled within-polyline gaps and failed its owner-reported
  live result; C2 restricts to distinct feature IDs and adds a gravity-edge gate. Its initial P1 test was
  invalid: held-out Qfaults source systems and the full catalogue remained visible to candidate/base
  construction.
- **Corrected conditional diagnostic:** C2 adds 940 dots to the full-data 40,199-dot base (41,139
  total). With a fold-rebuilt base and Qfaults system IDs excluded within the 600 m square holdout buffer
  plus a 100 m raster guard, P1 mean ΔDTI is **−0.0007220038** (folds −0.0007243, −0.0011430,
  −0.0006367, −0.0003840; 0/4 positive). Across folds, the candidate adds 2,643 dots and zero
  incremental TPw; its added FPw equals those 2,643 dots. P2 remains **+0.0002831018**. The numeric
  gate FAILS; the artifact is **not slot-cleared**. The frozen
  H19-5 source surface is not regenerated per fold, so this is a conditional diagnostic, not an independent
  confirmation. Artifact (research only):
  `docs/downloads/gems33-c2-stepover-relay-20261004-01f660dd8656.tif`, SHA-256
  `7272633447365d7ec8a9c07972b48df92b071a1ecc5765cf14199c14dea4f0f7`. No live score.

## Rank 2 — H33-A analog-field transfer with a domain-adaptation bound — DESIGN ONLY, UNVALIDATED

- **Potential sources:** Dixie Valley fault-map files listed in
  [GDR #207](https://gdr.openei.org/submissions/207) (the page notes extensive public-domain geoscience
  and well data, but does not establish that every map trace is drilling-verified); the official
  [NBMG OF 03-27 product page](https://pubs.nbmg.unr.edu/Geol_Desert_Peak_Brady_geotherm_p/of2003-27.htm)
  for the Desert Peak–Brady preliminary geologic map (free PDF ZIP and geospatial PDF are listed; no GIS
  vector archive is confirmed on that page); and [GDR #1288](https://gdr.openei.org/submissions/1288),
  which includes geothermal/non-geothermal labels, mineral alteration, temperature, fault-density, and
  other layers for Brady/Desert Peak.
- **Geolocation and feature compatibility are prerequisites:** the actual source layers must be
  downloaded, geolocated, and audited for CRS, resolution, coverage, lineage, and label definition. Build
  only a common feature set that is demonstrably present and comparably processed in source and target.
  Do not assume the analog sites contain or match the GeoDAWN 19-band training raster. GDR #1288's
  geothermal labels and feature grids are not GeoDAWN truth and are not an equivalent 19-band raster;
  its fault input is a density layer, not expert fault labels.
- **Formal limit:** Ben-David et al. (2010, DOI
  <https://doi.org/10.1007/s10994-009-5152-4>) give a target-error bound of the form
  `εT(h) ≤ εS(h) + ½ dHΔH(DS, DT) + λ`, where λ is the joint error of the best shared hypothesis. A
  classifier-two-sample test estimates a divergence term for a defined common representation; small
  divergence alone does not establish small λ, semantic label compatibility, or target accuracy. Require
  source-site holdouts and target-proxy validation.
- **Why it may add information / difference:** detailed analog mapping could add structural information
  missing from a regional catalogue, but neither the claimed omission class nor cross-field label
  equivalence is established. The supplied campaign ledger does not document a completed, audited
  source-to-target fault transfer. H33-A is a research plan, not a result.
- **Expected DTI / cost:** unknown until data and labels are aligned; potentially high upside, high
  uncertainty, medium-high integration and validation cost. Official source pages are accessible. A direct
  attempt to retrieve GDR #207's listed archive failed TLS/connection setup; no bytes were obtained, so
  this branch is not currently runnable. Other source files also have not been ingested or audited here.

## Rank 3 — H33-B shallow thermal-probe residuals × gravity edges — DESIGNED, NOT RUN

- **Layers:** GDR #1391 lists a 1.03 MB 2 m temperature-probe archive; those bytes are not in the current
  candidate cache. Candidate context includes training band 18 `iso_grav_anom_hg` and band 5
  `iso_grav_anom_slope` (gravity derivative, not thermal). The USGS release DOI 10.5066/P9BZPVUC has
  background conductive heat-flow maps and well-point/residual products; these are not 2 m probe
  temperatures.
- **Physical signature:** residualize shallow probes against a pre-registered regional/topographic
  background; test coherent positive residuals near gravity edges using spatially blocked matched controls.
- **Why it may capture an omitted feature / difference:** shallow fluid-flow anomalies might occur
  without a preserved surface scarp. Springs, season, elevation, land cover, and sampling density are
  confounds. Unlike discharge-point conjunctions, H33-B tests a residualized spatial field; it has no
  result yet.
- **Expected DTI / cost:** unknown; medium effort after file retrieval, metadata audit, bias controls,
  and proxy validation.

## Rank 4 — H33-D radiometric K/Th alteration corridors — PARTIALLY PRE-EMPTED

- **Layers:** GeoDAWN K/eU/Th radiometric grids and independently defined gravity context; verify band
  metadata before constructing any ratios. Do not relabel band 5, `iso_grav_anom_slope`, as thermal.
- **Physical signature:** test whether coherent K/eU and Th/K anomalies align with independent gravity
  lineaments, while controlling for survey edges and surface effects.
- **Why it may capture an omitted feature / difference:** alteration can mark fluid pathways without a
  Quaternary surface rupture, but is indirect and confounded. GEMSDOE29 appears to have tried a
  radiometric arm; the primary result record is unretrieved (IR-EVIDENCE-01). Reconcile before execution.
- **Expected DTI / cost:** unknown; low-to-medium only after recovering the prior result and verifying
  preprocessing. Do not claim novelty before that audit.

## Rank 5 — H33-E expert-panel evidence dossier — METRIC-BLIND STRATEGY

- **Mechanism:** maintain provenance and independent geological corroboration for proposed traces. The
  official competition description says submissions are reviewed by an expert panel and the Final Prize
  Round uses an expanded label set to evaluate the selected submission; acceptance of any proposed trace
  is unknown.
- **Difference:** this is a review/selection strategy, not a raster transform and not an Initial-Round
  DTI improvement. It has no numerical expected DTI gain.
- **Cost:** low per candidate when provenance is captured during construction; potentially high downside
  if mapping evidence or semantics are misrepresented.

## Legacy variants and valid conclusions

- Old C1–C5 P1 deltas are preserved in `evidence/holdout33_legacy_catalogue_only.json` but are invalid for
  promotion because candidate/base construction was not fold-masked. Do not describe C1, C3, C4, or C5 as
  P1-validated or P1-refuted from that run.
- Their SGMC P2 deltas remain local comparisons against an independent compilation, subject to its vintage
  and scope. They are not contest scores and do not clear a slot.
- C2's corrected conditional P1 diagnostic is negative in all four folds. C2 is a research artifact only;
  no one-click file is currently recommended for competition submission.

The corrected evidence is `evidence/holdout33.json`. The exact C2 file passes only the project's local
format audit; it has no organizer score and no slot clearance.
