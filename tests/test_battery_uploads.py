"""End-to-end checks for uploaded battery tables and their scientific gates."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "battery-review-figure" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from batteryplot import (  # noqa: E402
    DataContractError, coulombic_efficiency, cycling_capacity, inspect_table,
    read_table, symmetric_voltage, tofsims_map, tofsims_depth,
)


BASE = {
    "source_id": "test:synthetic", "evidence_state": "verified",
    "chemistry": "synthetic Li metal", "cell_configuration": "half cell",
    "temperature_c": "25", "electrolyte_ul_mg": "10",
    "rate": "1 C", "loading_mg_cm2": "2", "voltage_window_v": "2.5-4.2",
}


class UploadedBatteryPlotTests(unittest.TestCase):
    def test_tofsims_requires_complete_calibrated_map(self):
        common={"source_id":"test:ion-map","evidence_state":"verified",
                "sample_id":"Li-cycled","fragment":"LiF2-","signal_unit":"counts",
                "normalization":"none","ion_polarity":"negative",
                "measurement_state":"cycled, transferred under inert atmosphere"}
        rows=[{**common,"x_um":x,"y_um":y,"signal":v}
              for x,y,v in [(0,0,3),(1,0,5),(0,1,4),(1,1,6)]]
        fig,ax=tofsims_map(rows,sample_id="Li-cycled",fragment="LiF2-")
        self.assertEqual(fig.batteryplot_meta["chart"],"tofsims_map")
        self.assertEqual(ax.images[0].get_array().shape,(2,2))
        plt.close(fig)
        with self.assertRaisesRegex(DataContractError,"Incomplete or duplicate"):
            tofsims_map(rows[:-1],sample_id="Li-cycled",fragment="LiF2-")

    def test_tofsims_depth_preserves_sputter_time(self):
        common={"source_id":"test:ion-depth","evidence_state":"verified",
                "sample_id":"Li-cycled","signal_unit":"a.u.",
                "normalization":"per-fragment maximum","ion_polarity":"negative",
                "measurement_state":"cycled, transferred under inert atmosphere"}
        rows=[{**common,"fragment":fragment,"sputter_time_s":time,"signal":signal}
              for fragment,values in [("LiF2-",[(0,.2),(30,.8)]),("C2HO-",[(0,.9),(30,.3)])]
              for time,signal in values]
        fig,ax=tofsims_depth(rows,sample_id="Li-cycled")
        self.assertEqual(list(ax.lines[0].get_xdata()),[0.0,30.0])
        self.assertIn("Sputter time",ax.get_xlabel())
        plt.close(fig)
        rows[-1]["sputter_time_s"]=20
        with self.assertRaisesRegex(DataContractError,"different sputter-time grids"):
            tofsims_depth(rows,sample_id="Li-cycled")

    def test_ce_ratio_is_explicit_and_never_clipped(self):
        rows = [
            {**BASE, "series": "A", "cycle": str(cycle), "ce_definition": "discharge/charge",
             "ce_numerator": str(discharge), "ce_denominator": "100"}
            for cycle, discharge in [(1, 99), (2, 101)]
        ]
        fig, ax = coulombic_efficiency(rows)
        self.assertEqual(list(ax.lines[0].get_ydata()), [99.0, 101.0])
        self.assertEqual(fig.batteryplot_meta["calculation_note"], "CE = 100 × ce_numerator / ce_denominator")
        plt.close(fig)
        rows[0]["ce_denominator"] = "0"
        with self.assertRaisesRegex(DataContractError, "denominator"):
            coulombic_efficiency(rows)

    def test_full_and_half_cell_cannot_be_mixed(self):
        rows = [{**BASE, "series": "A", "cycle": "1", "discharge_capacity": "145",
                 "capacity_basis": "cathode active mass", "capacity_unit": "mAh g-1"}]
        with self.assertRaisesRegex(DataContractError, "full cell"):
            cycling_capacity(rows, cell_configuration="full")
        fig, _ = cycling_capacity(rows, cell_configuration="half")
        plt.close(fig)

    def test_symmetric_comparison_requires_matching_protocol(self):
        rows = [
            {**BASE, "cell_configuration": "Li|Li symmetric",
             "series": name, "time_h": "1", "voltage_mv": value,
             "current_density_ma_cm2": density, "areal_capacity_mah_cm2": "1",
             "pressure_mpa": "0.1"}
            for name, value, density in [("A", "10", "1"), ("B", "13", "2")]
        ]
        with self.assertRaisesRegex(DataContractError, "conditions differ"):
            symmetric_voltage(rows)

    def test_cross_source_ce_with_unknown_protocol_is_not_direct(self):
        rows = [
            {**BASE, "source_id": f"synthetic:{name}", "series": name,
             "cycle": "1", "ce_pct": "99", "ce_definition": "discharge/charge"}
            for name in ("A", "B")
        ]
        with self.assertRaisesRegex(DataContractError, "conditions not declared"):
            coulombic_efficiency(rows)
        same_paper_rows = [{**row, "source_id": "synthetic:same-paper"} for row in rows]
        with self.assertRaisesRegex(DataContractError, "conditions not declared"):
            coulombic_efficiency(same_paper_rows)
        fig, _ = coulombic_efficiency(
            rows, mode="contextual", condition_note="CE protocols not fully documented"
        )
        self.assertEqual(fig.batteryplot_meta["comparison"], "contextual")
        plt.close(fig)

    def test_csv_xlsx_inspect_and_plot_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "ce.csv"
            rows = [{"sample": "A", "cycle_no": "1", "eff": "99.2"},
                    {"sample": "A", "cycle_no": "2", "eff": "99.7"}]
            with data.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            self.assertEqual(read_table(data), rows)
            self.assertEqual(inspect_table(rows)["row_count"], 2)
            config = {
                "kind": "coulombic_efficiency", "claim": "Synthetic CE example",
                "style": "rose_blue",
                "caption_notes": "Synthetic, not real evidence.",
                "columns": {"series": "sample", "cycle": "cycle_no", "ce_pct": "eff"},
                "common": {**BASE, "ce_definition": "discharge/charge"},
            }
            metadata = root / "mapping.json"
            metadata.write_text(json.dumps(config), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "plot_uploaded.py"), "plot",
                 "--data", str(data), "--metadata", str(metadata), "--out", str(root / "ce_plot")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "ce_plot.pdf").exists())
            self.assertTrue((root / "ce_plot.png").exists())
            self.assertEqual(json.loads((root / "ce_plot.provenance.json").read_text(encoding="utf-8"))["chart"],
                             "coulombic_efficiency")
            self.assertEqual(json.loads((root / "ce_plot.provenance.json").read_text(encoding="utf-8"))["style"],
                             "rose_blue")
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Test"
            sheet.append(["series", "cycle", "ce_pct"])
            sheet.append(["A", 1, 99.2])
            path = root / "ce.xlsx"
            workbook.save(path)
            self.assertEqual(read_table(path)[0]["ce_pct"], "99.2")

    def test_extra_csv_cells_are_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.csv"
            path.write_text("cycle,ce_pct\n1,99,unexpected\n", encoding="utf-8")
            with self.assertRaisesRegex(DataContractError, "more cells"):
                read_table(path)


if __name__ == "__main__":
    unittest.main()
