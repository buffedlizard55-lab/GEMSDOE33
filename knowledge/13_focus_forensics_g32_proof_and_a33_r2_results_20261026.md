# Nine-Site Focus Review, PhD Forensics of `GEMSDOE32` (`0.2778`), and `A33-R2-CSHT` Results

**Date:** 2026-10-26 UTC
**Repository / Branch:** `buffedlizard55-lab/GEMSDOE33` (`arena/b9872db2-gemsdoe33`)
**Assigned Lane:** Analog-field & geothermal/hydrothermal-system structural transfer (`GEMSDOE33`)
**Evidence Labeling Rule:** Every local validation metric is labeled **`HOLDOUT-DTI`** (`evaluator_version = "gems-segment-pooled-v1"`, `60,988` withheld catalogue positives, 10 km block-bootstrap 95% CI). Every historical DrivenData score (`0.4413`, `0.3195`, `0.2778`, `0.2750`, etc.) is labeled **`USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)`** because no organizer-authenticated submission receipt is stored in any repository. Zero numeric competition-score projections are made.

---

## 1. Executive Summary Across All Nine Focus Sites

All **21** SHA-256-verified rasters (`12` classic focus-site rasters + `5` newly user-reported 2026-10-25 focus-site rasters + `4` local `GEMSDOE33` rasters) were audited directly on disk (`registry/focus_rasters_20261026.json`, SHA-256 `6e71453c77dd4b2bbb5f1d7e36db74f6641f9a47f6ecfb87b099db21ea8f1500`).

