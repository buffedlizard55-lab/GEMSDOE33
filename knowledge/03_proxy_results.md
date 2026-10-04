# Session-33 proxy validation results (2026-10-04)

**Protocol (frozen before results were inspected):** candidates are compared pairwise
against the scored C0 control (`h27-4-r1-solo-d2-8`, 40,199 dots, owner-reported live
0.2708) on two local proxies:

* **P1 — catalogue-hidden 4-fold spatial block holdout.** Catalogue fault systems are
  grouped with a 600 m buffer and split into 4 quadrant folds. Each fold hides one
  quadrant's systems (removed from the known-mask along with the buffer) and scores DTI
  on the hidden pixels only. Paired ΔDTI, candidate minus control.
* **P2 — SGMC off-catalogue.** DTI against USGS State Geologic Map Compilation faults
  rasterised at 100 m that lie ≥300 m from the supplied catalogue (83,593 → truth
  pixels after masking). An independent compilation — the best local stand-in for
  "faults the catalogue does not list".
* **Gate:** P1 mean ΔDTI > 0 AND majority of folds positive AND P2 not worse than −0.001.

**Caveats:** proxies are NOT competition scores. The hidden test set is expert-labelled
NEW faults; the catalogue is only a structural stand-in. The SGMC proxy is closer in
spirit (independent, non-Quaternary-scope compilation) but coarser in intent.

## Results (`evidence/holdout33.json`)

| Candidate | Dots | P1 mean ΔDTI | P1 folds (ΔDTI) | P2 ΔDTI | Gate |
|---|---:|---:|---|---:|---|
| C1 = C0 + 12 H38-1 corroborated Euler-cluster dots | 40,211 | −0.00000 | [−0.0, −1e-05, −0.0, −0.0] | +0.00002 | FAIL (neutral) |
| **C2 = C0 + 944 stepover relay-bridge dots** | **41,143** | **+0.00043** | [+0.00034, −0.00001, +0.00037, +0.00101] | **+0.00028** | **PASS** |
| C3 = rung-3.0 re-pack of C0 | 34,474 | −0.00123 | [−0.00035, −0.00218, −0.00085, −0.00155] | −0.00814 | FAIL |
| C4 = C3 + C1 | 34,486 | −0.00124 | same pattern | −0.00810 | FAIL |
| C5 = C2 + C1 | 41,155 | +0.00042 | [+0.00034, −0.00002, +0.00037, +0.00100] | +0.00030 | PASS |

## Decisions

1. **C2 promoted** to the one-click slot (parsimony over C5: identical gate, 12 fewer
   dots, P1 marginally higher). Artifact:
   `docs/downloads/gems33-c2-stepover-relay-20261004-eb6bcf02361f.tif`,
   content id `eb6bcf02361f`, format audit PASS (finite [0,1] whole array).
2. **C3/C4 refuted.** Re-packing an already-pruned dot set is net-negative locally even
   though GEMSDOE28's H36-1 (re-pack of the full H19-5 surface + flank prune) passed its
   own LOSFO gate. The two operations look alike but act on different inputs; the local
   measurement governs.
3. **C1 neutral.** Only 12 of 140 published H38-1 clusters sit ≤300 m from the H19-5
   ridge in our grid alignment (127 far, 1 too close); the marginal effect is below
   proxy resolution. The corroborated-dot concept remains viable via H33-B/H33-A where
   denser corroborators exist.
4. Bridge-dot geology note: 12,851 qualifying tip pairs existed region-wide; the gravity
   edge + spacing + footprint gates kept 944 dots. C2's positive P1 comes mostly from
   fold 3 (+0.00101) — a single fold should not be over-read; slot use is ultimately the
   owner's decision, and this repo's rule is: never spend a slot on a file that has not
   beaten the current holdout best — C2 beat C0 on both proxies, C0 being the scored best.

## Bug found and fixed during the run

First gate run reported exactly 0.00000 P1 for every candidate because the hidden fold
truth was itself inside the `known` catalogue mask (truth zeroed after masking). Fix:
remove each hidden fold's dilated systems from the known-mask before scoring
(`src/gems33/holdout.py`). All numbers above are post-fix.
