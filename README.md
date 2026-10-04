# GEMSDOE33 — GEMS Prize Challenge research & submission campaign

**Project status checked 2026-10-04 UTC; the latest authorized static leaderboard snapshot in this repository is dated 2026-10-03 (local).**
The goal is to beat the owner-reported campaign best of **0.2708** and pursue the official leaderboard
leader, listed as **0.3262** in that dated snapshot. These are different kinds of evidence: 0.2708 is
owner-reported from a prior manual submission; 0.3262 is a point-in-time public organizer leaderboard
observation, not the private prize-round score. The 0.2708 belongs specifically to GEMSDOE28's
`h27-4-r1-solo-d2-8`; its separate H36-1 and H38-1 experiments remain unscored and are not the source
of that result. Nothing in this repository has been submitted for a live
score. **No new candidate is currently cleared for a submission slot.** The earlier C2 proxy PASS was
withdrawn after the P1 audit found held-out-label and Qfaults-source leakage; see
[`evidence/holdout33.json`](evidence/holdout33.json) and the archived legacy report.

## ⬇ One-click GeoTIFF

| File | Description | Status |
|---|---|---|
| [`gems33-c2-stepover-relay-20261004-01f660dd8656.tif`](docs/downloads/gems33-c2-stepover-relay-20261004-01f660dd8656.tif) | C0 reference plus 940 stepover-relay bridge dots; SHA-256 `7272633447365d7ec8a9c07972b48df92b071a1ecc5765cf14199c14dea4f0f7` | **Research artifact only; earlier P1 PASS withdrawn; do not use a slot** |
| [`gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif`](docs/downloads/gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif) | Locally format-audited reference re-pack of the h27-4-r1-solo-d2-8 baseline | Owner-reported **0.2708**; reference only, not an organizer-authenticated score or a new candidate |

Both files pass the local format audit: one band, float32, EPSG:32611, 100 m, exact 3,730 × 3,292
sample-grid shape/transform/bounds, finite values in `[0,1]` over the whole array, and zero outside the
survey footprint. This is the project's conservative local policy, not organizer acceptance. The owner
reported a portal validation error for an earlier NaN-outside file; attributing that error to NaNs is an
inference, not an organizer support ruling. The C2 file is **not slot-cleared** after the P1 leakage audit;
its download is for research/reproduction, not an upload recommendation. The C0 file is a reference, not a
recommendation to resubmit the old baseline. See [the upload guide](docs/how-to-submit.html) for the
manual steps, official-rule constraints, and AI-disclosure draft. **This repo never logs in to or uploads
to DrivenData.**

