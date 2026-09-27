"""Package paired synthetic example CSVs for the beginner guide."""
from pathlib import Path
import json
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "showcase"
DEST = ROOT / "docs" / "assets" / "showcase"

BUNDLES = {
    "full-cell": ("full_cell", {"data.csv": "cycling.csv", "voltage_profiles.csv": "voltage_profiles.csv"},
                  "These files are synthetic demonstration data, not experimental results.\nGive both CSV files to BatteryReviewForge. Check columns, units and cell conditions before plotting.\n"),
    "li-cu-ce": ("li_cu_ce", {"data.csv": "ce.csv", "profiles.csv": "voltage_profiles.csv"},
                 "These files are synthetic demonstration data, not experimental results.\nThis is cycle-by-cycle Li||Cu CE, not an Aurbach protocol. Give both CSV files to BatteryReviewForge.\n"),
}


def main() -> None:
    for name, (source_dir, files, readme) in BUNDLES.items():
        target = DEST / f"BRF-demo-{name}.zip"
        folder = f"BRF-demo-{name}"
        with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
            for old, new in files.items():
                archive.write(SOURCE / source_dir / old, f"{folder}/{new}")
            metadata = json.loads((SOURCE / source_dir / 'metadata.json').read_text(encoding='utf-8'))
            metadata['source_files'] = [files[name] for name in metadata['source_files']]
            archive.writestr(f'{folder}/metadata.json', json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
            archive.writestr(f"{folder}/README.txt", '这是虚构演示数据，不是实验结果。\n把整个文件夹交给 AI 软件，先读取 metadata.json 的单位、测试条件和 source_files，再画图。\n输出到新建 brf-output，保留输入文件。\n\n' + readme)
        print(target)
    # Retain relative paths for composites whose inputs live in neighbouring samples.
    for sample in sorted(SOURCE.iterdir()):
        metadata_file = sample / 'metadata.json'
        if not metadata_file.is_file():
            continue
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        paths = {metadata_file}
        for name in metadata['source_files']:
            path = (sample / name).resolve()
            if not path.is_relative_to(SOURCE.resolve()) or not path.is_file():
                raise ValueError(f'Invalid example input: {name}')
            paths.add(path)
            neighbour = path.parent / 'metadata.json'
            if neighbour.is_file():
                paths.add(neighbour)
        target = DEST / f'BRF-demo-{sample.name}.zip'
        with ZipFile(target, 'w', compression=ZIP_DEFLATED) as archive:
            for path in sorted(paths):
                archive.write(path, path.relative_to(SOURCE.resolve()).as_posix())
            archive.writestr('README.txt', f'BatteryReviewForge 示例：{sample.name}\n这是虚构演示数据，不是实验结果。\n请先阅读 {sample.name}/metadata.json 的 source_files、单位、条件和图型。\n全部输入保留相对路径；不要移动或改名其中单个 CSV。\n让 AI 软件核对文件后绘图；输出到新建 brf-output，保留原始输入。\n')


if __name__ == "__main__":
    main()
