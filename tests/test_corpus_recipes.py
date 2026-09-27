"""Scientific guardrails and CLI smoke for optional corpus figure grammars."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / 'examples/showcase'
sys.path.insert(0, str(ROOT / 'skills/battery-review-figure/scripts'))
from batteryplot.corpus import CORPUS_RECIPES
from batteryplot.specialist import RECIPES, render_recipe


class CorpusRecipeTests(unittest.TestCase):
    def _copy(self, recipe, target):
        shutil.copytree(SHOWCASE / recipe, target, ignore=shutil.ignore_patterns('figure.*', 'render-report.json', 'alignment.json'))

    @staticmethod
    def _change_csv(path, change):
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        change(rows)
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _change_meta(path, change):
        data = json.loads(path.read_text(encoding='utf-8'))
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def test_all_recipes_are_optional_and_physically_aligned(self):
        self.assertTrue(set(CORPUS_RECIPES) <= set(RECIPES))
        for recipe in CORPUS_RECIPES:
            with self.subTest(recipe=recipe):
                meta = json.loads((SHOWCASE / recipe / 'metadata.json').read_text(encoding='utf-8'))
                self.assertEqual(meta['figure_grammar_id'], f'optional:{recipe}')
                self.assertFalse(meta['reference']['default_template'])
                self.assertEqual(meta['data_status'], 'synthetic_demo')
                self.assertTrue(meta['reference']['doi'])
                fig, report = render_recipe(recipe, SHOWCASE / recipe)
                try:
                    self.assertEqual(report['status'], 'optional_variant')
                    self.assertEqual(report['alignment']['status'], 'pass')
                    self.assertEqual(len(report['alignment']['checks']), 3)
                    self.assertEqual(report['reference']['doi'], meta['reference']['doi'])
                    self.assertEqual(set(report['source_files']), set(meta['source_files']))
                finally:
                    plt.close(fig)

    def test_nonfinite_or_unphysical_spectra_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'ftir'
            self._copy('ftir', folder)
            self._change_csv(folder / 'data.csv', lambda rows: rows[0].__setitem__('transmittance_percent', '101'))
            with self.assertRaisesRegex(ValueError, '0..100'):
                render_recipe('ftir', folder)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'nmr'
            self._copy('nmr', folder)
            self._change_meta(folder / 'metadata.json', lambda data: data['render_options'].pop('chemical_shift_reference'))
            with self.assertRaisesRegex(ValueError, 'chemical_shift_reference'):
                render_recipe('nmr', folder)

    def test_rdf_and_msd_do_not_silently_reorder_or_infer(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'rdf'
            self._copy('rdf_coordination', folder)
            self._change_csv(folder / 'data.csv', lambda rows: rows[8].__setitem__('coordination_number', '-0.2'))
            with self.assertRaisesRegex(ValueError, 'cumulative coordination'):
                render_recipe('rdf_coordination', folder)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'rdf'
            self._copy('rdf_coordination', folder)
            def shift_coordination_tail(rows):
                for row in rows[120:550]:
                    row['coordination_number'] = str(float(row['coordination_number']) + .2)
            self._change_csv(folder / 'data.csv', shift_coordination_tail)
            with self.assertRaisesRegex(ValueError, 'inconsistent with'):
                render_recipe('rdf_coordination', folder)
        with (SHOWCASE / 'rdf_coordination' / 'data.csv').open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        for pair in {row['pair'] for row in rows}:
            group = [row for row in rows if row['pair'] == pair]
            self.assertLess(float(group[0]['g_r']), .01)
            self.assertAlmostEqual(float(group[-1]['g_r']), 1.0, delta=.02)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'msd'
            self._copy('msd', folder)
            self._change_csv(folder / 'data.csv', lambda rows: rows[2].__setitem__('time_ps', rows[1]['time_ps']))
            with self.assertRaisesRegex(ValueError, 'strictly increasing'):
                render_recipe('msd', folder)

    def test_lsv_conditions_and_transference_complete_parameters(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'lsv'
            self._copy('lsv', folder)
            self._change_meta(folder / 'metadata.json', lambda data: data['render_options'].pop('working_electrode'))
            with self.assertRaisesRegex(ValueError, 'working_electrode'):
                render_recipe('lsv', folder)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'transference'
            self._copy('transference', folder)
            self._change_meta(folder / 'metadata.json', lambda data: data['render_options'].update(known_parameters={}))
            fig, report = render_recipe('transference', folder)
            plt.close(fig)
            self.assertEqual(report['calculations'], {})
            self._change_meta(folder / 'metadata.json', lambda data: data['render_options'].update(
                known_parameters={'A': {'initial_current_mA': .04, 'steady_current_mA': .03}}))
            with self.assertRaisesRegex(ValueError, 'require exactly'):
                render_recipe('transference', folder)

    def test_transference_uses_resistance_corrected_formula(self):
        fig, report = render_recipe('transference', SHOWCASE / 'transference')
        plt.close(fig)
        values = report['calculations']['A']['inputs']
        i0 = values['initial_current_mA'] / 1000
        iss = values['steady_current_mA'] / 1000
        dv = values['polarization_voltage_V']
        expected = iss * (dv - i0 * values['initial_resistance_ohm']) / (
            i0 * (dv - iss * values['steady_resistance_ohm']))
        self.assertAlmostEqual(report['calculations']['A']['tLi_plus'], expected)
        self.assertNotAlmostEqual(report['calculations']['A']['tLi_plus'], iss/i0)

    def test_public_cli_exports_all_formats_without_overwriting_input(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'rendered'
            script = ROOT / 'skills/battery-review-figure/scripts/render_specialist.py'
            subprocess.run([sys.executable, str(script), '--recipe', 'ftir',
                            '--input-folder', str(SHOWCASE / 'ftir'), '--output-dir', str(out)],
                           check=True, capture_output=True, text=True)
            self.assertTrue(all((out / f'figure.{suffix}').is_file() for suffix in ('png', 'svg', 'pdf')))
            report = json.loads((out / 'provenance.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'], 'optional_variant')
            self.assertIn('data.csv', report['input_sha256'])
            self.assertEqual(report['alignment']['status'], 'pass')


if __name__ == '__main__':
    unittest.main()
