# GEMSDOE33 proxy results and the P1 leakage audit (2026-10-04 UTC)

## Decision

**No candidate is cleared for a submission slot.** The initial C1–C5 report numerically marked C2 as a P1/P2 pass, but that P1 result is withdrawn. The candidate and its control were constructed with information from the full catalogue, and C2 used the same Qfaults source geometries for systems later called “held out.” The corrected source-exclusion diagnostic reverses C2's P1 sign. P2 remains a small positive independent-compilation proxy delta; that cannot override P1 or be called a competition score.

## What changed

The official [GEMS problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) describes an expert-labelled target of new faults. A catalogue-hidden test is therefore only meaningful if the hidden geometry is absent not just from the metric mask, but also from candidate construction and any catalogue-derived inputs. The pinned sibling GEMSDOE28 [LOSFO code](https://github.com/buffedlizard55-lab/GEMSDOE28/blob/33cc5942220f1440531d7184889c5c6f5d2f0a3e/src/gems27/losfo.py) explicitly warns that Qfaults/SGMC-derived layers must be excluded or audited because those features were not re-derived with held-out systems removed.

The old runner hid catalogue labels only when scoring. It did **not**:

1. rebuild the H27-4 base after hiding a fold (its one-pixel flank prune used the full label raster);
2. pass a fold-visible catalogue mask to C2's catalogue-distance filter; or
3. remove held-out fault systems from the Qfaults vectors that create C2's bridge tips.

That is target/source leakage, not merely an imprecise metric. The old P1 values are preserved in [`evidence/holdout33_legacy_catalogue_only.json`](../evidence/holdout33_legacy_catalogue_only.json), with an explicit withdrawal annotation. **All old C1–C5 P1 deltas are invalid for slot decisions.** Their P2 numbers remain separate SGMC proxy measurements, not competition scores.

## Corrected conditional diagnostic

[`scripts/run_holdout33_source_audit.py`](../scripts/run_holdout33_source_audit.py) now:

- rebuilds the H27-4 control from the fixed H19-5 ridge plus only each fold's visible catalogue labels;
- reproduces the full-label 40,199-dot H27-4 raster exactly when the full catalogue is visible;
- excludes an entire Qfaults source-system ID if any sampled part of its polyline enters the held-out system's 600 m square buffer plus a one-pixel (100 m) raster guard;
- samples source polylines at at most 50 m intervals before candidate construction; and
- uses the fold-visible catalogue mask for C2's catalogue-distance suppression.

| Spatial fold | Hidden truth px | Fold C0 dots | Fold C2 dots | Qfault source IDs excluded | C2 − C0 ΔDTI |
|---:|---:|---:|---:|---:|---:|
| 0 | 13,293 | 40,983 | 41,699 | 40 | −0.0007242642 |
| 1 | 12,755 | 41,269 | 42,063 | 40 | −0.0011430116 |
| 2 | 14,117 | 40,821 | 41,600 | 40 | −0.0006367379 |
| 3 | 20,823 | 41,614 | 41,968 | 51 | −0.0003840016 |
| **Mean** | — | — | — | — | **−0.0007220038 (0/4 positive)** |

For retained Qfaults IDs, the nearest sampled source geometry was 18.97–29.00 pixels (about 1.9–2.9 km) from the hidden fold; exclusion covered a 6-pixel (600 m) square buffer plus a one-pixel raster guard. C2 adds 354–794 bridge dots per fold, but the paired DTI is lower than the fold-rebuilt C0 in every fold. More specifically, across folds it adds 2,643 dots and no incremental TPw; the increase in FPw is exactly 2,643. None of the added dots earned true-positive kernel weight in the held-out systems under this diagnostic.

### P2 remains a separate proxy

Against the pinned SGMC fault raster at least 300 m from the full supplied catalogue, the full-data C2 file has 41,139 dots and DTI `0.0968980018` versus `0.0966149000` for C0: **ΔDTI `+0.0002831018`**. This is an independent compilation proxy with different scope/vintage—not the organizers' private expert labels and not a contest score.

### Status and remaining caveat

- The corrected numerical P1/P2 gate **fails** because P1 is negative and has 0/4 positive folds.
- **No slot is cleared**, even though the exact full-data C2 GeoTIFF passes the local format audit.
- The fixed H19-5 ridge raster is not regenerated per fold. Its upstream production/training code is not in this checkout, so the corrected run remains a conditional diagnostic rather than a complete leakage-free confirmation.
- This corrective run was prompted by the earlier result and is not an independent preregistered confirmation. A fresh candidate needs a documented upstream pipeline, fold/source-safe feature generation, and a preregistered validation before reconsidering a slot.
- C2's vector input is a pinned community mirror of [GDR #1391](https://gdr.openei.org/submissions/1391); the official archive version is not byte-authenticated against the mirror. The result applies only to the pinned mirror.

## Other variants and preserved evidence

The old run's C1/C3/C4/C5 P1 differences must not be used as valid generalization results. Their P2 values in the legacy report may be read only as SGMC proxy comparisons. C2 remains available as a **research artifact**, not as a submission recommendation:

- TIFF: [`docs/downloads/gems33-c2-stepover-relay-20261004-01f660dd8656.tif`](../docs/downloads/gems33-c2-stepover-relay-20261004-01f660dd8656.tif)
- SHA-256: `7272633447365d7ec8a9c07972b48df92b071a1ecc5765cf14199c14dea4f0f7`
- Local format report: [`evidence/format_check_c2_01f660dd8656.json`](../evidence/format_check_c2_01f660dd8656.json)
- Corrected diagnostic: [`evidence/holdout33.json`](../evidence/holdout33.json)
- Withdrawn legacy report: [`evidence/holdout33_legacy_catalogue_only.json`](../evidence/holdout33_legacy_catalogue_only.json)

All proxy values are local diagnostics. They are not DrivenData scores, private-label results, or a validated score projection.
