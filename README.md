# GEMSDOE33 — DOE GEMS fault-discovery research

**Current decision (2026-10-25): negative / no competition submission approved.** The available top-ranked H33-6 experiment did not pass its conditional spatial holdout, its final raster triggered the repository's duplicate guard against several local reference artifacts, its pre-placement surface screen was not run in this checkout, and comparable rasters from all cited GEMSDOE sites were not present for a complete registry check. Do not upload an existing GEMSDOE33 candidate or spend a competition slot.

The complete project mandate and protocol are preserved in [`standing_prompt.md`](standing_prompt.md). Read that file at the start of each project session. Core operating values: **Maximize P(Win)** by choosing evidence over optimism, and **Own the Outcome** by recording negative results, correcting unsupported claims, and following through on validation.

## Executive summary

- **Research TIFF (downloadable, but not for submission):** [`GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif`](docs/downloads/research/GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif). The landing page says prominently that it is **NOT approved for competition upload**. A unique artifact is not automatically a valid or competitive submission.
- **Artifact name:** `GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7`
- **Paste-ready note (110 characters):** `H33-6 edge-normal research artifact; holdout gate failed; not approved for competition upload. id 6c888d2ce0f7`
- **SHA-256:** `18604d71f11db269a3f70007433d1dd74e4f09eb195861dc2aeda4d98aa8efe7`
- **Local saved-byte audit:** one-band float32; EPSG:32611; 3730×3292; 100 m; recorded grid match; finite in-footprint values in [0,1], NaN outside. Whole-array all-finite check **fails** because outside-footprint cells are NaN. Portal acceptance is untested. Do not infer the cause of the earlier reported `[0,1]` portal error without an organizer diagnostic.
- **HOLDOUT-DTI:** local `dti_binary` evaluator in [`src/gemsdoe33/metric.py`](src/gemsdoe33/metric.py), source SHA-256 recorded in [`evidence/duplicate_guard_run_card_20261025.json`](evidence/duplicate_guard_run_card_20261025.json); no semantic evaluator-version identifier was preserved. H33-6 mean delta **−0.00273732 DTI** over four spatial folds and 60,988 aggregate withheld catalogue pixels; 2/4 fold deltas positive. Descriptive 95% fold-t interval: **[−0.015020, +0.009546] DTI**, based on four folds (df=3); very imprecise and conditional, not uncertainty against private expert truth. The fixed H19-5 surface was not regenerated per fold.
- **HOLDOUT-DTI:** P2 SGMC off-catalogue proxy delta **+0.00015900 DTI**; this is not a competition score. No candidate is slot-cleared.
- **Duplicate guard:** 7/9 comparison rasters already in this checkout crossed at least one configured threshold (Spearman rho >0.90 or >70% of candidate dots within 3 px). External GEMSDOE site rasters were not staged, so full cross-site uniqueness is unknown. This is a stop condition, not a claim that every site is an exact duplicate.
- **No new TIFF was generated in this review.** The retained artifact was already present; guard checks and validation failed to establish that a fresh, unique, slot-worthy candidate could be safely generated. See the JSON run card for the measured comparisons, limits, and decision.

## What can be said about reported scores?

The brief reports `0.2778` for `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, along with earlier values such as `0.2600`, `0.2708`, `0.2708`/`0.2710`, and the aspirational `0.3195`. These are **user/owner-reported values**, not organizer-confirmed score/file receipts in this checkout. The retained GEMSDOE28 owner-page review reportedly labels H27-4 unscored/research-only. Accordingly, this repository cannot truthfully explain why H27-4 “scored 0.2708” as an established fact, cannot link the reported `0.2778` to authenticated raster bytes, and cannot claim that a new candidate beats it or the stated `0.3195` target.

A cautious scientific interpretation is that high DTI generally rewards predictions placed close to hidden fault pixels under the competition's distance-tolerant metric, with the density/placement tradeoff mattering. The repository implementation and formulas are in [`src/gemsdoe33/metric.py`](src/gemsdoe33/metric.py). A filename suffix such as `zeros` describes an encoding choice; without a controlled matched-byte experiment and organizer receipt it does not explain a score. No projection is a score.

## Ranked hypotheses and next experiment

The frozen 2026-10-04 slate contains five ranked hypotheses with named layers, physical signatures, prior-art differences, qualitative upside/cost, and external source availability checks: [`knowledge/07_hypothesis_slate_20261004.md`](knowledge/07_hypothesis_slate_20261004.md). The top runnable candidate, **H33-6**, combines aligned TMI/gravity edge normals with basement-depth/conductivity edge corroboration and matched-budget relocation. The experiment was run before this review; it failed its predeclared gate. Its held-out metric is conditional because the H19-5 source surface is fixed and its upstream code is missing. The leakage canary for each individual feature is not present in retained evidence. Do not tune against the completed holdout.

Remaining concepts include BRIDGE field-pick transfer and Gabbs Valley 3D fault surfaces, both blocked until official source bytes, schema, CRS, license, coverage and actual feature overlap can be audited. The source listing is not proof of usable data. Use the pre-registered slate and the explicit limitations; do not present these as validated candidates.

## Competition upload instructions

The [`executive summary`](docs/executive-summary.html) contains the safe upload workflow and official links. **There is currently no approved TIFF to submit.** For any later candidate, first pass the spatial holdout, leakage canaries, duplicate/overlap screen, saved-byte GeoTIFF audit, and current competition rules; then use the account holder's authenticated DrivenData browser session. This workspace has no DrivenData authentication and cannot submit or retrieve a receipt. Save the organizer receipt before calling any score organizer-confirmed.

## Build and test

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHON=.venv/bin/python bash scripts/run_checks.sh
```

The project check script rebuilds the static pages, runs the test suite, compiles Python sources, and checks the diff. Data restoration is separate and may require authenticated competition files; see [`data/README.md`](data/README.md). No check here implies scientific validity, portal acceptance, or competition performance.

## Reviewable sources

- [Official DrivenData competition problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (login may be required)
- [Official competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR BRIDGE #1682](https://gdr.openei.org/submissions/1682) — listed source; archive not locally audited
- [USGS Gabbs Valley ScienceBase item](https://www.sciencebase.gov/catalog/item/62b21845d34e74f0d80f17aa?format=json) — metadata/source listing; payload not locally audited
- [EPSG:32611](https://epsg.io/32611)

Source claims, attribution, limitations, irregularities, and provenance are itemized in [`registry/sources.json`](registry/sources.json), [`registry/irregularities.json`](registry/irregularities.json), [`knowledge/09_20261025_review.md`](knowledge/09_20261025_review.md), and the machine-readable run card. The retired H33-D candidate and domain-transfer runners now fail closed; their archived artifacts are not upload recommendations. Historical score records are not a current leaderboard feed.
