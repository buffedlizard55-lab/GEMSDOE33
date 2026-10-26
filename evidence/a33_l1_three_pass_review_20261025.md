# A33-L1 three-pass implementation and release review

**Date:** 2026-10-25
**Scope:** analog-transfer implementation, holdout result, nine-site forensics, GeoTIFF package, README and generated site.
**Overall disposition:** **PASS FOR RESEARCH RELEASE; NEGATIVE FOR COMPETITION SUBMISSION.**

## Pass 1 — scientific protocol and adversarial leakage review

Reviewed the frozen preregistration, `SegmentHoldout`, all A33-L1 feature/model paths, emission, evaluator calls and evidence fields line by line.

Checks:

- preregistration SHA-256 remains `fa30ed9c567a9802cd6053ff1831e18ce0556f78a1e62f9f769e812d4ad4a06d`;
- 12 implemented feature names and model/quantile/fusion/emission parameters match the frozen A33-L1 protocol;
- fold CDF construction uses `train & ~analog`; source fitting uses `train`, `visible` and distance to `visible`; no held-out truth coordinates enter fitting, mapping, masking or placement;
- complete 8-connected components touching the fold/collar are hidden globally, with a 15-pixel training purge;
- candidate, B0, B1 and matched random use the same fold eligibility, dot-thinning operator and budget;
- pooled TPw/FPw/FNw, paired 10 km-block bootstrap and 3/4 fold gate are applied by the pinned shared evaluator;
- all feature canaries and both novelty stages execute before any competition decision.

Findings and corrections:

1. The first draft of the refreshed README/site accidentally described A33-L2–L5 with names from a different conceptual slate. This documentation drift did not affect code or the frozen experiment. It was corrected to the exact preregistered leave-one-field consensus, matched local contrast, CORAL covariance alignment, and blocked BRIDGE/Gabbs hypotheses; tests now lock those names.
2. The runner originally computed the pre-final gate with `all(scientific_gate.values())`, which included a non-empty baseline-name string. It happened to be truthy and did not alter this result, but was fragile. The code now enumerates only the six boolean criteria explicitly. No experiment was rerun and recorded values were not changed.

Verdict: fold mechanics satisfy the stated catalogue hide-and-recover proxy. Remaining scientific limitation is fundamental: source labels are the same mapped catalogue, not independent dense analog truth; 8-connected raster components are a proxy for expert fault segment IDs.

## Pass 2 — implementation, reproducibility and artifact review

Checks:

- vendored `holdout.py`, `metric.py`, `submission.py`, and `validator.py` exactly match all SHA-256 values in `vendor/gems24_template/SOURCE.json` at pinned GEMSDOE24 commit `fc2bc6f350bf5c6ce8da5d7a2ab03578ea1259d1`;
- 17/17 restored inputs and the canonical grid audit pass; focus registry restoration verifies 9/9 SHA-256 values and template grids;
- the runner is one-shot and refuses implicit retuning after evidence exists; `--verify-recorded` passes;
- zero-outside TIFF independently passes `scripts/validate_submission.py`: one float32 band, EPSG:32611, exact shape/transform/bounds, whole-array finite `[0,1]`, 37,654 positive cells;
- primary TIFF SHA-256 is `2bbbf7e381720f2242959e3efd6f2437f273afe6e7c48540d769524d2b4e8759`;
- ZIP integrity passes and contains exactly that one TIFF; docs run card is byte-semantically equal to the evidence run card;
- final note is 95 characters, under the required 140-character limit;
- 81 automated tests pass, including frozen preregistration, source-transform unit tests, saved-byte grid/range/hash, ZIP, run-card verdict, uniqueness thresholds, focus lineage and vendor hashes.

Verdict: reproducible and suitable as a research artifact. Format validity is explicitly not portal acceptance or scientific promotion.

## Pass 3 — release, claims and site review

Checks:

- rebuilt every generated site page from `scripts/build_site.py`;
- all local links resolve; one-click TIFF/ZIP/twin links point to existing files;
- landing page and executive summary place **DO NOT SUBMIT / NOT OK TO SUBMIT** ahead of the download;
- current results are consistently labelled HOLDOUT-DTI with evaluator version, 60,988 withheld positives and 95% CI;
- every historical focus value is labelled OWNER/USER-REPORTED, NOT ORGANIZER-CONFIRMED;
- no portal upload, organizer receipt, leaderboard polling or competition-score projection is claimed;
- README, standing brief addendum, scientific report, site, run card and irregularity registry agree on the negative verdict;
- `git diff --check`, site generation, compile checks and all 81 tests pass.

Release decision:

- **OK to download:** yes, for research/audit.
- **OK to submit:** **no**.
- **Why:** A33-L1 HOLDOUT-DTI 0.108374 [0.097607, 0.119402] is below B1 0.113244 [0.102796, 0.124169]; paired delta −0.004870 [−0.010900, +0.001226], 0/4 wins.
- **Slot action:** selector not run; zero slots spent.

Known limitations preserved: owner-mirror rather than organizer-authenticated inputs; no independent analog labels; component proxy rather than expert segment IDs; mapped-catalogue proxy rather than private target truth; historical score/file pairings unauthenticated; no portal acceptance test.
