"""Checkpoint checks must catch stale artifacts and unearned completion."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/runtime_contract'
spec = importlib.util.spec_from_file_location('checkpoint', SOURCE / 'check_task_state.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        (self.folder / 'input.csv').write_text('cycle,capacity\n1,120\n')
        (self.folder / 'figure.svg').write_text('<svg/>')
        (self.folder / 'review.txt').write_text('Fixture review; not a real visual check.')
        self.state = json.loads((SOURCE / 'TASK_STATE.json').read_text())
        self.state.update(task_id='test', objective='Test resume', skill_id='voltpeer-plot', updated_at='2026-09-27T12:00:00Z')
        for role, path in [('inputs', 'input.csv'), ('outputs', 'figure.svg')]:
            self.state[role] = [{'path': path, 'sha256': hashlib.sha256((self.folder / path).read_bytes()).hexdigest()}]
        self.state['checks'] = [{'name':'fixture', 'status':'pass', 'evidence_path':'review.txt'}]

    def test_resumable_and_complete(self):
        self.assertEqual(module.validate(self.state, self.folder), [])
        self.state['status'] = 'complete'
        self.assertEqual(module.validate(self.state, self.folder), [])

    def test_changed_input_requires_recheck(self):
        (self.folder / 'input.csv').write_text('changed')
        self.assertTrue(any('hash mismatch' in p for p in module.validate(self.state, self.folder)))

    def test_edited_or_missing_output(self):
        (self.folder / 'figure.svg').write_text('author edit')
        self.assertTrue(module.validate(self.state, self.folder))
        (self.folder / 'figure.svg').unlink()
        self.assertTrue(any('file missing' in p for p in module.validate(self.state, self.folder)))

    def test_incomplete_science_cannot_be_complete(self):
        for field, value in [('pending_questions',['Which reference cycle?']), ('checks',[{'name':'visual','status':'pending'}]), ('outputs',[])]:
            item = copy.deepcopy(self.state); item.update(status='complete'); item[field] = value
            self.assertTrue(module.validate(item, self.folder), field)

    def test_claimed_pass_requires_evidence(self):
        self.state['checks'][0]['evidence_path'] = 'missing.txt'
        self.assertTrue(module.validate(self.state, self.folder))

    def test_all_skill_packages_are_self_contained(self):
        for folder in (ROOT / 'skills').iterdir():
            if not (folder / 'SKILL.md').is_file(): continue
            for source, target in [('EXECUTION.md','references/EXECUTION.md'), ('TASK_STATE.json','assets/templates/TASK_STATE.json'), ('check_task_state.py','scripts/check_task_state.py')]:
                self.assertEqual((SOURCE / source).read_bytes(), (folder / target).read_bytes())


if __name__ == '__main__': unittest.main()
