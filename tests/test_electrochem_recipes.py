"""Only science/contract gates for four optional electrochemistry views."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/voltpeer-plot/scripts'))
from batteryplot.electrochem import ELECTROCHEM_RECIPES
from batteryplot.specialist import RECIPES, render_recipe


class ElectrochemRecipeTests(unittest.TestCase):
    def copy_demo(self, name, folder):
        shutil.copytree(ROOT/'examples/showcase'/name, folder)

    def change_csv(self, folder, edit):
        path = folder/'data.csv'
        with path.open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
            fields = list(rows[0])
        edit(rows)
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader(); writer.writerows(rows)

    def change_meta(self, folder, edit):
        path = folder/'metadata.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        edit(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def test_all_optional_and_aligned(self):
        for name in ELECTROCHEM_RECIPES:
            with self.subTest(name=name):
                self.assertIn(name, RECIPES)
                folder = ROOT/'examples/showcase'/name
                fig, report = render_recipe(name, folder)
                self.assertEqual(report['status'], 'optional_variant')
                self.assertEqual(report['calculations'], {})
                self.assertEqual(report['alignment']['status'], 'pass')
                self.assertEqual(len(report['alignment']['checks']), 3)
                self.assertFalse(report['reference']['default_template'])
                self.assertEqual(set(report['source_files']), {'data.csv'})
                self.assertTrue((folder/'figure.png').is_file())
                self.assertTrue((folder/'figure.svg').is_file())
                self.assertTrue((folder/'figure.pdf').is_file())
                import matplotlib.pyplot as plt
                plt.close(fig)

    def test_aurbach_rejects_undeclared_or_repeated_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'protocol'; self.copy_demo('aurbach_protocol', folder)
            self.change_meta(folder, lambda m: m['render_options'].pop('capacity_schedule_mAh_cm2'))
            with self.assertRaisesRegex(ValueError, 'capacity_schedule'):
                render_recipe('aurbach_protocol', folder)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'protocol'; self.copy_demo('aurbach_protocol', folder)
            self.change_csv(folder, lambda rows: rows[140].__setitem__('stage', 'formation plate'))
            with self.assertRaisesRegex(ValueError, 'contiguous'):
                render_recipe('aurbach_protocol', folder)

    def test_eis_rejects_bad_frequency_and_preserves_signed_imaginary(self):
        folder = ROOT/'examples/showcase/eis_frequency'
        with (folder/'data.csv').open(encoding='utf-8', newline='') as stream:
            first = next(csv.DictReader(stream))
        self.assertLess(float(first['z_imag_ohm']), 0)
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp)/'eis'; self.copy_demo('eis_frequency', copy)
            self.change_csv(copy, lambda rows: rows[4].__setitem__('frequency_Hz', '0'))
            with self.assertRaisesRegex(ValueError, 'positive'):
                render_recipe('eis_frequency', copy)

    def test_ca_requires_declared_potential_and_ocv_no_capacity_calculation(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'ca'; self.copy_demo('chronoamperometry', folder)
            self.change_meta(folder, lambda m: m['render_options'].pop('applied_potential_V'))
            with self.assertRaisesRegex(ValueError, 'applied_potential'):
                render_recipe('chronoamperometry', folder)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'ocv'; self.copy_demo('ocv_rest', folder)
            self.change_csv(folder, lambda rows: rows[7].__setitem__('time_h', rows[6]['time_h']))
            with self.assertRaisesRegex(ValueError, 'strictly increasing'):
                render_recipe('ocv_rest', folder)

    def test_public_cli_exports_without_overwriting_input(self):
        source = ROOT/'examples/showcase/eis_frequency'
        original = (source/'data.csv').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)/'new-output'
            command = [sys.executable, str(ROOT/'skills/voltpeer-plot/scripts/render_specialist.py'),
                       '--recipe', 'eis_frequency', '--input-folder', str(source),
                       '--output-dir', str(output), '--style', 'forge']
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertTrue(all((output/f'figure.{ext}').is_file() for ext in ('png', 'svg', 'pdf')))
            self.assertEqual(json.loads((output/'provenance.json').read_text(encoding='utf-8'))['recipe'], 'eis_frequency')
        self.assertEqual((source/'data.csv').read_bytes(), original)


if __name__ == '__main__': unittest.main()
