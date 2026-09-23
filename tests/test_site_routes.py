"""Guard the plain-language website route from leading readers to source files."""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit, unquote


ROOT = Path(__file__).resolve().parents[1] / "docs"
PAGES = ("index.html", "guide.html", "disclaimer.html", "developers.html")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.translations = set()
        self.task_links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if values.get("data-t"):
            self.translations.add(values["data-t"])
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.links.append(values[attribute])
        if tag == "a" and "task-row" in values.get("class", "").split():
            self.task_links.append(values.get("href"))


class SiteRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {}
        for name in PAGES:
            parser = PageParser()
            parser.feed((ROOT / name).read_text(encoding="utf-8"))
            cls.pages[name] = parser

    def test_beginner_tasks_stay_on_site(self):
        self.assertEqual(
            self.pages["index.html"].task_links,
            ["guide.html#data", "guide.html#assemble", "guide.html#schematic", "guide.html#review"],
        )
        for name in ("index.html", "guide.html", "disclaimer.html"):
            for link in self.pages[name].links:
                if "github.com/" in link:
                    self.assertIn("/releases/download/", link, f"{name}: {link}")

    def test_all_local_links_and_anchors_resolve(self):
        for name, page in self.pages.items():
            for link in page.links:
                parts = urlsplit(link)
                if parts.scheme or parts.netloc or link.startswith("mailto:"):
                    continue
                target = unquote(parts.path)
                resolved = ROOT / target if target else ROOT / name
                self.assertTrue(resolved.is_file(), f"{name}: missing {link}")
                if parts.fragment and resolved.suffix.lower() == ".html":
                    target_page = self.pages.get(resolved.name)
                    self.assertIsNotNone(target_page, f"{name}: unknown HTML {link}")
                    self.assertIn(parts.fragment, target_page.ids, f"{name}: missing anchor {link}")

    def test_english_translation_covers_visible_labels(self):
        script = (ROOT / "site.js").read_text(encoding="utf-8")
        translated = set(re.findall(r"^  ([A-Za-z][A-Za-z0-9]*):", script, re.M))
        for name, page in self.pages.items():
            self.assertFalse(page.translations - translated, f"{name}: untranslated keys {page.translations - translated}")


if __name__ == "__main__":
    unittest.main()
