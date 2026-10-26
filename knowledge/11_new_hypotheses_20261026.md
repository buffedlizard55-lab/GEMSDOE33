# New (untried) hypothesis slate — GEMSDOE33, 2026-10-26

**Status:** planning record, not preregistration and not validation. No numeric DTI improvement forecasts are asserted (ranking is qualitative upside vs implementation cost). Every hypothesis below is untried in this repo; none was trained or selected in this session. The top candidate (H-N1, the G33-HA lane) WAS implemented and evaluated on the spatially blocked holdout — it failed (pooled confirmation ΔDTI −0.0907, 0/4 folds; CI [−0.1210, −0.0594]) and is reported as a negative deliverable. All inputs named are free official sources; obtainability checks show which are usable now and which are blocked pending payload retrieval.

Inputs already in the checkout (owner-mirror, hash-pinned, NOT organizer-authenticated): `training_features.tif` (19 GeoDAWN bands), `labels.tif` (catalogue), `lidar_scarp_features_u8.tif`, `geodawn_rad_u8.tif`, `geodawn_extensions_u8.tif`, `derived_sgmc_faults_100m_u8.tif`, plus the 121 cached feature channels.

---

## H-N1 (tried — NEGATIVE) Tilt ≈ 0 × gravity edge × LiDAR coherence, sparse off-catalogue dots

- **Layers:** band 6 `tc` (tilt/total curvature), band 18 `iso_grav_anom_hg` (gravity horizontal gradient), `lid_coh100` (LiDAR scarp coherence), `lid_step_max` (LiDAR step). All from the 121-channel cache.
- **Physical signature:** near-vertical potential-field contact (`tc` ≈ 0) co-located with a strong gravity-gradient edge and a coherent linear LiDAR scarp break — a concealed or subtle fault signature needing no preserved surface trace.
- **Why it targets catalogue-absent faults:** blind or poorly mapped structures can juxtapose susceptibility/density/basement without a Quaternary scarp in USGS/INGENIOUS; the conjunction is deliberately sparse to limit false-positive mass under DTI (α=0.2 per isolated dot).
- **Difference from repo:** no H19-5 surface, no catalogue-proximate dots (H19/H27/D2.8/B2 family), no H33-6 gradient-vector alignment or matched-budget reallocation; catalogue enters only as a fold-visible ≥2 px exclusion mask.
- **Result (holdout):** screen ΔDTI −0.09235, confirmation ΔDTI −0.09070 (0/4 folds positive), descriptive CI [−0.1210, −0.0594]; no channel stand-alone AUC > 0.90 (no signal, not leakage). Unique vs all 12 pinned registry rasters (max ρ 0.0046; max 29.9% of dots within 3 px). TIFF built and published as `gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7` — format-valid, **NOT cleared to submit**.
- **Named non-fault mimic:** lithologic contacts, basin margins, alteration fronts and surficial Quaternary lineaments.
- **Cost:** low (cached channels only). **Expected improvement:** qualitative low on this proxy; negative result delivered.

---

## H-N2 Catalogue-flank frontier dots with H19-5 corroboration

- **Layers:** catalogue mask `labels.tif` (fold-visible), `h19_5_nan.tif` ridge emission.
- **Physical signature:** dots placed 2–3 px (200–300 m) from visible catalogue flanks — inside the 300 m triangular kernel reach of held-out catalogue extensions — AND on the H19-5 ridge; thinned at 2.8 px.
- **Why it targets catalogue-absent faults:** on the catalogue proxy, held-out segments abut visible ones, so frontier dots at kernel reach can earn true-positive weight on nearby held-out pixels; H19-5 selects the geophysically live flanks. In the live competition this same geometry targets unmapped parallel/stepover strands adjacent to mapped traces.
- **Difference from repo:** B2/H27/H38 DELETE near-catalogue dots; H-N2 ADDS only kernel-reach near-catalogue dots with H19-5 corroboration — the opposite pruning direction; not implemented anywhere in this repo. **Duplicate risk:** likely high overlap with the B2/H27-4 registry rasters; a rho > 0.90 or >70% within-3px check against the registry is mandatory before any emission, and a match must be logged as a duplicate and stopped.
- **Cost:** low. **Expected improvement:** qualitative moderate on the proxy; untested.

---

## H-N3 Signed strain-lobe across conductor–basement edge

