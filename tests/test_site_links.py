import hashlib
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(value)


class SiteLinkTests(unittest.TestCase):
    def test_all_local_html_links_resolve(self):
        missing = []
        html_files = [ROOT / "index.html", *sorted(DOCS.glob("*.html"))]
        for html_path in html_files:
            parser = LinkParser()
            parser.feed(html_path.read_text(encoding="utf-8"))
            for href in parser.hrefs:
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or href.startswith("#"):
                    continue
                target = (html_path.parent / unquote(parsed.path)).resolve()
                if not target.is_file():
                    missing.append(f"{html_path.relative_to(ROOT)} -> {href}")
        self.assertEqual(missing, [], "broken local links:\n" + "\n".join(missing))

    def test_repository_root_redirects_to_the_docs_site(self):
        root_index = ROOT / "index.html"
        html = root_index.read_text(encoding="utf-8").lower()
        self.assertIn('http-equiv="refresh"', html)
        self.assertIn("url=docs/index.html", html)
        self.assertTrue((DOCS / "index.html").is_file())

    def test_reference_and_failed_research_artifacts_match_their_manifests(self):
        baseline_manifest = json.loads((DOCS / "downloads" / "manifest.json").read_text())
        baseline = DOCS / "downloads" / baseline_manifest["recommended"]
        self.assertTrue(baseline.is_file(), str(baseline))
        self.assertEqual(hashlib.sha256(baseline.read_bytes()).hexdigest(),
                         baseline_manifest["artifacts"][0]["sha256"])

        research_path = DOCS / "downloads" / "research" / "h33-6-research-manifest.json"
        research = json.loads(research_path.read_text())
        self.assertFalse(research["recommended_for_upload"])
        self.assertFalse(research["slot_cleared"])
        self.assertLessEqual(research["note_chars"], 200)
        self.assertIn("RESEARCH ONLY", research["note"])
        self.assertLess(research["p1_mean_delta_dti"], 0)
        self.assertTrue(research["format_audit"]["pass"])
        self.assertEqual(research["format_audit"]["sha256"], research["artifacts"][0]["sha256"])
        audit_path = ROOT / research["format_audit_path"]
        self.assertTrue(audit_path.is_file(), str(audit_path))
        audit = json.loads(audit_path.read_text())
        nan_artifact = next(a for a in research["artifacts"] if a["variant"] == "nan")
        self.assertEqual(audit["sha256"], nan_artifact["sha256"])
        self.assertTrue(audit["in_range_0_1_footprint"])
        self.assertTrue(audit["outside_is_null_or_zero"])
        self.assertTrue(audit["outside_has_nan"])
        self.assertTrue(audit["pass"])
        for artifact in research["artifacts"]:
            for path_key in ("path", "file"):
                if path_key in artifact["validation"]:
                    self.assertFalse(Path(artifact["validation"][path_key]).is_absolute())
            path = ROOT / artifact["file"]
            zipped = ROOT / artifact["zip"]
            self.assertTrue(path.is_file(), str(path))
            self.assertTrue(zipped.is_file(), str(zipped))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), artifact["sha256"])
            self.assertEqual(hashlib.sha256(zipped.read_bytes()).hexdigest(), artifact["zip_sha256"])
            self.assertTrue(artifact["validation"]["pass"])

        stale = DOCS / "downloads" / "gems33-c2-stepover-relay-20261004-01f660dd8656.tif"
        self.assertFalse(stale.exists(), "withdrawn C2 is not distributed from the recommended download directory")


if __name__ == "__main__":
    unittest.main()
