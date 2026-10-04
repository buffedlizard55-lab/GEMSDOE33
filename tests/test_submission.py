"""Local GeoTIFF writer/validator contract on a synthetic official-sized grid."""
from __future__ import annotations

import numpy as np
from affine import Affine
from rasterio.crs import CRS

from gemsdoe33 import grid, submission


HEIGHT, WIDTH = 3730, 3292
TRANSFORM = Affine(100, 0, 243350, 0, -100, 4508550)
CRS_UTM11 = CRS.from_epsg(32611)


def test_package_writes_both_outside_variants_and_note(tmp_path, monkeypatch):
    footprint = np.ones((HEIGHT, WIDTH), dtype=bool)
    footprint[-1, -1] = False
    profile = {
        "driver": "GTiff", "height": HEIGHT, "width": WIDTH, "count": 1,
        "dtype": "float32", "crs": CRS_UTM11, "transform": TRANSFORM,
        "nodata": np.nan, "compress": "deflate", "predictor": 3,
    }
    monkeypatch.setattr(grid, "template_footprint", lambda: footprint)
    monkeypatch.setattr(grid, "template_profile", lambda: profile.copy())
    monkeypatch.setattr(grid, "template_georef", lambda: (TRANSFORM, WIDTH, HEIGHT, CRS_UTM11))

    mask = np.zeros_like(footprint)
    mask[100, 100] = True
    mask[100, 101] = True
    mask[100, 102] = True
    receipt = submission.build_package(
        mask, None, "synthetic-test", tmp_path,
        "test note {cid}",
    )

    assert receipt["all_checks_pass"]
    assert receipt["note_chars"] <= submission.MAX_NOTE
    assert receipt["emitted_pixels"] == 3
    assert receipt["nan"]["checks"]["outside_is_null_or_zero"]
    assert receipt["zeros"]["checks"]["outside_is_null_or_zero"]
    assert receipt["nan"]["sha256"] != receipt["zeros"]["sha256"]
    assert receipt["zip_nan"]["members"] == 1
    assert receipt["zip_zeros"]["members"] == 1
