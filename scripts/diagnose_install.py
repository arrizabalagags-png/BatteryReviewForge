"""Check requirements of the actual installed Skill(s), never install packages.

Accept a collection or one Skill directory. Local imports/exports cannot prove
native host discovery, model behaviour, scientific correctness or visual quality.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout, redirect_stderr
import importlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from check_skill_dependencies import MODULE_DISTRIBUTIONS, OPTIONAL, normalize, requirements, skill_folders, skill_id

MODULES = {normalize(value): key for key, value in MODULE_DISTRIBUTIONS.items() if key != 'fitz'}
SMOKE_SKILLS = {'battery-review-figure', 'battery-figure-assemble'}


def satisfies(version, constraint):
    if not constraint:
        return True
    try:
        from packaging.specifiers import SpecifierSet
        return version in SpecifierSet(constraint)
    except ImportError:
        # Current declarations are numeric minimums. Complex unsupported specs
        # remain untested; lexical comparison would produce false successes.
        if not re.fullmatch(r'\d+(?:\.\d+)*', version):
            return None
        actual = tuple(map(int, version.split('.')))
        for part in constraint.split(','):
            match = re.fullmatch(r'\s*(>=|<=|==|!=|>|<|~=)\s*(\d+(?:\.\d+)*)\s*', part)
            if not match:
                return None
            operator, value = match.groups()
            target = tuple(map(int, value.split('.')))
            width = max(len(actual), len(target))
            a, b = actual + (0,) * (width-len(actual)), target + (0,) * (width-len(target))
            if operator == '~=':
                if len(target) < 2:
                    return None
                upper = target[:-2] + (target[-2]+1,)
                okay = a >= b and a < upper + (0,) * (width-len(upper))
            else:
                okay = {'>=': a >= b, '<=': a <= b, '==': a == b, '!=': a != b, '>': a > b, '<': a < b}[operator]
            if not okay:
                return False
        return True


def probe(entry):
    name = entry['name']
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        version = None
    module = MODULES.get(normalize(name), name.replace('-', '_'))
    imported, error = False, None
    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            importlib.import_module(module)
        imported = True
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'
    acceptable = satisfies(version, entry['constraint']) if version else False
    if not version:
        error = 'Distribution is not installed'
    elif acceptable is False:
        error = f'Installed {version} does not satisfy {entry["constraint"]}'
    state = 'PASS' if version and imported and acceptable is True else ('NOT_TESTED' if acceptable is None and imported else 'FAIL')
    return {**entry, 'module': module, 'version': version, 'imported': imported,
            'version_satisfied': acceptable, 'status': state, 'error': error}


def command(argv):
    process = subprocess.run([sys.executable, '-X', 'utf8', *map(str, argv)], capture_output=True, encoding='utf-8', timeout=90)
    if process.returncode:
        raise RuntimeError(process.stderr[-3000:] or process.stdout[-3000:] or 'Smoke command failed')


def smoke_figure(folder, output):
    data = output / 'synthetic.csv'
    data.write_text('series,cycle,discharge_capacity\nSynthetic check,1,150\nSynthetic check,2,149\nSynthetic check,3,148\n', encoding='utf-8')
    common = {'source_id': 'SYNTHETIC-SMOKE-TEST', 'evidence_state': 'verified', 'chemistry': 'DEMO only',
        'cell_configuration': 'full cell', 'temperature_c': '25', 'rate': '1 C', 'voltage_window_v': '2.5-4.2',
        'capacity_basis': 'cathode active mass', 'capacity_unit': 'mAh g-1', 'loading_mg_cm2': '2',
        'electrolyte_ul_mg': '10', 'np_ratio': '1.1', 'cell_format': 'synthetic coin',
        'formation_protocol': 'synthetic test', 'pressure_mpa': '0.1'}
    metadata = output / 'synthetic.json'
    metadata.write_text(json.dumps({'kind': 'full_cell_cycling', 'style': 'forge', 'columns': {},
        'claim': 'SYNTHETIC export check only', 'caption_notes': 'Not experimental data.', 'common': common}), encoding='utf-8')
    command([folder / 'scripts/plot_uploaded.py', 'plot', '--data', data, '--metadata', metadata, '--out', output / 'figure'])
    from PIL import Image
    from pypdf import PdfReader
    import xml.etree.ElementTree as ET
    with Image.open(output / 'figure.png') as image:
        image.verify()
    if not ET.parse(output / 'figure.svg').getroot().tag.endswith('svg') or len(PdfReader(output / 'figure.pdf').pages) != 1:
        raise ValueError('Malformed SVG/PDF export')
    return 'local synthetic PDF/PNG/SVG export; visual and scientific review NOT_TESTED'


def smoke_assembly(folder, output):
    command([folder / 'examples/demo_assemble.py', '--output', output / 'demo', '--without-svg'])
    from PIL import Image
    from pypdf import PdfReader
    with Image.open(output / 'demo/composite.png') as image:
        image.verify()
    if len(PdfReader(output / 'demo/composite.pdf').pages) != 1:
        raise ValueError('Malformed composition PDF')
    return 'local synthetic PDF/PNG composition; SVG/native/visual/scientific review NOT_TESTED'


def diagnose(root: Path, host='unspecified', host_version='not reported', output: Path | None = None):
    root = root.resolve()
    folders = skill_folders(root)
    report = {'host': host, 'host_version': host_version, 'skills_path': str(root), 'python_path': sys.executable,
        'python_version': platform.python_version(), 'skills_readable': {}, 'dependencies': {}, 'dependency_imports': {},
        'skills': {}, 'stages': {'copied': 'PASS' if folders else 'FAIL', 'discovered': 'NOT_TESTED',
        'runtime_ready': 'NOT_TESTED', 'smoke_test_passed': 'NOT_TESTED'}, 'outputs': [], 'errors': [],
        'next': 'In a new host task, read the actual installed skills. Files/imports cannot prove host discovery or model behaviour.'}
    if not folders:
        report['errors'].append('No readable SKILL.md at this directory or its immediate children.')
    for folder in folders:
        name = skill_id(folder)
        key = name if name not in report['skills'] else f'{name}@{folder.name}'
        report['skills_readable'][key] = True
        item = {'skill_id': name, 'path': str(folder), 'requirements_file': None, 'dependencies': [],
                'runtime_ready': 'NOT_REQUIRED', 'capabilities': {}, 'smoke': 'NOT_TESTED'}
        manifest = folder / 'requirements.txt'
        if manifest.is_file():
            item['requirements_file'] = str(manifest)
            try:
                for entry in requirements(manifest, folder):
                    checked = probe(entry)
                    reason = OPTIONAL.get(name, {}).get(checked['module'])
                    checked['optional_for_base_runtime'] = bool(reason)
                    item['dependencies'].append(checked)
                    report['dependencies'][entry['name']] = checked['version']
                    report['dependency_imports'][entry['name']] = checked['imported']
                    if reason:
                        item['capabilities']['svg_panel_import'] = 'AVAILABLE_IMPORT_ONLY' if checked['status'] == 'PASS' else 'UNAVAILABLE_NATIVE_CAIRO_REQUIRED'
                    elif checked['status'] == 'FAIL':
                        report['errors'].append(f'{key}: {entry["name"]}: {checked["error"]}')
                states = [x['status'] for x in item['dependencies'] if not x['optional_for_base_runtime']]
                item['runtime_ready'] = 'FAIL' if 'FAIL' in states else ('NOT_TESTED' if 'NOT_TESTED' in states else ('PASS' if states else 'NOT_REQUIRED'))
                if sys.version_info < (3, 10) and states:
                    item['runtime_ready'] = 'FAIL'
                    report['errors'].append(f'{key}: use isolated Python >=3.10.')
            except ValueError as exc:
                item['runtime_ready'] = 'FAIL'
                report['errors'].append(f'{key}: {exc}')
        report['skills'][key] = item
    states = [x['runtime_ready'] for x in report['skills'].values()]
    if states:
        report['stages']['runtime_ready'] = 'FAIL' if 'FAIL' in states else ('NOT_TESTED' if 'NOT_TESTED' in states else ('PASS' if 'PASS' in states else 'NOT_REQUIRED'))
    if output is not None:
        supported = [(key, item) for key, item in report['skills'].items() if item['skill_id'] in SMOKE_SKILLS]
        for item in report['skills'].values():
            if item['skill_id'] not in SMOKE_SKILLS:
                item['smoke'] = 'NOT_SUPPORTED'
        if not supported:
            report['stages']['smoke_test_passed'] = 'NOT_SUPPORTED' if folders else 'NOT_TESTED'
            report['next'] = 'No smoke route exists for these skills; use actual host workflow EVAL. No output directory was created.'
        else:
            output = output.resolve()
            output.mkdir(parents=True, exist_ok=False)
            for key, item in supported:
                if item['runtime_ready'] != 'PASS':
                    report['errors'].append(f'{key}: smoke not run; fix declared requirements first.')
                    continue
                target = output / key
                target.mkdir()
                try:
                    item['smoke_scope'] = (smoke_figure if item['skill_id'] == 'battery-review-figure' else smoke_assembly)(Path(item['path']), target)
                    item['smoke'] = 'PASS'
                    report['outputs'].extend(str(p) for p in sorted(target.rglob('*')) if p.is_file())
                except Exception as exc:
                    item['smoke'] = 'FAIL'
                    report['errors'].append(f'{key}: {exc}')
            states = [x['smoke'] for x in report['skills'].values()]
            report['stages']['smoke_test_passed'] = 'FAIL' if 'FAIL' in states else ('NOT_TESTED' if 'NOT_TESTED' in states else ('PARTIAL' if 'NOT_SUPPORTED' in states else 'PASS'))
            report['next'] = 'Only the stated local smoke scope ran. Open the files; host/model/visual/scientific checks remain NOT_TESTED.'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-root', type=Path, required=True, help='Collection or one installed SKILL.md directory')
    parser.add_argument('--host', default='unspecified')
    parser.add_argument('--host-version', default='not reported')
    parser.add_argument('--smoke-output', type=Path)
    parser.add_argument('--show-paths', action='store_true', help='Show local paths; redact before sharing')
    args = parser.parse_args()
    report = diagnose(args.skills_root, args.host, args.host_version, args.smoke_output)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if not args.show_paths:
        for personal in {str(Path.home()), os.environ.get('USERPROFILE', '')}:
            if personal:
                text = text.replace(json.dumps(personal, ensure_ascii=False)[1:-1], '<USER>')
    print(text)
    return int('FAIL' in report['stages'].values())


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    raise SystemExit(main())
