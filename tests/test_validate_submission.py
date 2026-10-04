import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_submission import audit


class SubmissionAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.template = self.root / "template.tif"
        self.good = self.root / "good.tif"
        self.profile = {
            "driver": "GTiff",
            "width": 5,
            "height": 4,
            "count": 1,
            "dtype": "float32",
            "crs": "EPSG:32611",
            "transform": Affine(100, 0, 100000, 0, -100, 4200000),
            "nodata": np.nan,
        }
        template_arr = np.zeros((4, 5), dtype=np.float32)
        template_arr[0, 0] = np.nan
        with rasterio.open(self.template, "w", **self.profile) as ds:
            ds.write(template_arr, 1)
        good_arr = np.zeros((4, 5), dtype=np.float32)
        good_arr[1, 2] = 1.0
        profile = dict(self.profile)
        profile["nodata"] = None
        with rasterio.open(self.good, "w", **profile) as ds:
            ds.write(good_arr, 1)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name, array, *, profile=None):
        path = self.root / name
        use_profile = dict(profile or self.profile)
        with rasterio.open(path, "w", **use_profile) as ds:
            ds.write(np.asarray(array, dtype=use_profile["dtype"]), 1)
        return path

    def test_valid_local_policy_grid_passes(self):
        result = audit(self.good, self.template)
        self.assertTrue(result["pass"])
        self.assertEqual(result["emitted_pixels"], 1)
        self.assertTrue(result["outside_footprint_all_zero"])

    def test_nan_outside_footprint_is_allowed_by_official_policy(self):
        arr = np.zeros((4, 5), dtype=np.float32)
        arr[0, 0] = np.nan
        path = self._write("nan-outside.tif", arr)
        result = audit(path, self.template)
        self.assertFalse(result["all_finite"])
        self.assertTrue(result["outside_is_null_or_zero"])
        self.assertTrue(result["pass"])
        strict = audit(path, self.template, strict_zero_outside=True)
        self.assertFalse(strict["pass"])

    def test_nonfinite_inside_footprint_fails(self):
        arr = np.zeros((4, 5), dtype=np.float32)
        arr[1, 1] = np.nan
        path = self._write("nan-inside.tif", arr)
        result = audit(path, self.template)
        self.assertFalse(result["in_range_0_1_footprint"])
        self.assertFalse(result["pass"])

    def test_infinite_outside_footprint_fails(self):
        arr = np.zeros((4, 5), dtype=np.float32)
        arr[0, 0] = np.inf
        path = self._write("infinite-outside.tif", arr)
        result = audit(path, self.template)
        self.assertFalse(result["outside_is_null_or_zero"])
        self.assertFalse(result["pass"])

    def test_out_of_range_prediction_fails(self):
        arr = np.zeros((4, 5), dtype=np.float32)
        arr[1, 1] = 1.01
        path = self._write("range.tif", arr)
        result = audit(path, self.template)
        self.assertFalse(result["in_range_0_1_whole_array"])
        self.assertFalse(result["pass"])

    def test_nonzero_outside_footprint_fails_project_policy(self):
        arr = np.zeros((4, 5), dtype=np.float32)
        arr[0, 0] = 0.5
        path = self._write("outside.tif", arr)
        result = audit(path, self.template)
        self.assertFalse(result["outside_footprint_all_zero"])
        self.assertFalse(result["pass"])

    def test_shape_mismatch_fails_without_boolean_index_crash(self):
        arr = np.zeros((3, 5), dtype=np.float32)
        profile = dict(self.profile)
        profile["height"] = 3
        path = self._write("wrong-shape.tif", arr, profile=profile)
        result = audit(path, self.template)
        self.assertFalse(result["shape_match"])
        self.assertFalse(result["pass"])

    def test_grid_mismatch_fails(self):
        arr = np.zeros((4, 5), dtype=np.float32)
        profile = dict(self.profile)
        profile["transform"] = Affine(200, 0, 100000, 0, -200, 4200000)
        path = self._write("wrong-grid.tif", arr, profile=profile)
        result = audit(path, self.template)
        self.assertFalse(result["resolution_match"])
        self.assertFalse(result["pass"])


if __name__ == "__main__":
    unittest.main()
