# GEMSDOE33 — DOE GEMS Fault Discovery Project (DrivenData #306)

> **Current decision (2026-10-25): no candidate is submission-cleared. Existing downloadable TIFFs are research/reference artifacts, not “OK to submit.”** Read §3 before using any file.

## Active-session outcome and starting point (2026-10-25 continuation)

Read this README **and the complete consolidated [standing prompt](standing_prompt.md)** every session. The current parallel protocol, nine-site focus, score-provenance requirements, 3-experiment/2-hour cap, unique-TIFF requirement, automatic inspection requirement, values, and PR/merge request are preserved in its active-request addendum. It is a consolidated specification, not a verbatim transcript of repeated chat text.

**New work:** all 17 pinned owner-mirror inputs restored and audited; 121 cached feature channels prepared (no detector retraining). Twelve historical rasters across all nine focus sites were byte-pinned and compared in 132 ordered pairs. GEMSDOE32 B2 was reproduced **pixel-exactly as deletion-only pruning** of the GEMSDOE28 H27-4 reference: 40,199 → 37,654 dots, 2,545 deleted and none added. This is prior-art forensics, not a new prediction or an official score. Against H27-4, B2 has Spearman 0.967587 and 100% candidate-dot overlap within 3 px, so copying this strategy would violate the lane duplicate gate.

**Still NOT OK TO SUBMIT:** no new unique competition TIFF was generated. The request omits an explicit new method-lane paragraph/canonical template identity; the standing analog-transfer lane lacks independent official analog fault labels. Four new within-lane planning hypotheses are ranked but explicitly blocked, not claimed viable. Zero new experiments, zero slots, zero uploads. Existing failed arms were not rerun or retuned. This is an explicit incomplete scientific deliverable, not a claimed completion of the unique-submission goal.

- [Current forensic review, scientific reasoning and next steps](knowledge/10_focus_review_20261025.md)
- [Pinned twelve-raster registry](registry/focus_rasters_20261025.json) / [measured forensic audit](evidence/focus_raster_audit_20261025.json)
- [Four conditional analog hypotheses](registry/analog_hypotheses_20261025.json)
- [Automatic promotion evidence gate](scripts/check_promotion.py): checks all required evidence; never selects/uploads a slot. It is not a replacement evaluator or proof of arbitrary JSON's scientific validity.
- [Current negative run card](evidence/run_card_focus_20261025.json) / [current gate decision](evidence/promotion_gate_20261025.json)

