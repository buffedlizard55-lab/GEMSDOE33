# A33-R7 PHCONG — results and executive summary (2026-10-28)

## Executive summary table — what to download, estimated score, uniqueness

Every historical DrivenData figure is **OWNER/USER-REPORTED (NOT ORGANIZER-CONFIRMED)**.
Every local figure is **HOLDOUT-DTI (`gems-segment-pooled-v1`, 60,988 withheld catalogue
positives, 95% CI)** — a catalogue hide-and-recover proxy, **not** a leaderboard estimate.
No numeric leaderboard score is estimable for any unique file (no validated transfer from
the catalogue proxy to the private expert-labelled truth exists in this repo).

| Site | Best file (owner-reported score*) | File to download from THIS repo | HOLDOUT-DTI / estimate | Unique vs 21-raster registry? | OK to submit? |
|---|---|---|---|---|---|
| GEMSDOE24 | h25-1 d1.5, 60,069d, 0.2477* | — (prior art) | not estimable | family member | NO — H19-5 family |
| GEMSDOE25 | dotted d2.8, 44,090d, 0.2600* | — | not estimable | = GEMSDOE30 byte-identical | NO |
| GEMSDOE27 | topo-gap, 61,328d, 0.2449* (h29 0.2190* strongest independent) | — | not estimable | family/superset | NO |
| GEMSDOE28 | h36-1, 37,660d, 0.2710* | — | not estimable | >93% vs B2 | NO |
| GEMSDOE30 | d28, 44,090d, 0.2600* | — | not estimable | = GEMSDOE25 | NO |
| GEMSDOE31 | h27-4 solo, 40,199d, 0.2708* | — | not estimable | B2 parent | NO |
| **GEMSDOE32** | **h33-2-b2, 37,654d, 0.2778* (9-site peak)** | — (do not copy) | not estimable | reference | NO — already submitted, duplicate |
| GEMSDOE36 | anderson, 38,854d, 0.2750* | — | not estimable | B2 dots +1,200 exactly | NO |
| **GEMSDOE33 (this repo, newest)** | h33d 0.2632* (retired) | **`gemsdoe33-a33-r7-pcsup-37654-20261028-d1f9cca0af02-zeros.tif`** | HOLDOUT-DTI screen 0.168298 [0.161, 0.175†], confirmation 0.163037 — **leaderboard: not estimable** | **YES** — surface+dots pass vs 21 rasters (see run card) | **🛑 NO — holdout gate failed vs same-operator random; research only** |

†CI from experiment JSON. The newest unique download is PCSUP; PHCONG/PHCONGDT twins are
also in `docs/downloads/` (research only). **No file in this repo is OK TO SUBMIT.**

## Why B2 got 0.2778* (byte-verified, knowledge/22)
B2 added zero detections to H19-5: it deleted the last 2,545 catalogue-flank (≤200 m)
dots from the d2.8 thinning. Under DTI α=0.2/β=0.8 + 300 m kernel + pixel-exact
catalogue masking, flank dots cost 0.2·FP_w and earn ~0 TP_w, so deletion raised the
score monotonically (0.1922→0.2477→0.2600→0.2708→0.2778*). Grafting dots back
(GEMSDOE36 +1,200 → 0.2750*; GEMSDOE33 h33d +stepovers → 0.2632*) lowered it: added
dots must clear ΔTP_w/ΔFP_w > 0.0714 and the grafts missed real (curved, >300 m) traces.

## Can we beat 0.2778*? — measured answer: not yet, and the proxy cannot prove it
Three preregistered experiments ran this session (budget 3/3 used):

