# 14. `A33-R3-LCHC` Result & Round-4 Ranked Hypothesis Slate (2026-10-26)

## Part A — `A33-R3-LCHC` executed result (NEGATIVE, honest deliverable)

### Hypothesis as preregistered

`evidence/a33_r3_lchc_preregistration_20261026.json` (frozen SHA-256
`bc4ecef34e3b81e19f41c9422fba60d99ed4c8a6c06eadb4617198753dd63a6e`, verified intact by
`scripts/evaluate_holdout.py --verify-a33-r3-lchc`): **Least-Cost Hydrothermal
Connectivity (`LCHC`)** — build a 300 m resistance (cost) surface from
percentile-rank-averaged `cond_surf`, `cond_surf_gms2`, `iso_grav_anom_hg`,
`iso_grav_anom_slope`, `geod_shearrate`, `geod_dilaterate`, and
`depth_to_base_surf`-derived `basement_edge`; multi-source Dijkstra + minimum
spanning tree among up to 90 merged DOE GDR #1391 thermal/vent seed clusters
(`1,116` catalogue-free cells, `dist_known_fault_px` hard-excluded); keep the
shortest `85%` of MST edges; trace each kept path; blend with LiDAR/TMI
corroboration; place `37,654` dots via the shared 300 m triangular-kernel
`CELF` operator. This is a genuinely different mechanism from every prior
`GEMSDOE33` lane (not a pixel classifier, not a geometric stepover graft, not
a regional HGB favorability surface) — the candidate connecting fault
segments are literally graph shortest paths through a resistance field, not
pointwise scores.

### Executed result

| Experiment | Split | `A33_R3_LCHC` | `B1_regional` | Paired Δ (95% CI) | Fold wins |
|---|---|---:|---:|---|---:|
| Screen (1/3) | `quadrant-buffered-15px-v1` | `0.043712` | `0.125441` | `-0.081728 [-0.097741, -0.062859]` | `0/4` |
| Confirm (2/3) | `diagonal-wedge-buffered-20px-confirm-v1` | `0.035199` | `0.128184` | `-0.092985 [-0.108431, -0.075215]` | `0/4` |

- **Verdict: `negative`.** Failed gates: `screen_beats_current_best`,
  `independent_confirmation`. All other 10/12 `promotion.py` gates PASS,
  including `all_feature_canaries` (max pooled AUC `0.5663`, far under the
  `0.90` leakage threshold — importantly, even the **finished full LCHC
  surface itself** canaries at pooled AUC `0.5001`, i.e. statistically
  indistinguishable from random against held-out catalogue segments) and,
  notably, **both** `surface_not_duplicate` and `final_dots_not_duplicate`
  (max `|Spearman ρ| = 0.0054`, max 3-px overlap `18.6%` surface /
  `16.7%` final dots — the most orthogonal surface produced in this repo to
  date, versus `A33-R2-CSHT`'s fail-closed `91%` surface collapse with
  `G30-MSDB1`).
- **Mechanistic explanation (ties directly to the GEMSDOE32 `B2` DTI
  mechanism in `knowledge/13`):** DTI weights false negatives 4× false
  positives (`α=0.2`, `β=0.8`). A connectivity-tree surface is structurally
  sparse by construction — it only lights up single-pixel-wide shortest paths
  between a few dozen seed clusters (`1,955` nonzero 300 m cells pre-blend
  against a `5,167,373`-cell footprint), so even if every placed dot were a
  true fault, the surface cannot physically cover enough of the withheld
  segment mass to avoid heavy `0.8·FN_w` penalty. This the same failure mode
  recorded for `GEMSDOE28`'s `S18` (`11,082` dots, `0.0217`*) and the
  project's own `H-N1` precedent: **recall-starved, precision-only
  detectors lose under this metric even when structurally novel and
  leakage-clean.**
- **Artifacts:** `docs/downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-{zeros,nan}.tif`
  (+ `.zip`, receipt). `ok_to_download = true`, `ok_to_submit = false` (now for
  a *different* reason than `A33-R2-CSHT`: here it is a clean statistical
  loss, not a duplicate-surface fail-close). Full run card:
  `evidence/a33_r3_lchc_run_card_20261026.json` /
  `docs/data/a33_r3_lchc_run_card_20261026.json`. Reproduce/verify with
  `python scripts/evaluate_holdout.py --verify-a33-r3-lchc` (no rerun; this is
  a frozen, already-decided negative result — rerunning after viewing these
  numbers would violate the no-post-hoc-tuning rule).
- **Lesson for future rounds:** sparse, high-precision, physically pure
  connectivity/graph methods are now a *second* confirmed dead end alongside
  dense regional HGB favorability surfaces (which hit the uniqueness
  fail-close instead). The viable region is narrow: a candidate must (a) cover
  enough footprint area to avoid `FN_w` starvation, while (b) not converging
  on the same ~100 m regional-geophysics feature space as `G30-MSDB1` /
  `G24-gvc1` / `G25-h66` / `A33-R2-CSHT`. Genuinely orthogonal, *areal*
  (not single-trace) detectors are required — see Part B.