- **Layers:** band 7 `geod_shearrate`, band 8 `geod_dilaterate`, band 17 `cond_surf`, band 15 `depth_to_base_surf`, band 18 `iso_grav_anom_hg` (cached).
- **Physical signature:** a signed strain/shear-rate asymmetry across a sharp conductivity or basement-depth edge, co-located with a gravity horizontal-gradient edge — not raw strain or conductivity amplitude.
- **Why it targets catalogue-absent faults:** a blind, permeable fault can host mechanical strain and fluid alteration (conductor) above a basement offset without a surface Quaternary trace; the signed edge rule is specific to the juxtaposition, not to either field alone.
- **Difference from repo:** related to DILCOND/SRCOH strain screens in owner history (reported weak); the exact signed strain-lobe × edge conjunction is not in the local builders and needs a direct ablation before trust.
- **Named non-fault mimic:** conductive sedimentary contacts, alteration fronts, basin-edge gravity contrasts.
- **Cost:** low–medium (cached channels). **Expected improvement:** qualitative low–moderate.

---

## H-N4 2 m shallow-temperature probe anomaly proximity (GDR #1391 INGENIOUS)

- **Layers:** INGENIOUS 2 m temperature probe points/wells (DOE GDR submission 1391 probe ZIP, listed 1.03 MB) rasterized to the grid, combined with GeoDAWN bands 3/9/13/14/15/18.
- **Physical signature:** subtle shallow near-surface thermal anomalies offset from mapped fault traces, marking blind conduits.
- **Why it targets catalogue-absent faults:** probe temperatures can reveal concealed upflow where the surface fault compilation has no trace; used as proximity evidence, not as temperature truth.
- **Difference from repo:** no subsurface temperature source is used in any local builder.
- **Named non-fault mimic:** shallow groundwater/surface-expression effects unrelated to faults.
- **Source & obtainability check:** official page https://gdr.openei.org/submissions/1391 (public, CC BY 4.0; probe ZIP listed). Previous attempts to retrieve gdr.openei.org payloads from this sandbox failed (TLS); schema, seasonal/sampling metadata, and footprint coverage are UNVERIFIED. **BLOCKED until the official ZIP is fetched, hashed and audited; not viable now.**

---

## H-N5 ComCat focal-plane orientation × potential-field lineaments

- **Layers:** USGS ANSS ComCat focal mechanisms (event location + nodal-plane strike/dip/rake) + bands 3 `tmi_hg`, 9 `tmi_vg`, 19 `det_elev_slope` (cached).
- **Physical signature:** candidate magnetic/geomorphic lineaments whose azimuth/dip direction is mechanically compatible with nearby reviewed focal-plane solutions; earthquake density is NOT used as a fault label (nodal-plane ambiguity preserved).
- **Why it targets catalogue-absent faults:** focal mechanisms constrain active seismogenic slip planes from waveform radiation, independent of the surface trace compilation; a compatible lineament absent from USGS/INGENIOUS is a blind-structure candidate.
- **Difference from repo:** already described as earlier H33-2 (not new in concept), never implemented or harvested locally; differs from band 16 earthquake intensity/density by using per-event plane geometry.
- **Named non-fault mimic:** non-tectonic lineaments, nodal-plane ambiguity, aftershock clouds without structures.
- **Source & obtainability check:** USGS ANSS ComCat docs https://earthquake.usgs.gov/data/comcat/index.php and FDSN API https://earthquake.usgs.gov/fdsnws/event/1/ (free, official). A count query previously worked (6,168 products M≥2.5 in footprint); a full product extract was not staged (retrieval TLS failures). **Partially blocked: viable only after a pinned extract and product audit.**

---

## Ranking (qualitative, no numeric DTI forecasts)

| Rank | Hypothesis | Expected DTI improvement (qualitative) | Cost | Data status |
|------|------------|----------------------------------------|------|-------------|
| 1 (tried) | H-N1 tilt-gravity-LiDAR coherence | negative on proxy (−0.0907 ΔDTI) | low | local, usable |
| 2 | H-N2 catalogue-flank frontier + H19-5 | moderate (proxy); duplicate risk high | low | local, usable |
| 3 | H-N3 signed strain-lobe × conductor edge | low–moderate | low–medium | local, usable |
| 4 | H-N4 2 m probe proximity (GDR 1391) | moderate (coverage-dependent) | medium–high | **blocked** — payload not obtainable here |
| 5 | H-N5 ComCat focal-plane orientation | low–moderate | medium | **partially blocked** — API works, extract not staged |

**Next-work note:** H-N2 is the next runnable candidate but carries a high duplicate-lane risk versus the B2/H27-4 registry rasters; the uniqueness screen (rho ≤ 0.90, ≤70% within 3 px) must be run on its final dots before any emission, and a positive screen result must be logged or the arm stopped per the lane protocol.
