"""Blind-shape engineering adaptation checks. These are synthetic fixtures, not model EVALs."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('full_cell', 'li_li', 'operando_xrd')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8-sig')


def csv_write(path, columns, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RecipePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='VoltPeer 独立包 带空格 ')
        cls.workspace = Path(cls.temp.name)
        completed = subprocess.run([sys.executable, str(ROOT / 'scripts/package_recipe_packs.py'), '--out', str(cls.workspace / 'downloads')], capture_output=True, text=True, encoding='utf-8')
        if completed.returncode:
            raise RuntimeError(completed.stderr + completed.stdout)
        cls.packs = {}
        for archive in (cls.workspace / 'downloads').glob('*.zip'):
            with ZipFile(archive) as z:
                z.extractall(cls.workspace / '解压 单独运行')
        for kind in KINDS:
            cls.packs[kind] = cls.workspace / '解压 单独运行' / kind

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def command(self, pack, config, out):
        return subprocess.run([sys.executable, str(pack / 'src/plot.py'), '--config', str(config), '--out', str(out)], cwd=pack, capture_output=True, text=True, encoding='utf-8')

    def author_fixture(self, kind, folder):
        """Simulate fresh author-input shape, while documenting that fixture numbers are synthetic."""
        folder.mkdir()
        pack = self.packs[kind]
        config = json.loads((pack / 'config.real.example.json').read_text(encoding='utf-8'))
        config['provenance']['demo_conditions_cleared'] = True
        config['title'] = 'Engineering input-shape test; not experimental evidence'
        samples = ['New group ' + letter + ' with a deliberately long independently supplied label' for letter in 'ABC']
        config['labels'] = {samples[2]: '新样品C—中文名称与第三组较长图例'}
        common = config['conditions']['common']
        if kind == 'full_cell':
            common.update(cathode='Declared cathode X', anode='Declared anode Y', capacity_basis='Cathode active material mass', rate_or_current='Author declared 0.2 C', formation='Two recorded formation cycles', loading_or_areal_capacity='2.1 mAh cm^-2', temperature_C=23, voltage_window_V=[2.5, 4.5], N_P='not reported', E_C='not reported')
            config['units'] = {'cycle': '1', 'capacity': 'mAh g^-1', 'voltage': 'V', 'ce': '%'}
            rows = [(s, c, 450 - i * 90 - c * 2.5, 101 - c * .07) for i, s in enumerate(samples) for c in range(1, 5 + i * 3)]
            csv_write(folder / '新循环.csv', ['组别', '循环', '容量', '效率'], rows)
            config['data'] = {'cycling': {'path': '新循环.csv', 'columns': {'sample': '组别', 'cycle': '循环', 'capacity': '容量', 'ce': '效率'}}}
        elif kind == 'li_li':
            common.update(metal='Na', cell_configuration='Na||Na', area_basis='Projected geometric overlap electrode area', current_density_mA_cm2=.3, half_cycle_areal_capacity_mAh_cm2=.9, temperature_C=30, rest_protocol='Recorded 10 min after each half-cycle', failure_rule='Stop only on the author-defined 1 V criterion')
            config['units'] = {'time': 's', 'voltage': 'V'}
            rows = [(s, j * 50, (-1 if j % 2 else 1) * (.1 + .005 * i + .01 * j)) for i, s in enumerate(samples) for j in range(3 + i * 3)]
            csv_write(folder / '新轨迹.csv', ['group', 'seconds', 'signed_V'], rows)
            config['data'] = {'trace': {'path': '新轨迹.csv', 'columns': {'sample': 'group', 'time': 'seconds', 'voltage': 'signed_V'}}}
        else:
            common.update(radiation='Author declared monochromatic synchrotron', wavelength_A=.61992, cell_configuration='Author declared operando cell X', progress_definition='Reported charge progress percentage; supplied reference definition', synchronization='Voltage and XRD share declared 0 to 100 progress endpoints', intensity_normalization='No normalization; recorded detector counts')
            config['units'] = {'two_theta': 'deg', 'progress': '%', 'intensity': 'counts', 'voltage': 'V'}
            rows = [(s, 20 + k * (1.5 + i), p, 2300 + 120 * i - k * 20 + p * .9) for i, s in enumerate(samples) for p in (0, 10, 55, 100) for k in range(2 + i)]
            csv_write(folder / '新衍射.csv', ['group', 'angle', 'charge_progress', 'detector_counts'], list(reversed(rows)))
            voltages = [(s, p, 2.8 + p * .013) for s in samples for p in (0, 5, 30, 100)]
            csv_write(folder / '同步电压.csv', ['group', 'charge_progress', 'V'], voltages)
            config['data'] = {'diffraction': {'path': '新衍射.csv', 'columns': {'sample': 'group', 'two_theta': 'angle', 'progress': 'charge_progress', 'intensity': 'detector_counts'}}, 'voltage': {'path': '同步电压.csv', 'columns': {'sample': 'group', 'progress': 'charge_progress', 'voltage': 'V'}}}
        path = folder / '真实格式 模拟输入.json'
        dump(path, config)
        return path, config, samples

    def test_extracted_packs_run_without_repository_parent(self):
        for kind, pack in self.packs.items():
            with self.subTest(resource_id=kind):
                manifest = json.loads((pack / 'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
                for file in manifest['files']:
                    self.assertEqual(file_hash(pack / file['path']), file['sha256'], file['path'])
                result = self.command(pack, pack / 'config.demo.json', self.workspace / (kind + ' demo Working'))
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                working = self.workspace / (kind + ' demo Working')
                self.assertTrue((working / 'results/figure.pdf').is_file())
                self.assertTrue((working / 'results/figure.svg').is_file())
                self.assertTrue((working / 'results/figure.png').is_file())
                from PIL import Image
                with Image.open(working / 'results/figure.tiff') as image:
                    self.assertEqual(image.tag_v2[259], 5)
                check = subprocess.run([sys.executable, str(pack / 'checks.py'), '--working', str(working)], cwd=pack, capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(check.returncode, 0, check.stderr + check.stdout)
                self.assertIn('review remains pending', check.stdout)

    def test_blind_groups_uneven_lengths_units_and_no_overwrite(self):
        for kind, pack in self.packs.items():
            with self.subTest(resource_id=kind):
                config_path, cfg, samples = self.author_fixture(kind, self.workspace / (kind + ' 新输入'))
                source_files = [config_path.parent / x['path'] for x in cfg['data'].values()]
                before = {p: file_hash(p) for p in source_files}
                output = self.workspace / (kind + ' 新结果')
                result = self.command(pack, config_path, output)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                record = json.loads((output / '.voltpeer/records/data_checks.json').read_text(encoding='utf-8'))
                self.assertEqual(record['data_status'], 'author_data')
                self.assertEqual(set(record['conditions']), set(samples))
                self.assertEqual(record['unit_mapping'], cfg['units'])
                self.assertEqual({p: file_hash(p) for p in source_files}, before)
                self.assertNotIn('SYNTHETIC DEMO', (output / 'results/figure.svg').read_text(encoding='utf-8'))
                plotted = record['exact_data_artist_checks']
                if kind == 'full_cell':
                    self.assertEqual(max(c['y'][0] for c in plotted if ':capacity' in c['identity']), 447.5)
                    self.assertEqual(sorted(c['points'] for c in plotted if ':capacity' in c['identity']), [4, 7, 10])
                    self.assertTrue(record['material_questions'])
                elif kind == 'li_li':
                    self.assertTrue(any(v < 0 for c in plotted for v in c['y']))
                    self.assertEqual(max(v for c in plotted for v in c['x']), 400)
                else:
                    maps = [c for c in plotted if ':raw_diffraction_grid' in c['identity']]
                    self.assertEqual(len(maps), 3)
                    group_a = next(c for c in maps if c['identity'].startswith(samples[0] + ':'))
                    self.assertEqual(group_a['intensity'][0][0], 2300)
                    self.assertEqual(sorted(len(c['two_theta']) for c in maps), [2, 3, 4])
                    self.assertTrue(all(c['display_extent']['progress'] == [0, 100] for c in maps))
                first_hash = file_hash(output / 'results/figure.pdf')
                again = self.command(pack, config_path, output)
                self.assertEqual(again.returncode, 0, again.stderr)
                self.assertTrue(output.with_name(output.name + '_v002').is_dir())
                self.assertEqual(file_hash(output / 'results/figure.pdf'), first_hash)

    def test_should_stop_inputs_and_old_ranges_do_not_create_outputs(self):
        for kind, pack in self.packs.items():
            with self.subTest(resource_id=kind):
                config_path, valid, _ = self.author_fixture(kind, self.workspace / (kind + ' 拒绝输入'))
                variants = []
                missing_unit = json.loads(json.dumps(valid))
                missing_unit['units'] = {}
                variants.append(missing_unit)
                invalid_container = json.loads(json.dumps(valid))
                invalid_container['units'] = []
                variants.append(invalid_container)
                missing_condition = json.loads(json.dumps(valid))
                missing_condition['conditions']['common'] = {}
                variants.append(missing_condition)
                old_range = json.loads(json.dumps(valid))
                old_range['limits'] = {'full_cell': {'cycling': {'y': [145, 188]}}, 'li_li': {'trace': {'y': [-.01, .01]}}, 'operando_xrd': {'intensity': [0, 1]}}[kind]
                variants.append(old_range)
                for index, bad in enumerate(variants):
                    dump(config_path, bad)
                    output = self.workspace / (kind + f' 不应生成{index}')
                    result = self.command(pack, config_path, output)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertFalse(output.exists())
                demo_as_author = json.loads((pack / 'config.demo.json').read_text(encoding='utf-8'))
                demo_as_author['data_status'] = 'author_data'
                demo_as_author['provenance'] = {'input_origin': 'author_supplied', 'demo_conditions_cleared': True}
                dump(config_path, demo_as_author)
                result = self.command(pack, config_path, self.workspace / (kind + ' 不可借演示条件'))
                self.assertEqual(result.returncode, 2)
                self.assertIn('演示', result.stderr)

    def test_xrd_duplicate_or_missing_grid_and_unsynchronized_voltage_stop(self):
        pack = self.packs['operando_xrd']
        config_path, config, _ = self.author_fixture('operando_xrd', self.workspace / 'XRD应停')
        data = config_path.parent / config['data']['diffraction']['path']
        original = data.read_text(encoding='utf-8-sig')
        for index, contents in enumerate((original + original.splitlines()[1] + '\n', '\n'.join(original.splitlines()[:-1]) + '\n')):
            data.write_text(contents, encoding='utf-8')
            result = self.command(pack, config_path, self.workspace / f'网格不完整{index}')
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('网格', result.stderr)
        data.write_text(original, encoding='utf-8')
        voltage = config_path.parent / config['data']['voltage']['path']
        voltage.write_text(voltage.read_text(encoding='utf-8-sig').replace(',100,', ',99,'), encoding='utf-8')
        result = self.command(pack, config_path, self.workspace / '不同步不外推')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('同步', result.stderr)


if __name__ == '__main__':
    unittest.main()
