"""Explicitly create invented tutorial data. Never imported by the real renderer."""
import argparse
import csv
import json
import math
from pathlib import Path
import sys

PACK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACK / 'src'))
from output_safety import new_directory
from cli_runtime import configure_utf8


def write_csv(path, headers, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def main():
    configure_utf8()
    parser = argparse.ArgumentParser(description='仅生成明确标识的原创合成数据；不能替代作者数据。')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root, _ = new_directory(args.out.resolve())
    config = json.loads((PACK / 'config.demo.json').read_text(encoding='utf-8-sig'))
    kind = config['resource_id']
    samples = ['Demo sample A', 'Demo sample B']
    if kind == 'full_cell':
        rows = [(s, c, 170 - i * 6 - c * (0.22 + i * 0.05), 98.7 + (1 - math.exp(-c / 8)) * .7) for i, s in enumerate(samples) for c in range(1, 41)]
        write_csv(root / 'cycling.csv', ['sample', 'cycle', 'capacity', 'ce'], rows)
        profiles = [(s, c, q, 4.2 - 1.3 * q / (170 - i * 6 - c * (.22 + i * .05))) for i, s in enumerate(samples) for c in (1, 20, 40) for q in [j * (170 - i * 6 - c * (.22 + i * .05)) / 25 for j in range(26)]]
        write_csv(root / 'profiles.csv', ['sample', 'cycle', 'capacity', 'voltage'], profiles)
    elif kind == 'li_li':
        rows = [(s, j / 20, (1 if int(j / 20) % 2 == 0 else -1) * (20 + i * 12 + .12 * j / 20 + 3 * math.sin(j / 20 * math.pi))) for i, s in enumerate(samples) for j in range(801)]
        write_csv(root / 'trace.csv', ['sample', 'time', 'voltage'], rows)
    else:
        rows, voltage = [], []
        for sample in samples[:1]:
            for j in range(16):
                progress = j / 15
                voltage.append((sample, progress, 3.1 + 1.1 * progress))
                for k in range(65):
                    theta = 35 + k * .125
                    intensity = .04 + math.exp(-((theta - (38 + progress * .6)) / .3) ** 2) + .6 * math.exp(-((theta - (41.3 - progress * .3)) / .4) ** 2)
                    rows.append((sample, theta, progress, intensity))
        write_csv(root / 'diffraction.csv', ['sample', 'two_theta', 'progress', 'intensity'], rows)
        write_csv(root / 'voltage.csv', ['sample', 'progress', 'voltage'], voltage)
    for table in config['data'].values():
        table['path'] = Path(table['path']).name
    (root / 'config.demo.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('原创合成数据：' + str(root))


if __name__ == '__main__':
    main()
