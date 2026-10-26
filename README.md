# GEMSDOE33 — DOE GEMS Fault Discovery Project (DrivenData #306)

> **Read first, every session:** this README (current status), then [`standing_prompt.md`](standing_prompt.md) in full and [`AGENTS.md`](AGENTS.md). Latest dated addendum governs current status; earlier addenda are historical.
> **Core values:** Maximize P(Win) · Own the Outcome.
> **Labels:** performance values are HOLDOUT-DTI (evaluator, withheld positives, 95% CI) or ORGANIZER-CONFIRMED. Historical values marked \* are USER/OWNER-REPORTED, never score estimates.

## 🔴 Current decision (reviewed 2026-10-26): **NO raster is OK TO SUBMIT** · existing A33-R3-LLC TIF is **OK TO DOWNLOAD** for research only

**Review scope:** no new TIFF, modeling experiment, holdout evaluation, competition slot, or upload was produced in this review. The 17 pinned owner-mirror inputs were restored and hash-verified; `scripts/audit_inputs.py` verified 17/17 pins and the shared grid; the cached 121-channel feature preparation succeeded with the detector skipped. This is preparation only—not organizer-authenticated data or model evidence. Current blockers remain an unidentified standalone method lane and an unspecified canonical shared-template identity. See [`evidence/repository_review_20261026.json`](evidence/repository_review_20261026.json) and [`evidence/data_preparation_20261026.json`](evidence/data_preparation_20261026.json).

| Question | Answer (decided by code: [`scripts/select_submission.py`](scripts/select_submission.py) → [`docs/data/submission_selection.json`](docs/data/submission_selection.json)) |
|---|---|
| **OK TO DOWNLOAD?** | **✅ YES.** The A33-R3-LLC GeoTIFF passes the strict format audit. It is a single-band `float32` file on the `sample_submission.tif` grid (`EPSG:32611`, `3730×3292`, `100 m`, origin `(243350, 4508550)`). Every cell is finite and in `[0, 1]`, with `0.0` outside the footprint, so it passes the project's stricter all-array range audit. The cause of the earlier owner-reported portal error and live-portal acceptance remain unconfirmed. It has 37,654 dots and 0 on-catalogue pixels. It is unique against all 22 registry rasters: max 3-px overlap 43.25%, and 37.48% vs GEMSDOE32 B2. |
| **OK TO SUBMIT?** | **🛑 NO — do not spend a weekly slot.** A33-R3-LLC tied the current holdout best rather than beating it. Screen HOLDOUT-DTI was `0.137868` vs CSHT `0.137555` (paired Δ `+0.0003 [−0.0080, +0.0083]`, 2/4 folds). Confirmation was `0.131506` vs `0.132066` (Δ `−0.0006 [−0.0090, +0.0075]`, 2/4). Withheld positives: 60,988 per split. The selector re-checked all 9 run cards, including the parallel-session DPPS card, and found **0 eligible**. HMDT has no run card, so it cannot be eligible. |
| **Best reported artifact across the 9 focus sites** | **GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (0.2778\*)**. This is owner/user-reported, not organizer-confirmed, and is not a submission recommendation. See the audit table below. |
| **Competition-score estimate for any current research TIFF** | **NOT ESTIMABLE.** HOLDOUT-DTI is not calibrated to the contest score; do not project or translate it. |

**Downloads (A33-R3-LLC, research only):**
- **[Primary GeoTIFF, zeros outside (827 KB)](docs/downloads/gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif)**
- **[Single-TIFF .zip (184 KB)](docs/downloads/gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.zip)**
- [NaN-outside twin](docs/downloads/gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-nan.tif)
- [Writer/validator receipt](docs/downloads/receipt-gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9.json)
- [Run card](evidence/a33_r3_run_card_20261026.json)
- [Report](knowledge/16_a33_r3_llc_preregistration_and_result_20261026.md)
- [How to submit](docs/how-to-submit.html)

| Field | Value |
|---|---|
| Unique submission name | `gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros` |
| Note (104/140 chars) | `GEMS33 A33-R3-LLC V2_gamma05: scarp line-integral x CSHT prior, CELF300 37654d \| NEGATIVE \| 7f91f9f3ced9` |
| SHA-256 (.tif) | `76f9e157d01bb9bec2d98c3c5941b6114e06e0f439272d5f140af6e3584c8825` |
| Verdict | `negative`. Failed gates: `screen_beats_current_best`, `independent_confirmation`. 0 slots used. |

Earlier artifacts from today stay **OK TO DOWNLOAD / NOT OK TO SUBMIT**:
- G33-DPPS (parallel session; verdict `negative`).
- A33-R2-HMDT (parallel session; holdout **not measured**, so it is not eligible; see `IR-33-HMDT-UNGATED-01`).
- A33-R2-CSHT (verdict `duplicate`).
- A33-R3-LCHC (parallel session; verdict `negative`; see banner below — this is the only one that also passes BOTH uniqueness gates cleanly).

A33-R3-LLC is unique against both parallel-session rasters: 17.98% of its dots lie within 3 px of DPPS and 0.33% within 3 px of HMDT, with ρ ≤ 0.0093 ([lane check](evidence/a33_r3_parallel_lane_check_20261026.json)).

---

## 🟠 Parallel-session decision (2026-10-26, `G33-DPPS`, merged via PR #20): **✅ OK TO DOWNLOAD: YES** · **🛑 OK TO SUBMIT: NO (DO NOT SPEND A WEEKLY SLOT — verdict: negative)**

