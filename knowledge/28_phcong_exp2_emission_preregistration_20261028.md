# A33-R7 Exp 2 preregistration — emission-operator isolation (2026-10-28, before Exp 2 code)

Exp 1 (A33-R7-PHCONG, knowledge/27 slate SHA f322a3b0…) result, HOLDOUT-DTI
`gems-segment-pooled-v1`, 60,988 withheld: screen 0.169316 [0.162772, 0.175496],
confirmation 0.170588 [0.163996, 0.176581] — above recorded B1_regional
0.112418/0.115122. **Irregularity flagged (IR-33-CELF-RANDOM-01):** the paired
matched-random control *inside the CELF operator* scored 0.180992-equivalent
(candidate Δ −0.011098 [−0.016260, −0.006098], 0/4 folds). CELF greedily maximises
300 m triangular-kernel coverage — the same kernel as the DTI metric — so a
random surface under CELF becomes a uniform-coverage optimiser and is not a
neutral random control (in A33-R3, matched-random under `dot_thin` scored
0.073931). Exp 1's `promote` verdict therefore rests only on the recorded-B1
gates used by prior campaigns; it does **not** show the PHCONG surface adds value
over its own emission operator. No slot is authorised on Exp 1 alone.

## Exp 2 (this experiment, same lane/surface, emission isolated)
- Surface: identical frozen PHCONG surface (cached `.cache/phcong_*.npy`).
- Emission: `emission.dot_thin(eligible, 2.8, priority=surface, max_dots=budget)`
  (the historical d=2.8 dotted operator), fold budgets identical to Exp 1.
- Controls, paired on both splits: (a) dot_thin with random priority (true
  matched-random under this operator); (b) Exp-1 CELF dots are not recomputed —
  absolute DTI is compared across experiments on identical splits only as context.
- Gates for the Exp 2 artifact: screen AND confirmation DTI > recorded B1
  (0.112418/0.115122) with CI lower bound above it; paired Δ vs dot_thin-random
  strictly positive CI on screen; both uniqueness gates; canary (already passed
  in Exp 1, rerun for the record); saved-byte format audit.
- If Exp 2 passes, the Exp 2 (dot_thin) artifact supersedes Exp 1 as the
  candidate; if it fails, verdict is negative and Exp 1 is not promoted either.
  Budget used after this: 2/3 experiments. No retuning of the surface.