Reproduce locally (large arrays stay ignored; these commands never contact DrivenData):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/restore_data.py --group all
.venv/bin/python scripts/audit_inputs.py
.venv/bin/python scripts/prepare_data.py --skip-detector
.venv/bin/python scripts/audit_focus_rasters.py --fetch
.venv/bin/python scripts/check_promotion.py --evidence evidence/promotion_input_20261025.json --out evidence/promotion_gate_20261025.json
# Expected exit 2 above: blocked/negative, NOT an execution failure.
PYTHON=.venv/bin/python bash scripts/run_checks.sh
```

The ignored caches are local working state and may not survive workspace snapshots; restore/prepare commands and integrity receipts support rebuilding, not a guarantee of permanent array storage.

The project writer now rejects invalid values rather than clipping, rejects infinity outside, accepts aligned full-shape predictions, and enforces notes <=140 characters. The validator CLI defaults to the actual restored `data/sample_submission.tif`. Existing NaN and zero research files were independently reopened and validated against that template; a format pass is not promotion. The official reference explicitly supports CPU: a GPU is not the only remaining blocker. Current leaderboard, weekly cap, official data provenance/rules and score receipts are still unverified; restricted outbound hosts prevent fetching GDR/USGS binary archives here.

## §1. Standing Brief & Master Project Directive

> **Operational Directive (Mandatory Starting Point for Every Session):**
>
> Review the repo.
>
> MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION.
>
> There should be an easy to download submission tif file as described by the prompt. Read the entire prompt.
>
> Borrow ground truth from a better-mapped analog field, with the transfer itself bounded. GeoDAWN isn't the only Great Basin geothermal terrain — nearby fields with decades of industry exploration drilling (Dixie Valley, Desert Peak, Brady's) have far denser, field-verified fault mapping, because economic stakes justified fieldwork a regional USGS/INGENIOUS compilation never got. Ben-David, Blitzer, Crammer, Kulesza, Pereira, and Vaughan's domain adaptation theory (Machine Learning, 2010) gives the formal machinery for using this responsibly: it bounds a model's target-domain error by its source-domain error plus a measurable divergence between the two domains' feature distributions — the same kind of divergence the classifier-two-sample-test confound audit elsewhere in this program already computes. Pretrain or co-train on the analog field's denser catalogue, measure that source-target divergence on shared feature layers before trusting any transfer, and where it's small, treat the analog field's known fault geometries as a genuinely independent validation set — one whose locations were never touched by GeoDAWN's own incomplete catalogue to begin with.
>
> WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
> https://buffedlizard55-lab.github.io/GEMSDOE28/
> h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan: 0.2708
> Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2708?
> Answer the question using Phd level experience, knowledge, and judgement.
>
> The following is the leaderboard for the competition:
> https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
>
> 0.3195 is the highest score right now so we need to design a new strategy, research, testing, analyzing, and generating submission system than the current website. It should be unique, take unique approaches to generating a submission that can score higher than 0.3195.
>
> Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted, why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot.
>
> The site should be able to generate a TIF file that is required for submission. It should be as easy as download to click a File to submit into the competition. This needs to be in the executive summary or the very beginning of the site. it should be obvious when you visit the site.
>
> I tried to submit the document that i downloaded from the site but it returned this error on the submission form: "Predicted values must be in range [0, 1]"
> Also we need to give it a unique name and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25
>
> Create a executive summary subpage that explains exactly how to make a submission into the contest.
>
> Work line by line verifying from official verified trusted sources, provide links for manual review. There should be no manual input, work on your own to complete tasks. Flag any irregularities for review. No hallucinations. Verify no hallucinations.

---

## §2. Our Core Operating Values

### Maximize P(Win)
> **“Maximize the Probability of Winning”**: our decision-making framework. In every decision, we weigh tradeoffs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside our emotions and make tough decisions in order to maximize P(Win). “Maximize P(Win)” frees us from constraints and clarifies that we must put Arena first.

### Own the Outcome
> **We own results end to end** — not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

---

## §3. Submission status — READ BEFORE DOWNLOADING

> **No current TIFF is cleared for competition upload.** Do not upload either the historical reference or the H33 experimental raster based on this repository's evidence. The H33-6 preregistered diagnostic did not beat its local baseline (mean catalogue-proxy ΔDTI −0.00273732; positive in 2/4 folds); it is conditional because its H19-5 source was not re-derived per fold. Its local artifact is research-only. No organizer receipt or score/file association is present. A valid-format TIFF is not proof of scientific improvement or portal acceptance.

The repository contains historical TIFFs in `docs/downloads/`, including H33-D and D2.8. Their old text below may overstate validation, score pairing, or upload suitability; treat these files as **archived research/reference artifacts only**, not recommended submissions. The H33-D claims of transfer-bound validation, projected score, “beats” status, and range-error root cause are not supported by the current evidence and are withdrawn. See [`knowledge/08_h33_6_result_20261004.md`](knowledge/08_h33_6_result_20261004.md), [`evidence/first_pass_disposition.json`](evidence/first_pass_disposition.json), and [`docs/irregularities.html`](docs/irregularities.html).

A candidate may be called submission-ready only after a fresh independent, fold-safe evaluation beats a comparable baseline, passes the written leakage/duplicate gates, is validated on the exact competition grid with official nodata semantics, and the evidence is reviewed. Organizer acceptance still requires an actual portal receipt. The project does not have DrivenData account access and must not upload or scrape.

## §4. Historical Reference Baseline (For Comparison & Education)

> **Not cleared for upload. Historical reference only.** This is an owner-mirror reference emission from GEMSDOE28, not a new model or a demonstrated leaderboard improvement. The source is an owner-published mirror. Its claimed `0.2600` score is owner-reported; no organizer receipt ties that score to these exact bytes.

| | Recommended — follows the null/NaN-outside wording | Troubleshooting alternative |
|---|---|---|
| Historical artifact (do not submit) | [NaN-outside TIFF](docs/downloads/gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif) | [Zero-outside TIFF](docs/downloads/gemsdoe33-d28-reference-20261004-426073b6b4ab-zeros.tif) |
| SHA-256 | `c5e07fad5672879562ea43805cf71c7ba7512fd1a37ca460de83971bc6d8abdc` | `29ca0bc2cf249f96f1504b8c0ec5e775e78668f6d0f54f5c1c33c580cce74f73` |
| Bytes | 499,842 | 423,456 |
| Outside footprint | NaN | `0.0` (troubleshooting alternative) |
| Local file checks | 10/10 passed | 10/10 passed |

**Historical identifier (not an approved submission name):** `gemsdoe33-d28-reference-20261004`
**Paste-ready note (158/200 characters):**
> `GEMSDOE33 D2.8 reference | owner-mirror emission; 0.2600 is owner-reported, score/file pairing unconfirmed | format-checked, not a new model | id 426073b6b4ab`

See the [executive summary](docs/executive-summary.html) for gates and general upload procedure. This historical artifact is not recommended for upload. No submission was uploaded from this session.

---

## §5. Historical metric analysis — not a verified explanation of score 0.2708

The following historical discussion and calculations have not been independently revalidated against organizer truth or a score-linked submission file. In particular, the owner-published GEMSDOE28 page is reported in the repository to label H27-4 unscored/research-only; the user's reported `0.2708` and `0.3195` are not organizer-confirmed in this checkout. No claim that GEMSDOE33 beats either value is justified. The full DTI definitions and old reasoning below are retained as historical notes only; they are not validation, a projected score, or permission to upload.

## §6. Research record and current candidate slate

The five hypotheses and their layers, mechanisms, prior-art distinctions, costs, and source availability checks are recorded in [`knowledge/07_hypothesis_slate_20261004.md`](knowledge/07_hypothesis_slate_20261004.md) and the frozen machine-readable record [`evidence/hypothesis_slate_20261004_preregistered.json`](evidence/hypothesis_slate_20261004_preregistered.json). The selected runnable H33-6 experiment is complete and **failed its numeric gate**; do not rerun/retune it to seek a better result. After summing the retained TPw/FPw/FNw over all folds, pooled HOLDOUT-DTI is 0.112486 for H33-6 and 0.114669 for the control (pooled ΔDTI −0.002183). The unweighted mean of the fold deltas is −0.00273732, 2/4 folds positive. A later review calculated a descriptive 95% Student-t interval across the four fold deltas, [−0.015020, +0.009546], df=3; it is small-n and conditional, not an interval for the pooled statistic, nor a private-label or competition-score confidence interval. This is conditional catalogue-proxy evidence, not private expert truth or a competition score. The official BRIDGE/USGS analog-data candidates remain blocked on obtaining and auditing the actual payload bytes. See [`knowledge/08_h33_6_result_20261004.md`](knowledge/08_h33_6_result_20261004.md) and the current run card.

## §7. Review of reported campaign scores

The score/method list in the prompt is **user-provided context, not independently verified evidence**. It indicates a rising owner-reported sequence among the examples: H25 dotted-ridge (0.2477), D2.8 (0.2600), H27-4 (0.2708), H36-1 (0.2710), H33-2 B2 (0.2778), and a separately supplied leaderboard high (0.3195). None of these values alone establishes why an artifact scored well, its exact bytes, whether the score is official, or whether the experiment is comparable; repository evidence says H27-4 lacks an organizer-verified score/file pairing. **Do not claim H33-2 zeros is the reason for 0.2778 or infer a reproducible mechanism without its TIFF, code, validation details, and organizer receipt.** The most plausible general explanation for the incremental H25→D2.8→H27-4 progression is sparse, spatially regular emission plus pruning near known-catalogue mid-segment flanks, but this is a hypothesis based on owner-mirror campaign descriptions—not causal proof. The distinct H33-6 edge-consensus intervention did not improve the local proxy control, so there is no validated basis to claim this repo can exceed 0.2778 or 0.3195.

The supplied list also names high-ranking contenders in GEMSDOE24/25/27/28/30/31/32/33/36, but sites use owner-published material. Scores and labels are treated only as the user's supplied historical claims unless an organizer receipt and byte-identifiable artifact are archived. Terms and leaderboard restrictions prohibit building a live scraper/refresh feed without authorization; current process follows [`AGENTS.md`](AGENTS.md). The official competition reference solution and rules are linked below for manual review.

## §8. Download and upload instructions

There is **no current approved submission download**. Old files in `docs/downloads/` are historical/reference or failed research outputs. A `format_check` pass does not satisfy the scientific holdout gate or establish organizer acceptance. Do not upload any old artifact as a candidate from this README. When a future candidate passes the promotion gate, the website's executive-summary page will provide its exact file, unique name/comment, grid validation, hash, and appropriate upload steps; only then should the owner upload via the official competition page. This workspace cannot access a DrivenData account or create an organizer receipt.

## §9. Trusted-source review links

- [DrivenData competition overview/rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData reference solution (GitHub)](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GBCGE INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)
- [US DOE GEMS technical report](https://docs.nrel.gov/docs/fy26osti/96647.pdf) (the provided DOE-host variant is retained as a user-supplied link; verify current availability and requirements on the competition page)
- [Ben-David et al. 2010, domain adaptation](https://doi.org/10.1007/s10994-009-5152-4) — theoretical bounds require their assumptions and terms; an arbitrary domain-classifier AUC is not a transfer guarantee.
- [Official competition submission instructions](https://www.drivendata.org/competitions/306/competition-doe-gems/)

The official competition data download requires an authenticated account. This runtime has no DrivenData authentication; the source-page redirect/login was previously recorded. Owner mirrors are not proof of official data provenance; consult [`registry/sources.json`](registry/sources.json), [`registry/owner_mirror_input_pins.json`](registry/owner_mirror_input_pins.json), and [`data/README.md`](data/README.md). Do not state data placement is complete: `data/core/` is not present here.

## §10. Limitations and next work

1. Recover competition inputs through an authorized official source/account, verify provenance and exact grid/nodata semantics; do not treat the sample raster's positive cells as truth (it overlaps labels).
2. Any fresh experiment must first declare its single lane, build leakage-safe whole-segment buffered folds with fold-specific feature derivation, report every feature's standalone leakage-canary AUC, and compute pooled DTI with a defined 95% interval. Explicitly check rank correlation and dot proximity against registry rasters before placement and on final output; stop and log duplicates at the stated thresholds.
3. Use the shared holdout/evaluator and writer, not private methods. Do not proceed if those required shared utilities/data are absent or known to leak. New candidate must beat a comparable current holdout baseline on independent confirmation before it can be considered for a slot. No score projection substitutes for this gate.
4. Verify candidate against official schema and exact template, including no NaN inside footprint, `[0,1]` values, CRS/shape/transform, and outside-footprint semantics. Separate artifact reproducibility from organizer acceptance.
5. The requested exact lane paragraph, access to the cited competition account, organizer score receipts, and hidden expert truth are unavailable. The retrospective four-fold interval is descriptive only. These are explicit blockers; no higher-scoring TIF can responsibly be claimed here.

Full session brief and recurring operating rules: [`standing_prompt.md`](standing_prompt.md). Core values: **Maximize P(Win)** and **Own the Outcome**—including the obligation to stop promoting a failed or unsupported candidate. See [`registry/irregularities.json`](registry/irregularities.json) for recorded issues.

## §11. 2026-10-25 duplicate guard and saved-byte review

The current work branch revisited the existing H33-6 artifact, without rebuilding it or running a new geological experiment. The protocol's exact “single method paragraph” is not explicitly identified in the prompt; no new lane was assumed. Seven of nine same-grid local TIFFs triggered at least one final-dot duplicate threshold (rho >0.90 or >70% within 3 pixels). This is only the local checkout subset; external GEMSDOE registry TIFFs are unavailable here. The pre-placement surface could not be tested because the source feature cache is absent. The duplicate guard is therefore a stop, not proof of cross-site uniqueness.

Saved-byte readback confirmed one band, float32, EPSG:32611, shape 3730×3292, recorded affine transform, 5,167,373 finite cells, 7,111,787 NaNs, finite range [0,1], and 40,199 positive cells. The present checkout does not include the sample template, so an exact fresh template comparison was not possible. Whole-array finiteness fails because outside-footprint values are NaN. The previously recorded local validator result is historical; no current official portal validation was performed. Evidence: [`evidence/saved_bytes_audit_20261025.json`](evidence/saved_bytes_audit_20261025.json) and [`evidence/duplicate_guard_run_card_20261025.json`](evidence/duplicate_guard_run_card_20261025.json).

The H33-D builder and the old domain-transfer runner are disabled fail-closed because their earlier versions made unsupported promotion/range-immunity claims. No new unique TIFF was generated, no competition slot was spent, and no upload was made. A locally unique filename is not enough to satisfy the lane duplicate rule or the scientific holdout gate.


<details>
<summary>Current request / mandatory consolidated starting prompt (2026-10-25)</summary>



Read this addendum and README before future work. This preserves the current requirements in a consolidated form, not a verbatim transcript of repeated chat paragraphs. Earlier dated decisions remain historical.

### Highest urgency and parallel-run protocol

**MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.** Do not meet this requirement by renaming, re-encoding, randomly perturbing or lightly editing a previous raster. A negative result is preferable to a falsely cleared submission.

1. **LANE.** Stay in the single assigned method paragraph. If raster rank-correlation with any registry raster exceeds 0.90, or more than 70% of candidate dots fall within 3 px of one registry raster's dots, log duplicate and stop. Check the surface before placement AND final dots. The current request does not contain an identifiable new standalone lane paragraph; the README's analog-field transfer paragraph is historical context, not authority to switch lanes.
2. **REUSE, DON'T REBUILD.** Use the template's cached feature stack, `evaluate_holdout.py` and `submission_writer.py`. Holdout = hide-and-recover: withhold whole fault segments with a buffer; derive every catalogue-based feature from visible faults only; mask visible faults pixel-exactly; score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). Fix a shared-tool bug in its actual template, once; do not keep a private evaluator fork. There is no identified canonical shared-template commit/path in this checkout. Other sites' same-named scripts are not automatically the canonical template.
3. **LABEL EVERY NUMBER.** Performance results must be HOLDOUT-DTI (evaluator version, withheld-positive count, 95% CI) or ORGANIZER-CONFIRMED (submission-page receipt). User-supplied scores are unverified historical claims, not measured results; projections must never be presented as scores. Counts, distances, hashes, and diagnostics are not performance scores.
4. **LEAKAGE CANARY.** Test each feature alone on the holdout before trusting it. AUC above 0.90 means leakage until proven otherwise.
5. **RUN CARD.** End with one JSON card: hypothesis; mechanism; named non-fault mimic; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside footprint, values in [0,1], matching CRS/shape/transform); submission name + note <=140 characters; verdict promote/negative. Use null plus a reason for unmeasured fields, not invented values.
6. **BUDGET.** Stop after 3 experiments or 2 hours. Do not pick submissions: promotion to a real slot is a separate selector within the verified weekly cap. Never guess the cap or spend a slot on an unvalidated idea.

### Focus and goals

- Review the highest-scoring named artifacts from GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33 and GEMSDOE36. Study GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, user-reported at 0.2778; explain its construction from audited bytes, distinguish causal hypotheses from proof, and seek a genuinely distinct strategy.
- The request gives conflicting current-leader values, 0.4413 and 0.3195. Neither is a verified current score in this checkout. Do not choose one or fabricate a live feed.
- Before model implementation, rank 3–5 new geological hypotheses with named layers, transform/physical signature, reason for missing-catalogue sensitivity, difference from local prior art, expected improvement (qualitative unless measured), cost, and verified obtainable free official data. An unverified source is blocked, not viable.
- Validate the top viable candidate on spatially blocked holdout and independent confirmation against the current comparable holdout best. Do not spend a weekly slot unless all scientific, leakage, uniqueness and format gates pass. Inspection must be automated in-project, not delegated to a human scientific inspector.
- Build a clean GitHub Pages site with a first-screen download/status area and executive-summary submission instructions. The download must say separately whether it is safe for research and whether it is cleared for submission. Single-band GeoTIFF or ZIP containing one GeoTIFF; exact template CRS, shape and geotransform; finite in-footprint predictions in [0,1]; explain unresolved outside-mask semantics. Give a distinctive name and <=140-character note. Do not assert that the reported range error was caused by NaN without the rejected bytes and organizer diagnostic.
- Organize trusted-source research and data into auditable tables with links, hashes and explicit provenance limitations. The scientific competition target is missing faults relevant to geothermal exploration, not direct verified geothermal vent discovery. External-source licensing, independence, schema and coverage must be checked before training.
- Complete available data restoration/feature preparation autonomously. Do not treat an owner mirror as an official authenticated download. Do not claim a GPU is mandatory for every model: the official reference supports CPU, though GPU training may be faster.
- Implement, then adversarially review, then reconcile against the full request; fix defects in each pass. Preserve negative results and flag irregularities. No hallucinated scores, access, validation or receipts. Keep Maximize P(Win) and Own the Outcome central.
- Create a PR on this session branch and merge using the explicit PR number if checks/protections permit. Suggest the next work and report limitations accurately. Never upload to DrivenData or select a competition slot in this session.

### Review links supplied by the owner

- Competition/problem: https://www.drivendata.org/competitions/306/competition-doe-gems/ and https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- About/data/leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/ ; https://www.drivendata.org/competitions/306/competition-doe-gems/data/ ; https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Organizer reference: https://github.com/drivendataorg/gems-prize-reference-solution
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf (not reauthenticated here)
- GeoDAWN official source: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- GDR: https://gdr.openei.org/submissions/1391
- Grid and metric background: https://epsg.io/32611 ; https://en.wikipedia.org/wiki/Tversky_index (secondary background, not the competition metric contract)
- Owner Pages for each focus repo: `https://buffedlizard55-lab.github.io/GEMSDOE{N}/` (N = 24,25,27,28,30,31,32,33,36); GEMSDOE32 source page: https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
- Dropbox data/rules links in the original owner request remain unverified third-party mirrors, not official authentication. Prefer the recorded hash-pinned GitHub mirrors for this restricted workspace; never embed credentials.

</details>
