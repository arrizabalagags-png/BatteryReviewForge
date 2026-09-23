"""Check user-selected palette behavior and original SVG recoloring."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "battery-review-figure" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from batteryplot import coulombic_efficiency  # noqa: E402
from batteryplot.style import PRESETS  # noqa: E402


def contrast_on_white(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
              for value in channels]
    luminance = sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))
    return 1.05 / (luminance + 0.05)


class StyleTests(unittest.TestCase):
    def test_all_plot_series_are_visible_against_white(self):
        self.assertEqual(len(PRESETS), 6)
        for name, preset in PRESETS.items():
            with self.subTest(style=name):
                self.assertEqual(len(preset["series"]), 5)
                self.assertTrue(all(contrast_on_white(color) >= 3.0 for color in preset["series"]))

    def test_selected_style_changes_chart_and_provenance(self):
        common = {"source_id": "test:synthetic", "evidence_state": "verified",
                  "chemistry": "synthetic Li", "cell_configuration": "half cell",
                  "temperature_c": "25", "ce_definition": "discharge/charge", "rate": "1 C",
                  "current_density_ma_cm2": "1", "areal_capacity_mah_cm2": "1",
                  "cutoff_rule": "synthetic cutoff", "ce_protocol": "synthetic protocol",
                  "loading_mg_cm2": "2", "electrolyte_ul_mg": "10",
                  "voltage_window_v": "2.5-4.2"}
        rows = [{**common, "series": name, "cycle": "1", "ce_pct": value}
                for name, value in (("A", "98.9"), ("B", "99.2"))]
        fig, ax = coulombic_efficiency(rows, style="rose_blue")
        try:
            self.assertEqual(ax.lines[0].get_color(), PRESETS["rose_blue"]["series"][0])
            self.assertEqual(ax.lines[1].get_color(), PRESETS["rose_blue"]["series"][1])
            self.assertEqual(ax.lines[0].get_linewidth(), PRESETS["rose_blue"]["line_pt"])
            self.assertEqual(fig.batteryplot_meta["style"], "rose_blue")
        finally:
            plt.close(fig)

    def test_cli_demands_a_style_instead_of_guessing(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            data = folder / "ce.csv"
            data.write_text("series,cycle,ce_pct\nA,1,99\n", encoding="utf-8")
            metadata = folder / "metadata.json"
            metadata.write_text(json.dumps({"kind": "coulombic_efficiency"}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "plot_uploaded.py"), "plot", "--data", str(data),
                 "--metadata", str(metadata), "--out", str(folder / "chart")],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing style", result.stderr)

    def test_only_original_svg_palette_is_recolored(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "lab.svg"
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "render_template.py"),
                 "--template", "battery-lab-primitives", "--style", "thermal_balance",
                 "--out", str(output)], capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn(PRESETS["thermal_balance"]["roles"]["new_or_intervention"], text)
            self.assertNotIn("#348678", text)
            self.assertIn('id="coin-cell"', text)


if __name__ == "__main__":
    unittest.main()
