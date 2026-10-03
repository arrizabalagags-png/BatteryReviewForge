"""Inspect and explicitly map a battery instrument CSV without hidden cleaning."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream)
        try: headers = next(reader)
        except StopIteration: raise ValueError('CSV is empty')
        if not headers or any(not h.strip() for h in headers) or len(headers) != len(set(headers)):
            raise ValueError('CSV headers must be unique and nonempty')
        rows = list(reader)
    for index, row in enumerate(rows, 1):
        if len(row) != len(headers):
            raise ValueError(f'Row {index} has {len(row)} cells, expected {len(headers)}; no repair inferred')
    return headers, rows


def inspect(path: Path):
    headers, rows = read_csv(path)
    columns = []
    for index, header in enumerate(headers):
        values = [row[index] for row in rows]
        nonempty = [v for v in values if v.strip()]
        finite = 0
        for value in nonempty:
            try: finite += math.isfinite(float(value))
            except ValueError: pass
        columns.append({'header': header, 'blank_rows': sum(not v.strip() for v in values),
                        'finite_numeric_cells': finite, 'nonempty_cells': len(nonempty)})
    return {'source': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'data_rows': len(rows), 'columns': columns, 'scientific_units_inferred': False}


def prepare(path: Path, mapping_path: Path, output: Path):
    if output.exists(): raise ValueError('Output directory already exists; choose a new one')
    headers, rows = read_csv(path)
    mapping = json.loads(mapping_path.read_text(encoding='utf-8'))
    columns, units = mapping.get('columns'), mapping.get('units')
    if not isinstance(columns, dict) or not columns or not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v in headers for k, v in columns.items()):
        raise ValueError('columns must map nonempty output names to exact source headers')
    if len(set(columns.values())) != len(columns): raise ValueError('Each source header may be mapped once')
    if not isinstance(units, dict) or set(units) != set(columns) or not all(isinstance(v, str) and v.strip() for v in units.values()):
        raise ValueError('units must explicitly describe every mapped column')
    context = mapping.get('plot_context', '')
    if not isinstance(context, str):
        raise ValueError('plot_context must be a string describing the checked test conditions')
    numeric = mapping.get('numeric_columns', [])
    if not isinstance(numeric, list) or len(numeric) != len(set(numeric)) or not set(numeric) <= set(columns):
        raise ValueError('numeric_columns must be unique mapped output names')
    exclusions = mapping.get('exclude_rows', [])
    if not isinstance(exclusions, list): raise ValueError('exclude_rows must be a list')
    excluded = {}
    for item in exclusions:
        if not isinstance(item, dict) or set(item) != {'row_number', 'reason'}:
            raise ValueError('Each exclusion needs row_number and reason')
        number, reason = item['row_number'], item['reason']
        if type(number) is not int or not 1 <= number <= len(rows) or number in excluded or not isinstance(reason, str) or not reason.strip():
            raise ValueError('Exclusions need unique in-range row numbers and a specific reason')
        excluded[number] = reason.strip()
    kept = []
    for number, row in enumerate(rows, 1):
        if number in excluded: continue
        mapped = {new: row[headers.index(old)] for new, old in columns.items()}
        for key in numeric:
            try: number_value = float(mapped[key])
            except ValueError: raise ValueError(f'Row {number}: {key} is not numeric; retain or exclude explicitly')
            if not math.isfinite(number_value): raise ValueError(f'Row {number}: {key} is nonfinite; retain or exclude explicitly')
        kept.append(mapped)
    record = {'source': str(path.resolve()), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'mapping_sha256': hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
              'columns': columns, 'units': units, 'numeric_columns': numeric,
              'unmapped_source_headers': [h for h in headers if h not in columns.values()],
              'source_rows': len(rows), 'retained_rows': len(kept),
              'excluded_rows': [{'row_number': n, 'reason': excluded[n]} for n in sorted(excluded)],
              'transformations': ['exact column rename and selection only; no unit conversion or value editing'],
              'author_confirmed_mapping_and_units': mapping.get('author_confirmed') is True,
              'author_confirmed_plot_context': mapping.get('plot_context_confirmed') is True,
              'plot_context': context.strip(),
              'ready_for_plot': bool(kept) and bool(numeric) and mapping.get('author_confirmed') is True
                                and mapping.get('plot_context_confirmed') is True and bool(context.strip())
                                and all(v.casefold() != 'unknown' for v in units.values())}
    output.mkdir(parents=True)
    with (output/'mapped.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(columns))
        writer.writeheader(); writer.writerows(kept)
    if excluded:
        with (output/'excluded-rows.csv').open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['source_row_number', 'reason', *headers])
            for number in sorted(excluded): writer.writerow([number, excluded[number], *rows[number-1]])
    (output/'prepare-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    read = sub.add_parser('inspect'); read.add_argument('--input', type=Path, required=True)
    make = sub.add_parser('prepare'); make.add_argument('--input', type=Path, required=True)
    make.add_argument('--mapping', type=Path, required=True); make.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.input) if args.action == 'inspect' else prepare(args.input, args.mapping, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
