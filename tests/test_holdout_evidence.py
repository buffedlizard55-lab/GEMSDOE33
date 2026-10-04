"""Guardrails for the corrected and withdrawn Session-33 holdout reports."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HoldoutEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corrected = json.loads((ROOT / "evidence/holdout33.json").read_text(encoding="utf-8"))
        cls.legacy = json.loads(
            (ROOT / "evidence/holdout33_legacy_catalogue_only.json").read_text(encoding="utf-8")
        )

    def test_corrected_diagnostic_fails_and_does_not_clear_a_slot(self):
        report = self.corrected
        self.assertFalse(report["validity"]["slot_cleared"])
        self.assertLess(report["p1"]["mean_delta_dti"], 0)
        self.assertEqual(report["p1"]["positive_folds"], 0)
        self.assertEqual(report["p1"]["n_folds"], 4)
        self.assertFalse(report["numeric_proxy_gate"]["pass"])

    def test_candidate_only_dots_receive_no_incremental_true_positive_weight(self):
        contribution = self.corrected["p1"]["incremental_contribution_summary"]
        self.assertTrue(contribution["no_incremental_true_positive_weight_any_fold"])
        self.assertEqual(contribution["delta_tpw_total"], 0)
        self.assertEqual(contribution["delta_fpw_total"], 2643)
        self.assertEqual(contribution["added_dots_total_across_folds"], 2643)

    def test_positive_p2_is_labeled_as_a_proxy_not_competition_truth(self):
        self.assertGreater(self.corrected["p2"]["delta_dti"], 0)
        self.assertEqual(
            self.corrected["p2"]["status"],
            "INDEPENDENT_COMPILATION_PROXY_NOT_COMPETITION_TRUTH",
        )
        self.assertIn("not an independent preregistered confirmation", self.corrected["promotion"])

    def test_legacy_p1_result_is_withdrawn_for_promotion(self):
        self.assertEqual(
            self.corrected["validity"]["previous_full_catalogue_p1_status"],
            "WITHDRAWN_FOR_PROMOTION",
        )
        self.assertEqual(self.legacy["_review"]["status"], "WITHDRAWN_FOR_PROMOTION")
        self.assertIn("not valid spatial-generalization evidence", self.legacy["_review"]["reason"])
        self.assertTrue(self.legacy["gate"]["C2"]["pass"])  # preserved legacy numeric result only


if __name__ == "__main__":
    unittest.main()
