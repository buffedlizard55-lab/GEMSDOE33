# Repository review and 2026-10-27 continuation

**Decision:** No new model experiment, raster, competition submission, or score was produced in this review. The current prompt asks for a single method paragraph/lane but does not identify one. The most recent standing instruction explicitly says not to infer a lane. Picking a new method from a ranked slate would violate that rule. The latest already-generated unique artifact remains FSML2-CC: available to download for research, **NOT OK TO SUBMIT** because its two fold-safe comparisons were negative. The automated selector currently returns **0 eligible of 13 candidate run cards**.

This is a negative continuation result, not evidence that the project has achieved the requested high-scoring submission. The current selector snapshot is [`evidence/submission_selection_20261027.json`](../evidence/submission_selection_20261027.json); this review's no-experiment card is [`evidence/20261027_review_card.json`](../evidence/20261027_review_card.json).

## Pass 1 — inspect and prepare reproducible inputs

1. Read the complete `README.md`, `standing_prompt.md`, and `AGENTS.md`, then reviewed the latest selector-safety, Round-4, B2-forensics, and FSML results.
2. Confirmed that the checkout initially contained neither competition inputs nor the ignored feature cache. No DrivenData login, submission, leaderboard request, or external official-site fetch was made.
3. Used the repository's existing `scripts/restore_data.py` against the registered public owner-maintained GitHub mirrors. All 17 inputs matched their registered byte counts and SHA-256 pins. This verifies mirror identity only; it does **not** authenticate organizer origin, completeness, or licensing. The local `sample_submission.tif` was checked only for grid/finiteness metadata because its finite values exactly equal the catalogue labels.
4. Ran the shared `scripts/prepare_data.py --skip-detector` once to restore the shared 121-channel cache; it did not train a generic detector or create a candidate-specific stack. The cache and source rasters are under ignored `.cache/` and are not included in the patch or site. On a fresh checkout, the repository's documented restore/prepare commands must be run again.
5. Refreshed the fail-closed selector from saved bytes. It found no eligible submission. The newest unique file is the existing FSML2-CC artifact, not a file generated in this review.

## Pass 2 — adversarial review and fixes

### Found and corrected

- `README.md` incorrectly named A33-R2-HMDT as the assigned current lane despite the later standing brief explicitly saying that the current request contains no identifiable lane. Corrected the operating brief and current decision.
- `README.md` described the old HMDT artifact as a candidate generated "this session" and promoted download language without prominently stating that its holdout was never measured. Reclassified it as historical, unvalidated prior art; it is not a recommendation.
- The documented next steps still recommended the fold-safe H19-5 re-derivation even though FSML/FSML2 had already tested it, and described COULOMB geometry as locally available although the feasibility audit found that its trace geometry/CRS was unusable. Replaced these stale actions with the current ranked slate and precise blockers.
- The prior selector snapshot had 12 cards. The current byte-level selector scans 13 run cards and returns 0 eligible; regenerated the 2026-10-27 snapshot and corrected current-site counts. Old dated reports remain labelled as historical.
- The 2026-10-26 user-provided score CSV omitted four lower-scoring focus-site reports that were included in the current user brief. Added them as USER-REPORTED rows; none changes the highest reported entry for its site, and none is organizer-confirmed.
- Added a machine-readable, three-candidate research slate. A tracked-code search found no implementation of phase-congruency/log-Gabor edges, basement/gravity ridge bifurcation persistence, or repeated cross-valley profile asymmetry as specified. This is a search of this repository, not a claim of novelty across other projects. The second candidate is explicitly marked as conceptually adjacent to existing ridge/network work; the third is blocked pending raw official 3DEP tiles.

### Scientific readout

The retained B2 forensics describe the reported GEMSDOE32 artifact as a 37,654-dot exact subset of GEMSDOE28 H27-4, deleting 2,545 additional catalogue-flank dots and adding none. Under the asymmetric, kernel-saturated DTI, reducing redundant low-credit predictions is a plausible mechanism for a higher reported score. It is **not proven causal**: hidden organizer labels and a receipt associating the exact raster bytes with the reported score are absent. The B2 value `0.2778` remains USER/OWNER-REPORTED, not ORGANIZER-CONFIRMED; copying or lightly altering that raster would be a duplicate and is disallowed.

