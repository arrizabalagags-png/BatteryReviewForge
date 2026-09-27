"""Validate the published ZIPs without rewriting released scientific assets."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
version=json.loads((ROOT/'.codex-plugin/plugin.json').read_text())['version']
assert json.loads((ROOT/'plugin.json').read_text())['version']==version
files=sorted((ROOT/'docs/downloads').glob(f'*-v{version}.zip'))
assert len(files)==3, 'Expected main, WorkBuddy full and WorkBuddy starter packages'
mapping=json.loads((ROOT/'docs/SKILL_NAMES.json').read_text(encoding='utf-8'))['skills']
assert {x['id'] for x in mapping}=={p.name for p in (ROOT/'skills').iterdir() if (p/'SKILL.md').is_file()}
report=[]
for path in files:
    with ZipFile(path) as archive:
        assert archive.testzip() is None, path.name
        names=archive.namelist()
        assert not any(n.startswith(('source/','dist/','.git/')) or n.endswith(('i18n.js','author-wechat.jpg')) for n in names)
        if path.name==f'BatteryReviewForge-v{version}.zip':
            assert len([n for n in names if n.startswith('skills/') and n.endswith('/SKILL.md')])==15
            plugin=json.loads(archive.read('.codex-plugin/plugin.json'))
            assert plugin['version']==version
            for item in mapping:
                metadata=archive.read(f"skills/{item['id']}/agents/openai.yaml").decode('utf-8')
                assert item['display_name'] in metadata
                skill=archive.read(f"skills/{item['id']}/SKILL.md").decode('utf-8-sig')
                assert ('name: '+item['id']) in skill or ('name: "'+item['id']+'"') in skill
            assert json.loads(archive.read('docs/SKILL_NAMES.json'))['skills']==mapping
    report.append({'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(ROOT/'outputs').mkdir(exist_ok=True)
(ROOT/'outputs/version-consistency.json').write_text(json.dumps({'version':version,'archives':report},indent=2)+'\n')
(ROOT/'outputs/distribution-sha256.txt').write_text(''.join(f"{r['sha256']}  {r['file']}\n" for r in report))
print(json.dumps({'version':version,'checked_archives':len(report),'result':'passed'}))
