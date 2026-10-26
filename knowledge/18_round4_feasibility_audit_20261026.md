# Round-4 continuation: feasibility audit and stop decision (2026-10-26)

## Executive decision

**No new candidate was evaluated and no new TIFF was generated in this continuation.** The submission selector reports no eligible file. The latest pre-existing candidate, A33-R3-LLC, remains a format-valid research download and is **NOT OK TO SUBMIT** because its frozen confirmation did not beat its fold-safe comparator. This review used no DrivenData access, did not choose a weekly slot, and makes no score projection.

The user-provided protocol says to remain in one explicitly assigned method lane. The current request did not identify a single method paragraph, so no candidate implementation was authorized by that protocol. Separately, inspection of the prior Round-4 shortlist found that its top two concepts are not ready to validate from the files actually staged. We restored inputs and rebuilt the cache, then stopped at feasibility triage rather than manufacture a score or a TIFF.

## Completed data preparation and integrity checks

- `python scripts/restore_data.py --group all` restored the 17 input records from the registered public GitHub owner mirrors; all 17 passed the local size/SHA-256 pin audit. The resulting `evidence/input_grid_audit.json` records the audit.
- Provenance limitation: these are owner-published mirrors. Hash agreement authenticates equality to the manifest bytes, **not** original DrivenData delivery, official provenance, or license.
- `.venv/bin/python scripts/prepare_data.py --skip-detector` rebuilt the shared 121-channel cache from the 19-band mirror and the pinned 100 m auxiliary rasters. Detector fitting was deliberately skipped.
- The cache and restored data are git-ignored, not committed, and not part of the static Pages site. No independent labels or organizer truth were obtained.
- `.venv/bin/python -m pytest -q`: **148 passed**. This is software regression testing, not scientific validation.
- `.venv/bin/python scripts/select_submission.py --date 20261026`: **NO RASTER IS OK TO SUBMIT**, 0 eligible of 11 recorded run cards.
- A saved-byte strict-zero-outside audit was rerun on the *existing* A33-R3-LLC file against the restored template. It passed the local file-format checks (one float32 band, EPSG:32611, 3730×3292, 100 m transform, finite values [0,1], zero outside). This does not change the negative scientific verdict or establish portal acceptance.

## Ranked Round-4 hypotheses (qualitative priority; no numeric DTI estimate)

These are candidate research ideas, not scores. Expected gain is qualitative. A HOLDOUT-DTI value cannot be supplied until an authorized, fold-safe experiment is run. `A33-R4-COULOMB` and `CURVTRACE` are retained as ideas but are **not viable with the present local payloads**.

