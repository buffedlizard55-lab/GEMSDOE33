# GEMSDOE33 — GEMS Prize Challenge: bounded analog-field transfer & stepover relay discovery

**Goal: beat the owner-reported 0.2708 campaign best and reach for the 0.3195 public leader on
[DrivenData #306 — The Geologic Enhanced Mapping System (GEMS) Prize Challenge](https://www.drivendata.org/competitions/306/competition-doe-gems/).**

## ⬇ One-click submission (portal-safe, format-audited)

| File | What it is | Status |
|---|---|---|
| [`docs/downloads/gems33-c2-stepover-relay-20261004-eb6bcf02361f.tif`](docs/downloads/gems33-c2-stepover-relay-20261004-eb6bcf02361f.tif) | Scored h27-4 base (0.2708) + 944 stepover relay-bridge dots that passed the frozen P1/P2 proxy gate | proxy-gated, **unscored** |
| [`docs/downloads/gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif`](docs/downloads/gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif) | Portal-safe re-pack of the 0.2708-scored h27-4-r1-solo raster | owner-reported **0.2708** |

Both files are single-band float32, EPSG:32611, 100 m, identical shape/geotransform/bounds to the
official sample submission, and **finite [0, 1] over the whole array** (zero outside the survey
footprint) — the exact portal rule that rejected earlier NaN-outside files with
"Predicted values must be in range [0, 1]" (irregularity IR-PORTAL-01, fixed).
See [docs/index.html](docs/index.html) (deployed as GitHub Pages) for the executive summary,
the how-to-submit guide, hypothesis ranking, and verified data-source tables.

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
bash scripts/download_competition_data.sh     # restores hash-pinned public mirrors (never contacts DrivenData)
PYTHONPATH=src .venv/bin/python tests/test_metric.py                     # metric unit tests
PYTHONPATH=src .venv/bin/python scripts/run_holdout33.py --candidates C1,C2,C3,C4,C5 --out evidence/holdout33.json
PYTHONPATH=src .venv/bin/python scripts/build_submission33.py --candidate C2
PYTHONPATH=src .venv/bin/python scripts/validate_submission.py --submission docs/downloads/<file>.tif
```

---

## Standing brief (the prompt this repo is built against)

> Review the repo.
>
> There should be an easy to download submission tif file as described by the prompt. Read the entire prompt.
>
> **Borrow ground truth from a better-mapped analog field, with the transfer itself bounded.** GeoDAWN isn't
> the only Great Basin geothermal terrain — nearby fields with decades of industry exploration drilling
> (Dixie Valley, Desert Peak, Brady's) have far denser, field-verified fault mapping, because economic stakes
> justified fieldwork a regional USGS/INGENIOUS compilation never got. Ben-David, Blitzer, Crammer, Kulesza,
> Pereira, and Vaughan's domain adaptation theory (Machine Learning, 2010) gives the formal machinery for
> using this responsibly: it bounds a model's target-domain error by its source-domain error plus a measurable
> divergence between the two domains' feature distributions — the same kind of divergence the
> classifier-two-sample-test confound audit elsewhere in this program already computes. Pretrain or co-train
> on the analog field's denser catalogue, measure that source-target divergence on shared feature layers
> before trusting any transfer, and where it's small, treat the analog field's known fault geometries as a
> genuinely independent validation set — one whose locations were never touched by GeoDAWN's own incomplete
> catalogue to begin with.
>
> WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF
> IS DOWNLOADED FROM WHICH IS THE FOLLOWING: https://buffedlizard55-lab.github.io/GEMSDOE28/
> **h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan: 0.2708.** Why and how did this get the highest score and
> are we able to generate a submission that scores higher than 0.2708? Answer the question using PhD level
> experience, knowledge, and judgement. Current public leaderboard best: **0.3195** — design a new strategy,
> research, testing, analyzing, and generating submission system that can score higher.
>
> Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the
> specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature
> transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already
> in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI
> improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before
> touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the
> current holdout best. If a candidate can't be validated without new external data, name the specific free,
> official source needed and check it's obtainable before proposing the idea as viable.
>
> Work line by line verifying from official verified trusted sources, provide links for manual review. There
> should be no manual input, work on your own to complete tasks. Flag any irregularities for review.
> No hallucinations.
>
> The site should be able to generate a TIF file that is required for submission. It should be as easy as
> download to click a File to submit into the competition. This needs to be in the executive summary or the
> very beginning of the site. It should be obvious when you visit the site. Give submissions a unique name and
> a short comment to tell them apart later. Create an executive summary subpage that explains exactly how to
> make a submission into the contest.
>
> Our Core Values — **Maximize P(Win)**: in every decision, weigh tradeoffs, assess risk, and choose the path
> that maximizes the probability of winning. **Own the Outcome**: own results end to end — not just an
> individual slice of the work; treat failure and success as signals and use them to improve.
>
> The goal of this project is to place top of the leaderboard in this competition. Get familiar with the
> problem through the overview and problem description, download the data, create and train your own model,
> use your model to generate predictions that match the submission format. Find free publicly available
> sources and data from official and verified sources for any 3rd party or external data.

### Session-status pointer

* Answer to "why did 0.2708 win" → [`knowledge/01_why_0.2708_won.md`](knowledge/01_why_0.2708_won.md)
* The 5 ranked new hypotheses → [`registry/hypotheses.json`](registry/hypotheses.json) and [`knowledge/02_hypotheses_H33.md`](knowledge/02_hypotheses_H33.md)
* This session's proxy validation (C2 passes, C3 refuted) → [`evidence/holdout33.json`](evidence/holdout33.json), [`knowledge/03_proxy_results.md`](knowledge/03_proxy_results.md)
* Limitations & access needs → [`knowledge/04_limitations_and_access.md`](knowledge/04_limitations_and_access.md)
* Verified official data-source table → [`knowledge/05_data_sources_verified.md`](knowledge/05_data_sources_verified.md)
* Score ledger across all campaign sites → [`registry/score_ledger.json`](registry/score_ledger.json)

### Known irregularities (flagged for review)

| ID | Finding |
|---|---|
| IR-PORTAL-01 | Upload form validates the whole array against [0,1] and rejects NaN; all session outputs are zero-outside instead of NaN-outside |
| IR-QFAULTS-01 | GEMSDOE24 mirror `qfaults_v2_in_footprint.json` geometry is in a non-invertible shifted coordinate frame; replaced by the authoritative INGENIOUS shapefile (NAD83, validated) |
| IR-EVIDENCE-01 | GEMSDOE29's GeoDAWN-radiometric experiment record (seeds 280–289) could not be retrieved via the GitHub API this session; H33-D is marked partially pre-empted until reconciled |
| IR-NET-01 | This sandbox has egress only to github.com/api.github.com/codeload.github.com; USGS/GDR/Dropbox/DrivenData bytes require an unrestricted machine |
