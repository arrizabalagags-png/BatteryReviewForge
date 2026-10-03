"""Check actual distributable ZIP contents, including each isolated Skill tree."""
from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from check_skill_distribution import check_skill
from check_skill_dependencies import check_skill_dependencies
from check_demo_metadata import check_demo, validate_metadata

ROOT = Path(__file__).resolve().parents[1]


def inspect_full_source_payload(archive: ZipFile, names: list[str]) -> int:
    """Require the complete full-package payload, including installers and plugin assets."""
    from package_release import TOP_LEVEL, PUBLIC_DOCS
    files = [ROOT/name for name in TOP_LEVEL+PUBLIC_DOCS]
    files += [p for folder in ('.codex-plugin','skills','evals') for p in (ROOT/folder).rglob('*')]
    expected = {p.relative_to(ROOT).as_posix():p for p in files
                if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'}}
    assert set(names) == set(expected), 'Full package file set differs from source payload'
    for name, source in expected.items():
        assert archive.read(name) == source.read_bytes(), 'Full package source bytes differ: '+name
    return len(expected)


def same_source(left: Path, right: Path) -> bool:
    """Git checkouts may normalize CRLF; archive manifest hashes stay byte-exact."""
    actual, expected = left.read_bytes(), right.read_bytes()
    if right.suffix in {".py", ".txt", ".json", ".md", ".csv", ".svg", ".yaml", ".yml", ".cff", ".sh", ".ps1"} or right.name == "LICENSE":
        actual, expected = actual.replace(b"\r\n", b"\n"), expected.replace(b"\r\n", b"\n")
    return actual == expected


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
        dependencies = check_skill_dependencies(folder)
        assert dependencies["status"] == "PASS", (folder.name, dependencies["issues"], dependencies["unresolved_dynamic_imports"])
        meta = json.loads((folder / "assets/SKILL_RELEASE.json").read_text(encoding="utf-8"))
        assert meta["version"] == version, (folder.name, meta)
        source = ROOT / "skills" / folder.name
        # Check actual downloaded files, including lazy imports, requirements,
        # CJK glyph handling, palettes and frame/export gates. Frontmatter may
        # vary by host; the scientific/execution body must still match.
        expected = {p.relative_to(source).as_posix() for p in source.rglob("*")
                    if p.is_file() and p.name != "SKILL.md" and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}}
        actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*")
                  if p.is_file() and p.name != "SKILL.md"}
        assert actual == expected, f"{folder.name}: downloaded file set differs"
        for name in sorted(expected):
            assert (folder / name).read_bytes() == (source / name).read_bytes(), (folder.name, name)
        original = (source/"SKILL.md").read_text(encoding="utf-8-sig")
        packed = (folder/"SKILL.md").read_text(encoding="utf-8-sig")
        assert original.split("---", 2)[2] == packed.split("---", 2)[2], f"{folder.name}: Skill body differs"
    return len(folders)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-only', action='store_true', help='Check the current renamed Skill archives; preserve historical scientific packages without rebuilding them.')
    parser.add_argument('--download-root', type=Path, help='Inspect a separate current distribution directory, without touching frozen download bytes.')
    parser.add_argument('--report-dir', type=Path, help='Write this check record to a new evidence directory.')
    args = parser.parse_args()
    version = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    assert json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))["version"] == version
    release = json.loads((ROOT / "docs/RELEASE_STATUS.json").read_text(encoding="utf-8"))
    assert release["version"] == version and release["channel"] in {"beta", "stable"}
    if release["channel"] == "stable":
        assert all(release[key] == "PASS" for key in ["desktop_discovery_to_delivery", "flash_model_evaluation", "pro_model_evaluation"]), "Stable requires real host/model evidence"
    mapping = json.loads((ROOT / "docs/SKILL_NAMES.json").read_text(encoding="utf-8"))["skills"]
    ids = {x["id"] for x in mapping}
    assert ids == {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()}
    historical_downloads = ROOT / "docs/downloads"
    downloads = (args.download_root or historical_downloads/f"v{version}").resolve()
    full = downloads / f"VoltPeer-v{version}.zip"
    collections = [downloads / f"VoltPeer-WorkBuddy-v{version}.zip", downloads / f"VoltPeer-WorkBuddy-Starter-v{version}.zip"]
    singles = [downloads / "single" / f"{key}-v{version}.zip" for key in sorted(ids)]
    workbuddy = [downloads / "workbuddy" / f"{key}-workbuddy-v{version}.zip" for key in sorted(ids)]
    files = [full, *collections, *singles, *workbuddy]
    report = []
    isolated_checks = 0
    full_source_files = 0
    for path in files:
        assert path.is_file() and path.stat().st_size > 0, f"Missing package: {path}"
        with TemporaryDirectory(prefix="voltpeer-distribution-") as directory, ZipFile(path) as archive:
            target = Path(directory)
            names = unpack(archive, target)
            if path == full:
                full_source_files = inspect_full_source_payload(archive, names)
                assert {"install.ps1", "install.sh", "docs/COMPATIBILITY.md", "docs/EVAL.md", "docs/DEMO_METADATA_SCHEMA.json",
                        "skill-migration.tsv", "docs/SKILL_MIGRATION.json", "docs/NAMING_MIGRATION.md", "plugin.json",
                        ".agents/plugins/marketplace.json", "assets/brand.svg",
                        "docs/validation/2026-09-30-frame-final-regression.json", "docs/validation/2026-09-30-frame-regression-initial.json",
                        "scripts/check_skill_distribution.py", "scripts/check_skill_dependencies.py", "scripts/check_demo_metadata.py"} <= set(names)
                for name in ("docs/DEMO_METADATA_SCHEMA.json", "scripts/check_skill_dependencies.py", "scripts/check_demo_metadata.py",
                             "install.ps1", "install.sh", "skill-migration.tsv", "docs/SKILL_MIGRATION.json", "plugin.json",
                             "docs/validation/2026-09-30-frame-final-regression.json", "docs/validation/2026-09-30-frame-regression-initial.json"):
                    assert same_source(target / name, ROOT / name), name
                migration = json.loads((target / "docs/SKILL_MIGRATION.json").read_text(encoding="utf-8"))
                assert migration["canonical_only"] is True and migration["install_legacy_aliases"] is False
                plugin = json.loads((target / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
                marketplace = json.loads((target / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
                assert plugin["name"] == marketplace["name"] == marketplace["plugins"][0]["name"] == "voltpeer"
                assert plugin["interface"]["displayName"] == marketplace["interface"]["displayName"] == "VoltPeer"
                assert marketplace["plugins"][0]["source"]["url"] == "https://github.com/arrizabalagags-png/Voltpeer-skills.git"
                assert plugin["interface"]["logo"] in names
                assert (target / plugin["interface"]["logo"]).read_bytes() == (ROOT / plugin["interface"]["logo"]).read_bytes()
                isolated_checks += inspect_skills(target / "skills", ids, version)
                assert json.loads((target / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"] == version
                assert json.loads((target / "docs/SKILL_NAMES.json").read_text(encoding="utf-8"))["skills"] == mapping
                for item in mapping:
                    folder = target / "skills" / item["id"]
                    assert item["display_name"] in (folder / "agents/openai.yaml").read_text(encoding="utf-8")
                    content = (folder / "SKILL.md").read_text(encoding="utf-8-sig")
                    assert f"name: {item['id']}" in content or f'name: "{item["id"]}"' in content
            elif path in collections:
                chosen = ids if "-Starter-" not in path.name else {"voltpeer-plot", "voltpeer-assemble"}
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
    if args.skills_only:
        result = {'version': version, 'channel': release['channel'], 'scope': f'{len(report)} archives containing {isolated_checks} isolated Skill copies; historical science examples and packages are separately protected by immutable hashes.',
                  'archives': report, 'isolated_skill_checks': isolated_checks, 'real_host_model_behavior': 'NOT_RUN', 'native_discovery': 'NOT_RUN'}
        record = (args.report_dir/'skill-distribution-check.json') if args.report_dir else ROOT / f'docs/validation/2026-10-02-naming-distribution-v{version}.json'
        record.parent.mkdir(parents=True,exist_ok=True)
        record.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'status':'PASS', 'archives':len(report), 'isolated_skill_checks':isolated_checks, 'version':version, 'scope':'skills-only'}))
        return
    recipe_index=json.loads((historical_downloads/'recipes/recipe-packs.json').read_text(encoding='utf-8'))
    assert {row['resource_id'] for row in recipe_index['packs']} == {'full_cell','li_li','operando_xrd'}
    for row in recipe_index['packs']:
        recipe_version = row['version']
        assert Path(row['file']).name == row['file']
        path=historical_downloads/'recipes'/row['file']
        assert path.stat().st_size == row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        with TemporaryDirectory(prefix='voltpeer-recipe-gate-') as directory, ZipFile(path) as archive:
            target=Path(directory);names=unpack(archive,target)
            roots=[p for p in target.iterdir() if p.is_dir()]
            assert len(roots)==1
            package=roots[0]
            assert all((package/f).is_file() for f in ['AGENT_GUIDE.md','input_contract.json','config.demo.json','config.real.example.json','src/plot.py','checks.py','requirements.txt','LICENSE'])
            manifest=json.loads((package/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
            assert manifest['resource_id']==row['resource_id'] and manifest['version']==recipe_version
            declared = [item['path'] for item in manifest['files']]
            actual = {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file() and p.name != 'PACKAGE_MANIFEST.json'}
            assert len(declared) == len(set(declared)) and set(declared) == actual, 'Manifest file closure differs'
            for item in manifest['files']:
                checked=(package/item['path']).resolve()
                assert checked.is_relative_to(package.resolve()) and checked.is_file()
                assert hashlib.sha256(checked.read_bytes()).hexdigest()==item['sha256']
            source = ROOT / 'examples/recipe_packs' / row['resource_id']
            for name in actual:
                assert same_source(package/name, source/name), (row['resource_id'], name)
            runtime = ROOT / 'examples/recipe_packs/_runtime/recipe_runtime.py'
            assert same_source(package/'src/recipe_runtime.py', runtime)
            assert same_source(package/'src/font_coverage.py', runtime.parent/'font_coverage.py')
            assert same_source(package/'src/renderer.py', runtime.parent/f"render_{row['resource_id']}.py")
            for name in ('output_safety.py', 'delivery_contract.py', 'share_bundle.py', 'cli_runtime.py'):
                assert same_source(package/'src'/name, ROOT/'scripts/runtime_contract'/name)
            reference = json.loads((package/'reference/metadata.json').read_text(encoding='utf-8'))
            validate_metadata(reference)
            sources = json.loads((package/'sources.json').read_text(encoding='utf-8'))
            config = json.loads((package/'config.demo.json').read_text(encoding='utf-8'))
            model = json.loads((package/'demo/model.json').read_text(encoding='utf-8'))
            records = json.loads((package/'reference/data_checks.json').read_text(encoding='utf-8'))
            assert reference['figure_grammar_id'] == 'adaptable_recipe:' + row['resource_id']
            assert reference['scientific_basis'] == sources['scientific_basis'] == model
            assert sources['config_demo_sha256'] == hashlib.sha256((package/'config.demo.json').read_bytes()).hexdigest()
            assert sources['model_sha256'] == hashlib.sha256((package/'demo/model.json').read_bytes()).hexdigest()
            expected_inputs = {table['path']: hashlib.sha256((package/table['path']).read_bytes()).hexdigest() for table in config['data'].values()}
            assert sources['demo_inputs_sha256'] == expected_inputs, 'Reference must use its own recipe CSVs'
            assert {record['sha256'] for record in records['input_records']} == set(expected_inputs.values())
            assert records['resource_id'] == row['resource_id'] and records['pack_version'] == recipe_version
            for name, expected in sources['reference_sha256'].items():
                assert hashlib.sha256((package/name).read_bytes()).hexdigest() == expected
            for name in reference['source_files']:
                checked = (package/'reference'/name).resolve()
                assert checked.is_relative_to(package.resolve()) and checked.is_file()
        report.append({'file':path.relative_to(historical_downloads).as_posix(),'bytes':row['bytes'],'sha256':row['sha256'], 'preserved_version':recipe_version})
    starter_folder = downloads/'starter'
    starter_index = json.loads((starter_folder/'plot-starter.json').read_text(encoding='utf-8'))
    assert starter_index['schema_version'] == 1 and len(starter_index['packs']) == 1
    for row in starter_index['packs']:
        assert row['resource_id'] == 'plot_starter' and row['version'] == version and row['channel'] == release['channel']
        assert row['hosts'] == ['dsh','codex'] and row['scientific_runtime'] == 'batteryplot'
        assert Path(row['file']).name == row['file']
        path = starter_folder/row['file']
        assert path.stat().st_size == row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        with TemporaryDirectory(prefix='voltpeer-starter-gate-') as directory, ZipFile(path) as archive:
            target = Path(directory)
            unpack(archive, target)
            assert {p.name for p in target.iterdir()} == {'plot_starter'}
            package = target/'plot_starter'
            manifest = json.loads((package/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
            assert manifest['version'] == version and manifest['resource_id'] == row['resource_id']
            assert manifest['scientific_runtime'] == 'batteryplot' and manifest['api_key_for_install'] is False
            declared = [item['path'] for item in manifest['files']]
            actual = {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file() and p.name != 'PACKAGE_MANIFEST.json'}
            assert len(declared) == len(set(declared)) and set(declared) == actual
            assert {'start.py','README.md','AGENT_GUIDE.md','INPUT_GUIDE.md','LICENSE','HOSTS.json','DEMO_INDEX.json'} <= actual
            for item in manifest['files']:
                checked = (package/item['path']).resolve()
                assert checked.is_relative_to(package.resolve()) and checked.is_file()
                assert hashlib.sha256(checked.read_bytes()).hexdigest() == item['sha256']
            for name in ('start.py','README.md','AGENT_GUIDE.md','INPUT_GUIDE.md'):
                assert same_source(package/name, ROOT/'scripts/starter'/name)
            isolated_checks += inspect_skills(package/'skills', {'voltpeer-plot'}, version)
            assert len(list(package.rglob('batteryplot/__init__.py'))) == 1, 'Host adapters must not fork the scientific runtime'
            demos = json.loads((package/'DEMO_INDEX.json').read_text(encoding='utf-8'))
            assert set(demos) == set(row['plot_kinds']) and len(demos) == 10
            for item in demos.values():
                assert item['data_status'] == 'synthetic_demo' and item['author_data_fallback'] is False
                for key in ('data','metadata'):
                    assert (package/item[key]).resolve().is_relative_to(package.resolve()) and (package/item[key]).is_file()
        report.append({'file':path.relative_to(downloads).as_posix(),'bytes':row['bytes'],'sha256':row['sha256']})
    demo_checks = []
    for metadata in sorted((ROOT/'examples/showcase').glob('*/metadata.json')):
        identity = metadata.parent.name
        demo_checks.append(check_demo(metadata.parent, ROOT/'docs/assets/showcase'/identity,
                                      ROOT/f'docs/assets/showcase/BRF-demo-{identity}.zip'))
    assert len(demo_checks) == 30, 'Expected 30 current canonical demos'
    outputs = ROOT / "outputs"
    outputs.mkdir(exist_ok=True)
    result = {"version": version, "channel": release["channel"], "archives": report,
              "full_package_source_file_count":full_source_files,
              "full_package_source_payload_set_and_bytes":"PASS",
              "scope": "34 current archives containing 63 isolated Skill copies, plus 3 preserved recipe archives and 30 historical demo metadata checks; no model or native host gate.",
              "current_archive_count": 34, "preserved_recipe_archive_count": 3,
              "isolated_skill_checks": isolated_checks, "ast_dependency_checks": isolated_checks,
              "downloaded_skill_file_closure_and_body": "PASS", "downloaded_python_requirements_match_source": "PASS",
              "text_source_comparison": "Current packaged non-SKILL files are byte-exact; host-specific SKILL frontmatter may differ, with the body unchanged. Historical recipe text comparisons normalize CRLF/LF. ZIP manifests and archive hashes are byte-exact.",
              "recipe_runtime_and_manifest_closure": "PASS",
              "plot_starter_manifest_and_single_runtime_closure": "PASS",
              "demo_schema_source_site_zip_checks": demo_checks, "real_host_model_behavior": "NOT_RUN"}
    (outputs / "version-consistency.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    current = [r for r in report if 'preserved_version' not in r]
    assert len(current) == 34 and isolated_checks == 63 and len(report) == 37
    checksums = "".join(f"{r['sha256']}  {r['file']}\n" for r in current)
    (downloads / "distribution-sha256.txt").write_text(checksums, encoding="utf-8")
    index = {'schema_version':1,'brand':'VoltPeer','version':version,'channel':release['channel'],
             'publication':'LOCAL_CANDIDATE_NOT_PUSHED_NOT_RELEASED','base_url':f'downloads/v{version}/',
             'current_archive_count':len(current),'archives':current,
             'skill_ids':sorted(ids),'primary_skill_ids':json.loads((ROOT/'docs/SKILL_NAMES.json').read_text(encoding='utf-8'))['primary_skill_ids'],
             'preserved_science_archives':[r for r in report if 'preserved_version' in r],
             'contains_experimental_data':False,'native_host_discovery':'NOT_RUN','full_model_gate':'NOT_RUN'}
    (downloads/'download-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (outputs / "distribution-sha256.txt").write_text(checksums, encoding="utf-8")
    print(json.dumps({"version": version, "channel": release["channel"], "checked_archives": len(report),
                      "isolated_skill_checks": isolated_checks, "ast_dependency_checks": isolated_checks,
                      "canonical_demo_schema_checks": len(demo_checks), "result": "passed"}))


if __name__ == "__main__":
    main()
