"""Actual isolated legacy installation transactions; no user discovery roots."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]
MAPPING=json.loads((ROOT/'docs/SKILL_MIGRATION.json').read_text(encoding='utf-8'))
PAIRS={row['legacy_id']:row['canonical_id'] for row in MAPPING['aliases']}
SHELLS={'ps1':shutil.which('pwsh') or shutil.which('powershell'),
        'sh':str(Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git/bin/bash.exe') if os.name=='nt' else shutil.which('sh')}
RESULTS=[]

def snapshot(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}


class NamingMigrationTests(unittest.TestCase):
    def trial(self,engine,case):
        requested_case=case
        case=case.removesuffix('_crlf')
        if not SHELLS[engine] or not Path(SHELLS[engine]).is_file():self.skipTest(engine+' unavailable')
        with tempfile.TemporaryDirectory(prefix='VoltPeer 迁移 空格 ') as tmp:
            base=Path(tmp);pkg=base/'package';pkg.mkdir();home=base/'home';home.mkdir()
            workspace=base/'研究项目';workspace.mkdir();target=workspace/'.dsh/skills'
            shutil.copyfile(ROOT/('install.'+engine),pkg/('install.'+engine))
            (pkg/'docs').mkdir();shutil.copyfile(ROOT/'docs/SKILL_MIGRATION.json',pkg/'docs/SKILL_MIGRATION.json')
            shutil.copyfile(ROOT/'skill-migration.tsv',pkg/'skill-migration.tsv')
            if requested_case.endswith('_crlf'):
                p=pkg/'skill-migration.tsv';p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
            if case=='missing_map':
                (pkg/'skill-migration.tsv').unlink();(pkg/'docs/SKILL_MIGRATION.json').unlink()
            for name in PAIRS.values():
                folder=pkg/'skills'/name;folder.mkdir(parents=True)
                (folder/'SKILL.md').write_text('---\nname: '+name+'\ndescription: fixture\n---\nNew '+name,encoding='utf-8')
                (folder/'new-contract.txt').write_text('current checked package',encoding='utf-8')
            unrelated=target/'unrelated-author-skill';unrelated.mkdir(parents=True)
            (unrelated/'SKILL.md').write_text('author-owned unrelated instruction',encoding='utf-8')
            research=workspace/'research.txt';research.write_text('author data sentinel',encoding='utf-8')
            old_names=list(PAIRS) if case in {'migrate_all','check_only','legacy_default','legacy_overwrite','collision'} else []
            for name in old_names:
                folder=target/name;folder.mkdir()
                (folder/'SKILL.md').write_text('old customised '+name,encoding='utf-8')
                (folder/'custom-config.json').write_text('{"author":"keep exact old settings"}',encoding='utf-8')
            if case in {'overwrite','canonical_default','collision'}:
                folder=target/'voltpeer-plot';folder.mkdir()
                (folder/'SKILL.md').write_text('existing canonical customisation',encoding='utf-8')
                (folder/'obsolete.py').write_text('preserve in backup, never stale-merge',encoding='utf-8')
            if case=='invalid_source':(pkg/'skills/invalid-skill').mkdir()
            if case=='source_link':
                try:(pkg/'skills/voltpeer-plot/linked.txt').symlink_to(research)
                except OSError:self.skipTest('symlink privilege unavailable')
            if case=='source_junction':
                if os.name!='nt':self.skipTest('Windows junction fixture')
                linked=pkg/'skills/voltpeer-plot/linked-directory'
                owner=base/'author-directory';owner.mkdir();(owner/'keep.txt').write_text('retain external original')
                shell=SHELLS['ps1']
                if not shell:self.skipTest('PowerShell unavailable')
                script="New-Item -ItemType Junction -Path '"+str(linked).replace("'","''")+"' -Target '"+str(owner).replace("'","''")+"' | Out-Null"
                made=subprocess.run([shell,'-NoProfile','-Command',script],capture_output=True)
                if made.returncode:self.skipTest('junction creation unavailable')
            before=snapshot(target);outside=[research.read_bytes(),snapshot(unrelated)]
            env={**os.environ,'HOME':str(home),'USERPROFILE':str(home),'CODEX_HOME':str(home/'.codex'),'KIMI_CODE_HOME':str(home/'.kimi-code'),'DSH_HOME':str(home/'.dsh')}
            if engine=='ps1':
                cmd=[SHELLS[engine],'-NoProfile','-File',str(pkg/'install.ps1'),'-Workspace',str(workspace)]
                if case in {'migrate_all','collision'}:cmd+=['-MigrateLegacy']
                if case in {'overwrite','legacy_overwrite','collision'}:cmd+=['-Overwrite']
                if case=='check_only':cmd+=['-CheckOnly']
            else:
                cmd=[SHELLS[engine],str(pkg/'install.sh'),'--workspace',str(workspace)]
                if case in {'migrate_all','collision'}:cmd+=['--migrate-legacy']
                if case in {'overwrite','legacy_overwrite','collision'}:cmd+=['--overwrite']
                if case=='check_only':cmd+=['--check-only']
            run=subprocess.run(cmd,cwd=pkg,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90)
            success=case in {'clean','migrate_all','overwrite','check_only'}
            self.assertEqual(run.returncode==0,success,(engine,case,run.stdout,run.stderr))
            self.assertEqual([research.read_bytes(),snapshot(unrelated)],outside)
            if not success or case=='check_only':
                self.assertEqual(snapshot(target),before,'refused/read-only call modified installation')
                self.assertFalse((target.parent/'.voltpeer-install-backups').exists())
            else:
                self.assertEqual({p.name for p in target.glob('voltpeer-*')},set(PAIRS.values()))
                self.assertFalse(list(target.glob('battery-*')))
                self.assertEqual((target/'voltpeer-plot/new-contract.txt').read_text(),'current checked package')
                if case=='migrate_all':
                    saved=list((target.parent/'.voltpeer-install-backups').glob('*/legacy'))
                    self.assertEqual(len(saved),1)
                    self.assertFalse(saved[0].is_relative_to(target))
                    self.assertEqual({p.name for p in saved[0].iterdir()},set(PAIRS))
                    for name in PAIRS:
                        self.assertEqual((saved[0]/name/'SKILL.md').read_text(),'old customised '+name)
                        self.assertEqual((saved[0]/name/'custom-config.json').read_text(),'{"author":"keep exact old settings"}')
                if case=='overwrite':
                    saved=list((target.parent/'.voltpeer-install-backups').glob('*/canonical/voltpeer-plot'))
                    self.assertEqual(len(saved),1)
                    self.assertEqual((saved[0]/'obsolete.py').read_text(),'preserve in backup, never stale-merge')
                    self.assertFalse((target/'voltpeer-plot/obsolete.py').exists())
            RESULTS.append({'engine':engine,'case':requested_case,'exit_code':run.returncode,'passed':True})

    def test_actual_install_and_legacy_protection(self):
        for engine in SHELLS:
            for case in ('clean','legacy_default','legacy_overwrite','check_only','migrate_all','migrate_all_crlf','canonical_default','overwrite','collision','collision_crlf','invalid_source','missing_map','source_link','source_junction'):
                with self.subTest(engine=engine,case=case):self.trial(engine,case)

    def test_alias_map_is_bijective_and_source_has_only_canonical_entries(self):
        self.assertEqual(len(PAIRS),15)
        self.assertEqual(len(set(PAIRS.values())),15)
        self.assertEqual(sum(row['primary'] for row in MAPPING['aliases']),6)
        self.assertEqual({p.parent.name for p in (ROOT/'skills').glob('*/SKILL.md')},set(PAIRS.values()))
        pairs=[tuple(line.split()) for line in (ROOT/'skill-migration.tsv').read_text().splitlines() if not line.startswith('#')]
        self.assertEqual(dict(pairs),PAIRS)
        self.assertFalse(MAPPING['install_legacy_aliases'])

    @classmethod
    def tearDownClass(cls):
        out=ROOT/'outputs/naming-migration-20261002';out.mkdir(exist_ok=True)
        (out/'installer-actual.json').write_text(json.dumps({'scope':'Isolated filesystem transactions; host discovery NOT_RUN','results':RESULTS},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':unittest.main()
