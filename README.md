# GEMSDOE33 — DOE GEMS Fault Discovery

Repository for research on the DrivenData DOE GEMS fault-mapping challenge. **Read this README, [`standing_prompt.md`](standing_prompt.md), and [`AGENTS.md`](AGENTS.md) at the start of each session.** The current review and its evidence card are [`knowledge/24_repository_review_20261027.md`](knowledge/24_repository_review_20261027.md) and [`evidence/20261027_review_card.json`](evidence/20261027_review_card.json).

## Current decision — 2026-10-27

> **NO raster is OK TO SUBMIT.** The fail-closed selector finds **0 eligible of 13** candidate run cards. This review used no experiment, produced no new GeoTIFF, selected no competition slot, and made no upload. The task does not identify the required single assigned method lane; choosing a hypothesis from the slate would violate the standing parallel-run protocol.

The latest unique *existing* artifact is **FSML2-CC**, generated 2026-10-26, not in this review. It is **OK TO DOWNLOAD FOR RESEARCH: YES / OK TO SUBMIT: NO**. Its local format audit and duplicate checks pass against the pinned registry; its two holdout comparisons are negative. Uniqueness means only “passed the checked 22-raster registry,” not global uniqueness. There is no public-score estimate.

- [Download FSML2-CC `[0,1]` GeoTIFF](docs/downloads/gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-zeros.tif) · [ZIP](docs/downloads/gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-zeros.zip) · [NaN-outside twin](docs/downloads/gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-nan.tif)
- Submission name: `gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-zeros`
- Note: `GEMS33 FSML2-CC V1_cc6 spyPU+worm+line CELF 37654d | NEGATIVE | 6fd4410bbaee` (77/140 characters)
- SHA-256: `be5013aad085c23a9317959f85c7d494e28eac5875f61addce8ec81b5bb51de3`
- Decision logic and saved-byte evidence: [`docs/data/submission_selection.json`](docs/data/submission_selection.json), [`evidence/submission_selection_20261027.json`](evidence/submission_selection_20261027.json), and [`knowledge/23_fsml_results_20261026.md`](knowledge/23_fsml_results_20261026.md).

### FSML2-CC validation summary

**HOLDOUT-DTI** uses `gems-segment-pooled-v1`, 60,988 withheld catalogue positives, and 10 km spatial block-bootstrap 95% confidence intervals. It is a catalogue-recovery proxy, not a competition score.

| Split | FSML2-CC | A33-R2-CSHT comparator | Paired difference (95% CI; fold wins) |
|---|---:|---:|---:|
| Screen | 0.110427 [0.1009, 0.1203] | 0.135672 [0.1241, 0.1477] | −0.025246 [−0.0355, −0.0151]; 0/4 |
| Frozen confirmation | 0.103077 [0.0941, 0.1129] | 0.132066 [0.1201, 0.1440] | −0.028989 [−0.0410, −0.0174]; 0/4 |

It passed the pre-placement and final-dot uniqueness gates against the checked registry, but failed the beat-CSHT promotion gates. Download is for research only; **do not submit**. Full canaries, protocol, and run card: [`knowledge/23_fsml_results_20261026.md`](knowledge/23_fsml_results_20261026.md) and [`evidence/fsml2_run_card_20261026.json`](evidence/fsml2_run_card_20261026.json).

## Why the reported GEMSDOE32 B2 value is higher

The `GEMSDOE32` B2 file is a **37,654-dot exact subset** of the earlier 40,199-dot H27-4 emission; byte-level comparison finds no added dots. H27-4 itself is a thinning of the 44,090-dot `d=2.8` H19-5 emission. B2 removes another 2,545 dots from the next catalogue-distance halo, following the earlier removal of 3,891 nearest-halo dots. The supplied historical reports rise from 0.2600 to 0.2708 to **0.2778** across this pruning sequence.

The plausible metric mechanism is that removing detections near already mapped fault traces reduces weighted false-positive mass while losing comparatively little kernel-weighted recall. DTI weights false positives by α=0.2 and missed catalogue positives by β=0.8 with a 300 m triangular kernel, so well-placed sparse dots can outperform an over-dense superset. This is an interpretation, **not a demonstrated causal explanation of the private score**: the organizer labels are hidden, the public values are owner-reported, and no receipt binds exact raster bytes to the reported score. B2 is prior art; do not copy or lightly perturb it. See [`knowledge/22_b2_forensics_and_fsml_slate_20261026.md`](knowledge/22_b2_forensics_and_fsml_slate_20261026.md).

All nine focus sites' top owner-reported files are in the same H19-5 pruning/emission family. A historical GEMSDOE36 file contains the B2 dots plus 1,200 additions; it is not an independent surface. The detailed byte-level comparisons are recorded in the B2 forensics report. **No public leaderboard value is estimated from HOLDOUT-DTI.**

## Executive comparison — nine focus sites

