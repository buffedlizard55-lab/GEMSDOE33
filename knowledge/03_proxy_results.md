# Session-33 proxy validation results (2026-10-04 UTC)

**Protocol:** candidates are compared pairwise against C0, the h27-4-r1-solo-d2-8 control (40,199 dots;
owner-reported live score 0.2708), on two local proxies. The 0.2708 result is not an organizer receipt
archived here.

- **P1 — catalogue-hidden four-fold spatial block holdout.** Catalogue fault systems are grouped with a
  600 m buffer and split into 2×2 spatial folds. Each fold hides one quadrant's catalogue systems; its
  dilated systems are removed from the known mask so they remain scorable. Reported ΔDTI is candidate
  minus control.
- **P2 — SGMC off-catalogue.** Compare against pixels from the USGS State Geologic Map Compilation fault
  raster at 100 m, at least 300 m from the supplied catalogue. This independent compilation is a proxy,
  not the organizer's hidden truth; its content and vintage may differ from the competition target.
- **Gate:** paired P1 mean ΔDTI > 0, a strict majority of non-empty P1 folds positive, and measured P2
  ΔDTI ≥ −0.001. Missing fold or P2 results fail closed.

**Caveat:** the challenge target is described as expert-labelled new faults missing from the public
catalogue. P1 masks catalogue systems and P2 uses another compilation; neither is the hidden organizer
label set. Proxy improvement is not live-score evidence.

## Results (`evidence/holdout33.json`)

| Candidate | Dots | P1 mean ΔDTI | P1 fold ΔDTI | P2 ΔDTI | Gate |
|---|---:|---:|---|---:|---|
| C1 = C0 + 12 H38-1 corroborated Euler-cluster dots | 40,211 | −0.000004106 | [−0.000004002, −0.000005506, −0.000003245, −0.000003671] | +0.000022370 | FAIL (0/4 positive) |
| **C2 = C0 + 940 stepover relay-bridge dots** | **41,139** | **+0.000405159** | [+0.000344234, −0.000010034, +0.000277096, +0.001009339] | **+0.000283102** | **PASS** |
| C3 = rung-3.0 re-pack of C0 | 34,474 | −0.001233611 | [−0.000351414, −0.002182825, −0.000847949, −0.001552255] | −0.008137088 | FAIL |
| C4 = C3 + C1 | 34,486 | −0.001237814 | [−0.000355629, −0.002188395, −0.000851287, −0.001555947] | −0.008100640 | FAIL |
| C5 = C2 + C1 | 41,151 | +0.00040105 | 3/4 positive | +0.00030539 | PASS (C2 preferred for parsimony) |

## Decisions

1. **C2 is the current one-click candidate** because it passes both frozen proxies and is simpler than C5.
   It has 41,139 emitted dots, 940 above C0, and 12,811 qualifying tip pairs before raster/spacing/
   gravity/footprint gates. Current file:
   `docs/downloads/gems33-c2-stepover-relay-20261004-01f660dd8656.tif`.
   SHA-256 `7272633447365d7ec8a9c07972b48df92b071a1ecc5765cf14199c14dea4f0f7`. The standalone
   format audit is `evidence/format_check_c2_01f660dd8656.json`; it passes the repository's fail-closed
   grid/value policy. C2 has not been submitted and has no live score.
2. **C3/C4 fail locally.** Re-packing an already-pruned dot set loses proxy value. GEMSDOE28's H36-1
   result used a different input (the full H19-5 surface plus a flank prune); superficially similar
   operations can behave differently on different masks.
3. **C1 fails the current gate.** Its P1 changes are slightly negative in all four folds (0/4 positive)
   despite a small positive P2 change. The small magnitude is not a pass under the pre-registered strict
   majority rule.
4. C2's largest P1 gain is fold 3 (+0.001009); fold 1 is slightly negative. Do not over-read one fold.
   The promotion is a local proxy decision only; the human owner decides whether to use a slot after
   checking the exact artifact and current rules.

## Determinism fix

The initial C2 generator assigned randomized Python `hash(name)` fallbacks to non-integer fault IDs. That
could vary between processes and could collide. It was replaced by stable, collision-free integer IDs
based on the fault's `NUM`, or `NAME` when `NUM` is absent. The rebuild changed the result from 41,143 to
41,139 dots and changed the file hash. The prior TIFF was superseded and must not be distributed as
current. All values above describe the deterministic-ID rebuild.

## Bug found and fixed during the run

An earlier gate run reported exactly zero P1 for every candidate because the hidden fold's truth pixels
were removed by the known-catalogue mask. `src/gems33/holdout.py` now removes each hidden fold's dilated
systems from that mask before scoring. The values above are post-fix. The gate implementation is covered
by unit tests in `tests/test_holdout_gate.py`.