| Exp | Candidate | Screen / Confirmation HOLDOUT-DTI | Paired vs same-operator random | Canary | Uniqueness | Verdict |
|---|---|---|---|---|---|---|
| 1 | PHCONG (label-free phase congruency, CELF) | 0.169316 [0.162772,0.175496] / 0.170588 [0.163996,0.176581] | **−0.011098 [−0.016260,−0.006098], 0/4** (CELF-random) | max AUC 0.5224 | pass (ρ≤0.0036, ≤18.5%) | **negative (promote withdrawn)** |
| 2 | PHCONGDT (same surface, dot-thin d2.8) | 0.160093 / 0.159986 | **−0.009834 [−0.015758,−0.003545], 0/4** | 0.5224 | pass | **negative** |
| 3 | PCSUP (supervised subsurface HGB, CELF) | 0.168298 / 0.163037 | −0.010163 [−0.022979,+0.002861] vs CELF-random; −0.001018 vs PHCONG (CIs span 0) | max AUC 0.5726 (18 feats) | pass | **negative** |

Findings:
1. The PHCONG per-pixel surface is ≈random on withheld catalogue pixels (AUC 0.507);
   its high absolute DTI is emission coverage, not detection. Amplitude-invariant
   potential-field edges do not, alone, locate catalogue-type faults in this stack.
2. **IR-33-CELF-RANDOM-01 / IR-33-FOLD-BUDGET-01** (registry/irregularities.json):
   at the inherited 2.5% fold-emission density (deployment is 0.73%), spaced uniform
   dots saturate the 300 m kernel and random emission scores 0.17–0.18, compressing
   all discrimination. This flaw also affects the THKCOND/BASESTEP campaign family
   and invalidates cross-campaign DTI comparisons at mismatched densities. The next
   campaign must (a) emit folds at deployment density, (b) re-baseline B1/CSHT at
   that density, and (c) require a strictly positive paired Δ vs same-operator
   matched-random before any promotion.
3. Supervising only on PHCONG+subsurface channels (PCSUP) did not beat the
   label-free surface — the subsurface channel set carries little catalogue-proxy
   signal beyond coverage (contrast CSHT's topo/LiDAR-inclusive 0.1367 at its own
   density; densities differ, so no cross-campaign ranking is claimed).

## Validator (newest artifact, saved bytes, no human inspection)
`gemsdoe33-a33-r7-pcsup-37654-20261028-d1f9cca0af02-zeros.tif`: single-band float32,
EPSG:32611, 3730×3292, template transform, whole array finite in [0,1], 37,654 dots,
strict saved-byte audit pass (evidence/a33_r7_pcsup_experiment_20261028.json).
Name/note (≤140): see run card. Portal acceptance remains unverified; the earlier
"[0,1] range" portal error cannot be caused by this file's values.

## Run card (JSON)
```json
{"hypothesis":"Multiscale monogenic phase-congruency (tmi/up150/gravity) x orientation agreement finds blind basement faults; supervised variant learns fault-vs-intrusive weighting on subsurface channels only","mechanism":"Amplitude-invariant phase-coherent potential-field step edges under cover","named_non_fault_mimic":"Intrusive plutonic contacts, caldera ring margins, airborne survey seams","holdout_dti":{"label":"HOLDOUT-DTI","evaluator_version":"gems-segment-pooled-v1","withheld_positives":60988,"PCSUP_screen":0.168298,"PCSUP_confirmation":0.163037,"paired_vs_CELF_random_CI95":[-0.022979,0.002861]},"correlation_overlap_vs_registry":"pass vs 21 rasters (surface and final dots; see pcsup run card)","raster_sha256":"see evidence/a33_r7_pcsup_run_card_20261028.json","validator":"saved-byte pass; no NaN inside footprint; values in [0,1]; CRS/shape/transform match","submission_name":"gemsdoe33-a33-r7-pcsup-37654-20261028-d1f9cca0af02-zeros","verdict":"negative"}
```

**Next decisive step (new session, fresh preregistration):** rebuild the holdout at
deployment density (0.73%), re-baseline B1/CSHT/H19-5-reference at that density, and
only then test a new surface. Do not spend a slot on any current artifact.
Sources: DrivenData competition https://www.drivendata.org/competitions/306/ ,
reference solution https://github.com/drivendataorg/gems-prize-reference-solution ,
USGS GeoDAWN https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and ,
EPSG:32611 https://epsg.io/32611 , Tversky index https://en.wikipedia.org/wiki/Tversky_index
