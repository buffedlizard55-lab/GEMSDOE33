# Fresh hypothesis slate — 2026-10-25

**Status: frozen before implementation; no candidate was implemented or evaluated.** These are three
research hypotheses for the next permitted round, not submission recommendations. The rank is a
qualitative priority, not a numeric HOLDOUT-DTI estimate or a leaderboard-score projection. This
screen is limited to the tracked GEMSDOE33 repository and the user-supplied prior-art list; the named
GEMSDOE site raster bytes and methods were not independently fetched, so cross-site novelty is not
claimed. Band numbers/descriptions below follow the local code's owner-mirror mapping in
`src/gemsdoe33/grid.py`; they were not re-read from raw TIFF metadata during this session.

## Hard stop before implementation

The parallel-run prompt says the session lane is “the single method paragraph below,” but no unique
method paragraph or lane is identified. The prompt's duplicate screen therefore has no selected
candidate surface to test. In addition, the current checkout contains no `training_features.tif`,
`labels.tif`, `sample_submission.tif`, cached feature stack, or external registry TIFFs. The prior
2026-10-25 audit says the final H33-6 dots already cross the local duplicate guard; it is not an
eligible replacement for the absent pre-placement check. No new experiment, placement, holdout, or
TIF build was run. Do not infer that any candidate is unique or viable from a filename or this slate.

The shared DTI primitive and GeoTIFF writer do exist at `src/gemsdoe33/metric.py` and
`src/gemsdoe33/submission.py`. `src/gemsdoe33/holdout.py` is only a quadrant-index helper;
`src/gems33/holdout.py:evaluate_proxy` scores prebuilt arrays but explicitly does not rebuild candidate
or source features per fold and is invalid for source-dependent promotion. The repository has no
reusable whole-fault-segment, buffered, fold-rebuilt `evaluate_holdout.py` orchestrator matching the
new protocol. H33-6's old runner is conditional and cannot be recycled as confirmation. The current
promotion gate is therefore **blocked**.

## Ranked hypotheses