| Site | Highest Classic Artifact (Dots; Reported DTI*) | Latest 2026-10-25 Artifact (Dots; B2 3-px Overlap; Reported DTI*) | Executive Assessment & Suitability |
|---|---|---|---|
| **GEMSDOE24** | `GEMSDOE24-h25-1-d1p5-20261004-989f59505db1.tif` (`60,069` dots; `0.2477`*) | `gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif` (`37,654` dots; `36.62%` B2 3-px; `0.0859`*); later `RSHG1` (`HOLDOUT-DTI 0.1387`, blocked at `72.69% > 70%` ridge overlap) | Hosted the canonical `gems24_template` (`SegmentHoldout`, `submission.py`, `validator.py`). `H25-1` (`d=1.5`) was over-dense (`60,069` dots inflating `0.2 * FP_w`). `GVC1` (`0.0859`*) proved negative lineaments alone over-fire on non-fault contacts; `RSHG1` exposed cross-lane supervised-ridge convergence. **Do not submit `H25-1`, `GVC1`, or `RSHG1`.** |
| **GEMSDOE25** | `gems25-h19-5-d2p8-20261004T201317Z-e56ea318af89.tif` (`44,090` dots; `0.2600`*) | `gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif` (`44,832` dots; `30.38%` B2 3-px; `0.0742`*) | Classic `e56ea318af89` is pixel-identical (`Jaccard = 1.000`) to `GEMSDOE30` `91eae1ca` (`d=2.8` thinning of `H19-5`, retaining `6,436` `0 < d_cat <= 2 px` halo dots). `H66` (`0.0742`*) showed basement-flank gravity gradients fire broadly on buried pediments/intrusives rather than discrete Quaternary fault traces. **Unsuitable for a new slot.** |
| **GEMSDOE27** | `gems27-topo-gap-20261004-5512495c6bd1.tif` (`61,328` dots; `0.2449`*) | `gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite.tif` (`37,654` dots; `56.12%` B2 3-px; **`0.2190`**\*) | `topo-gap` (`61,328` dots) was an over-dense superset containing `100%` of `G24` `H25-1`. By contrast, **`H29` (`0.2190`*) is the strongest independent non-`H19-5` 2026-10-25 submission across all 9 focus sites**: combining hydrothermal alteration, piedmont flexure, 1 m LiDAR scarps, and 300 m `CELF` submodular placement lifted genuine from-scratch discovery `2.5x–10x` above `G24`/`G25`/`G28`, though still `0.0588` below `G32` `B2` (`0.2778`*). |
| **GEMSDOE28** | `h36-1-r1-band-prune-20261004T231500Z-b531dae0a36f-zeros.tif` (`37,660` dots; `0.2710`*); `h27-4` (`40,199` dots; `0.2708`*) | `gems28-s18-mxtp-20261025-3e95505c011a-allfinite.tif` (`11,082` dots; `17.14%` B2 3-px; `0.0217`*) | Classic `H36-1`/`H35-1`/`H27-4` are minor prunings of the `H19-5 -> H27-4` chain (`93.6%–100%` overlap with `B2`). `S18` (`11,082` dots, `0.0217`*) severely under-allocated dot budget (`29%` of `37,654`), collapsing recall against `0.8 * FN_w`. **Unsuitable for a new slot.** |
| **GEMSDOE30** | `gems30-d28-baseline-20261004-91eae1ca-zeros.tif` (`44,090` dots; `0.2600`*) | `gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif` (`44,090` dots; `39.18%` B2 3-px; `0.1462`*) | Classic `91eae1ca` is pixel-identical to `GEMSDOE25` (`Jaccard = 1.0`). `MSDB1` (`0.1462`*) trained a 31-feature OOF `HistGradientBoostingClassifier` on `labels.tif` and emitted `44,090` `d=2.8` dots; its `0.1462`* outcome provides the crucial empirical anchor showing what regional catalogue-supervised HGB surfaces achieve without `H19-5` trace detection or 300 m `CELF`. |
| **GEMSDOE31** | `h27-4-r1-solo-d2-8-20261004T195206Z-8acb75e1-zeros.tif` (`40,199` dots; `0.2708`*) | `GEMSDOE31-H31R-1-relay-damage-research-20261025-7a16d0b4cfdc-zeros.tif` (`DO NOT SUBMIT`, negative on holdout) | Classic `8acb75e1` deleted `3,891` `d_cat == 1` halo pixels from `d2.8` (`+0.0108`* over `0.2600`*), leaving `2,545` `1 < d_cat <= 2` halo pixels still intact. Latest `H31R-1` failed its holdout gate. **Unsuitable for a new slot.** |
| **GEMSDOE32** | **`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`** (`37,654` dots; **`0.2778`**\*) | `gems32-sbir1-20261025-2e6742b7075c-zeros.tif` (`DO NOT SUBMIT`, negative on holdout) | **Highest user-reported score across all 9 focus sites (`0.2778`*).** Equals `GEMSDOE31` `H27-4` minus the remaining `2,545` `1 < d_cat <= 2 px` boundary-halo pixels (`pixel_exact_match = True`). Latest `SBIR1` failed holdout. Remains the historical benchmark (`sha256: c55bafc4...fa9`), **not** re-emittable under uniqueness rules. |
| **GEMSDOE33** *(This Site)* | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-zeros.tif` (`41,865` dots; `0.2632`*, retired) | Prior `A33-L1` (`2bbbf7e3...`, `HOLDOUT-DTI 0.1084` vs `0.1132`, negative); **New Round 2 `A33-R2-CSHT`**: `gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif` (`37,654` dots; `35.86%` B2 3-px; **`HOLDOUT-DTI 0.136716` screen / `0.131169` confirm**) | `H33-D` was an `H27-4` + `1,666`-dot stepover graft (`98.0%` B2 overlap) that diluted precision (`0.2708 -> 0.2632`*). New **`A33-R2-CSHT`** fixed `IR-33-LIDAR-VOID-01`, won **`8 / 8` holdout folds** across both orthogonal splits, passed `50 / 50` canaries & `21 / 21` `final_dots` uniqueness (`max = 69.34% <= 70%`), **OK TO DOWNLOAD (`YES`)**, **OK TO SUBMIT (`NO — DO NOT SPEND SLOT`: blocked by pre-placement surface convergence with `G30-MSDB1` [`0.1462`*])**. |
| **GEMSDOE36** | `gemsdoe36-anderson-dipslip-h33b2-k1200-20261004-9b9ea4e6-zeros.tif` (`38,854` dots; `0.2750`*) | `gems36-mstd1-mohr-slip-dilation-20261025-830680814c61-zeros.tif` (`DO NOT SUBMIT`, negative on holdout) | Classic `9b9ea4e6` = exact `G32` `B2` (`37,654` dots) + `1,200` Andersonian dip-slip tip extensions (`Spearman = 0.9843` vs `B2`), reducing user-reported score from `0.2778`* to `0.2750`* (`-0.0028`*). Latest `MSTD1` failed holdout. **Unsuitable for a new slot.** |

*\*All historical DrivenData DTI figures are **USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)**.*

---

## 2. PhD-Level Forensic Proof: Why `GEMSDOE32` `B2` Achieved `0.2778` — And Can We Beat `0.2778`?

### 2.1 Exact Pixel-Algebraic Lineage of `GEMSDOE32` `B2`
Direct byte-level comparison (`evidence/focus_raster_audit_20261025.json`) establishes the deterministic subtraction chain originating in `19GEMSDOE` `H19-5` (a curvilinear multi-scale 1 m 3DEP LiDAR scarp + detrended-DEM + potential-field trace detector):

$$\text{H19-5}\;(\sim 124\text{k px},\;0.1922^*) \xrightarrow{d=1.5}\text{G24}\;(60{,}069,\;0.2477^*) \xrightarrow{d=2.8}\text{G25/G30}\;(44{,}090,\;0.2600^*) \xrightarrow{d_{\text{cat}}>1}\text{G31}\;(40{,}199,\;0.2708^*) \xrightarrow{d_{\text{cat}}>2}\mathbf{G32\text{-}B2}\;(37{,}654,\;\mathbf{0.2778^*}).$$

Not a single fault prediction was *added* between `d2.8` (`44,090` dots) and `G32-B2` (`37,654` dots):
- `G31` (`H27-4`) deleted the `3,891` dots at Euclidean distance $0 < d_{\text{cat}} \le 1\text{ px}$ (`100 m`) from `existing_faults.tif` (`+0.0108`* reported DTI).
- `G32` (`B2`) deleted the remaining `2,545` dots at $1 < d_{\text{cat}} \le 2\text{ px}$ (`100–200 m`), leaving `37,654` binary `{0, 1}` dots strictly inside $d_{\text{cat}} > 2\text{ px}$ (`+0.0070`* additional reported DTI, `pixel_exact_match = True`).

### 2.2 Exact DTI Partial-Derivative & Boundary-Halo Theorem
In DrivenData #306, known catalogue pixels $K$ (`60,988` cells) are masked at `0 m` (`prediction[K] = 0`, `truth[K] = 0`) before applying the 29-tap 300 m (`3 px`) triangular MAX kernel $K_{\triangle}(d) = \max(0, 1 - d/3)$:

$$\text{DTI} = \frac{\text{TP}_w}{\text{TP}_w + \alpha\,\text{FP}_w + \beta\,\text{FN}_w}, \qquad \alpha = 0.2,\;\;\beta = 0.8,\;\;\text{TP}_w + \text{FN}_w = |T_{\text{new}}|\;\text{(constant)}.$$

Differentiating with respect to $\text{FP}_w$ at fixed $\text{TP}_w$:

$$\frac{\partial\,\text{DTI}}{\partial\,\text{FP}_w} = -\frac{\alpha\,\text{TP}_w}{\left(\text{TP}_w + \alpha\,\text{FP}_w + \beta\,\text{FN}_w\right)^2} < 0.$$

Why did deleting the `6,436` dots in the `0 < d_cat <= 2 px` (`<= 200 m`) annulus around $K$ lift reported DTI monotonically by **`+0.0178`** (`0.2600 -> 0.2778`*)?
1. **Cross-strike scarp-width halo bleed ($\Delta \text{TP}_w \approx 0$, $\Delta \text{FP}_w \approx -1$ per deleted dot):** A real Quaternary range-front scarp has `100–250 m` topographic width, whereas the digitized USGS polyline in $K$ is `1 px` (`100 m`) wide. Any gradient/scarp detector fires across the entire `200 m` scarp slope flanking $K$. Those flanking pixels are **not** unmapped parallel faults in the hidden expert truth $T_{\text{new}}$ — they are lateral halo bleed of the *already-mapped* fault $K$, so after masking $K$ at `0 m`, they find no $T_{\text{new}}$ within `300 m` and incur pure false-positive penalty $\alpha = 0.2$.
2. **Along-strike tip redundancy under the 300 m MAX kernel:** Even where a newly mapped fault continuation starts immediately at the tip of $K$, a dot placed at $d_{\text{cat}} = 2.5\text{ px}$ (`250 m`) still covers `t = 1 px` (`100 m`) past the tip with weight $1 - 1.5/3 = 0.50$ and `t = 2 px` (`200 m`) with weight $0.833$ under the $\max$ operator — retaining nearly full tip credit while shedding thousands of lateral scarp-width false positives!
3. **Why grafts onto `B2` degraded score:** `GEMSDOE36` added `1,200` Andersonian tip dots (`0.2778 -> 0.2750`*) and `GEMSDOE33` `H33-D` added `1,666` stepover dots (`0.2708 -> 0.2632`*) because at $\text{DTI} \approx 0.278$, an added dot breaks even if and only if its expected incremental true-positive weight satisfies $\Delta \text{TP}_w / \Delta \text{FP}_w > \frac{\alpha\,\text{DTI}}{1 - \beta\,\text{DTI}} = \frac{0.2 \times 0.2778}{1 - 0.8 \times 0.2778} = \mathbf{0.0714}$ of *uncovered* $T_{\text{new}}$ pixels. Naive geometric extrapolations off catalogue tips miss real curved traces by `> 300 m` (`\Delta \text{TP}_w \approx 0`).

### 2.3 Honest PhD Verdict: Can `GEMSDOE33` Beat `0.2778` Under Current Constraints?
- **Within `GEMSDOE33`'s strict lane & non-duplication rules (`zero H19-5/B2 pixels`, supervised solely on public `labels.tif`):** **No — not in this campaign.** Empirical evidence across all 9 focus sites is unambiguous:
  - Pure regional/geophysical `labels.tif`-supervised models without `H19-5` curvilinear scarp-trace detection achieve `0.0742`* (`G25-h66`), `0.0859`* (`G24-gvc1`), `0.1462`* (`G30-MSDB1`), and at best **`0.2190`**\* (`G27-h29`, using hydrothermal + piedmont + 1 m LiDAR + 300 m `CELF`).
  - Why is there a structural gap between `labels.tif`-supervised tabular pixel classifiers (`~0.14–0.22`*) and curvilinear scarp/trace detectors (`0.2778`*–`0.4413`*)? Because `labels.tif` is a **positive-unlabeled (PU) noisy catalogue**: thousands of genuine Quaternary faults are *unlabeled* in `labels.tif` (so `y = 0` during training!), teaching tree classifiers to downweight subtle Quaternary scarps while upweighting broad range-bounding lithologic contrasts that characterize historically mapped faults.
- **What WOULD genuinely beat `0.2778` (and move toward user-reported `0.3195`* / `0.4413`*) in a future dedicated detector campaign?**
  1. **Multi-azimuth Steger / Gabor curvilinear trace tracking on 1 m LiDAR + detrended DEM** enforcing `>= 1.5 km` along-strike continuity (eliminating isolated lithologic speckles that plague pixel-wise HGBs);
  2. **Explicit regime split at `lid_valid == 0` (`24.63%` of footprint, `IR-33-LIDAR-VOID-01`)**, using curvilinear scarp tracking where `lid_valid > 0` and our `A33-R2-CSHT` concealed/hydrothermal transfer strictly inside the `1,272,913`-cell 3DEP LiDAR void and deep alluvial stepovers; and
  3. **Exact 300 m triangular-kernel `CELF` submodular dot allocation** (`d_cat > 2 px`, `d_self >= 2.8–3.2 px`) replacing `H19-5`'s greedy point-wise `d=2.8` thinning.

---

## 3. Round 2 (`A33-R2-CSHT`) Empirical Validation, Uniqueness & Gate Audit

### 3.1 Pooled `HOLDOUT-DTI` Results (`evaluator_version = "gems-segment-pooled-v1"`)

| Split / Role | Split ID | Collar | Withheld Positives | `matched_random` | `B0_raw_analog` | `B1_regional` (Incumbent) | **`A33-R2-CSHT` (Candidate)** | Paired $\Delta$ vs `B1_regional` (95% Block-Bootstrap CI) | Fold Wins |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| **Experiment 2/3 — Primary Screen** | `quadrant-buffered-15px-v1` | `1,500 m` | `60,988` | `0.025617` (`[0.0226, 0.0287]`) | `0.088435` (`[0.0789, 0.0985]`) | `0.112418` (`0.113244` rec.) | **`0.136716`** (`[0.1191, 0.1544]`) | **`+0.024298`** (`[+0.012427, +0.035833]`) | **`4 / 4`** |
| **Experiment 3/3 — Frozen Confirmation** | `diagonal-wedge-buffered-20px-confirm-v1` | `2,000 m` | `60,988` | — | — | `0.115122` (`[0.1038, 0.1268]`) | **`0.131169`** (`[0.1152, 0.1467]`) | **`+0.016047`** (`[+0.003817, +0.028030]`) | **`4 / 4`** |

**Per-Fold Breakdown (`8 / 8` Folds Won):**
- **Screen (`quadrant-buffered-15px-v1`):** `NW`: `0.135575` vs `0.111013` (`+0.024562`); `NE_LidarGapHeavy`: **`0.165257` vs `0.134070` (`+0.031188`, +23.3% relative lift inside the 3DEP LiDAR gap after fixing `IR-33-LIDAR-VOID-01`)**; `SW`: `0.100915` vs `0.100586` (`+0.000329`); `SE`: **`0.157058` vs `0.110546` (`+0.046512`, +42.1% lift)**.
- **Orthogonal Confirmation (`diagonal-wedge-buffered-20px-confirm-v1`):** `N_wedge`: `0.166755` vs `0.150349` (`+0.016406`); `E_wedge`: `0.163097` vs `0.130631` (`+0.032467`); `S_wedge`: `0.125747` vs `0.109005` (`+0.016742`); `W_wedge`: `0.108183` vs `0.102680` (`+0.005504`).

### 3.2 Per-Feature Leakage Canaries & 21-Raster Uniqueness Screen
- **Leakage Canary (`50 / 50` channels tested alone via `SegmentHoldout.canary`):** **PASSED** (`0` features `> 0.90`; max pooled two-sided AUC = `0.7209` on `lid_step_max`; max single-fold two-sided AUC = `0.7685`).
- **Final Placed GeoTIFF Uniqueness (`final_dots_not_duplicate`, `37,654` `CELF-300m` dots vs all 21 pinned rasters):** **PASSED (`21 / 21`)**:
  - Max `|Spearman ρ|` = **`0.0416 <= 0.90`** (`G24-gvc1`).
  - Max `3-px dot overlap` = **`0.6934 <= 0.70`** (`G30-MSDB1`), `0.6539` (`G25-h66`), `0.6236` (`G24-gvc1`), `0.4310` (`G27-topo-gap`), **`0.3586` (`G32-B2`)**, **`0.3519` (`G33-A33-L1`)**, and **`0.3118` (`G27-h29`)**.
- **Pre-Placement Surface Guard (`surface_not_duplicate`):** **STOPPED (`FAIL-CLOSED`):**
  - While pre-placement surface `|Spearman ρ|` was `<= 0.1146` across all 21 rasters (note `IR-33-SPEARMAN-SPARSE-CEILING-01`: mathematical ceiling $\sqrt{3p(1-p)} \approx 0.159$), top pre-placement surface peaks exceeded `70%` 3-px overlap against the three 2026-10-25 sibling regional-HGB rasters (`G30-MSDB1`: `91.11%` unthinned / `77.82%` matched-37k 1-px NMS crests; `G24-gvc1`: `88.49%`; `G25-h66`: `73.41%`), while passing all 18 other rasters (`<= 65.11%`).
  - Per Protocol Rule 5 & Rule 7 (`3 / 3` experiments reached), we **refused to game the gate denominator** and stopped cleanly with Run Card `"verdict": "duplicate"`, **`ok_to_download = True`**, **`ok_to_submit = False`**.

### 3.3 Generated GeoTIFF Deliverable & Automated Validation Summary
- **Primary `[0, 1]` GeoTIFF (0 outside footprint):** `docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif` (`826,756` bytes, SHA-256 `14ab452c22aaf07444cd02e589fce4627d682e99f44c63e78dc1383955e0c602`) + `.zip` (`169,085` bytes).
- **Official-text `NaN`-outside twin:** `docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-nan.tif` (`1,591,192` bytes, SHA-256 `c1173e63bec4f2f673074e6951218ac3d269f25994b322e9eff39905b9e64af5`) + `.zip` (`281,499` bytes).
- **Short note (`98` chars `<= 140`):** `GEMS33 A33-R2-CSHT: cover+hydrothermal transfer + 300m CELF 37654d | gate DUPLICATE | 0b78c04d5fad`
- **Automated `scripts/validate_submission.py` checks:** `1 band float32`, `EPSG:32611`, `3730 x 3292`, `100 m x -100 m` origin `(243350.0, 4508550.0)`, `5,167,373` finite footprint cells strictly in `[0.0, 1.0]`, `0` NaN in primary `-zeros.tif` (`min = 0.0, max = 1.0` across all `12,279,160` cells), `37,654` positive dots, `0` overlap with `labels.tif`, **`pass = True`**.
