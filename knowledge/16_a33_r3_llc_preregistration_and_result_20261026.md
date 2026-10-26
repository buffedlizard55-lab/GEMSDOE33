# A33-R3: preregistered slate, line-localised CSHT result, and what it says about beating B2 (2026-10-26)

**Evidence labels.** Every performance number here is labelled.
- **HOLDOUT-DTI** means evaluator `gems-segment-pooled-v1` (`vendor/gems24_template/holdout.py`), α=0.2, β=0.8, 300 m triangular kernel, 60,988 withheld catalogue positives per split, with a 10 km block-bootstrap 95% CI.
- Historical leaderboard numbers carry a \* and are **USER/OWNER-REPORTED**. None is organizer-confirmed.
- Nothing here projects a competition score.

## 1. Preregistration (frozen before any R3 code or evaluation)

- File: `evidence/a33_r3_preregistration_20261026.json`, sha256 `79e7564b…a18c8` (full hash in `.sha256`).
- Authoritative freeze: git commit `61e79c6` at 2026-10-26T04:40:15Z. The JSON's hand-typed `frozen_utc` is wrong; see `IR-33-R3-PREREG-TIMESTAMP-01`.
- `src/gemsdoe33/r3_line_localized.py` and `scripts/run_a33_r3.py` were written after the freeze. The campaign ran from 04:44:51Z to 05:00:28Z (995 s).

| Rank | ID | Layers | Physical signature / transform | Why it could find faults missing from USGS/INGENIOUS | Status |
|---|---|---|---|---|---|
| 1 | **A33-R3-LLC** | `lid_step_max`, `lid_ex_max`, `lid_cross_max`, `lid_valid`, `det_elev_slope` (+ CSHT prior) | Multi-scale Hessian ridge strength (Steger 1998; Frangi 1998), integrated along strike over 12 azimuths with a 500 m × 75 m anisotropic Gaussian, then 1-px NMS. LiDAR and LiDAR-void regimes are handled separately. | Unmapped faults are short, low-relief scarps. Integrating along strike accumulates weak collinear evidence and puts dots on traces rather than zone centroids. | **Run — negative** |
| 2 | A33-R3-SGC | fold-visible catalogue orientation tensor, `lid_strike` | cos² misfit between local scarp strike and regional mapped-fault grain | Faults in a Basin-and-Range domain are sub-parallel. | Reserve |
| 3 | A33-R3-MAGT | `rtp`, `ext_TMI_up150`, `depth_to_base_surf` | Zero-crossings of the tilt derivative at two continuation heights under deep cover | Basement offsets that are buried with no scarp | Reserve; GEMSDOE76 tiltworm (0.2343\*) is close prior art, so duplicate risk is high |
| 4 | A33-R3-LSRT | absolute DEM (USGS 3DEP) | Reject iso-elevation scarp chains near the Lahontan highstand (1318–1341 m; Adams & Wesnousky 1998) | Removes the main intrabasin mimic | **Blocked:** the 3DEP/TNM hosts return HTTP 000 from this sandbox |
| 5 | A33-R3-PALEOTEMP | DOE GDR #1391 sinter/tufa + 2 m temperature probes | Conduit proximity | Blind systems (~39% per Faulds & Hinz 2015) | **Blocked:** GDR returns HTTP 000 |

The table is ranked by expected improvement against cost, judged qualitatively. No numeric gain was claimed before measurement.

## 2. Protocol (as frozen)

1. **Leakage canary** on every new channel (quadrant split, 15 px buffer). Any AUC above 0.90 stops the run.
2. **Pre-placement surface uniqueness** against 22 registry rasters (`registry/focus_rasters_20261026_r3.json`):
   - Spearman |ρ| ≤ 0.90;
   - top-37,654 3-px overlap ≤ 70%.
3. **Experiment 1/3 screen** (`quadrant-buffered-15px-v1`).
   - Comparators: in-run A33-R2-CSHT recipe, B1_regional, matched_random, and the informational H19-5 reference (not fold-safe).
4. **Selection:** the best screen variant goes forward.
5. **Experiment 2/3 confirmation** (`diagonal-wedge-buffered-20px-confirm-v1`).
6. Experiment 3/3 is reserved for a tool defect only. It was **unused**.
7. **Full CELF-300m placement** (37,654 dots, d_cat > 2 px, self-spacing 2.5 px), then:
   - final-dot uniqueness check;
   - shared writer;
   - saved-byte audit;
   - `promotion.assess`.

**Promotion gates:**
- **Screen:** beat max(in-run CSHT, 0.136716, in-run B1), with paired CI vs CSHT > 0 and at least 3/4 fold wins.
- **Confirmation:** beat max(in-run CSHT, 0.131169), with CI > 0 and at least 3/4 wins.

## 3. Results

**Canaries (two-sided AUC, pooled / max fold).** All passed.

| Channel | Pooled | Max fold |
|---|---|---|
| e_lid | 0.5657 | 0.5890 |
| e_void | 0.5122 | 0.5240 |
| ridge_rank | 0.5966 | 0.6336 |
| oli_rank | 0.6381 | 0.6743 |
| l_line | 0.5074 | 0.5106 |

**Surface uniqueness.**
- V1 (γ=1): **duplicate** of our own A33-R2-CSHT (79.15% > 70%). It was dropped before evaluation.
- V2 (γ=0.5): passed. Worst overlap was 67.79% vs A33-R2-CSHT, with max |ρ| = 0.0111.

