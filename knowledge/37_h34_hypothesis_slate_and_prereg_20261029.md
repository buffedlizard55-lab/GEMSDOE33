# 34 — Hypothesis slate (ranked) and frozen preregistration, 2026-10-29

**Scope.** One session, one method lane (budget: 3 experiments, 2 hours). Evaluator, feature cache,
duplicate guard and writer are the shared template tools (`evaluate_holdout.py`,
`vendor/gems24_template`, `src/gemsdoe33/csht_transfer.py`, `submission_writer.py`). No DrivenData
access, upload, scrape or slot selection. Every number below is **HOLDOUT-DTI** (local catalogue
proxy, not organizer-confirmed) unless stated otherwise.

## 1. Ranked candidate hypotheses (not yet tested)

Ranking = expected holdout gain (qualitative) × inverse implementation cost, after checking prior art.
Prior art checked: `knowledge/07`, `10`, `11`, `13`, `14`, `15`, `22`, `24`, `25`, `26`, `27`, `30`, `31`, `32`.

| Rank | ID | Layer(s) | Physical signature targeted | Why it should reach a fault absent from the USGS/INGENIOUS catalogue | Difference from repo prior art | Expected gain (qualitative) | Cost | Data status |
|---|---|---|---|---|---|---|---|---|
| **1 (tested here)** | **H34-COH** | `tmi_ridge` (NMS ridge of the magnetic second-derivative, cache ch. 118) gated into the B1 regional expert | **Line coherence**: a fault is a long, roughly straight ridge set; isolated ridge pixels are not. Score = max over 8 orientations of 11-px line-averages, minus their mean | Coherent linear ridge trains need not appear in the catalogue; continuity is a geometric property the regional expert does not encode | SEISDIL/PHCONG gate gradients and strain/phase; DPPS projects positions; none uses an orientation-line coherence of the magnetic ridge map | low–medium | Low (cached channel, ~8 convolutions) | Pinned, staged |
| 2 | H34-SPUR | `tmi_ridge` + `ieq_n100a15_ridge` | Suppress orientation-parallel stripes | Airborne flight-line striping is a known artefact, so removing it can raise precision without touching real faults | Not in prior art as a standalone | low gain, low cost | Low | Pinned |
| 3 | H34-DEPTH | `depth_to_base_surf` gradient × B1 | Abrupt basement-depth steps (offset of the basement) | Basement offsets without surface trace may be missed by the catalogue | Partly covered by BASESTEP/THKCOND (R5/R6) and failed; overlap high | medium | Medium | Pinned |
| 4 | H34-CURVTRACE | Raw USGS 3DEP 1 m curvature | Low-relief buried/eroded scarps | Scarps below the 100 m grid are invisible | Blocked: raw 1 m tiles not staged (`knowledge/18`) | high if available | High | **Blocked** — tiles not staged; not verified obtainable here |
| 5 | H34-COULOMB | DOE GDR #1391 fault geometry | Stress-transfer lobes around slipping faults | Predicts blind splays | Blocked: CSV lacks vertices/strike; CRS unresolved (`knowledge/18`) | unknown | High | **Blocked** |

Obtainability checks for blocked items were taken from the repo's own audit (`knowledge/18`,
`evidence/round4_input_feasibility_20261026.json`). They were **not** re-verified online in this session,
so they are not promoted.

## 2. Frozen definition of the tested candidate (H34-COH)

1. `tmi_ridge` read from `.cache/features/tmi_ridge.npy` (3730×3292, float32).
2. Eight line kernels (length 11 px, angles k·22.5°, k=0..7), normalised to mean 1. `A_k = conv(tmi_ridge, line_k)`.
3. `C = max_k A_k − mean_k A_k` (orientation-coherence), then `pct(C)` on the training-fold `valid` domain.
4. Surface: `S = pct(B1) × (0.2 + 0.8 × pct(C))`, where `B1 = fit_regional_expert(train, visible)` and `pct` is `analog_invariant.percentile_surface`. The gate form matches SEISDIL, so the operator comparison is matched.
5. Emission: `csht_transfer.celf_emit_300m(S, eligible = valid & (dist_to_visible > 2 px), budget)`, with budget `round(37654 × |valid| / 5,167,373)` per fold and 37,654 at full deployment.
6. **Matched-random control (same budget, same eligibility):** uniform random emission, seeded.
7. Holdouts: `SegmentHoldout(buffer_px=15)` (screen) and `DiagonalSegmentHoldout(buffer_px=20)` (confirm), both from the shared template.

## 3. Preregistered decision rule (fixed before running)

Promote only if **all** hold:
- (a) Screen: H34-COH DTI > B1 DTI, paired 95% CI strictly > 0, fold_wins ≥ 3 of 4.
- (b) Confirm: same three conditions on the confirm holdout.
- (c) H34-COH DTI > matched-random DTI on both holdouts (control must lose).
- (d) Feature canary: no single feature AUC > 0.90 on the holdout.
- (e) Duplicate guard passes on the pre-placement surface AND the final dots (|ρ| ≤ 0.90, overlap ≤ 70% within 3 px) against all 22 registry rasters.
- (f) Saved bytes pass the format audit (single band, float32, EPSG:32611, 3730×3292, template transform, footprint finite in [0,1]).

If (a)–(f) fail, the verdict is **negative**. A negative result is kept and no retuning follows.

**Stop rules.** Exp 1 = baseline audit. Exp 2 = H34-COH. Exp 3 is held in reserve and is used only for a confirmatory
rerun if Exp 2 passes (a)–(f). No parameter (line length, 8 directions, gate weights) is tuned on holdout results.

**Named non-fault mimics** (to be tested as failure modes): airborne flight-line striping and levelling artefacts in the
magnetic channel (stripe-parallel ridges); drainage incision and cultural linears (roads, fences, pipelines, canal
banks), which are straight and continuous.

**Expected outcome (stated before running).** Probable negative. Gating by a single-channel line coherence adds little
beyond the regional expert, which already sees the ridge channel as a feature. A pass would be surprising.
