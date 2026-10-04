import hashlib
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
        for html_path in sorted(DOCS.glob("*.html")):
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

    def test_main_download_artifacts_exist_and_c2_hash_matches(self):
        baseline = DOCS / "downloads" / "gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif"
        candidate = DOCS / "downloads" / "gems33-c2-stepover-relay-20261004-01f660dd8656.tif"
        for path in (baseline, candidate):
            self.assertTrue(path.is_file(), str(path))
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        self.assertEqual(digest, "7272633447365d7ec8a9c07972b48df92b071a1ecc5765cf14199c14dea4f0f7")
        stale = DOCS / "downloads" / "gems33-c2-stepover-relay-20261004-eb6bcf02361f.tif"
        self.assertFalse(stale.exists(), "superseded nondeterministic C2 must not be distributed")


if __name__ == "__main__":
    unittest.main()
