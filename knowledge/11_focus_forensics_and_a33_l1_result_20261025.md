# Nine-repository focus forensics and A33-L1 result

**Date:** 2026-10-25
**Decision:** **A33-L1 is negative. The new TIFF is unique and format-valid, but it is NOT OK TO SUBMIT.**

## Evidence labels and hard boundary

- **OWNER/USER-REPORTED — NOT ORGANIZER-CONFIRMED:** every historical DTI value below. No authenticated DrivenData receipt tying a portal result to these exact bytes is retained in this checkout. Repository prose cannot upgrade itself into organizer confirmation.
- **HOLDOUT-DTI (`gems-segment-pooled-v1`, 60,988 withheld catalogue-positive pixels, spatial-block bootstrap 95% CI):** the new A33-L1 experiment only. This is a mapped-catalogue hide-and-recover proxy, not hidden organizer truth.
- **MEASURED-BYTES:** hashes, dot counts, set inclusion, correlations, distances and validator checks recomputed from the pinned GeoTIFF bytes.

The score claims are not training labels and are not presented as official scores. There was no leaderboard polling, portal upload or score projection in this run.

## Focus registry: what was actually reviewed

Each row is pinned by repository commit, path, Git blob and SHA-256 in `registry/focus_rasters_20261025.json`. Reproduction: restore with `scripts/cache_focus_registry.py`, then run `scripts/analyze_focus_registry.py`; complete pairwise results are in `evidence/focus_registry_analysis_20261025.json`.

| Repository artifact | Dots (MEASURED-BYTES) | DTI claim (OWNER/USER-REPORTED, not organizer-confirmed) | Byte-level finding |
|---|---:|---:|---|
| GEMSDOE24 H25-1 d1.5 | 60,069 | 0.2477 | 98.0% Jaccard with GEMSDOE27; exact subset of it |
| GEMSDOE25 d2.8 | 44,090 | 0.2600 | Pixel-identical to GEMSDOE30; parent of the 31→32 pruning ladder |
| GEMSDOE27 topo-gap | 61,328 | 0.2449 | Near-copy/superset of GEMSDOE24 (binary Spearman 0.9896) |
| GEMSDOE28 H36-1 | 37,660 | 0.2710 | Distinct exact set, but 95.5% of its dots fall within 3 px of GEMSDOE32 |
| GEMSDOE30 d2.8 | 44,090 | 0.2600 | Pixel-identical to GEMSDOE25 despite a different repository/name |
| GEMSDOE31 H27-4 solo | 40,199 | 0.2708 | Exact subset of d2.8; contains GEMSDOE32 B2 exactly |
| GEMSDOE32 H33-2-B2 | 37,654 | 0.2778 | Exact subset of GEMSDOE31 after a second catalogue-distance prune |
| GEMSDOE33 H33-D | 41,865 | 0.2632 | Strong family proximity; not an exact subset relation |
| GEMSDOE36 Anderson | 38,854 | 0.2750 | Contains all 37,654 B2 dots plus exactly 1,200 |

Important dependence findings:

1. GEMSDOE25 and GEMSDOE30 are exactly the same binary raster (Spearman 1.0000, Jaccard 1.0000).
2. GEMSDOE31 and GEMSDOE32 have Spearman 0.9676; B2 is an exact subset of solo.
3. GEMSDOE32 and GEMSDOE36 have Spearman 0.9843 and Jaccard 0.9691; B2 is an exact subset of Anderson.
4. GEMSDOE24 and GEMSDOE27 have Spearman 0.9896; H25-1 is an exact subset of topo-gap.

These are not nine independent confirmations. Several are deterministic edits of the same belief field.

## Why B2 may have produced the reported 0.2778

The most supportable explanation is **metric-aware subtraction from an already useful lineament field**, not discovery by a new detector.

### 1. The geometry is a controlled subtraction ladder

The pinned bytes establish:

- d2.8 (44,090) → solo (40,199): exactly 3,891 dots removed; every removed dot is exactly 1 pixel (100 m) from the mapped catalogue.
- solo (40,199) → B2 (37,654): exactly 2,545 dots removed; every removed dot is more than 1 and at most 2 pixels (100–200 m) from the mapped catalogue.
- B2 (37,654) → Anderson (38,854): Anderson retains every B2 dot and adds 1,200.

The associated reported claims rise 0.2600 → 0.2708 → 0.2778 as near-catalogue mass is removed, then fall to 0.2750 after 1,200 dots are added. **If those owner reports are accurate and byte-linked**, this is strong observational evidence that denominator thrift helped. It is not independent organizer authentication and does not prove every removed dot was geologically wrong.

### 2. The DTI objective rewards sparse, nonredundant placement

The pinned shared metric has `α=0.2`, `β=0.8`, and a 300 m triangular kernel. A zero-credit emitted dot increases false-positive cost; multiple dots near the same hidden truth can be redundant because truth credit uses nearest/best coverage. Under the idealized nonredundant binary increment and `α+β=1`, a new dot with hidden-truth kernel credit `k` improves a current DTI `d` only when `k > αd`. At the reported `d=0.2778`, the break-even credit is about `0.0556`.

