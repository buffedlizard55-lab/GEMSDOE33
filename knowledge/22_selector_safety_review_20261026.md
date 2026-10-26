# Selector safety and focus-site review — 2026-10-26

## Outcome

**No submission is approved. No new TIFF or holdout experiment was generated in this review.**
The prompt refers to a single assigned method paragraph but supplies none identifiable as this
session's exclusive lane. Choosing a lane from a new slate would violate that constraint. Existing
negative experiments must not be retuned. This is an explicit incomplete scientific objective,
not a claim to have delivered a new high-scoring submission.

The executive-summary page now lists all nine focus sites, exact registered historical filenames
(or explicitly missing pairing), reported values, an estimate column, and whether the file is new.
All leaderboard estimates are **not estimable**: no validated mapping from catalogue hide-and-recover
DTI to private organizer labels is available. Historical owner reports are not ORGANIZER-CONFIRMED.
The conflicting leader claims in the request remain unauthenticated.

## Scientific interpretation

The saved forensic evidence describes GEMSDOE32 B2 as deletion-only pruning of the H27-4 family.
Removing predictions with low credit can improve an asymmetric overlap objective; that is a
plausible explanation, not a demonstrated cause of the reported organizer result. The private
labels and a receipt linking exact bytes to the result are absent. It is not evidence that
another pruning threshold will improve discovery, and copying or lightly perturbing that file
would violate the novelty requirement. Fault recovery is also not direct detection of geothermal
vents: permeability, heat supply and fluid availability are additional unvalidated conditions.

## New research slate, before any implementation

These are **untested proposals**, ranked by qualitative expected DTI benefit versus cost, not
numerical improvements. A search of current `src/`, hypothesis registries and knowledge notes
found no implementation of these exact mechanisms; this does not establish uniqueness across
all remote sites. No new external data is required in principle, but only the grid template was
restored in this clean sandbox; the full feature cache remains unstaged here. Use the existing
pinned restore/cache pipeline, not a new private feature stack.

| Rank | Layers and physical signature | Missing-fault rationale; distinction from prior code | Non-fault mimic; cost and feasibility |
|---|---|---|---|
| 1 | Cached `tmi`, upward-continued TMI and `iso_grav_anom`: signed multiscale quadrature phase-congruency edges, with gravity/magnetic orientation agreement | An amplitude-invariant edge may recover weak buried displacement across different anomaly amplitudes. Unlike gradient-magnitude fusion, scarp line integrals and dip projection, uses local phase alignment across wavelengths, without catalogue distance as evidence. | Intrusive contacts and survey seams. Moderate CPU/design cost; cache-only concept, not yet canary- or novelty-tested. Highest *qualitative* priority, no DTI forecast. |
| 2 | Cached `depth_to_base_surf` and gravity anomaly: scale-space ridge bifurcation graph with persistent Y-junction topology | Buried splay junctions might survive smoothing where surface traces are absent. Unlike catalogue tip/stepover bridging and thermal least-cost graphs, the graph is built solely from subsurface ridge topology. | Intersecting basin margins and interpolation artifacts. Moderate cost; cache-only concept. Additional benefit relative to existing topology priors is uncertain; surface uniqueness could fail. |
| 3 | Cached `det_elev`, basement-depth and gravity fields: repeated signed cross-valley profile asymmetry along inferred drainage crossings | Coherent profile breaks across several independent valleys may indicate concealed cross-cutting displacement, rather than a lone scarp. Unlike maximum line-integral persistence, requires repeated profile-sign consistency in separate catchments. | Lithologic knickpoints and fan-head incision. High design cost; 100 m DEM resolution may make it infeasible. Raw 3DEP tiles would then be needed, and must not be called obtainable here: USGS host is outside the network allowlist. |

Required future test for an explicitly assigned lane: freeze feature definitions, split and matched
baseline before looking at outcomes; feature-alone canaries; whole-segment buffered visible-only
training; exact visible-fault masks; shared pooled triangular 300 m HOLDOUT-DTI evaluator at
alpha=0.2, beta=0.8; paired spatial confidence intervals; independent frozen confirmation; surface
and final-dot novelty checks. Stop at a duplicate, failed gate, three experiments or two hours.
No promotion to a real slot occurs in a campaign run.

## Tooling fixes

- The selector previously accepted a flipped summary eligibility flag despite explicit false
  gates in the same card. It now requires the complete shared gate schema, literal boolean true
  on every gate, and an empty failed-gate list. This checks internal evidence consistency;
  it cannot authenticate forged receipts or reproduce scientific evidence from arbitrary JSON.
- Confirmation DTI used for ranking must be a finite numeric value within [0,1]; booleans,
  missing values, NaN and infinity cannot win selection. Unknown legacy schemas remain blocked.
- A false diagnostic such as `outside_has_nan=false` is no longer listed as a format failure.
- Corrected S33's displayed note count to 79, and removed a stale claim that only LCHC passed
  both novelty gates.

## Evidence and access limits

Only the SHA-pinned owner-mirror sample was restored. It is used for grid and footprint, never
labels. A fresh saved-byte audit of the existing S33 zero-outside TIFF passes: single float32
band, EPSG:32611, 3730 rows × 3292 columns, exact template transform, no nonfinite values, range
[0,1]. See `evidence/review_27537860_format.json`. This is not a new raster, a new novelty audit,
or portal acceptance. Existing S33 screen/confirmation and novelty measurements remain historical
receipts, not reruns. The null/NaN versus zero-outside portal contract is unresolved.

The official organizer reference README was fetched through GitHub at commit
[`aebe92f7c8a990f0e3443451b7a825d9afd6336b`](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b).
It explicitly supports CPU-only environments; a GPU is faster, not an absolute training requirement.
The statement in the prompt that data placement is the *only* training blocker is not established:
the repository's generic detector training is still unsupported (IR-33-PREPARE-OOF-01).
Campaign-specific training is a separate path.

Official links retained for review, **not freshly verified here**:
[problem/format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[DOE GDR #1391](https://gdr.openei.org/submissions/1391),
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
[USGS 3DEP](https://www.usgs.gov/3d-elevation-program).
Non-GitHub official hosts are outside this sandbox's outbound allowlist. No DrivenData login,
polling or upload was performed. Slots and current leaderboard cannot be authenticated here.

## Three passes

1. Audited README/standing brief/operating rules, prior cards and selector; restored the pinned
   grid template; implemented selector consistency fixes and the executive comparison columns.
2. Adversarial tests exposed a local-vs-remote registry schema mismatch and boolean coercion of
   confirmation DTI. Fixed both. Added data-free gate-contract tests and saved-byte regression tests.
3. Rebuilt pages, ran the complete suite (**174 passed**, with restored template), compiled Python,
   refreshed the selector (**0 eligible of 12**), reran the S33 saved-byte audit and checked whitespace.
   Full input audit/cache rebuild was not run because other inputs are not restored. No scientific
   experiment budget or competition slot was consumed. The high-score/new-TIFF objective is blocked,
   not completed. Next session needs an explicit lane and staged pinned feature cache before testing.
