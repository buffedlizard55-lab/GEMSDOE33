# Ranked geological hypothesis slate — 2026-10-29

**Historical-order caveat (must be read first).** This slate was written **after** the deployment-density audit
(`knowledge/34`) and **before** any candidate code. It is a ranked plan, **not** a clean preregistration. No candidate
below has been implemented or scored. No numeric DTI gain is forecast. Ranks are qualitative: expected discriminative
value against implementation cost and overlap with prior lanes.

**Deployment-density rule.** Any candidate must be scored at deployment density (37,654 dots, 0.7287%), with a
matched-random control at that density and a paired CI (`knowledge/34`). Its floor is HOLDOUT-DTI **0.0737**.

**Layers checked against the restored mirror.** Band names were read from `data/training_features.tif` (19 float32 bands,
EPSG:32611, 100 m, 3730 × 3292), not from memory. Band list: `mag_anom, rtp, tmi_hg, geod_2ndinv,
iso_grav_anom_slope, tc, geod_shearrate, geod_dilaterate, tmi_vg, deq_n100a15, iso_grav_anom_vg, det_elev,
iso_grav_anom, tmi, depth_to_base_surf, ieq_n100a15, cond_surf, iso_grav_anom_hg, det_elev_slope`.

**Overlap check.** Each candidate was checked against the repo's prior slates by keyword search (`knowledge/`, `src/`).
Keyword search is weak evidence; a near-duplicate can use different words.

## Ranked slate

| Rank | Candidate | Layers and physical signature | Why it could find a fault missing from the USGS/INGENIOUS catalogue | Mimics to test | Prior-lane overlap | Cost | Data status and official source check |
|---|---|---|---|---|---|---|---|
| **1** | **H-MAGDEPTH** — step in top-of-crust magnetic source depth across a fault-parallel line | Official "top-of-crustal magnetic source depth estimate" (from the official feature list). **Not present** in the mirror's 19 bands. Signature: a depth step (shallow block against deep block) lying along a regional structural grain. | A basement offset buried under cover has no surface trace, so it is absent from the Quaternary catalogue, yet can shift magnetic source depth. | Shallow intrusive or volcanic bodies; magnetite-rich lithologic contacts; sediment-thickness changes. | **No prior lane found** for "source depth" (keyword search: 0 hits). Related but different: TMI gradients (`tmi_hg`, `tmi_vg`), tilt (`tc`), phase congruency (`knowledge/30`). | Medium. Needs a depth estimator, and its validity depends on which estimator the organizer used. | **BLOCKED.** (a) The mirror lacks the band, and so does the organizer's own 19-band listing in its reference notebook (IR-33-20261029-BAND-DEPTH-01). (b) The official GeoDAWN data release (DOI 10.5066/P93LGLVQ, CC0) lists magnetic and radiometric grids and flight lines; its summary does not list a source-depth product ([USGS page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), fetched 2026-10-29). (c) Official `training_features.tif` is login-walled on DrivenData; the sandbox cannot fetch it. **Unblock:** a human download of the official file, or the organizer's band documentation. A self-derived depth grid from the mirror's 100 m `tmi` would be a *different* feature and must be labelled as such. |
| 2 | H-STRAINRIDGE — orientation-coherent ridges of `geod_shearrate` and `geod_dilaterate`, computed without the catalogue | `geod_shearrate`, `geod_dilaterate`, `geod_2ndinv`. Signature: linear strain localisation, coherent in orientation across scales. | Strain localisation can mark active shear zones before a mapped trace exists. | Irrigation and reservoir loading; survey-geometry artefacts from the geodetic product. | **High.** Strain and seismicity were tested in `S33-SEISDIL` and `analog`/`csht` lanes (`knowledge/13`, `knowledge/07`). | Low. All data in hand. | In hand (mirror). Upstream geodetic source not independently verified in this session. |
| 3 | H-MAGLOW — linear magnetic lows from demagnetisation along fault damage zones | `tmi`, `rtp`, `mag_anom`. Signature: elongated low lineament, negative curvature, consistent with hydrothermal demagnetisation. | Demagnetised damage zones can be buried and unmapped. | Lithologic magnetic-low contacts (for example, sediment-filled basins). | **High.** A negative-lineament detector was tested by the owner on GEMSDOE24 (`GVC1`, 0.0859\*), and its lineaments fired on lithologic contacts. | Low. | In hand. Owner-reported result is not organizer-confirmed. |
| 4 | H-RADKTH — K/Th ratio edge along strike from the radiometric channels | `rad_K`, `rad_Th` (in the cached stack); `ext_ThK`, `ext_UK`. Signature: a directional edge in the K/Th ratio, indicating alteration. | Alteration halos mark fluid pathways without surface scarp. | Soil and lithology changes; radon background (the GeoDAWN product states a radon-background correction). | **Partial.** `A33-R5-THKCOND` (K/Th × conductivity, negative) is the closest prior lane. | Low. | In hand. GeoDAWN radiometric grids are the official source ([USGS](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)). |
| 5 | H-SPRINGCOLL — collinear chains of GDR wellspring cells | `data/gdr_wellspring_in_footprint.csv` (27,092 lines, including repeat chemistry records). Signature: at least 3 springs aligned within a tolerance azimuth. | Springs sit on permeable fault strands that are not mapped. | Drainage and valley alignments; irrigation lines. | **High.** Thermal-vent seeds were used in `csht_transfer` and `lchc`. `A33-R3-LCHC` (least-cost connectivity, HOLDOUT-DTI 0.0437) lost to its control. | Low. | In hand. Schema check: the file carries `dist_known_fault_px`, which the repo flags as blocked for leakage (`IR-33-CSV-DIST-FAULT-01`). **Must not** be used as a feature. |

## Recommendation

1. **Unblock rank 1 first**, because it is the only candidate with no prior lane and a distinct physical signature. The
   blocker is data access, not compute. A human download of the official `training_features.tif` (login on DrivenData)
   would settle whether the official band exists in the form the brief describes. Nothing in this sandbox can fetch it.
2. **Do not spend a lane on ranks 2 to 5 without a new distinguishing element.** Each one overlaps a prior negative lane.
   Expect the same surface duplicate that `knowledge/22` (FSML-PU) and `knowledge/30` (PCSUP) reported.
3. Any new candidate is evaluated at deployment density against its matched-random control, with a paired CI.

## What is explicitly not claimed

- No candidate here is validated, scored or uniqueness-tested. No raster was written.
- No leaderboard score is estimated for any candidate.
- The "no prior lane" finding for H-MAGDEPTH is a keyword result, not a full literature search.
