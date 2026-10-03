"""Package independent gallery redraws; never generate or alter source data."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples/showcase"
DEST = ROOT / "docs/assets/showcase"
FAMILIES = {
 "build": ("full_cell", "li_cu_ce", "li_li", "eis", "operando_xrd", "tof_sims", "integrated_study",
           "rate_capability", "gcd_profiles", "pouch_thermal", "literature_benchmark", "reporting_matrix", "capability_spread", "style_presets"),
 "advanced": ("cyclic_voltammetry", "differential_capacity", "gitt_pulse", "ionic_conductivity", "xps_components", "raman_series"),
 "corpus": ("ftir", "nmr", "rdf_coordination", "msd", "lsv", "transference"),
 "electrochem": ("aurbach_protocol", "eis_frequency", "chronoamperometry", "ocv_rest"),
}
NAMES = tuple(name for names in FAMILIES.values() for name in names)
LEGACY = {
 "full-cell": ("full_cell", {"data.csv": "cycling.csv", "voltage_profiles.csv": "voltage_profiles.csv"}),
 "li-cu-ce": ("li_cu_ce", {"data.csv": "ce.csv", "profiles.csv": "voltage_profiles.csv"}),
}
REQUIREMENTS = "numpy>=1.26,<3\nmatplotlib>=3.8,<4\n"


def digest(content):
    return hashlib.sha256(content).hexdigest()


def family_for(name):
    for family, names in FAMILIES.items():
        if name in names:
            return family
    raise ValueError(f"No standalone redraw contract for {name!r}")


def input_closure(name, source=SOURCE):
    """Resolve declared files and composite members, not all gallery images."""
    source = source.resolve()
    collected, visited = set(), set()

    def existing(path):
        path = path.resolve()
        if not path.is_relative_to(source) or not path.is_file():
            raise ValueError(f"Missing or unsafe gallery input: {path.name}")
        return path

    def add_file(path):
        path = existing(path)
        if path in collected:
            return
        collected.add(path)
        if path.suffix == ".json" and path.name != "metadata.json":
            value = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(value, dict):
                for member in value.get("members", []):
                    visit(member)
                for relative in value.get("uses", []):
                    if not isinstance(relative, str):
                        raise ValueError("Composite uses must be relative paths")
                    add_file(path.parent / relative)

    def visit(identity):
        if not isinstance(identity, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", identity):
            raise ValueError(f"Invalid gallery member: {identity!r}")
        if identity in visited:
            return
        visited.add(identity)
        folder = source / identity
        path = existing(folder / "metadata.json")
        metadata = json.loads(path.read_text(encoding="utf-8-sig"))
        if not metadata.get("scientific_basis"):
            raise ValueError(f"{identity}: scientific model record required before packaging")
        collected.add(path)
        for relative in metadata["source_files"]:
            if not isinstance(relative, str):
                raise ValueError("source_files must contain relative paths")
            path = existing(folder / relative)
            add_file(path)
            if (path.parent / "metadata.json").is_file() and path.parent != folder:
                visit(path.parent.name)

    visit(name)
    return sorted(collected)


def code_files(family, repo=ROOT):
    scripts = repo / "skills/voltpeer-plot/scripts"
    # __init__ imports all chart/export modules; specialist imports both corpus
    # and electrochem. Include that Python closure without unrelated Skills.
    paths = [repo / f"examples/showcase/{family}.py",
             repo / "examples/recipe_packs/_runtime/generate_demo.py", scripts / "output_safety.py",
             repo / "skills/voltpeer-plot/assets/figure_theme.json",
             repo / "skills/voltpeer-plot/assets/SKILL_RELEASE.json"]
    paths.extend(sorted((scripts / "batteryplot").glob("*.py")))
    if any(not path.is_file() for path in paths):
        raise ValueError("The standalone renderer source closure is incomplete")
    return sorted(set(paths))


def readme(name, metadata):
    return (f"VoltPeer 示例：{name}\n\n"
      "包含样图、示例数据和 Python 源码。数据由声明的教学模型生成，不是实验结果。\n"
      f"先看 {metadata} 中的列名、单位、测试条件和模型说明。\n\n"
      "重画示例（无需 AI，也不调用模型）：\n"
      "  python -m venv .venv\n"
      "  Windows: .venv\\Scripts\\python -m pip install -r requirements.txt\n"
      "  Windows: .venv\\Scripts\\python render_existing.py --output brf-output\n"
      "  macOS/Linux: .venv/bin/python -m pip install -r requirements.txt\n"
      "  macOS/Linux: .venv/bin/python render_existing.py --output brf-output\n\n"
      "已备好 numpy 和 matplotlib 的环境可直接运行最后一条命令。\n"
      "结果在 brf-output：PNG、SVG、PDF、本次输入副本和运行记录。目录已存在时会停止，请换一个名称。\n\n"
      "换成自己的数据：保留整个文件夹和相对路径，让 AI 对照样图与 code/ 源码核对列名、单位、测试条件和坐标范围，再替换 CSV。\n"
      "这是同类型图的源码起点，不会自动识别任意仪器表头。换过的输入只记为待核对的作者数据，不沿用示例的科学背书。\n"
      "有意调整 code/ 中的源码后，运行命令加 --allow-code-changes；改后的文件哈希会单独记录，缺文件仍会停止。\n"
      "你也可以用自己的话说：照这张图，用我的数据画；先问清楚缺的条件，原文件不要改。\n\n"
      "Synthetic teaching models, not measured data. Run render_existing.py to redraw the existing CSVs only.\n"
      "Check columns, units, conditions and axis limits before replacing data. The reference model does not validate author inputs.\n"
      "The runner never regenerates data, overwrites output, installs packages or calls an online service.\n"
      "SOURCE_MANIFEST.json records actual included bytes, without claiming an old GitHub commit contains this package.\n")


def package_sample(name, output=DEST, *, repo=ROOT, source=SOURCE, alias=None):
    family = family_for(name)
    inputs = input_closure(name, source)
    source, repo, output = source.resolve(), repo.resolve(), output.resolve()
    payload, manifest_inputs = {}, []
    prefix = f"BRF-demo-{alias}/" if alias else ""
    aliases = LEGACY[alias][1] if alias else {}
    for path in inputs:
        render_path = path.relative_to(source).as_posix()
        packed, archive_path = path.read_bytes(), render_path
        if alias and path.parent == source / name:
            archive_path = aliases.get(path.name, path.name)
            if path.name == "metadata.json":
                value = json.loads(packed)
                value["source_files"] = [aliases.get(entry, entry) for entry in value["source_files"]]
                packed = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        payload[archive_path] = packed
        manifest_inputs.append({"archive_path": archive_path, "render_path": render_path,
                                "sha256": digest(packed), "original_sha256": digest(path.read_bytes())})
    code = []
    for path in code_files(family, repo):
        original = path.relative_to(repo).as_posix()
        archive_path, content = "code/" + original, path.read_bytes()
        payload[archive_path] = content
        code.append({"archive_path": archive_path, "repository_path": original, "sha256": digest(content)})
    payload["render_existing.py"] = (repo / "examples/demo_bundle_runner.py").read_bytes()
    code.append({"archive_path": "render_existing.py", "repository_path": "examples/demo_bundle_runner.py",
                 "sha256": digest(payload["render_existing.py"])})
    for suffix in ("png", "svg", "pdf"):
        path = source / name / f"figure.{suffix}"
        if not path.is_file():
            raise ValueError(f"{name}: render the reference before packaging")
        payload[f"reference/figure.{suffix}"] = path.read_bytes()
    payload["reference/metadata.json"] = (source / name / "metadata.json").read_bytes()
    payload["requirements.txt"] = REQUIREMENTS.encode("utf-8")
    payload["README.txt"] = readme(name, "metadata.json" if alias else name + "/metadata.json").encode("utf-8")
    payload["LICENSE"] = (repo / "LICENSE").read_bytes()
    manifest = {"schema_version": 1, "sample": name, "renderer": f"examples/showcase/{family}.py",
      "entry_point": "render_existing.py", "operation": "render_existing_inputs_only",
      "source_snapshot": "archive-contained bytes; no remote publication asserted",
      "input_policy": "author changes recorded; model not certified for changed data",
      "output_policy": "new directory only; original inputs never written", "code": code, "inputs": manifest_inputs,
      "files": [{"path": path, "sha256": digest(content)} for path, content in sorted(payload.items())]}
    payload["SOURCE_MANIFEST.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"BRF-demo-{alias or name}.zip"
    handle = tempfile.NamedTemporaryFile(prefix=".demo-bundle-", suffix=".zip", dir=output, delete=False)
    temporary = Path(handle.name)
    handle.close()
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for relative, content in sorted(payload.items()):
                info = ZipInfo(prefix + relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type, info.external_attr = ZIP_DEFLATED, 0o100644 << 16
                archive.writestr(info, content)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return {"sample": name, "file": target.name, "bytes": target.stat().st_size,
            "sha256": digest(target.read_bytes()), "input_files": len(inputs), "code_files": len(code), "standalone_redraw": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEST)
    parser.add_argument("--name", choices=NAMES, action="append")
    parser.add_argument("--no-legacy", action="store_true")
    args = parser.parse_args()
    names = args.name or NAMES
    rows = [package_sample(name, args.out) for name in names]
    if not args.no_legacy:
        rows += [package_sample(name, args.out, alias=alias) for alias, (name, _) in LEGACY.items() if name in names]
    print(json.dumps({"canonical_count": len(names), "packages": rows}, ensure_ascii=False))


if __name__ == "__main__":
    main()