The latest public leaderboard snapshot stored here (checked 2026-10-03 local) is #1 `nchuzhoy` 0.3262,
#2 `kinghorton42` 0.3222, #3 `DARD` 0.3195. It is dated evidence, not a live feed. The
[results page](docs/results.html) shows the snapshot and the organizer link. The official
[Terms of Use](https://www.drivendata.org/termsofuse/) prohibit automated monitoring and manual monitoring/
copying without prior written consent, so this repository cannot lawfully promise an automatically current
leaderboard feed under the terms reviewed here. Use only an authorized method if DrivenData provides one.

## Current candidate result and decision

**No candidate is cleared for a submission slot.** The first C1–C5 run reported a C2 numeric pass, but a
subsequent protocol audit found that its P1 test masked labels only at scoring time: the baseline's blind
catalogue-flank prune and C2's catalogue-distance filter still saw the full catalogue, while the Qfaults
source vectors still contained the held-out systems. That P1 result is withdrawn for promotion.

A corrected conditional diagnostic rebuilds the H27-4 base using only each fold's visible catalogue and
excludes entire Qfaults source IDs within a 600 m square buffer plus a 100 m raster guard. It gives:

- P1 fold deltas: **−0.000724, −0.001143, −0.000637, −0.000384**; mean **−0.000722**, **0/4** positive.
- Across the folds, C2 adds 2,643 candidate-only dots, gains **0 TPw**, and adds exactly 2,643 FPw.
- P2 SGMC off-catalogue delta: **+0.000283**. P2 is a separate compilation proxy, not organizer truth.
- Numeric P1/P2 gate: **FAIL**; slot status: **NO SLOT**.
- The strict diagnostic still uses the legacy H19-5 ridge raster as a fixed input. Its upstream generation
  code is absent, so it is not a fully independent confirmation even apart from the negative result.
- The format-audited C2 research raster has **41,139 dots**, 940 above the full-data reference, and the
  same SHA-256 listed above. A local format pass does not rescue the holdout failure.

The initial numeric report is preserved as
[`evidence/holdout33_legacy_catalogue_only.json`](evidence/holdout33_legacy_catalogue_only.json), marked
withdrawn. The corrected diagnostic is [`evidence/holdout33.json`](evidence/holdout33.json); the exact
C2 build is [`evidence/build_c2_01f660dd8656.json`](evidence/build_c2_01f660dd8656.json). The ranked
hypothesis register remains useful for research planning, but C2 must not be described as proxy-gated or
slot-ready. H33-A analog-field transfer remains a **plan**: official archives were listed but not obtained
in this workspace, and source data have not been geolocated, semantically aligned, or validated against the
target. GDR #1288 geothermal-feature/classification layers are not the GeoDAWN 19-band training raster or
fault labels. See the [executive summary](docs/executive-summary.html) and
[limitations/access register](knowledge/04_limitations_and_access.md).

## Quick start

Install the project dependencies, restore the hash-checked public inputs, and reproduce the C2
holdout/build. The downloader defaults to the candidate group; it does not use DrivenData.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
GEMS_DATA_DIR="$PWD/.cache/gemsdata" PYTHON=".venv/bin/python" bash scripts/download_competition_data.sh

# Fold-specific conditional diagnostic and C2 research-artifact rebuild
PYTHONPATH=src .venv/bin/python scripts/run_holdout33_source_audit.py --out evidence/holdout33.json
PYTHONPATH=src .venv/bin/python scripts/build_submission33.py --candidate C2

# Fast tests, static-ledger consistency, local links, and both deliverable format audits.
bash scripts/run_checks.sh
```

The build command generates a new uniquely named file from the current timestamp/content ID. Update all
published pointers and evidence from its build report before replacing the one-click asset. The checked-in
C2 filename above is the deterministic build used by the current ledger and site. A score-gated artifact
still requires manual owner review and upload; never consume a competition slot on a proxy-only claim.

## Results, methods, and evidence

- Executive summary and one-click download: [`docs/index.html`](docs/index.html)
- Executive research summary: [`docs/executive-summary.html`](docs/executive-summary.html)
- Manual upload steps plus a unique-name/short-note template for a future cleared candidate: [`docs/how-to-submit.html`](docs/how-to-submit.html)
- Static results feed, official snapshot, and live leaderboard link: [`docs/results.html`](docs/results.html),
  [`docs/score-feed.json`](docs/score-feed.json)
- Five ranked H33 hypotheses: [`registry/hypotheses.json`](registry/hypotheses.json),
  [`docs/hypotheses.html`](docs/hypotheses.html)
- Why the prior best scored 0.2708: [`knowledge/01_why_0.2708_won.md`](knowledge/01_why_0.2708_won.md)
- Corrected conditional P1/P2 diagnostic: [`evidence/holdout33.json`](evidence/holdout33.json); withdrawn legacy run: [`evidence/holdout33_legacy_catalogue_only.json`](evidence/holdout33_legacy_catalogue_only.json)
- Proxy results and leakage audit: [`knowledge/03_proxy_results.md`](knowledge/03_proxy_results.md)
- Sample/label irregularity: [`evidence/sample_template_label_overlap.json`](evidence/sample_template_label_overlap.json)
- Limitations, access needs, and decision gates: [`knowledge/04_limitations_and_access.md`](knowledge/04_limitations_and_access.md)
- Verified data sources: [`knowledge/05_data_sources_verified.md`](knowledge/05_data_sources_verified.md),
  [`docs/data-sources.html`](docs/data-sources.html)
- Three-pass acceptance review: [`knowledge/06_three_pass_review.md`](knowledge/06_three_pass_review.md)
- Cross-campaign score source: [`registry/score_ledger.json`](registry/score_ledger.json)

Rows with no score remain explicitly unscored. Public GitHub API lookups for the repositories named
`31GEMSDOE` and `32GEMSDOE` returned 404 to the configured public account; that does **not** establish
whether either repository is private, uncreated, or hosted elsewhere. The original request supplied no
submission name, URL, or score for those headings, so the feed records only that missing information.

## Restored data and provenance

`registry/data_manifest.json` pins the core training raster, labels, and sample-grid template, plus the
candidate inputs (including H27-4 and the Quaternary-fault shapefile components). H27-4 comes from an
owner-maintained public mirror; its hash pins the bytes but does not make the score organizer-authenticated.
The Quaternary-fault files are from a pinned community mirror of GDR #1391; those hashes likewise pin the
fetched bytes, not an organizer certification. GDR #1391 lists Quaternary Faults v1 and a newer v2 that
supersedes v1; this mirror's exact version correspondence has not been verified. A local HEAD request for
the official v2 ZIP failed TLS, so C2's passing proxy result applies only to the currently pinned mirror.
`scripts/restore_data.py` supports `core` and `candidate` groups; the optional unpinned research archive
is excluded from the default candidate restore.

The cached inputs live under `.cache/gemsdata/` and may need to be restored after a clean checkout. The
candidate downloader verifies SHA-256 and the core grid before a build. The GDR data listing is evidence
that the source exposes specific downloadable layers, not evidence that those layers are equivalent to
GeoDAWN labels or its 19 training bands.

## Standing brief (original user prompt, retained verbatim)

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

> **Status note:** the original prompt's 0.3195 leaderboard value is preserved above as part of the brief;
> it is now rank 3 in the 2026-10-03 official snapshot. The current leader is 0.3262; see the dated
> [results page](docs/results.html). H33-A analog transfer has not been executed and is explicitly subject to
> feature compatibility, geographic alignment, provenance checks, and holdout validation.

### Session-status pointer

* Answer to “why did 0.2708 win” → [`knowledge/01_why_0.2708_won.md`](knowledge/01_why_0.2708_won.md)
* Five ranked new hypotheses → [`registry/hypotheses.json`](registry/hypotheses.json) and [`knowledge/02_hypotheses_H33.md`](knowledge/02_hypotheses_H33.md)
* Current proxy validation → [`evidence/holdout33.json`](evidence/holdout33.json), [`knowledge/03_proxy_results.md`](knowledge/03_proxy_results.md)
* Limitations and access needs → [`knowledge/04_limitations_and_access.md`](knowledge/04_limitations_and_access.md)
* Verified sources → [`knowledge/05_data_sources_verified.md`](knowledge/05_data_sources_verified.md)
* Score ledger → [`registry/score_ledger.json`](registry/score_ledger.json)

### No-automation / submission policy

Code and CI may fetch only public repository data sources listed in the manifest. No code may log into,
upload to, scrape, or poll DrivenData. The official [Terms of Use](https://www.drivendata.org/termsofuse/)
reviewed 2026-10-04 prohibit automated monitoring and manual monitoring/copying without prior written
consent; the leaderboard remains a static, dated snapshot unless an authorized API or permission becomes
available. The human owner is responsible for authorized portal actions. The rules allow up to three
submissions per week but require one final selection across both prize phases. No candidate is currently
cleared for a slot. Generative-AI use must be disclosed in the final submission narrative; a draft is in the
upload guide and requires owner review.

### Known irregularities (flagged for review)

| ID | Finding |
|---|---|
| IR-PORTAL-01 | Owner observed “Predicted values must be in range [0, 1]” while using an earlier NaN-outside file. NaNs are a plausible cause, not an organizer-confirmed diagnosis. The project's current policy is finite `[0,1]` across the array and zero outside the footprint. |
| IR-HOLDOUT-LEAKAGE-01 | The initial P1 proxy run generated/scored candidates with the full catalogue and used Qfaults source geometries for hidden systems. Its apparent C2 PASS is withdrawn. Fold-specific source exclusion changes P1 mean ΔDTI to −0.000722 (0/4 positive); P2 remains +0.000283. No slot is cleared. |
| IR-SAMPLE-LABEL-01 | The restored sample template exactly equals `labels.tif` on all 5,167,373 finite-footprint cells (60,988 ones; 5,106,385 zeros). Code uses only its finite footprint/grid metadata, never its values as truth. See `evidence/sample_template_label_overlap.json`. |
| IR-QFAULTS-01 | GEMSDOE24 mirror `qfaults_v2_in_footprint.json` geometry is in a non-invertible shifted coordinate frame; candidate construction uses the separately pinned INGENIOUS shapefile mirror instead. |
| IR-QFAULTS-02 | GDR #1391 lists Quaternary Faults v2 as superseding v1; the pinned community mirror's exact version is not confirmed. A direct local request for the official v2 ZIP failed TLS. C2's evidence applies only to the mirror as pinned; re-audit before swapping inputs. |
| IR-EVIDENCE-01 | GEMSDOE29's radiometric experiment record (seeds 280–289) could not be retrieved through the available public GitHub API lookup; H33-D is marked partially pre-empted until reconciled. |
| IR-NET-01 | Official GDR/NBMG/USGS file downloads were not restored for analog transfer; direct workspace requests for GDR #207 `GIS_Faults.zip` and the GDR #1391 Quaternary Faults v2 ZIP failed connection/TLS setup. Source-listing availability is not local data readiness. Do not run H33-A until location, labels, common features, and license/provenance are audited. |
| IR-REPO-31-32 | Public GitHub API lookups of repositories named `31GEMSDOE` and `32GEMSDOE` returned 404. They may be private, uncreated, or elsewhere; no URL/name/score was supplied. |
