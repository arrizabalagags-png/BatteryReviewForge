"""Validate files referenced by skills independently, including extracted single ZIPs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote

LINK = re.compile(r'\]\(([^\s)]+)\)')
SCRIPT = re.compile(r'(?<![\w/])scripts/[\w./-]+\.py')


def check_skill(folder: Path):
    folder = folder.resolve()
    issues = []
    if not (folder / 'SKILL.md').is_file():
        return ['Missing SKILL.md']
    for path in folder.rglob('*'):
        if path.is_symlink():
            issues.append(f'Linked file is not portable: {path.relative_to(folder)}')
        if path.suffix != '.md':
            continue
        content = path.read_text(encoding='utf-8-sig')
        for value in LINK.findall(content):
            if re.match(r'^(https?:|mailto:|data:|#)', value):
                continue
            value = unquote(value.split('#', 1)[0])
            target = (path.parent / value).resolve()
            if not target.is_relative_to(folder):
                issues.append(f'{path.relative_to(folder)} requires another package: {value}')
            elif not target.exists():
                issues.append(f'{path.relative_to(folder)} missing: {value}')
        # Entry-point executable references must be shipped, not merely documented.
        if path.name == 'SKILL.md':
            for value in sorted(set(SCRIPT.findall(content))):
                if not (folder / value).is_file():
                    issues.append(f'SKILL.md missing executable: {value}')
    required = ['references/EXECUTION.md', 'assets/templates/TASK_STATE.json', 'scripts/check_task_state.py']
    for value in required:
        if not (folder / value).is_file():
            issues.append('Missing execution contract: ' + value)
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-root', type=Path)
    parser.add_argument('--skill', type=Path, action='append', default=[])
    args = parser.parse_args()
    folders = list(args.skill)
    if args.skills_root:
        folders.extend(path for path in args.skills_root.iterdir() if path.is_dir() and (path / 'SKILL.md').is_file())
    if not folders:
        parser.error('Choose --skills-root or at least one --skill')
    results = {str(folder): check_skill(folder) for folder in folders}
    print(json.dumps({'standalone_reference_check': 'FAIL' if any(results.values()) else 'PASS', 'skills': results,
                      'host_discovery_and_model_behavior': 'NOT_TESTED'}, ensure_ascii=False, indent=2))
    return int(any(results.values()))


if __name__ == '__main__':
    raise SystemExit(main())
