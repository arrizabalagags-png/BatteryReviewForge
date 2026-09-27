"""Isolated installer checks. Never writes to a user's actual skill directories."""
import os,shutil,subprocess,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASH=Path(os.environ.get('BRF_TEST_BASH') or shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe')
if os.name=='nt' and not os.environ.get('BRF_TEST_BASH'): BASH=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git/bin/bash.exe'
PWSH=Path(os.environ.get('BRF_TEST_PWSH') or shutil.which('pwsh') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'))
results=[]
for engine in ('sh','ps1'):
 for case in ('clean','unrelated_shared','same_shared','same_target','overwrite_backup_restore','empty','invalid','kimi','dsh'):
  with tempfile.TemporaryDirectory(prefix='brf installer ') as tmp:
   base=Path(tmp);pkg=base/'package with spaces';pkg.mkdir();home=base/'home with spaces';home.mkdir()
   shutil.copy2(ROOT/f'install.{engine}',pkg/f'install.{engine}')
   src=pkg/'skills';src.mkdir();id='battery-review-figure'
   if case!='empty':
    (src/id).mkdir();(src/id/'SKILL.md').write_text('new skill')
   if case=='invalid':(src/'battery-invalid').mkdir()
   host='kimi' if case=='kimi' else 'dsh' if case=='dsh' else 'codex'
   hosthome=home/('.kimi-code' if host=='kimi' else '.'+host);target=hosthome/'skills'
   if case in ('unrelated_shared','same_shared'):
    d=home/'.agents/skills'/('battery-unrelated-demo' if case=='unrelated_shared' else id);d.mkdir(parents=True);(d/'SKILL.md').write_text('old shared')
   if case in ('same_target','overwrite_backup_restore'):
    d=target/id;d.mkdir(parents=True);(d/'SKILL.md').write_text('old skill');(d/'sentinel.txt').write_text('preserve me')
   env=os.environ.copy();env.update(HOME=str(home),USERPROFILE=str(home),CODEX_HOME=str(home/'.codex'),KIMI_CODE_HOME=str(home/'.kimi-code'),DSH_HOME=str(home/'.dsh'))
   if engine=='sh':
    cmd=[str(BASH),'install.sh','--agent',host]+(['--overwrite'] if case=='overwrite_backup_restore' else [])
   else:
    cmd=[str(PWSH),'-NoProfile','-File','install.ps1','-Agent',{'codex':'Codex','kimi':'KimiCode','dsh':'DeepSeekHarness'}[host]]+(['-Overwrite'] if case=='overwrite_backup_restore' else [])
   run=subprocess.run(cmd,cwd=pkg,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
   success=case in ('clean','unrelated_shared','overwrite_backup_restore','kimi','dsh')
   assert (run.returncode==0)==success,(engine,case,run.stdout,run.stderr)
   if success:assert (target/id/'SKILL.md').read_text()=='new skill'
   elif case=='same_target':assert (target/id/'sentinel.txt').read_text()=='preserve me'
   else:assert not (target/id).exists(),(engine,case,'partial install')
   if case=='overwrite_backup_restore':
    backup=list((hosthome/'.brf-install-backups').glob('*/battery-review-figure'))
    assert len(backup)==1 and (backup[0]/'sentinel.txt').read_text()=='preserve me'
    # Move new installation aside and restore backup, entirely inside this fixture.
    (target/id).rename(base/'new aside');shutil.move(str(backup[0]),str(target/id));assert (target/id/'SKILL.md').read_text()=='old skill'
   results.append({'engine':engine,'case':case,'exit':run.returncode,'passed':True})
(ROOT/'outputs').mkdir(exist_ok=True)
(ROOT/'outputs/installer-regression.json').write_text(json.dumps({'platform':'Windows; Git Bash and PowerShell; isolated fixtures, not native client verification','results':results},indent=2))
print(f'{len(results)} installer cases passed')
