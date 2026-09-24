"""Product site links, downloads and the actual beginner route."""
from html.parser import HTMLParser
from pathlib import Path
import csv
import json
import unittest
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
PAGES = ("index.html", "start.html", "features.html", "gallery.html", "learn.html",
         "community.html", "contribute.html", "support.html", "roadmap.html",
         "developers.html", "guide.html", "disclaimer.html")
SAMPLES = ("full_cell", "li_cu_ce", "li_li", "eis", "operando_xrd", "tof_sims", "integrated_study",
           "rate_capability", "gcd_profiles", "pouch_thermal", "literature_benchmark", "reporting_matrix", "capability_spread")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.buttons_without_type = []
        self.images_without_size = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "button" and values.get("type") != "button":
            self.buttons_without_type.append(values)
        if tag == "img" and (not values.get("width") or not values.get("height")):
            self.images_without_size.append(values)
        for key in ("href", "src"):
            if values.get(key):
                self.links.append(values[key])


class ProductSiteTest(unittest.TestCase):
    @staticmethod
    def rows(name, filename="data.csv"):
        with (REPO / "examples/showcase" / name / filename).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    @classmethod
    def setUpClass(cls):
        cls.pages = {}
        for name in PAGES:
            parser = Links()
            parser.feed((DOCS / name).read_text(encoding="utf-8"))
            cls.pages[name] = parser

    def test_navigation_and_all_local_links(self):
        for name, page in self.pages.items():
            for link in page.links:
                parts = urlsplit(link)
                if parts.scheme or parts.netloc or link.startswith(("mailto:", "#")):
                    if link.startswith("#") and len(link) > 1:
                        self.assertIn(link[1:], page.ids, f"{name}: {link}")
                    continue
                target = unquote(parts.path)
                file = DOCS / target if target else DOCS / name
                self.assertTrue(file.is_file(), f"{name}: missing {link}")
                if parts.fragment and file.suffix == ".html":
                    target_page = self.pages.get(file.name)
                    self.assertIsNotNone(target_page)
                    self.assertIn(parts.fragment, target_page.ids, f"{name}: {link}")

    def test_home_is_product_route_not_prompt_router(self):
        home = (DOCS / "index.html").read_text(encoding="utf-8")
        self.assertIn("把电池数据，<br>画成论文图。", home)
        self.assertIn('href="start.html"', home)
        self.assertIn('href="gallery.html"', home)
        self.assertEqual(home.count('class="gallery-card'), 5)
        self.assertNotIn("assets/gallery/", home)
        self.assertNotIn("wizard-prompt", home)
        self.assertNotIn("先让助手看一眼", home)
        self.assertIn("同一研究的六面板图", home)
        self.assertIn("软包电池表面温度", home)
        self.assertIn("文献数据对照散点", home)
        self.assertNotIn("准备写综述", home)
        self.assertNotIn("写综述时", home)

    def test_onboarding_has_deterministic_steps_and_real_downloads(self):
        html = (DOCS / "start.html").read_text(encoding="utf-8")
        js = (DOCS / "start.js").read_text(encoding="utf-8")
        for step in ("client", "os", "install", "test"):
            self.assertIn(f'data-wizard-step="{step}"', html)
        self.assertIn("goToStep", js)
        self.assertIn("popstate", js)
        self.assertNotIn("history.back()", js)
        self.assertIn('preferredClient', js)
        self.assertIn('preferredOS', js)
        self.assertIn('compatibility = {', js)
        self.assertIn('document.execCommand("copy")', js)
        self.assertIn('state.client === "workbuddy" ? ["client","install","test"]', js)
        self.assertIn("demo_full_cell.csv", html)
        self.assertTrue((DOCS / "assets/showcase/assembly-demo.zip").is_file())
        with ZipFile(DOCS / "assets/showcase/assembly-demo.zip") as z:
            self.assertEqual(len([n for n in z.namelist() if n.startswith("panel-") and n.endswith(".png")]), 6)
            self.assertIn("figure_manifest.json", z.namelist())
            self.assertIn("assembled-example.qa.json", z.namelist())

    def test_search_is_local_and_beginner_first(self):
        index = json.loads((DOCS / "search-index.json").read_text(encoding="utf-8"))
        self.assertEqual(index[0]["group"], "开始做")
        self.assertTrue(any("库伦效率" in item["keywords"] for item in index))
        js = (DOCS / "product.js").read_text(encoding="utf-8")
        self.assertIn('fetch("search-index.json")', js)
        self.assertNotIn("sendBeacon", js)
        self.assertNotIn("XMLHttpRequest", js)
        self.assertIn('region.inert = true', js)
        self.assertIn('搜索内容加载失败，请重试', js)
        for name in PAGES:
            self.assertNotIn('type="file"', (DOCS / name).read_text(encoding="utf-8"))
            self.assertNotIn('client=codex&amp;os=windows', (DOCS / name).read_text(encoding="utf-8"))
            self.assertNotIn('client=codex&os=windows', (DOCS / name).read_text(encoding="utf-8"))
            self.assertEqual(self.pages[name].buttons_without_type, [], name)
            self.assertEqual(self.pages[name].images_without_size, [], name)

    def test_showcase_has_sources_and_final_exports(self):
        for name in SAMPLES:
            source = REPO / "examples/showcase" / name
            public = DOCS / "assets/showcase" / name
            metadata = json.loads((source / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["data_status"], "synthetic_demo")
            self.assertIn("random_seed", metadata)
            self.assertIn("variables_and_units", metadata)
            self.assertIn("sample_identity", metadata)
            for part in ("generate_data.py", "plot.py", "figure.svg", "figure.pdf", "figure.png"):
                self.assertTrue((source / part).is_file(), f"{name}: {part}")
            for part in ("figure.svg", "figure.pdf", "figure.png", "metadata.json"):
                self.assertTrue((public / part).is_file(), f"{name}: {part}")
            alignment = json.loads((source / "alignment.json").read_text(encoding="utf-8"))
            self.assertFalse(alignment["failures"], name)
            self.assertTrue((public / "alignment.json").is_file(), name)
            for item in metadata["source_files"]:
                self.assertTrue((source / item).resolve().is_file(), f"{name}: {item}")

    def test_versioned_downloads_and_contributors(self):
        version = json.loads((REPO / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertEqual(version, json.loads((REPO / "plugin.json").read_text(encoding="utf-8"))["version"])
        for suffix in ("", "-WorkBuddy"):
            self.assertTrue((DOCS / "downloads" / f"BatteryReviewForge{suffix}-v{version}.zip").is_file())
        with ZipFile(DOCS / "downloads" / f"BatteryReviewForge-v{version}.zip") as z:
            self.assertEqual(len([n for n in z.namelist() if n.endswith("/SKILL.md")]), 13)
        self.assertEqual(json.loads((DOCS / "contributors.json").read_text(encoding="utf-8")), json.loads((REPO / "CONTRIBUTORS.yaml").read_text(encoding="utf-8")))

    def test_new_demos_preserve_linked_data_and_honest_ids(self):
        rate = self.rows("rate_capability")
        selected = self.rows("rate_capability", "voltage_profiles.csv")
        rate_index = {(r["sample"], r["cycle"]): r for r in rate}
        self.assertEqual([float(r["discharge_rate_C"]) for r in rate if r["sample"] == "A" and int(r["cycle"]) in {1, 11, 21, 31, 41, 51}], [.2, .5, 1, 2, 5, .2])
        for r in selected:
            self.assertAlmostEqual(float(r["cycling_endpoint_mAh_g"]), float(rate_index["A", r["cycle"]]["capacity_mAh_g"]), places=5)
        thermal = self.rows("pouch_thermal")
        line = self.rows("pouch_thermal", "line_profile.csv")
        lookup = {(r["x_mm"], r["y_mm"]): float(r["surface_temperature_C"]) for r in thermal}
        for r in line:
            self.assertAlmostEqual(float(r["surface_temperature_C"]), lookup[r["distance_mm"], "35.0"], places=5)
        history = self.rows("pouch_thermal", "history.csv")
        self.assertAlmostEqual(float(history[-1]["Tmax_C"]), max(lookup.values()), places=5)
        benchmark = self.rows("literature_benchmark")
        self.assertEqual(len(benchmark), 48)
        self.assertEqual(len({r["synthetic_id"] for r in benchmark}), 48)
        self.assertEqual({(r["discharge_rate_C"], r["cycle"], r["temperature_C"]) for r in benchmark}, {("0.2", "100", "25")})
        matrix = self.rows("reporting_matrix")
        self.assertEqual(len(matrix), 18 * 7)
        self.assertEqual({r["status"] for r in matrix}, {"R", "P", "NR", "NV", "NA"})
        spread = self.rows("capability_spread", "data_index.csv")
        self.assertEqual([r["panel"] for r in spread], list("abcdefghij"))
        self.assertEqual(json.loads((REPO / "examples/showcase/capability_spread/alignment.json").read_text(encoding="utf-8"))["status"], "pass")


if __name__ == "__main__":
    unittest.main()
