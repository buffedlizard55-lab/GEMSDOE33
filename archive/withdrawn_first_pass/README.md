# Withdrawn first-pass artifacts — audit only

**Do not run or cite these files as validation, a leaderboard prediction, a formal domain-divergence
bound, or evidence to approve a submission slot.** They are preserved to document why the original
promotion claims were retracted. The active policy and findings are in
[`evidence/first_pass_disposition.json`](../../evidence/first_pass_disposition.json) and
[`registry/irregularities.json`](../../registry/irregularities.json).

The main validity failures were: pseudo-hidden truth locations were passed into
`reconstruct_shadow` to modify the prediction; the reconstruction radius was tuned against
owner-reported scores; confirmation seeds and budgets were reused; the comparison instrument was
structurally biased across emission families; an arbitrary random-row discriminator was treated as
field-transfer evidence without valid source/target domains, `HΔH` class, finite-sample term or
joint-label error `lambda`; and a hand-coded AUC / uint8 radiometric-ratio pipeline had unresolved
method assumptions. No archived score or metric is promotion evidence.

The historical scripts reference the former holdout API, which has been removed from active code so
that the invalid pseudo-hidden instrument cannot be accidentally rerun. The former
`run_domain_adaptation.py` source itself was overwritten before an archival copy was made; its
result and execution log remain, and this gap is disclosed as `IR-33-ARCHIVE-01`. The old confirmation
plan is in `knowledge/02_preregistration_confirmation_historical.md`. Experimental TIFFs and their
paste-ready notes are not in `docs/downloads/`.

A dated leaderboard review was performed once at the owner's request. After reviewing DrivenData's
Terms of Use, copied participant/rank/score rows and the target-score examples derived from them were
removed from the active records and this archive. The remaining model-derived inversion is withdrawn,
not reproducible from the removed examples, and not promotion evidence. No further leaderboard
monitoring or copying is authorized by this repository; see `registry/leaderboard_review.json`.
