# AI and data provenance disclosure

## AI assistance

This repository's implementation, research notes and tests were prepared by an autonomous AI agent
under the owner's standing brief. The agent did **not** submit anything to DrivenData. Quantitative
claims in the site are either official page observations, measurements reproduced from local bytes,
or explicitly classified as owner-reported/unverified. The initial experimental promotion claims
were withdrawn after review; see `evidence/first_pass_disposition.json`.

## Data provenance

- The competition rasters in `data/` were restored from public GitHub mirrors maintained by the
  repository owner and checked against a 17-file SHA-256 ledger. They are **not** organizer-authenticated
  downloads; no DrivenData receipt or authenticated data download record is available here.
- GDR 1391 and GDR 1682 official pages identify their own license/access terms. The BRIDGE GIS archive
  payload was **not** downloaded in this sandbox (TLS/HTTP 000), so no contents from that archive were
  used.
- USGS ComCat product availability was checked through the official FDSN web interface; a full event
  extract was not stored or used to build a submission.
- For the official third-party-data permission rule, consult the current competition rules and the
  original source license. No claim is made that every owner-mirror derivative or raster is licensed
  for redistribution.

## Human review / before upload

The primary one-click file is a D2.8 reference emission, **not a new model**. Its claimed 0.2600 score
is owner-reported, and the score-to-exact-file pairing is unverified. Confirm the competition portal
accepts the GeoTIFF, inspect it in a GIS, and verify the note and score attribution before relying on
it. No file in this repository is claimed to exceed the current official public leader.
