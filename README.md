# GEMSDOE33 — DOE GEMS Fault Discovery Project (DrivenData #306)

## 🔴 Current decision (2026-10-25): unique TIFF generated; **NOT OK TO SUBMIT**

A genuinely new A33-L1 analog-transfer raster was generated and validated automatically. It is easy to download and passes the prescribed saved-byte format checks, but its preregistered scientific holdout gate **failed**. **Do not spend a weekly slot on it.** No portal upload was made, no organizer receipt exists, and no competition score is predicted.

- **[Download unique zero-outside GeoTIFF](docs/downloads/gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros.tif)**
- **[Download single-file ZIP](docs/downloads/gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros.zip)**
- [Official-template-profile NaN-outside twin](docs/downloads/gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-nan.tif)
- [Machine receipt](docs/downloads/receipt-gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34.json) · [one final JSON run card](evidence/a33_l1_run_card.json)

| Required item | Result |
|---|---|
| Unique name | `gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros` |
| Note (95/140 characters) | `A33-L1 analog-CDF fusion 37654d \| holdout gate FAIL \| research; selector not run \| 85c94a805a34` |
| Saved-byte SHA-256 | `2bbbf7e381720f2242959e3efd6f2437f273afe6e7c48540d769524d2b4e8759` |
| Format | One float32 band; EPSG:32611; 3730×3292; exact transform; values `[0,1]`; no NaN in footprint |
| Content | 37,654 dots; content ID `85c94a805a34` |
| Scientific verdict | **NEGATIVE — NOT OK TO SUBMIT** |
| Why not | A33-L1 lost to the fold-safe regional comparator; required selector was therefore not run |

A format-valid TIFF is not a scientifically promoted submission and does not prove portal acceptance.

## 1. Standing brief and non-negotiable protocol

The full recurring project request and durable rules are preserved in [`standing_prompt.md`](standing_prompt.md). The present run follows its assigned **analog-field transfer** lane:

> Review the repository and the strongest user-reported GEMSDOE24/25/27/28/30/31/32/33/36 artifacts; explain scientifically why the strongest may have worked; create a genuinely unique, easy-to-download competition-format TIFF without copying an old submission; preregister 3–5 new geological hypotheses; test the top candidate on a spatially blocked hide-and-recover holdout before any slot decision; automate validation; update the executive-summary site and README; preserve negative results and evidence; and state conspicuously whether the TIFF is OK to submit.

Mandatory controls applied here:

- withhold whole fault components by quadrant with a 15-pixel buffer;
- derive catalogue-dependent sampling from fold-visible faults only and mask those faults pixel-exactly;
- evaluate pooled DTI with `α=0.2`, `β=0.8`, and a 300 m triangular kernel;
- run every source feature alone; two-sided AUC `>0.90` is a leakage stop;
- stop as duplicate at Spearman `>0.90` or when `>70%` of candidate dots fall within 3 pixels of one registry raster;
- use the shared pinned evaluator and writer, issue no score projection, and separate scientific promotion from weekly-slot selection;
- stop after three experiments or two hours. This run used **one experiment**, about 3.2 minutes, and zero slots.

Core values remain **Maximize P(Win)** and **Own the Outcome**. Here that means publishing the new artifact for audit while refusing to promote a negative experiment.

## 2. Focus review: why GEMSDOE32 B2 may have the reported 0.2778

All historical values in this section are **OWNER/USER-REPORTED — NOT ORGANIZER-CONFIRMED**. This checkout has no authenticated DrivenData receipt tying any historical result to exact bytes. The values are context, not labels or official scores.

Nine highest-reported focus artifacts were restored from pinned repository commits and SHA-256 checked. The byte-level analysis establishes that much of the apparent top-method diversity is one dependent family:

- GEMSDOE25 d2.8 and GEMSDOE30 d2.8 are pixel-identical: 44,090 dots, Spearman 1.0000.
- GEMSDOE31 solo is an exact 40,199-dot subset of d2.8, removing exactly 3,891 dots at 100 m from the mapped catalogue.
- GEMSDOE32 B2 is an exact 37,654-dot subset of solo, removing exactly 2,545 more dots at 100–200 m from the catalogue.
- GEMSDOE36 Anderson contains every B2 dot plus 1,200 more; B2/Anderson Spearman is 0.9843 and Jaccard is 0.9691.
- GEMSDOE24 and GEMSDOE27 are another near-copy pair (Spearman 0.9896).