No available holdout result can be converted to a leaderboard-score estimate. The catalogue hide-and-recover proxy anti-ranks this emission ladder, and the user supplied conflicting current-leader values `0.3195` and `0.4413`. Neither is verified here. No value is projected as a score.

## Pass 3 — final reconciliation and verification

The final review reconciles the user request against repository evidence as follows:

- The README and GitHub Pages first-screen decision distinguish the existing unique research download from a submission-approved file. The site says there is **no file OK TO SUBMIT**. FSML2-CC remains **OK TO DOWNLOAD FOR RESEARCH: YES / OK TO SUBMIT: NO**; it is not described as new in this review.
- The nine-site executive table continues to identify each site's highest owner-reported artifact, the precise file/name, an unavailable public-score estimate, and the fact that each is historical rather than a new globally-verified unique candidate. Recent lower owner reports are retained separately in the CSV and are explicitly labelled.
- Three candidate hypotheses are ranked in [`registry/hypotheses_20261027.json`](../registry/hypotheses_20261027.json) and displayed on the hypothesis page. The top candidate is multiscale cross-physics phase congruency using cached GeoDAWN magnetic/gravity fields. Its expected benefit is qualitative only. No experiment was started because there is no assigned lane paragraph.
- The only new outside-source requirement is H27-CATCHMENT-PROFILE's raw 1 m USGS 3DEP terrain. The official USGS source URL is provided, but raw tiles are absent and the recorded network allowlist blocks the tile host. It is therefore **blocked, not viable**. H27-PHASEEDGE and H27-BIFURCATION require no new data for a local research screen, but their local inputs are owner-mirror bytes, not organizer-authenticated downloads.
- The shared evaluator/writer and existing format audit were not forked. Saved-byte selector checks run against the restored grid template; the updated selector remains at 0 eligible of 13. No slot was picked or used.
- Existing unique FSML2-CC `-zeros.tif` remains the only highest-priority downloadable artifact. Its recorded local audit is single-band float32, EPSG:32611, shape 3730×3292, matching template transform, with values in [0,1]. This does not establish portal acceptance; the previously reported range error's rejected bytes and organizer diagnosis are still missing, and outside-footprint null/NaN versus zero semantics remain unresolved.

### Test and audit record

- Initial environment-only baseline before restoration: `166 passed, 12 skipped`; skips were due to absent local template/data.
- Final post-restoration, post-documentation command: `PYTHON=.venv/bin/python GEMS_DATA_DIR="$PWD/.cache/gemsdata" bash scripts/run_checks.sh` — **177 passed**, no failures. It rebuilt the site, ran all applicable tests, audited restored inputs/template, reran the selector, compiled source/scripts/tests, and passed `git diff --check`.
- `scripts/audit_inputs.py`: 17/17 registered owner-mirror pins passed; exact grid audit passed.
- `scripts/audit_sample_template_values.py`: sample/template finite mask and labels have exact positive-set agreement on the 5,167,373-cell finite footprint; sample **values are not used as labels or training truth**.
- `scripts/select_submission.py --date 20261027`: 0 eligible of 13. FSML2-CC's file, hash, ZIP, note, and saved-byte format checks pass, but its negative verdict/promotion gates fail.
- No new hypothesis feature was canaried, no HOLDOUT-DTI run was made, no TIFF was written, and no competition slot was touched.

## Ranked untested candidates and official-source availability

The slate is hypotheses only; it does not override the missing lane assignment. Each must be preregistered and have its feature-alone leakage canary and pre-placement uniqueness check before placement or holdout scoring.

