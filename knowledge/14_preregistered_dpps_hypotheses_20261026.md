# Preregistered DPPS hypothesis slate — 2026-10-26 (GEMSDOE33, new lane)

**Frozen before any DPPS surface was built or scored.** Machine-readable twin:
`evidence/dpps_preregistration_20261026.json` (SHA-256 sidecar
`evidence/dpps_preregistration_20261026.sha256`). Campaign/host budget: **3 experiments**
(Exp 1 = quadrant screen, Exp 2 = diagonal-wedge confirmation, Exp 3 = production build +
uniqueness/format audit), ≤ 2 h wall time. No retuning after seeing any holdout result; a
negative result is a deliverable. All local validation numbers will be labelled
**HOLDOUT-DTI** (`evaluator_version="gems-segment-pooled-v1"`, pooled TPw/FPw/FNw,
α=0.2, β=0.8, 300 m triangular kernel, 60,988 withheld catalogue positives, 10 km
block-bootstrap 95% CI) or **OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)** for historical
DrivenData figures. No organizer receipt exists in this repo for any historical score.

## Why a new lane is required (evidence boundary)

- The 9-site reported peak `GEMSDOE32 h33-h33-2-b2-...-zeros` (**0.2778\***) was reproduced
  in-repo **pixel-exactly** as deletion-only pruning of `GEMSDOE28/31 H27-4` (44,090 → 40,199 →
  37,654 dots; see `knowledge/13_focus_forensics_g32_proof_and_a33_r2_results_20261026.md`).
  Its mechanism is removal of ≤200 m catalogue-halo scarp-slope dots (FPw reduction), **not**
  new fault discovery. Copying/perturbing it trips the duplicate gate (ρ=0.9676, 100% within 3 px vs H27-4).
- `A33-R2-CSHT` (this repo, 2026-10-26) beat the `B1_regional` HGB incumbent 8/8 holdout folds
  (**HOLDOUT-DTI 0.136716** screen / **0.131169** confirm) and its placed dots were unique, but its
  **pre-placement HGB surface peaks duplicated sibling `GEMSDOE30-MSDB1`** (91.11% within 3 px), so
  verdict = duplicate / do-not-submit. Lesson: any HistGradientBoosting surface supervised on
  `labels.tif` converges to the same peaks as every sibling HGB lane.
- Therefore DPPS uses **zero learned weights and zero catalogue geometry in its surface**:
  a deterministic geophysics/gemorphology operator. Catalogue pixels enter only as the
  fold-visible exclusion mask at emission time (and the full catalogue in production).

## Ranked candidate hypotheses (3–5, not previously executed as a primary lane)

