"""Read-only checkpoint validation. Never executes commands from a record.

File entries: {path, sha256}. Check entries: {name, status, evidence_path}.
Relative paths are resolved against the checkpoint's directory.
"""
import argparse
import hashlib
import json
from pathlib import Path


def validate(record, folder):
    problems = []
    if not isinstance(record, dict):
        return ['Checkpoint must be an object.']
    if record.get('schema_version') != 1:
        problems.append('Unsupported schema_version.')
    for key in ('task_id', 'objective', 'skill_id', 'updated_at'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            problems.append('Missing text: ' + key)
    if record.get('mode') not in ('guided', 'adaptive', 'review'):
        problems.append('Unknown execution mode.')
    if record.get('status') not in ('in_progress', 'needs_input', 'complete'):
        problems.append('Unknown status.')
    for key in ('user_choices', 'scientific_context'):
        if not isinstance(record.get(key), dict):
            problems.append(key + ' must be an object.')
    for key in ('inputs', 'outputs', 'completed_steps', 'checks', 'pending_questions'):
        if not isinstance(record.get(key), list):
            problems.append(key + ' must be an array.')
    if problems:
        return problems
    for role in ('inputs', 'outputs'):
        for i, item in enumerate(record[role]):
            if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not item['path']:
                problems.append(f'{role}[{i}]: missing path.'); continue
            path = (folder / item['path']).resolve()
            if not path.is_file():
                problems.append(f'{role}[{i}]: file missing.'); continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if item.get('sha256') != digest:
                problems.append(f'{role}[{i}]: hash mismatch or missing; recheck changed file.')
    for i, check in enumerate(record['checks']):
        if not isinstance(check, dict) or not check.get('name') or check.get('status') not in ('pass', 'fail', 'pending'):
            problems.append(f'checks[{i}]: requires name and pass/fail/pending.'); continue
        if check['status'] == 'pass':
            evidence = check.get('evidence_path')
            if not isinstance(evidence, str) or not evidence or not (folder / evidence).is_file():
                problems.append(f'checks[{i}]: a pass requires an existing evidence file.')
    if record['status'] == 'complete':
        if record['pending_questions']:
            problems.append('Complete task still has pending questions.')
        if not record['outputs'] or not record['checks']:
            problems.append('Complete task needs outputs and recorded checks.')
        if any(not isinstance(c, dict) or c.get('status') != 'pass' for c in record['checks']):
            problems.append('Complete task still has failed or pending checks.')
    elif not isinstance(record.get('next_action'), str) or not record['next_action'].strip():
        problems.append('Unfinished task needs a concrete next_action.')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.checkpoint.read_text(encoding='utf-8-sig'))
        problems = validate(record, args.checkpoint.resolve().parent)
    except (OSError, ValueError) as error:
        problems = [str(error)]
    print(json.dumps({'structural_check': 'failed' if problems else 'passed', 'problems': problems,
                      'scientific_and_visual_review': 'not_performed_by_this_validator'}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(problems))


if __name__ == '__main__':
    main()