Mapped faults themselves are excluded from scoring. A dot concentrated beside a mapped trace can therefore pay prediction-mass cost without finding an omitted segment. B2's 200 m exclusion removed such risky mass while preserving the inherited off-catalogue lineament geometry. The earlier d2.8 spacing also limits local redundancy. This is scientifically plausible because fault-zone mapping can be locally complete near known traces while concealed continuations, relay structures and parallel basin-bounding faults occur farther away.

### 3. The inherited field may contain real structure—but that mechanism is not isolated

The owner documents describe the parent H19-5 field as multiline/cross-physics corroboration. Potential-field and topographic discontinuities can follow concealed faults, and multi-layer agreement can reject single-sensor noise. However, lithologic contacts, basin-fill edges, acquisition boundaries and conductive alteration fronts can produce similar signatures. The nested artifacts do not isolate whether geologic corroboration, spacing, catalogue exclusion, or their interaction supplied the reported result.

### 4. Why the causal claim must stay modest

- Score/file pairing rests on owner reports, not a retained organizer receipt.
- The family is highly dependent, so the 31/32/36 ordering is not independent replication.
- The catalogue is not hidden truth; a proximity prune can also discard genuine subparallel strands.
- GEMSDOE32's own later review reports that a catalogue-hidden instrument ranked the B ladder backward when gates were derived from the full catalogue. That is exactly the leakage defect the A33 protocol prevents by rebuilding visible-fault features per fold.

Pinned prior-art review link: `https://github.com/buffedlizard55-lab/GEMSDOE32/blob/5fc7792c5887735ecd3aa9a612787da588a7bf2c/knowledge/03_why_02778_and_the_anatomy_of_the_family.md`.

## Is a higher result supportable now?

**No—not from this experiment.** A higher result may be possible in principle, but current evidence does not support claiming or spending a slot on one.

A33-L1 tested a genuinely different analog-transfer mechanism: 12 structural channels, per-field 257-knot source-to-target CDF alignment, equal source-field loss, and a frozen 0.80 regional / 0.20 adapted-analog rank fusion. Every catalogue-dependent training operation was rebuilt from fold-visible faults; whole connected fault components were withheld with a 15-pixel buffer; the same dot budget/operator was used for candidate and controls.

| Method | HOLDOUT-DTI (`gems-segment-pooled-v1`; 60,988 withheld positives; 95% CI) |
|---|---:|
| Raw pooled analog B0 | 0.087750 [0.079569, 0.095940] |
| Regional visible-fault expert B1 | **0.113244 [0.102796, 0.124169]** |
| A33-L1 field-balanced transfer | 0.108374 [0.097607, 0.119402] |
| Matched random | 0.071432 [0.068402, 0.074308] |

Against the best valid comparator B1, A33-L1's paired delta was **−0.004870**, spatial-block bootstrap 95% CI **[−0.010900, +0.001226]**, and it won **0/4 folds**. It improved substantially over the raw analog B0 (+0.020624, paired 95% CI [+0.013580, +0.027951], 4/4 folds), showing that target alignment and regional fusion repair some transfer error, but the analog contribution still dilutes the regional expert.

Thus:

- **Scientific verdict:** negative.
- **Slot verdict:** do not submit.
- **Projection verdict:** no competition-score projection is issued.
- **Next scientific implication:** portable local appearance was not the missing signal; a higher candidate needs independent off-catalogue truth or a detector that adds location-specific structural information rather than another member of the subtraction family.

At fixed mass and comparable denominator terms, moving from the reported 0.2778 to 0.30 would require roughly 8% more useful hidden-fault credit; this is algebraic scale context, **not a score prediction**. Extending the same B ladder is both scientifically uncertain and disallowed in this analog lane because it would fail the preregistered duplicate thresholds.

## Unique A33-L1 artifact and guards

The final 37,654-dot raster is genuinely different from all nine comparators:

- maximum pre-placement surface Spearman: **0.1084** (stop only if `>0.90`);
- maximum final binary Spearman: **0.02221** (stop only if `>0.90`);
- maximum fraction of candidate dots within 3 px of one registry raster: **42.25%** (stop only if `>70%`);
- versus GEMSDOE32 B2 specifically: Spearman **0.02203**, within-3-px fraction **37.07%**.

Its zero-outside TIFF is a one-band float32 raster on the exact template grid, EPSG:32611, values in `[0,1]`, with no NaN inside the footprint. Saved-byte SHA-256: `2bbbf7e381720f2242959e3efd6f2437f273afe6e7c48540d769524d2b4e8759`. Format validity does not override the negative scientific gate.

Full machine evidence: `evidence/a33_l1_experiment.json`, `evidence/a33_l1_run_card.json`, and `docs/downloads/receipt-gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34.json`.