| Rank | Candidate; layers and physical signature | Why it could detect a fault missing from the catalogue; distinction from prior work | Named mimic; cost; data/source viability |
|---|---|---|---|
| 1 (conceptual) | **A33-R4-COULOMB:** Quaternary-fault geometry plus slip rate/sense/dip, computing elastic half-space Coulomb stress-change lobes around mapped segments. | Positive stress lobes may indicate blind synthetic/antithetic splays beyond the mapped trace. Distinct from geometric tip/stepover halos and the prior Mohr-slip/dilation detector because it requires spatial dislocation geometry and elastic stress transfer. | **Mimics:** intrusive/caldera margins and spatial frictional heterogeneity. **Moderate cost. Blocked:** the local `gdr_qfaults_traces.csv` has 1,126 rows with UTM centroid, slip rate, recency, dip direction and slip sense but no vertices or strike; the companion `qfaults_v2_in_footprint.json` has 32,589 vertices with x range −298,965…86,070 and y 1,550,976…2,040,013, while its metadata bbox is geographic lon/lat and supplies no geometry CRS. Those coordinates do not align with the EPSG:32611 template bounds (x 243,350…572,550; y 4,135,550…4,508,550) or the CSV centroid ranges. The exact official source/version correspondence is also unresolved. No safe trace geometry is available for a fold-safe ΔCFS field. Official listing to review: [DOE GDR #1391](https://gdr.openei.org/submissions/1391). |
| 2 (conceptual) | **A33-R4-CURVTRACE:** raw 1 m USGS 3DEP DEM, multi-azimuth hillshade/profile curvature, and orientation-tracked scarp continuity over ≥1.5 km. | Could recover low-relief subpixel scarps that a 100 m classifier cannot resolve; distinct in scale from pixel HGB but conceptually adjacent to the prior 100 m line-localized experiment. | **Mimics:** Lake Lahontan beaches, fluvial terrace risers, roads/canal berms. **High cost. Blocked:** local LiDAR descriptor raster is 12-band, 100 m grid, made from 2 m processing; it cannot recover raw 1 m morphology. Raw 3DEP tiles are not in the 17 pinned inputs. Official free source: [USGS 3DEP](https://www.usgs.gov/3d-elevation-program); tile service host was not obtainable under this session's outbound allowlist, and no tile download was attempted. |
| 3 (highest cache-only candidate, not selected) | **A33-R4-PFRT:** `depth_to_base_surf`, `iso_grav_anom_hg`, and directional updip projection of basement-edge evidence by a bounded listric-dip kernel. | Targets blind listric faults whose surface/piedmont expression lies updip from a basement density break; different from unshifted gradient or pixel-level regional classification. | **Mimics:** prograding fan toes and buried pediments. **Low–moderate cost; local stack present.** High duplicate risk because gravity-gradient surfaces resemble prior regional classifiers. Official context: [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). It was not run: no single lane was assigned in the request and the protocol prohibits silently switching lanes. |
| 4 (not untried) | **A33-R4-HMDT:** cached conductivity, upward-continued TMI, gravity gradient and dilatation; signed cross-gradient magnetic/conductivity doublet. | A hydrothermal alteration doublet might locate concealed fault conduits; differs from unsigned rank averaging in CSHT. | **Mimics:** saline playa/evaporite lenses and nonmagnetic lacustrine tuff. **Low–moderate cost.** An HMDT TIFF exists from a parallel session, but no reproducible fold-safe runner/run card is retained. Treating its final bytes as holdout-safe would be invalid. Therefore it is not a fresh untried idea and was not scored. Source links: [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [DOE GDR #1391](https://gdr.openei.org/submissions/1391). |
| 5 (blocked) | **A33-R4-PALEOTEMP:** DOE 2 m temperature-probe and paleosinter/tufa inventory joined with cached conductivity and geophysical edges. | Could expose dormant/relict conduits absent from active spring/vent seed layers; distinct from the active thermal/well site features already tried. | **Mimics:** paleochannel thermal outflow distal from a feeder fault. **Moderate cost. Blocked:** exact probe/sinter payload is not among pinned inputs; the source listing is [DOE GDR #1391](https://gdr.openei.org/submissions/1391), but the named payload has not been obtained or schema/coverage/license audited in this checkout. Do not call it available based on a listing alone. |

## Why no candidate holdout was run

1. **Lane ambiguity:** the parallel-run rule names one assigned method paragraph, but none is identifiable in the new request. We did not infer permission to switch to a competing method from the ranked slate.
2. **Rank 1 is not implementable as specified:** the staged Quaternary fault attributes lack trace strike/vertex geometry; the companion vector file has no usable CRS declaration and its numeric coordinates are outside the target grid. Approximating it with centroids would not be Okada/Coulomb stress transfer and could create arbitrary artifacts.
3. **Rank 2 needs new data:** a 100 m aggregate cannot be upsampled to claim 1 m trace evidence. Raw USGS tiles are not staged.
4. **No valid score proxy for discovery:** even a future HOLDOUT-DTI measures recovery of withheld mapped-catalogue segments, not private organizer expert labels or geothermal vents. A candidate aimed at genuinely unmapped faults can be penalized by the catalogue proxy.

The user's cap is three experiments/two hours. This triage used zero holdout experiments and zero competition slots. No experiments remain spent for a future authorized slate; the budget is not a license to tune after observing holdout results.

## Answer on GEMSDOE32 B2 and the nine focus sites

The repository's byte-level forensic record states that GEMSDOE32 B2 is the exact 37,654-dot result of removing 2,545 additional 1–2 px catalogue-flank dots from the 40,199-dot GEMSDOE28/31 H27-4 emission. This establishes a raster-set relationship, not a causal explanation for a private organizer score. DTI's asymmetric false-positive/false-negative costs make a reduction in low-credit false-positive mass a plausible explanation, but it is not proven without a matched score receipt and private truth. The reported 0.2778 remains **USER/OWNER-REPORTED, NOT ORGANIZER-CONFIRMED**.

No new candidate has been shown to beat it. The highest-focus-site table is in README §1; every numeric competition score there remains owner-reported. The two purported current-leader values 0.3195 and 0.4413 conflict and were not refreshed or authenticated. There is no honest numerical estimate of competition score for the unrun proposals.

## Irregularity: reported portal range error

Some old text in a local receipt described a zero-outside file as "immune" to the range error. That is not supported: the rejected bytes and organizer diagnostic were not preserved. A local `[0,1]` whole-array check only shows that local values are in range; it does not prove portal acceptance or that NaN caused the reported rejection. The recorded official-format wording specifies null/NaN outside, so zero-outside semantics remain unresolved. This is now explicitly flagged as `IR-33-PORTAL-RANGE-CLAIM-01`; current public guidance does not promise that either encoding is accepted.

## Official links for review

- [Competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem and submission metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Organizer reference implementation](https://github.com/drivendataorg/gems-prize-reference-solution)
- [DOE INGENIOUS GDR #1391](https://gdr.openei.org/submissions/1391)
- [USGS GeoDAWN data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [EPSG:32611](https://epsg.io/32611)

These links are listed for review; this session did not newly download external GDR/USGS payloads or freshly authenticate the competition portal.

## Three-pass review record

1. **Pass 1 — implementation:** restored and pinned the mirror inputs, built the shared cache, created the Round-4 source feasibility note/run card, updated the README and generated site to put current download/submission status first, and added a five-candidate table with official source links and explicit availability.
2. **Pass 2 — adversarial review:** tests exposed stale static-site claims that H33-6 or G33-DPPS was the newest item, stale 2025 status in site headers, a claim that all past files were already submitted, a broken Round-4 card link, and a focus-site table missing its “submit now?” cell. These were corrected. The obsolete G33-HA “current unique submission” hero was removed; that older research artifact is explicitly archived and its then-12-raster uniqueness audit is not represented as current.
3. **Pass 3 — final verification:** rebuilt the static pages, ran the repository check script, re-ran the selector and strict-zero-outside validator on the existing A33-R3-LLC bytes, and ran the full test suite: **148 passed**. `git diff --check` passed. Final selector result: **0 eligible of 11 recorded run cards**. No new experiment, TIF, or competition slot was used.
