"""Check actual distributable ZIP contents, including each isolated Skill tree."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from check_skill_distribution import check_skill

ROOT = Path(__file__).resolve().parents[1]


def unpack(archive: ZipFile, target: Path) -> list[str]:
    assert archive.testzip() is None, "Corrupt ZIP member"
    names = archive.namelist()
    assert len(names) == len(set(names)), "Duplicate ZIP paths"
    for name in names:
        path = PurePosixPath(name)
        assert not path.is_absolute() and ".." not in path.parts and "\\" not in name and ":" not in name, name
        assert not name.startswith(("source/", "dist/", ".git/", "outputs/", ".qa/")), name
        assert not name.endswith(("i18n.js", "author-wechat.jpg", ".pyc", ".pyo")), name
        assert archive.getinfo(name).external_attr >> 16 & 0o170000 != 0o120000, "Symbolic link in ZIP"
    archive.extractall(target)
    return names


def inspect_skills(root: Path, ids: set[str], version: str) -> int:
    folders = [p for p in root.iterdir() if (p / "SKILL.md").is_file()]
    assert {p.name for p in folders} == ids, "Packaged Skill set differs from SKILL_NAMES"
    for folder in folders:
        issues = check_skill(folder)
        assert not issues, f"{folder.name}: {issues}"
        meta = json.loads((folder / "assets/SKILL_RELEASE.json").read_text(encoding="utf-8"))
        assert meta["version"] == version, (folder.name, meta)
    return len(folders)


def main() -> None:
    version = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    assert json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))["version"] == version
    release = json.loads((ROOT / "docs/RELEASE_STATUS.json").read_text(encoding="utf-8"))
    assert release["version"] == version and release["channel"] in {"beta", "stable"}
    if release["channel"] == "stable":
        assert all(release[key] == "PASS" for key in ["desktop_discovery_to_delivery", "flash_model_evaluation", "pro_model_evaluation"]), "Stable requires real host/model evidence"
    mapping = json.loads((ROOT / "docs/SKILL_NAMES.json").read_text(encoding="utf-8"))["skills"]
    ids = {x["id"] for x in mapping}
    assert ids == {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()}
    downloads = ROOT / "docs/downloads"
    full = downloads / f"BatteryReviewForge-v{version}.zip"
    collections = [downloads / f"BatteryReviewForge-WorkBuddy-v{version}.zip", downloads / f"BatteryReviewForge-WorkBuddy-Starter-v{version}.zip"]
    singles = [downloads / "single" / f"{key}-v{version}.zip" for key in sorted(ids)]
    workbuddy = [downloads / "workbuddy" / f"{key}-workbuddy-v{version}.zip" for key in sorted(ids)]
    files = [full, *collections, *singles, *workbuddy]
    report = []
    isolated_checks = 0
    for path in files:
        assert path.is_file() and path.stat().st_size > 0, f"Missing package: {path}"
        with TemporaryDirectory(prefix="voltpeer-distribution-") as directory, ZipFile(path) as archive:
            target = Path(directory)
            names = unpack(archive, target)
            if path == full:
                assert {"install.ps1", "install.sh", "docs/COMPATIBILITY.md", "docs/EVAL.md", "scripts/check_skill_distribution.py"} <= set(names)
                isolated_checks += inspect_skills(target / "skills", ids, version)
                assert json.loads((target / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"] == version
                assert json.loads((target / "docs/SKILL_NAMES.json").read_text(encoding="utf-8"))["skills"] == mapping
                for item in mapping:
                    folder = target / "skills" / item["id"]
                    assert item["display_name"] in (folder / "agents/openai.yaml").read_text(encoding="utf-8")
                    content = (folder / "SKILL.md").read_text(encoding="utf-8-sig")
                    assert f"name: {item['id']}" in content or f'name: "{item["id"]}"' in content
            elif path in collections:
                chosen = ids if "-Starter-" not in path.name else {"battery-review-figure", "battery-figure-assemble"}
                nested = list(target.glob("*.zip"))
                assert len(nested) == len(chosen)
                found = set()
                for i, packed in enumerate(nested):
                    sub = target / f"unpacked-{i}"
                    with ZipFile(packed) as inner:
                        unpack(inner, sub)
                    actual = {p.name for p in sub.iterdir() if (p / "SKILL.md").is_file()}
                    assert len(actual) == 1 and actual <= chosen and not (actual & found)
                    found.update(actual)
                    isolated_checks += inspect_skills(sub, actual, version)
                assert found == chosen
            else:
                actual = {p.name for p in target.iterdir() if (p / "SKILL.md").is_file()}
                assert len(actual) == 1 and actual <= ids
                isolated_checks += inspect_skills(target, actual, version)
        report.append({"file": path.relative_to(downloads).as_posix(), "bytes": path.stat().st_size,
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    recipe_index=json.loads((downloads/'recipes/recipe-packs.json').read_text(encoding='utf-8'))
    assert {row['resource_id'] for row in recipe_index['packs']} == {'full_cell','li_li','operando_xrd'}
    for row in recipe_index['packs']:
        assert row['version'] == version and Path(row['file']).name == row['file']
        path=downloads/'recipes'/row['file']
        assert path.stat().st_size == row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        with TemporaryDirectory(prefix='voltpeer-recipe-gate-') as directory, ZipFile(path) as archive:
            target=Path(directory);names=unpack(archive,target)
            roots=[p for p in target.iterdir() if p.is_dir()]
            assert len(roots)==1
            package=roots[0]
            assert all((package/f).is_file() for f in ['AGENT_GUIDE.md','input_contract.json','config.demo.json','config.real.example.json','src/plot.py','checks.py','requirements.txt','LICENSE'])
            manifest=json.loads((package/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
            assert manifest['resource_id']==row['resource_id'] and manifest['version']==version
            for item in manifest['files']:
                checked=(package/item['path']).resolve()
                assert checked.is_relative_to(package.resolve()) and checked.is_file()
                assert hashlib.sha256(checked.read_bytes()).hexdigest()==item['sha256']
        report.append({'file':path.relative_to(downloads).as_posix(),'bytes':row['bytes'],'sha256':row['sha256']})
    outputs = ROOT / "outputs"
    outputs.mkdir(exist_ok=True)
    result = {"version": version, "channel": release["channel"], "archives": report,
              "isolated_skill_checks": isolated_checks, "real_host_model_behavior": "NOT_RUN"}
    (outputs / "version-consistency.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    checksums = "".join(f"{r['sha256']}  {r['file']}\n" for r in report)
    (downloads / "distribution-sha256.txt").write_text(checksums, encoding="utf-8")
    (outputs / "distribution-sha256.txt").write_text(checksums, encoding="utf-8")
    print(json.dumps({"version": version, "channel": release["channel"], "checked_archives": len(report),
                      "isolated_skill_checks": isolated_checks, "result": "passed"}))


if __name__ == "__main__":
    main()
