# Three-pass review record (2026-10-04 UTC)

Scope: the original standing brief in `README.md`, the repository `AGENTS.md`, and the updated competition/proxy evidence. This review records the completed implementation, review/fix, and final acceptance re-check; a proxy or local format pass is not a contest score or organizer approval.

## Pass 1 — Implement

- Reproduced the C2 submission TIFF and its local format audit. The 41,139-dot file is explicitly a research artifact, not a submission-slot recommendation.
- Withdrew the legacy C2 P1 pass after identifying full-catalogue base/candidate construction and held-out Qfaults source geometries in the old test. Retained the numeric legacy report with a clear withdrawal marker.
- Implemented a conditional source-exclusion P1 diagnostic: fold-visible baseline rebuilding, fold-visible catalogue filters, whole source-system exclusion within a 600 m square holdout buffer plus a 100 m raster guard, and source-line sampling at up to 50 m.
- Kept P2 separate as an SGMC off-catalogue compilation proxy. No proxy is entered as a competition score.
- Published five ranked geological/review hypotheses, a provenance register, one-click research/reference downloads, and a manual submission/compliance guide with a conditional AI-use disclosure template.

## Pass 2 — Review and fix

- Re-read the original brief and checked the official September 2026 rules PDF in all seven parsed chunks (§§3.2, 3.4–3.5) and the DrivenData Terms of Use. Updated the submission-frequency/final-choice/AI-disclosure guidance and removed any implication of an automatically monitored leaderboard feed.
- Rechecked the public-score distinction: h27-4-r1-solo-d2-8 is the owner-reported 0.2708 result. GEMSDOE28 H36-1 and H38-1 are separate, unscored experiments; no model projection is recorded as a score.
- Added exact fold-by-fold incremental-mass reporting. The conditional C2 P1 diagnostic adds 2,643 fold-specific dots, zero incremental TPw, and exactly 2,643 additional FPw; the mean ΔDTI is negative.
- Added regression coverage for sample-template value independence, withdrawn legacy evidence, the current no-slot decision, and the distinction between P2 proxy values and organizer truth.
- Flagged unresolved inputs rather than assuming availability: the GDR #207 archive request failed TLS/connection setup; the Qfaults mirror's exact official version is unverified; H19-5 is not regenerated per fold; IR-SAMPLE-LABEL-01 remains explicit.

## Pass 3 — Acceptance re-check

| Original-brief criterion | Re-check result |
|---|---|
| Explain the highest owner-reported score without conflating unscored variants | **Met.** `knowledge/01_why_0.2708_won.md`, the executive summary, results feed, and README identify h27-4 as the 0.2708 result and H36-1/H38-1 as separate unscored entries. |
| Aim beyond the dated public leader without calling proxies contest scores | **Met with honest limits.** The stored 2026-10-03 public snapshot is 0.3262; the project makes no live-score projection. |
| Rank 3–5 geological hypotheses | **Met.** Five hypotheses are in `registry/hypotheses.json` and `docs/hypotheses.html`; estimates are withheld where evidence is missing. |
| Use linked official/free sources and preserve provenance | **Met with flagged retrieval gaps.** Source levels, mirror hashes, limitations, terms, and failed requests are recorded in `knowledge/05_data_sources_verified.md` and `docs/data-sources.html`. |
| Require fold-safe validation before any slot | **Met.** Corrected P1 is −0.0007220038 (0/4 positive), P2 is +0.0002831018, and no candidate is slot-cleared. The remaining H19-5 upstream limitation is disclosed. |
| Easy download plus clear manual submission guidance | **Met with safety boundary.** Download links are prominent; C2 is labelled research-only because it fails P1. The guide covers authorized manual portal steps, naming/comment template, format limits, and owner-reviewed AI disclosure. |
| Flag irregularities | **Met.** IR-PORTAL-01, IR-HOLDOUT-LEAKAGE-01, IR-SAMPLE-LABEL-01, IR-QFAULTS-01/02, IR-EVIDENCE-01, IR-NET-01, and IR-REPO-31-32 remain documented. |
| Run tests and local checks | **Completed:** 36 unit tests pass; the repository's `bash scripts/run_checks.sh` passes; all six site HTML pages parse with balanced tags; `git diff --check` is clean. |
| Create and merge the requested PR, if permitted | GitHub operation follows the local acceptance re-check and remains confined to the fixed Arena session branch; PR/check state is recorded by GitHub. |

## Decision

The technical/documentation acceptance criteria are complete, but **there is no cleared competition submission**. The C2 TIFF is downloadable for research/reproduction only. The corrected negative P1 result and unresolved upstream H19-5 provenance remain visible. PR creation/merge is tracked separately from scientific validation.