All listed public values are `USER/OWNER-REPORTED`, not organizer-confirmed. The best artifact per site below is the highest supplied historical report; recent lower-scoring attempts are included where available. An asterisk marks owner-reported score provenance. The additive score ledger has 130 records (including blanks and four rows from the latest supplied brief): [`registry/user_reported_scores_20261026.csv`](registry/user_reported_scores_20261026.csv). The byte-pinned raster registry is narrower and contains 21 files: [`registry/focus_rasters_20261026.json`](registry/focus_rasters_20261026.json). Do not infer that every score row has a locally audited raster.

| Site | Highest supplied owner-reported artifact | Recent comparison / executive read |
|---|---|---|
| **GEMSDOE24** | `GEMSDOE24-h25-1-d1p5-20261004-989f59505db1.tif` — 60,069 dots, **0.2477*** | GVC1 — 37,654 dots, 0.0859*; reported as a negative-lineament attempt. |
| **GEMSDOE25** | `gems25-h19-5-d2p8-20261004T201317Z-e56ea318af89.tif` — 44,090 dots, **0.2600*** | H66/MGD flank — 0.0742*; lower reported result. The high-score `d2.8` emission is shared with GEMSDOE30. |
| **GEMSDOE27** | `gems27-topo-gap-20261004-5512495c6bd1.tif` — 61,328 dots, **0.2449*** | H29 — 0.2190*; H31 (`gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite`) — 0.2250*. H29 remains the supplied independent non-H19-5 comparator. |
| **GEMSDOE28** | `h36-1-r1-band-prune-20261004T231500Z-b531dae0a36f-zeros.tif` — 37,660 dots, **0.2710***; H27-4 — 40,199 dots, 0.2708* | S18 — 0.0217*; S21 (`gems28-s21-puhgb-20261026-16bbf281ba9b-allfinite`) — 0.0206*. High-score files are in the H19-5 pruning family. |
| **GEMSDOE30** | `gems30-d28-baseline-20261004-91eae1ca-zeros.tif` — 44,090 dots, **0.2600*** | MSDB1, catalogue-supervised HGB — 0.1462*; classic `d2.8` is also reported for GEMSDOE25. |
| **GEMSDOE31** | `h27-4-r1-solo-d2-8-20261004T195206Z-8acb75e1-zeros.tif` — 40,199 dots, **0.2708*** | H31R-1 is unscored and failed its holdout gate. H27-4 is prior art in the B2 pruning chain. |
| **GEMSDOE32** | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` — 37,654 dots, **0.2778*** | Supplied nine-site peak; exact subset of H27-4. This score/file association is not independently verified by an organizer receipt. |
| **GEMSDOE33** | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-zeros.tif` — 41,865 dots, **0.2632*** (retired) | S33-SEISDIL (`gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros`) — 0.0963*. Newer research candidates are negative or duplicate-blocked; no GEMSDOE33 raster is OK TO SUBMIT. |
| **GEMSDOE36** | `gemsdoe36-anderson-dipslip-h33b2-k1200-20261004-9b9ea4e6-zeros.tif` — 38,854 dots, **0.2750*** | KPL36 (`gemsdoe36-kpl36-exp3-20261026-fc869911e88c-zeros`) — 0.1647*. Anderson contains B2 plus 1,200 tip dots; it is not an independent high-scoring surface. |

**Comparison caveats:** public score reports have no retained organizer receipts, exact-score attribution to a file is not verified, and these historical submissions are not ranked by a single controlled experiment. The supplied current-leader claims 0.3195 and 0.4413 conflict and remain unverified; no automated or manual leaderboard refresh was done. Further source and date notes: [`registry/leaderboard_review.json`](registry/leaderboard_review.json) and [`registry/irregularities.json`](registry/irregularities.json).

## Ranked geological hypotheses — proposals only, not a lane assignment

The following slate was ranked qualitatively by plausible geological signal, implementation cost, prior-art overlap, and data availability. **No numeric improvement is forecast and none was tested**, because no assigned method paragraph/lane was identified. Machine-readable definitions, physical mechanisms, mimics, prior-art distinctions, source status, and shared validation gates are in [`registry/hypotheses_20261027.json`](registry/hypotheses_20261027.json).