---

## Part B — Round-4 ranked hypothesis slate (proposed, **not executed** this session)

The table ranks candidate mechanisms by *qualitative expected DTI upside relative to implementation/risk cost*; no numerical improvement is forecast. Four mechanisms are untried at the candidate/holdout level: `COULOMB`, `CURVTRACE`, `PFRT` and `PALEOTEMP`. `HMDT` is retained for completeness as a previously generated 42,000-dot artifact, but it has no holdout run card and is **not** counted as an untried hypothesis. All are distinct from the fully evaluated mechanisms already tried in this repo (`H19-5` deletion pruning, `CSHT` percentile-rank multi-physics blend, `LCHC` least-cost graph connectivity, `H33-D`/Anderson geometric tip-stepover grafts, `H33-6` edge-consensus, tilt-gravity-LiDAR coherence, `DA-HGCM`, `MSTD1` Mohr-slip, `H29` hydrothermal-piedmont, `SBIR1`, `H31R` relay-damage, `RSHG1` supervised ridge, `GVC1` negative lineament). No candidate in the table has a valid, complete screen-and-confirm result; no new hypothesis experiment was run in the current review. **No candidate may be promoted without first passing the full preregistered screen/confirm/uniqueness holdout protocol**, exactly as `A33-R2-CSHT` and `A33-R3-LCHC` were.

