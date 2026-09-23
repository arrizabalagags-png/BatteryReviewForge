"""Test geometry, fidelity gates, and vector/raster assembly."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "battery-figure-assemble" / "scripts"))
from batterycompose import ComposeError, compose, resolve_layout  # noqa: E402
from batterycompose.inventory import inventory  # noqa: E402


def fixture(root: Path) -> dict:
    sources = root / "sources"
    sources.mkdir()
    for name in ("a.png", "b.png"):
        Image.new("RGB", (1200, 700), "#F7F8F8").save(sources / name)
    pdf = canvas.Canvas(str(sources / "vector.pdf"), pagesize=(600, 350))
    pdf.setFont("Helvetica", 16)
    pdf.drawString(30, 180, "VECTOR_SOURCE_TEXT")
    pdf.save()
    return {"version": 1, "figure_id": "Fig. T", "claim": "Test layout fidelity.",
            "width_mm": 180, "margin_mm": 4, "gutter_mm": 2,
            "row_heights_mm": [46], "col_weights": [1, 1], "label_band_mm": 4,
            "dpi": 300, "_manifest_path": str(root / "manifest.json"),
            "panels": [
                {"label": "a", "path": "sources/a.png", "role": "left", "source_id": "test-a",
                 "rights_status": "original", "row": 0, "col": 0},
                {"label": "b", "path": "sources/b.png", "role": "right", "source_id": "test-b",
                 "rights_status": "original", "row": 0, "col": 1},
            ]}


class ComposeTests(unittest.TestCase):
    def test_grid_edges_and_gutter_are_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            layout = resolve_layout(fixture(Path(temp)))
            a, b = (panel["slot_mm"] for panel in layout["panels"])
            self.assertAlmostEqual(a[0], 4)
            self.assertAlmostEqual(b[0] - (a[0] + a[2]), 2)
            self.assertAlmostEqual(a[1], b[1])
            self.assertAlmostEqual(a[3], b[3])

    def test_zero_gutter_is_valid_for_contiguous_panels(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = fixture(Path(temp))
            manifest["margin_mm"] = 0
            manifest["gutter_mm"] = 0
            layout = resolve_layout(manifest)
            a, b = (panel["slot_mm"] for panel in layout["panels"])
            self.assertAlmostEqual(a[0] + a[2], b[0])

    def test_overlap_and_unexplained_crop_are_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = fixture(Path(temp))
            manifest["panels"][1]["col"] = 0
            with self.assertRaisesRegex(ComposeError, "overlaps"):
                resolve_layout(manifest)
            manifest["panels"][1]["col"] = 1
            manifest["panels"][0]["crop_px"] = [1, 1, 500, 500]
            with self.assertRaisesRegex(ComposeError, "crop_reason"):
                resolve_layout(manifest)

    def test_composition_keeps_vector_text_and_reports_raster_dpi(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = fixture(root)
            manifest["panels"][1]["path"] = "sources/vector.pdf"
            report = compose(manifest, root / "out")
            self.assertTrue((root / "out.pdf").exists())
            self.assertTrue((root / "out.png").exists())
            self.assertTrue((root / "out.qa.json").exists())
            self.assertEqual(report["panels"][0]["kind"], "raster")
            self.assertGreater(report["panels"][0]["effective_dpi"], 300)
            self.assertEqual(report["panels"][1]["kind"], "vector")
            font_panels = report["font_audit"]["panels"]
            self.assertEqual(font_panels[0]["status"], "raster_text_unmeasurable")
            self.assertEqual(font_panels[1]["status"], "review_small_text")
            self.assertLess(font_panels[1]["min_pt"], 6)
            page = PdfReader(root / "out.pdf").pages[0]
            self.assertIn("VECTOR_SOURCE_TEXT", page.extract_text())
            self.assertAlmostEqual(float(page.mediabox.width) / 72 * 25.4, 180, places=3)

    def test_low_dpi_strict_blocks_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = fixture(root)
            Image.new("RGB", (100, 70), "white").save(root / "sources" / "a.png")
            with self.assertRaisesRegex(ComposeError, "effective raster resolution"):
                compose(manifest, root / "strict", strict=True)
            self.assertFalse((root / "strict.pdf").exists())

    def test_alignment_group_needs_plot_rects(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = fixture(root)
            for panel in manifest["panels"]:
                panel["alignment_group"] = "row-1"
            with self.assertRaisesRegex(ComposeError, "plot_box_fraction"):
                compose(manifest, root / "strict", strict=True)

    def test_inventory_reports_all_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            result = inventory(root / "sources", root / "inspection")
            self.assertEqual(result["count"], 3)
            self.assertTrue((root / "inspection" / "contact-01.png").exists())
            self.assertEqual(len(json.loads((root / "inspection" / "inventory.json").read_text(encoding="utf-8"))["assets"]), 3)

    def test_svg_external_reference_and_bad_label_band_are_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = fixture(root)
            manifest["label_band_mm"] = 0
            with self.assertRaisesRegex(ComposeError, "label_band_mm"):
                resolve_layout(manifest)
            manifest["label_band_mm"] = 4
            svg = root / "sources" / "unsafe.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"><style>rect{fill:url(https://example.com/a.svg)}</style><rect width="100" height="50"/></svg>', encoding="utf-8")
            manifest["panels"][1]["path"] = "sources/unsafe.svg"
            with self.assertRaisesRegex(ComposeError, "external style"):
                compose(manifest, root / "unsafe")

    def test_actual_plot_box_drift_blocks_strict_assembly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = fixture(root)
            for panel in manifest["panels"]:
                panel["alignment_group"] = "cycling-pair"
            manifest["panels"][0]["plot_box_fraction"] = [0.05, 0.1, 0.95, 0.9]
            manifest["panels"][1]["plot_box_fraction"] = [0.05, 0.25, 0.95, 0.9]
            with self.assertRaisesRegex(ComposeError, "plot-area rows differ"):
                compose(manifest, root / "misaligned", strict=True)


if __name__ == "__main__":
    unittest.main()