| Priority | Candidate, layers and physical signature | Why it could find an omitted fault | Difference from implemented repository methods | Expected DTI priority / cost / data gate |
|---:|---|---|---|---|
| 1 | **H33-11 — paired signed vertical-gradient zero-crossing traces.** GeoDAWN training-raster bands 9 (`tmi_vg`) and 11 (`iso_grav_anom_vg`), with bands 14 (`tmi`) and 13 (`iso_grav_anom`) retained for polarity/profile checks. Target continuous, co-located zero-crossing centerlines with opposed-sign lobes on both sides, not simply high gradient magnitude. | A buried fault that juxtaposes or offsets magnetized and density-contrasting basement units can create a paired potential-field boundary even where basin fill has removed a surface scarp. Agreement across magnetic and gravity responses is a stronger structural hypothesis than one-field amplitude alone; it still does not prove faulting. | H33-6 scored gradient magnitudes and edge-normal alignment in raw TMI/gravity, then used basement/conductivity corroboration and matched-budget dot reallocation. H33-11 uses the sign and zero-crossing topology of the supplied vertical-gradient products. The current feature code has individual derivatives and coherence primitives, but the active candidate builders do not implement this paired sign-crossing operator. | **Qualitative priority 1 of 3; moderate plausible upside, no numeric DTI prediction. Medium cost.** No new external dataset is needed. It requires the official competition feature raster; its login-gated source is not accessible here, and only owner-mirror hashes are recorded. No input bytes/cache are present now, so it is not runnable. |
| 2 | **H33-12 — matched-window potential-field texture-offset test.** GeoDAWN bands 14 (`tmi`), 13 (`iso_grav_anom`), and 15 (`depth_to_base_surf`). Target a laterally consistent cross-fault displacement of local geophysical texture: paired windows on opposite sides of a candidate corridor should show a reproducible translation/phase shift in more than one physical field. | A concealed fault can displace basement fabric or geophysical boundaries under cover without producing a surface scarp. A consistent cross-field offset is a kinematic/structural signature, unlike merely finding a strong lineament. | No active GEMSDOE33 builder estimates a matched-window translation vector across the potential-field textures. This is not a claim of broad novelty: the repository's reference archive contains earlier depth-step and Euler/source-depth work, and other owner sites may have tried related registration methods. It differs from H33-6's coincident edge-normal score, but has a substantial prior-art and confounding risk. | **Qualitative priority 2 of 3; upside unknown, high cost.** No new external dataset is required; the same absent, login-gated GeoDAWN feature raster is required. Must use label-blind, preregistered window/scale rules and matched spatial controls; do not optimize scale on holdout. |
| 3 | **H33-13 — mapped-lithology contact control for potential-field edges.** Official USGS SGMC 2026 replacement map-unit polygons (DOI 10.5066/P1A3DQZK), plus GeoDAWN bands 13/14/15. Target persistent magnetic/gravity/basement boundaries that are not explained by mapped lithologic contacts, while retaining an explicit uncertainty band around map contacts. | A large false-positive source for geophysical lineaments is a non-fault lithologic or intrusive contact. Conditioning on mapped units could prioritize unexplained boundaries that are more consistent with concealed structure rather than simply amplifying every contact. A real fault that coincides with a mapped unit boundary could be suppressed, so this is a confound-control test, not a fault truth layer. | Existing local inputs include an owner-mirrored SGMC fault raster used as a separate proxy; the active candidate builders do not use current official SGMC map-unit polygons to explain away geophysical contact responses. This is not the same as using SGMC faults as labels. | **Qualitative priority 3 of 3; upside unknown/possibly modest, high cost and blocked.** Specific free official source: USGS SGMC replacement, [DOI 10.5066/P1A3DQZK](https://doi.org/10.5066/P1A3DQZK). Repository notes only identify the replacement release; its payload, download availability, licence, schema, CRS, coverage, and map-unit semantics have not been audited. The source is therefore **not confirmed obtainable and is not viable yet**. No substitute owner mirror should be called official. |

## Protocol if a later session clears the data/lane blockers

1. Record the exact single-method lane and freeze this candidate slate and evaluation plan before code changes. If any registry raster has rank-correlation `>0.90` or more than `70%` of candidate dots within `3 px`, log the duplicate and stop before placement; repeat on final dots.
2. Use one shared cached feature stack, a fold-safe whole-fault-segment hide-and-recover evaluator, and the shared submission writer. Recompute every catalogue-derived feature from fold-visible fault segments only; buffer withheld segments and mask visible catalogue pixels exactly.
3. Evaluate the best-ranked candidate and each feature alone. Investigate any feature AUC `>0.90` as leakage until disproved. Report pooled HOLDOUT-DTI, evaluator content hash/version, withheld-positive count, and a defensible `95%` interval; include a matched-count/random control where emission changes.
4. Do not spend a competition slot unless a fresh independent confirmation beats a comparable current holdout baseline and every duplicate/format gate passes. Slot selection is a separate selector action under the competition's current cap. A local validation pass is not organizer acceptance.

## Sources and evidence boundary

- [Official competition problem/metric page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) and [official data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/): data retrieval is login-gated in this workspace; no organizer data bytes were available in the current checkout.
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and): primary source pointer for the survey; the current input raster is not staged or authenticated here.
- [USGS SGMC 2026 replacement DOI](https://doi.org/10.5066/P1A3DQZK): official source pointer from `knowledge/05_data_sources_verified.md`; its content/licence/coverage/download remain unaudited.
- Repository prior-art search: `src/gemsdoe33/features.py`, `src/gemsdoe33/analog.py`, `src/gems33/candidates.py`, `registry/hypotheses.json`, `knowledge/07_hypothesis_slate_20261004.md`, and `reference/gems28/`.
- Owner-reported leaderboard/site scores, including the user-reported H33-2 value `0.2778`, are not used as labels, thresholds, or DTI projections. No organizer receipt in this checkout links that number to exact TIFF bytes.
