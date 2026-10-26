# 22. Why B2 (0.2778*) won — byte-level forensics — and the FSML-PU lane (2026-10-26)

Evidence labels: `*` = USER/OWNER-REPORTED public score (no organizer receipt in this repo).
`HOLDOUT-DTI` = `gems-segment-pooled-v1`, α=0.2, β=0.8, 300 m triangular kernel, 60,988 withheld
catalogue positives. Reproduction: `scripts/forensic_b2_20261026.py` on SHA-pinned bytes restored by
`scripts/restore_data.py --group all` (17/17 verified) + `registry/focus_rasters_20261026_r3.json`.

## 1. The nine focus sites' best files are ONE emission family (measured today)

| Site | Best file (owner-reported*) | Dots | d_cat≤1 | 1<d≤2 | 2<d≤3 | d>3 | Relation (measured) |
|---|---|---:|---:|---:|---:|---:|---|
| 19GEMSDOE (origin) | H19-5 mask 0.1922* | 121,131 | 9,651 | 7,675 | 6,841 | 96,964 | binary {0,1} mask (not a probability surface) |
| GEMSDOE24 | dotted d1.5 0.2477* | 60,069 | 5,355 | 3,414 | 3,169 | 48,131 | 1.5 px thinning of H19-5 mask |
| GEMSDOE25 / GEMSDOE30 | dotted d2.8 0.2600* | 44,090 | 3,891 | 2,545 | 2,171 | 35,483 | pixel-identical sets (xor=0) |
| GEMSDOE27 | topo-gap on d1.5 0.2449* | 61,328 | 5,413 | 3,462 | 3,312 | 49,141 | d1.5 + gap closure; scored below d2.8 |
| GEMSDOE28 / GEMSDOE31 | H27-4 solo d2.8 0.2708* | 40,199 | 0 | 2,545 | 2,171 | 35,483 | pixel-identical (xor=0); = d2.8 minus its 3,891 d_cat≤1 dots |
| GEMSDOE32 | **B2 0.2778\*** | 37,654 | 0 | 0 | 2,171 | 35,483 | = H27-4 minus its 2,545 (1,2] dots; 0 dots outside H27-4 |
| GEMSDOE36 | "Anderson PINN" 0.2750* | 38,854 | 0 | 0 | 2,281 | 36,573 | **contains all 37,654 B2 dots exactly** + 1,200 extra |
| GEMSDOE33 | h33d analog 0.2632* | — | — | — | — | — | family-adjacent (registry) |

Every B2 dot lies within 3 px of every other family member (fraction 1.000). Independent surfaces in
the registry (G27-h29 0.2190*, G30-MSDB1 0.1462*) share only 42.5% / 49.6%.

## 2. Why B2 scored highest (mechanism, PhD-level reading of the DTI)

DTI = TPw / (TPw + 0.2·FPw + 0.8·FNw), k(d)=max(1−d/300 m,0), catalogue pixels masked pixel-exactly
(organizer clarification linked in GEMSDOE36's README:
https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4).

1. **Kernel saturation ⇒ thinning is free recall insurance.** A truth pixel's credit is the *maximum*
   over nearby prediction pixels. Extra dots within 300 m of an already-credited truth pixel add
   ~zero TPw but full FPw. Thinning 121,131 → 60,069 → 44,090 kept almost all coverage while
   deleting redundant FP mass: 0.1922* → 0.2477* → 0.2600*.
2. **Catalogue-flank dots are nearly pure FP.** Hidden truth = *new* faults; catalogue pixels are
   masked. A dot 100–200 m from a mapped fault earns credit only if an unmapped fault happens to lie
   within 300 m of it — empirically rare relative to its FP cost. Deleting d_cat≤1 (+0.0108*) then
   1<d_cat≤2 (+0.0070*) raised the score monotonically. B2 is exactly that deletion endpoint.
3. **The marginal bar is low but real.** Adding dots raises DTI iff ΔTP/ΔFP > 0.2·DTI/(1−0.2·DTI)
   = 0.0588 at DTI 0.2778 (`src/gems33/metric.py:inclusion_threshold`). GEMSDOE36's +1,200 dots on
   top of B2 scored 0.2750* < 0.2778*: that batch's marginal hit rate was below ~5.9%.
4. **The underlying H19-5 mask carries genuine multi-physics signal.** Per 19GEMSDOE's README it is
   the top-2.45% level set of four corroborating lines (power-law tip/step-over prior, GDR #1391
   thermal/geochem inversion, DEM openness/LRM scarps, geopotential worms) with a
   second-best-line rejection gate. No independent surface in ~90 sibling sites has beaten its
   thinned emissions publicly (best independent: GEMSDOE70 0.2478*, GEMSDOE24-family aside).

**What this does NOT prove:** that pruning *caused* 0.2778 (no receipt pairs bytes to score; hidden
labels unseen), or that further pruning (d_cat>3, 35,483 dots) would score higher. That file would
be a pixel-subset of B2 → duplicate under the parallel-run protocol → not submittable from this repo.