| Rank | Candidate; layers/signature | Why it may recover a missing fault; local distinction | Named mimic | Expected benefit / cost | Source and availability |
|---|---|---|---|---|---|
| 1 | **H27-PHASEEDGE:** cached `tmi`, `ext_TMI_up150`, `iso_grav_anom`, optional `depth_to_base_surf`; multiscale local phase-congruency edges with cross-physics edge-normal agreement. | Buried displacement may juxtapose magnetic and density boundaries without a strong surface scarp. Phase alignment is different from the repo's raw-gradient H33-6 test, Hessian/ridge filters, scarp line integrals, and dip projection; it still shares layers and could converge. | Intrusive/stratigraphic contacts, magnetic-domain boundaries, survey seams, gridding artifacts. | Rank 1 qualitatively; moderate-to-high plausibility, unquantified. Medium-high implementation cost. | No new external data required for an internal test. Relevant layers exist in the 121-channel cache restored from SHA-pinned owner mirrors. Official reference link: [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and); not re-fetched this review, mirror bytes do not establish official provenance. |
| 2 | **H27-BIFURCATION:** cached `depth_to_base_surf`, `iso_grav_anom`, `iso_grav_anom_hg`; scale-persistent ridge skeleton and supported Y-junction/branch-termination graph. | Concealed basement steps/relay splays may produce persistent subsurface junctions without surface traces. Unlike catalogue-tip bridges or hydrothermal least-cost paths, the graph comes from multiscale geophysical ridges; however, existing ridge/network work makes this only partially distinct. | Intersecting lithologic contacts, basin margins, magnetic domains, interpolation seams. | Rank 2; plausible but lower confidence due common non-fault junctions and prior-art overlap. Medium cost. | No new data required for a research screen; cached bands are present in the local owner-mirror feature stack. Official reference: [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and); source not reauthenticated this review. |
| 3 | **H27-CATCHMENT-PROFILE:** raw USGS 3DEP 1 m DEM plus cached `det_elev`, basement-depth and gravity context; repeated cross-valley profile asymmetry and channel deflection across neighboring catchments. | Repeated, orientation-consistent drainage response could expose low-relief blind displacement not represented by mapped surface traces. It is not the previous maximum scarp-line integral, but the local 100 m DEM aggregate cannot resolve the intended signature. | Lithologic knickpoints, stream capture, fan-head incision, terraces, roads/canals. | Rank 3; potentially useful but currently unquantified and blocked. High cost. | Specific free official source: [USGS 3DEP](https://www.usgs.gov/3d-elevation-program). Raw tiles are absent; the recorded feasibility audit says the host is outside the allowlist. No fetch was attempted. Do not call viable until the exact official tiles, CRS, coverage, licence and schema are audited. |

## Limitations and remaining work

1. **Lane definition is the immediate experiment blocker.** The task contains the instruction to stay in “the single method paragraph below,” but does not include an identifiable assigned-method paragraph. Do not select or switch to a hypothesis on the model's authority. A future prompt must identify one exact method paragraph to authorize the lane; then freeze the design before viewing any holdout result.
2. **Private labels and organizer scores are unavailable.** HOLDOUT-DTI predicts recovery of withheld catalogue segments, not expert truth or geothermal vents. A numerical leaderboard-score estimate is not defensible. Historical score/file attribution has no organizer receipts.
3. **Official data provenance is incomplete.** The 17 local rasters are owner-maintained mirrors; hash pins provide integrity, not organizer authentication. No DrivenData authentication was used. Do not request credentials in chat.
4. **The site cannot promise a current automatic leaderboard feed.** No scraping, polling, or refresh is implemented because the recorded Terms-of-Use review prohibits it without written consent or an authorized API. Use dated user-provided reports only, labelled as such.
5. **Submission-format ambiguity remains.** The existing locally-valid zero-outside encoding has no organizer acceptance receipt; the official wording retained in the repo describes null/NaN outside, while the rejected bytes and cause of the reported range error are not available. No file is approved.
6. **Novelty scope is bounded.** Current uniqueness screens use a pinned focus registry, not every artifact ever published by every GEMSDOE site. For any future candidate, distinguish “unique vs registry checked” from global uniqueness.
7. **Temporary cache.** Inputs and the 121-channel cache are git-ignored. This run restored them, but they will not be delivered in Git; rerun the documented restore/prepare commands in a clean workspace.

## Official and primary-source links for manual review

- [DrivenData competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — login access not present here; not fetched this review
- [Organizer reference implementation](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [DOE GDR #1391 / INGENIOUS](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [DrivenData Terms of Use](https://www.drivendata.org/termsofuse/) — local repo records a one-time read 2026-10-04; not refreshed this review

All non-GitHub official-site links above are retained for manual review but were **not freshly authenticated in this session**. No DrivenData page or leaderboard was contacted.
