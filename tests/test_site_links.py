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

    def test_unique_download_exists_and_is_not_the_d28_reference(self):
        unique = DOCS / "downloads" / "gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef-nan.tif"
        d28 = DOCS / "downloads" / "gemsdoe33-d28-reference-20261004-426073b6b4ab-nan.tif"
        self.assertTrue(unique.is_file(), str(unique))
        digest = hashlib.sha256(unique.read_bytes()).hexdigest()
        self.assertEqual(digest, "59a68dcd752fc31d774b856e46fddbb9b0e3a9e9c7ab4abb06f77e99b218b10d")
        if d28.is_file():
            self.assertNotEqual(digest, hashlib.sha256(d28.read_bytes()).hexdigest())
        zip_path = DOCS / "downloads" / "gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef-nan.zip"
        self.assertTrue(zip_path.is_file())
