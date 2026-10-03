"""Render an explicit-input optional battery recipe, including electrochemistry.

Scientific choices come from input CSV and metadata, never downloaded paper
curves. Corpus and electrochemistry grammars are optional variants, not defaults.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from batteryplot.specialist import RECIPES, render_recipe
from batteryplot.style import PRESETS, register_community_style
from batteryplot.qa import data_plot_checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipe', choices=RECIPES, required=True)
    parser.add_argument('--input-folder', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--style', default='forge')
    parser.add_argument('--community-style-lock', type=Path)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('Choose a new output directory to preserve earlier figures and input files')
    if args.community_style_lock:
        pin, _ = register_community_style(args.community_style_lock)
        if pin != args.style: parser.error('Style must match exact local community lock')
    if args.style not in PRESETS: parser.error('Unknown style')
    fig, report = render_recipe(args.recipe, args.input_folder, style=args.style)
    report['actual_artist_checks'] = data_plot_checks(fig)
    report['input_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in args.input_folder.iterdir() if p.is_file() and p.suffix in ('.csv','.json')}
    args.output_dir.mkdir(parents=True)
    with matplotlib.rc_context(fig.brf_export_rc):
        for suffix in ('png','svg','pdf'):
            fig.savefig(args.output_dir / f'figure.{suffix}', dpi=300, facecolor='white')
    (args.output_dir / 'provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(args.output_dir.resolve())


if __name__ == '__main__': main()
