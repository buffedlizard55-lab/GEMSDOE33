# `data/` — local inputs (git-ignored)

`data/` is not included in Git. Restore the 17 SHA-256-pinned inputs with:

```bash
python scripts/restore_data.py --group all
python scripts/prepare_data.py
```

See `registry/owner_mirror_input_pins.json` for the 17 audited owner-mirror files, mirror paths, expected byte counts and SHA-256 digests. `registry/data_manifest.json` is the separate upstream C0/C2 restore manifest; do not confuse its candidate-specific inputs with this reference package's pins.

## Provenance warning

All 17 competition / external rasters are owner-published GitHub mirrors. A matching SHA-256 proves
the fetched file matches the registered mirror; it does **not** authenticate that the bytes came
from DrivenData or prove their licence. The official GDR/USGS source pages are linked separately in
`registry/sources.json`. The owner-mirror sample raster is known to be non-blank: its 60,988 values
of 1.0 match the positive set of `labels.tif`, so it is used only for the exact template grid and
finite-footprint mask, never as a fault-absence label.
