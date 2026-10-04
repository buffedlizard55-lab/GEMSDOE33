"""H33-F analog-field constants, uniqueness, and holdout-gate honesty."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AnalogHypothesisTests(unittest.TestCase):
    def test_five_new_hypotheses_name_layers_and_sources(self):
        hyp = json.loads((ROOT / "registry/hypotheses.json").read_text(encoding="utf-8"))
        ids = [h["id"] for h in hyp["hypotheses"]]
        self.assertEqual(ids, ["H33-F", "H33-G", "H33-H", "H33-J", "H33-I"])
        f = hyp["hypotheses"][0]
        self.assertIn("dixie", " ".join(f["layers"]).lower())
        self.assertIn("brady", " ".join(f["layers"]).lower())
        self.assertIn("desert peak", " ".join(f["layers"]).lower())
        self.assertIn("gdr.openei.org/submissions/1391", f["specific_free_official_source"])
        self.assertIn("NOT_SLOT_CLEARED", f["status"])
        for h in hyp["hypotheses"]:
            self.assertTrue(h["layers"])
            self.assertTrue(h["physical_signature"])
            self.assertTrue(h["why_it_targets_faults_absent_from_USGS_INGENIOUS"])
            self.assertTrue(h["difference_from_prior_art"])
            self.assertTrue(h["specific_free_official_source"].startswith("http")
                            or "http" in h["specific_free_official_source"])

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

    def test_unique_tif_manifest_is_not_d28_and_has_paste_note(self):
        man = json.loads((ROOT / "docs/downloads/manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(man["recommended"].startswith("gemsdoe33-h33f-analog-xfer-20261004"))
        self.assertTrue(man["source"]["not_a_copy_of_d28"])
        self.assertFalse(man["holdout_gate"]["slot"])
        self.assertLessEqual(man["note_chars"], 200)
        self.assertIn("research not slot-approved", man["note"])
        self.assertEqual(man["emitted_pixels"], 44090)
        nan = ROOT / "docs/downloads" / man["recommended"]
        zeros = ROOT / "docs/downloads" / man["alternate"]
        self.assertTrue(nan.is_file())
        self.assertTrue(zeros.is_file())
        d28 = ROOT / "docs/downloads/gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif"
        if d28.is_file():
            self.assertNotEqual(nan.read_bytes(), d28.read_bytes())
        self.assertEqual(man["artifacts"][0]["sha256"],
                         "59a68dcd752fc31d774b856e46fddbb9b0e3a9e9c7ab4abb06f77e99b218b10d")
