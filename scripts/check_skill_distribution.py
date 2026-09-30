"""Check portable Markdown dependencies in each independently installed Skill.

Markdown links are document-relative. Bare scripts/references/assets/examples
paths are Skill-root-relative; ./ and ../ explicitly mean document-relative.
Repository-prefixed paths do not become portable just because the repo has them.
Only explicit parameter placeholders and output-option destinations are excluded.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PureWindowsPath
import re
import sys
from urllib.parse import unquote

LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(?:<(?P<angle>[^>\n]+)>|(?P<plain>[^\s)]+))(?:\s+[\"\'][^\n]*?[\"\'])?\s*\)')
DEFINITION = re.compile(r'^\s*\[[^\]\n]+\]:\s*(?:<(?P<angle>[^>\n]+)>|(?P<plain>[^\s]+))', re.MULTILINE)
URL = re.compile(r'(?:[A-Za-z][\w+.-]*://|mailto:|data:)[^\s`<>\"\']+')
PREFIX = r'(?:[A-Za-z]:[/\\]|[/\\])?(?:[\w.@%+~-]+[/\\])*'
ROOTS = r'(?:scripts|references|assets|examples)[/\\]'
BARE = re.compile(r'(?<![\w/\\])' + PREFIX + ROOTS + r'[^\s`\"\'<>，。；：、)]+')
QUOTED = re.compile(r'(?P<quote>[\"\'`])(?P<value>[^\n]+?)(?P=quote)')
OUTPUT = re.compile(r'--(?:out|output|output-dir|output-directory)(?:=|\s+)(?:[\"\'][^\"\'\n]+[\"\']|[^\s`]+)')
PLACEHOLDER = re.compile(r'<[^>]+>|\{[^}]+\}|\[[^\]]+\]|[*…]|(?:^|[/\\])\.\.\.(?:$|[/\\])')
PLACEHOLDER_PATH = re.compile(r'(?:[\w.-]+[/\\])*<[^>\n]+>(?:[/\\][^\s`\"\'<>]*)?')


def markdown_paths(content):
    """Yield actual local paths, with semantic origin and line number."""
    excluded = []
    for pattern in (LINK, DEFINITION):
        for match in pattern.finditer(content):
            value = match['angle'] or match['plain']
            excluded.append(match.span())
            yield value, True, content.count('\n', 0, match.start()) + 1
    excluded.extend(match.span() for pattern in (URL, OUTPUT, PLACEHOLDER_PATH) for match in pattern.finditer(content))
    # Full quoted paths can contain spaces; command strings are scanned below.
    for match in QUOTED.finditer(content):
        if any(a <= match.start() < b for a, b in excluded):
            continue
        value = match['value']
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '\"\'':
            value = value[1:-1]
        command_tail = re.search(r'\.(?:py|ps1|sh)\s+|\s--', value)
        if re.fullmatch(PREFIX + ROOTS + r'.+', value) and not command_tail and not any(char in value for char in ('\n', '=')):
            excluded.append(match.span())
            yield value, False, content.count('\n', 0, match.start()) + 1
    for match in BARE.finditer(content):
        if not any(a <= match.start() < b for a, b in excluded):
            yield match[0].rstrip('.,;:'), False, content.count('\n', 0, match.start()) + 1


def path_issue(folder, document, value, link):
    if value.startswith('#') or re.match(r'^(?:https?://|mailto:|data:)', value, re.IGNORECASE):
        return None
    value = unquote(value.split('#', 1)[0].split('?', 1)[0]).replace('\\', '/')
    if not value:
        return None
    if PLACEHOLDER.search(value):
        if link:
            return 'Placeholder is not a usable portable link: ' + value
        return None
    if value.startswith('/') or PureWindowsPath(value).is_absolute() or re.match(r'^[A-Za-z][\w+.-]*:', value):
        return 'Nonportable absolute/scheme path: ' + value
    base = document.parent if link or value.startswith(('./', '../')) else folder
    target = (base / value).resolve()
    if not target.is_relative_to(folder):
        return 'Requires another package/outside path: ' + value
    if not target.exists():
        return 'Missing portable dependency: ' + value
    return None


def check_skill(folder: Path):
    folder = folder.resolve()
    if not (folder / 'SKILL.md').is_file():
        return ['Missing SKILL.md']
    issues = []
    for path in sorted(folder.rglob('*')):
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            issues.append(f'Linked file is not portable: {path.relative_to(folder)}')
            continue
        if path.suffix.lower() != '.md' or not path.is_file():
            continue
        for value, link, number in markdown_paths(path.read_text(encoding='utf-8-sig')):
            issue = path_issue(folder, path, value, link)
            if issue:
                issues.append(f'{path.relative_to(folder)}:{number}: {issue}')
    for value in ('references/EXECUTION.md', 'assets/templates/TASK_STATE.json', 'scripts/check_task_state.py'):
        if not (folder / value).is_file():
            issues.append('Missing execution contract: ' + value)
    return list(dict.fromkeys(issues))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-root', type=Path)
    parser.add_argument('--skill', type=Path, action='append', default=[])
    args = parser.parse_args()
    folders = list(args.skill)
    if args.skills_root:
        if (args.skills_root / 'SKILL.md').is_file():
            folders.append(args.skills_root)
        elif args.skills_root.is_dir():
            folders.extend(p for p in args.skills_root.iterdir() if p.is_dir() and (p / 'SKILL.md').is_file())
    if not folders:
        parser.error('Choose a skills collection or at least one --skill')
    results = {str(folder): check_skill(folder) for folder in folders}
    print(json.dumps({'standalone_reference_check': 'FAIL' if any(results.values()) else 'PASS', 'skills': results,
                      'host_discovery_and_model_behavior': 'NOT_TESTED'}, ensure_ascii=False, indent=2))
    return int(any(results.values()))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    raise SystemExit(main())