| Rank | Hypothesis | Mechanism and possible missing-fault signal | Named non-fault mimic | Data / cost status |
|---|---|---|---|---|
| **1** | **H27-PHASEEDGE — multiscale cross-physics phase-congruency edges** | Phase-aligned magnetic/gravity boundaries, optionally supported by basement-depth edges, may reveal buried displacement with weak surface expression. Different transform from raw-gradient, Hessian/ridge and scarp-integral work; shared-layer duplicate risk remains. | Intrusive or stratigraphic contacts, magnetic-domain boundaries, survey seams, processing artifacts. | Cached channels locally present from owner mirrors; medium-high cost. The official [USGS GeoDAWN record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) is linked in repository sources but was not reauthenticated this session. |
| **2** | **H27-BIFURCATION — persistent basement/gravity ridge junction graph** | Track geophysical ridge branches across frozen scales; reward persistent Y-junctions only with cross-physics orientation support. Concealed basement steps or relay splays could create branching subsurface boundaries. Conceptually adjacent to existing ridge/network work; novelty is uncertain. | Intersecting lithologic contacts, basin margins, magnetic domains, interpolation seams. | Required channels locally cached from owner mirrors; medium cost, with high prior-art/duplicate risk. Same official GeoDAWN source caveat as above. |
| **3** | **H27-CATCHMENT-PROFILE — repeated cross-valley profile asymmetry** | Repeated, orientation-consistent channel deflection and profile breaks could reflect low-relief blind displacement across neighboring valleys. | Lithologic knickpoints, stream capture, fan incision, terraces, roads and canals. | Requires raw USGS [3DEP](https://www.usgs.gov/3d-elevation-program) 1 m tiles, which are absent; the local 100 m aggregate is not an adequate substitute. Tile host is outside this sandbox's recorded allowlist. **Blocked, not viable until exact official payloads are obtained and audited.** High cost. |

The ranked list is not permission to experiment. For any authorized single lane, preregister before evaluating; stop if continuous-surface rank-correlation with any registry raster is >0.90 or >70% of candidate dots fall within 3 px of a registry raster. Run feature-alone leakage canaries; AUC >0.90 is leakage-suspect until resolved. Use at most three experiments or two hours, whichever comes first.

## Data, provenance, reproducibility, and checks

- The current workspace restored 17 SHA-pinned files from public owner-maintained GitHub mirrors and verified all hashes. This proves mirror-byte identity only, **not official origin, completeness, or licensing**.
- The sample submission's finite values exactly copy catalogue labels on its footprint. It is used only for grid/footprint metadata, never as training or validation truth.
- `scripts/prepare_data.py --skip-detector` prepared 121 cached channels; 3,073 footprint cells have a missing core band. The cache and restored inputs live under ignored `.cache/` and are not included in Git or this deliverable. A fresh checkout must restore and prepare them again.
- No generic OOF detector was trained. The repository has no supported `fit_predict_oof` implementation for this pipeline; the explicit training path fails closed. Use the shared holdout/evaluator and writer; do not make a private fork.
- Required spatial holdout: hide whole fault segments with a buffer, derive every catalogue-based feature only from fold-visible faults, and mask visible faults pixel-exactly. Score pooled DTI with α=0.2, β=0.8, and a 300 m triangular kernel. Report `HOLDOUT-DTI`, evaluator version, withheld-positive count, and 95% CI. Feature-alone AUC >0.90 is leakage-suspect until demonstrated otherwise.
- A submission candidate must pass continuous-surface and final-dot uniqueness checks, saved-byte grid/range validation, independent confirmation, and the separate fail-closed selector. No slot selection or upload occurs in this research lane.

Recreate the local inputs/cache and run checks:

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
GEMS_DATA_DIR="$PWD/.cache/gemsdata" .venv/bin/python scripts/restore_data.py --group all --data-dir .cache/gemsdata
GEMS_DATA_DIR="$PWD/.cache/gemsdata" GEMS_CACHE_DIR="$PWD/.cache" .venv/bin/python scripts/prepare_data.py --skip-detector
GEMS_DATA_DIR="$PWD/.cache/gemsdata" .venv/bin/python scripts/audit_inputs.py
GEMS_DATA_DIR="$PWD/.cache/gemsdata" .venv/bin/python scripts/audit_sample_template_values.py
GEMS_DATA_DIR="$PWD/.cache/gemsdata" .venv/bin/python scripts/select_submission.py --date 20261027
PYTHON=.venv/bin/python bash scripts/run_checks.sh
```

## Primary-source links

These are official/primary sources retained for manual review. **They were not freshly fetched or reauthenticated on 2026-10-27.** The current run accessed no DrivenData account, competition portal, or leaderboard.

- [DrivenData DOE GEMS overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem statement and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — login is not available in this workspace
- [Organizer reference implementation](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [DOE GDR #1391 / INGENIOUS](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [DrivenData Terms of Use](https://www.drivendata.org/termsofuse/) — the repository records a one-time read dated 2026-10-04; it was not refreshed in this review

## Review record and project brief

- Three implementation/review passes, exact blocked status, prior-art notes, limitations, and the 2026-10-27 source/data audit: [`knowledge/24_repository_review_20261027.md`](knowledge/24_repository_review_20261027.md).
- No-experiment JSON card: [`evidence/20261027_review_card.json`](evidence/20261027_review_card.json).
- Dated selector decision: [`evidence/submission_selection_20261027.json`](evidence/submission_selection_20261027.json).
- Full standing operating brief and dated addenda: [`standing_prompt.md`](standing_prompt.md).
- Tracked review findings/irregularities: [`registry/irregularities.json`](registry/irregularities.json).
