# H33-F named analog-field transfer — historical screen result

> **Superseded as the featured-candidate record.** H33-F is a distinct exploratory artifact that failed its local proxy gates and is not slot-approved. H33-6 was evaluated in a later, separately frozen round; its failed result is in `knowledge/08_h33_6_result_20261004.md`. The D2.8 file remains a separate historical owner-mirror reference.

**Date:** 2026-10-04. **Evidence class:** `[MEASURED]` local proxies from owner-mirror rasters;
`[OFFICIAL]` source pages for field coordinates; **not** an organizer score.

## Why 0.2708 is not the target we can copy

The brief asked why GEMSDOE28 `h27-4-r1-solo-d2-8` was reported at 0.2708. The GEMSDOE28
public page itself says **NO GEMSDOE28 SCORE** and labels artifacts unscored
([site](https://buffedlizard55-lab.github.io/GEMSDOE28/)). No organizer receipt in this
repository pairs 0.2708 with those bytes. The owner-reported lineage (H19-5 solid → dotted
d=1.5 → d=2.8 → 1-px catalogue-flank prune) is a packing/pruning story on an existing
detector surface, not analog-field transfer.

Copying that emission cannot be this session's unique submission.

## Analog fields are inside the GeoDAWN footprint

Official centroids convert onto the owner-mirror EPSG:32611 template:

| Field | Official source | lon, lat | row, col (measured) |
|---|---|---|---|
| Dixie Valley | [OpenEI](https://openei.org/wiki/Dixie_Valley_Geothermal_Area) 39°58'3.59\" N, 117°51'18.27\" W | −117.855075, 39.967664 | 840.3, 1836.3 |
| Brady Hot Springs | [USGS MRDS 10221999](https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10221999) | −119.01319, 39.7866 | 1025.4, 842.6 |
| Desert Peak II | [OpenEI facility](https://openei.org/wiki/Desert_Peak_II_Geothermal_Facility) | −118.953781, 39.753855 | 1062.9, 892.7 |

GDR 1391 well/spring names in the owner-mirror CSV hit all three fields (Dixie 69 unique
cells, Brady 136, Desert Peak 28). 12 km well buffers ∪ 15 km centroid buffers give
**527,997** analog cells and **7,848** public-catalogue pixels inside them.

GDR [1682](https://gdr.openei.org/submissions/1682) BRIDGE GIS (3.79 MB) and GDR
[207](https://gdr.openei.org/submissions/207) `GIS_Faults.zip` (15.1 MB) could not be
downloaded (`curl: (35) SSL_ERROR_SYSCALL`). Independent field-verified extra traces were
**not** used.

## Ben-David (2010) and the measured shift

Paper: [Machine Learning 79:151–175](https://link.springer.com/article/10.1007/s10994-009-5152-4).
Theorem 2 needs source error, empirical `HΔH`, a complexity term, and **λ** (joint-label
error of the best shared hypothesis).

An exploratory HistGradientBoosting domain discriminator on shared GeoDAWN+LiDAR layers,
trained/tested on 20 km even/odd spatial blocks (40,000 cells/domain), had held-out AUC
**0.917** and error **0.172**. That is **not** `d_HΔH`. It does show the analog fields are
easily distinguished from the rest of the footprint, so a large shift is present. λ cannot
be estimated because source labels are the same USGS/INGENIOUS catalogue, not an independent
analog-only map. **Transfer is not licensed as a bound.**

## Unique emission and proxy holdout

Builder: `scripts/run_analog_campaign.py`. Classifier trained on analogue-field catalogue
vs analogue background; predicted on the full footprint; off-catalogue analog-score ridges
Poisson-thinned at d=2.8 to 44,090 dots. SHA-256 of the NaN-outside GeoTIFF differs from
the historical D2.8 file.

Fold-safe P1 (catalogue systems, 600 m buffer, H19-5 not re-derived per fold — same
limitation as C2):

| Fold | ΔDTI vs rebuilt C0 |
|---:|---:|
| 0 | −0.067172 |
| 1 | −0.129228 |
| 2 | −0.075281 |
| 3 | −0.100608 |
| mean | **−0.093072** (0/4 positive) |

P2 SGMC off-catalogue: candidate DTI below rebuilt C0 by **−0.016163**; above matched-N
random by **+0.001234** (barely). **NOT_SLOT_CLEARED.**

In-sample training AUC 0.986 with P1 recall ~0.01–0.05 on held-out catalogue is
overfitting to analog-field appearance plus the measured domain shift.

## What this means for P(Win)

A unique, format-checked H33-F GeoTIFF was generated, but it lost the catalogue-hidden proxy by a wide margin and did not beat C0 on SGMC off-catalogue. It is a separate research artifact, not the current featured file and not slot-cleared. **Do not spend the slot.** The current top-level package is the historical D2.8 reference, while H33-6 has its own failed, separate research TIFF. The H33-F round had unrun follow-up leads: H33-G conductivity × gravity edge, H33-H dilatation × magnetic edge, H33-I vent alignments, and H33-J LiDAR upface residual. They are historical unvetted leads, not the current ranked slate; see the separately frozen H33-6 slate and result for current research.
