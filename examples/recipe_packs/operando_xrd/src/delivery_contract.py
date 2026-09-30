"""Create a result-first Working Bundle; private recovery files stay under .voltpeer."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import shutil
import sys

from output_safety import new_directory

FIGURE_SUFFIXES = {'.pdf', '.svg', '.png', '.tiff', '.tif'}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_working_bundle(files: list[Path], requested: Path, *, inputs: list[Path] = (),
                           skill_id: str, objective: str, specification: dict | None = None,
                           title: str = '图件结果') -> Path:
    files, inputs = [Path(p).resolve() for p in files], [Path(p).resolve() for p in inputs]
    if not files or any(not p.is_file() for p in files + inputs):
        raise ValueError('交付需要实际存在的结果文件和输入文件。')
    root, version = new_directory(requested.resolve())
    results, internal = root / 'results', root / '.voltpeer'
    results.mkdir()
    (internal / 'inputs').mkdir(parents=True)
    (internal / 'records').mkdir()
    entries, outputs = [], []
    for index, path in enumerate(files, 1):
        public = path.suffix.lower() in FIGURE_SUFFIXES and '.record.' not in path.name
        folder = results if public else internal / 'records'
        target = folder / path.name
        if target.exists():
            target = folder / f'{index:02d}_{path.name}'
        shutil.copy2(path, target)
        relative = target.relative_to(root).as_posix()
        entries.append({'path': relative, 'sha256': digest(target), 'role': 'result' if public else 'internal_record'})
        outputs.append({'path': '../' + relative, 'sha256': digest(target)})
    copied_inputs = []
    for index, path in enumerate(inputs, 1):
        target = internal / 'inputs' / f'{index:02d}_{path.name}'
        shutil.copy2(path, target)
        copied_inputs.append({'path': target.relative_to(internal).as_posix(), 'sha256': digest(target), 'original_path': str(path)})
    spec = specification or {'status': 'journal_neutral_preview', 'journal_requirements': 'needs_confirmation'}
    state = {'schema_version': 1, 'task_id': f'{skill_id}-{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")}',
             'objective': objective, 'skill_id': skill_id, 'mode': 'guided', 'status': 'needs_input',
             'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
             'user_choices': {'specification': spec, 'output_version': version, 'parent_version': version - 1 if version > 1 else None},
             'inputs': copied_inputs, 'outputs': outputs, 'scientific_context': {},
             'completed_steps': ['Result files created and retained without overwriting earlier versions.'],
             'checks': [{'name': 'result files saved', 'status': 'pass', 'evidence_path': outputs[0]['path']},
                        {'name': 'final scientific and visual review', 'status': 'pending'}],
             'pending_questions': ['请核对图里的单位、条件和最终尺寸下的可读性。'],
             'next_action': 'Open index.html, inspect the final figures and resolve remaining requirements.'}
    (internal / 'TASK_STATE.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (internal / 'manifest.json').write_text(json.dumps({'schema_version': 1, 'bundle_type': 'working', 'files': entries, 'inputs': copied_inputs,
            'specification': spec, 'generated_at': state['updated_at']}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    visible = [e for e in entries if e['role'] == 'result']
    rows = '\n'.join(f'- [{Path(e["path"]).name}]({e["path"]})' for e in visible)
    (root / 'README.md').write_text(f'# {title}\n\n打开 `index.html` 看图；可交付图件在 `results` 文件夹。\n\n{rows}\n\n投稿前核对数据、单位、测试条件及期刊最新要求。\n\n要继续修改，请把整个工作文件夹交给 AI；恢复记录保存在 `.voltpeer`。对外分享请先生成脱敏分享包。\n', encoding='utf-8')
    cards = ''.join(f'<li><a href="{html.escape(e["path"])}">{html.escape(Path(e["path"]).name)}</a></li>' for e in visible)
    previews = ''.join(f'<img src="{html.escape(e["path"])}" alt="结果预览">' for e in visible if Path(e['path']).suffix == '.png')
    (root / 'index.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>:root{{color-scheme:light dark}}body{{max-width:960px;margin:40px auto;padding:0 20px;font:16px/1.7 system-ui}}img{{max-width:100%;background:white}}a{{color:LinkText}}</style><h1>{html.escape(title)}</h1><p>打开下面的文件。投稿前请核对数据、单位和期刊要求。</p>{previews}<ul>{cards}</ul><details><summary>继续修改或分享</summary><p>继续修改时保留整个文件夹；公开分享请先生成脱敏分享包。</p></details></html>', encoding='utf-8')
    if sys.platform == 'win32':
        # Only the newly created internal directory is hidden from casual browsing.
        import ctypes
        attributes = ctypes.windll.kernel32.GetFileAttributesW(str(internal))
        if attributes != -1:
            ctypes.windll.kernel32.SetFileAttributesW(str(internal), attributes | 2)
    return root


def check_working_bundle(root: Path) -> list[str]:
    problems = []
    try:
        manifest = json.loads((root / '.voltpeer/manifest.json').read_text(encoding='utf-8-sig'))
        for item in manifest['files']:
            path = (root / item['path']).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file() or digest(path) != item['sha256']:
                problems.append('结果文件缺失或已修改：' + item['path'])
        for item in manifest.get('inputs', []):
            path = (root / '.voltpeer' / item['path']).resolve()
            if not path.is_relative_to((root / '.voltpeer/inputs').resolve()) or not path.is_file() or digest(path) != item['sha256']:
                problems.append('输入文件缺失或已修改：' + item['path'])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(str(exc))
    return problems
