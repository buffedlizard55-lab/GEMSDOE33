# GEMSDOE33 — DOE GEMS Fault Discovery Project (DrivenData #306)

## 🟡 Current Decision (2026-10-26, `A33-R2-CSHT`): **OK TO DOWNLOAD: YES** · **OK TO SUBMIT: NO (DO NOT SPEND A WEEKLY SLOT)**

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
| **GEMSDOE33** *(This Repo)* | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-zeros.tif` (`41,865`; `0.2632`*, retired) | Prior `A33-L1` (`HOLDOUT-DTI 0.1084` vs `0.1132`, negative); **New `A33-R2-CSHT` (`37,654`; `35.86%` vs B2; `HOLDOUT-DTI 0.136716` screen / `0.131169` confirm)** | Fixed shared `IR-33-LIDAR-VOID-01` (`1.27M` void cells), won **`8/8` holdout folds**, passed `50/50` canaries & `21/21` `final_dots` uniqueness, **OK to download (`YES`)**, **NOT OK to submit (`NO`: pre-placement surface convergence with `G30-MSDB1`)**. |
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
   - **What WOULD beat `0.2778` in a dedicated next-generation detector campaign:** Coupling (i) multi-azimuth curvilinear 1 m scarp/DEM trace tracking (`>= 1.5 km` continuity) where `lid_valid > 0`, (ii) our `A33-R2-CSHT` void-safe concealed/hydrothermal transfer strictly inside the `24.63%` 3DEP LiDAR gap (`IR-33-LIDAR-VOID-01`) and deep alluvial stepovers, and (iii) 300 m triangular-kernel submodular `CELF` allocation. Full derivation: [`knowledge/13_focus_forensics_g32_proof_and_a33_r2_results_20261026.md`](knowledge/13_focus_forensics_g32_proof_and_a33_r2_results_20261026.md).

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
| **USGS 3DEP 1 m LiDAR Scarp Derivatives** | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · `data/lidar_scarp_features.json` | Public Domain; `75.37%` footprint coverage (`1,272,913` void cells fixed in `IR-33-LIDAR-VOID-01`). |
| **Preserved Standing Brief & Operating Rules** | [`standing_prompt.md`](standing_prompt.md) · [`AGENTS.md`](AGENTS.md) · [`registry/irregularities.json`](registry/irregularities.json) | Full consolidated standing prompt, 2026-10-26 Round 2 addendum, and fail-closed promotion contract. |

### Reproduce & Run All Automated Checks (Zero Human Inspector Needed)

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
GEMS_DATA_DIR=$PWD/.cache/gemsdata .venv/bin/python scripts/restore_data.py --group all --data-dir .cache/gemsdata
.venv/bin/python scripts/evaluate_holdout.py --verify-recorded
.venv/bin/python scripts/evaluate_holdout.py --verify-a33-r2
.venv/bin/python scripts/validate_submission.py --submission docs/downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif --template data/sample_submission.tif --strict-zero-outside
PYTHON=.venv/bin/python bash scripts/run_checks.sh
```

---

## Operating Prompt — Embedded for Every Session (2026-10-26)

Source: user request (parallel-run protocol, GEMSDOE24/25/27/28/30/31/32/33/36 focus sites, highest-urgency submission generation). Read this section at start of every session to confirm we are building what is aimed for.

### Core Values
- Maximize P(Win): decide by evidence, not hope; prefer leakage-audited holdout over projection.
- Own the Outcome: fix shared bugs once, report them; never keep private forks; make negative results visible.

### Parallel-Run Protocol (must follow)
1. LANE: stay inside the single method paragraph (for this repo: A33-R2-HMDT / analog-transfer / coherence interaction + 300m CELF).
2. REUSE, DON'T REBUILD: use cached feature stack, evaluate_holdout.py, submission_writer.py; fix shared tools once.
3. LABEL EVERY NUMBER: HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (submission-page receipt). Never label a projection as a score.
4. LEAKAGE CANARY: test each feature alone; AUC > 0.90 means leakage until proven otherwise.
5. RUN CARD: end with JSON card (hypothesis; mechanism; named non-fault mimic process; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output; submission name + ≤140 char note; verdict promote / negative).
6. BUDGET: stop after 3 experiments or 2 hours; do not pick submissions; promotion to real slot is separate selector step.

### Highest-Urgency Requirements
- MUST generate a UNIQUE TIF submission; do NOT copy a previous submission unless for learning.
- Must be OBVIOUS whether OK to download and OK to submit (format gates + uniqueness + holdout status clearly labeled).
- Must pass validation: single-band float32 GeoTIFF, EPSG 32611, 3730×3292, 100 m transform, values inside footprint strictly in [0,1] (no NaN inside footprint for zero-variant; NaN only outside for nan-variant), no NaN inside footprint.
- Must include easy download (.tif + .zip) with note ≤ 140 chars.
- Must include executive summary per focus site (GEMSDOE24/25/27/28/30/31/32/33/36) identifying best reported submission and why.
- Must verify no hallucinations; provide official verified links; work line by line.

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

### New Candidate Generated This Session
- Name: gemsdoe33-a33-r2-hmdt-20261026-hmdt-unique-zeros / -nan
- Mechanism: A33-R2-HMDT (magnetite-destruction × clay-cap coherence + 300m CELF)
- Dots: 42,000; overlap with parents: 0%; Spearman ρ vs registry: ≤ 0.0046
- Format: PASS; Uniqueness: PASS
- Holdout: NOT MEASURED (no feature stack restored; derivation from validated parents via interaction)
- Verdict: negative-on-score-unknown / positive-on-format-and-uniqueness — download OK, submit as experimental only with awareness no holdout improvement over 0.2778 demonstrated.

