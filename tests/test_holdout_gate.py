import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems33.holdout import gate_summary


class GateSummaryTests(unittest.TestCase):
    def test_strict_majority_and_both_proxies_pass(self):
        report = {
            "p1_mean_d_dti": 0.0004,
            "p1_positive_folds": 3,
            "p1_n_folds": 4,
            "p2": {"d_dti": 0.0002},
        }
        self.assertTrue(gate_summary(report)["pass"])

    def test_tie_is_not_a_majority(self):
        report = {
            "p1_mean_d_dti": 0.001,
            "p1_positive_folds": 2,
            "p1_n_folds": 4,
            "p2": {"d_dti": 0.0},
        }
        verdict = gate_summary(report)
        self.assertFalse(verdict["p1_majority_folds_positive"])
        self.assertFalse(verdict["pass"])

    def test_missing_p2_fails_closed(self):
        report = {
            "p1_mean_d_dti": 0.001,
            "p1_positive_folds": 4,
            "p1_n_folds": 4,
            "p2": None,
        }
        verdict = gate_summary(report)
        self.assertFalse(verdict["p2_not_worse"])
        self.assertFalse(verdict["pass"])

    def test_p2_tolerance_boundary_is_inclusive(self):
        report = {
            "p1_mean_d_dti": 0.001,
            "p1_positive_folds": 3,
            "p1_n_folds": 4,
            "p2": {"d_dti": -0.001},
        }
        self.assertTrue(gate_summary(report)["pass"])

    def test_empty_fold_result_fails(self):
        report = {
            "p1_mean_d_dti": 0.001,
            "p1_positive_folds": 0,
            "p1_n_folds": 0,
            "p2": {"d_dti": 0.0},
        }
        self.assertFalse(gate_summary(report)["pass"])


if __name__ == "__main__":
    unittest.main()
