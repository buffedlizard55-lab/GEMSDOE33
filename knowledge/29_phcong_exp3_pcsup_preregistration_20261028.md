# A33-R7 Exp 3 preregistration — PCSUP supervised subsurface model (2026-10-28, before Exp 3 code)

Exp 2 verdict: **negative**. PHCONG surface under d=2.8 dot-thinning scored
HOLDOUT-DTI screen 0.160093 / confirmation 0.159986 but lost paired to dot-thin
random on both splits (screen Δ −0.009834 [−0.015758, −0.003545], 0/4; confirmation
Δ −0.011082, 0/4), and its per-pixel canary AUC is ≈0.507. Conclusion: the
label-free PHCONG surface has no measurable per-pixel fault discrimination on the
catalogue proxy; Exp 1/2 DTI is an emission-coverage effect. **Exp 1's `promote`
verdict is withdrawn** (its gates omitted the same-operator matched-random gate).
Neither Exp 1 nor Exp 2 artifact is OK to submit. This is experiment 3/3.

## Exp 3 — A33-R7-PCSUP (slate Candidate 2, knowledge/27)
- **Features (subsurface only, no topography/LiDAR/radiometric):** PHCONG channels
  (`pc_tmi`, `pc_ext_TMI_up150`, `pc_iso_grav_anom`, orientation agreement,
  combined surface) + cached `tmi`, `ext_TMI_up150`, `iso_grav_anom`,
  `iso_grav_anom_hg`, `iso_grav_anom_vg`, `cond_surf`, `depth_to_base_surf`,
  `geod_2ndinv`, `geod_shearrate`, `geod_dilaterate`, `tc`, `tmi_hg`, `tmi_vg`.
- **Model:** one HistGradientBoostingClassifier per fold, trained only on that
  fold's `train` mask with positives = fold-visible catalogue, negatives =
  train & ~visible with distance-to-visible > 8 px (splay-safe), class-weighted.
  No held-out truth, no catalogue-derived feature (distance-to-catalogue is
  used only to define training negatives, never as a feature).
- **Emission:** CELF-300 m (Exp 1 operator) at identical fold/full budgets,
  because the model surface — unlike Exp 1 — must first prove paired value vs
  **both** same-operator controls below.
- **Gates (all required):** screen + confirmation DTI > recorded B1 with CI
  lower bound above it; paired Δ vs CELF-random **and** vs CELF-emitted PHCONG
  (Exp 1 surface, recomputed per fold) strictly positive CI on screen;
  per-feature canaries ≤0.90 (model surface canary reported too); both
  uniqueness gates vs 21 registry rasters; saved-byte format audit.
- Named mimic: intrusive contacts learned as faults. If any gate fails:
  verdict negative, no submission is promoted this session, and the honest
  deliverable is the negative result plus the IR-33-CELF-RANDOM-01 finding.
