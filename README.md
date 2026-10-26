# GEMSDOE33 — DOE GEMS Fault Discovery Project (DrivenData #306)

## ⚡ Top-of-Page Submission Readiness & Automated Gate Verdict (2026-10-25)

> ### **STATUS: FORMAT `[0, 1]` & 9-SITE UNIQUENESS VALIDATED — LIVE WEEKLY SLOT GATED (`verdict: negative` · DO NOT AUTO-SUBMIT)**
>
> - **Generated Unique GeoTIFF (Round 3):** [`docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif`](docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif) (`148,375` bytes) · [Single-TIFF `.zip`](docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.zip) (`116,535` bytes) · [Validator Receipt JSON](docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.json) · [Run Card JSON](evidence/round3_da_hgcm_run_card_20261025.json)
> - **Unique Submission Name:** `gemsdoe33-r3-da-hgcm-37654-a6a8552e`
> - **Suggested Note (`105 / 140` chars):** `GEMSDOE33 H33-R3-3 37654d [0,1] zeros; unique vs 201 9-site dl; gated (r13-lattice-s5/proxy); id a6a8552e`
> - **Raster SHA-256:** `2c1b648364d976bb29a52ab9045f5e2233920870f7a9670533283f00a0b1e2a8`
> - **Is it OK to download?** **YES** — programmatically validated without human inspection across all `12,279,160` cells (`15/15` checks passed, `0` NaN anywhere, values strictly in `[0.0, 1.0]`, `0.0` outside footprint, `0` on-catalogue dots).
> - **Is a live weekly competition slot auto-cleared?** **NO (`verdict: negative`, `0` slots spent)** — `H33-R3-3` passed **Gates G1–G5** (including `8/8` independent confirmation fold wins and uniqueness across **all 201 published submission GeoTIFFs of the 9 focused sites** `GEMSDOE24..36`), **but failed Gate G6** under the literal unexempted `vendor/gems57/uniqueness.py` scan of non-download subdirectories because `GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` (`206,895` dots) is a uniform spacing-5 synthetic calibration lattice whose 3-px disks cover **99.87%** of the entire off-catalogue footprint (`0.9997 > 0.70` forward 3-px proximity despite `Jaccard < 0.03`). Combined with Parallel-Run Protocol Rule 6 (*"promotion to a real slot is a separate selector step"*) and owner-mirror input provenance, **do not spend a live weekly competition slot without explicit human selector review**. Archived Round-2 `H33-6` and Round-1 `H33-F` remain failed research records (`NOT approved for competition upload`).

| Automated Gate | Threshold / Rule | Measured Result | Status |
|---|---|---|---|
| **G1 — Format & `[0, 1]` Range** | `EPSG:32611`, `3730×3292`, `float32`, `0` NaNs anywhere, `[0.0, 1.0]` whole array, `0` on-catalogue px | `15/15` checks passed (`vendor/gems57/validate.py` + `scripts/validate_submission.py --strict-zero-outside`); `37,654` binary dots | **PASS** |
| **G2 — Standalone Leakage Canaries** | Every feature tested alone on buffered holdout has `max(AUC, 1-AUC) <= 0.90`; `dist_known_fault_px` & `SGMC` excluded | `52/52` features passed; max oriented AUC = `0.7945` (`vis_tip_aniso_cone`); all 46 `H33-R3-3` features `<= 0.5975` | **PASS** |
| **G3 — Ben-David Domain Invariance** | 20 km spatial-block `|AUC(D_S vs D_T) - 0.5| <= 0.20` screen | `46/48` kept (2 GDR point-density plumes auto-dropped); joint linear domain AUC cut from `0.9169` (`H33-F`) to **`0.5178`** ($\hat{d}_{\mathcal{H}\Delta\mathcal{H}} = 0.0712$, $d_{\text{VC}} = 47$) | **PASS** |
| **G4 — Spatially-Blocked Holdout & Fresh Confirmation** | Beat fold-rebuilt matched controls (`37,654` dots) with positive 20 km block-bootstrap 95% CI on Selection (`seeds 20,21`) & Confirmation (`seeds 33,34`) + non-inferior `SGMC` | Selection `HOLDOUT-DTI = 0.101977`; Confirmation **`HOLDOUT-DTI = 0.114084`** (`[0.096891, 0.132095]`), **`8/8` fold wins** (`+0.066412` vs `CTRL-RIDGE-B2`, `+0.027924` vs `CTRL-GBDT`); `SGMC` **`0.120202`** (**`+0.024070` / `+25.0%`** over `GEMSDOE32` `H33-2-B2`) | **PASS** |
| **G5 — Focused 9-Site Published Submissions (`201` TIFs)** | Pre-placement surface & final dots `|Spearman rho| <= 0.90` and `3-px overlap <= 0.70` across `GEMSDOE24,25,27,28,30,31,32,33,36` `docs/downloads/` + local | Surface `|\rho| = 0.1162`, top-K 3-px `0.6811`; Final dots `|\rho| = 0.0614`, max 3-px **`0.5265`** (`0.4430` vs `GEMSDOE32` `H33-2-B2`; only `4.27%` shared pixels) | **PASS** |
| **G6 — Literal 9-Repo Subdirectory Scan (`214` TIFs)** | Unexempted literal scan including `inputs/calibration/` (`vendor/gems57/uniqueness.py`: lattice priors not exempt) | `213/214` pass; `GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5` (`99.87%` footprint 3-px halo) gives `0.9997 > 0.70` | **GATED (`negative`)** |

