# Operating rules for every session in GEMSDOE33

1. **Read `README.md` (standing brief) first.** It is the contract this repo is built against.
2. **No DrivenData login, upload, scrape, or polling from code, ever.** Manual upload of
   staged files by the owner is the only portal contact.
3. **No slot without a gate pass.** A candidate may only approach a weekly submission slot
   after it beats the current holdout best on the frozen P1/P2 proxy protocol
   (`scripts/run_holdout33.py`) and passes `scripts/validate_submission.py`.
4. **Portal-safe outputs only**: single-band float32, EPSG:32611, 100 m, same
   shape/geotransform/bounds as the sample submission, finite [0,1] over the WHOLE array,
   zero outside the footprint (IR-PORTAL-01).
5. **Provenance discipline**: every external byte enters via `registry/data_manifest.json`
   (hash-pinned mirrors) or is flagged; every claim carries a verification level
   ([B]/[P]/[S]/[C] per knowledge/05). Scores are "owner-reported" until an organizer
   receipt exists.
6. **Proxies are not scores.** Catalogue-hidden and SGMC off-catalogue DTI are local
   stand-ins for the private expert-labelled truth; say so in every report.
7. **Own the outcome**: if a run fails or an artifact is missing, fix it or flag it as an
   irregularity (IR-*) in the README table the same session.
