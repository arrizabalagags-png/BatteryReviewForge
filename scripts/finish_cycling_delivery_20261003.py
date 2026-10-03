"""Complete the current cycle revision's isolated downloads, without publication.

The initial revision ZIPs remain byte-identical. Five domain examples receive
the common input-only entry in v1.0.1. Recipe/Starter instructions receive their
own new directory. The site resolver reads the resulting overlay JSON.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
ASSETS=DOCS/'assets/cycling-rule-v1.0.0'
UPDATE=DOCS/'assets/cycling-rule-v1.0.2'
DOWNLOADS=DOCS/'downloads/v0.12.0-cycling-rule-v1.0.0'
EVIDENCE=ROOT.parent/'deployment/evidence/2026-10-03/cycling-science-rule'
sys.path.insert(0,str(ROOT/'examples'))
sys.path.insert(0,str(ROOT/'scripts'))
import revise_cycling_science_20261003 as revision


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def relative(path):return Path(path).relative_to(DOCS).as_posix()


def build():
    record=ASSETS/'skill-downloads.json'
    if record.exists():raise FileExistsError('Completed current delivery exists; choose a new revision before replacing bytes')
    current=json.loads((ASSETS/'CYCLING_REVISION.json').read_text(encoding='utf-8'))
    overrides=[]
    for row in current['affected_examples']:
        ident=row['id']
        if ident not in revision.DOMAIN:continue
        target=UPDATE/'showcase'/ident
        shutil.copytree(ROOT/'examples/domain_showcase'/ident,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        metadata=json.loads((target/'metadata.json').read_text(encoding='utf-8'))
        metadata['reproduce']='python render_existing.py --output new-result'
        metadata['current_bundle_entry']='render_existing.py; supplied CSV only; domain draw() called, never data() or main()'
        for citation in metadata.get('scientific_basis',{}).get('references',[]):
            if citation.get('doi','').lower()=='10.1038/s41467-022-28381-x':
                citation['title']='Open challenges and good experimental practices in the research field of aqueous Zn-ion batteries'
        dump(target/'metadata.json',metadata)
        archive=revision.domain_package(ident,target,UPDATE,UPDATE.name)
        components=revision.components(ident,archive,target,UPDATE)
        item={**row,'asset_root':relative(target),'archive':relative(archive),
            'archive_sha256':sha(archive),'metadata_sha256':sha(target/'metadata.json'),**components,
            'prompt':relative(UPDATE/'split-demos'/ident/(ident+'-prompt.txt'))}
        overrides.append(item)
    import package_recipe_packs,package_plot_starter
    recipes=package_recipe_packs.package(ASSETS/'recipes-v1.0.1')
    starter=package_plot_starter.package(ASSETS/'starter-v1.0.1')
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/package_release.py'),'--output-root',str(DOWNLOADS)],check=True)
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/package_workbuddy.py'),
        '--output',str(DOWNLOADS/'workbuddy'),'--collection',str(DOWNLOADS/'VoltPeer-WorkBuddy-v0.12.0.zip')],check=True)
    archives=[]
    url_map={}
    for path in sorted(DOWNLOADS.rglob('*.zip')):
        name=path.relative_to(DOWNLOADS).as_posix()
        url_map['downloads/v0.12.0/'+name]=relative(path)
        archives.append({'file':name,'url':relative(path),'bytes':path.stat().st_size,'sha256':sha(path)})
    if len(archives)!=35:raise ValueError('Expected full package, 16 single, 16 WorkBuddy and two collections')
    starter_row={'file':starter.name,'url':relative(starter),'bytes':starter.stat().st_size,'sha256':sha(starter)}
    checksums=''.join(row['sha256']+'  '+row['file']+'\n' for row in archives)
    checksums+=starter_row['sha256']+'  '+starter_row['url']+'\n'
    (DOWNLOADS/'distribution-sha256.txt').write_text(checksums,encoding='utf-8')
    index={'schema_version':1,'brand':'VoltPeer','version':'0.12.0','channel':'beta',
        'resource_revision':'cycling-rule-v1.0.0','publication':'LOCAL_CANDIDATE_NOT_PUSHED_NOT_DEPLOYED',
        'base_url':relative(DOWNLOADS)+'/', 'current_skill_archive_count':len(archives),'archives':archives,
        'plot_starter':starter_row,'native_host_discovery':'NOT_RUN','full_model_gate':'NOT_RUN',
        'science_scope':'User cycle display preference and explicit scientific input contracts; no acquired-data certification.'}
    dump(DOWNLOADS/'download-index.json',index)
    for filename in ('distribution-sha256.txt','download-index.json'):
        url_map['downloads/v0.12.0/'+filename]=relative(DOWNLOADS/filename)
        url_map['downloads/'+filename]=relative(DOWNLOADS/filename)
    url_map['downloads/v0.12.0/starter/'+starter.name]=relative(starter)
    overlay={'schema_version':1,'revision':'cycling-rule-v1.0.0','plugin_version':'0.12.0',
        'url_map':url_map,'archives':archives,'skill_archive_count':len(archives),
        'distribution_sha256':relative(DOWNLOADS/'distribution-sha256.txt'),
        'download_manifest':relative(DOWNLOADS/'download-index.json'),
        'recipe_registry':relative(recipes/'recipe-packs.json'),'starter_archive':relative(starter),
        'starter_registry':relative(starter.parent/'plot-starter.json'),
        'affected_examples':overrides,
        'installer_contract':{'entry_point':'render_existing.py','metadata_path':'<id>/metadata.json',
            'source_and_data':'Unzip both components into the same new folder; code and input hashes recorded in SOURCE_MANIFEST.json'},
        'publication':{'GitHub':'NOT_PUSHED','ECS':'NOT_DEPLOYED'},
        'limits':['All example inputs are teaching models; author data need confirmed fields and conditions.',
            'Zn-I2 and flow retention references are declared original model cycle 1; acquired rate/protocol absent.',
            'Model/native discovery and end-to-end model behavior not run.']}
    dump(record,overlay)
    dump(EVIDENCE/'current-download-overlay.json',overlay)
    print(json.dumps({'record':str(record),'skill_archives':len(archives),'domain_replay_overrides':len(overrides)},ensure_ascii=False),flush=True)
    return overlay


if __name__=='__main__':build()
