# GEMSDOE33 — New geological hypothesis slate (2026-10-27)

**Purpose:** standing-prompt Rule 4 — before implementing any candidate, write and rank 3–5 genuinely new geological hypotheses. This slate preregisters the candidates, their layers, physical signatures, catalogue-missing rationale, distinction from prior repository work, qualitative expected-improvement rank, implementation cost, and a specific free official source + availability check for any idea needing new data. No numeric DTI improvement is invented; values can only come from a fold-safe holdout run. This document is the preregistration for Experiment 1 (A33-R5-THKCOND); its SHA-256 is recorded in the run card.

**Protocol constraints honored:** single method lane per session — this session's lane is the radiometric/alteration detector below; all feature derivations consume fold-visible catalogue only; leakage canary AUC > 0.90 halts; no weekly slot is spent unless screen + independent confirmation beat the fold-safe incumbent with a strictly positive paired CI; no projection of HOLDOUT-DTI to the DrivenData leaderboard; all historical focus-site scores remain OWNER/USER-REPORTED, not organizer-confirmed.

## Candidate 1 (selected — run this session): A33-R5-THKCOND

**Rank:** 1 (top viable candidate: new physical axis, lowest implementation cost, all inputs staged, label-free).

**Layers:**
- `data/geodawn_extensions_u8.tif` bands `ThK` and `UK` (GeoDAWN airborne radiometric thorium/potassium and uranium/potassium ratios; pinned owner mirror, SHA-256 verified; grid 3730×3292, EPSG:32611, 100 m — matches template).
- `training_features.tif` bands `cond_surf`, `depth_to_base_surf`, `iso_grav_anom_hg` (shared 121-channel cache).
- Catalogue mask: `labels.tif` (public USGS/INGENIOUS faults) used ONLY as fold-visible truth/hidden-segment mask per SegmentHoldout; never as a detector input.

**Physical signature targeted:** argillic/clay alteration concentrates K and Th (elevated Th/K) above a conductive geothermal reservoir (high `cond_surf`), where the basement is shallow (`depth_to_base_surf` low) at a gravity-mapped basin-margin fault edge (high `iso_grav_anom_hg`). Surface score = normalized product of exceedance gates over train-fit percentiles. This is an alteration × conduit × cover-thickness × structural-edge signature, i.e. a concealed hydrothermal plumbing system rather than a mapped scarp.

**Why it may catch faults missing from USGS/INGENIOUS:** the public catalogue is dominated by mapped Quaternary surface traces; blind or cover-buried faults controlling geothermal upflow show no surface scarp and are absent from the catalogue. Radiometric alteration and MT conductivity are independent physical measurements that do not read the catalogue at all.

**Named non-fault mimic:** saline playa/evaporite surfaces and nonmagnetic lacustrine tuff can also yield high radiometric K/Th and near-surface conductivity without a throughgoing fault (same failure mode noted for HMDT clay-cap work in knowledge/17).

**Distinction from prior repository work:** no lane tried in this repo uses radiometric Th/K as a leading detector term. CSHT used `ext_TMI_up150` inside a 34-channel HGB blend; HMDT used an unsigned `cond_surf × TMI-gradient` cross-gradient; DPPS used LiDAR scarp persistence + dip-projected gravity; S33-SEISDIL used strain/seismicity. THKCOND is the first label-free radiometric-primary surface and shares zero pixels with any registry raster by construction.

**Expected DTI improvement:** qualitative, moderate — new independent physical axis likely complementary to gravity/LiDAR lanes; not estimable numerically before the holdout run. Could still lose to the catalogue proxy because hidden truth is not catalogue truth.

**Implementation cost:** low — band algebra + percentile gates + shared CELF-300 m emission; no model fitting.

**Data/source availability check:** `geodawn_extensions_u8.tif` restored and SHA-256 verified 2026-10-27 (all 17 pins). Official context: [USGS GeoDAWN data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). No new download needed. **VIABLE NOW.**

## Candidate 2 (deferred — blocked): A33-R5-COULOMB

**Rank:** 2 on mechanism distinctness, not implementable safely this session.

**Layers:** USGS Quaternary fault trace geometry (strike, dip, rake, slip, depth, width), `depth_to_base_surf`.

**Signature:** Okada elastic half-space Coulomb failure-stress change ΔCFS on receiver planes from characteristic events on mapped sources; positive ΔCFS lobes beyond mapped traces flag blind splays/stepovers.

**Why it may catch catalogue-missing faults:** stress transfer activates synthetic/antithetic structures not mapped at the surface; distinct from proximity halos because it requires dislocation geometry and elastic stress transfer.

**Mimic:** intrusive/caldera margins and spatial frictional heterogeneity.

**Distinction:** first physics-based static-stress lane; all repo lanes are geometric proximity or supervised catalogue transfer.

