"""Regression tests for the 2026-10-29 nine-site audit (scripts/nine_site_audit.py).

These tests read committed evidence and the manifest only. They do not download
anything and do not need the git-ignored data/ directory.
"""
import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import nine_site_audit as nsa  # noqa: E402

EVIDENCE = ROOT / "evidence" / "nine_site_audit_20261029.json"
MANIFEST = ROOT / "registry" / "nine_site_best_files_20261029.json"


class BlobHashTests(unittest.TestCase):
    def test_git_blob_sha1_matches_git(self):
        # Known values from `git hash-object --stdin`.
        self.assertEqual(nsa.git_blob_sha1(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
        self.assertEqual(nsa.git_blob_sha1(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_sha256_helper(self):
        self.assertEqual(nsa.sha256_bytes(b"abc"), hashlib.sha256(b"abc").hexdigest())


class DotMaskTests(unittest.TestCase):
    def test_near3_is_a_three_pixel_dilation(self):
        mask = np.zeros((9, 9), dtype=bool)
        mask[4, 4] = True
        near = nsa.near3(mask)
        self.assertTrue(near[4, 7])        # distance 3 counts
        self.assertFalse(near[4, 8])       # distance 4 does not
        self.assertEqual(near.dtype, bool)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text())
        self.evidence = json.loads(EVIDENCE.read_text())

    def test_names_are_unique_and_roles_are_known(self):
        names = [f"{e['site']}/{e['user_reported_name']}" for e in self.manifest["entries"]]
        self.assertEqual(len(names), len(set(names)))
        roles = {e["role"] for e in self.manifest["entries"]}
        self.assertLessEqual(roles, {"site_best", "site_listed", "local_research_zeros"})

    def test_nine_site_best_files_one_per_site(self):
        best = [e["site"] for e in self.manifest["entries"] if e["role"] == "site_best"]
        self.assertEqual(sorted(best), ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                                        "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"])
        self.assertEqual(len(best), 9)
        self.assertEqual(len(set(best)), 9)

    def test_every_entry_has_a_40_hex_blob_id(self):
        for e in self.manifest["entries"]:
            self.assertRegex(e["blob_sha1"], r"^[0-9a-f]{40}$")

    def test_verdicts_cover_every_manifest_entry(self):
        self.assertEqual(len(self.evidence["site_verdicts"]), len(self.manifest["entries"]))

    def test_unique_flag_matches_trigger_count(self):
        for v in self.evidence["site_verdicts"]:
            self.assertEqual(v["unique_under_guard"], len(v["duplicate_trigger_vs_other_submissions"]) == 0,
                             v["name"])

    def test_no_site_best_file_is_unique(self):
        # Decision-relevant invariant: the nine site-best files are one family and must not be
        # reported as unique. If this fails, the audit changed and the executive summary must change too.
        for v in self.evidence["site_verdicts"]:
            if v["role"] == "site_best":
                self.assertFalse(v["unique_under_guard"], v["name"])

    def test_b2_recount_is_a_pure_deletion_of_h27_4(self):
        for f in self.evidence["b2_forensic_recount"]:
            self.assertEqual(f["parent_dots"] - f["child_dots"], f["removed_dots"])
            self.assertEqual(f["added_dots"], 0)
            self.assertTrue(f["child_is_exact_subset_of_parent"])
            self.assertEqual(f["child_dots_on_catalogue"], 0)
            self.assertEqual(f["removed_by_catalogue_distance"]["d_1_to_2px"], f["removed_dots"])
            self.assertEqual(f["child_dots"], 37654)
            self.assertEqual(f["parent_dots"], 40199)

    def test_out_of_footprint_failure_is_detected_for_hmdt(self):
        hmdt = [v for v in self.evidence["nine_site_files"] if "hmdt" in v["name"]]
        self.assertEqual(len(hmdt), 1)
        self.assertFalse(hmdt[0]["format_checks"]["outside_footprint_zero_or_nan"])
        self.assertFalse(hmdt[0]["format_pass"])


if __name__ == "__main__":
    unittest.main()