## 3. The proxy trap (measured today)

Scoring the ladder against the *full catalogue* (illustrative mechanics only): d1.5 DTI 0.1719,
d2.8 0.1618, H27-4 0.0491, **B2 0.0067**. The catalogue proxy *anti-ranks* the public ladder on the
emission axis, because flank pruning deletes exactly the dots a catalogue-recovery proxy rewards.
Consequence: **no numeric public-score estimate for any candidate is defensible from holdout alone.**
The honest estimator is ordinal: a candidate has evidence *consistent with* beating 0.2778* only if
its fold-safe surface beats both the fold-safe CSHT best (HOLDOUT-DTI 0.1379 screen) and the fixed
H19-5 reference emission (0.1620, not fold-safe) under identical emission — and even then the public
number remains unknowable until an organizer receipt exists.

Additionally, GEMSDOE32's parallel sessions identified `IR-A8A-PU-BIAS-01`: training with
negatives = "not in catalogue" teaches the model to suppress genuinely unmapped faults (they sit in
the negative pool). Every supervised surface in this repo (CSHT, B1) has this bias. Positive-
Unlabeled learning (Elkan & Noto 2008; spy/reliable-negative mining, Liu et al. 2002) is the
standard correction and is untested in this repo.

## 4. Ranked candidate slate (3–5, per brief; qualitative gains only)

| Rank | ID | Layers | Physical signature | Why it can find catalogue-missing faults | vs prior art in this repo | Cost / data |
|---|---|---|---|---|---|---|
| 1 | **FSML-PU** (this session's lane) | 4 disjoint channel groups from cached 121-ch stack (lidar scarp; mag/grav worms; basement/conductivity/radiometric cover; strain/seismic/thermal incl. new wellspring density) + fold-visible tip-lobe geometry | 4 spy-PU HGB experts, rank-fused × second-best-line gate (H19-5's corroboration idea, re-derived fold-safely); CELF dotted emission, d_cat>2 | PU removes the "unmapped = negative" suppression; gate demands ≥2 independent physics lines, the property that made H19-5 generalize to hidden labels | CSHT: 3 non-PU experts, weighted (ungated) fusion, geographic negatives. Decides knowledge/16's open leakage-vs-signal question | Medium; cached data only |
| 2 | BUDGET-DESCENT | best fold-safe surface | budget {25k vs 37,654} chosen on screen (folded into FSML lane as emission selection) | Public ladder is monotone in pruning; repo budget 37,654 was inherited from B2, never optimized | All prior repo emissions fixed at 37,654 | Low; cached |
| 3 | PFRT | depth_to_base_surf, iso_grav_anom_hg | updip projection of basement edge by bounded listric kernel | blind listric faults offset from density break | unrun (round-4 slate) | Low–med; cached; high duplicate risk |
| 4 | COULOMB | GDR #1391 Quaternary traces + slip | ΔCFS lobes (Okada) | stress-triggered splays beyond mapped tips | unrun | **Blocked:** cached CSV lacks vertices/strike; vector JSON has no CRS (knowledge/17) |
| 5 | CURVTRACE | raw 1 m USGS 3DEP | ≥1.5 km curvature-trace continuity | sub-100 m scarps | LLC used 100 m aggregates only | **Blocked:** raw tiles unstaged; host outside sandbox allowlist |

## 5. Lane (single method paragraph, per protocol)

**FSML-PU:** fold-safe multi-line corroboration with PU-corrected experts. Four HGB experts on
disjoint physics channel groups, each trained per fold by two-step spy-PU (P vs U → reliable
negatives → P vs RN) using only fold-visible catalogue; a fifth untrained geometric line from
fold-visible fault-tip PCA lobes; percentile-rank fusion multiplied by a second-best-line gate
`clip(second/0.75, 0.30, 1.0)` (V1) vs ungated mean-rank ablation (V2); CELF-300 m dotted emission
with d_visible>2 px; budget 25,000 vs 37,654 selected on the screen split only. Named non-fault
mimic: Lake Lahontan shorelines, playa/evaporite margins, and lithologic contacts that corroborate
across gravity+radiometric+topography without a throughgoing fault. Frozen in
`evidence/fsml_preregistration_20261026.json`. Duplicate guard: surface before placement AND final
dots vs 22 registry rasters (ρ>0.90 or >70% within 3 px ⇒ duplicate, stop).

Sources: DrivenData #306 problem/metric https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ ·
reference solution https://github.com/drivendataorg/gems-prize-reference-solution ·
USGS GeoDAWN https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and ·
DOE GDR #1391 https://gdr.openei.org/submissions/1391 ·
Elkan & Noto (2008) https://doi.org/10.1145/1401890.1401920 ·
Liu et al. (2002) spy EM https://cdn.aaai.org/ICML/2002/ICML02-053.pdf ·
Faulds & Hinz (2015) https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf
(URLs for manual review; not fetched from this sandbox except GitHub mirrors via git.)