**Blocker:** staged `gdr_qfaults_traces.csv` (1,126 rows) has centroid UTM + slip rate + recency + dip direction + slip sense but **no vertices or strike**; `qfaults_v2_in_footprint.json` (32,589 vertices) declares a geographic lon/lat metadata bbox whose numeric x/y ranges do not align with the EPSG:32611 template bounds (x 243,350–572,550; y 4,135,550–4,508,550); CSV centroids also fall outside template bounds. A centroid-only approximation would not be Okada/Coulomb stress transfer and could create arbitrary artifacts. **Unblock condition:** obtain trace polylines with a declared CRS aligned to EPSG:32611 (official review source: [USGS Quaternary Fault and Fold Database via ScienceBase](https://www.sciencebase.gov/catalog/) or DOE [GDR #1391](https://gdr.openei.org/submissions/1391)), implement and unit-verify Okada ΔCFS, then run the surface duplicate screen (catalogue-derived dots risk >70% 3-px overlap → duplicate guard).

**Cost:** moderate–high; data not safely usable as staged.

## Candidate 3 (blocked — new external data required): A33-R5-CURVTRACE

**Rank:** 3.

**Layers:** raw 1 m USGS 3DEP DEM tiles (not among the 17 pinned inputs).

**Signature:** multi-azimuth profile/plane curvature plus orientation-tracked curvilinear scarp continuity over ≥1.5 km at 1 m resolution.

**Why it may catch catalogue-missing faults:** young, low-relief fault scarps with sub-100-m expression are generalized away from the catalogue; trace continuity at 1 m resolves them.

**Mimic:** Lake Lahontan shoreline benches, fluvial terrace risers, road/canal berms.

**Distinction:** repo LiDAR is a 12-band 100 m aggregate (`lidar_scarp_features_u8.tif`, 2 m processing); CURVTRACE targets raw 1 m morphology — adjacent in idea to line-localized work but different scale and input.

**Source/availability check:** official free source [USGS 3DEP](https://www.usgs.gov/3d-elevation-program). **Not obtainable in this session:** the 3DEP tile service host is not in the sandbox outbound allowlist; no tile download was attempted; 100 m aggregation cannot be re-interpolated to claim 1 m evidence. Deferred until tiles are staged and coverage/license audited.

## Candidate 4 (viable, deferred by budget): A33-R5-BASESTEP

**Rank:** 4.

**Layers:** `depth_to_base_surf` first derivative (basement step/flexure), `ext_TMI_up150` (deep magnetic basement), `cond_surf`.

**Signature:** sharp basement-depth step coincident with a conductive-cover edge = listric fault sole beneath piedmont cover.

**Why it may catch catalogue-missing faults:** buried listric faults sole into basement steps with little surface expression; catalogue maps Quaternary traces, not blind listric soles.

**Mimic:** prograding fan toes and buried pediments (same as CURVTRACE).

**Distinction:** uses depth-to-basement geometry as the leading term — not tried as a primary detector in any repo lane.

**Cost:** low–medium; all inputs staged. **Deferred by this session's 3-experiment / 2-hour budget**, not by data availability.

## Candidate 5 (blocked): A33-R5-PALEOTEMP

**Rank:** 5 (not untried in concept — paleotemperature was A33-R2-PALEOTEMP — deferred).

**Layers:** DOE GDR #1391 2 m shallow-temperature probes and paleosinter/tufa inventory, joined with `cond_surf` and geophysical edges.

**Signature:** relict sinter/tufa and shallow thermal anomalies distal from active springs mark dormant conduits.

**Mimic:** paleochannel thermal outflow distal from a feeder fault.

**Blocker:** the named probe/sinter payload is not among pinned inputs; GDR #1391 egress was blocked in prior sessions and the vents CSV shipped in the mirror carries the hard-blocked column `dist_known_fault_px` (IR-33-CSV-DIST-FAULT-01), so it cannot be used as-is. Official listing: [DOE GDR #1391](https://gdr.openei.org/submissions/1391) — availability/license/schema not audited in this checkout. Deferred.

## Selection for Experiment 1

**Selected:** A33-R5-THKCOND (rank 1 viable). It is the only candidate that is (a) genuinely untried in this repo, (b) fully implementable from SHA-verified staged inputs, (c) label-free with low duplicate risk, and (d) completable within the session budget.

**Holdout design:** `vendor/gems24_template.holdout.SegmentHoldout(buffer_px=15)`, quadrant folds, whole-segment hide-and-recover, pooled DTI `gems-segment-pooled-v1` (α=0.2, β=0.8, 300 m triangular kernel), paired block-bootstrap CI vs matched-random control; single-feature leakage canary; full-footprint CELF-300 m emission at 37,654 dots; pre-placement surface + final-dot duplicate screen vs the 21-raster registry in `registry/focus_rasters_20261026.json`; saved-byte writer + strict format audit via `scripts/submission_writer.py` / `scripts/validate_submission.py`.

**No slot is requested:** promotion requires screen + confirmation vs B1_regional with strictly positive paired CI and ≥3/4 fold wins each, plus both uniqueness gates. A negative result is published as an honest deliverable.
