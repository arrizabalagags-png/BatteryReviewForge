"""Guard the plain-language website route from leading readers to source files."""

from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest
from urllib.parse import urlsplit, unquote
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1] / "docs"
PAGES = ("index.html", "start.html", "guide.html", "disclaimer.html", "developers.html")


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
            ["start.html?material=data", "start.html?material=images", "start.html?material=review", "start.html"],
        )
        for name in ("index.html", "start.html", "guide.html", "disclaimer.html"):
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

    def test_site_claim_about_no_file_intake_remains_true(self):
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("<form", html.lower(), name)
            self.assertNotRegex(html, r"<input\b[^>]*\btype=[\"']file[\"']", name)
        script = (ROOT / "site.js").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\b(?:fetch|XMLHttpRequest|sendBeacon)\s*\(")

    def test_beginner_controls_hide_technical_detail_until_chosen(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="platform-codex"><summary>', home)
        self.assertIn('<details class="skill-details">', home)
        self.assertIn('href="guide.html#unsure"', home)
        self.assertIn('<details class="gallery-more">', home)
        wizard = (ROOT / "start.html").read_text(encoding="utf-8")
        self.assertIn('data-step="1"', wizard)
        self.assertIn('data-step="2"', wizard)
        self.assertIn('data-step="3"', wizard)
        self.assertIn('id="wizard-prompt"', wizard)
        script = (ROOT / "start.js").read_text(encoding="utf-8")
        for task in ("cycling", "ce", "other", "assemble", "schematic", "plan", "draft"):
            self.assertIn(f'id: "{task}"', script)
        self.assertNotRegex(script, r"\b(?:fetch|XMLHttpRequest|sendBeacon)\s*\(")

    def test_editorial_gallery_example_discloses_synthetic_sources(self):
        gallery = ROOT / "assets" / "gallery"
        metadata = json.loads((gallery / "editorial-assembly-demo.layout.json").read_text(encoding="utf-8"))
        self.assertIn("synthetic", metadata["status"])
        self.assertEqual(set(metadata["panels"]), set("abcdef"))
        for filename in ("editorial-assembly-demo.png", "editorial-assembly-demo.svg", "editorial-assembly-demo.pdf"):
            self.assertTrue((gallery / filename).is_file())
        self.assertIn('data-t="galleryEditorialCaveat"', (ROOT / "index.html").read_text(encoding="utf-8"))

    def test_synthetic_tutorial_figures_are_not_featured_as_validated_samples(self):
        gallery = ROOT / "assets" / "gallery"
        for stem in ("full-cell-frontpage", "ce-frontpage", "eis-frontpage", "evidence-matrix-frontpage"):
            metadata = json.loads((gallery / f"{stem}.layout.json").read_text(encoding="utf-8"))
            self.assertIn("synthetic", metadata["status"])
            for item in metadata["input_csv"]:
                self.assertTrue((gallery / item).is_file(), item)
            for suffix in (".png", ".svg", ".pdf"):
                self.assertTrue((gallery / f"{stem}{suffix}").is_file())
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="gallery-review"', home)
        self.assertLess(home.index('class="gallery-review"'), home.index('class="gallery-feature"'))
        self.assertNotIn('class="hero-plate"><a href="assets/gallery/', home)
        self.assertIn('data-t="galleryReviewNote"', home)
        self.assertEqual(home.count('class="gallery-item'), 4)
        for stem in ("full-cell-frontpage", "ce-frontpage", "editorial-assembly-demo", "tofsims-demo"):
            self.assertIn(f"assets/gallery/{stem}.png", home)

    def test_homepage_downloads_match_current_plugin(self):
        repo = ROOT.parent
        version = json.loads((repo / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertEqual(version, json.loads((repo / "plugin.json").read_text(encoding="utf-8"))["version"])
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        for basename in (f"BatteryReviewForge-v{version}.zip", f"BatteryReviewForge-WorkBuddy-v{version}.zip"):
            self.assertIn(f"/downloads/{basename}", home)
            self.assertTrue((ROOT / "downloads" / basename).is_file())
        with ZipFile(ROOT / "downloads" / f"BatteryReviewForge-v{version}.zip") as archive:
            self.assertEqual(len([name for name in archive.namelist() if name.endswith("/SKILL.md")]), 13)
            self.assertIn("skills/battery-review-figure/references/BATTERY_FIGURE_GRAMMAR.json", archive.namelist())


if __name__ == "__main__":
    unittest.main()
