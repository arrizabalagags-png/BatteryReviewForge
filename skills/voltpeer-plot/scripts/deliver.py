"""Make a result-first, versioned Working bundle from author-reviewed data."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import tempfile

from batteryplot import DataContractError, save_bundle
from batteryplot.specification import resolve_specification
from plot_uploaded import render_from_metadata
from delivery_contract import collect_working_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='Working folder; existing versions are preserved')
    parser.add_argument('--journal', default='journal_neutral', help='Stored profile ID or path to an author-verified JSON profile')
    parser.add_argument('--content-class', choices=('line_art', 'image', 'mixed'), default='line_art')
    parser.add_argument('--dpi', type=int)
    parser.add_argument('--style', help='Explicit author-selected palette; omitted preserves metadata.style, recorded without changing input JSON')
    parser.add_argument('--png-dpi', type=int)
    parser.add_argument('--tiff-dpi', type=int)
    parser.add_argument('--formats', nargs='+', choices=('pdf', 'svg', 'png', 'tiff'), default=['pdf', 'svg', 'png', 'tiff'])
    args = parser.parse_args()
    try:
        profiles_path = Path(__file__).resolve().parents[1] / 'references/JOURNAL_FIGURE_SPEC.json'
        profiles = json.loads(profiles_path.read_text(encoding='utf-8-sig'))
        profile_path = Path(args.journal)
        if args.journal in profiles and isinstance(profiles[args.journal], dict):
            profile = {**profiles[args.journal], 'profile_id': args.journal}
        elif profile_path.is_file():
            profile = json.loads(profile_path.read_text(encoding='utf-8-sig'))
            profile.setdefault('profile_id', 'author_profile')
        else:
            raise DataContractError('Unknown profile; choose journal_neutral, a stored ID, or an explicit JSON profile')
        per_format = {key: value for key, value in {'png': args.png_dpi, 'tiff': args.tiff_dpi}.items() if value is not None}
        specification = resolve_specification(profile, content_class=args.content_class, requested_dpi=args.dpi, dpi_by_format=per_format)
        with tempfile.TemporaryDirectory(prefix='voltpeer-plot-') as temp:
            fig, config = render_from_metadata(args.data, args.metadata, style_override=args.style)
            files = save_bundle(fig, Path(temp) / 'figure', claim=config['claim'], source_data=str(args.data),
                caption_notes=config['caption_notes'], dpi=specification['dpi'], dpi_by_format=per_format,
                formats=tuple(args.formats), specification=specification, close=True)
            folder = collect_working_bundle(files, args.out, inputs=(args.data, args.metadata),
                skill_id='voltpeer-plot', objective=config['claim'], specification=specification)
        print(json.dumps({'result_folder': str(folder / 'results'), 'preview': str(folder / 'index.html'),
                          'review': '请核对图中单位、实验条件和结论；投稿前再核对目标期刊规格。'}, ensure_ascii=False))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    from cli_runtime import configure_utf8
    configure_utf8()
    main()
