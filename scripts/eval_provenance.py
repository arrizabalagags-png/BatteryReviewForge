"""Freeze complete installed Skill trees and source/environment identity for EVALs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import platform
import re
import struct
import subprocess


def tree_manifest(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Missing installed Skill tree to freeze')
    rows = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('Skill provenance cannot follow links outside the frozen tree')
        rows.append({'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
    if not rows:
        raise ValueError('Cannot freeze an empty Skill tree')
    encoded = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return {'sha256': hashlib.sha256(encoded).hexdigest(), 'files': rows}


def environment():
    return {'os': platform.system(), 'os_release': platform.release(),
            'architecture': platform.machine(), 'pointer_bits': struct.calcsize('P') * 8,
            'python': platform.python_version()}


def source_provenance(root):
    """Use this repository only, never an unrelated ancestor Git checkout."""
    root = Path(root).resolve()
    def git(*arguments):
        return subprocess.run(['git', '-C', str(root), *arguments], capture_output=True)
    try:
        top = git('rev-parse', '--show-toplevel')
        if top.returncode == 0 and Path(top.stdout.decode('utf-8').strip()).resolve() == root:
            commit = git('rev-parse', 'HEAD').stdout.decode('ascii').strip()
            if not re.fullmatch(r'[0-9a-f]{40}', commit):
                raise ValueError('Cannot freeze a valid source commit')
            status = git('status', '--porcelain').stdout
            diff = git('diff', '--binary', 'HEAD').stdout
            return {'source_commit': commit, 'source_worktree_dirty': bool(status),
                    'source_tracked_diff_sha256': hashlib.sha256(diff).hexdigest(),
                    'source_identity_origin': 'actual_repository_HEAD_and_worktree'}
    except OSError:
        pass
    manifest = root / '.codex-plugin/plugin.json'
    package_version = json.loads(manifest.read_text(encoding='utf-8-sig')).get('version') if manifest.is_file() else None
    versioned = root / f'docs/SOURCE_PROVENANCE_v{package_version}.json'
    source = versioned if versioned.is_file() else root / 'docs/SOURCE_PROVENANCE.json'
    if not source.is_file():
        raise ValueError('Unpacked source needs docs/SOURCE_PROVENANCE.json; unknown source commit cannot be invented')
    result = json.loads(source.read_text(encoding='utf-8-sig'))
    if not re.fullmatch(r'[0-9a-f]{40}', result.get('source_commit', '')):
        raise ValueError('Packaged source commit is missing or invalid')
    return {key: result[key] for key in ('source_commit', 'source_worktree_dirty', 'source_tracked_diff_sha256')} | {'source_identity_origin': 'packaged_source_provenance; commit plus recorded worktree state'}


def freeze(root, installed_skill_root):
    installed = tree_manifest(installed_skill_root)
    canonical = tree_manifest(Path(root) / 'skills')
    return {**source_provenance(root), 'skill_tree_sha256': installed['sha256'],
            'skill_tree_files': installed['files'], 'source_skill_tree_sha256': canonical['sha256'],
            'preparation_environment': environment()}


def validate_frozen(run, installed_skill_root=None):
    """Version 1 is historical; every newly prepared/recorded trial needs version 2."""
    issues = []
    if run.get('schema_version', 1) < 2:
        return ['Historical version 1 lacks complete provenance; preserve it, then prepare a new version 2 trial']
    if not re.fullmatch(r'[0-9a-f]{40}', run.get('source_commit', '')):
        issues.append('Missing source commit')
    if type(run.get('source_worktree_dirty')) is not bool or not re.fullmatch(r'[0-9a-f]{64}', run.get('source_tracked_diff_sha256', '')):
        issues.append('Missing source worktree identity')
    for key in ('skill_tree_sha256', 'source_skill_tree_sha256'):
        if not re.fullmatch(r'[0-9a-f]{64}', run.get(key, '')):
            issues.append('Missing ' + key)
    rows = run.get('skill_tree_files')
    if not isinstance(rows, list) or not rows:
        issues.append('Missing full Skill file manifest')
    else:
        encoded = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
        if hashlib.sha256(encoded).hexdigest() != run.get('skill_tree_sha256'):
            issues.append('Full Skill file manifest hash changed')
    prepared = run.get('preparation_environment', {})
    if not prepared.get('os') or not prepared.get('architecture'):
        issues.append('Missing preparation OS/architecture')
    if installed_skill_root is not None and tree_manifest(installed_skill_root)['sha256'] != run.get('skill_tree_sha256'):
        issues.append('Installed Skill tree changed after preparation; start a new trial')
    return issues
