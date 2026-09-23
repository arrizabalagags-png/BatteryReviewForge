"""Tests for the scientific gates and reproducible export."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "battery-review-figure" / "scripts"))

from batteryplot import DataContractError, comparison_bars, conditions_matrix, cycle_retention, rate_capability, save_bundle  # noqa: E402


BASE = {
    "source_id": "doi:demo/1", "evidence_state": "verified", "chemistry": "Li-ion",
    "cell_configuration": "coin half-cell", "temperature_c": "25",
    "loading_mg_cm2": "2.0", "electrolyte_ul_mg": "10",
}


class BatteryPlotTests(unittest.TestCase):
    def test_direct_comparison_rejects_changed_condition(self):
        rows = [
            {**BASE, "series": "A", "cycle": "0", "retention_pct": "100", "retention_basis": "initial", "rate": "1 C"},
            {**BASE, "series": "B", "cycle": "0", "retention_pct": "90", "retention_basis": "initial", "rate": "2 C"},
        ]
        with self.assertRaisesRegex(DataContractError, "conditions differ"):
            cycle_retention(rows)
        with self.assertRaisesRegex(DataContractError, "condition_note"):
            cycle_retention(rows, mode="contextual")
        fig, _ = cycle_retention(rows, mode="contextual", condition_note="Rates differ")
        self.assertEqual(fig.batteryplot_meta["comparison"], "contextual")

    def test_unverified_numeric_values_are_blocked(self):
        row = {**BASE, "evidence_state": "NV", "label": "A", "value": "123",
               "metric_unit": "mAh g-1", "metric_basis": "active mass", "rate": "1 C"}
        with self.assertRaisesRegex(DataContractError, "author-checked values"):
            comparison_bars([row], metric_label="Capacity")

    def test_missing_context_and_partial_uncertainty_are_blocked(self):
        base_bar = {**BASE, "label": "A", "value": "123", "metric_unit": "mAh/g",
                    "metric_basis": "active mass", "rate": "1 C", "uncertainty": "3"}
        with self.assertRaisesRegex(DataContractError, "Uncertainty is missing"):
            comparison_bars([base_bar, {**base_bar, "label": "B", "uncertainty": ""}],
                            metric_label="Capacity", uncertainty_label="SD")
        with self.assertRaisesRegex(DataContractError, "conditions matrix"):
            comparison_bars([{**base_bar, "loading_mg_cm2": "NR"}],
                            metric_label="Capacity", uncertainty_label="SD")

    def test_rate_preserves_recovery_step_and_rejects_missing_step(self):
        common = {**BASE, "capacity_unit": "mAh g-1", "capacity_basis": "active mass"}
        rows = [
            {**common, "series": series, "step": str(step), "rate_label": label, "capacity": str(value)}
            for series, values in (("A", (150, 110, 145)), ("B", (140, 90, 132)))
            for step, (label, value) in enumerate(zip(("0.1 C", "2 C", "0.1 C"), values))
        ]
        fig, ax = rate_capability(rows)
        self.assertEqual([tick.get_text() for tick in ax.get_xticklabels()], ["0.1 C", "2 C", "0.1 C"])
        self.assertEqual(list(ax.lines[0].get_ydata()), [150.0, 110.0, 145.0])
        with self.assertRaisesRegex(DataContractError, "sequences differ"):
            rate_capability(rows[:-1])
        matplotlib.pyplot.close(fig)

    def test_matrix_preserves_nr_nv_and_export_trace(self):
        rows = [{"source_id": "doi:demo/1", "label": "A", "loading": "2", "pressure": "NR"},
                {"source_id": "doi:demo/2", "label": "B", "loading": "NV", "pressure": "1"}]
        fig, ax = conditions_matrix(rows, ("loading", "pressure"))
        self.assertEqual(ax.images[0].get_array().tolist(), [[2, 1], [0, 2]])
        with tempfile.TemporaryDirectory() as temp:
            files = save_bundle(fig, Path(temp) / "matrix", claim="Demo", source_data="test fixture",
                                caption_notes="NR and NV are different", formats=("pdf", "svg", "png"), close=True)
            self.assertEqual(len(files), 4)
            self.assertTrue(all(path.exists() for path in files))
            payload = json.loads(files[-1].read_text(encoding="utf-8"))
            self.assertEqual(payload["source_ids"], ["doi:demo/1", "doi:demo/2"])
            self.assertEqual(payload["qa_status"], "requires_human_review")


if __name__ == "__main__":
    unittest.main()
