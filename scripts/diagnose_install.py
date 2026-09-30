"""Local BRF checks. Reads an explicit skills directory; no network or global installs.

Host discovery cannot be proven by this standalone script. Run a new host task
to confirm it. Use --smoke-output to opt into one small synthetic export.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
import importlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

SKILLS = ('battery-review-figure', 'battery-figure-assemble')
PACKAGES = ('matplotlib', 'numpy', 'openpyxl', 'python-pptx', 'Pillow', 'pypdf',
            'pypdfium2', 'reportlab', 'CairoSVG', 'pdfplumber', 'PyMuPDF')
OPTIONAL = {'CairoSVG'}


def diagnose(root: Path, host='unspecified', host_version='not reported', output: Path | None = None):
    root = root.resolve()
    readable = {name: (root / name / 'SKILL.md').is_file() for name in SKILLS}
    versions = {}
    imports = {}
    dependency_errors = []
    module_names = {'python-pptx': 'pptx', 'Pillow': 'PIL', 'CairoSVG': 'cairosvg', 'PyMuPDF': 'pymupdf'}
    for name in PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
        try:
            with redirect_stdout(io.StringIO()):
                importlib.import_module(module_names.get(name, name))
            imports[name] = True
        except Exception as exc:
            imports[name] = False
            if name not in OPTIONAL:
                dependency_errors.append(f'{name}: {exc}')
    report = {'host': host, 'host_version': host_version, 'skills_path': str(root),
              'python_path': sys.executable, 'python_version': platform.python_version(),
              'skills_readable': readable, 'dependencies': versions, 'dependency_imports': imports,
              'stages': {'copied': 'PASS' if all(readable.values()) else 'FAIL',
                         'discovered': 'NOT_TESTED',
                         'runtime_ready': 'PASS' if all(versions[name] and imports[name] for name in PACKAGES if name not in OPTIONAL) else 'FAIL',
                         'smoke_test_passed': 'NOT_TESTED'},
              'capabilities': {'svg_panel_import': 'AVAILABLE' if imports['CairoSVG'] else 'UNAVAILABLE_NATIVE_CAIRO_REQUIRED',
                               'pdf_png_tiff_composition': 'AVAILABLE' if all(imports[name] for name in ('Pillow', 'pypdf', 'pypdfium2', 'reportlab', 'pdfplumber')) else 'UNAVAILABLE',
                               'plot_svg_export': 'AVAILABLE' if imports['matplotlib'] else 'UNAVAILABLE'},
              'outputs': [], 'errors': dependency_errors,
              'next': 'Ask the host in a new task to locate both skills. File existence is not discovery.'}
    if output is not None:
        # A new directory avoids replacing any user file, even from an earlier run.
        output = output.resolve()
        output.mkdir(parents=True, exist_ok=False)
        if not all(readable.values()):
            report['errors'].append('Both figure and assembly skills must be readable before testing.')
            report['stages']['smoke_test_passed'] = 'FAIL'
        else:
            try:
                data = output / 'full_cell_cycling.csv'
                data.write_text('series,cycle,discharge_capacity\nSynthetic export check,1,150\nSynthetic export check,2,149\nSynthetic export check,3,148\n', encoding='utf-8')
                common = {'source_id': 'SYNTHETIC-SMOKE-TEST', 'evidence_state': 'verified',
                     'chemistry': 'DEMO only', 'cell_configuration': 'full cell',
                     'temperature_c': '25', 'rate': '1 C', 'voltage_window_v': '2.5-4.2',
                     'capacity_basis': 'cathode active mass', 'capacity_unit': 'mAh g-1',
                     'loading_mg_cm2': '2', 'electrolyte_ul_mg': '10', 'np_ratio': '1.1',
                     'cell_format': 'synthetic coin', 'formation_protocol': 'synthetic test', 'pressure_mpa': '0.1'}
                metadata = output / 'full_cell_cycling.json'
                metadata.write_text(json.dumps({'kind': 'full_cell_cycling', 'style': 'forge', 'columns': {},
                    'claim': 'SYNTHETIC export check only', 'caption_notes': 'Not experimental data.', 'common': common}), encoding='utf-8')
                process = subprocess.run([sys.executable, '-X', 'utf8', str(root / SKILLS[0] / 'scripts/plot_uploaded.py'),
                    'plot', '--data', str(data), '--metadata', str(metadata), '--out', str(output / 'full_cell_cycling')],
                    capture_output=True, encoding='utf-8', timeout=90)
                if process.returncode:
                    raise RuntimeError(process.stderr[-3000:] or 'Plot command failed')
                from PIL import Image
                import xml.etree.ElementTree as ET
                png, svg = (output / 'full_cell_cycling.png'), (output / 'full_cell_cycling.svg')
                with Image.open(png) as im:
                    im.verify()
                if not ET.parse(svg).getroot().tag.endswith('svg'):
                    raise ValueError('SVG export did not contain an SVG root')
                report['outputs'] = [str(p) for p in sorted(output.iterdir()) if p.is_file()]
                report['stages']['smoke_test_passed'] = 'PASS'
                report['next'] = 'Open PNG and SVG, inspect axes and units. Native host discovery and real model EVAL remain untested.'
            except Exception as exc:
                report['stages']['smoke_test_passed'] = 'FAIL'
                report['errors'].append(str(exc))
                report['next'] = 'Check this environment and requirements.txt. Retry at most once with a new output directory.'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-root', type=Path, required=True)
    parser.add_argument('--host', default='unspecified')
    parser.add_argument('--host-version', default='not reported')
    parser.add_argument('--smoke-output', type=Path)
    parser.add_argument('--show-paths', action='store_true', help='Show local paths; do not share them unredacted')
    args = parser.parse_args()
    report = diagnose(args.skills_root, args.host, args.host_version, args.smoke_output)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if not args.show_paths:
        for personal in {str(Path.home()), os.environ.get('USERPROFILE', '')}:
            if personal:
                text = text.replace(json.dumps(personal, ensure_ascii=False)[1:-1], '<USER>')
    print(text)
    return 1 if 'FAIL' in report['stages'].values() else 0


if __name__ == '__main__':
    raise SystemExit(main())
