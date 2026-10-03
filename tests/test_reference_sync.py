"""Repeated command occurrences must not grow installed-owner prefixes."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import sync_standalone_references as sync


class ReferenceSyncTests(unittest.TestCase):
    def test_repeated_commands_and_second_sync_are_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = root / 'skills'
            owner = skills / 'battery-owner'
            recipient = skills / 'battery-recipient'
            (owner / 'scripts').mkdir(parents=True)
            (owner / 'references').mkdir()
            (recipient / 'references').mkdir(parents=True)
            (owner / 'scripts/run.py').write_text('print("example")\n', encoding='utf-8')
            (owner / 'references/GUIDE.md').write_text(
                '# Guide\n\n```sh\npython scripts/run.py inspect\npython scripts/run.py plot\n'
                'python scripts/run.py export\n```\n', encoding='utf-8')
            (recipient / 'SKILL.md').write_text('[Guide](../battery-owner/references/GUIDE.md)\n', encoding='utf-8')
            target = recipient / 'references/shared/battery-owner/references/GUIDE.md'
            with patch.object(sync, 'ROOT', root), patch.object(sync, 'SKILLS', skills):
                sync.sync_skill(recipient)
                first = target.read_bytes()
                self.assertEqual(first.count(b'python <installed-battery-owner>/scripts/run.py'), 3)
                self.assertNotIn(b'<installed-battery-owner>/<installed-battery-owner>', first)
                before = {p.relative_to(recipient).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in recipient.rglob('*') if p.is_file()}
                sync.sync_skill(recipient)
                after = {p.relative_to(recipient).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in recipient.rglob('*') if p.is_file()}
                self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
