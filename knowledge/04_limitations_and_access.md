# Limitations and access needs (GEMSDOE33, 2026-10-04)

## Hard limitations in this sandbox

| ID | Limitation | Consequence | Mitigation |
|---|---|---|---|
| IR-NET-01 | Egress allow-list: only github.com, api.github.com, codeload.github.com reachable. USGS, ScienceBase, GDR, NBMG, Dropbox, DrivenData all TLS-blocked | Cannot fetch official heat flow (DOI 10.5066/P9BZPVUC), MT conductance (DOI 10.5066/P9TWT2LU), GDR analog-field vectors, 1 m DEM tiles, or DrivenData files directly | All data restored from hash-pinned public GitHub mirrors (`scripts/download_competition_data.sh`); analog-field bytes must be fetched on an unrestricted machine |
| NO-AUTH | No DrivenData credentials (by policy: this repo never logs in anywhere) | Cannot upload submissions or read private scores; leaderboard values are owner-reported reads | Submission files are built, audited and staged for manual upload; scores are recorded in `registry/score_ledger.json` as owner-reported |
| COMPUTE | 2 vCPU, 3 GB RAM, no GPU, ~20 GB disk | U-Net training on the 19-band stack infeasible; 1 m DEM (716 tiles, ~1 TB) infeasible | Dot-emission analytics, distance-transform metrics, vector/raster joins all run fine (proven this session) |
| TRUTH | The scoring truth (expert-labelled new faults) is private by design | Local validation uses catalogue-hidden (P1) and SGMC off-catalogue (P2) proxies only | Every proxy result is labelled a proxy; slot policy requires beating the holdout best before submission |

## Access requests that would raise the ceiling (ranked)

1. **Unrestricted-egress run of `scripts/download_external_analogs.sh`** (next session) to
   pull GDR #207 GIS_Faults.zip (Dixie Valley), NBMG OF 03-27 (Desert Peak–Brady's) and
   GDR #1288 labelled grids → unlocks H33-A (rank-2 hypothesis).
2. **DrivenData manual upload** of the staged one-click file by the owner (weekly slot):
   `gems33-c2-stepover-relay-20261004-eb6bcf02361f.tif` with note
   `33GEMSDOE C2 stepover relay | P1 +0.00043 3/4 folds, P2 +0.00028 vs 0.2708 base | id eb6bcf02361f | proxy-gated`.
3. **GPU machine** for a supervised scarp detector on 1 m DEM tiles (the GEMSDOE28
   analysis identifies this as the credible route to 0.3195).
4. **GEMSDOE29 radiometric record** (seeds 280–289) — not retrievable via API this
   session (IR-EVIDENCE-01); needed to clear H33-D of pre-emption.

## What WAS completed autonomously this session

* Full competition data placement from hash-pinned mirrors with SHA-256 verification
  (419 MB feature stack included; `evidence/data_placement.json`).
* Campaign-validated DTI metric ported with 7 passing unit tests.
* Five candidates built, P1/P2-gated; one promoted (C2), one honestly refuted (C3).
* Portal-safe TIF generation fixing IR-PORTAL-01 (finite [0,1], zero outside footprint).
* Verified official source table: `knowledge/05_data_sources_verified.md`.