| Rank | Hypothesis | Layers used | Physical signature | Why it catches off-catalogue faults | Differs from existing work by | External data needed? | Cost | Expected DTI gain | Key risk |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **`A33-R4-COULOMB`** — Okada elastic Coulomb-stress-transfer from mapped Quaternary faults | `data/gdr_qfaults_traces.csv` + `data/qfaults_v2_in_footprint.json` (slip_rate, dip_direct, slip_sense, clipped_length_m — **already pinned locally, zero new fetch**) | Static Coulomb failure stress change (ΔCFS) computed via closed-form elastic half-space (Okada 1992) dislocation from each mapped QFFD segment's slip rate/sense/dip; positive-ΔCFS lobes at fault tips and on sub-parallel/conjugate planes are the textbook geomechanical location for synthetic/antithetic splay growth | Stress-triggering is a documented physical cause of blind splay faults near step-overs/segment ends — a *mechanism*, not a proximity heuristic, so it can propose candidate fault locations that are geometrically far from any mapped trace but physically loaded by it | `H33-D`/Anderson only measured geometric distance/dip-slip kinematics; nothing in this repo has computed actual elastic stress transfer | **No** — fully derivable from already-pinned QFFD attributes | Moderate (closed-form Okada formulas, pure NumPy/SciPy, ~2–3 hr incl. guard against recreating the failed naive-stepover halo) | Moderate–high, unproven | Must gate on *positive*-ΔCFS-only lobes with a minimum-distance exclusion, or it degenerates into the already-failed `H33-D` halo graft |
| **2** | **`A33-R4-CURVTRACE`** — multi-azimuth curvilinear 1 m LiDAR trace-continuity detector | `data/lidar_scarp_features_u8.tif`, `data/lidar_scarp_features.json`, DEM derivatives already in `data/` | Multi-azimuth (0°/45°/90°/135°) hillshade + profile-curvature stack fed through a Radon/Hough-style directional line-continuity score requiring ≥ 1.5 km continuous alignment, restricted to `lid_valid > 0` (`75.37%` of footprint) with the existing `IR-33-LIDAR-VOID-01` void mask as a hard exclusion (not backfilled by inference) | Sub-100 m geomorphic scarp morphology is directly visible at 1 m LiDAR resolution but invisible to 100 m-pixel regional HGB classifiers — this is the specific gap identified in `knowledge/13`'s own derivation of what would be needed to beat `0.2778` | Every classifier tried so far (`CSHT`, `MSDB1`, `gvc1`, `h66`) operates on ~100 m regional geophysics; none has directly traced 1 m morphology | **No** — 3DEP LiDAR already restored/pinned | Higher (Radon-transform/curvature-stack implementation, azimuth kernel bank, ~2–3 hr) | Potentially the highest of the five (this is literally the mechanism `knowledge/13` concluded would be required to beat `B2`), but **only covers 75% of the footprint** — needs an explicit fallback policy for the LiDAR-void remainder | Line detectors are notorious for false positives on non-tectonic linear topography (roads, canal/levee berms, glacial/alluvial terrace risers) — must explicitly screen against the named non-fault mimic before preregistering |
| **3** | **`A33-R4-HMDT`** — hydrothermal magnetite-destruction × clay-cap signed dipole | `cond_surf`, `tmi_hg`-derived upward-continued TMI minus RTP, `iso_grav_anom_hg` (all already cached from `CSHT`) | Signed cross-gradient $\nabla\text{cond\_surf}\cdot\nabla(\text{TMI}_{\text{up150}}-\text{RTP})$ gated inside dilational-strain zones — targets the specific asymmetric magnetic-low/conductive-high *doublet* diagnostic of argillic clay-cap alteration haloing one side of a buried normal fault | A signed, oriented dipole feature is a specific rock-magnetic alteration signature, not a generic unsigned multi-physics favorability average (`CSHT`'s mechanism) | `CSHT` democratically averaged percentile ranks (unsigned, undirected); nothing in this repo has used a signed cross-gradient dipole | **No** — carried over from `A33-R2`'s preregistered reserve list, already viable on the pinned 17-input cache | Low (~1 hr; reuses existing `CELF` placement) | Modest — carries the same sparsity/precision-only risk flagged by the `LCHC` result above | Local-contrast-gated dipole features tend toward the same recall-starved failure mode just confirmed for `LCHC`; must budget footprint coverage, not just precision, before screening |
| **4** | **`A33-R4-PFRT`** — listric dip-projected basement-to-piedmont offset-vector transfer | `depth_to_base_surf`, `iso_grav_anom_hg` (already cached) | Projects buried basement gravity-high crests updip by $z_{\text{base}}\cot\delta$, $\delta\in[45^\circ,65^\circ]$, along $-\nabla z_{\text{base}}$ onto piedmont flexures — models the specific geometric relationship of a blind listric normal fault emerging updip from a basement high, not a generic gradient-magnitude favorability weight | Encodes one explicit fault geometry (listric dip projection) rather than scoring raw gradient magnitude the way the fail-closed `A33-R2-CSHT`/`G30-MSDB1`/`G24-gvc1` surfaces did | Carried over from `A33-R2`'s preregistered reserve list; still untried | **No** | Low–moderate | Speculative/moderate | **Highest duplicate risk of the five** — any surface built mainly from `iso_grav_anom_hg` must be checked for 3-px overlap against `G30-MSDB1`/`G24-gvc1`/`G25-h66` within the **first few minutes**, before further investment, per the exact lesson of `A33-R2-CSHT`'s fail-close |
| **5** | **`A33-R4-PALEOTEMP`** — paleogeothermal sinter/tufa & 2 m shallow-temperature-probe conduit transfer | Would need a BHT/sinter inventory product inside DOE GDR #1391 not yet pinned locally (distinct from the already-pinned wellspring/vent CSVs used by `CSHT`/`LCHC`) | Shallow (2 m) temperature-probe anomalies and paleo-sinter/tufa deposits mark long-lived, possibly currently-quiescent hydrothermal conduits tied to older (pre-Holocene) fault activity, complementing the active-vent-only seeds used by `LCHC` | Targets *inactive/relict* conduits, which `LCHC`/`CSHT` (active thermal/vent seeds only) structurally cannot see | **Yes — named, specific, and currently BLOCKED in this sandbox.** Official source: DOE Geothermal Data Repository submission #1391, `https://gdr.openei.org/submissions/1391` (CC BY 4.0, same official submission already partially pinned for the wellspring/vent CSVs). The *specific additional data product* (2 m probe/sinter inventory) is not in the current pin set and `gdr.openei.org` is **not** reachable from this sandbox's outbound allowlist (`github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org` only). | Blocked until an owner-mirror SHA-256 pin for that specific file is added outside this sandbox (`IR-33-MIRROR-01`) | N/A until data is pinned | Not assessable until obtainable | Do not preregister or budget an experiment slot for this until the named source is confirmed pinned and hash-verified |

**Merge-time addendum (2026-10-26):** a concurrent parallel session in this
same repository independently generated an `A33-R2-HMDT` artifact
(`gemsdoe33-a33-r2-hmdt-20261026-hmdt-unique-zeros.tif`) matching Rank-3's
mechanism name, but **did not measure its holdout DTI** (flagged
`IR-33-HMDT-UNGATED-01`; no run card exists, so `scripts/select_submission.py`
correctly treats it as not eligible). Rank 3 below should therefore be read as
"finish the holdout screen/confirm for the existing `HMDT` surface" rather
than building a new one from scratch. This does not change the Rank-1/Rank-2
recommendation (`A33-R4-COULOMB`, `A33-R4-CURVTRACE`), which remain untried in
any form.

**Guidance carried forward from this round's two consecutive results (`A33-R2`
surface-duplicate fail-close, `A33-R3` recall-starved negative):** the
project has now empirically ruled out (a) dense regional multi-physics HGB
favorability surfaces (duplicate-convergent) and (b) sparse single-trace
connectivity/graph surfaces (recall-starved) as viable paths to beat
`GEMSDOE32` `B2` (`0.2778`*, user-reported). Rank-1 (`A33-R4-COULOMB`) and
Rank-2 (`A33-R4-CURVTRACE`) above are the two candidates in this slate judged
most likely to occupy the narrow remaining viable region — areal enough to
avoid `FN_w` starvation, physically distinct enough to avoid the HGB
duplicate-convergence trap — and are the recommended next experiments for a
future session's 3-experiment/2-hour budget, screened on holdout **before**
any submission slot is spent.