---

## §1. Session Prompt & Standing Project Directive (Contract of Record)

> **User Prompt Stored as Starting Contract (2026-10-25):**
>
> Review the repo. Focus on the highest-scoring submissions from `GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, `GEMSDOE36` (user-supplied historical score context includes `GEMSDOE24` `0.2477`, `GEMSDOE25` `0.2600`, `GEMSDOE27` `0.2449`, `GEMSDOE28` `0.2708`/`0.2710`, `GEMSDOE30` `0.2600`, `GEMSDOE31` `0.2708`, `GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778`, `GEMSDOE33` `0.2632`, `GEMSDOE36` `0.2750`, plus broader user-cited campaign/leaderboard context up to `0.3195` and `0.4413` — treated strictly as user-supplied historical reports, not organizer-authenticated receipts; row-level public leaderboard tables are not reproduced per DrivenData Terms of Use).
>
> **Core Requirements:**
> 1. **MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION.** Do not copy a previous submission unless for learning and education. It must be immediately obvious whether it is OK to download and submit the generated TIF submission, with automated programmatic validation in `[0, 1]` matching template CRS, shape, and geotransform without human intervention.
> 2. **Study, analyze, and understand `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778`):** Why and how did it get the highest listed score among the 9 focused sites, and are we able to generate a submission that scores higher than `0.2778` (and move toward `0.3195` / `0.4413`)? Answer with PhD-level judgment.
> 3. **Pre-implementation geological hypotheses:** Generate 3–5 untried candidate geological hypotheses naming exact layers, targeted physical signature, why it catches faults missing from the USGS/INGENIOUS catalogue, how it differs from existing repo implementations, ranking by expected DTI gain and cost, and verified free official sources if external data is required.
> 4. **Parallel-Run Protocol:**
>    - **1. STAY IN YOUR LANE (`GEMSDOE33` Standing Analog-Field Domain Adaptation & Hydrothermal Conduit Lane, Ben-David et al., *Machine Learning* 2010; see [`standing_prompt.md`](standing_prompt.md)).** Check pre-placement surface AND final dots against registry rasters (`|Spearman rho| > 0.90` or `>70%` of dots within `3 px` = duplicate -> log and stop).
>    - **2. REUSE, DON'T REBUILD.** Use cached feature stack, shared `evaluate_holdout.py`, and `submission_writer.py`. Holdout = hide-and-recover whole fault segments with a buffer, derive catalogue features strictly from visible faults, mask visible faults pixel-exactly, score pooled DTI ($\alpha=0.2, \beta=0.8$, 300 m triangular kernel).
>    - **3. PROVENANCE.** Label every metric `HOLDOUT-DTI` (evaluator version, withheld positives count, 95% CI) or `ORGANIZER-CONFIRMED` (from submission receipt). Never write projections as scores.
>    - **4. LEAKAGE CANARY FIRST.** Test each feature alone on holdout (`AUC > 0.90` = target leakage until proven otherwise).
>    - **5. RUN CARD.** End with one JSON card (`hypothesis`, `mechanism`, `non_fault_mimic`, `holdout_dti` + `ci`, `registry_correlation_overlap`, `raster_sha256`, `validator_output`, `submission_name` + `note <= 140` chars, `verdict`: `promote` / `negative`).
>    - **6. BUDGET.** Stop after at most 3 experiments or 2 hours. Promotion to a live slot is a separate selector step within the weekly cap.
> 5. **Verify from official trusted sources with links, flag irregularities, zero hallucinations, run 3 review passes, and open + merge PR onto `main`.**

---

## §2. Core Operating Values

- **Maximize P(Win):** Weigh tradeoffs quantitatively, attack the real bottleneck (replacing uncalibrated `H19-5` pruning with cross-basin transferable multi-physics + exact submodular 300 m Tversky optimization), and never waste a weekly submission slot on unvalidated heuristics.
- **Own the Outcome:** Automate data restoration, feature construction, holdout confirmation, registry screening, and byte-level GeoTIFF validation end to end; surface failures and blockers transparently alongside breakthroughs.

---

## §3. PhD Forensic Analysis: Why `GEMSDOE32` (`h33-h33-2-b2-...-zeros: 0.2778`) Topped the 9 Focused Sites & How to Beat Its Ceiling

All `214` unique valid-grid (`3730 × 3292`, `EPSG:32611`) GeoTIFFs across `GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, and `GEMSDOE36` were downloaded into `.cache/registry_9sites/` and audited pixel-by-pixel ([`evidence/nine_site_forensics_20261025.json`](evidence/nine_site_forensics_20261025.json); full mathematical derivation in [`knowledge/11_20261025_round3_report.md`](knowledge/11_20261025_round3_report.md)).

