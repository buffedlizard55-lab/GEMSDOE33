# GEMSDOE33 hypothesis register (2026-10-04)

Five candidates, ranked by expected ΔDTI per engineering cost (machine-readable copy in
`registry/hypotheses.json`). Every candidate must pass the frozen P1/P2 proxy gate
(`scripts/run_holdout33.py` protocol, `evidence/holdout33.json`) before any weekly slot.
Ranges below are subjective priors that include zero; proxies are not scores.

## Rank 1 — H33-C2 stepover relay-bridge faults — IMPLEMENTED, PROXY-GATED (PASS)

* **Layers:** INGENIOUS Quaternary fault vectors (NBMG/USGS regional shapefile, NAD83,
  validated at 42.5% vertex proximity to the supplied catalogue); training band 18
  `iso_grav_anom_hg` (≥80th percentile within 200 m); scored h27-4 base.
* **Signature:** tip-to-tip approach of DISTINCT polylines (300–2500 m gap, ≤30° strike
  difference) ⇒ relay ramp; sparse 283 m bridge dots along the tip line, gated by the
  gravity edge.
* **Why off-catalogue:** stepovers/terminations/intersections concentrate unmapped
  synthetic/antithetic strands and blind tips (Faulds & Hinz 2015,
  https://www.osti.gov/servlets/purl/1110517); Desert Peak and Brady's are both hosted in
  fault step-overs. The catalogue lists major strands, not relay splays.
* **Difference from prior work:** GEMSDOE27's T-v2 filled gaps INSIDE the same polyline
  (230/345 links same-FID compiler artifacts; live −0.0028). C2 uses distinct-FID tip
  pairs + potential-field edge gate + pre-slot validation.
* **Result:** P1 mean ΔDTI +0.00043 (3/4 folds), P2 +0.00028 → PASS. Artifact:
  `docs/downloads/gems33-c2-stepover-relay-20261004-eb6bcf02361f.tif`.

## Rank 2 — H33-A analog-field transfer with measured domain-adaptation bound

* **Layers:** Dixie Valley field fault map (GDR #207, DOI 10.15121/1148837,
  https://gdr.openei.org/submissions/207 — GIS_Faults.zip, LiDAR + field-verified);
  Desert Peak–Brady's detailed map (NBMG OF 03-27, Faulds & Garside 2003); GDR #1288
  labelled grids (DOI 10.15121/1773692); shared 19-band feature layers resampled locally.
* **Signature (protocol, not transform):** pretrain/co-train on the analog field's dense
  drilling-verified catalogue; measure source→target divergence on shared feature layers
  with a classifier two-sample test (d_A distance); Ben-David et al. 2010
  (https://doi.org/10.1007/s10994-009-5152-4) bounds target error by source error plus
  divergence, licensing analog geometries as an independent validation set never touched
  by the GeoDAWN catalogue.
* **Why off-catalogue:** analog fields contain verified geometries of the exact omission
  class (blind/buried/low-scarp strands) that a regional compilation never captured.
* **Difference:** no campaign has used off-region labelled faults; the only labelled truth
  locally is the supplied catalogue and proxies derived from it.
* **Viability check:** GDR/OSTI pages confirmed reachable and public (links above); bytes
  themselves are egress-blocked in this sandbox (IR-NET-01) — fetch on any unrestricted
  machine. Viable, gated on one download step.

## Rank 3 — H33-B 2 m thermal-probe residual lineaments × gravity edges

* **Layers:** INGENIOUS 2 m temperature probe archive (mirrored locally; original GDR
  #1391, CC BY 4.0, https://gdr.openei.org/submissions/1391); training bands 5/18; USGS
  heat-flow residual (DeAngelo et al. 2022, DOI 10.5066/P9BZPVUC).
* **Signature:** aligned positive 2 m residuals above the de-convected background that
  co-align with a gravity-gradient edge — warm shallow ground along a buried conduit
  without a mapped scarp.
* **Difference:** GEMSDOE28 H35-1 used spring/well DISCHARGE POINTS and failed its
  far-field gate below a matched random control; H33-B uses the continuous probe field and
  a residual definition. Runnable next session from local mirrors.

## Rank 4 — H33-D radiometric K/Th alteration corridors (PARTIALLY PRE-EMPTED)

* **Layers:** GeoDAWN K/eU/Th grids (mirrored; native CC0 via USGS GeoDAWN release,
  https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and);
  gravity bands 13/18.
* **Signature:** argillic leaching drives K/eU and Th/K lows elongated along an
  independent gravity lineament — altered conduits with no Quaternary rupture.
* **Flag:** GEMSDOE29 ran a radiometric arm on seeds 280–289; its result record was not
  retrievable this session (IR-EVIDENCE-01). Reconcile before executing.

## Rank 5 — H33-E expert-panel dossier (Final Round optionality)

* **Mechanism:** the Final Prize Round re-scores every submission against an EXPANDED
  label set built by an expert panel reviewing all submissions
  (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
  Well-localised, independently corroborated traces that experts accept become new truth.
* **Strategy:** carry C1/C2 corroborated dots + SGMC off-catalogue traces as a
  panel-oriented dossier; its value is invisible to Initial-Round DTI.

## Refuted this session

* **C3 rung-3.0 re-pack of h27-4:** FAILS locally (P1 −0.00123, 0/4 folds; P2 −0.00814).
  GEMSDOE28's H36-1 re-pack passed because it re-packed the FULL H19-5 surface with a
  flank prune; re-packing an already-pruned set removes credit-bearing dots. Honest
  negative result — kept as a control, not shipped.
