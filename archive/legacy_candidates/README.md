# Legacy C0/C2 artifacts — audit only, not submission recommendations

These files were merged from the prior upstream project state. They are retained as research evidence,
not as additional downloads. Do not upload either file or interpret its name as score verification.

- `gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif` is the historical 40,199-dot H27-4-like
  control. The upstream filename said “scored,” but the GEMSDOE28 owner page says “NO GEMSDOE28
  SCORE”; no organizer receipt authenticates a score/file pairing.
- `gems33-c2-stepover-relay-20261004-01f660dd8656.tif` is a 41,139-dot research candidate. Its earlier
  P1 `+0.000405` result was withdrawn for leakage. The corrected conditional source-exclusion P1
  diagnostic is `−0.000722` (0/4 positive folds); P2 is `+0.000283` on the SGMC proxy. It is **not
  slot-cleared** because the fixed H19-5 surface was not re-derived per fold, the corrective test was
  not an independent preregistered confirmation, and the Qfaults mirror is not authenticated to the
  official archive. See `evidence/holdout33.json` and `registry/irregularities.json`.

Hashes and byte/grid receipts remain in `evidence/build_c0_89bf5b9a2fea.json`,
`evidence/build_c2_01f660dd8656.json`, and the corresponding format-check JSON files. The project site
recommends only the D2.8 owner-mirror reference package; no C0/C2 score is claimed.
