"""Maintain one execution contract and ship it self-contained in each skill."""
from pathlib import Path
import shutil
import re
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/runtime_contract'
PARAGRAPH = '''<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Show the result, its file link and material unresolved questions; keep logs and recovery records inside the project's `.voltpeer/` folder. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->'''


def main():
    version = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8-sig'))['version']
    for folder in sorted((ROOT / 'skills').iterdir()):
        skill = folder / 'SKILL.md'
        if not skill.is_file():
            continue
        for origin, target in [('EXECUTION.md', 'references/EXECUTION.md'), ('TASK_STATE.json', 'assets/templates/TASK_STATE.json'), ('check_task_state.py', 'scripts/check_task_state.py')]:
            path = folder / target
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / origin, path)
        content = skill.read_text(encoding='utf-8-sig')
        if '<!-- execution-contract -->' in content:
            content = re.sub(r'<!-- execution-contract -->.*?<!-- /execution-contract -->', PARAGRAPH, content, flags=re.S)
        else:
            close = content.index('\n---', 4)
            heading_end = content.index('\n', content.index('\n# ', close) + 1)
            content = content[:heading_end] + '\n\n' + PARAGRAPH + content[heading_end:]
        skill.write_text(content, encoding='utf-8')
        release_path = folder / 'assets/SKILL_RELEASE.json'
        release_path.write_text(json.dumps({'schema_version': 1, 'skill_id': folder.name, 'version': version}, indent=2) + '\n', encoding='utf-8')
        if folder.name in {'battery-review-figure', 'battery-figure-assemble'}:
            for name in ('output_safety.py', 'delivery_contract.py', 'share_bundle.py', 'cli_runtime.py'):
                if (SOURCE / name).is_file():
                    shutil.copyfile(SOURCE / name, folder / 'scripts' / name)
    print('15 self-contained execution contracts synchronized.')


if __name__ == '__main__':
    main()
