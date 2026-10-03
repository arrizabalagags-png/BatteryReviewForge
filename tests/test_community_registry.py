"""Version pinning, hash checks and claim discipline for Battery Commons."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "voltpeer-plot" / "scripts"))

import build_community_registry as community_builder  # noqa: E402
from build_community_registry import layout_preview, validate, validate_layout  # noqa: E402
from community_registry import browse, read_bytes, resolve, NoRedirect  # noqa: E402
from batteryplot.style import PRESETS, register_community_style  # noqa: E402


class CommonsTest(unittest.TestCase):
    def test_empty_build_and_invalid_input_preserve_published_snapshot(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            source, public = Path(tmp) / 'source', Path(tmp) / 'public'
            (source / 'styles').mkdir(parents=True)
            (source / 'layouts').mkdir()
            with patch.object(community_builder, 'SOURCE', source), patch.object(community_builder, 'PUBLIC', public):
                community_builder.main()
                empty = (public / 'catalog.json').read_bytes()
                self.assertEqual(json.loads(empty)['assets'], [])
                self.assertIsNone(json.loads(empty)['updated_at'])
                shutil.copyfile(ROOT / 'community/styles/ocean-electrolyte@1.0.0.json', source / 'styles/ocean-electrolyte@1.0.0.json')
                (source / 'layouts/bad.json').write_text('{}')
                with self.assertRaises(ValueError):
                    community_builder.main()
                self.assertEqual((public / 'catalog.json').read_bytes(), empty)
                self.assertFalse((public / 'styles/ocean-electrolyte@1.0.0.json').exists())

    def test_withdrawal_is_separate_and_blocks_new_resolution(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            source, public = Path(tmp) / 'source', Path(tmp) / 'public'
            (source / 'styles').mkdir(parents=True)
            (source / 'layouts').mkdir()
            path = source / 'styles/ocean-electrolyte@1.0.0.json'
            shutil.copyfile(ROOT / 'community/styles/ocean-electrolyte@1.0.0.json', path)
            original = path.read_bytes()
            review = {'id':'ocean-electrolyte','version':'1.0.0','lifecycle':'withdrawn',
                      'reviewer':'Test reviewer','reviewed_at':'2026-09-27','reason':'Test fixture only','evidence':['fixture report']}
            (source / 'reviews.json').write_text(json.dumps([review]))
            with patch.object(community_builder, 'SOURCE', source), patch.object(community_builder, 'PUBLIC', public):
                community_builder.main()
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(json.loads((public / 'search-index.json').read_text()), [])
            with self.assertRaisesRegex(ValueError, 'withdrawn'):
                resolve(str(public / 'catalog.json'), 'community:ocean-electrolyte@1.0.0', Path(tmp) / 'out', allow_network=False)

    def test_local_scope_and_redirects_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            outside = ROOT / 'community/styles/ocean-electrolyte@1.0.0.json'
            with self.assertRaisesRegex(ValueError, 'authorized'):
                read_bytes(str(outside), allow_network=False, local_root=Path(tmp))
        with self.assertRaisesRegex(ValueError, 'redirects'):
            NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.com/payload')

    def test_catalog_matches_published_assets(self):
        catalog = json.loads((ROOT / "community/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["assets"]), 2)
        for item in catalog["assets"]:
            category = "styles" if item["category"] == "style" else "layouts"
            source = ROOT / "community" / category / f'{item["id"]}@{item["version"]}.json'
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), item["sha256"])
            self.assertEqual(validate(source)["status"], "community")
            self.assertEqual((ROOT / "docs/commons" / category / source.name).read_bytes(), source.read_bytes())

    def test_public_text_limits_match_submission_guidance(self):
        source = json.loads((ROOT / "community/styles/ocean-electrolyte@1.0.0.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ocean-electrolyte@1.0.0.json"
            valid = {**source, "name":"N" * 80, "author":"A" * 120,
                     "description":"D" * 400, "description_zh":"Z" * 400, "tags":["t" * 40]}
            path.write_text(json.dumps(valid), encoding="utf-8")
            self.assertEqual(validate(path)["name"], "N" * 80)
            for field, value in (("name", "N" * 81), ("author", "A" * 121),
                                 ("description", "D" * 401), ("description_zh", "Z" * 401),
                                 ("tags", ["t" * 41])):
                with self.subTest(field=field):
                    invalid = {**valid, field:value}
                    path.write_text(json.dumps(invalid), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        validate(path)

    def test_explicit_pin_and_hash_enforced(self):
        source = ROOT / "community/styles/ocean-electrolyte@1.0.0.json"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            catalog = folder / "catalog.json"
            entry = {"id":"ocean-electrolyte","version":"1.0.0","category":"style","status":"community",
                     "source_url":str(source),"sha256":digest}
            catalog.write_text(json.dumps({"assets":[entry]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                resolve(str(catalog), "community:ocean-electrolyte@latest", folder / "bad", allow_network=False)
            result = resolve(str(catalog), "community:ocean-electrolyte@1.0.0", folder / "out", allow_network=False, local_root=ROOT / 'community')
            pin = "community:ocean-electrolyte@1.0.0"
            try:
                resolved_pin, provenance = register_community_style(result["lock"])
                self.assertEqual(resolved_pin, pin)
                self.assertIn(pin, PRESETS)
                self.assertEqual(provenance["sha256"], digest)
                Path(result["asset"]).write_text("{}", encoding="utf-8")
                with self.assertRaises(Exception):
                    register_community_style(result["lock"])
            finally:
                PRESETS.pop(pin, None)

    def test_pinned_style_is_recorded_in_real_plot_output(self):
        source = ROOT / "community/styles/ocean-electrolyte@1.0.0.json"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            catalog = folder / "catalog.json"
            catalog.write_text(json.dumps({"assets":[{"id":"ocean-electrolyte","version":"1.0.0",
                "category":"style","status":"community","source_url":str(source),"sha256":digest}]}), encoding="utf-8")
            resolved = resolve(str(catalog), "community:ocean-electrolyte@1.0.0", folder / "locks", allow_network=False, local_root=ROOT / 'community')
            data = folder / "ce.csv"
            data.write_text("sample,cycle_no,eff\nA,1,99.2\nA,2,99.7\n", encoding="utf-8")
            metadata = folder / "mapping.json"
            metadata.write_text(json.dumps({
                "kind":"coulombic_efficiency", "style":"community:ocean-electrolyte@1.0.0",
                "community_style_lock":resolved["lock"], "claim":"Synthetic CE example",
                "caption_notes":"Synthetic, not experimental evidence.",
                "columns":{"series":"sample","cycle":"cycle_no","ce_pct":"eff"},
                "common":{"source_id":"test:synthetic","evidence_state":"verified",
                          "chemistry":"synthetic Li metal","cell_configuration":"half cell",
                          "temperature_c":"25","electrolyte_ul_mg":"10","rate":"1 C",
                          "loading_mg_cm2":"2","voltage_window_v":"2.5-4.2",
                          "ce_definition":"discharge/charge"}}, ensure_ascii=False), encoding="utf-8")
            output = folder / "ce_plot"
            process = subprocess.run([sys.executable, str(ROOT / "skills/voltpeer-plot/scripts/plot_uploaded.py"),
                "plot", "--data", str(data), "--metadata", str(metadata), "--out", str(output)],
                capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            record = json.loads(output.with_suffix(".provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(record["style"], "community:ocean-electrolyte@1.0.0")
            self.assertEqual(record["community_style"]["sha256"], digest)
            self.assertTrue(output.with_suffix(".svg").is_file())

    def test_community_search_is_bounded_and_filterable(self):
        entries = []
        for index in range(50):
            entries.append({"id":f"palette-{index}","version":"1.0.0","category":"style","status":"community",
                "name":f"Ocean Palette {index}","author":"Researcher","description_zh":"blue green electrochemistry",
                "tags":["electrochemistry","blue"],"search_terms":["蓝绿色","四条曲线配色"],"recommended_series_count":4})
        with tempfile.TemporaryDirectory() as tmp:
            catalog = Path(tmp) / "catalog.json"
            for fixture in ([], entries[:1], entries[:10], entries):
                catalog.write_text(json.dumps({"assets":fixture}), encoding="utf-8")
                self.assertEqual(len(browse(str(catalog), allow_network=False)), min(len(fixture), 10))
            results = browse(str(catalog), allow_network=False, query="ocean", tags=["blue"], category="style", limit=3, search=True)
            self.assertEqual(len(results), 3)
            self.assertTrue(all("pin" in row and row["pin"].startswith("community:palette-") for row in results))
            self.assertTrue(browse(str(catalog), allow_network=False, query="蓝绿色配色", search=True))
            self.assertTrue(browse(str(catalog), allow_network=False, query="四条曲线配色", series_count=4, search=True))
            self.assertEqual(browse(str(catalog), allow_network=False, tags=["t" * 40]), [])
            with self.assertRaisesRegex(ValueError, "tags to 40"):
                browse(str(catalog), allow_network=False, tags=["t" * 41])
            self.assertEqual(browse(str(catalog), allow_network=False, query="not-there"), [])

    def test_layout_schema_supports_two_through_ten_panels(self):
        with tempfile.TemporaryDirectory() as tmp:
            for count in (2, 3, 6, 10):
                cols = 5 if count == 10 else 2
                rows = (count + cols - 1) // cols
                panels = []
                for index in range(count):
                    panels.append({"label":chr(97+index),"role":f"Evidence role {index+1}","row":index//cols+1,"col":index%cols+1,"rowspan":1,"colspan":1})
                asset = {"panel_count":count,"roles":[panel["role"] for panel in panels],"minimum_width_mm":183,"minimum_font_pt":6,
                         "canvas":{"width_mm":183,"margin_mm":8,"gutter_mm":4},
                         "grid":{"rows":rows,"cols":cols,"row_weights":[1]*rows,"col_weights":[1]*cols},"panels":panels}
                path = Path(tmp) / f"layout-{count}.json"
                validate_layout(asset, path)
                svg = layout_preview({**asset,"name":"Safe preview"})
                self.assertEqual(svg.count("<rect "), count + 1)
            overlapping = {"panel_count":2,"roles":["a","b"],"minimum_width_mm":183,"minimum_font_pt":6,
                "canvas":{"width_mm":183,"margin_mm":8,"gutter_mm":4},"grid":{"rows":1,"cols":2,"row_weights":[1],"col_weights":[1,1]},
                "panels":[{"label":"a","role":"one","row":1,"col":1},{"label":"b","role":"two","row":1,"col":1}]}
            with self.assertRaisesRegex(ValueError,"overlap"):
                validate_layout(overlapping, Path("bad-layout.json"))
            too_many = {**overlapping,"panel_count":11,"roles":[str(i) for i in range(11)]}
            with self.assertRaisesRegex(ValueError,"2 to 10"):
                validate_layout(too_many, Path("too-many.json"))

    def test_layout_preview_escapes_panel_text(self):
        asset = {"name":"Preview","panel_count":2,"roles":["one","two"],"minimum_width_mm":183,"minimum_font_pt":6,
            "canvas":{"width_mm":183,"margin_mm":8,"gutter_mm":4},"grid":{"rows":1,"cols":2,"row_weights":[1],"col_weights":[1,1]},
            "panels":[{"label":"a","role":"<script>alert(1)</script>","row":1,"col":1},{"label":"b","role":"second","row":1,"col":2}]}
        svg = layout_preview(asset)
        self.assertIn("&lt;script&gt;", svg)
        self.assertNotIn("<script>", svg)

    def test_duplicate_id_version_is_rejected_before_catalog_publish(self):
        style = json.loads((ROOT / "community/styles/ocean-electrolyte@1.0.0.json").read_text(encoding="utf-8"))
        layout = json.loads((ROOT / "community/layouts/cycling-plus-profiles@1.0.0.json").read_text(encoding="utf-8"))
        layout["id"] = style["id"]
        layout["version"] = style["version"]
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "community"
            public = Path(tmp) / "public"
            (source / "styles").mkdir(parents=True)
            (source / "layouts").mkdir()
            (source / "styles/ocean-electrolyte@1.0.0.json").write_text(json.dumps(style), encoding="utf-8")
            (source / "layouts/ocean-electrolyte@1.0.0.json").write_text(json.dumps(layout), encoding="utf-8")
            with patch.object(community_builder, "SOURCE", source), patch.object(community_builder, "PUBLIC", public):
                with self.assertRaisesRegex(ValueError, "Duplicate community id@version"):
                    community_builder.main()

    def test_resolve_rejects_unsafe_pins_and_noncommons_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            with self.assertRaisesRegex(ValueError, "safe exact"):
                resolve("unused", "community:../outside@1.0.0", output, allow_network=False)
            with self.assertRaisesRegex(ValueError, "official Battery Commons path"):
                read_bytes("https://arrizabalagags-png.github.io/other/catalog.json", allow_network=True)
            for url in (
                "https://arrizabalagags-png.github.io/BatteryReviewForge/commons/../../README.md",
                "https://arrizabalagags-png.github.io/BatteryReviewForge/commons/%2e%2e/README.md",
            ):
                with self.subTest(url=url), self.assertRaisesRegex(ValueError, "official Battery Commons path"):
                    read_bytes(url, allow_network=True)

    def test_public_submission_templates_match_registry_permissions(self):
        for name in ("submit-style.yml", "submit-layout.yml"):
            template = (ROOT / ".github/ISSUE_TEMPLATE" / name).read_text(encoding="utf-8")
            self.assertRegex(template, r"允许项目自动生成预览[^\n]*\n\s+required: true")
            self.assertIn("模型训练", template)


if __name__ == "__main__":
    unittest.main()
