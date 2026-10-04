"""H33-F analog-field constants, uniqueness, and holdout-gate honesty."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AnalogHypothesisTests(unittest.TestCase):
    def test_current_five_hypothesis_slate_keeps_h33f_as_earlier_failed_run(self):
        hyp = json.loads((ROOT / "registry/hypotheses.json").read_text(encoding="utf-8"))
        ids = [h["id"] for h in hyp["hypotheses"]]
        self.assertEqual(ids, ["H33-6", "H33-7", "H33-8", "H33-9", "H33-10"])
        self.assertEqual(len([h for h in hyp["hypotheses"] if h["rank"] <= 3]), 3)
        for h in hyp["hypotheses"]:
            self.assertTrue(h["layers"])
            self.assertTrue(h["physical_signature"])
            self.assertTrue(h["why_it_targets_faults_absent_from_USGS_INGENIOUS"])
            self.assertTrue(h["difference_from_prior_art"])
            self.assertTrue(h["specific_free_official_source"])
            self.assertTrue(h["expected_DTI_improvement_rank"])
            self.assertTrue(h["implementation_cost"])
        h33f = next(x for x in hyp["earlier_experiments"] if x["id"] == "H33-F")
        self.assertLess(h33f["p1_mean_delta_dti"], 0)
        self.assertFalse(h33f["transfer_bound_licensed"])
        self.assertIn("research-only", h33f["status"])

    def test_holdout_analog_does_not_clear_a_slot(self):
        report = json.loads((ROOT / "evidence/holdout_analog.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "NOT_SLOT_CLEARED")
        self.assertFalse(report["gate"]["slot"])
        self.assertLess(report["p1_mean_delta_dti"], 0)
        self.assertEqual(report["p1_positive_folds"], 0)
        self.assertIn("private expert", report["proxy_warning"])

    def test_domain_preflight_is_exploratory_not_a_bound(self):
        da = json.loads((ROOT / "evidence/domain_adaptation_preflight.json").read_text(encoding="utf-8"))
        self.assertEqual(da["status"], "EXPLORATORY_NOT_LICENSED")
        self.assertFalse(da["ben_david"]["bound_computed"])
        self.assertEqual(da["domain_discriminator"]["status"], "EXPLORATORY_NOT_A_BOUND")
        self.assertGreater(da["domain_discriminator"]["held_out_block_auc"], 0.5)
        self.assertFalse(da["external_gis"]["staged"])

    def test_unique_h33f_is_separate_from_the_d28_reference(self):
        d28_manifest = json.loads((ROOT / "docs/downloads/manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(d28_manifest["recommended"].startswith("gemsdoe33-d28-reference-20261004"))
        h33f_path = ROOT / "docs/downloads/research/h33-f-analog-transfer-manifest.json"
        man = json.loads(h33f_path.read_text(encoding="utf-8"))
        self.assertFalse(man["recommended_for_upload"])
        self.assertFalse(man["slot_cleared"])
        self.assertTrue(man["research_artifact"].startswith("gemsdoe33-h33f-analog-xfer-20261004"))
        self.assertLessEqual(man["note_chars"], 200)
        self.assertIn("research not slot-approved", man["note"])
        self.assertEqual(man["emitted_pixels"], 44090)
        nan = ROOT / "docs/downloads" / man["research_artifact"]
        d28 = ROOT / "docs/downloads" / d28_manifest["recommended"]
        self.assertTrue(nan.is_file())
        self.assertTrue(d28.is_file())
        self.assertNotEqual(nan.read_bytes(), d28.read_bytes())
        self.assertEqual(man["artifacts"][0]["sha256"],
                         "59a68dcd752fc31d774b856e46fddbb9b0e3a9e9c7ab4abb06f77e99b218b10d")
