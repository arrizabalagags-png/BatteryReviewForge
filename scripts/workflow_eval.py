"""Prepare isolated task folders and freeze recorded EVAL evidence; never infer model PASS."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from eval_provenance import freeze, validate_frozen

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def case_digest(case):
    return hashlib.sha256(json.dumps(case, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def suite():
    base = json.loads((ROOT / 'evals/workflow_cases.json').read_text(encoding='utf-8-sig'))
    extension = json.loads((ROOT / 'evals/evidence_conflict_cases.json').read_text(encoding='utf-8-sig'))
    return {**base, 'suite_id': 'voltpeer-workflow-69-v2', 'base_suite_id': base['suite_id'],
            'extension_suite_id': extension['suite_id'], 'cases': [*base['cases'], *extension['cases']]}


def validate_cases(data):
    issues, ids = [], set()
    groups, conflict_skills = {}, set()
    for case in data.get('cases', []):
        key = case.get('id')
        if not key or key in ids:
            issues.append('Missing or duplicate case ID: ' + str(key))
        ids.add(key)
        if case.get('case_class') == 'evidence_conflict':
            conflict_skills.add(case.get('skill_id'))
        else:
            groups.setdefault(case.get('skill_id'), set()).add(case.get('case_class'))
        if not case.get('prompt') or len(case.get('expected', [])) < 3 or not case.get('synthetic'):
            issues.append('Incomplete case: ' + str(key))
        for value in case.get('input_files', []):
            path = (ROOT / value).resolve()
            if not path.is_relative_to(ROOT / 'evals/fixtures') or not path.is_file():
                issues.append('Missing/outside fixture: ' + str(value))
    kinds = {'normal', 'missing', 'conflict', 'fabrication', 'resume'}
    base_count = sum(case.get('case_class') != 'evidence_conflict' for case in data.get('cases', []))
    if len(groups) != 13 or any(values != kinds for values in groups.values()) or base_count != 65:
        issues.append('Base suite must preserve 13 skills, each with all five classes, exactly 65 unique cases')
    expected_conflicts = {'voltpeer-claim-check', 'voltpeer-metrics', 'voltpeer-review-audit', 'voltpeer-reviewer'}
    if conflict_skills != expected_conflicts or len(ids) != 69:
        issues.append('Extension must add exactly four evidence-conflict cases for claim/metrics/audit/reviewer; 69 total')
    return issues


def prepare(case_id, output):
    data = suite()
    problems = validate_cases(data)
    if problems:
        raise ValueError('; '.join(problems))
    matches = [case for case in data['cases'] if case['id'] == case_id]
    if len(matches) != 1:
        raise ValueError('Unknown case: ' + case_id)
    case = matches[0]
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    # DSH discovers the nearest ancestor .git as project root. A prepared run
    # below this repository must be its own real root, without commits/remotes.
    init = subprocess.run(['git', 'init', '--quiet', str(output)], capture_output=True, text=True, encoding='utf-8')
    if init.returncode:
        raise ValueError('Cannot anchor isolated EVAL workspace: ' + init.stderr.strip())
    skill_root = output / '.dsh/skills' / case['skill_id']
    shutil.copytree(ROOT / 'skills' / case['skill_id'], skill_root, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    paths = []
    for value in case['input_files']:
        original = ROOT / value
        destination = output / 'input' / original.name
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(original, destination)
        paths.append({'path': destination.relative_to(output).as_posix(), 'sha256': digest(destination)})
    if case['case_class'] == 'resume':
        state_folder = output / 'old-working/.voltpeer'
        state_folder.mkdir(parents=True)
        old_result = output / 'old-working/旧结果.md'
        old_result.write_text('Author edited this existing result; keep it.\n', encoding='utf-8')
        checkpoint = json.loads((ROOT / 'scripts/runtime_contract/TASK_STATE.json').read_text(encoding='utf-8-sig'))
        first = output / paths[0]['path']
        before = first.read_text(encoding='utf-8-sig')
        checkpoint.update({'task_id':case_id, 'skill_id':case['skill_id'], 'objective':case['prompt'],
            'updated_at':datetime.now(timezone.utc).isoformat(), 'status':'in_progress', 'mode':'guided',
            'inputs':[{'path':'../../' + paths[0]['path'], 'sha256':digest(first)}],
            'outputs':[{'path':'../旧结果.md', 'sha256':digest(old_result)}],
            'user_choices':{'language':'中文','width_mm':89,'style':'journal','denominator':'cathode active mass'},
            'scientific_context':{'source_id':'S1','third_cycle_capacity':116},
            'checks':[{'name':'old source read','status':'pass','evidence_path':'../../' + paths[0]['path']}],
            'pending_questions':[], 'completed_steps':['Earlier source inspected'], 'next_action':'Verify input hashes before continuation'})
        (state_folder / 'TASK_STATE.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')
        # A real changed input makes old checks invalid; no fabricated model result.
        first.write_text(before.replace('116','110'),encoding='utf-8')
        for value in paths[1:]:
            path = output / value['path']
            if path.suffix == '.csv':
                path.write_text(path.read_text(encoding='utf-8-sig').replace('3,116','3,110'),encoding='utf-8')
        old_result.write_text(old_result.read_text(encoding='utf-8')+'Additional author edit after checkpoint.\n',encoding='utf-8')
    request = case['prompt'] + '\n\n输入文件：\n' + '\n'.join(item['path'] for item in paths)
    if case['case_class'] == 'resume':
        request += '\n恢复状态：old-working/.voltpeer/TASK_STATE.json\n'
    paths = [{'path': item['path'], 'sha256': digest(output / item['path'])} for item in paths]
    (output / 'TASK.md').write_text(request + '\n', encoding='utf-8')
    (output / 'EVAL_RUN.json').write_text(json.dumps({'schema_version':2,'suite_id':data['suite_id'],'case_id':case_id,'case_sha256':case_digest(case),'input_files':paths,
        'prepared_at':datetime.now(timezone.utc).isoformat(),'execution_status':'NOT_RUN','discovery_root':'local empty git repository; no commits/remotes','skill_sha256':digest(skill_root/'SKILL.md'),
        'skill_version':json.loads((ROOT/'plugin.json' if (ROOT/'plugin.json').is_file() else ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8-sig'))['version'],
        **freeze(ROOT,output/'.dsh/skills')},ensure_ascii=False,indent=2),encoding='utf-8')
    return output


def record(workspace, review_path, output):
    workspace = Path(workspace).resolve()
    run = json.loads((workspace / 'EVAL_RUN.json').read_text(encoding='utf-8-sig'))
    problems = validate_frozen(run, workspace / '.dsh/skills')
    if problems:
        raise ValueError('; '.join(problems))
    review = json.loads(Path(review_path).read_text(encoding='utf-8-sig'))
    case = next(case for case in suite()['cases'] if case['id'] == run['case_id'])
    if case_digest(case) != run.get('case_sha256'):
        raise ValueError('Frozen case/independent expected criteria changed; preserve the old trial and prepare a new one')
    if review.get('case_id') != run['case_id'] or not all(review.get(k) for k in ('host','host_version','model_id','reviewer')):
        raise ValueError('Provide matching case_id and actual host, host_version, model_id, reviewer')
    execution_environment = review.get('execution_environment', {})
    if not isinstance(execution_environment, dict) or not execution_environment.get('os') or not execution_environment.get('architecture'):
        raise ValueError('New records require the actual execution OS and architecture; do not copy preparation values without checking')
    observations = review.get('observations', [])
    if len(observations) != len(case['expected']) or {row.get('criterion') for row in observations} != set(range(len(case['expected']))):
        raise ValueError('Review must cover each expected criterion exactly once')
    evidence = {}
    for row in observations:
        path = (workspace / row.get('evidence_file', '')).resolve()
        if row.get('status') not in {'pass','fail','pending'} or not row.get('note') or not row.get('evidence_anchor') or not path.is_relative_to(workspace) or not path.is_file() or not path.stat().st_size:
            raise ValueError('Every judgment requires a local evidence file, concrete anchor and note')
        evidence[path] = digest(path)
    output = Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    for path in evidence:
        destination = output / path.relative_to(workspace)
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,destination)
    status = 'fail' if any(r['status']=='fail' for r in observations) else 'pending' if any(r['status']=='pending' for r in observations) else 'reviewer_reported_pass'
    record_data = {'schema_version':2,'run':run,'review':review,'judgment':status,'recorded_at':datetime.now(timezone.utc).isoformat(),
                   'evidence':[{ 'path':p.relative_to(workspace).as_posix(),'sha256':value} for p,value in evidence.items()],
                   'automation_scope':'Record structure and file hashes only; semantic judgment belongs to the named reviewer.'}
    (output/'record.json').write_text(json.dumps(record_data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('validate',help='Validate fixed case files; does not invoke a model')
    p=sub.add_parser('prepare');p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True)
    r=sub.add_parser('record');r.add_argument('--workspace',type=Path,required=True);r.add_argument('--review',type=Path,required=True);r.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=='validate':
            errors=validate_cases(suite());print(json.dumps({'fixture_integrity':'FAIL' if errors else 'PASS','errors':errors,'base_cases':65,'evidence_conflict_cases':4,'total_cases':69,'model_behavior':'NOT_RUN'},ensure_ascii=False));return int(bool(errors))
        path=prepare(args.case,args.out) if args.command=='prepare' else record(args.workspace,args.review,args.out)
        print(str(path));return 0
    except (ValueError,KeyError,OSError,StopIteration) as exc:
        parser.exit(2,str(exc)+'\n')


if __name__=='__main__':
    from runtime_contract.cli_runtime import configure_utf8
    configure_utf8()
    raise SystemExit(main())
