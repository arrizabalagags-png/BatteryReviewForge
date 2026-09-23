"""Cross-panel scientific consistency checks for the explicitly synthetic demos."""
import csv
import json
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1] / "examples" / "showcase"


def rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class ShowcaseDataTest(unittest.TestCase):
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
            expected = p["Rs_ohm"] + 1 / (1 / p["Rct_ohm"] + p["CPE_Q"] * jw ** p["CPE_alpha"]) + p["Warburg_sigma"] / np.sqrt(jw)
            self.assertAlmostEqual(float(r["Zreal_ohm"]), expected.real, places=5)
            self.assertAlmostEqual(float(r["Zimag_ohm"]), expected.imag, places=5)

    def test_integrated_study_references_same_sources(self):
        manifest = json.loads((ROOT / "integrated_study/sources.json").read_text(encoding="utf-8"))
        for source in manifest["uses"]:
            self.assertTrue((ROOT / "integrated_study" / source).resolve().is_file())
        self.assertIn("no mechanistic inference", manifest["status"])


if __name__ == "__main__":
    unittest.main()
