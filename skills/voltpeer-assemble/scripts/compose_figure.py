"""Inspect sources and assemble a reproducible battery manuscript composite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from batterycompose import ComposeError, compose, load_manifest
from batterycompose.inventory import inventory
from delivery_contract import collect_working_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("inventory", help="Create an asset list and visual contact sheets")
    scan.add_argument("--input", required=True)
    scan.add_argument("--output", required=True)
    make = sub.add_parser("compose", help="Assemble an explicit panel manifest")
    make.add_argument("--manifest", required=True)
    make.add_argument("--out", required=True, help="Extensionless output stem")
    make.add_argument("--strict", action="store_true", help="Block output on every QA warning")
    deliver = sub.add_parser('deliver', help='Create a result-first versioned Working folder')
    deliver.add_argument('--manifest', required=True, type=Path)
    deliver.add_argument('--out', required=True, type=Path)
    deliver.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == "inventory":
            result = inventory(args.input, args.output)
            print(json.dumps({"count": result["count"], "contact_sheets": result["contact_sheets"]}, ensure_ascii=False))
        elif args.command == 'deliver':
            manifest = load_manifest(args.manifest)
            with tempfile.TemporaryDirectory(prefix='voltpeer-compose-') as temp:
                result = compose(manifest, Path(temp) / 'figure', strict=args.strict)
                final = [Path(result['outputs'][name]) for name in ('pdf', 'png')]
                records = [Path(temp) / 'figure.qa.json', Path(result['outputs']['alignment_overlay'])]
                record_overlay = Path(temp) / 'alignment-check.record.png'
                records[1].rename(record_overlay)
                records[1] = record_overlay
                crops = []
                for crop in Path(result['outputs']['panel_checks']).glob('*.png'):
                    target = Path(temp) / (crop.stem + '.record.png')
                    crop.rename(target)
                    crops.append(target)
                result['outputs'] = {'pdf':'results/figure.pdf', 'png':'results/figure.png',
                                     'alignment_overlay':'.voltpeer/records/alignment-check.record.png',
                                     'panel_checks':['.voltpeer/records/' + crop.name for crop in crops]}
                result['output_paths_relative_to'] = 'working_bundle_root'
                records[0].write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                inputs = [args.manifest] + [Path(panel['resolved_path']) for panel in result_manifest_panels(manifest)]
                folder = collect_working_bundle(final + records + crops, args.out, inputs=inputs,
                    skill_id='voltpeer-assemble', objective=manifest['claim'], specification=result['specification'], title='组合图结果')
            print(json.dumps({'result_folder': str(folder / 'results'), 'preview': str(folder / 'index.html'),
                              'review': '请核对组合图及来源；存在待审查项。' if result['warnings'] else '请核对最终尺寸的标签、图例和科学含义。'}, ensure_ascii=False))
        else:
            result = compose(load_manifest(args.manifest), args.out, strict=args.strict)
            print(json.dumps({"status": result["status"], "warnings": result["warnings"],
                              "outputs": result["outputs"]}, ensure_ascii=False))
    except (ComposeError, ValueError, OSError, KeyError) as exc:
        parser.exit(2, f"assembly error: {exc}\n")


def result_manifest_panels(manifest):
    from batterycompose.render import _auto_rows
    from batterycompose.layout import resolve_layout
    return resolve_layout(_auto_rows(manifest))['panels']


if __name__ == "__main__":
    from cli_runtime import configure_utf8
    configure_utf8()
    main()
