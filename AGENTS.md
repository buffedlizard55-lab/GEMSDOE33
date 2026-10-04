# Operating rules for every session in GEMSDOE33

1. **Read `README.md` (standing brief) first.** It is the contract this repo is built against.
2. **No DrivenData login, upload, scraping, or polling from code.** The official
   [DrivenData Terms of Use, §Prohibited Uses](https://www.drivendata.org/termsofuse/)
   (read 2026-10-04) prohibit automated access/monitoring and manual monitoring or copying
   without prior written consent; `robots.txt` also disallows the leaderboard partial endpoint.
   Do not build an auto-refresh feed. Keep dated snapshots explicitly static, link to the official
   page, and use only authorized manual portal actions by the owner.
3. **No submission slot without valid, fold-safe evidence.** Candidate generation, the baseline,
   catalogue masks, and catalogue-derived source features must be rebuilt or excluded using only
   each fold's visible information. A candidate must beat the current holdout best on the frozen
   P1/P2 protocol and pass the exact format audit before a slot is even considered. The old
   `scripts/run_holdout33.py` result is withdrawn; it is legacy-only. The replacement
   `scripts/run_holdout33_source_audit.py` is still a conditional diagnostic because its upstream
   H19-5 surface is not re-derived per fold. Neither result clears a slot unless those limitations
   are resolved and the gate passes.
4. **Portal-safe local outputs only**: single-band float32, EPSG:32611, 100 m, same
   shape/geotransform/bounds as the sample submission, finite `[0,1]` over the WHOLE array,
   zero outside the footprint (IR-PORTAL-01). A local format pass is not organizer acceptance.
5. **Sample-template values are not truth.** Use only finiteness/grid metadata from the restored
   `sample_submission.tif`. It was found to equal the catalogue labels on all 5,167,373 finite
   footprint cells (IR-SAMPLE-LABEL-01); see `evidence/sample_template_label_overlap.json`.
6. **Provenance discipline**: every external byte enters via `registry/data_manifest.json`
   (hash-pinned mirrors) or is flagged; every claim carries a verification level
   ([B]/[P]/[S]/[C] per `knowledge/05_data_sources_verified.md`). Hashes identify mirror bytes;
   they do not authenticate the official source. Scores are "owner-reported" until an organizer
   receipt exists.
7. **Proxies are not scores.** Catalogue-hidden and SGMC off-catalogue DTI are local stand-ins for
   the private expert-labelled truth; say so in every report. A proxy delta is not a contest-score
   forecast.
8. **Own the outcome**: if a run fails or an artifact is missing, fix it or flag it as an
   irregularity (IR-*) in the README table the same session.
