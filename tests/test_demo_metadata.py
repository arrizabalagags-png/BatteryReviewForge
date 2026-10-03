"""The release gate must reject malformed metadata and stale distributed files."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from check_demo_metadata import validate_metadata, check_demo, MetadataError


class DemoMetadataTests(unittest.TestCase):
    def test_all_canonical_demo_schemas(self):
        files = list((ROOT/'examples/showcase').glob('*/metadata.json'))
        self.assertEqual(len(files), 30)
        for file in files:
            with self.subTest(file=file.parent.name):
                validate_metadata(json.loads(file.read_text(encoding='utf-8')))

    def test_schema_rejects_missing_and_false_declarations(self):
        source = json.loads((ROOT/'examples/showcase/full_cell/metadata.json').read_text(encoding='utf-8'))
        valid = copy.deepcopy(source)
        valid['limitations'] = 'Synthetic demonstration; not experimental evidence.'
        validate_metadata(valid)
        cases = []
        a = copy.deepcopy(source); del a['test_conditions']; cases.append(a)
        a = copy.deepcopy(source); a['not_experimental_data'] = 'true'; cases.append(a)
        a = copy.deepcopy(source); a['data_status'] = 'experimental'; cases.append(a)
        a = copy.deepcopy(source); a['source_files'] = []; cases.append(a)
        a = copy.deepcopy(source); a['data_frame_checks'][0]['spines']['top'] = False; cases.append(a)
        a = copy.deepcopy(source); a['unknown_passing_claim'] = True; cases.append(a)
        a = copy.deepcopy(source); a['limitations'] = ['not a string']; cases.append(a)
        a = copy.deepcopy(source); a['limitations'] = ''; cases.append(a)
        a = copy.deepcopy(source); a['render_options'] = {'invalid_number': float('nan')}; cases.append(a)
        for index, meta in enumerate(cases):
            with self.subTest(case=index), self.assertRaises(MetadataError):
                validate_metadata(meta)

    def test_zip_site_and_source_must_agree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root/'source/full_cell'; site = root/'site/full_cell'
            shutil.copytree(ROOT/'examples/showcase/full_cell', source)
            shutil.copytree(source, site)
            archive = root/'demo.zip'
            def pack(meta=None, stale_input=False):
                with ZipFile(archive, 'w', ZIP_DEFLATED) as out:
                    for file in source.iterdir():
                        if file.is_file():
                            if file.name == 'metadata.json' and meta is not None:
                                out.writestr('full_cell/metadata.json', json.dumps(meta))
                            elif file.name == 'data.csv' and stale_input:
                                out.writestr('full_cell/data.csv', 'stale input')
                            else:
                                out.write(file, 'full_cell/'+file.name)
            pack(); self.assertEqual(check_demo(source, site, archive)['schema'], 'PASS')
            meta = json.loads((source/'metadata.json').read_text(encoding='utf-8'))
            meta['test_conditions'] = 'Different conditions'
            pack(meta)
            with self.assertRaisesRegex(MetadataError, 'ZIP metadata differs'):
                check_demo(source, site, archive)
            pack(stale_input=True)
            with self.assertRaisesRegex(MetadataError, 'ZIP input differs'):
                check_demo(source, site, archive)
            pack(); (site/'metadata.json').write_text(json.dumps(meta), encoding='utf-8')
            with self.assertRaisesRegex(MetadataError, 'site metadata differs'):
                check_demo(source, site, archive)