| Rank | Hypothesis | Layers (exact cached channels) | Physical signature / transform | Why it can catch faults missing from USGS/INGENIOUS | Named non-fault mimic | Difference vs everything in this repo | Expected DTI rank / cost |
|---|---|---|---|---|---|---|---|
| **1 — EXECUTE** | **DPPS: Dip-Projected Persistence Scarp.** Surface traces of dipping Basin-and-Range normal faults are laterally offset updip from their buried basement gravity step by `z·cot δ`; requiring ≥1.5 km along-strike scarp persistence plus dip-projected gravity support separates true fault scarps from isolated scarp-like pixels. | `lid_step_max`, `lid_lapneg_max`, `lid_ex_max`, `lid_valid` (USGS 3DEP 1 m LiDAR derivatives), `det_elev_curv4`, `det_elev_laps4`, `det_elev_coh` (100 m DEM), `iso_grav_anom_hg`, `depth_to_base_surf` (GeoDAWN/competition stack) | (i) rank-blended scarp strength with DEM-flexure fallback in the LiDAR void; (ii) 8-orientation, 15-px (1.5 km) line-mean persistence (max over orientations); (iii) variable dip-projection warp of the gravity horizontal-gradient field along `+∇(depth-to-basement)` by `clip(z·cot60°/100 m, 0, 15) px`; (iv) fixed geometric fusion; (v) 300 m CELF emission. | Catalogue mapping follows exposed range fronts. Under 0.5–2 km of basin fill the gravity crest sits basinward of the surface trace, so every co-located pixel product (all HGB lanes, H33-6, G33) puts support on the wrong cell; unmapped piedmont/basin traces are exactly where the offset is largest. Persistence removes short cultural/erosional scarps that pixel classifiers emit. | Prograding alluvial-fan toes and Lake Lahontan shoreline benches over buried pediments (long, linear, gravity-supported, no Quaternary slip). | `A33-R2-PFRT` was preregistered as a *reserve* in R2 but **never executed**; no prior lane warps any field by a dip-offset vector field, none uses an along-strike line-persistence operator as the primary score, and DPPS has **no supervised classifier** (vs A33-L1/CSHT/Round-3 HGBs and G33's static conjunction). | Highest expected ΔDTI of the slate; low–medium CPU (deterministic convolutions/warp, no per-fold fitting for the candidate). Viable now: all 9 channels are in the pinned cache restored & SHA-verified 2026-10-26 (17/17 inputs). |
| 2 — reserve | **HMDT: Hydrothermal magnetite-destruction × clay-cap signed dipole.** | `rtp`, `ext_TMI_up150`, `tmi_vg`, `cond_surf`, `cond_surf_gms2`, `iso_grav_anom_hg`, `geod_dilaterate` | Signed cross-gradient `∇cond · ∇(TMI_up150 − RTP)` gated by gravity-gradient crests in dilational strain zones. | Fault-hosted hydrothermal flow destroys magnetite and precipitates conductive smectite along the damage zone, erasing scarp competence — mappable by geophysics where photo/LiDAR mapping fails. | Saline playa evaporites over non-magnetic lacustrine tuffs. | Preregistered in R2, never executed; H33-6 used unsigned edge-rank products without polarity or fluid conditioning. | Medium ΔDTI; low cost; viable on pinned cache. Execute only in a future campaign (would exceed the 3-experiment budget here). |
| 3 — reserve | **RDX: Radiometric discordance lineaments.** | `ext_ThK`, `ext_UK`, `ext_UTh`, `rad_K`, `rad_Th`, `rad_U` (USGS GeoDAWN airborne radiometrics) | Oriented persistence of `∇(Th/K) × ∇(U/K)` discordance: K-metasomatism/argillization along fault conduits moves K (and U) while Th stays immobile, so ratio gradients are discordant only along fluid pathways. | Alteration halos along blind geothermal conduits can be the only surface expression of a fault with no scarp and no magnetic contrast. | Lithologic contacts between felsic intrusives and volcanics (bulk K/Th contrast without faulting). | Radiometric channels have only been HGB inputs; never a dedicated signed ratio-discordance detector. | Medium–low ΔDTI; low cost; viable on pinned cache. |
| 4 — reserve | **EQA: Earthquake-alignment tensor ridges.** | `ieq_n100a15`, `deq_n100a15`, `geod_2ndinv`, `geod_shearrate` | Structure-tensor ridge (`_ridge`/`_coh` transforms) of the azimuth-15° earthquake density fields: microseismicity lineates along blind active faults before a scarp forms. | A seismogenic blind fault under basin fill produces aligned epicentres while remaining invisible to scarp/gravity mapping. | Volcanic swarm seismicity and geothermal production/injection-induced seismicity. | Strain channels were HGB inputs; the a15 alignment fields were never ridge-detected as a primary surface. | Low–medium ΔDTI (100 km smoothing limits 100 m precision); low cost; viable on pinned cache. |
| 5 — **blocked/deferred** | **LSO: Lahontan shoreline-offset terraces.** | USGS 3DEP 1 m DEM tiles listed in pinned `dem_links.json` (541,953 B, SHA in `registry/owner_mirror_input_pins.json`) + `det_elev` | Contour-parallel paleoshoreline bench tracking; a bench vertically offset/terminated across a lineament is a direct Quaternary-slip marker. | Shoreline benches are regionally continuous datums; their offset proves post-Lahontan slip on piedmont faults too subtle to map as scarps. | Wave-cut benches segmented by fan-head trenching/drainage incision. | Never attempted in any GEMSDOE lane. **Source check:** USGS 3DEP (https://www.usgs.gov/3d-elevation-program, public domain) — the tile index is pinned locally, but tile payloads are not in the 17-input contract and cannot be fetched inside this campaign's budget; named **not viable for this campaign**, viable as a future dedicated ingest. | Potentially high ΔDTI but high ingest/implementation cost; deferred honestly rather than half-built. |

## Frozen DPPS operator (no free parameters after this file)

Notation: `rank(X)` = empirical CDF (average tied ranks / N) of finite footprint cells, in [0,1].

1. `S_scarp = mean(rank(lid_step_max), rank(lid_lapneg_max), rank(lid_ex_max))`;
   `S_flex = mean(rank(|det_elev_curv4|), rank(|det_elev_laps4|))`;
   `S = S_scarp` where `lid_valid > 0` and all three LiDAR channels are finite, else `S_flex`;
   `S = 0` outside the footprint. (Fixes `IR-33-LIDAR-VOID-01` explicitly: void cells never
   inherit smeared scarp values.)
2. **Persistence:** orientations `u ∈ {(1,0),(0,1),(1,1),(1,−1),(2,1),(1,2),(2,−1),(1,−2)}`
   normalized; integer offsets `round(t·u)`, `t = −7..7` (deduplicated); `P = max_u mean_t S(y+Δy, x+Δx)`
   computed on an edge-padded grid; `P = 0` outside footprint.
3. **Dip projection:** `z = clip(depth_to_base_surf, 0, ∞)` smoothed by normalized Gaussian
   convolution σ=3 px; `g = ∇z` (central differences), `û = g/(|g|+1e-12)`;
   `d_px = clip(z·cot(60°)/100, 0, 15)`; `G_proj(y,x) = rank(iso_grav_anom_hg)` bilinearly sampled
   at `(y + d·û_y, x + d·û_x)` (the buried crest basinward of the surface trace).
4. **Fusion (fixed):** `surface = rank(P) · (0.6 + 0.4·rank(G_proj)) · (0.7 + 0.3·rank(det_elev_coh))`,
   clipped to [0,1], 0 outside footprint, finite everywhere.
5. **Emission:** eligible = footprint ∩ valid-fold ∩ `{dist(visible catalogue) > 2 px}`;
   `csht_transfer.celf_emit_300m(surface, eligible, budget, min_self_spacing_px=2.5)`
   (pinned shared code, defaults unchanged). Fold budget `round(37,654 · valid/footprint)`;
   production budget exactly 37,654 dots with the full catalogue as the >2 px exclusion.

## Frozen evaluation contract

- **Canary first:** `SegmentHoldout.canary` on all 9 input channels; any two-sided AUC > 0.90
  aborts the campaign before scoring (leakage until proven otherwise).
- **Exp 1 screen:** `SegmentHoldout(buffer_px=15)` quadrants (`quadrant-buffered-15px-v1`).
  Candidate = DPPS+CELF. Controls, same budgets: **B1_regional** (in-run
  `analog_invariant.fit_regional_expert` + dot-thin 2.8, the repo incumbent system),
  **CTRL-PIXEL** (surface `S` + identical CELF emission — isolates persistence+projection),
  **matched_random**.
- **Exp 2 confirmation:** `DiagonalSegmentHoldout(buffer_px=20)`
  (`diagonal-wedge-buffered-20px-confirm-v1`), frozen now, before screen results exist.
  Candidate vs B1_regional and CTRL-PIXEL.
- **Exp 3 production:** full-footprint surface → 37,654 CELF dots → strict saved-byte audit.
  Primary file = **zeros outside** (whole array finite in [0,1]; this is the variant that cannot
  trigger the owner-reported portal error *"Predicted values must be in range [0, 1]"* from NaN
  handling); NaN-outside twin written for the official-text convention.
- **Uniqueness (surface AND final dots)** vs an expanded 25-raster registry: the 21 pinned
  rasters in `registry/focus_rasters_20261026.json` **plus** local A33-R2-CSHT, G33,
  Round-3 DA-HGCM and H33-R3-invariant zeros twins. Stop/duplicate if |Spearman ρ| > 0.90 or
  > 70% of candidate (preview or final) dots lie within 3 px of any single registry raster.
  Surface preview = top-37,654 raw eligible surface pixels before any spacing operator.
- **Promote (eligible to submit) iff ALL hold:** canaries pass; screen pooled HOLDOUT-DTI > B1
  and > CTRL-PIXEL with paired 95% CI vs B1 strictly > 0 and ≥ 3/4 fold wins vs B1; confirmation
  likewise > B1 with paired CI > 0 and ≥ 3/4 folds; surface and final-dots uniqueness pass vs
  all 25; strict format audit passes on saved bytes; note ≤ 140 chars; ≤ 3 experiments.
  Otherwise verdict = **negative/duplicate** and the site must say OK TO SUBMIT: NO.
- Recorded context (not paired-recomputable here): A33-R2-CSHT screen **HOLDOUT-DTI 0.136716** /
  confirm **0.131169** (duplicate-blocked on its surface). DPPS pooled values will be printed
  beside them without claiming a paired comparison.

\* All historical DrivenData numbers are OWNER-REPORTED (NOT ORGANIZER-CONFIRMED).
Official sources: DrivenData #306 overview/problem/rules
(https://www.drivendata.org/competitions/306/competition-doe-gems/ ,
…/page/967/, …/rules/), reference solution
(https://github.com/drivendataorg/gems-prize-reference-solution), USGS GeoDAWN
(https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
GBCGE INGENIOUS (https://gbcge.org/current-projects/ingenious/), EPSG:32611
(https://epsg.io/32611), Tversky index (https://en.wikipedia.org/wiki/Tversky_index).
