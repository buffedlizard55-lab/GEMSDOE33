# 2026-10-28 review — no submission cleared

## Executive decision

**No new experiment was run and no new TIFF was generated in this session.** The prompt refers
repeatedly to a single method paragraph but provides no designated lane. Assigning a different lane
would violate the parallel-run restriction. No weekly slot was used. The historical
[BASESTEP TIFF](../docs/downloads/gemsdoe33-a33-r6-basestep-37654-20261027-4e0c37d1d539-zeros.tif)
is downloadable for research only; **NOT OK TO SUBMIT**. Its advertised novelty applies only to
its recorded 21-raster registry, not every prior submission. The
[local saved-byte recheck](../evidence/basestep_format_recheck_20261028.json) passed single-band,
finite [0,1], CRS, shape and transform against the pinned owner-mirror template. This is neither
organizer acceptance nor an authentic organizer template verification.

## Pass 1 — source and data review

* All 17 pinned owner-mirror files were restored via GitHub and SHA-verified; see
  [input audit](../evidence/input_grid_audit.json) and [pins](../registry/owner_mirror_input_pins.json).
  A hash proves mirror integrity, not origin, license, or authorization. The current sandbox
  restricts outbound hosts and lacks organizer login. Git-ignored inputs/cache are not portable
  with the repository. The organizer's [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
  supports CPU or GPU; a GPU is not an absolute prerequisite.
* Prior [B2 forensics](22_b2_forensics_and_fsml_slate_20261026.md) reports an exact pruning
  relationship, not a causal proof of the privately scored result. The user's 0.2778 value is
  **USER-REPORTED, not ORGANIZER-CONFIRMED**. No submission-page receipt tying that score to
  exact bytes was found. A mechanism is that thinning can reduce false-positive mass and redundant
  kernel coverage; the private labels are unknown, so its causal contribution is unverified.
  Catalogue-recovery DTI cannot be converted to a defensible leaderboard prediction. Historical
  focus-site records are listed in the [executive summary](../docs/executive-summary.html).
* A 3–5 item prior slate, with sources, distinctions and feasibility, is recorded in
  [knowledge/26](26_thk_cond_slate_20261027.md) and [knowledge/24](24_pfrt_hypothesis_slate_20261027.md).
  It is historical, not evidence that its proposals remain untried. We did not claim a new
  validated hypothesis or choose a lane in this review.

## Pass 2 — scientific safety defects

**IR-33-20261028-LEAK:** both `run_basestep_campaign.py` and `run_thk_cond_campaign.py` call
`build_surface()` before creating folds. `build_surface()` calculates percentiles from
`footprint & ~grid.load_labels()`, where `load_labels()` is the full catalogue. Thus withheld
labels influence threshold/scaling fits. The canary is called once on the **combined** surface,
not separately for its input features, and the full final placement precedes the surface novelty
screen. These facts violate the requested protocol even if the distortion happens to be small.
Previously recorded DTI and confidence intervals are retained as **exploratory historical outputs**,
not valid holdout evidence or estimates of hidden score. The reported negative decision stays in
force. Both runners now fail closed before writing anything; their source remains available for
forensics. Do not retune these completed experiments on the same holdout.

The alternate spatial partition of the same catalogue is not automatically a statistically
independent new sample. A future design needs a frozen, truly independent confirmation protocol,
per-fold threshold fitting using only visible labels, each-feature canaries and pre-placement
novelty checks. Matched-random and historic B1 figures are not a paired comparison to the current
best. No scientific winner is identified here.

**IR-33-20261028-SELECTOR:** the previous selector trusted run-card boolean gate flags. Its former
positive-control test demonstrated that a negative card could be changed to a promote card without
re-evaluating the original measurements. The selector now requires a `promotion_evidence` object
with an evidence-directory JSON filename and SHA-256; it reassesses that file with the shared
promotion gate, binds the saved-byte audit, note and confirmation value, and fails closed if the
link is missing or mismatched. Existing cards remain blocked. This tests declared evidence
consistency, not authenticity: an invented but internally consistent JSON document could still
pass; source hashes, registry completeness, measurements and split independence require a stronger
automated provenance chain before a slot can be trusted.

## Pass 3 — product/validation check and next steps

* Repaired a broken BASESTEP validator-receipt link in the site generator and rebuilt the pages.
  The site now foregrounds the safety warning and the scoped meaning of uniqueness. The format
  validator's zero-outside pass is not proof that the organizer accepts this encoding, nor proof
  of the cause of the reported range error. The `-nan` alternative is not authorized either.
* Selector snapshot: [evidence/submission_selection_20261028.json](../evidence/submission_selection_20261028.json).
  No eligible candidate. The count includes non-candidate and historical run-card records, not
  independent models. The selector does not access or upload to DrivenData.
* Next: explicitly freeze the lane for a fresh run; rebuild every catalogue-derived feature and
  fit only from visible labels per split; canary every input; compare against a matched, fold-safe
  current best; check the registry on the surface before placement and again on final dots; audit
  an official template and organizer rules/weekly cap through authorized access. No leaderboard
  number is projected. Obtain valid source/licensing documentation before claiming owner mirrors
  are official. See [competition reference](https://github.com/drivendataorg/gems-prize-reference-solution),
  [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
  and [DOE GDR #1391](https://gdr.openei.org/submissions/1391) for manual source review; non-GitHub
  hosts could not be independently accessed from this sandbox in this session.
