"""Cross-panel scientific consistency checks for the explicitly synthetic demos."""
import csv
import json
from pathlib import Path
import unittest
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1] / "examples" / "showcase"
sys.path.insert(0, str(ROOT))
from build import impedance, plot_ce, plot_eis, style_presets_figure, figure, curve_style_audit
import matplotlib.pyplot as plt


def rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class ShowcaseDataTest(unittest.TestCase):
    def test_capacity_and_composite_exports_reject_point_markers(self):
        for name in ("full_cell", "rate_capability", "capability_spread", "integrated_study"):
            with self.subTest(name=name):
                fig=figure(name)
                try:
                    checks=curve_style_audit(fig)
                    self.assertTrue(checks)
                    self.assertTrue(all(c["line_style"]=="-" and c["marker"] in (None,"None",""," ") for c in checks))
                    data_axes=[ax for ax in fig.axes if ax.axison and not hasattr(ax,"_colorbar")]
                    self.assertTrue(all(ax.spines[side].get_visible() for ax in data_axes
                                        for side in ("top","right","bottom","left")))
                    # A leaked legacy marker must stop the export even when data are unchanged.
                    line=next(line for ax in fig.axes for line in ax.lines)
                    line.set_marker("o")
                    with self.assertRaisesRegex(ValueError, "without markers"):
                        curve_style_audit(fig)
                    line.set_marker("None")
                    data_axes[0].spines["top"].set_visible(False)
                    with self.assertRaisesRegex(ValueError, "four frame spines"):
                        curve_style_audit(fig)
                finally:
                    plt.close(fig)

    def test_scientific_preview_styles_and_nyquist_geometry(self):
        fig, axes = plt.subplots(2, 2, figsize=(6, 5))
        try:
            plot_ce(axes[0, 0], axes[0, 1])
            plot_eis(axes[1, 0], axes[1, 1])
            fig.canvas.draw()
            for ax in axes.flat:
                self.assertTrue(all(line.get_linestyle() == "-" for line in ax.lines))
            self.assertTrue(all(line.get_marker() in (None, "None", "") for line in axes[0, 0].lines))
            self.assertEqual(len({line.get_color() for line in axes[0, 1].lines}), 4)
            points = axes[1, 0].transData.transform([[0, 0], [1, 1]])
            self.assertAlmostEqual(*(points[1] - points[0]), places=6)
        finally:
            plt.close(fig)
        fig = style_presets_figure()
        try:
            for ax in fig.axes:
                self.assertTrue(all(line.get_linestyle() == "-" for line in ax.lines[:2]))
                self.assertNotEqual(ax.lines[0].get_color(), ax.lines[1].get_color())
        finally:
            plt.close(fig)

    def test_full_cell_profiles_share_cycling_endpoints(self):
        cycling = {int(r["cycle"]): float(r["A_mAh_g"]) for r in rows(ROOT / "full_cell/data.csv")}
        profiles = rows(ROOT / "full_cell/voltage_profiles.csv")
        for cycle in (1, 100, 300, 500):
            selected = [r for r in profiles if int(r["cycle"]) == cycle]
            self.assertGreater(len(selected), 100)
            self.assertAlmostEqual(float(selected[-1]["capacity_mAh_g"]), cycling[cycle], places=3)
            self.assertAlmostEqual(float(selected[-1]["cycling_endpoint_mAh_g"]), cycling[cycle], places=3)

    def test_li_cu_profiles_encode_same_cycle_ce(self):
        cycling = {int(r["cycle"]): r for r in rows(ROOT / "li_cu_ce/data.csv")}
        profiles = rows(ROOT / "li_cu_ce/profiles.csv")
        for sample in ("A", "B"):
            for cycle in (1, 100, 300):
                strip = [r for r in profiles if r["sample"] == sample and int(r["cycle"]) == cycle and r["stage"] == "strip"]
                ce = float(cycling[cycle][f"{sample}_ce_pct"])
                self.assertAlmostEqual(float(strip[-1]["capacity_mAh_cm2"]), ce / 100, places=4)
                self.assertAlmostEqual(float(strip[-1]["cycle_ce_pct"]), ce, places=4)

    def test_eis_is_complex_impedance_from_declared_circuit(self):
        model = json.loads((ROOT / "eis/model.json").read_text(encoding="utf-8"))
        self.assertIn("Warburg", model["circuit"])
        for r in rows(ROOT / "eis/data.csv"):
            p = model["parameters"][r["sample"]]
            frequency = float(r["frequency_Hz"])
            jw = 2j * np.pi * frequency
            warburg = p["Warburg_sigma"] * (1 - 1j) / np.sqrt(2 * np.pi * frequency)
            expected = p["Rs_ohm"] + 1 / (p["CPE_Q"] * jw ** p["CPE_alpha"] + 1 / (p["Rct_ohm"] + warburg))
            self.assertAlmostEqual(float(r["Zreal_ohm"]), expected.real, places=5)
            self.assertAlmostEqual(float(r["Zimag_ohm"]), expected.imag, places=5)

    def test_randles_limiting_cases(self):
        # Independent analytic RC-circle identity, high-frequency intercept,
        # and low-frequency Warburg slope catch topology/convention regressions.
        f = np.logspace(6, -6, 160)
        z = impedance(f, 4.2, 23, .00085, 1.0, 0.0)
        np.testing.assert_allclose((z.real - (4.2 + 23/2))**2 + z.imag**2, (23/2)**2, rtol=1e-10)
        high = impedance(np.array([1e15]), 4.2, 23, .00085, .86, 3.0)[0]
        self.assertAlmostEqual(high.real, 4.2, places=7)
        low = impedance(np.array([1e-10, 1e-11]), 4.2, 23, .00085, .86, 3.0)
        slope = -(low[1].imag-low[0].imag)/(low[1].real-low[0].real)
        self.assertAlmostEqual(slope, 1.0, places=4)

    def test_integrated_study_references_same_sources(self):
        manifest = json.loads((ROOT / "integrated_study/sources.json").read_text(encoding="utf-8"))
        for source in manifest["uses"]:
            self.assertTrue((ROOT / "integrated_study" / source).resolve().is_file())
        self.assertIn("no mechanistic inference", manifest["status"])


if __name__ == "__main__":
    unittest.main()
