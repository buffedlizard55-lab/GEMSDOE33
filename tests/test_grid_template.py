"""The sample TIFF is a footprint/grid template, never a source of truth."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gems33.grid import load_template  # noqa: E402


class TemplateValueTests(unittest.TestCase):
    def test_template_values_do_not_change_the_returned_footprint(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp) / "a.tif", Path(temp) / "b.tif"]
            profile = {
                "driver": "GTiff",
                "width": 4,
                "height": 3,
                "count": 1,
                "dtype": "float32",
                "crs": "EPSG:32611",
                "transform": Affine(100, 0, 1000, 0, -100, 4000),
                "nodata": np.nan,
            }
            first = np.array([[0, 1, np.nan, 0], [1, 0, 1, np.nan], [0, 0, 1, 1]], dtype=np.float32)
            second = np.array([[9, -4, np.nan, 6], [10, 20, 30, np.nan], [7, 8, 9, 10]], dtype=np.float32)
            for path, array in zip(paths, (first, second)):
                with rasterio.open(path, "w", **profile) as ds:
                    ds.write(array, 1)
            mask_a, grid_a = load_template(paths[0])
            mask_b, grid_b = load_template(paths[1])
            np.testing.assert_array_equal(mask_a, np.isfinite(first))
            np.testing.assert_array_equal(mask_b, mask_a)
            self.assertEqual(grid_a, grid_b)


if __name__ == "__main__":
    unittest.main()