| Immediate Reader Question | Unmistakable Answer |
|---|---|
| **Is there a new, unique TIF?** | **✅ YES.** `gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235-zeros.tif` — a deterministic **dip-projected persistence-scarp** emission (zero learned weights; zero catalogue/H19-5/B2 pixels in its surface), generated under a SHA-frozen preregistration ([`knowledge/14_preregistered_dpps_hypotheses_20261026.md`](knowledge/14_preregistered_dpps_hypotheses_20261026.md)). It is **not a copy of any previous submission**: surface + final dots pass the duplicate guard vs **25** registry rasters (final max 3-px overlap `44.62% ≤ 70%`, max \|ρ\| `0.0213`; only `24.0%` of its dots within 3 px of GEMSDOE32 B2). |
| **OK TO DOWNLOAD?** | **✅ YES.** Single-band `float32`, `EPSG:32611`, `3730×3292`, template transform; whole array finite in `[0, 1]` (values `{0.0, 1.0}`, **0 NaN anywhere**, `0.0` outside footprint) — this primary `-zeros.tif` passes the local strict all-array range check. The earlier portal message's cause and live-portal acceptance remain unverified. `37,654` dots, `0` on-catalogue, strict saved-byte validator `pass = True`, `9/9` leakage canaries (max AUC `0.6875 ≤ 0.90`). Download: **[.tif (808 KB)](docs/downloads/gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235-zeros.tif)** · **[.zip (164 KB)](docs/downloads/gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235-zeros.zip)** · [NaN twin](docs/downloads/gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235-nan.tif) · [receipt](docs/downloads/receipt-gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235.json) · [run card](evidence/dpps_run_card_20261026.json) · [how to submit](docs/how-to-submit.html) |
| **OK TO SUBMIT TO DRIVENDATA?** | **🛑 NO — DO NOT SUBMIT.** Automated gates (no human inspector): HOLDOUT-DTI screen `0.095407` vs B1 `0.111285` (Δ `−0.015878 [−0.028932, −0.002121]`, 1/4 folds) and confirmation `0.096015` vs B1 `0.114619` (Δ `−0.018604`, 0/4) — **fails every beat-the-incumbent gate**. The mechanism itself is validated vs its pixel ablation (+`0.0226`/`+0.0231`, 8/8 folds), which is why it is kept as a measured negative result ([`knowledge/15_dpps_results_20261026.md`](knowledge/15_dpps_results_20261026.md)). Unique name `gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235-zeros`; note (82/140) `GEMS33 DPPS dip-projected persistence scarp CELF 37654d \| 111ae96bb235 \| gate FAIL`; SHA-256 `449ad2a4a3c746ef960f8e788b01e0b0cedef794a5dab5f22b0ae993b322f62d`. `0` slots spent; no upload made; **no score above 0.2778\* is claimed or projected** (\*owner-reported, not organizer-confirmed). |
| **So which of the 9 sites' files *should* I submit?** | **None today.** The highest owner-reported historical file is GEMSDOE32 B2 (`0.2778`*) — already submitted and pixel-exactly a pruning of H27-4, so re-uploading it (or GEMSDOE36/GEMSDOE28/GEMSDOE31 family members at `>93%` overlap) is a duplicate that wastes a slot. A33-R2-CSHT below passed holdout but is surface-duplicate-blocked. DPPS is unique but failed holdout. Next: a fresh preregistered lane (1 m trace-stage rebuild or reserve HMDT), not a retune. |

---

## 🟣 Parallel-session decision (2026-10-26, `A33-R3-LCHC`, this PR): **✅ OK TO DOWNLOAD: YES** · **🛑 OK TO SUBMIT: NO (DO NOT SPEND A WEEKLY SLOT — verdict: negative)**

