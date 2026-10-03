"""Installed single-Skill boundaries, broken docs, and undeclared lazy imports."""
from __future__ import annotations
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_skill_distribution import check_skill
from check_skill_dependencies import check_skill_dependencies
from diagnose_install import diagnose


def fixture(base, name='voltpeer-claim-check', deps=None):
    folder = base / name
    for directory in ('references/nested', 'assets/templates', 'scripts'):
        (folder / directory).mkdir(parents=True, exist_ok=True)
    (folder / 'SKILL.md').write_text(f'---\nname: {name}\n---\n[Guide](references/EXECUTION.md)\n', encoding='utf-8')
    (folder / 'references/EXECUTION.md').write_text('Local execution guide', encoding='utf-8')
    (folder / 'assets/templates/TASK_STATE.json').write_text('{}', encoding='utf-8')
    (folder / 'scripts/check_task_state.py').write_text('import json\n', encoding='utf-8')
    if deps is not None:
        (folder / 'requirements.txt').write_text(deps, encoding='utf-8-sig')
    return folder


class SkillPortabilityTests(unittest.TestCase):
    def test_native_dependency_is_declared_optional_and_required_only_for_its_capability(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp), 'voltpeer-data')
            (folder / 'scripts/native.py').write_text('def native():\n    import NewareNDA\n', encoding='utf-8')
            self.assertEqual(check_skill_dependencies(folder)['status'], 'FAIL')
            (folder / 'requirements-native.txt').write_text('NewareNDA==2026.6.11\n', encoding='utf-8')
            report = check_skill_dependencies(folder)
            self.assertEqual(report['status'], 'PASS', report['issues'])
            self.assertEqual(report['optional_requirements'][0]['constraint'], '==2026.6.11')
            self.assertTrue(next(row for row in report['imports'] if row['module']=='NewareNDA')['optional_capability'])
    def test_single_workflow_has_no_plot_dependency_or_invented_smoke(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = fixture(root)
            with patch('diagnose_install.importlib.metadata.version', side_effect=AssertionError('Do not probe unrelated packages')):
                result = diagnose(folder, output=root / 'unused smoke')
            self.assertEqual(result['stages']['copied'], 'PASS')
            self.assertEqual(result['stages']['runtime_ready'], 'NOT_REQUIRED')
            self.assertEqual(result['stages']['smoke_test_passed'], 'NOT_SUPPORTED')
            self.assertEqual(result['stages']['discovered'], 'NOT_TESTED')
            self.assertEqual(result['dependencies'], {})
            self.assertFalse((root / 'unused smoke').exists())

    def test_collection_reads_only_each_installed_skills_requirements(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            fixture(root, 'custom-data-skill', 'pypdf>=5\n')
            with patch('diagnose_install.importlib.metadata.version', return_value='6.0') as version, patch('diagnose_install.importlib.import_module') as imported:
                result = diagnose(root)
            self.assertEqual(result['stages']['runtime_ready'], 'PASS')
            self.assertEqual(result['skills']['voltpeer-claim-check']['runtime_ready'], 'NOT_REQUIRED')
            self.assertEqual(set(result['dependencies']), {'pypdf'})
            version.assert_called_once_with('pypdf')
            imported.assert_called_once_with('pypdf')

    def test_missing_old_or_unimportable_actual_requirement_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp), 'custom-data-skill', 'numpy>=2\n')
            cases = [(None, None), ('1.26', None), ('2.1', OSError('runtime unavailable'))]
            for version, error in cases:
                with self.subTest(version=version), patch('diagnose_install.importlib.metadata.version',
                    side_effect=importlib.metadata.PackageNotFoundError('numpy') if version is None else None, return_value=version), patch('diagnose_install.importlib.import_module', side_effect=error):
                    result = diagnose(folder)
                self.assertEqual(result['stages']['runtime_ready'], 'FAIL')
                self.assertEqual(result['stages']['discovered'], 'NOT_TESTED')

    def test_optional_cairo_failure_does_not_fail_declared_pdf_route(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp), 'voltpeer-assemble', 'Pillow>=10\nCairoSVG>=2.7\n')
            def version(name): return '12.0' if name == 'Pillow' else '2.9'
            def imported(name):
                if name == 'cairosvg': raise OSError('native Cairo missing')
                return object()
            with patch('diagnose_install.importlib.metadata.version', side_effect=version), patch('diagnose_install.importlib.import_module', side_effect=imported):
                result = diagnose(folder)
            self.assertEqual(result['stages']['runtime_ready'], 'PASS')
            self.assertEqual(result['skills']['voltpeer-assemble']['capabilities']['svg_panel_import'], 'UNAVAILABLE_NATIVE_CAIRO_REQUIRED')
            self.assertEqual(result['stages']['smoke_test_passed'], 'NOT_TESTED')

    def test_local_requirements_include_and_escape_are_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp), 'custom-data-skill', '-r references/requirements-extra.txt\n')
            extra = folder / 'references/requirements-extra.txt'
            extra.write_text('pypdf>=5\n')
            with patch('diagnose_install.importlib.metadata.version', return_value='6'), patch('diagnose_install.importlib.import_module'):
                self.assertEqual(diagnose(folder)['stages']['runtime_ready'], 'PASS')
            extra.write_text('-r ../../unrelated.txt\n')
            self.assertEqual(diagnose(folder)['stages']['runtime_ready'], 'FAIL')

    def test_single_plot_smoke_actually_runs_without_assembly_installed(self):
        with tempfile.TemporaryDirectory(prefix='独立 技能 ') as temp:
            root = Path(temp)
            folder = root / '绘图技能'
            shutil.copytree(ROOT / 'skills/voltpeer-plot', folder, ignore=shutil.ignore_patterns('__pycache__'))
            result = diagnose(folder, output=root / '烟雾检查 结果')
            self.assertEqual(result['stages']['runtime_ready'], 'PASS', result['errors'])
            self.assertEqual(result['stages']['smoke_test_passed'], 'PASS', result['errors'])
            self.assertEqual(set(result['skills']), {'voltpeer-plot'})
            self.assertEqual(result['stages']['discovered'], 'NOT_TESTED')
            self.assertTrue(any(p.endswith('figure.svg') for p in result['outputs']))

    def test_single_assembly_smoke_without_native_svg_route(self):
        with tempfile.TemporaryDirectory(prefix='独立 拼版 ') as temp:
            root = Path(temp)
            folder = root / '拼版技能'
            shutil.copytree(ROOT / 'skills/voltpeer-assemble', folder, ignore=shutil.ignore_patterns('__pycache__'))
            result = diagnose(folder, output=root / '组合检查')
            self.assertEqual(result['stages']['smoke_test_passed'], 'PASS', result['errors'])
            scope = result['skills']['voltpeer-assemble']['smoke_scope']
            self.assertIn('SVG/native/visual/scientific review NOT_TESTED', scope)
            self.assertEqual(set(result['skills']), {'voltpeer-assemble'})

    def test_all_source_skills_have_portable_references_and_declared_imports(self):
        folders = [p for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file()]
        self.assertEqual(len(folders), 15)
        for folder in folders:
            with self.subTest(skill=folder.name):
                self.assertEqual(check_skill(folder), [])
                report = check_skill_dependencies(folder)
                self.assertEqual(report['status'], 'PASS', report['issues'])

    def test_bare_paths_in_nested_guide_use_root_and_explicit_document_semantics(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp))
            (folder / 'scripts/demo.py').write_text('')
            (folder / 'assets/theme.json').write_text('{}')
            guide = folder / 'references/nested/guide.md'
            guide.write_text('`scripts/demo.py inspect`\n`../../assets/theme.json`\n`assets/theme.json`\n`references/EXECUTION.md`\n')
            self.assertEqual(check_skill(folder), [])
            (folder / 'assets/theme.json').unlink()
            issues = check_skill(folder)
            self.assertTrue(any('assets/theme.json' in item for item in issues))
            self.assertTrue(all('guide.md' in item for item in issues))

    def test_missing_nonscript_files_and_repository_prefixed_paths_are_not_hidden(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp))
            guide = folder / 'references/nested/guide.md'
            guide.write_text('`assets/missing.json`\n`examples/demo.csv`\n`references/missing.txt`\n`skills/battery-other/scripts/run.py`\n')
            issues = check_skill(folder)
            self.assertEqual(len(issues), 4, issues)

    def test_output_and_explicit_placeholders_do_not_hide_missing_executable(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp))
            guide = folder / 'references/nested/guide.md'
            guide.write_text('`<installed-battery-other>/scripts/run.py`\n`assets/<AUTHOR_INPUT>.csv`\npython scripts/missing.py --out assets/author-result.json\n')
            issues = check_skill(folder)
            self.assertEqual(len(issues), 1, issues)
            self.assertIn('scripts/missing.py', issues[0])

    def test_spaces_markdown_links_definitions_and_absolute_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp))
            (folder / 'assets/my guide.json').write_text('{}')
            guide = folder / 'references/guide.md'
            guide.write_text('[Good](<../assets/my guide.json>)\n[good]: ../assets/my%20guide.json\n`"assets/my guide.json"`\n')
            self.assertEqual(check_skill(folder), [])
            guide.write_text('[Outside](../../private.md)\n[absolute](C:/private.md)\n[file](file:///tmp/private.md)\n[encoded](%2e%2e/%2e%2e/private.md)\n`"assets/missing guide.json"`\n')
            self.assertEqual(len(check_skill(folder)), 5)

    def test_ast_gate_catches_lazy_and_literal_dynamic_undeclared_imports(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp))
            (folder / 'scripts/plot.py').write_text('def plot():\n    import numpy\n    return __import__("pypdf")\n')
            report = check_skill_dependencies(folder)
            self.assertEqual(report['status'], 'FAIL')
            self.assertEqual(len(report['issues']), 2)
            external = [item for item in report['imports'] if item['kind'] == 'third_party']
            self.assertTrue(all(item['lazy'] for item in external))

    def test_ast_gate_identifies_shipped_local_stdlib_and_declared_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp), deps='Pillow>=10\n')
            (folder / 'scripts/local_helper.py').write_text('import csv\n')
            (folder / 'scripts/plot.py').write_text('import local_helper, pathlib\nfrom PIL import Image\n')
            report = check_skill_dependencies(folder)
            self.assertEqual(report['status'], 'PASS', report['issues'])
            self.assertTrue(any(x['kind'] == 'local' and x['module'] == 'local_helper' for x in report['imports']))
            (folder / 'scripts/local_helper.py').unlink()
            self.assertEqual(check_skill_dependencies(folder)['status'], 'FAIL')

    def test_nonliteral_dynamic_import_remains_not_tested(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = fixture(Path(temp))
            (folder / 'scripts/plugin.py').write_text('def plugin(name):\n    return __import__(name)\n')
            report = check_skill_dependencies(folder)
            self.assertEqual(report['status'], 'NOT_TESTED')
            self.assertEqual(len(report['unresolved_dynamic_imports']), 1)


if __name__ == '__main__':
    unittest.main()
