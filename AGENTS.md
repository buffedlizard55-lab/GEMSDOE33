# Operating rules for every session in GEMSDOE33

1. **Read `README.md` (standing brief) first.** It is the contract this repo is built against.
2. **No DrivenData login, upload, scraping, or polling from code.** The official
   [DrivenData Terms of Use, §Prohibited Uses](https://www.drivendata.org/termsofuse/)
   (read 2026-10-04) prohibit automated monitoring/copying and manual monitoring/copying without
   prior written consent. Do not build an auto-refresh feed, copy leaderboard rows, or refresh a
   snapshot without written consent or an authorized API. The repository keeps only a dated status
   note; an official portal upload remains a manual action by the owner.
3. **No submission slot without valid, fold-safe evidence.** Candidate generation, the baseline,
   catalogue masks, and catalogue-derived source features must be rebuilt or excluded using only
   each fold's visible information. H33-6's preregistered screen failed P1 (mean ΔDTI `−0.00273732`,
   positive in 2/4 folds) against the local H27-4 owner-mirror raster control; that control's
   score/file pairing is unverified. Stop this arm: do not rerun the completed screen to repair its
   post-write logging or retune from its holdout, and do not upload its research-only TIFF. The old `scripts/run_holdout33.py` result is withdrawn; it is legacy-only. The
   conditional C2 source-audit, H33-F and H33-6 results retain the unresolved fixed-H19-5
   upstream provenance limitation. None clears a slot. A future candidate needs a fresh, frozen,
   independent confirmation against a comparable local reference, and must pass the exact format
   audit before a slot is even considered.
4. **Submission-output policy**: single-band float32, EPSG:32611, 100 m, same
   shape/geotransform/bounds as the owner-mirror sample. The top-level D2.8 file is a historical
   reference, not a new model or verified score/file pair. Its NaN-outside variant follows the
   recorded official null/NaN wording; a zero-outside alternative is troubleshooting only. H33-F
   and H33-6 TIFFs are separate failed research artifacts, not featured submissions. An earlier
   owner-observed portal range error did not establish that NaN caused it. A local format pass is
   not organizer acceptance.
5. **Sample-template values are not truth.** Use only finiteness/grid metadata from the restored
   `sample_submission.tif`. It was found to equal the catalogue labels on all 5,167,373 finite
   footprint cells (IR-SAMPLE-LABEL-01); see `evidence/sample_template_label_overlap.json`.
6. **Provenance discipline**: the reference's 17 inputs are pinned in
   `registry/owner_mirror_input_pins.json`; the separate `registry/data_manifest.json` describes the
   upstream C0/C2 candidate inputs. Any other external byte is flagged. Hashes identify mirror bytes;
   they do not authenticate the official source. Scores are "owner-reported" until an organizer
   receipt exists.
7. **Proxies are not scores.** Catalogue-hidden and SGMC off-catalogue DTI are local stand-ins for
   the private expert-labelled truth; say so in every report. A proxy delta is not a contest-score
   forecast.
8. **Own the outcome**: if a run fails or an artifact is missing, fix it or flag it as an
   irregularity (IR-*) in the README table the same session.

9. **Pre-A33 continuation record:** `knowledge/10_focus_review_20261025.md` records the concurrent 12-reference B2 audit, writer repairs, and fail-closed promotion checker. Keep it as prior art: B2 is a deletion-only duplicate-family emission, and `scripts/check_promotion.py` is an evidence-completeness gate—not an evaluator, selector, or upload tool.
10. **Current A33-L1 outcome:** read the final addendum in `standing_prompt.md`, `knowledge/11_focus_forensics_and_a33_l1_result_20261025.md`, and `evidence/a33_l1_run_card.json`. One frozen analog-transfer experiment ran through the pinned shared evaluator. Its 12 feature canaries and 9-reference/12-reference release novelty guards passed, and a genuinely distinct 37,654-dot TIFF was written, but the scientific gate failed: HOLDOUT-DTI 0.108374 vs regional B1 0.113244; paired delta −0.004870, 95% CI [−0.010900,+0.001226], 0/4 folds. It is research-only and **NOT OK TO SUBMIT**. Do not rerun or retune A33-L1; no selector/upload/score projection followed.
11. **G33-DPPS outcome (2026-10-26):** read `knowledge/15_dpps_results_20261026.md` and
    `evidence/dpps_run_card_20261026.json`. DPPS (deterministic dip-projected persistence scarp)
    is unique vs 25 rasters and format-clean, and its mechanism beat its pixel ablation 8/8
    folds, but it **failed vs B1_regional on both splits** (screen HOLDOUT-DTI 0.095407 vs
    0.111285; confirmation 0.096015 vs 0.114619). It is **NOT OK TO SUBMIT**; do not retune it.
    No file in this repo is currently slot-approved.

12. **FSML / FSML2-CC outcome (2026-10-26):** read `knowledge/22_b2_forensics_and_fsml_slate_20261026.md`
    and `knowledge/23_fsml_results_20261026.md`. FSML-PU (fold-safe H19-5-style PU re-derivation)
    was a surface **duplicate** of A33-R2-CSHT (87.51% within 3 px) — supervised rankings on this
    stack converge; do not rebuild another catalogue-supervised blend expecting uniqueness.
    FSML2-CC is unique (final max 3-px 40.68%) and format-valid but **negative** vs CSHT on both
    splits (Δ −0.0252/−0.0290, 0/4+0/4); uniform 25k budget descent was also rejected for both
    surfaces. Do not retune either. All nine focus sites' best files are one H19-5 emission family;
    GEMSDOE36's file contains B2's dots exactly. No file is slot-approved (selector 0/13).

13. **A33-R7 correction (2026-10-28):** read `knowledge/31_r7_pcsup_lane_correction_20261028.md`
    and `evidence/a33_r7_pcsup_lane_correction_20261028.json`. A33-R7-PCSUP's preserved experiment JSON
    explicitly records pre-placement surface overlap `0.860838` > `0.70` (max |ρ| `0.100959`), even
    though its final dots later passed. The surface gate failed and must have stopped the lane before
    placement/evaluation. Treat PCSUP as duplicate/drift, not unique; its later HOLDOUT-DTI is
    exploratory only. Original evidence is immutable. Do not retune or run a fourth A33-R7 experiment.
    No raster is OK TO SUBMIT; the latest site/README summary must preserve this correction.

14. **Density rule (2026-10-29):** report every holdout comparison at deployment density (37,654 dots, 0.7287% of the footprint) as well as the 2.5% campaign density. A candidate counts only if its paired CI against the matched random control at deployment density lies strictly above zero with at least 3/4 fold wins. Read `knowledge/34_density_audit_results_20261029.md` and `evidence/density_audit_20261029.json`. Random floor at deployment density: 0.0737 HOLDOUT-DTI.
15. **Official check rule (2026-10-29):** every official claim used in a run card or page must have a row in `knowledge/36_official_verification_20261029.md` with its link and the text actually read. Do not rely on memory. The organizer's reference notebook is an official source for band names and output format.