| Immediate Reader Question | Unmistakable Answer |
|---|---|
| **Is there a new, unique TIF?** | **✅ YES.** `gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-zeros.tif` — a deterministic **least-cost hydrothermal connectivity** graph (multi-source Dijkstra + minimum spanning tree threading `1,116` catalogue-free DOE GDR #1391 thermal/vent seeds through a label-free conductivity/gravity/geodetic-strain/basement-edge resistance surface), generated under a SHA-frozen preregistration ([`evidence/a33_r3_lchc_preregistration_20261026.json`](evidence/a33_r3_lchc_preregistration_20261026.json), `SHA-256: bc4ecef34e3b81e19f41c9422fba60d99ed4c8a6c06eadb4617198753dd63a6e`). It is the **most orthogonal artifact in this repository to date**: both surface and final dots pass uniqueness against all 21 pinned registry rasters (max `|Spearman ρ| = 0.0054`; max 3-px overlap `18.6%` surface / `16.7%` final dots). |
| **OK TO DOWNLOAD?** | **✅ YES.** Single-band `float32`, `EPSG:32611`, `3730×3292`, template transform; whole array finite in `[0, 1]`, `0.0` outside footprint, `37,654` dots, `0` on-catalogue, strict saved-byte validator `pass = True`, `11/11` leakage canaries (max pooled AUC `0.5663 ≤ 0.90`; notably the **finished full surface itself** canaries at AUC `0.5001`, indistinguishable from random). Download: **[.tif (787 KB)](docs/downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-zeros.tif)** · **[.zip](docs/downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-zeros.zip)** · [NaN twin](docs/downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-nan.tif) · [receipt](docs/downloads/receipt-gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7.json) · [run card](evidence/a33_r3_lchc_run_card_20261026.json) · [full report & Round-4 slate](knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md) |
| **OK TO SUBMIT TO DRIVENDATA?** | **🛑 NO — DO NOT SUBMIT.** Automated gates: HOLDOUT-DTI screen `0.043712` vs `B1_regional 0.125441` (Δ `-0.081728 [-0.097741, -0.062859]`, `0/4` folds) and frozen confirmation `0.035199` vs `0.128184` (Δ `-0.092985 [-0.108431, -0.075215]`, `0/4` folds) — **fails every beat-the-incumbent gate**. Unlike `A33-R2-CSHT` (surface-duplicate blocked despite winning holdout) or `A33-R3-LLC` (tied CSHT), this candidate loses outright: a sparse connectivity-tree surface structurally cannot avoid the metric's `4×` false-negative penalty (`α=0.2`, `β=0.8`), regardless of its clean precision/uniqueness. Unique name `gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-zeros`; note (100/140) `GEMS33 A33-R3-LCHC: thermal/vent least-cost connectivity graph 37654d \| gate NEGATIVE \| 77337fc0c6c7`; SHA-256 `a58219e1cc9f15f0ede99863b0e5a619dbfa6946c7fdd4fb61f7050ddd5070ac`. `0` slots spent; no upload made; no score above `0.2778`\* is claimed or projected. |
| **Round-4 hypothesis slate** | Five ranked, untried hypotheses for the next round (`A33-R4-COULOMB` — Okada elastic Coulomb-stress-transfer from mapped USGS Quaternary faults, already pinned locally; `A33-R4-CURVTRACE` — multi-azimuth curvilinear LiDAR trace continuity; plus `HMDT`/`PFRT`/`PALEOTEMP` carried over from the `A33-R2` reserve list), each with named layers, physical mechanism, differentiation from every mechanism already tried across this repo, external-data viability, and expected-DTI-gain-vs-cost ranking: [`knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md`](knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md). None executed or budgeted this session. |

Verify (no rerun — frozen decided result): `.venv/bin/python scripts/evaluate_holdout.py --verify-a33-r3-lchc`.

---

## 🟡 Previous Decision (2026-10-26, `A33-R2-CSHT`): **OK TO DOWNLOAD: YES** · **OK TO SUBMIT: NO (DO NOT SPEND A WEEKLY SLOT)**

| Immediate Reader Question | Unmistakable Answer |
|---|---|
| **OK TO DOWNLOAD?** | **✅ YES — READY TO DOWNLOAD.** Validated single-band `float32` GeoTIFF & `.zip` matching `sample_submission.tif` (`EPSG:32611`, `3730×3292`, exact `100 m` geotransform), strictly in `[0, 1]` (`{0.0, 1.0}`, `0` NaN across all `12,279,160` cells in `-zeros.tif`; `5,167,373` finite `[0, 1]` footprint cells in `-nan.tif` twin). Placed `final_dots` (`37,654` dots via 300 m submodular `CELF`) pass **21 / 21** registry uniqueness checks (`max |Spearman ρ| = 0.0416 <= 0.90`, `max 3-px dot overlap = 69.34% <= 70%`, and only **`35.86%`** within 3 px of `GEMSDOE32` `B2`). |
| **OK TO SUBMIT TO DRIVENDATA?** | **🛑 NO — DO NOT SPEND ONE OF THE 3 WEEKLY SLOTS (`verdict: duplicate` / `ok_to_submit: false`).** Even though `A33-R2-CSHT` won **`8 / 8` spatial holdout folds** against incumbent `B1_regional` (`screen HOLDOUT-DTI = 0.136716` vs `0.112418` [`0.113244` recorded], `4/4` folds; orthogonal `confirmation HOLDOUT-DTI = 0.131169` vs `0.115122`, `4/4` folds) and passed **`11 / 12`** automated `promotion.py` gates (`50/50` leakage canaries `<= 0.90`, `21/21` `final_dots` uniqueness, `100%` format audit), its **pre-placement continuous surface peaks** exceeded `70%` 3-px overlap against 2026-10-25 sibling regional-HGB rasters `GEMSDOE30` `MSDB1` (user-reported `0.1462`), `GEMSDOE24` `GVC1` (`0.0859`), and `GEMSDOE25` `H66` (`0.0742`). Cross-lane convergence with `MSDB1` (`0.1462`) confirms this surface family will **not** beat `GEMSDOE32` `B2` (`0.2778`). |

### Direct Download Links (`A33-R2-CSHT`, 2026-10-26)
- **[Download Primary `[0, 1]` Zero-Outside GeoTIFF (`.tif`, 827 KB)](docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif)** · **[Download Primary `.zip` (169 KB)](docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.zip)**
- [Download Official-Text `NaN`-Outside Twin (`.tif`, 1.59 MB)](docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-nan.tif) · [Download `NaN`-Twin `.zip` (281 KB)](docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-nan.zip)
- [Writer & Validator Receipt](docs/downloads/receipt-gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad.json) · [Authoritative Round 2 JSON Run Card](evidence/a33_r2_run_card_20261026.json) · [Submission Instructions Subpage](docs/how-to-submit.html) · [Prior Round 1 (`A33-L1`) Run Card](evidence/a33_l1_run_card.json)

| Artifact Field | Verified Value |
|---|---|
| **Unique Submission Name** | `gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros` |
| **Short Note (`98 / 140` chars)** | `GEMS33 A33-R2-CSHT: cover+hydrothermal transfer + 300m CELF 37654d \| gate DUPLICATE \| 0b78c04d5fad` |
| **Primary `.tif` SHA-256** | `14ab452c22aaf07444cd02e589fce4627d682e99f44c63e78dc1383955e0c602` |
| **`NaN`-Twin `.tif` SHA-256** | `c1173e63bec4f2f673074e6951218ac3d269f25994b322e9eff39905b9e64af5` |
| **Grid & Range Audit** | `1` band `float32`, `EPSG:32611`, `3730 × 3292`, `100 m` spacing, origin `(243350.0, 4508550.0)`, `37,654` positive `{0,1}` dots, `0` catalogue overlap, `pass = True` |
| **Automated Gate Status** | **`11 / 12` `promotion.py` gates PASS** (`screen` `4/4`, `confirm` `4/4`, `50/50` canaries, `21/21` `final_dots` uniqueness, saved-byte format); **1 gate (`surface_not_duplicate`) BLOCKED** (`ok_to_submit = false`, `0` slots spent) |

---

### Clean audit table — best report, uniqueness, and download/submit status

The complete linked table is [`registry/focus_best_artifact_summary_20261026.csv`](registry/focus_best_artifact_summary_20261026.csv) ([JSON](registry/focus_best_artifact_summary_20261026.json)). It covers the nine classic best-reported artifacts and 36 pairwise comparisons among them, **not a global registry**. All reported values lack an organizer receipt in this checkout; **score estimate: NOT ESTIMABLE**. The pinned owner-mirror artifact may be downloaded for research, but no historical artifact below should be submitted as a new unique prediction: each breaches at least one gate (`|ρ| > 0.90` OR `>70%` candidate-dot coverage within 3 px).

| Site | Best reported artifact | Reported value | Score-evidence class | Max `|ρ|` vs peer | Max 3-px candidate-dot coverage vs peer | Download / submit |
|---|---|---:|---|---:|---:|---|
| GEMSDOE24 | H25-1 | 0.2477* | USER/OWNER-REPORTED | 0.9896 (GEMSDOE27) | 100.00% (GEMSDOE25) | Download from pinned mirror / Do not submit |
| GEMSDOE25 | D2.8 | 0.2600* | USER/OWNER-REPORTED | 1.0000 (GEMSDOE30) | 100.00% (GEMSDOE24) | Download from pinned mirror / Do not submit |
| GEMSDOE27 | topo-gap | 0.2449* | USER/OWNER-REPORTED | 0.9896 (GEMSDOE24) | 98.02% (GEMSDOE24) | Download from pinned mirror / Do not submit |
| GEMSDOE28 | H36-1 | 0.2710* | USER/OWNER-REPORTED | 0.7137 (GEMSDOE31) | 100.00% (GEMSDOE24) | Download from pinned mirror / Do not submit |
| GEMSDOE30 | D2.8 / 91eae1ca | 0.2600* | USER/OWNER-REPORTED | 1.0000 (GEMSDOE25) | 100.00% (GEMSDOE24) | Download from pinned mirror / Do not submit |
| GEMSDOE31 | H27-4 solo D2.8 | 0.2708* | USER/OWNER-REPORTED | 0.9676 (GEMSDOE32) | 100.00% (GEMSDOE24) | Download from pinned mirror / Do not submit |
| GEMSDOE32 | H33-2 B2 | 0.2778* | USER/OWNER-REPORTED | 0.9843 (GEMSDOE36) | 100.00% (GEMSDOE24) | Download from pinned mirror / Do not submit |
| GEMSDOE33 | H33d | 0.2632* | USER/OWNER-REPORTED | 0.8193 (GEMSDOE31) | 99.71% (GEMSDOE27) | Download from pinned mirror / Do not submit |
| GEMSDOE36 | Anderson | 0.2750* | USER/OWNER-REPORTED | 0.9843 (GEMSDOE32) | 97.58% (GEMSDOE27) | Download from pinned mirror / Do not submit |

*Values are OWNER/USER-REPORTED, not ORGANIZER-CONFIRMED and not calibrated estimates. Maxima compare each row only with the other eight classic artifacts; the evidence and pinned file identity are in the CSV/JSON.

## 1. Executive Summary of All Nine Focus Sites (`GEMSDOE24`–`GEMSDOE36`)

All **21** SHA-256-pinned rasters (`12` classic focus-site artifacts + `5` newly user-reported 2026-10-25 focus-site artifacts + `4` local `GEMSDOE33` historical artifacts) are audited in [`registry/focus_rasters_20261026.json`](registry/focus_rasters_20261026.json). Every historical DrivenData figure below is **`USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)`**; no organizer submission receipt is stored in this checkout, and zero leaderboard scraping was performed (`IR-33-TERMS-01`).

| Focus Site | Classic Highest-Reported Artifact (`Dots`; `Reported DTI*`) | 2026-10-25 Artifact (`Dots`; `3-px vs B2`; `Reported DTI*`) | Executive Suitability Summary |
|---|---|---|---|
| **GEMSDOE24** | `GEMSDOE24-h25-1-d1p5-20261004-989f59505db1.tif` (`60,069`; `0.2477`*) | `gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif` (`37,654`; `36.62%`; `0.0859`*); `RSHG1` (`HOLDOUT-DTI 0.1387`, blocked at `72.69% > 70%`) | Canonical source of `vendor/gems24_template`. `H25-1` (`d=1.5`) was over-dense (`60k` dots inflating `0.2·FP_w`); `GVC1` (`0.0859`*) showed negative lineaments fire on lithologic contacts; `RSHG1` flagged cross-lane supervised-ridge convergence. **Not suitable to submit.** |
| **GEMSDOE25** | `gems25-h19-5-d2p8-20261004T201317Z-e56ea318af89.tif` (`44,090`; `0.2600`*) | `gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif` (`44,832`; `30.38%`; `0.0742`*) | Classic `d2.8` is pixel-identical (`Jaccard = 1.000`) to `GEMSDOE30` `91eae1ca` and retains `6,436` `<= 200 m` catalogue-halo dots. `H66` (`0.0742`*) showed gravity-flank detectors over-fire on buried pediments/intrusives. **Not suitable to submit.** |
| **GEMSDOE27** | `gems27-topo-gap-20261004-5512495c6bd1.tif` (`61,328`; `0.2449`*) | `gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite.tif` (`37,654`; `56.12%`; **`0.2190`**\*) | `topo-gap` (`61k` dots) was an over-dense superset of `G24` `H25-1`. **`H29` (`0.2190`*) is the strongest independent non-`H19-5` 2026-10-25 upload across all 9 sites**, pairing hydrothermal + piedmont + 1 m LiDAR features with 300 m `CELF` allocation, though still `0.0588` below `G32` `B2` (`0.2778`*). |
| **GEMSDOE28** | `h36-1-r1-band-prune-20261004T231500Z-b531dae0a36f-zeros.tif` (`37,660`; `0.2710`*); `h27-4` (`40,199`; `0.2708`*) | `gems28-s18-mxtp-20261025-3e95505c011a-allfinite.tif` (`11,082`; `17.14%`; `0.0217`*) | Classic `H36-1`/`H27-4` belong to the `H19-5` pruning chain (`>93%` overlap with `B2`). `S18` (`11,082` dots, `0.0217`*) starved dot recall against `0.8·FN_w`. **Not suitable to submit.** |
| **GEMSDOE30** | `gems30-d28-baseline-20261004-91eae1ca-zeros.tif` (`44,090`; `0.2600`*) | `gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif` (`44,090`; `39.18%`; `0.1462`*) | Classic `91eae1ca` equals `G25` `d2.8` byte-for-byte. `MSDB1` (`0.1462`*) trained a 31-feature OOF `HistGradientBoostingClassifier` on `labels.tif`; its `0.1462`* outcome benchmarks pure catalogue-supervised HGB surfaces and caught our pre-placement surface convergence in `A33-R2-CSHT`. **Not suitable to submit.** |
| **GEMSDOE31** | `h27-4-r1-solo-d2-8-20261004T195206Z-8acb75e1-zeros.tif` (`40,199`; `0.2708`*) | `H31R-1-relay-damage-research` (unscored; failed holdout gate) | Classic `solo` deleted `3,891` `d_cat == 1` halo pixels from `d2.8` (`0.2600 -> 0.2708`*), leaving `2,545` `1 < d_cat <= 2` halo pixels behind. **Superseded by `G32` `B2`; duplicate-blocked.** |
| **GEMSDOE32** | **`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`** (`37,654`; **`0.2778`**\*) | `gems32-sbir1-20261025` (unscored; failed holdout gate) | **9-site reported peak (`0.2778`*).** Equals `G31` `solo` minus `2,545` `1 < d_cat <= 2 px` boundary-halo pixels (`pixel_exact_match = True`). Historical benchmark; cannot be copied or lightly perturbed under non-duplication rules. |
| **GEMSDOE33** *(This Repo)* | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-zeros.tif` (`41,865`; `0.2632`*, retired) | `A33-L1` (negative); `A33-R2-CSHT` (HOLDOUT-DTI `0.136716`/`0.131169`, duplicate); `G33-DPPS` (HOLDOUT-DTI `0.095407`/`0.096015`, negative); `A33-R2-HMDT` (holdout not measured); `A33-R3-LLC` (HOLDOUT-DTI `0.137868`/`0.131506`, a tie with CSHT, negative); **`A33-R3-LCHC`** (HOLDOUT-DTI `0.043712`/`0.035199`, negative — but the only artifact here passing BOTH uniqueness gates, max 3-px overlap `18.6%`/`16.7%`) | The best fold-safe surfaces here reach HOLDOUT-DTI ≈ 0.13–0.14; sparse connectivity-graph surfaces (`A33-R3-LCHC`) lose on recall despite perfect uniqueness. The informational H19-5 reference (not fold-safe) reaches 0.162 on the same split. **No GEMSDOE33 artifact is OK to submit.** The newest unique TIFs are OK to download. |
| **GEMSDOE36** | `gemsdoe36-anderson-dipslip-h33b2-k1200-20261004-9b9ea4e6-zeros.tif` (`38,854`; `0.2750`*) | `gems36-mstd1-mohr-slip-dilation-20261025` (unscored; failed holdout gate) | Classic `Anderson` = exact `G32` `B2` + `1,200` tip dots (`Spearman = 0.9843` vs `B2`), lowering reported score `0.2778 -> 0.2750`*. **Not suitable to submit.** |

*\*All historical DrivenData DTI figures are **USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)**; user-supplied leaderboard figures `0.4413` and `0.3195` are likewise unauthenticated aspirational context (`IR-33-SCORE-01`).*

---

## 2. Why `GEMSDOE32` `B2` Achieved `0.2778` — And Can We Beat `0.2778`?

1. **Exact Pixel-Algebraic Mechanism (`evidence/focus_raster_audit_20261025.json`):**
   `GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (`37,654` dots) added **zero** fault detections to `19GEMSDOE` `H19-5`. Instead, starting from `d=2.8` Poisson thinning (`44,090` dots, `0.2600`*), `G31` (`H27-4`) stripped `3,891` dots at $0 < d_{\text{cat}} \le 100\text{ m}$ (`0.2708`*), and `G32` (`B2`) stripped the remaining `2,545` dots at $100 < d_{\text{cat}} \le 200\text{ m}$ (`0.2778`*, `pixel_exact_match = True`).
2. **Boundary-Halo & 300 m Triangular-Kernel Proof:**
   Under $\text{DTI} = \text{TP}_w / (\text{TP}_w + 0.2\,\text{FP}_w + 0.8\,\text{FN}_w)$ with pixel-exact `0 m` masking of `existing_faults.tif` ($K$) and 300 m (`3 px`) triangular MAX kernel $K_{\triangle}(d) = \max(0, 1 - d/3)$, natural Quaternary fault scarps are `100–250 m` wide while $K$ is `1 px` (`100 m`) wide. Detectors therefore fire across the `<= 200 m` scarp slope flanking $K$ where no *unmapped* parallel fault exists ($\Delta \text{TP}_w \approx 0$, $\Delta \text{FP}_w = +1$), while true along-strike fault continuations starting past $K$'s tips remain covered from $d_{\text{cat}} = 2.5\text{ px}$ at kernel weight $0.50\text{–}0.83$. Pruning $d_{\text{cat}} \le 2\text{ px}$ strictly shrank $0.2\,\text{FP}_w$ at near-zero $\text{TP}_w$ loss; conversely, grafting `1,200` tip dots (`G36`: `0.2750`*) or `1,666` stepover dots (`G33` `H33-D`: `0.2632`*) missed real curved traces beyond `300 m` and failed the marginal break-even threshold $\Delta \text{TP}_w / \Delta \text{FP}_w > 0.2\,\text{DTI}/(1 - 0.8\,\text{DTI}) = 0.0714$.
3. **Can `GEMSDOE33` Beat `0.2778` Right Now?**
   - **Within `GEMSDOE33`'s strict analog-transfer lane (`zero H19-5/B2 pixels`, supervised only on incomplete `labels.tif`):** **No.** Across all 9 focus sites, pixel/window classifiers supervised solely on positive-unlabeled `labels.tif` empirically achieve `0.0742`–`0.2190`* (`G30-MSDB1 = 0.1462`*, `G27-h29 = 0.2190`*) because unlabeled real faults in `labels.tif` act as false negatives during training while broad lithologic/intrusive contacts mimic mapped range fronts.
   - **Tested this session and refuted as sufficient:** combining (i) strike-integrated 1 m scarp line evidence, (ii) the void-safe CSHT transfer and (iii) 300 m CELF allocation (A33-R3-LLC) gave **no** holdout gain over CSHT alone (Δ `+0.0003` screen / `−0.0006` confirm, CIs span 0). The likely reason is that the 300 m kernel already forgives sub-kernel mislocation.
   - **What remains open:** on the same withheld segments, the fixed H19-5 surface (the B2 family; not fold-safe) beats CSHT by `+0.0242 [+0.0150, +0.0328]` (4/4 folds). A fold-safe re-derivation of the H19-5 multiline-corroboration recipe remains a historical diagnostic lead, not an authorized next experiment. The current task still lacks an explicit method lane and canonical shared-template identity; do not run it until those blockers are resolved. Details and limitations: [`knowledge/16_a33_r3_llc_preregistration_and_result_20261026.md`](knowledge/16_a33_r3_llc_preregistration_and_result_20261026.md).
---

## 2b. Round 3 (`A33-R3`): preregistered slate and result (2026-10-26)

The slate was frozen in [`evidence/a33_r3_preregistration_20261026.json`](evidence/a33_r3_preregistration_20261026.json) (git `61e79c6`, 04:40:15Z) before any R3 code existed. It was ranked by expected improvement against cost:

1. **A33-R3-LLC** (run): Hessian ridge (Steger 1998 / Frangi 1998) of 1 m LiDAR scarp descriptors, or 100 m slope in LiDAR voids, integrated along 12 azimuths (500 m × 75 m kernel) with NMS, multiplied by the fold-trained CSHT prior. Named mimic: Lake Lahontan shorelines (Adams & Wesnousky 1998).
2. **A33-R3-SGC** (reserve): conformity of scarp strike to the regional mapped-fault grain.
3. **A33-R3-MAGT** (reserve): tilt-derivative zero-crossings beneath deep cover. Duplicate risk is high because of GEMSDOE76 tiltworm.
4. **A33-R3-LSRT** (blocked): reject iso-elevation shoreline chains. Needs the USGS 3DEP absolute DEM, which is unreachable from the sandbox.
5. **A33-R3-PALEOTEMP** (blocked): DOE GDR #1391, also unreachable.

| HOLDOUT-DTI (`gems-segment-pooled-v1`, 60,988 withheld) | Screen | Confirmation |
|---|---:|---:|
| **A33-R3-LLC V2 (γ=0.5)** | **0.137868 [0.1286, 0.1479]** | **0.131506 [0.1208, 0.1414]** |
| A33-R2-CSHT (in-run) | 0.137555 [0.1261, 0.1498] | 0.132066 [0.1201, 0.1440] |
| B1_regional | 0.110783 | 0.113576 |
| matched_random | 0.073931 | — |
| H19-5 reference (not fold-safe) | 0.162036 [0.1516, 0.1725] | — |

- **Canaries:** max fold AUC 0.6743 ≤ 0.90.
- **V1 (γ=1):** surface-duplicate of A33-R2-CSHT (79.15%) and dropped before evaluation.
- **Verdict:** **negative**. The reserve experiment 3/3 was not used, and nothing was retuned.

---

## 3. Preregistered Round 2 Geological Hypotheses (`A33-R2`)

Five untried hypotheses were formulated and SHA-256-frozen **prior to model implementation** in [`knowledge/12_preregistered_a33_r2_hypotheses_20261026.md`](knowledge/12_preregistered_a33_r2_hypotheses_20261026.md) and [`evidence/a33_r2_preregistration_20261026.json`](evidence/a33_r2_preregistration_20261026.json) (`SHA-256: f6144c2b6e0cd5bddb0966d9321697be3bb5a070808559a94f38eddcd2a70268`):

1. **`A33-R2-CSHT` — Cover-Stratified Multi-Physics & Hydrothermal-Conduit Analog Transfer + 300 m Submodular `CELF` Crest Allocation** *(Selected & Executed; viable on pinned 17 inputs)*: Fixes `IR-33-LIDAR-VOID-01` (`1,272,913` void cells preserved as `lid_valid = 0`, `lid_* = NaN`), fuses a 34-channel regional HGB, a 24-channel topography-free basin-upweighted subsurface/kinematic HGB, and a 16-channel 3 km local-contrast hydrothermal-conduit HGB across `1,116` INGENIOUS thermal/vent cells (`temp_c >= 37 °C` or `geothermquartz_c >= 100 °C`, splay-safe `d_neg > 800 m`), and places `37,654` dots via lazy-greedy 300 m triangular-kernel `CELF`.
2. **`A33-R2-HMDT` — Hydrothermal Magnetite-Destruction × Clay-Cap Signed Dipole Transfer** *(Reserve; viable on pinned cache)*: Signed cross-gradient $\nabla\text{cond\_surf}\cdot\nabla(\text{TMI}_{\text{up150}}-\text{RTP})$ gated by `iso_grav_anom_hg` inside dilational strain zones.
3. **`A33-R2-PFRT` — Listric Dip-Projected Basement-to-Piedmont Offset Vector Transfer** *(Reserve; viable on pinned cache)*: Projects buried `iso_grav_anom_hg` crests updip by $z_{\text{base}}\cot\delta$ ($\delta\in[45^\circ,65^\circ]$) along $-\nabla z_{\text{base}}$ onto piedmont flexures.
4. **`A33-R2-PALEOTEMP` — Paleogeothermal Sinter/Tufa & 2 m Shallow Temperature Probe Conduit Transfer** *(Deferred outside 17-input pin contract)*: Official DOE GDR #1391 (`https://gdr.openei.org/submissions/1391`, CC BY 4.0); verified in sibling `GEMSDOE24@fc2bc6f3`, direct `gdr.openei.org` egress blocked here.
5. **`A33-R2-BRIDGE3D` — Field-Verified BRIDGE LiDAR Picks + USGS 3D Slip/Dilation Tendency Transfer** *(Blocked in sandbox)*: DOE GDR #1682 (`https://gdr.openei.org/submissions/1682`) + USGS ScienceBase `10.5066/P9YL58W6` (`https://www.sciencebase.gov/catalog/item/6296974dd34ec53d276bb33d`); raw archives unreachable under sandbox outbound host allowlist.

---

## 4. Round 2 (`A33-R2-CSHT`) Holdout, Canary & Uniqueness Evidence

All performance figures below are **`HOLDOUT-DTI`** (`evaluator_version = "gems-segment-pooled-v1"`, `60,988` withheld catalogue positives, 10 km block-bootstrap 95% CI) — **not** competition scores or projections:

| Campaign Experiment | Split ID & Buffer | `B1_regional` Incumbent | **`A33-R2-CSHT` Candidate** | Paired $\Delta$ vs `B1_regional` (`95% CI`) | Fold Wins |
|---|---|---:|---:|---|---:|
| *Prior Round 1 (`A33-L1`, Exp 1/3)* | `quadrant-buffered-15px-v1` (`1.5 km`) | `0.113244 [0.1028, 0.1242]` | `0.108374 [0.0976, 0.1194]` | `-0.004870 [-0.010900, +0.001226]` | `0 / 4` |
| **Round 2 Primary Screen (Exp 2/3)** | `quadrant-buffered-15px-v1` (`1.5 km`) | `0.112418 [0.1016, 0.1235]` | **`0.136716 [0.1191, 0.1544]`** | **`+0.024298 [+0.012427, +0.035833]`** | **`4 / 4`** |
| **Round 2 Frozen Confirmation (Exp 3/3)** | `diagonal-wedge-buffered-20px-confirm-v1` (`2.0 km`) | `0.115122 [0.1038, 0.1268]` | **`0.131169 [0.1152, 0.1467]`** | **`+0.016047 [+0.003817, +0.028030]`** | **`4 / 4`** |

- **Shared-Stack Bug Fix Impact (`IR-33-LIDAR-VOID-01`):** In `NE_LidarGapHeavy` (`24.63%` footprint LiDAR void), `HOLDOUT-DTI` rose from `0.134070` (`B1_regional`) to **`0.165257`** (`+0.031188`); in `SE`, from `0.110546` to **`0.157058`** (`+0.046512`).
- **50-Channel Leakage Canary:** `50 / 50` channels (`34` base + `16` 3 km hydrothermal local-contrast channels) passed standalone `SegmentHoldout.canary` (`max pooled two-sided AUC = 0.7209`, `max fold two-sided AUC = 0.7685 <= 0.90`). Forbidden CSV column `dist_known_fault_px` is hard-blocked (`IR-33-CSV-DIST-FAULT-01`).
- **21-Raster Uniqueness Audit ([`evidence/a33_r2_uniqueness_20261026.json`](evidence/a33_r2_uniqueness_20261026.json)):**
  - **Final Placed Dots (`final_dots`, `37,654` `CELF-300m` dots):** **PASS (`21 / 21`)** — `max |Spearman ρ| = 0.0416 <= 0.90`; `max 3-px dot overlap = 69.34% <= 70%` (`G30-MSDB1`), `43.10%` (`G27-topo-gap`), **`35.86%` (`G32-B2`)**, **`35.19%` (`G33-A33-L1`)**, `31.18%` (`G27-h29`).
  - **Pre-Placement Surface (`surface`):** **FAIL-CLOSED STOP** — top pre-placement surface peaks exceeded `70%` 3-px overlap against 2026-10-25 sibling HGB rasters `G30-MSDB1` (`91.11%` unthinned / `77.82%` matched-37k 1-px NMS crests), `G24-gvc1` (`88.49%`), and `G25-h66` (`73.41%`), while passing all 18 other rasters (`<= 65.11%`). Also documented `IR-33-SPEARMAN-SPARSE-CEILING-01` ($\rho_{\max} = \sqrt{3p(1-p)} \approx 0.159$ on continuous-vs-binary pairs). Campaign stopped at `3 / 3` experiments with zero post-hoc retuning.

---

## 5. Official Data Sources, Provenance & Standing Brief

| Dataset / Source | Official Trusted Link | License / Status in Workspace |
|---|---|---|
| **DrivenData #306 DOE GEMS Competition, Problem & Rules** | [Overview](https://www.drivendata.org/competitions/306/competition-doe-gems/) · [Problem/Metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [Rules](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/) · [Reference Repo](https://github.com/drivendataorg/gems-prize-reference-solution) | Competition specification; no live portal auth/scraping (`IR-33-TERMS-01`); 17 inputs restored from SHA-256-pinned owner mirrors (`IR-33-MIRROR-01`); `sample_submission.tif` used strictly for grid/footprint (`IR-33-TEMPLATE-01`). |
| **USGS GeoDAWN Airborne Magnetic & Radiometric Survey** | [USGS Data Record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [ScienceBase `10.5066/P93LGLVQ`](https://www.sciencebase.gov/catalog/item/61969f02d34eb622f692f96c) | Public Domain (CC0); contractor radiometric ratios (`ext_ThK`, `ext_UK`) & upward-continued `ext_TMI_up150` verified via pinned `geodawn_rad_u8.tif` / `geodawn_extensions_u8.tif`. |
| **GBCGE / UNR DOE INGENIOUS Great Basin Play Fairway** | [INGENIOUS Project](https://gbcge.org/current-projects/ingenious/) · [DOE GDR #1391 (`10.15121/1881483`)](https://gdr.openei.org/submissions/1391) | CC BY 4.0; `27,092` well/spring records (`1,095` hot/geothermometer seed cells) & `21` volcanic vents verified in pinned CSVs (`dist_known_fault_px` column blocked). |
| **USGS 3DEP-derived LiDAR scarp descriptors** | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · `data/lidar_scarp_features.json` (owner-mirror copy) | Derived from 1 m DEM tiles at 2 m work resolution, aggregated to the 100 m competition grid; 706/716 listed tiles succeeded and about 75.37% of footprint cells are valid. Raw 1 m DEM tiles are absent from the restored data directory; owner-mirror provenance is not organizer authentication. |
| **Full user-reported score list (126 rows, GEMSDOE…GEMSDOE92)** | [`registry/user_reported_scores_20261026.csv`](registry/user_reported_scores_20261026.csv) | USER-REPORTED, transcribed from the 2026-10-26 brief; blank scores kept blank; not organizer-confirmed (`IR-33-LEDGER-STALE-01`). |
| **Preserved Standing Brief & Operating Rules** | [`standing_prompt.md`](standing_prompt.md) · [`AGENTS.md`](AGENTS.md) · [`registry/irregularities.json`](registry/irregularities.json) | Full consolidated standing prompt, 2026-10-26 Round 2 addendum, and fail-closed promotion contract. |

### Reproduce & Run All Automated Checks (Zero Human Inspector Needed)

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
GEMS_DATA_DIR=$PWD/.cache/gemsdata .venv/bin/python scripts/restore_data.py --group all --data-dir .cache/gemsdata
.venv/bin/python scripts/evaluate_holdout.py --verify-recorded
.venv/bin/python scripts/evaluate_holdout.py --verify-a33-r2
.venv/bin/python scripts/evaluate_holdout.py --verify-a33-r3-lchc
.venv/bin/python scripts/validate_submission.py --submission docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif --template data/sample_submission.tif --strict-zero-outside
.venv/bin/python scripts/validate_submission.py --submission docs/downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-zeros.tif --template data/sample_submission.tif --strict-zero-outside
.venv/bin/python scripts/select_submission.py   # automated OK-TO-SUBMIT decision
PYTHON=.venv/bin/python bash scripts/run_checks.sh
```

---

## Operating Prompt — Embedded for Every Session (2026-10-26)

Source: user request (parallel-run protocol, GEMSDOE24/25/27/28/30/31/32/33/36 focus sites, highest-urgency submission generation). Read this section at start of every session to confirm we are building what is aimed for.

### Core Values
- Maximize P(Win): decide by evidence, not hope; prefer leakage-audited holdout over projection.
- Own the Outcome: fix shared bugs once, report them; never keep private forks; make negative results visible.

### Parallel-Run Protocol (must follow)
1. LANE: stay inside the explicitly assigned single-method paragraph. The current task provides no identifiable lane; do not infer one from historical analog-transfer text or an existing HMDT artifact. No experiment until the lane is explicitly resolved.
2. REUSE, DON'T REBUILD: use cached features and the shared evaluator/writer selected by the coordinator. The current task has not identified the canonical shared-template commit/path; do not select an arbitrary same-named script or create a private evaluator fork.
3. LABEL EVERY NUMBER: HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (submission-page receipt). Never label a projection as a score.
4. LEAKAGE CANARY: test each feature alone; AUC > 0.90 means leakage until proven otherwise.
5. RUN CARD: end with JSON card (hypothesis; mechanism; named non-fault mimic process; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output; submission name + ≤140 char note; verdict promote / negative).
6. BUDGET: stop after 3 experiments or 2 hours; do not pick submissions; promotion to real slot is separate selector step.

### Highest-Urgency Requirements
- Project aim: generate a genuinely UNIQUE TIF after an explicit lane and canonical template are resolved; do NOT copy a previous submission except for learning. Current review produced no new TIFF and does not claim this aim was completed.
- Must be OBVIOUS whether OK to download and OK to submit (format gates + uniqueness + holdout status clearly labeled).
- Must pass validation: single-band float32 GeoTIFF, EPSG 32611, 3730×3292, 100 m transform, values inside footprint strictly in [0,1] (no NaN inside footprint for zero-variant; NaN only outside for nan-variant), no NaN inside footprint.
- Must include easy download (.tif + .zip) with note ≤ 140 chars.
- Must include executive summary per focus site (GEMSDOE24/25/27/28/30/31/32/33/36) identifying best reported submission and why.
- Must verify no hallucinations; provide trusted-source discovery links with a clear statement of whether each page/payload was freshly verified; work line by line.

### Our Focus Sites — Best Reported Artifacts (USER-REPORTED, NOT ORGANIZER-CONFIRMED — no organizer receipt stored)
- GEMSDOE24: H25-1 (60,069 dots, 0.2477*); new GVC1 (0.0859*, negative lineament)
- GEMSDOE25: d2.8 (44,090 dots, 0.2600*); H66 (0.0742*)
- GEMSDOE27: topo-gap (61,328 dots, 0.2449*); H29 (37,654 dots, 0.2190*) — strongest independent 2026-10-25 upload
- GEMSDOE28: H36-1 / H27-4 (37,660 / 40,199 dots, 0.2710* / 0.2708*); S18 (0.0217*)
- GEMSDOE30: 91eae1ca (44,090 dots, 0.2600*); MSDB1 (44,090 dots, 0.1462*)
- GEMSDOE31: solo d2.8 (40,199 dots, 0.2708*)
- GEMSDOE32: B2 (37,654 dots, 0.2778*) — 9-site reported peak; exact pixel-algebraic mechanism known (pruning of d=2.8 by halo removal)
- GEMSDOE33: A33-R2-CSHT (37,654 dots, HOLDOUT-DTI 0.136716/0.131169, format pass, duplicate-blocked by surface convergence with G30 MSDB1); H33d analog (41,865 dots, 0.2632*)
- GEMSDOE36: Anderson (38,854 dots, 0.2750*); exact B2 + 1,200 tip dots

*All historical DTI figures are USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED); aspirational leaderboard context 0.3195 / 0.4413 unverified; see registry/focus_rasters_20261026.json and evidence files for audit.

### Historical A33-R2-HMDT artifact (not evaluated; not generated in this review)

- Name: `gemsdoe33-a33-r2-hmdt-20261026-hmdt-unique-zeros` / `-nan`.
- Mechanism: A33-R2-HMDT (magnetite-destruction × clay-cap coherence + 300 m CELF).
- The prior artifact record reports 42,000 dots and format/uniqueness checks; those checks do not establish scientific validity.
- **HOLDOUT-DTI was never measured for HMDT.** Restoring inputs and preparing features during this review does not retrofit a holdout result or validate the old emission.
- **OK TO SUBMIT: NO.** It has no eligible run card and has not demonstrated improvement over the current comparable holdout best.

---

## 6. Suggested next work & limitations (current review: do not experiment yet)

**Immediate gate:** the task does not contain an identifiable standalone single-method lane paragraph, and does not explicitly identify the canonical shared-template commit/path. A pin in this repository or a same-named script at another site is not enough to resolve that authorization. Therefore, do not run H19-5 re-derivation, Coulomb, Curvtrace, PFRT, or another model until the assigned lane/template are explicit. Continue only with code/doc/test review and source/provenance auditing while blocked.

**Qualitative future research slate** (planning only; no numeric DTI or score estimate):
1. `A33-R4-COULOMB`: elastic Coulomb stress-transfer from pinned QFFD attributes; moderate–high unproven potential, moderate implementation cost. Local inputs are owner-mirror copies; verify official provenance/schema before use.
2. `A33-R4-CURVTRACE` (reframed): continuity analysis on available 100 m-grid LiDAR-derived descriptors; possible morphology signal, but the original 1 m DEM tile stack is absent, coverage is partial, and shorelines/terraces/roads/streams mimic faults.
3. `A33-R4-PFRT`: listric dip-projected basement-to-piedmont transfer; low–moderate cost but high duplicate-convergence risk against regional geophysics.
4. `A33-R4-PALEOTEMP`: relict probe/sinter transfer; blocked until the named GDR #1391 product is specifically obtained, pinned and audited.

The full hypotheses, signatures, named non-fault mimics, source limitations and qualitative ranks are in [`knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md`](knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md) and [`docs/hypotheses.html`](docs/hypotheses.html). `A33-R2-HMDT` is an existing artifact whose holdout was not measured; it is not a new hypothesis or eligible candidate.

**Limitations:**
- Hide-and-recover HOLDOUT-DTI withholds whole catalogue segments with buffers. It is a proxy and cannot measure private expert truth; it must not be translated into the competition metric or leaderboard score.
- No organizer receipts are stored for historical focus-site values. They remain USER/OWNER-REPORTED, including the 0.2778 B2 claim. The brief's 0.3195 and 0.4413 leader values conflict and remain unverified.
- The nine-artifact uniqueness analysis contains 36 pairwise comparisons among nine classic rasters; it is not a complete global registry. Every listed classic best breaches at least one threshold.
- Seventeen local inputs were restored and hash-verified against pinned owner mirrors, not organizer-authenticated sources. The 121-channel cache is gitignored, was built with detector training skipped, and is not itself evidence that any feature is valid.
- The raw 1 m LiDAR DEM tile stack and the specific paleotemperature/sinter product are absent from the restored inputs. Current 3DEP scarp descriptors are a partial-coverage 100 m-grid derivative made from a 2 m work-resolution product.
- The weekly slot count and current portal acceptance cannot be observed from this workspace. No automatic/manual leaderboard monitoring, upload, or organizer score retrieval was performed in this review.

**Auditable review records:** [`evidence/repository_review_20261026.json`](evidence/repository_review_20261026.json), [`evidence/data_preparation_20261026.json`](evidence/data_preparation_20261026.json), and [`registry/focus_best_artifact_summary_20261026.csv`](registry/focus_best_artifact_summary_20261026.csv) / [JSON](registry/focus_best_artifact_summary_20261026.json).
