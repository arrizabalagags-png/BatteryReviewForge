"""Maintain one execution contract and ship it self-contained in each skill."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/runtime_contract'
PARAGRAPH = '''<!-- execution-contract -->
For multi-step work or resuming after interruption, use [the execution and recovery guide](references/EXECUTION.md). Save verified inputs, user choices, pending conditions, outputs and the next action in the project's `TASK_STATE.json`; check file hashes before resuming. Start with guided execution when tool/vision capabilities are unverified; allow adaptive planning after a successful pilot. All modes retain the same scientific and output checks. For a one-step edit, keep the existing record and proceed directly.
<!-- /execution-contract -->'''


def main():
    for folder in sorted((ROOT / 'skills').iterdir()):
        skill = folder / 'SKILL.md'
        if not skill.is_file():
            continue
        for origin, target in [('EXECUTION.md', 'references/EXECUTION.md'), ('TASK_STATE.json', 'assets/templates/TASK_STATE.json'), ('check_task_state.py', 'scripts/check_task_state.py')]:
            path = folder / target
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / origin, path)
        content = skill.read_text(encoding='utf-8-sig')
        if '<!-- execution-contract -->' not in content:
            close = content.index('\n---', 4)
            heading_end = content.index('\n', content.index('\n# ', close) + 1)
            content = content[:heading_end] + '\n\n' + PARAGRAPH + content[heading_end:]
        skill.write_text(content, encoding='utf-8')
    print('15 self-contained execution contracts synchronized.')


if __name__ == '__main__':
    main()
