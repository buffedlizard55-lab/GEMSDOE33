from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gems33.hypotheses import edge_consensus_score, reallocate_edge_budget  # noqa: E402


class H336EdgeScoreTests(unittest.TestCase):
    def setUp(self):
        self.height = 81
        self.width = 81
        yy, xx = np.mgrid[:self.height, :self.width]
        self.footprint = np.ones((self.height, self.width), dtype=bool)
        line_x = xx >= 40
        line_y = yy >= 40
        self.layers = {
            "tmi": line_x.astype(np.float32) + (0.002 * (xx - 40) ** 2).astype(np.float32),
            "iso_grav_anom": (1.7 * line_x).astype(np.float32) + (0.001 * (xx - 40) ** 2).astype(np.float32),
            "depth_to_base_surf": (0.8 * line_x).astype(np.float32) + (0.002 * (yy - 40) ** 2).astype(np.float32),
            "cond_surf": (0.6 * line_x).astype(np.float32) + (0.001 * (xx - 40) ** 2).astype(np.float32),
        }
        self.yy = yy
        self.xx = xx
        self.line_y = line_y

    def test_aligned_edges_produce_finite_nonnegative_score_and_maxima(self):
        score, maxima, report = edge_consensus_score(self.layers, self.footprint)
        self.assertEqual(score.shape, self.footprint.shape)
        self.assertEqual(maxima.shape, self.footprint.shape)
        self.assertTrue(np.isfinite(score).all())
        self.assertTrue((score >= 0).all())
        self.assertGreater(float(score.max()), 0.0)
        self.assertGreater(int(maxima.sum()), 0)
        self.assertGreater(report["valid_score_cells"], 0)
        self.assertEqual(report["sigma_px"], 2.0)

    def test_perpendicular_gravity_edge_reduces_alignment_score(self):
        aligned, _, _ = edge_consensus_score(self.layers, self.footprint)
        perpendicular = dict(self.layers)
        perpendicular["iso_grav_anom"] = (self.line_y.astype(np.float32) +
                                            0.001 * (self.yy - 40) ** 2).astype(np.float32)
        crossed, _, _ = edge_consensus_score(perpendicular, self.footprint)
        self.assertGreater(float(aligned.max()), float(crossed.max()))

    def test_sentinel_and_nan_cells_are_not_used_as_physical_zero(self):
        layers = {name: array.copy() for name, array in self.layers.items()}
        layers["tmi"][0, 0] = np.float32(-3.4028234663852886e38)
        layers["cond_surf"][0, 1] = np.nan
        score, _, report = edge_consensus_score(
            layers, self.footprint,
            nodata={"tmi": np.float32(-3.4028234663852886e38)},
        )
        self.assertTrue(np.isfinite(score).all())
        self.assertLess(report["layers"]["tmi"]["valid_cells"], self.footprint.size)
        self.assertLess(report["layers"]["cond_surf"]["valid_cells"], self.footprint.size)

    def test_missing_layer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing required feature layers"):
            edge_consensus_score({"tmi": self.layers["tmi"]}, self.footprint)


class H336ReallocationTests(unittest.TestCase):
    def setUp(self):
        self.shape = (90, 90)
        self.footprint = np.ones(self.shape, dtype=bool)
        self.known = np.zeros(self.shape, dtype=bool)
        self.known[10:80, 44] = True
        self.control = np.zeros(self.shape, dtype=bool)
        self.control[5:85:6, 5:85:6] = True
        self.score = np.zeros(self.shape, dtype=np.float32)
        rr, cc = np.mgrid[:self.shape[0], :self.shape[1]]
        distance = ((rr - 45) ** 2 + (cc - 25) ** 2).astype(np.float32)
        np.divide(1.0, np.sqrt(distance), out=self.score, where=distance > 0)
        self.score[~np.isfinite(self.score)] = 0
        self.maxima = self.score >= self.score  # All cells are maxima for this isolated selection test.

    def test_edge_reallocation_preserves_budget_and_spacing(self):
        output, report = reallocate_edge_budget(
            self.control, self.known, self.footprint, self.score, self.maxima,
        )
        expected_replace = int(np.floor(0.05 * self.control.sum()))
        self.assertEqual(int(output.sum()), int(self.control.sum()))
        self.assertEqual(report["replacement_count"], expected_replace)
        self.assertEqual(report["removed_dots"], expected_replace)
        self.assertEqual(report["added_dots"], expected_replace)
        output_mask = output.astype(bool)
        self.assertFalse(np.any(output_mask & self.known))
        added = output_mask & ~self.control
        if added.any():
            self.assertTrue(np.all(distance_transform_edt(~(output.astype(bool) & ~added))[added] >= 2.8))
            self.assertTrue(np.all(distance_transform_edt(~self.known)[added] > 1.0))
            self.assertGreaterEqual(float(np.min(self.score[added])), float(report["added_score_min"]))

    def test_matched_random_reallocation_is_seeded_and_count_matched(self):
        first, first_report = reallocate_edge_budget(
            self.control, self.known, self.footprint, self.score, self.maxima, random_seed=7,
        )
        second, second_report = reallocate_edge_budget(
            self.control, self.known, self.footprint, self.score, self.maxima, random_seed=7,
        )
        third, _ = reallocate_edge_budget(
            self.control, self.known, self.footprint, self.score, self.maxima, random_seed=8,
        )
        np.testing.assert_array_equal(first, second)
        self.assertEqual(first_report["replacement_count"], second_report["replacement_count"])
        self.assertEqual(int(first.sum()), int(self.control.sum()))
        self.assertFalse(np.array_equal(first, third))
        self.assertEqual(first_report["mode"], "matched_random")

    def test_shape_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must match"):
            reallocate_edge_budget(
                self.control[:-1], self.known, self.footprint, self.score, self.maxima,
            )


if __name__ == "__main__":
    unittest.main()