### 3.1 Exact Pixel-by-Pixel Set Algebra Across the 9 Focused Sites

*(Note: SHA-256 hashes, dot counts, and Boolean pixel identities are measured directly from repository bytes; scores below are `USER-REPORTED` context, not `ORGANIZER-CONFIRMED` receipts.)*

| Site | Headline Artifact | User-Reported Score | Emitted Dots | Outside Footprint | $\min d_{\text{cat}}$ | Dots $\le 1\text{ px}$ | Dots $\le 2\text{ px}$ | Verified Pixel-Exact Identity |
|---|---|---:|---:|---|---:|---:|---:|---|
| `GEMSDOE24` | `gems24-h25-1-dotted-h19-5-d1-5` | `0.2477` | `60,069` | `NaN` | `1.00 px` | `5,355` | `8,769` | `19GEMSDOE` `h19-5` (`121,131` px) thinned at $d=1.5\text{ px}$ |
| `GEMSDOE27` | `gems27-topo-gap-closure-t-v2-on-d1-5` | `0.2449` | `61,328` | `NaN` | `1.00 px` | `5,413` | `8,875` | `GEMSDOE24` $\cup \Delta_{1259}$ (`+1,259` gap dots lowered DTI) |
| `GEMSDOE25` | `gems25-dotted-h19-5-d2-8` | `0.2600` | `44,090` | `NaN` | `1.00 px` | `3,891` | `6,436` | `h19-5` Poisson-disk thinned at $d=2.8\text{ px}$ |
| `GEMSDOE30` | `gemsdoe30-d28-poisson300m-offcat` | `0.2600` | `44,090` | `NaN` | `1.00 px` | `3,891` | `6,436` | **`GEMSDOE30 == GEMSDOE25` (`True` across all 12.28M cells)** |
| `GEMSDOE28` | `gems28-h27-4-r1-solo-d2-8` | `0.2708` | `40,199` | `NaN` | `1.41 px` | `0` | `2,545` | **`GEMSDOE25` $\cap \{d_{\text{cat}} > 1.0\text{ px}\}$ (`True`, `-3,891` dots)** |
| `GEMSDOE31` | `gemsdoe31-h27-4-solo-d28` | `0.2708` | `40,199` | `NaN` | `1.41 px` | `0` | `2,545` | **`GEMSDOE31 == GEMSDOE28` (`True` across all 12.28M cells)** |
| **`GEMSDOE32`** | **`h33-h33-2-b2-...-e5eb6e7e-zeros`** | **`0.2778`** | **`37,654`** | **`0.0` (`nodata=None`)** | **`2.24 px`** | **`0`** | **`0`** | **`GEMSDOE28` $\cap \{d_{\text{cat}} > 2.0\text{ px}\}$ (`True`, `-2,545` dots)** |
| `GEMSDOE36` | `anderson-geothermal-pinn-38854-zeros` | `0.2750` | `38,854` | `0.0` (`nodata=None`) | `2.24 px` | `0` | `0` | **Strict superset `GEMSDOE32` $\cup \Delta_{1200}$ (`+1,200` dots)** |
| `GEMSDOE33` (hist.) | `GEMSDOE33-h33d-analog-tip-stepover` | `0.2632` | `41,865` | `NaN` | `1.00 px` | `1,377` | `3,894` | Re-introduced `3,894` flank dots inside $d_{\text{cat}} \le 2.0\text{ px}$ |