The most supportable explanation is **metric-aware subtraction from a useful inherited lineament field**. DTI penalizes false-positive mass (`α=0.2`), known-catalogue faults are masked, and repeated nearby dots can be redundant under the 300 m kernel. If the reported sequence 0.2600 → 0.2708 → 0.2778 is accurate, removing low-yield mass beside already mapped traces improved denominator efficiency while preserving off-catalogue lineaments. The reported decrease to 0.2750 after Anderson adds 1,200 dots is directionally consistent with that mechanism. This is a plausible observational explanation—not authenticated score evidence or causal proof. Lithologic contacts, basin edges and acquisition boundaries remain non-fault mimics.

Full nine-site table, metric derivation, limitations and review link: [`knowledge/11_focus_forensics_and_a33_l1_result_20261025.md`](knowledge/11_focus_forensics_and_a33_l1_result_20261025.md). Machine measurements: [`evidence/focus_registry_analysis_20261025.json`](evidence/focus_registry_analysis_20261025.json). The concurrent broader prior-art audit adds three GEMSDOE28 variants and 132 ordered comparisons in [`knowledge/10_focus_review_20261025.md`](knowledge/10_focus_review_20261025.md).

## 3. Can this repository support a higher result now?

**No.** A higher result may be possible in principle, but A33-L1 does not support one and no numeric competition score is projected.

The frozen A33-L1 candidate used 12 structural channels, per-field 257-knot source-to-target marginal CDF alignment, equal source-field loss, and a fixed 0.80 regional / 0.20 adapted-analog rank fusion. It was compared against a raw analog expert (B0), an otherwise matched regional visible-fault expert (B1), and matched random placement at the same fold-scaled dot budgets.

| Method | HOLDOUT-DTI (`gems-segment-pooled-v1`; 60,988 withheld positives; spatial-block bootstrap 95% CI) |
|---|---:|
| Raw pooled analog B0 | 0.087750 [0.079569, 0.095940] |
| **Regional visible-fault expert B1** | **0.113244 [0.102796, 0.124169]** |
| A33-L1 field-balanced transfer | 0.108374 [0.097607, 0.119402] |
| Matched random | 0.071432 [0.068402, 0.074308] |

A33-L1 vs best comparator B1: paired delta **−0.004870**, 95% CI **[−0.010900, +0.001226]**, **0/4 fold wins**. A33-L1 did beat raw transfer B0 (+0.020624, 95% CI [+0.013580, +0.027951], 4/4), so target alignment repaired some transfer error; the analog contribution nevertheless diluted the stronger regional expert.

These are mapped-catalogue **HOLDOUT-DTI** diagnostics, not private expert truth and not organizer scores. Existing analog “labels” are not independently verified dense field truth; that limitation prevents a stronger transfer claim.

## 4. Novelty and leakage results

All 12 feature-alone canaries passed; the worst fold-level two-sided AUC was 0.6211, far below the `>0.90` stop. The generated artifact passed both duplicate stages against the frozen nine-raster experiment registry. After the concurrent canonical 12-reference registry became available, a release guard repeated both stages against all 12 and passed with the same maxima:

| Guard | Measured maximum | Stop threshold | Result |
|---|---:|---:|---|
| Pre-placement surface Spearman | 0.1084 | `>0.90` | pass |
| Final binary Spearman | 0.02221 | `>0.90` | pass |
| Candidate dots within 3 px of one registry raster | 42.25% | `>70%` | pass |
| Versus GEMSDOE32 B2 specifically | rho 0.02203; 37.07% nearby | same | pass |

The raster is therefore genuinely different under the preregistered lane rules and the broader canonical focus subset. Evidence: [`evidence/a33_l1_full_registry_guard_20261025.json`](evidence/a33_l1_full_registry_guard_20261025.json). This remains a focus subset rather than a global uniqueness certificate; uniqueness does not imply predictive improvement.

## 5. Frozen hypothesis slate

Five hypotheses were ranked before implementation in [`knowledge/10_analog_lane_hypotheses_20261025.md`](knowledge/10_analog_lane_hypotheses_20261025.md); the exact protocol was hash-frozen in [`evidence/analog_lane_preregistration_20261025.json`](evidence/analog_lane_preregistration_20261025.json).

