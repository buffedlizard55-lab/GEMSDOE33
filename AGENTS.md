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

9. **Latest continuation:** read `knowledge/10_focus_review_20261025.md` and the active addendum in `standing_prompt.md`. All 17 owner inputs and 121 cached channels were restored/prepared; this does not authenticate official origin or pass feature canaries. The 12-raster focus audit proves B2 is a deletion-only duplicate-family emission. Do not rerun H33-F/H33-6 or copy B2. Four new analog planning ideas are blocked by missing independent official labels and no explicit new lane/canonical template. `scripts/check_promotion.py` is an automatic completeness gate, not a new evaluator, selector or upload tool. Its expected current exit is 2; no new TIFF is claimed.
