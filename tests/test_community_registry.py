"""Version pinning, hash checks and claim discipline for Battery Commons."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "battery-review-figure" / "scripts"))

from build_community_registry import validate  # noqa: E402
from community_registry import resolve  # noqa: E402
from batteryplot.style import PRESETS, register_community_style  # noqa: E402


class CommonsTest(unittest.TestCase):
    def test_catalog_matches_published_assets(self):
        catalog = json.loads((ROOT / "community/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["assets"]), 2)
        for item in catalog["assets"]:
            category = "styles" if item["category"] == "style" else "layouts"
            source = ROOT / "community" / category / f'{item["id"]}@{item["version"]}.json'
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), item["sha256"])
            self.assertEqual(validate(source)["status"], "community")
            self.assertEqual((ROOT / "docs/commons" / category / source.name).read_bytes(), source.read_bytes())

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
            result = resolve(str(catalog), "community:ocean-electrolyte@1.0.0", folder / "out", allow_network=False)
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
            resolved = resolve(str(catalog), "community:ocean-electrolyte@1.0.0", folder / "locks", allow_network=False)
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
            process = subprocess.run([sys.executable, str(ROOT / "skills/battery-review-figure/scripts/plot_uploaded.py"),
                "plot", "--data", str(data), "--metadata", str(metadata), "--out", str(output)],
                capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            record = json.loads(output.with_suffix(".provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(record["style"], "community:ocean-electrolyte@1.0.0")
            self.assertEqual(record["community_style"]["sha256"], digest)
            self.assertTrue(output.with_suffix(".svg").is_file())


if __name__ == "__main__":
    unittest.main()