1. **A33-L1 target-aligned, field-balanced structural transfer** — runnable; selected; negative.
2. **A33-L2 leave-one-field-out consensus ensemble** — per-field target-aligned experts with two-of-three agreement; runnable but untested.
3. **A33-L3 matched local-contrast transfer** — 2–5 km annular median/MAD normalization with same-relief negatives; runnable but needs a separately frozen matching audit.
4. **A33-L4 CORAL covariance alignment with field holdout** — joint second-moment alignment plus field-holdout diagnostics; runnable, but cannot by itself bound joint-label error.
5. **A33-L5 field-verified BRIDGE/Gabbs supervision** — highest scientific ceiling; blocked because official archive bytes, schema, CRS, overlap and label policy could not be obtained and audited here.

No post-result tuning or second experiment was used to rescue the failed candidate.

## 6. Reproduce and verify

Prerequisites are defined in `pyproject.toml`. Restored owner-mirror inputs are SHA-256 pinned; the cached 121-channel stack is generated rather than committed.

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python scripts/restore_data.py --group all
.venv/bin/python scripts/audit_inputs.py
.venv/bin/python scripts/prepare_data.py --skip-detector
.venv/bin/python scripts/cache_focus_registry.py
.venv/bin/python scripts/evaluate_holdout.py --verify-recorded
.venv/bin/pytest -q
```

The experiment runner is deliberately one-shot: once evidence exists, it refuses implicit reruns. Shared numerical contracts are vendored unchanged from the pinned GEMSDOE24 source snapshot under `vendor/gems24_template/`; provenance and hashes are in `vendor/gems24_template/SOURCE.json`.

Primary evidence:

- [`evidence/a33_l1_experiment.json`](evidence/a33_l1_experiment.json) — complete fold, canary, model, bootstrap and guard record;
- [`evidence/a33_l1_run_card.json`](evidence/a33_l1_run_card.json) — required final JSON run card;
- [`registry/a33_l1_focus_rasters_20261025.json`](registry/a33_l1_focus_rasters_20261025.json) — exact nine-raster frozen experiment registry;
- [`registry/focus_rasters_20261025.json`](registry/focus_rasters_20261025.json) and [`evidence/focus_raster_audit_20261025.json`](evidence/focus_raster_audit_20261025.json) — canonical 12-reference release audit across all nine sites;
- [`knowledge/11_focus_forensics_and_a33_l1_result_20261025.md`](knowledge/11_focus_forensics_and_a33_l1_result_20261025.md) — scientific interpretation;
- [`evidence/a33_l1_three_pass_review_20261025.md`](evidence/a33_l1_three_pass_review_20261025.md) — protocol, implementation and release review.

## 7. Submission procedure—for a future promoted candidate only

Read the generated [executive summary and submission guide](docs/executive-summary.html). In brief:

1. Require an explicit **promote** scientific verdict and a separate **slot-cleared** selector decision. This A33-L1 file has neither.
2. Verify the exact SHA-256 and rerun the saved-byte validator against the official sample template.
3. Check current official competition instructions and remaining weekly slots.
4. Upload manually through the authenticated DrivenData account, using the unique name and ≤140-character note.
5. Preserve the organizer receipt before calling any value organizer-confirmed.

This environment has no DrivenData authentication. Repository automation does not upload, scrape the leaderboard, or claim portal acceptance.

## 8. Trusted review links and provenance limitations

- [DrivenData DOE GEMS competition](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem and metric description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GBCGE INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [Pinned GEMSDOE32 B2 forensic review](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/5fc7792c5887735ecd3aa9a612787da588a7bf2c/knowledge/03_why_02778_and_the_anatomy_of_the_family.md)

Competition inputs in this checkout are reproducible SHA-256-pinned owner mirrors, **not independently organizer-authenticated downloads**. The sample submission was proved to copy catalogue values over its finite footprint and is used only for grid/footprint metadata. No independent Dixie Valley, Brady or Desert Peak label archive was found; `labels.tif` and `existing_faults.tif` in the reviewed analog source are byte-identical. These irregularities are preserved rather than silently upgraded into ground truth.
