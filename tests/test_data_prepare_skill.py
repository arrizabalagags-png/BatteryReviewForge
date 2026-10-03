"""Traceability gates for explicit CSV mapping and exclusions."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'skills/voltpeer-data/scripts/prepare_csv.py'
spec = importlib.util.spec_from_file_location('prepare_csv', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DataPrepareTests(unittest.TestCase):
    def make(self, folder):
        raw = folder/'raw.csv'
        raw.write_text('Cycle Index,Discharge capacity,Flag\n1,180,ok\n2,179,ok\n3,bad,setup\n', encoding='utf-8')
        mapping = folder/'mapping.json'
        mapping.write_text(json.dumps({'columns': {'cycle': 'Cycle Index', 'capacity': 'Discharge capacity'},
                                       'units': {'cycle': 'count', 'capacity': 'mAh g-1'},
                                       'numeric_columns': ['cycle', 'capacity'],
                                       'author_confirmed': True,
                                       'plot_context': 'Author checked cell ID, formation and capacity mass basis against lab record',
                                       'plot_context_confirmed': True,
                                       'exclude_rows': [{'row_number': 3, 'reason': 'Author flagged setup row'}]}), encoding='utf-8')
        return raw, mapping

    def test_explicit_exclusion_preserves_raw_and_record(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); raw, mapping = self.make(folder); before = raw.read_bytes()
            info = module.inspect(raw)
            self.assertEqual(info['data_rows'], 3)
            self.assertFalse(info['scientific_units_inferred'])
            record = module.prepare(raw, mapping, folder/'new')
            self.assertEqual(raw.read_bytes(), before)
            self.assertEqual(record['source_rows'], 3)
            self.assertEqual(record['retained_rows'], 2)
            self.assertEqual(record['unmapped_source_headers'], ['Flag'])
            self.assertTrue(record['ready_for_plot'])
            self.assertIn('bad,setup', (folder/'new/excluded-rows.csv').read_text(encoding='utf-8'))
            with self.assertRaisesRegex(ValueError, 'already exists'):
                module.prepare(raw, mapping, folder/'new')

    def test_bad_numeric_value_is_not_silently_deleted(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); raw, mapping = self.make(folder)
            data = json.loads(mapping.read_text(encoding='utf-8')); data['exclude_rows'] = []
            mapping.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Row 3'):
                module.prepare(raw, mapping, folder/'new')
            self.assertFalse((folder/'new').exists())

    def test_unknown_unit_remains_unready(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); raw, mapping = self.make(folder)
            data = json.loads(mapping.read_text(encoding='utf-8')); data['units']['capacity'] = 'unknown'
            mapping.write_text(json.dumps(data), encoding='utf-8')
            record = module.prepare(raw, mapping, folder/'new')
            self.assertFalse(record['ready_for_plot'])

    def test_unconfirmed_mapping_remains_unready(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); raw, mapping = self.make(folder)
            data = json.loads(mapping.read_text(encoding='utf-8')); data.pop('author_confirmed')
            mapping.write_text(json.dumps(data), encoding='utf-8')
            record = module.prepare(raw, mapping, folder/'new')
            self.assertFalse(record['author_confirmed_mapping_and_units'])
            self.assertFalse(record['ready_for_plot'])

    def test_unconfirmed_plot_context_remains_unready(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); raw, mapping = self.make(folder)
            data = json.loads(mapping.read_text(encoding='utf-8'))
            data.pop('plot_context_confirmed')
            mapping.write_text(json.dumps(data), encoding='utf-8')
            record = module.prepare(raw, mapping, folder/'new')
            self.assertFalse(record['author_confirmed_plot_context'])
            self.assertFalse(record['ready_for_plot'])

    def test_empty_plot_context_remains_unready(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); raw, mapping = self.make(folder)
            data = json.loads(mapping.read_text(encoding='utf-8'))
            data['plot_context'] = '  '
            mapping.write_text(json.dumps(data), encoding='utf-8')
            record = module.prepare(raw, mapping, folder/'new')
            self.assertFalse(record['ready_for_plot'])


if __name__ == '__main__': unittest.main()