### 3.2 Three Exact Mathematical Reasons `GEMSDOE32` Reached `0.2778` — And Why Pruning Stops There

1. **Submodular `max` Coverage vs. Additive False-Positive Cost (`121,131 -> 44,090` dots):**
   In $\text{DTI} = \text{TP}_w / (\text{TP}_w + 0.2\,\text{FP}_w + 0.8\,\text{FN}_w)$ with $300\text{ m}$ ($3\text{ px}$) triangular kernel $k(d) = \max(0, 1 - d/3)$, $\text{TP}_w$ takes a **pointwise `max`** over predicted dots whereas $\text{FP}_w$ sums **additively** over every positive pixel. Decimating contiguous 100 m ridges to spacing $d \approx 2.6\text{–}2.8\text{ px}$ cuts FP mass by `63.6%` while retaining almost the entire 300 m kernel envelope (`0.1922 -> 0.2600`).
2. **Eliminating the $200\text{ m}$ Mapped-Catalogue Blur Halo (`44,090 -> 40,199 -> 37,654` dots):**
   Gravity, magnetic, and 100 m DEM gradients fire across a $\pm 200\text{ m}$ ($2\text{ px}$) blur zone flanking *already-mapped* Quaternary faults $C_{\text{mapped}}$. Because the official scorer masks $C_{\text{mapped}}$ pixel-exactly, flanking dots at $0 < d_{\text{cat}} \le 2.0\text{ px}$ remain active off-catalogue predictions whose true physical source was the *known* fault rather than a new hidden fault $G_{\text{new}}$, failing the marginal fractional Tversky inequality $\Delta\text{TP}_w / \Delta\text{FP}_w > \frac{\alpha S}{1 - \alpha S} \approx 0.0573$. Stripping $d_{\text{cat}} \le 1\text{ px}$ (`GEMSDOE28`, `0.2708`) and $1 < d_{\text{cat}} \le 2\text{ px}$ (`GEMSDOE32`, `0.2778`) removed `6,436` pure blur-halo false positives, while `GEMSDOE32`'s `-zeros.tif` encoding matched the official DrivenData U-Net reference writer (`drivendataorg/gems-prize-reference-solution` Cell 19: `y_out = np.zeros(...)`, `nodata=None`), avoiding IEEE-754 `NaN` `[0, 1]` rejections.
3. **Can We Score Higher Than `0.2778`?**
   Every `0.2477..0.2778` model is a subset of the fixed heuristic `H19-5` ridge network (`SGMC` off-catalogue `PROXY-DTI = 0.0961`). Once the $200\text{ m}$ blur halo is removed, `H19-5` has no further room to climb via deletion. Advancing beyond `0.2778` requires **replacing the `H19-5` surface itself** with a calibrated multi-physics + hydrothermal alteration posterior paired with exact CELF submodular 300 m Tversky allocation (`dinkelbach_allocate`) — as validated on spatially blocked holdout and off-catalogue `SGMC` (`+25.0%` over `GEMSDOE32`) below, with the strict caveat that **only an official organizer receipt can confirm a live leaderboard score**.

