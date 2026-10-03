"""Packaging and upgrade regression; never installs into the user's skill paths."""
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from diagnose_install import diagnose


class InstallationTests(unittest.TestCase):
    def test_starter_shared_references_are_present(self):
        version = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))['version']
        path = ROOT / 'docs/downloads' / f'v{version}' / f'VoltPeer-WorkBuddy-Starter-v{version}.zip'
        with ZipFile(path) as outer:
            zips = [name for name in outer.namelist() if name.endswith('.zip')]
            self.assertEqual(len(zips), 2)
            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                for name in zips:
                    with ZipFile(io.BytesIO(outer.read(name))) as inner:
                        inner.extractall(folder)
                for skill in folder.glob('*/SKILL.md'):
                    for ref in re.findall(r'\]\((\.\./[^)#]+)', skill.read_text(encoding='utf-8')):
                        self.assertTrue((skill.parent / ref).resolve().is_file(), ref)

    def test_diagnostic_does_not_invent_host_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = diagnose(Path(tmp))
        self.assertEqual(result['stages']['copied'], 'FAIL')
        self.assertEqual(result['stages']['discovered'], 'NOT_TESTED')
        self.assertEqual(result['stages']['smoke_test_passed'], 'NOT_TESTED')

    def test_sample_bundles_contain_declared_inputs(self):
        for source in (ROOT / 'examples/showcase').glob('*/metadata.json'):
            slug = source.parent.name
            with self.subTest(slug=slug), ZipFile(ROOT / f'docs/assets/showcase/BRF-demo-{slug}.zip') as archive:
                with tempfile.TemporaryDirectory() as tmp:
                    archive.extractall(tmp)
                    metadata = json.loads((Path(tmp) / slug / 'metadata.json').read_text(encoding='utf-8'))
                    for name in metadata['source_files']:
                        path = (Path(tmp) / slug / name).resolve()
                        self.assertTrue(path.is_relative_to(Path(tmp).resolve()))
                        self.assertTrue(path.is_file(), name)
                        self.assertEqual(path.read_bytes(), (source.parent / name).read_bytes())
        for slug in ('full-cell', 'li-cu-ce'):
            with ZipFile(ROOT / f'docs/assets/showcase/BRF-demo-{slug}.zip') as archive:
                folder = f'BRF-demo-{slug}'
                metadata = json.loads(archive.read(f'{folder}/metadata.json'))
                self.assertTrue(metadata['not_experimental_data'])
                for name in metadata['source_files']:
                    self.assertIn(f'{folder}/{name}', archive.namelist())

    @unittest.skipUnless(shutil.which('pwsh') or shutil.which('powershell'), 'PowerShell unavailable')
    def test_update_preserves_old_tree_without_stale_merge(self):
        shell = shutil.which('pwsh') or shutil.which('powershell')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'package'
            source = package / 'skills/voltpeer-plot'
            source.mkdir(parents=True)
            (source / 'SKILL.md').write_text('new', encoding='utf-8')
            shutil.copyfile(ROOT / 'install.ps1', package / 'install.ps1')
            (package / 'docs').mkdir()
            shutil.copyfile(ROOT / 'docs/SKILL_MIGRATION.json', package / 'docs/SKILL_MIGRATION.json')
            target = root / 'host/skills'
            old = target / 'voltpeer-plot'
            old.mkdir(parents=True)
            (old / 'SKILL.md').write_text('old', encoding='utf-8')
            (old / 'custom.txt').write_text('my changes', encoding='utf-8')
            command = [shell, '-NoProfile', '-File', str(package / 'install.ps1'), '-TargetRoot', str(target)]
            denied = subprocess.run(command, capture_output=True)
            self.assertNotEqual(denied.returncode, 0)
            self.assertEqual((old / 'SKILL.md').read_text(), 'old')
            updated = subprocess.run(command + ['-Overwrite'], capture_output=True)
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertEqual((old / 'SKILL.md').read_text(), 'new')
            self.assertFalse((old / 'custom.txt').exists())
            backups = list((target.parent / '.voltpeer-install-backups').glob('*/canonical/voltpeer-plot'))
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / 'custom.txt').read_text(), 'my changes')
            self.assertEqual((backups[0] / 'SKILL.md').read_text(), 'old')
