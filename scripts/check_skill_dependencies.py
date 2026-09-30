"""Statically match shipped Skill Python imports to its own requirements.

No package is imported or installed. Stdlib and actually shipped local modules
are distinguished from third-party modules; lazy/optional imports remain visible.
Dynamic nonliteral imports are NOT_TESTED rather than silently approved.
"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import re
import sys

MODULE_DISTRIBUTIONS = {'PIL': 'Pillow', 'pptx': 'python-pptx', 'pymupdf': 'PyMuPDF',
                        'fitz': 'PyMuPDF', 'cairosvg': 'CairoSVG'}
OPTIONAL = {'battery-figure-assemble': {'cairosvg': 'SVG input additionally requires native Cairo'}}


def normalize(value):
    return re.sub(r'[-_.]+', '-', value).lower()


def skill_id(folder):
    content = (folder / 'SKILL.md').read_text(encoding='utf-8-sig')
    match = re.search(r'^name:\s*[\"\']?([\w-]+)', content, re.MULTILINE)
    return match.group(1) if match else folder.name


def skill_folders(root):
    root = root.resolve()
    if (root / 'SKILL.md').is_file():
        return [root]
    return sorted(p for p in root.iterdir() if p.is_dir() and (p / 'SKILL.md').is_file()) if root.is_dir() else []


def requirements(path, folder, seen=None):
    """Parse current local requirement lines/includes, refusing unsupported forms."""
    path, folder = path.resolve(), folder.resolve()
    seen = set() if seen is None else seen
    if not path.is_relative_to(folder) or path in seen:
        raise ValueError(f'Requirements include outside skill or recursive: {path}')
    if not path.is_file():
        raise ValueError(f'Missing requirements file: {path}')
    seen.add(path)
    result = []
    for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        line = re.split(r'\s+#', line.strip(), 1)[0].strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith(('-r ', '--requirement ')):
            result.extend(requirements(path.parent / line.split(None, 1)[1], folder, seen))
            continue
        match = re.fullmatch(r'([A-Za-z0-9][A-Za-z0-9_.-]*)\s*(.*)', line)
        if not match or any(token in match[2] for token in ('@', ';', '[', ']')):
            raise ValueError(f'{path.name}:{number}: unsupported offline requirement: {line}')
        name, spec = match.groups()
        if spec and not re.fullmatch(r'(?:===|~=|>=|<=|==|!=|>|<)\s*\d[\w.*+!-]*(?:\s*,\s*(?:===|~=|>=|<=|==|!=|>|<)\s*\d[\w.*+!-]*)*', spec):
            raise ValueError(f'{path.name}:{number}: unsupported constraint: {spec}')
        result.append({'name': name, 'constraint': spec.strip(), 'requirement': line})
    seen.remove(path)
    return result


def check_skill_dependencies(folder):
    folder = folder.resolve()
    report = {'skill': str(folder), 'imports': [], 'requirements': [], 'issues': [], 'unresolved_dynamic_imports': [],
              'scope': 'all shipped .py files; AST/local filesystem only; no installed packages or model execution'}
    if not (folder / 'SKILL.md').is_file():
        report['issues'].append('Missing SKILL.md')
        report['status'] = 'FAIL'
        return report
    identity = skill_id(folder)
    try:
        if (folder / 'requirements.txt').is_file():
            report['requirements'] = requirements(folder / 'requirements.txt', folder)
    except ValueError as exc:
        report['issues'].append(str(exc))
    declared = {normalize(item['name']) for item in report['requirements']}
    stdlib = set(sys.stdlib_module_names) | set(sys.builtin_module_names)
    for file in sorted(folder.rglob('*.py')):
        if file.is_symlink() or not file.resolve().is_relative_to(folder):
            report['issues'].append('Nonportable Python source: ' + str(file.relative_to(folder)))
            continue
        try:
            tree = ast.parse(file.read_text(encoding='utf-8-sig'), filename=str(file))
        except (SyntaxError, UnicodeError) as exc:
            report['issues'].append(f'{file.relative_to(folder)}: {exc}')
            continue
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        importlib_aliases = {item.asname or item.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                             for item in node.names if item.name == 'importlib'}
        loader_aliases = {item.asname or item.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module == 'importlib'
                          for item in node.names if item.name == 'import_module'}
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    # Python relative import semantics start at the owning package.
                    base = file.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    target = base.joinpath(*(node.module or '').split('.')) if node.module else base
                    if not target.resolve().is_relative_to(folder) or not (target.is_dir() or target.with_suffix('.py').is_file()):
                        report['issues'].append(f'{file.relative_to(folder)}:{node.lineno}: missing/outside relative module {node.module}')
                    continue
                names = [node.module] if node.module else []
            elif isinstance(node, ast.Call):
                dynamic = isinstance(node.func, ast.Name) and node.func.id in {'__import__', *loader_aliases}
                dynamic |= isinstance(node.func, ast.Attribute) and node.func.attr == 'import_module' and isinstance(node.func.value, ast.Name) and node.func.value.id in importlib_aliases
                if dynamic:
                    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        names = [node.args[0].value]
                    else:
                        report['unresolved_dynamic_imports'].append(f'{file.relative_to(folder)}:{node.lineno}')
            for module in names:
                top = module.split('.')[0]
                roots = [file.parent, folder, folder / 'scripts', folder / 'examples']
                local = any((base / (top + '.py')).is_file() or ((base / top).is_dir() and any((base / top).rglob('*.py'))) for base in roots)
                distribution = MODULE_DISTRIBUTIONS.get(top, top)
                current, lazy = node, False
                while current in parents:
                    current = parents[current]
                    lazy |= isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
                kind = 'stdlib' if top in stdlib else ('local' if local else 'third_party')
                optional = OPTIONAL.get(identity, {}).get(top)
                entry = {'file': file.relative_to(folder).as_posix(), 'line': node.lineno, 'module': module,
                         'kind': kind, 'lazy': lazy, 'optional_capability': optional,
                         'distribution': distribution if kind == 'third_party' else None}
                report['imports'].append(entry)
                if kind == 'third_party' and normalize(distribution) not in declared:
                    report['issues'].append(f'{entry["file"]}:{node.lineno}: undeclared import {module} (distribution {distribution})')
    report['status'] = 'FAIL' if report['issues'] else ('NOT_TESTED' if report['unresolved_dynamic_imports'] else 'PASS')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-root', type=Path)
    parser.add_argument('--skill', type=Path, action='append', default=[])
    args = parser.parse_args()
    folders = [*args.skill, *(skill_folders(args.skills_root) if args.skills_root else [])]
    if not folders:
        parser.error('Choose a Skill directory or collection with SKILL.md files')
    reports = [check_skill_dependencies(p) for p in folders]
    state = 'FAIL' if any(r['status'] == 'FAIL' for r in reports) else ('NOT_TESTED' if any(r['status'] == 'NOT_TESTED' for r in reports) else 'PASS')
    print(json.dumps({'dependency_declaration_check': state, 'skills': reports}, ensure_ascii=False, indent=2))
    return int(state != 'PASS')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    raise SystemExit(main())