---

## §4. Preregistered Round-3 Geological Hypotheses (`knowledge/10_hypothesis_slate_20261025_r3.md`)

Frozen and SHA-256-pinned ([`evidence/hypothesis_slate_20261025_r3_preregistered.sha256`](evidence/hypothesis_slate_20261025_r3_preregistered.sha256)) **before** writing any Round-3 experiment code:

1. **`H33-R3-1` (`DA-HGCM-Submod`, Exp 1 — Medium cost, Viable locally):** 46 divergence-screened locally-detrended potential-field, basement/conductivity derivative, 1 m 3DEP LiDAR antislope scarp (`scarp_antislope_contrast`), and hydrothermal magnetite-destruction × clay/brine conductivity (`hydro_demag_clay_coupling`) channels + 4 strictly fold-visible tip/Voronoi-stepover features, fitted via Ben-David (2010) Theorem 3 LOQO HistGBDT on internal pseudo-hidden whole components + Choquet/CELF 300 m allocation (`37,654` dots). *Mimic:* altered ash-flow tuff or playa-margin clay contacts.
2. **`H33-R3-2` (`DA-PurePhys-Submod`, Exp 2 — Low–medium cost, Viable locally):** Pure label-free domain-adapted geophysical + LiDAR antislope + hydrothermal coupling HistGBDT (**zero** visible-network features), isolating blind detached basin fault recovery. *Mimic:* Lake Lahontan paleo-shorelines / buried paleochannels.
3. **`H33-R3-3` (`DA-LinearVC-Submod`, Exp 3 — Low cost, Viable locally — SELECTION & CONFIRMATION WINNER):** Same 46 divergence-screened differential + hydrothermal/antislope channels fitted with an **explicit finite-VC L2-regularized linear halfspace** ($d_{\text{VC}} = 47$, measured empirical $\hat{d}_{\mathcal{H}\Delta\mathcal{H}} = 0.0712$) under Ben-David Theorem 3 source+target LOQO weighting + exact 6-ring Choquet self-credit + CELF `dinkelbach_allocate` (`37,654` dots outside $d_{\text{cat}} \le 2.0\text{ px}$). Low VC complexity prevents tree memorization of basin-specific amplitude pockets. *Mimic:* regional linear lithologic unconformities.
4. **`H33-R3-4` (`MT-PhaseTensor-Skew` — External official source IRIS SPUD EMTF `https://ds.iris.edu/spud/emtf`, CC0):** Static-shift-free 3D magnetotelluric phase-tensor skew $|\beta_{\text{MT}}| > 3^\circ$ (Caldwell et al., 2004) fused with Bands 15, 17, 18 to detect sub-vertical geothermal fluid conduits beneath conductive playa brines. **Audited & blocked in this sandbox** due to outbound host allowlist; not claimed as runnable here.

---

## §5. Round-3 Campaign Results (`<= 3` Experiments · Shared `gems57-pooled-hide-v2` Evaluator)

Full results in [`evidence/round3_campaign_results_20261025.json`](evidence/round3_campaign_results_20261025.json), [`evidence/round3_domain_divergence_audit.json`](evidence/round3_domain_divergence_audit.json), and [`evidence/round3_leakage_canary_audit.json`](evidence/round3_leakage_canary_audit.json):