| HOLDOUT-DTI | Screen (quadrant) | Confirmation (diagonal wedge) |
|---|---|---|
| **V2_gamma05 (A33-R3-LLC)** | **0.137868** [0.1286, 0.1479] | **0.131506** [0.1208, 0.1414] |
| A33-R2-CSHT (in-run) | 0.137555 [0.1261, 0.1498] | 0.132066 [0.1201, 0.1440] |
| B1_regional | 0.110783 [0.1000, 0.1216] | 0.113576 [0.1029, 0.1244] |
| matched_random | 0.073931 [0.0710, 0.0769] | — |
| H19-5 reference (NOT fold-safe, informational) | 0.162036 [0.1516, 0.1725] | — |
| **Paired Δ LLC − CSHT** | **+0.000313** [−0.008009, +0.008288], 2/4 wins | **−0.000560** [−0.009035, +0.007547], 2/4 wins |
| Paired Δ LLC − B1 | +0.027085 [+0.015511, +0.039079], 4/4 | +0.017930 [+0.005860, +0.029612], 3/4 |

Per-fold LLC − CSHT differences:
- Screen: NW −0.0104, NE +0.0031, SW +0.0069, SE −0.0028.
- Confirmation: N −0.0208, E +0.0096, S +0.0080, W −0.0119.

**Verdict: NEGATIVE.** The failed gates are `screen_beats_current_best` and `independent_confirmation`. 0 slots were spent.

**Final dots.** Unique against all 22 rasters.
- Max |ρ| = 0.0194.
- Max 3-px overlap = 43.25% (vs G25-h66); 37.48% vs G32-B2.
- Format audit passed: 37,654 dots, 0 on-catalogue dots, all cells finite, values in {0, 1}.
- Artifact: `docs/downloads/gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif`, sha256 `76f9e157d01bb9bec2d98c3c5941b6114e06e0f439272d5f140af6e3584c8825`.
- **OK TO DOWNLOAD: YES. OK TO SUBMIT: NO.**

## 4. Interpretation

1. **Why line localisation did not help (interpretation, not a tested claim).**
   - The metric's 300 m triangular kernel credits a dot anywhere within 3 px of a truth pixel.
   - CSHT + CELF-300m already places dots on CSHT ridges, which are usually within 300 m of the trace that line-localisation would find.
   - Sharpening position below the kernel scale therefore buys almost nothing.
   - The line evidence by itself is a weak predictor of withheld faults (l_line canary AUC 0.507). Multiplying it in mostly reshuffles dots among equally scored cells.
   - It helped in the LiDAR-gap-heavy NE quadrant and in SW/E/S, and hurt in NW/N/W. The net effect is indistinguishable from zero.
2. **The holdout gap to the B2 family (IR-33-H19-HOLDOUT-GAP-01).**
   - The fixed H19-5 surface beats fold-safe CSHT by +0.0242 [+0.0150, +0.0328], 4/4 folds, on the same withheld segments.
   - Two explanations remain open:
     - (a) leakage: H19-5 was produced with the full catalogue visible, so some withheld segments may have shaped it;
     - (b) a real advantage from H19-5's multiline corroboration / power-law budget.
   - The public ordering points the same way: B2 0.2778\* against CSHT-like MSDB1 0.1462\*.
   - **The single most informative next experiment is a fold-safe re-derivation of the H19-5 recipe.** It decides whether the gap is signal (port the recipe into a new lane) or leakage (the holdout cannot rank the B2 family).
3. **Can we beat GEMSDOE32 B2 (0.2778\*)?**
   - Not with anything measured in this repository.
   - Every fold-safe surface we have built sits at HOLDOUT-DTI ≈ 0.13–0.14, against ≈ 0.16 for the H19-5 reference.
   - B2's own advantage came from removing false-positive mass: it pruned dots within 2 px of the catalogue, a halo that carries almost no hidden-truth credit. It did not come from discovering new faults (knowledge/13).
   - Beating it needs a surface that out-ranks H19-5 on fold-safe holdout, followed by the same halo-aware CELF emission.

## 5. Sources (official / peer-reviewed)

- Competition problem, metric and format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Steger, C. (1998). An unbiased detector of curvilinear structures. *IEEE TPAMI* 20(2):113–125. https://doi.org/10.1109/34.659930
- Frangi, A. F., et al. (1998). Multiscale vessel enhancement filtering. *MICCAI'98*, LNCS 1496:130–137. https://doi.org/10.1007/BFb0056195
- Adams, K. D., & Wesnousky, S. G. (1998). Shoreline processes and the age of the Lake Lahontan highstand in the Jessup embayment, Nevada. *GSA Bulletin* 110(10):1318. https://pubs.geoscienceworld.org/gsa/gsabulletin/article/110/10/1318/183306/
- Faulds, J. E., & Hinz, N. H. (2015). Favorable tectonic and structural settings of geothermal systems in the Great Basin region. *WGC 2015*. https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program
- DOE GDR #1391: https://gdr.openei.org/submissions/1391
- Both of the last two were unreachable from the sandbox (HTTP 000).

## 6. Reproduce

```bash
.venv/bin/python scripts/restore_focus_registry_r3.py      # 22 registry rasters, sha256-verified
.venv/bin/python scripts/run_a33_r3.py                      # refuses to rerun if the run card exists (--force logs an irregularity)
.venv/bin/python scripts/select_submission.py --date 20261026   # automated OK-TO-SUBMIT decision
```
