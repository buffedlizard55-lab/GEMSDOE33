# Continuation: restoration and evidence-claims audit — 2026-10-26

## Executive decision

**No file is OK TO SUBMIT.** This continuation resolves the previous review's data-placement blocker, not the scientific promotion blocker. No new candidate or unique TIFF was generated and no submission slot was selected or spent. The nine-site comparison, existing research downloads, and ranked five-concept feasibility slate remain on the executive/hypotheses pages. No competition score estimate can be calibrated honestly from the available organizer evidence.

## Pass 1 — complete the previous session's actionable next step

- Read README, standing brief, AGENTS, the prior review and Round-4 feasibility report.
- Installed pinned project requirements into ignored `.venv`.
- Ran `scripts/restore_data.py --group all`: all 17 inputs restored and SHA-256/size verified from registered public GitHub mirrors.
- Ran `scripts/audit_inputs.py`: 17/17 pins pass. Sample/label positive sets match exactly; continue to use sample only for grid/footprint, never truth or predictors.
- Ran `scripts/prepare_data.py --skip-detector`: rebuilt 121 shared channels; no detector fitted. Cache construction is not feature validation and does not authorize using catalogue-derived channels in a holdout.
- Ran the separate selector: 0 eligible of 11 run cards. Reopened LLC zero-outside TIFF against the restored sample using `scripts/validate_submission.py --strict-zero-outside`: pass, zero nonfinite cells, all values in [0,1], exact CRS/shape/transform match. Receipt: `evidence/restored_template_llc_validation_20261026.json`.

All pin matches establish equality to owner-mirror bytes, not original organizer provenance or licensing. Data/cache are ignored and are not delivered with a fresh clone. This report supersedes the *missing local files* statement in review 19, not its scientific limitations.

## Pass 2 — fix defects and unsupported assertions

- **IR-RESTORE-ATOMIC-01:** restoration deleted an existing mismatched destination before a replacement was fetched/verified. Failed network or pin validation could therefore destroy the previous bytes. Fixed to retain the old destination until atomic replacement after successful verification.
- **IR-RESTORE-CLEANUP-01:** restoration recursively removed `data/raw`, including unrelated files. Fixed to delete only the part paths created by the current restore operation. Restoration remains a serial tool; simultaneous writes to the same destination are not supported.
- Added four offline tests: network failure preserves existing bytes; hash mismatch preserves existing bytes; multipart success preserves unrelated raw files; already-verified input avoids network.
- **IR-CLAIM-01:** corrected README assertions that duplicate-family convergence proves a private leaderboard loss and that one sparse-tree experiment proves universal failure. Neither follows from the recorded evidence. Duplicate status alone remains sufficient to stop promotion.
- Removed the unverified exact weekly-slot count from the prominent CSHT decision. Current cap remains unverified; the selector does not spend slots.

## Pass 3 — final verification and limitations

- Run `PYTHON=.venv/bin/python bash scripts/run_checks.sh` after rebuilding the static site; the final verification result is recorded in `evidence/restoration_review_checks_20261026.json`.
- The organizer reference commit exists in the official `drivendataorg/gems-prize-reference-solution` repository: `evidence/organizer_reference_commit_check_20261026.json`. This check does not newly verify the live competition rules, leaderboard or external publications.
- No DrivenData request, automated leaderboard refresh, portal login, upload, or organizer receipt was made. Conflicting owner-provided leaderboard highs remain unresolved. HOLDOUT-DTI is a catalogue-hide-and-recover proxy, not a competition-score forecast.
- No new geological experiment: the request requires a single assigned lane but supplies no method paragraph. Existing stopped arms were not rerun or tuned. The ranked five-concept Round-4 slate remains in `knowledge/18_round4_feasibility_audit_20261026.md`; no blocked external-source idea is promoted as viable.

## Next safe work

Freeze one explicitly assigned method lane, source pins, candidate parameters and independent confirmation split **before** evaluating. Then run each feature canary, the shared whole-segment buffered evaluator with visible-only catalogue features/masking, surface duplicate guard before placement, final-dot guard and saved-byte validator. Stop on a duplicate or failed scientific gate. Only a successful separate selector may make a candidate eligible; current competition cap must be verified before any real upload. Do not infer hidden-fault labels or geothermal vents from the sample values or historical submitted rasters.

Official links for review: [organizer reference](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b), [competition description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [DOE GDR 1391](https://gdr.openei.org/submissions/1391). Except for the reference commit, these links were not freshly fetched in this continuation; the network allowlist excludes their hosts.
