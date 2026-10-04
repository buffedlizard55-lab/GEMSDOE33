"""Unit tests for fold-specific catalogue and source-vector masking."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from affine import Affine
from scipy.ndimage import distance_transform_edt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems33.candidates import exclude_source_fids_near_mask, rebuild_c0_from_known  # noqa: E402
from gems33.thinning import dot_thin  # noqa: E402


class DotThinTests(unittest.TestCase):
    def test_is_deterministic_subset_with_minimum_spacing(self):
        mask = np.zeros((32, 32), dtype=bool)
        mask[10, 3:29] = True
        mask[11, 6:26] = True
        first = dot_thin(mask, 2.8)
        second = dot_thin(mask, 2.8)
        self.assertTrue(np.array_equal(first, second))
        self.assertTrue(np.all(~first | mask))
        rows, cols = np.nonzero(first)
        if len(rows) > 1:
            for i in range(len(rows)):
                d2 = (rows[i + 1:] - rows[i]) ** 2 + (cols[i + 1:] - cols[i]) ** 2
                self.assertTrue(np.all(d2 >= 2.8 ** 2))

    def test_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            dot_thin(np.zeros((2, 2, 2)), 2.8)
        with self.assertRaises(ValueError):
            dot_thin(np.zeros((2, 2)), float("nan"))


class FoldSpecificBaseTests(unittest.TestCase):
    def test_catalogue_mask_is_recomputed_for_each_fold(self):
        raw = np.zeros((40, 40), dtype=bool)
        raw[20, 4:36] = True
        known = np.zeros_like(raw)
        known[20, 20] = True
        base, report = rebuild_c0_from_known(known, raw, min_dist_px=2.8, prune_px=1.0)
        self.assertEqual(int(base.sum()), report["dots_after_flank_prune"])
        self.assertFalse((base.astype(bool) & (distance_transform_edt(~known) <= 1.0)).any())
        self.assertTrue(np.all(~base.astype(bool) | raw))


class SourceExclusionTests(unittest.TestCase):
    def setUp(self):
        self.transform = Affine(100.0, 0.0, 0.0, 0.0, -100.0, 4000.0)
        self.target = np.zeros((40, 40), dtype=bool)
        self.target[20, 20] = True

    def test_excludes_whole_source_system_within_buffer_plus_guard(self):
        # (x,y) uses the same EPSG:32611 metre space as the synthetic grid.
        segments = [
            {"fid": 1, "pts": np.array([[1900.0, 2000.0], [2200.0, 2000.0]])},
            {"fid": 1, "pts": np.array([[1000.0, 1000.0], [1200.0, 1000.0]])},
            {"fid": 2, "pts": np.array([[1000.0, 1000.0], [1200.0, 1000.0]])},
        ]
        excluded, report = exclude_source_fids_near_mask(
            segments, self.target, self.transform, buffer_px=2, guard_px=1, sample_step_m=25.0
        )
        self.assertEqual(excluded, {1})
        self.assertEqual(report["source_fids_excluded"], 1)
        self.assertEqual(report["source_segments_excluded"], 2)
        self.assertEqual(report["source_exclusion_radius_px"], 3)
        self.assertEqual(report["source_exclusion_shape"], "square/Chebyshev")

    def test_no_target_excludes_nothing(self):
        excluded, report = exclude_source_fids_near_mask(
            [{"fid": 1, "pts": np.array([[1900.0, 2000.0], [2200.0, 2000.0]])}],
            np.zeros_like(self.target), self.transform,
        )
        self.assertEqual(excluded, set())
        self.assertEqual(report["source_fids_excluded"], 0)

    def test_rejects_rotated_grid(self):
        rotated = Affine(100.0, 1.0, 0.0, 0.0, -100.0, 4000.0)
        with self.assertRaises(ValueError):
            exclude_source_fids_near_mask([], self.target, rotated)


if __name__ == "__main__":
    unittest.main()
