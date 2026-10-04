# Historical three-pass review record — superseded 2026-10-04

> **Not current evidence or submission advice.** This closeout began with the first C2 round. Its former H27-4 `0.2708` score/file attribution is unsupported. A separate `0.3195` current-target claim is conflicted and unverified: the retained dated status notes are not row-level evidence, and no leaderboard rows are stored. The old shortlist was retrospective. See `knowledge/07_hypothesis_slate_20261004.md`, `knowledge/08_h33_6_result_20261004.md`, and `registry/leaderboard_review.json` for the later round and current disposition.

This record is retained to show review and correction history against the original project brief in `README.md` / `standing_prompt.md` and the repository `AGENTS.md`. It does not turn any catalogue proxy or local format pass into competition validation or organizer approval.

## Pass 1 — Implement and preserve evidence

- The first C2 stepover-relay P1 pass was withdrawn after review found that the candidate/control construction used full-catalogue labels and the Qfaults source geometries included systems later called held out. Those values are not promotion evidence.
- A corrected source-exclusion C2 diagnostic rebuilt the control from fold-visible catalogue labels and excluded whole Qfaults source IDs around each holdout. It remained conditional because the fixed H19-5 raster was not re-derived per fold. The corrected P1 mean ΔDTI is `−0.000722` (0/4 positive); P2 SGMC proxy is `+0.000283`. C2 is research-only and not slot-cleared.
- A separate exploratory H33-F analog-field run was also recorded: P1 mean ΔDTI `−0.093072` (0/4 positive), P2 `−0.016163` vs C0 and `+0.001234` vs matched random. Its domain-classifier AUC `0.917` is not `HΔH`; source labels were not independent field truth, `lambda` is unknown, and transfer was not licensed. Its distinct TIFF remains research-only; details are in `knowledge/07_analog_transfer.md` and `evidence/holdout_analog.json`.
- In a later, separate round, five hypotheses and H33-6 numeric gates were frozen and SHA-256 pinned before H33-6 implementation/holdout. H33-6's P1 mean ΔDTI is `−0.00273732` (2/4 positive); P2 is `+0.00015900`. It failed P1 and was stopped without retuning. Its unique TIFF is a distinct research artifact, not a submission recommendation; it is not the D2.8 reference.
- The top-level D2.8 raster remains a historical owner-mirror reference file only; no receipt authenticates its score/file pairing. No DrivenData upload occurred and no weekly slot was spent.

## Pass 2 — Review, correct, and disclose

- Corrected the H27-4 `0.2708` status: the linked GEMSDOE28 owner page says H27-4 is unscored/research-only, and no organizer receipt or authenticated account/file record ties that number to the TIFF. Do not explain it as a verified score or use it for calibration.
- Corrected the current-leader status: `0.3195` remains a user-supplied target with conflicting, non-row-level dated observations. Neither establishes the current leader. DrivenData's Terms of Use restrict monitoring/copying absent the required permission; the project stores no leaderboard rows and does not refresh the page.
- Reviewed official rules and source listings. AI-use disclosure and submission/final-choice constraints remain for the human owner to recheck before any eventual upload. Public source listings do not prove that binary payloads were retrieved, licensed for the intended reuse, or geometrically suitable.
- Kept the missing BRIDGE/Gabbs payloads explicit. Their listed availability and bounding-box overlap do not establish local bytes, schema, CRS, label compatibility, or feature-level overlap. No domain-transfer claim or `HΔH` estimate is made.
- Changed `scripts/validate_submission.py` to permit null/NaN or zero outside the finite footprint under the recorded format policy, require finite `[0,1]` values inside, and offer `--strict-zero-outside` as an explicit alternative. The separate audit is local format evidence only—not scientific validation, portal acceptance, or upload permission.
- Rebuilt the research page to show the frozen-protocol SHA-256, separate H33-6 from D2.8, link its artifact/note/evidence and independent local format-audit receipt, and state the failed gate and non-submission status.

## Pass 3 — Acceptance re-check

| Original-brief criterion | Re-check result |
|---|---|
| Explain the claimed H27-4 `0.2708` result without conflating unscored variants | **Corrected:** no verified score/file association exists; the score-claim review documents why the premise cannot be accepted as fact. |
| Treat the `0.3195` target cautiously | **Met:** conflict-aware dated status only; unverified as the current leader; no copied rows or refresh. |
| Rank 3–5 hypotheses before implementation and preserve prior-art/source reasoning | **Met for the H33-6 round:** five ranked hypotheses and a frozen protocol are recorded. The earlier first-round shortlist remains explicitly retrospective. |
| Require spatial screening before spending a slot | **Met with a stop:** H33-6 failed its frozen P1 gate; the earlier H33-F screen and corrected C2 diagnostic are also negative. None is slot-cleared; do not retune from completed holdouts. |
| Provide a distinct, uniquely named TIFF and short note | **Met as a research artifact only:** the H33-6 TIFF and note are downloadable in the research area and plainly marked **not for upload**. It does not copy the D2.8 TIFF or constitute approval to use a weekly slot. |
| Show local format evidence without implying success | **Met:** package checks and the separate audit are linked; NaNs are outside the footprint; the page says format checks do not prove scientific validity or portal acceptance. |
| Preserve provenance and data limitations | **Met with retrieval gaps:** owner-mirror provenance, uninspected official analog payloads, conditional H19-5 provenance, and proxy-label limitations are recorded. |
| Preserve the full prompt and run review/tests | **Met:** README retains the project brief and `standing_prompt.md` is synchronized. The site builds, 66 tests pass, the repository checks pass, and `git diff --check` is clean at this review. |
| Create a PR and merge if feasible | **Separate GitHub action:** scientific failure does not authorize a submission. PR/check/merge status is tracked separately by GitHub and does not change the scientific gate; work stays on the fixed Arena branch. |

## Decision

No candidate is cleared for a competition submission slot. H33-6 and the earlier H33-F each remain distinct failed-gate, unique research-only TIFFs; C2 remains withdrawn/conditional research evidence. The top-level D2.8 file is a distinct historical reference and is not proof of a score/file association. Local results and format checks are not a competition score, private-label validation, portal acceptance, or upload recommendation.
