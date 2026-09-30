"""EVAL fixture/provenance engineering checks; no model calls or semantic grading."""
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from eval_provenance import tree_manifest, validate_frozen
from prepare_recipe_comparison import prepare as prepare_comparison
from workflow_eval import prepare, record, suite, validate_cases


class EvalProvenanceTests(unittest.TestCase):
    def test_preserved_65_plus_four_actual_opposite_evidence_cases(self):
        base = json.loads((ROOT / 'evals/workflow_cases.json').read_text(encoding='utf-8-sig'))
        combined = suite()
        self.assertEqual(len(base['cases']), 65)
        self.assertEqual(combined['cases'][:65], base['cases'])
        self.assertEqual(len(combined['cases']), 69)
        self.assertEqual(validate_cases(combined), [])
        conflicts = combined['cases'][65:]
        self.assertEqual({case['skill_id'] for case in conflicts}, {'battery-claim-check', 'battery-metrics-audit', 'battery-review-audit', 'battery-reviewer'})
        self.assertTrue(all(case['case_class'] == 'evidence_conflict' for case in conflicts))
        with (ROOT / 'evals/fixtures/opposing_retention.csv').open(encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 24)
        effects = {}
        for source in ('S_POS', 'S_NEG'):
            averages = {}
            for group in ('no_Q', 'Q_1wtpercent'):
                values = [float(row['retention_percent']) for row in rows if row['source_id'] == source and row['group'] == group]
                self.assertEqual(len(values), 6)
                averages[group] = statistics.mean(values)
            effects[source] = averages['Q_1wtpercent'] - averages['no_Q']
        self.assertEqual(effects, {'S_POS': 12, 'S_NEG': -7})
        self.assertTrue(all(row['baseline_cycle'] == '1' and row['cycle'] == '100' for row in rows))
        text = (ROOT / 'evals/fixtures/opposing_sources.md').read_text(encoding='utf-8')
        self.assertIn('NR（not reported after checking', text)
        self.assertIn('NV（not yet verified）', text)

    def test_prepare_freezes_all_skill_files_without_exposing_expected(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = prepare('battery-claim-check-evidence-conflict', Path(temp) / 'run')
            run = json.loads((workspace / 'EVAL_RUN.json').read_text(encoding='utf-8'))
            self.assertEqual(run['execution_status'], 'NOT_RUN')
            self.assertEqual(run['schema_version'], 2)
            self.assertEqual(validate_frozen(run, workspace / '.dsh/skills'), [])
            self.assertGreater(len(run['skill_tree_files']), 1)
            self.assertTrue(run['preparation_environment']['os'])
            self.assertTrue(run['preparation_environment']['architecture'])
            self.assertEqual(len(run['source_commit']), 40)
            self.assertEqual(len(run['case_sha256']), 64)
            self.assertNotIn('expected', (workspace / 'TASK.md').read_text(encoding='utf-8'))
            self.assertFalse((workspace / 'evidence_conflict_cases.json').exists())
            self.assertEqual(len(list((workspace / 'input').iterdir())), 3)
            changed = workspace / '.dsh/skills' / next(row['path'] for row in run['skill_tree_files'] if not row['path'].endswith('SKILL.md'))
            changed.write_bytes(changed.read_bytes() + b'\nEngineering hash drift\n')
            self.assertTrue(any('changed' in value for value in validate_frozen(run, workspace / '.dsh/skills')))

    def test_resume_run_input_hashes_match_current_files_while_old_checkpoint_is_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = prepare('battery-claim-check-resume', Path(temp) / 'run')
            run = json.loads((workspace / 'EVAL_RUN.json').read_text(encoding='utf-8'))
            for row in run['input_files']:
                self.assertEqual(row['sha256'], hashlib.sha256((workspace / row['path']).read_bytes()).hexdigest())
            old = json.loads((workspace / 'old-working/.voltpeer/TASK_STATE.json').read_text(encoding='utf-8'))
            self.assertNotEqual(old['inputs'][0]['sha256'], run['input_files'][0]['sha256'])

    def test_new_record_requires_actual_os_architecture_and_unchanged_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = prepare('battery-claim-check-evidence-conflict', root / 'run')
            (workspace / 'transcript.md').write_text('Engineering record-structure fixture only; no model invocation.\n', encoding='utf-8')
            case = next(case for case in suite()['cases'] if case['id'] == 'battery-claim-check-evidence-conflict')
            review = {'case_id': case['id'], 'host': 'Engineering fixture', 'host_version': 'test-only', 'model_id': 'NOT_RUN', 'reviewer': 'test harness',
                      'observations': [{'criterion': index, 'status': 'pending', 'evidence_file': 'transcript.md', 'evidence_anchor': 'L1', 'note': 'No model execution; structure test only'} for index in range(len(case['expected']))]}
            review_path = root / 'review.json'
            review_path.write_text(json.dumps(review), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'actual execution OS'):
                record(workspace, review_path, root / 'invalid')
            review['execution_environment'] = {'os': 'test-fixture-OS', 'architecture': 'test-fixture-arch'}
            review_path.write_text(json.dumps(review), encoding='utf-8')
            output = record(workspace, review_path, root / 'record')
            result = json.loads((output / 'record.json').read_text(encoding='utf-8'))
            self.assertEqual(result['schema_version'], 2)
            self.assertEqual(result['judgment'], 'pending')
            self.assertEqual(result['run']['execution_status'], 'NOT_RUN')
            changed_suite = suite()
            next(case for case in changed_suite['cases'] if case['id'] == review['case_id'])['expected'][0] += ' Changed after preparation.'
            with patch('workflow_eval.suite', return_value=changed_suite), self.assertRaisesRegex(ValueError, 'expected criteria changed'):
                record(workspace, review_path, root / 'changed-expected')
            skill_file = workspace / '.dsh/skills/battery-claim-check/SKILL.md'
            skill_file.write_bytes(skill_file.read_bytes() + b'\nchanged\n')
            with self.assertRaisesRegex(ValueError, 'changed'):
                record(workspace, review_path, root / 'changed-record')

    def test_abc_records_freeze_identical_skill_tree_and_environment(self):
        with tempfile.TemporaryDirectory() as temp:
            output = prepare_comparison('li_li', 'new_shape', Path(temp) / 'comparison', 'Engineering fixture', 'test-only', 'NOT_RUN')
            runs = [json.loads((output / arm / 'RUN_RECORD.json').read_text(encoding='utf-8')) for arm in ('A', 'B', 'C')]
            self.assertEqual(len({run['skill_tree_sha256'] for run in runs}), 1)
            self.assertEqual(len({run['source_commit'] for run in runs}), 1)
            for arm, run in zip(('A', 'B', 'C'), runs):
                self.assertEqual(run['schema_version'], 2)
                self.assertEqual(run['run_state'], 'NOT_RUN')
                self.assertEqual(validate_frozen(run, output / arm / '.dsh/skills'), [])
                self.assertEqual(run['execution_environment'], {'os': None, 'architecture': None})
                self.assertTrue(run['preparation_environment']['architecture'])


if __name__ == '__main__':
    unittest.main()