| Split & Evidence Class | Model / Control | Emitted Dots | Pooled Score | 95% 20 km Spatial-Block CI | Paired $\Delta$ vs `CTRL-RIDGE-B2` (95% CI) | Paired $\Delta$ vs `CTRL-GBDT` (95% CI) |
|---|---|---:|---:|---|---|---|
| `HOLDOUT-DTI` · Selection (`seeds 20,21`, `22,893` withheld px) | `Exp 1: H33-R3-1` (`DA-HGCM-Submod`) | `37,654` | `0.092210` | `[0.081961, 0.101851]` | `+0.047434` (`[+0.0365, +0.0583]`) | `+0.005527` (`[-0.0029, +0.0142]`) |
| `HOLDOUT-DTI` · Selection (`seeds 20,21`, `22,893` withheld px) | `Exp 2: H33-R3-2` (`DA-PurePhys-Submod`) | `37,654` | `0.101581` | `[0.089004, 0.113844]` | `+0.056805` (`[+0.0436, +0.0702]`) | `+0.014898` (`[+0.0085, +0.0214]`) |
| `HOLDOUT-DTI` · Selection (`seeds 20,21`, `22,893` withheld px) | **`Exp 3: H33-R3-3` (`DA-LinearVC-Submod`)** | **`37,654`** | **`0.101977`** | **`[0.090344, 0.114066]`** | **`+0.057201` (`[+0.0444, +0.0703]`)** | **`+0.015294` (`[+0.0069, +0.0233]`)** |
| `HOLDOUT-DTI` · Selection Controls | `CTRL-GBDT` / `CTRL-RANDOM` / `CTRL-RIDGE-B2` | `37,654` | `0.086683` / `0.050832` / `0.044776` | — | — | — |
| **`HOLDOUT-DTI` · Fresh Confirmation (`seeds 33,34`, `22,733` withheld px)** | **`Frozen H33-R3-3` (`DA-LinearVC-Submod`)** | **`37,654`** | **`0.114084`** | **`[0.096891, 0.132095]`** | **`+0.066412` (`[+0.0487, +0.0861]`, `8/8` folds)** | **`+0.027924` (`[+0.0190, +0.0380]`, `8/8` folds)** |
| `HOLDOUT-DTI` · Confirmation Controls | `CTRL-GBDT` / `CTRL-RIDGE-B2` / `CTRL-RANDOM` | `37,654` | `0.086160` / `0.047672` / `0.046241` | — | — | — |
| **`OFF-CATALOGUE-PROXY-SGMC` (`d_cat >= 3 px`, `63,121` px)** | **`H33-R3-3` vs `GEMSDOE32` `H33-2-B2` (`37,654` dots)** | **`37,654`** | **`0.120202` vs `0.096132`** | — | **`+0.024070` (`+25.0%` over `GEMSDOE32`)** | **`+0.023587` over `GEMSDOE28` `H27-4` (`0.096615`)** |

---

## §6. Official Parallel-Run Protocol JSON RUN CARD (`evidence/round3_da_hgcm_run_card_20261025.json`)

```json
{
  "hypothesis": "H33-R3-3 (DA-LinearVC-Submod): Finite-VC Linear Halfspace Domain-Adapted Classifier with Measured Empirical d_H_Delta_H",
  "mechanism": "46/48 divergence-screened label-free differential geophysical, 1 m 3DEP LiDAR antislope scarp (scarp_antislope_contrast), and hydrothermal magnetite-destruction/conductivity coupling (hydro_demag_clay_coupling) channels (zero visible-network features; 2 point-sampled GDR enthalpy plumes automatically rejected by the 20 km spatial-block |AUC-0.5|<=0.20 domain-shift screen) fitted with an explicit finite-VC L2-regularized linear halfspace (vc_dim=47, emp d_H_Delta_H=0.0712) under Ben-David et al. (2010) Theorem 3 source+target LOQO weighting, paired with exact 6-ring Choquet self-credit and CELF submodular 300 m Tversky allocation (37,654 binary dots outside d_cat <= 2.0 px).",
  "non_fault_mimic": "Regional linear lithologic unconformities (e.g., Mesozoic metasedimentary basement against Tertiary volcanics).",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "selection_seeds_20_21": {"withheld_positive_pixels": 22893, "dti": 0.101977, "ci95_20km_block_bootstrap": [0.090344, 0.114066]},
    "independent_confirmation_seeds_33_34": {
      "withheld_positive_pixels": 22733,
      "dti": 0.114084,
      "ci95_20km_block_bootstrap": [0.096891, 0.132095],
      "delta_vs_ctrl_ridge_b2": 0.066412,
      "delta_vs_ctrl_ridge_b2_ci95": [0.048662, 0.08613],
      "delta_vs_ctrl_gbdt": 0.027924,
      "delta_vs_ctrl_gbdt_ci95": [0.01896, 0.038021],
      "fold_wins_vs_ctrl_ridge_b2": "8/8",
      "fold_wins_vs_ctrl_gbdt": "8/8"
    }
  },
  "registry_correlation_overlap": {
    "scope_a_9site_published_downloads_201_rasters": {
      "rasters_checked": 201,
      "pre_placement_surface_max_abs_rho": 0.11618,
      "pre_placement_topk_max_3px_overlap": 0.68107,
      "final_dots_max_abs_rho": 0.06142,
      "final_dots_max_3px_overlap": 0.52648,
      "unique_pass": true
    },
    "scope_b_complete_9repo_tree_214_rasters_literal": {
      "rasters_checked": 214,
      "final_dots_max_abs_rho": 0.0636,
      "final_dots_max_3px_overlap": 0.99971,
      "blocking_witness": "buffedlizard55-lab/GEMSDOE24:inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
      "unique_pass": false
    }
  },
  "raster_sha256": "2c1b648364d976bb29a52ab9045f5e2233920870f7a9670533283f00a0b1e2a8",
  "validator_output": {"all_checks_passed": true, "n_nan": 0, "min": 0.0, "max": 1.0, "crs": "EPSG:32611", "shape": [3730, 3292], "on_catalogue_positive_pixels": 0},
  "submission_name": "gemsdoe33-r3-da-hgcm-37654-a6a8552e",
  "note": "GEMSDOE33 H33-R3-3 37654d [0,1] zeros; unique vs 201 9-site dl; gated (r13-lattice-s5/proxy); id a6a8552e",
  "verdict": "negative"
}
```

