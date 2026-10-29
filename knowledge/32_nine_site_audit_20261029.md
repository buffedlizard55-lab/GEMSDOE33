# 32 — Nine-site uniqueness and validation audit (2026-10-29)

**Decision: OK TO SUBMIT: NO for every file.** No experiment was run and no candidate was generated in this session. A33-R7 is exhausted at 3/3, and no identifiable current method paragraph authorizes a new lane; no experiment was inferred.

## Scope
- Owner-listed TIFFs on the nine focus sites (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36): 21 files. Each is pinned to a git blob SHA-1 in `registry/nine_site_best_files_20261029.json` (role `site_best` for the 9 highest, `site_listed` for 12 others).
- Plus this repository's own 17 downloadable research TIFFs (role `local_research_zeros`, no owner score).
- Each file is compared with every other pinned file (38 manifest entries + 22 registry rasters; byte-identical copies excluded).
- Scores are USER/OWNER-REPORTED values from the brief. No DrivenData login, leaderboard scrape, or upload was used (AGENTS.md rule 2).

## Method (reproducible)
- `scripts/nine_site_audit.py` fetches each blob by SHA-1 with `gh api` (cached to `data/nine_site/`, git-ignored), checks format against the template, builds dot masks, and runs the duplicate guard: Spearman/phi > 0.90 **or** > 70% of candidate dots within 3 px of another file's dots.
- `scripts/validate_nine_site_files.py` runs the project validator (`scripts/validate_submission.py`) on every blob, in default and strict zero-outside modes.
- Outputs: `evidence/nine_site_audit_20261029.json` (mirrored to `docs/data/nine_site_audit.json`), `evidence/nine_site_validator_20261029.json`, `evidence/submission_selection_20261029.json`.

## Results (MEASURED)
1. **Nine site-best files are one H19-5 family.** Each triggers the guard (25 triggers, GEMSDOE30 26). Dot-set-identical groups: GEMSDOE25 d2.8 = GEMSDOE30 d2.8 = GEMSDOE33 d28-reference (44,090 dots); GEMSDOE28 H27-4 r1 = GEMSDOE31 H27-4 (40,199 dots).
2. **B2 recount.** GEMSDOE32 B2 (37,654 dots) = GEMSDOE31/28 H27-4 (40,199 dots) minus 2,545 dots. All 2,545 removed dots lie at catalogue distance 1–2 px, nothing is added, and 0 B2 dots lie on the catalogue. This confirms `knowledge/22`.
3. **Unique under the guard (dot-level, against every other pinned file):** GEMSDOE27 h31 (0.2250\*, max overlap 62.8%), GEMSDOE36 kpl36 (0.1647\*, 69.9%, borderline), GEMSDOE30 MSDB1 (0.1462\*, 55.0%), GEMSDOE33 s33-seisdil (0.0963\*, 42.9%), GEMSDOE24 gvc1 (0.0859\*, 69.1%), GEMSDOE25 h66 (0.0742\*, 50.8%), GEMSDOE28 s18 (0.0217\*, 24.9%), GEMSDOE28 s21 (0.0206\*, 69.4%). GEMSDOE27 h29 (0.2190\*) triggers once against h31 (88.8%). These are owner-scored already, so re-sending them adds nothing.
4. **This repo's research TIFFs.** Most pass the dot guard and the format check. Three are not independent: LCHC, THKCOND and BASESTEP overlap each other by 90.7–94.0% (`IR-33-20261029-MUTUAL-DUP-01`). Earlier "unique" labels for those three were scoped to the pinned registry only. HMDT has 33,616 cells of 1.0 outside the footprint (`IR-33-20261029-HMDT-OUTSIDE-01`). PCSUP passes the dot guard but failed the pre-placement surface gate at 86.08% (`IR-33-R7-PCSUP-SURFACE-01`).
5. **Validator (format only).** Default policy: 37/38 pass. Strict zero-outside: 28/38 pass. The failures are the NaN-outside files (strict only) and HMDT (both modes, `outside_policy_pass`). Validator pass is a format check, not a uniqueness or score check.
6. **Selector.** 0 eligible; no raster OK TO SUBMIT.

## Pass 2 — bugs found in review and fixed
- Table 3 showed "FAIL: unknown" for HMDT, because format details were read from the wrong record. Fixed to read `nine_site_files`.
- The validator wrapper read a nonexistent `checks` key and reported no failing gates. Replaced with explicit gate-value comparison.
- The scope wording "43 known files" was stale after the audit was extended. Corrected to the actual comparison set (38 + 22).
- Trigger-count wording was "24–26", but the measured range is 25–26. Corrected.
- The mutual-overlap minimum was typed as 90.9%; the measured value is 90.7%. Corrected.
- A table caption said unique files were "identical dots", which is wrong for unique files. Corrected.
- A test asserted a tautology when a constant was missing. Replaced with the explicit site list.

## Pass 3 — recheck against the request
| Request | Status |
|---|---|
| Executive summary, highest-scoring submissions from the nine sites, file to download, estimated score, uniqueness | Done (`docs/executive-summary.html`, Table 1). Estimated score: "Not estimable" for every file. |
| Unique GeoTIFF not a duplicate of any listed submission | **Not met.** No file is unique and unscored. Unique files exist only among already-scored or research files (Tables 2–3). |
| Passes automated validation | Format: yes for 37/38 by default. No file passes the holdout gate. |
| Obvious OK-to-download / OK-to-submit | Yes: every row says NO to submit; download is labelled learning-only or research-only. |
| Beat 0.2778 / 0.4413 | Not demonstrated. No holdout evidence supports a higher value. |
| Labels HOLDOUT-DTI or ORGANIZER-CONFIRMED; owner scores marked \* | Done. No organizer receipt exists. |
| IR-* flags | Six new entries in `registry/irregularities.json`. |
| Pages site with instructions and error handling | Done (executive summary and index; error text "Predicted values must be in range [0, 1]" is in the existing instructions). |
| README standing prompt | Done (`README.md`, "Standing prompt" section; `standing_prompt.md` addendum). |
| One JSON run card | `evidence/run_card_nine_site_20261029.json`. |

## Remaining work (ranked)
1. **Do not infer or start a new lane from this audit.** The only route to a unique, OK-to-submit TIFF is a new preregistered candidate that passes both the surface and final-dot guards, and then the holdout gate. A33-R7 is exhausted at 3/3, and the current request has no identifiable method paragraph; this is a protocol blocker, not permission to choose a lane.
2. Retract or re-scope the "unique" claims for LCHC, THKCOND and BASESTEP (`IR-33-20261029-MUTUAL-DUP-01`).
3. Fix or retire the HMDT zeros file, which has out-of-footprint 1.0 values (`IR-33-20261029-HMDT-OUTSIDE-01`).
4. Obtain organizer receipts for the owner-reported scores and reconcile 0.4413 / 0.3195 / 0.2778 (`IR-33-20261029-SCORE-CONFLICT-01`).
5. Settle the outside-footprint policy (NaN vs zero) with the organizer. The portal range error is still unexplained.

## Limitations
- Scores are owner/user-reported. No score in this repo is organizer-confirmed or estimated.
- The duplicate guard is dot-level. For binary rasters the surface and dot sets coincide, but the surface gate from `IR-33-R7-PCSUP-SURFACE-01` was applied in earlier lanes only.
- Blob identity proves the bytes in the owner repos, not who submitted them or with what score.
- The validator is a format check. It does not measure uniqueness, holdout gain, or the organizer's acceptance rules.
- No leaderboard access. The 0.4413 and 0.3195 figures are unverified.
