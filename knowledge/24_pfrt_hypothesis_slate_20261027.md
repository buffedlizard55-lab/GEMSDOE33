# 24. Ranked hypothesis slate and PFRT lane (2026-10-27)

Labels: `*` = USER/OWNER-REPORTED (no organizer receipt in this repo). HOLDOUT-DTI =
`gems-segment-pooled-v1`, alpha 0.2, beta 0.8, 300 m triangular kernel. No numeric
leaderboard projection is made for any candidate (knowledge/22 §3 measured that the
catalogue proxy anti-ranks the public B2 ladder on the emission axis).

## Why the reported peak is 0.2778* (GEMSDOE32 B2) — recap, verified in-repo

Byte forensics (knowledge/22, reproduced from SHA-pinned rasters): B2 (37,654 dots)
= GEMSDOE28/31 H27-4 (40,199) minus its 2,545 dots at 1 < d_cat <= 2 px; H27-4 =
d2.8 (44,090) minus its 3,891 d_cat <= 1 dots; d2.8 is a 2.8 px thinning of the
H19-5 multi-line mask (121,131). GEMSDOE36's file contains all B2 dots + 1,200.
Mechanism under DTI: extra dots within 300 m of an already-credited truth pixel add
FPw at alpha=0.2 and ~no TPw (kernel credit is a max), and catalogue-flank dots are
nearly pure FP because catalogue pixels are masked and hidden truth is *new* faults.
Deleting flank dots therefore raised the reported ladder monotonically
0.1922* -> 0.2477* -> 0.2600* -> 0.2708* -> 0.2778*. The marginal inclusion bar at
DTI 0.2778 is dTP/dFP > 0.0588 (src/gems33/metric.py inclusion_threshold, mirrored in
vendor template). This is a plausible mechanism, not proof: no organizer receipt
pairs bytes to score. Further pruning of B2 would be a pixel-subset duplicate.

## Ranked candidates not yet validated in this repo

| Rank | ID | Layers | Physical signature | Why it may catch catalogue-missing faults | Distinct from repo prior art | Cost / data viability |
|---|---|---|---|---|---|---|
| 1 (viable, this lane) | **PFRT** | `depth_to_base_surf`, `depth_to_base_surf_gms2`, `iso_grav_anom_hg` (cached 121-ch stack) | Basement-edge crest (geometric mean of percentile ranks of basement-depth gradient magnitude and \|gravity horizontal gradient\|), projected **updip** along -grad(depth_to_base) by `depth*cot(dip)/100m` px for dip in {50,60} deg, splatted and smoothed | A blind listric normal fault's basement density/depth break sits downdip of its piedmont emergence; unshifted gradient classifiers (CSHT/MSDB1/GVC1) score the buried break, not the emergence locus | No prior lane spatially *displaces* evidence along a modelled fault-dip vector; DPPS projected LiDAR scarps by persistence, not basement edges by depth-scaled listric offset | Low; cached only. Named mimic: prograding alluvial-fan toes and buried pediment edges |
| 2 (blocked) | COULOMB | GDR #1391 Quaternary traces | Okada dCFS lobes | Stress-loaded blind splays far from traces | Geomechanical, not geometric | Blocked: pinned CSV has centroids, no vertices/strike; vector JSON has no CRS and coordinates outside template bounds (knowledge/18). Source: https://gdr.openei.org/submissions/1391 |
| 3 (blocked) | CURVTRACE | raw 1 m USGS 3DEP DEM | >=1.5 km multi-azimuth curvature-trace continuity | Sub-100 m scarps invisible at 100 m | Scale, not re-ranking | Blocked: only 100 m aggregates pinned; tile host outside sandbox allowlist. Source: https://www.usgs.gov/3d-elevation-program |
| 4 (blocked) | PALEOTEMP | DOE GDR #1391 2 m probe / sinter inventory (not pinned) + cond_surf | Relict hydrothermal conduits | Inactive conduits invisible to active-seed lanes | Temporal, not active-thermal | Blocked: specific payload not pinned / not obtainable here. Source: https://gdr.openei.org/submissions/1391 |
| 5 (not untried) | HMDT | cond_surf, TMI_up150-RTP, iso_grav_anom_hg | Signed magnetite-destruction x clay-cap dipole | Oriented alteration doublet | Signed vs unsigned fusion | Artifact exists with **no holdout run card** (IR-33-HMDT-UNGATED-01); cannot be validated from final bytes fold-safely |

## Lane (single method paragraph, frozen)

**PFRT:** label-free listric dip-projection. Edge = sqrt(rank(depth-grad-mag) *
rank(|grav-HG|)) over the evaluation domain; crest = NMS ridge of the edge with
rank >= 0.90 and depth-gradient magnitude > 0; each crest pixel splats its edge
value at the two updip projections (dip 50/60 deg, offset clipped to [1,10] px)
with a 3x3 tent kernel; surface = gaussian(sigma=1) splat, percentile-ranked on the
domain. Emission: shared CELF-300m, d_visible > 2 px, budget 37,654, spacing 2.5.
No catalogue-derived feature, no supervised fit: fold safety is by construction;
the only fold-dependent inputs are the visible-catalogue exclusion mask and the
evaluation domain. Named non-fault mimic: prograding fan toes / buried pediments.
Frozen in `evidence/pfrt_preregistration_20261027.json` before any PFRT holdout run.

Sources (manual review): DrivenData #306 https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ ·
reference solution https://github.com/drivendataorg/gems-prize-reference-solution ·
USGS GeoDAWN https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and ·
DOE GDR #1391 https://gdr.openei.org/submissions/1391 · EPSG:32611 https://epsg.io/32611 ·
Tversky index https://en.wikipedia.org/wiki/Tversky_index