---

## §7. Verified Official & Mirror Data/Literature Sources (`registry/sources.json`)

| Source ID | Official / Mirror Link | Provenance Class | Role & Verification Summary |
|---|---|---|---|
| `competition-problem` | [DrivenData DOE GEMS Problem & Metric (#306)](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | `OFFICIAL` | DTI formula ($\alpha=0.2, \beta=0.8$, 300 m kernel), `EPSG:32611` 100 m grid, `[0, 1]` range. |
| `competition-rules` | [DrivenData GEMS Rules](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/) & [Terms of Use](https://www.drivendata.org/termsofuse/) | `OFFICIAL` | Weekly submission cap; prohibits automated portal scraping/uploading. |
| `reference-solution` | [drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) | `OFFICIAL REPO` | Inspected Cell 19 on 2026-10-25: `y_out = np.zeros(...)`, `nodata=None` (`0.0` outside footprint). |
| `geodawn` | [USGS GeoDAWN Airborne Magnetic & Radiometric Survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | `OFFICIAL USGS` | Provenance for magnetic/radiometric layers (`IR-33-RAD-01`: uint8 ordinal scaling). |
| `usgs-3dep-1m` | [USGS 3D Elevation Program (3DEP)](https://www.usgs.gov/3d-elevation-program) | `OFFICIAL USGS` | Provenance for 12-band 1 m LiDAR scarp summary (`upface_max`, `cross_max`, `coh100`). |
| `usgs-sgmc` | [USGS SGMC Compilation (Horton et al., 2017)](https://doi.org/10.3133/ds1052) | `OFFICIAL USGS` | Off-catalogue compilation fault benchmark (`d_cat >= 3 px`); never used in features/training. |
| `gdr-1391` | [DOE GDR #1391 INGENIOUS Regional Dataset](https://gdr.openei.org/submissions/1391) | `OFFICIAL DOE GDR` | Provenance for Quaternary fault compilation, wells/springs, and volcanic vents (`CC BY 4.0`). |
| `ben-david-2010` | [Ben-David et al. (2010), *Machine Learning* 79:151–175](https://doi.org/10.1007/s10994-009-5152-4) | `PEER-REVIEWED` | Lemma 2 $\hat{d}_{\mathcal{H}\Delta\mathcal{H}}$ domain discriminator & Theorem 2/3 source+target transfer theory. |
| `caldwell-2004-mt` | [Caldwell, Bibby & Brown (2004), *Geophys. J. Int.* 158](https://doi.org/10.1111/j.1365-246X.2004.02281.x) & [IRIS SPUD EMTF](https://ds.iris.edu/spud/emtf) | `PEER-REVIEWED` / `OFFICIAL` | Basis & official CC0 data archive for `H33-R3-4` (blocked by sandbox firewall here). |
| `vendor-gems57-pin` | [buffedlizard55-lab/GEMSDOE78 `vendor/gems57`](https://github.com/buffedlizard55-lab/GEMSDOE78/tree/30f1ab9400f92036b0bc613425f1b5b6046f3897/vendor/gems57) | `SHARED TEMPLATE` | 23/23 SHA-256 verified shared holdout evaluator, CELF allocator, uniqueness guard & writer. |
| `owner-mirrors` | [GEMSDOE](https://github.com/buffedlizard55-lab/GEMSDOE) · [GEMSDOE24](https://github.com/buffedlizard55-lab/GEMSDOE24) · [GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32) | `OWNER MIRRORS` | 17/17 input pins restored & SHA-256 verified locally (`evidence/input_grid_audit.json`); 214 9-site TIFs audited. |

---

## §8. Autonomous Reproducibility Commands

*(Note: Raw rasters and `.npy` caches are restored into git-ignored `.cache/` so large binaries are never committed to Git; `data/` in the repository intentionally retains only [`data/README.md`](data/README.md).)*

```bash
# 1. Restore & SHA-256 verify all 17 competition/external inputs into .cache/gems_data
.venv/bin/python scripts/restore_data.py --group all --data-dir .cache/gems_data
GEMS_DATA_DIR=.cache/gems_data .venv/bin/python scripts/audit_inputs.py

# 2. Build 19 sanitized bands + 121 label-free cached feature channels
GEMS_DATA_DIR=.cache/gems_data .venv/bin/python scripts/prepare_data.py --skip-detector

# 3. Execute preregistered Round-3 3-experiment campaign + automated validators
GEMS_DATA_DIR=.cache/gems_data .venv/bin/python scripts/run_round3_da_hgcm_campaign.py

# 4. Re-validate saved Round-3 GeoTIFF bytes & rebuild GitHub Pages + run full test suite
GEMS_DATA_DIR=.cache/gems_data .venv/bin/python scripts/validate_submission.py \
  --submission docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif \
  --strict-zero-outside
.venv/bin/python scripts/build_site.py
.venv/bin/pytest -q
```

---

## §9. Explicit Limitations, Irregularities & Next Steps

1. **Literal Synthetic Lattice Guard (`IR-33-LATTICE-WITNESS-01`):** While `H33-R3-3` is genuinely unique across all `201` published submission GeoTIFFs of `GEMSDOE24..36` (`max 3-px overlap = 0.5265 <= 0.70`, `max |rho| = 0.0614 <= 0.90`), `GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` covers `99.87%` of the entire GeoDAWN off-catalogue footprint within `3 px`. Under `vendor/gems57/uniqueness.py`'s non-exemption rule, literal Scope B (`214` blobs) blocks automatic `promote`; a human cross-lane selector must explicitly decide whether synthetic calibration lattices in `inputs/calibration/` are excluded when allocating weekly slots.
2. **Proxy Truth vs. Private Expert Truth:** Both buffered whole-component hide-and-recover (`HOLDOUT-DTI = 0.114084`) and off-catalogue `SGMC` (`0.120202`) are proxies for unpublished USGS/INGENIOUS expert test labels; proxy improvements do not guarantee live leaderboard gains.
3. **Owner-Mirror Input Provenance & Unobservable $\lambda$:** Restored inputs match `registry/owner_mirror_input_pins.json` (`17/17` SHA-256), not direct authenticated DrivenData downloads (`IR-SAMPLE-LABEL-01`, `IR-33-NODATA-01`, `IR-33-RAD-01`, `IR-33-DA-01`). In Ben-David et al. (2010) Theorem 2, $\lambda$ remains unobservable without complete target truth.
4. **Next High-Upside Steps Outside Sandbox Firewall:** Stage official DOE GDR `#1682` (`BRIDGE_GIS.zip` field-verified Dixie/Gabbs LiDAR picks) and EarthScope/IRIS SPUD Magnetotelluric Transfer Functions (`H33-R3-4` 3D phase-tensor skew $|\beta_{\text{MT}}|$) in an unrestricted environment, pin their SHA-256 hashes, and evaluate whether 3D MT phase-tensor skew further boosts blind basin conduit recall above `H33-R3-3`.
