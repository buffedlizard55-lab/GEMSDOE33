import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_campaign_feed as campaign_feed


class CampaignFeedTests(unittest.TestCase):
    def test_committed_ledger_renders_all_rows(self):
        ledger = campaign_feed.load_ledger()
        feed = campaign_feed.make_feed(ledger)
        html = campaign_feed.render_block(feed)
        self.assertEqual(len(feed["campaign_submissions"]), len(ledger["submissions"]))
        self.assertIn("nchuzhoy: 0.3262", html)
        self.assertIn("score-feed.json", html)
        self.assertIn("does not scrape or poll DrivenData", html)

    def test_unscored_rows_remain_explicit(self):
        ledger = campaign_feed.load_ledger()
        feed = campaign_feed.make_feed(ledger)
        rows = [row for row in feed["campaign_submissions"] if row["score"] is None]
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] == "unscored / no score reported" for row in rows))
        html = campaign_feed.render_block(feed)
        self.assertIn("unscored", html)

    def test_missing_campaign_placeholders_have_no_fabricated_urls_or_scores(self):
        feed = campaign_feed.make_feed(campaign_feed.load_ledger())
        rows = {row["site"]: row for row in feed["campaign_submissions"]}
        for site in ("31GEMSDOE", "32GEMSDOE"):
            self.assertIn(site, rows)
            self.assertIsNone(rows[site]["score"])
            self.assertIsNone(rows[site]["source_url"])
            self.assertIn("empty score heading", rows[site]["note"])

    def test_html_escapes_submission_names(self):
        ledger = campaign_feed.load_ledger()
        malicious = copy.deepcopy(ledger)
        malicious["submissions"] = [{
            "site": "Example",
            "name": '<script>alert("x")</script>',
            "score": 0.1,
            "note": '<img src=x onerror="alert(1)">',
        }]
        malicious["campaign_sites"] = {}
        feed = campaign_feed.make_feed(malicious)
        html = campaign_feed.render_block(feed)
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn('<img src=x', html)

    def test_invalid_score_is_rejected(self):
        invalid = campaign_feed.load_ledger()
        invalid["submissions"] = [{"site": "X", "name": "bad", "score": 1.1}]
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            path.write_text(json.dumps(invalid))
            original = campaign_feed.LEDGER
            try:
                campaign_feed.LEDGER = path
                with self.assertRaises(ValueError):
                    campaign_feed.load_ledger()
            finally:
                campaign_feed.LEDGER = original


if __name__ == "__main__":
    unittest.main()
