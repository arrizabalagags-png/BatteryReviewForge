"""Check that the public grammar cannot silently promote unsupported pairings."""

import json
from pathlib import Path
import unittest


BASE = Path(__file__).resolve().parents[1] / "skills" / "battery-review-figure" / "references"


class FigureGrammarTests(unittest.TestCase):
    def test_types_and_primary_evidence_are_consistent(self):
        grammar = json.loads((BASE / "BATTERY_FIGURE_GRAMMAR.json").read_text(encoding="utf-8"))
        evidence = json.loads((BASE / "PANEL_EVIDENCE.json").read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in grammar["types"]]
        self.assertGreaterEqual(len(ids), 45)
        self.assertEqual(len(ids), len(set(ids)))
        for figure in evidence["figures"]:
            self.assertTrue(figure["doi"].startswith("10."))
            self.assertEqual(figure["verification"], "caption_and_figure_page_inspected")
            panels = {panel["panel"] for panel in figure["panels"]}
            for panel in figure["panels"]:
                self.assertIn(panel["type"], ids)
                self.assertTrue(panel["x"] and panel["y"] and panel["role"])
                for paired in panel["paired_with"]:
                    self.assertEqual(str(figure["figure"]), paired[:-1])
                    self.assertIn(paired[-1], panels)
        for pair in grammar["validated_pairings"]:
            self.assertEqual(pair["status"], "default_option")
            self.assertTrue(set(pair["members"]) <= set(ids))
            self.assertGreaterEqual(len({item.split()[0] for item in pair["independent_primary_papers"]}), 3)

    def test_journal_profiles_are_attributed(self):
        profiles = json.loads((BASE / "JOURNAL_FIGURE_SPEC.json").read_text(encoding="utf-8"))
        self.assertIn("not a publisher", profiles["journal_neutral"]["source"])
        for key in ("nature", "acs_chemical_reviews", "wiley_general", "rsc_advances"):
            self.assertTrue(profiles[key]["source"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
