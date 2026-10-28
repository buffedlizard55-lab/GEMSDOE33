# GEMSDOE33 — Hypothesis slate A33-R7 (2026-10-28, preregistered before code)

Standing-prompt Rule 4 slate. No numeric DTI gain is invented. Historical scores are
OWNER/USER-REPORTED, not organizer-confirmed. Lane for this session (single method):
**multiscale quadrature phase-congruency of potential fields with gravity–magnetic
orientation agreement (A33-R7-PHCONG).** Budget: ≤3 experiments, ≤2 h. No slot unless
screen + independent confirmation beat the fold-safe incumbent with positive paired CI,
both uniqueness gates pass (Spearman |ρ|≤0.90 and ≤70% dots within 3 px, surface AND
final dots, vs the 21-raster registry), canary AUC≤0.90, and saved-byte format audit passes.

## Why B2 (0.2778*) won — byte-verified prior art (knowledge/22)
All nine focus sites' best files are thinnings/prunings of the 121,131-px H19-5 mask:
60,069 dots 0.2477* → 44,090 0.2600* → −catalogue flank ≤1 px 40,199 0.2708* →
−flank ≤2 px **37,654 = B2 0.2778*** (GEMSDOE36 = B2 dots exactly +1,200, 0.2750*).
Mechanism: under DTI α=0.2/β=0.8 with a 300 m triangular kernel and pixel-exact
catalogue masking, deleting ≤200 m catalogue-flank dots cuts 0.2·FP_w at ~zero TP_w
cost. Copying/perturbing that family is duplicate-blocked; a new lane must find dots
the H19-5 surface does not already rank highly.

## Candidate 1 — SELECTED: A33-R7-PHCONG
- **Layers:** cached 100 m bands `tmi`, `ext_TMI_up150`, `iso_grav_anom`
  (GeoDAWN magnetics/gravity in `training_features.tif`, 17-pin SHA-verified owner mirror).
- **Signature:** multiscale (wavelengths 4/8/16/32 px) monogenic quadrature
  phase congruency PC = |Σ_s (even_s, oddx_s, oddy_s)| / (Σ_s A_s + ε), computed per
  field; surface = geometric mean of the three PC fields × gravity–magnetic
  orientation agreement (|cos Δθ| on double-angle odd-vector orientation).
  Phase congruency is amplitude-invariant: a weak, deep basement step produces the
  same PC as a strong shallow one (Kovesi local-energy principle).
- **Why catalogue-missing:** blind basement faults under piedmont/basin cover have
  little topographic or radiometric expression and weak absolute gradients, so
  gradient-magnitude detectors (worms, tilt, HGB on raw gradients) rank them below
  lithologic edges; PC normalises amplitude away and keeps the coherent step.
- **Mimic (named):** intrusive plutonic contacts and caldera ring margins, plus
  airborne survey line seams — all are genuine potential-field step edges.
- **Distinction from repo prior art:** FSML2 used gradient-magnitude multiscale
  worms as one unsigned line; GEMSDOE76-style tiltworm is external prior art scored
  elsewhere; CSHT/FSML supervised HGBs use raw/derived gradient channels. No repo
  lane has used vector-sum/sum-of-amplitudes phase congruency or cross-field
  orientation agreement. Flagged in knowledge/22_selector_safety_review as the
  highest qualitative priority, never canary- or novelty-tested.
- **Cost:** low (~minutes CPU, FFT on cached bands). **Viable now, no new data.**

## Candidate 2 — reserve (Exp 2/3 only if Exp 1 canary/mechanism is non-degenerate)
A33-R7-PCSUP: fold-safe HistGradientBoosting supervised **only** on PHCONG channels
(3 PC fields, per-scale PC, orientation agreement) + subsurface channels
(`cond_surf`, `depth_to_base_surf`, geodetic strain), explicitly excluding all
topographic/LiDAR/radiometric channels. Same physical mechanism as Candidate 1 with
learned fault-vs-intrusive weighting from fold-visible catalogue only. Risk:
supervised rankings converge (FSML-PU was a surface duplicate of CSHT at 87.51%);
the pre-placement surface guard decides. Mimic: intrusive contacts learned as faults.

## Candidate 3 — A33-R7-XGRAD (not run)
Layers `iso_grav_anom`, `tmi`. Signature: normalised cross-gradient
|∇grav × ∇mag| near zero with both gradient magnitudes high (structurally coupled
basement boundary). Why missing: coupled gravity–magnetic basement faults under
cover. Mimic: intrusive contacts (also coupled). Distinction: no repo lane uses the
cross-gradient structural-similarity functional. Cost low. Deferred by budget.

## Candidate 4 — A33-R4-HMDT (not fresh; not run)
Signed conductivity×(up150−RTP) cross-gradient dipole in dilational zones
(knowledge/17/18). An ungated HMDT TIFF exists from a parallel session with no
reproducible fold-safe runner (IR-33-HMDT-UNGATED-01), so it is **not** a fresh
untried idea. Mimic: saline playa / nonmagnetic tuff. Not run.

## Candidate 5 — A33-R5-CURVTRACE (blocked)
Raw 1 m USGS 3DEP DEM multi-azimuth curvature trace continuity. Official free source:
USGS 3DEP (https://www.usgs.gov/3d-elevation-program). **Not obtainable here:** the
3DEP tile host is outside the sandbox outbound allowlist and no tiles are staged;
100 m aggregates cannot be re-interpolated into 1 m evidence. Blocked, not viable.

## Selection
Candidate 1 (Exp 1). Holdout: `SegmentHoldout(buffer_px=15)` quadrant screen +
`DiagonalSegmentHoldout(buffer_px=20)` confirmation, pooled DTI
`gems-segment-pooled-v1` (α=0.2, β=0.8, 300 m triangular kernel), matched-random
paired control, per-field leakage canaries, CELF-300 m emission at 37,654 dots,
surface+final-dot duplicate guard vs 21 registry rasters, `submission_writer`
saved-byte audit. Incumbent context (recorded, unpaired): B1_regional screen
0.112418 / confirmation 0.115122 (evidence/a33_r2_run_card_20261026.json).
A projection is never written as a score. Negative results are deliverables.
