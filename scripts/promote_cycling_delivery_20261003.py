"""Point the local site to an independent checked cycle delivery.

The mutable current pointer is separate from all immutable ZIP bytes. This
command records byte closure; actual replay/visual evidence is a separate gate.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'

def sha(value):return hashlib.sha256(value).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def relative(path):return path.relative_to(DOCS).as_posix()

def promote(revision_root,downloads):
    current=json.loads((revision_root/'CYCLING_REVISION.json').read_text(encoding='utf-8'))
    archives=[];mapping={}
    for path in sorted(downloads.rglob('*.zip')):
        name=path.relative_to(downloads).as_posix()
        archives.append({'file':name,'url':relative(path),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())})
        mapping['downloads/v0.12.0/'+name]=relative(path)
    if len(archives)!=35:raise ValueError('Expected 35 current Skill archives')
    starter=DOCS/current['starter_archive']
    starter_record={'url':relative(starter),'sha256':sha(starter.read_bytes()),'bytes':starter.stat().st_size}
    checksum=''.join(row['sha256']+'  '+row['file']+'\n' for row in archives)
    checksum+=starter_record['sha256']+'  '+starter_record['url']+'\n'
    (downloads/'distribution-sha256.txt').write_text(checksum,encoding='utf-8')
    index={'schema_version':1,'brand':'VoltPeer','version':'0.12.0','channel':'beta',
        'resource_revision':current['revision'],'package_revision':current.get('package_revision',current['revision']),'publication':'LOCAL_CANDIDATE_NOT_PUSHED_NOT_DEPLOYED',
        'base_url':relative(downloads)+'/', 'current_skill_archive_count':35,'archives':archives,'plot_starter':starter_record,
        'native_host_discovery':'NOT_RUN','full_model_gate':'NOT_RUN'}
    dump(downloads/'download-index.json',index)
    for name in ('distribution-sha256.txt','download-index.json'):
        mapping['downloads/v0.12.0/'+name]=relative(downloads/name)
        mapping['downloads/'+name]=relative(downloads/name)
    mapping['downloads/v0.12.0/starter/'+starter.name]=relative(starter)
    mapping['assets/frontpage/']=current['frontpage_root']+'/'
    for row in current['affected_examples']:
        records={}
        for key in ('source','data','figures','prompt'):
            path=DOCS/row[key]
            item={'url':row[key],'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}
            if key!='prompt':
                with ZipFile(path) as archive:
                    if archive.testzip():raise ValueError('Corrupt current ZIP '+str(path))
                    item['files']=archive.namelist()
                    item['members']=[{'path':name,'sha256':sha(archive.read(name)),'bytes':len(archive.read(name))} for name in archive.namelist()]
            records[key]=item
        row['component_records']=records
    pointer={**current,'plugin_version':'0.12.0','url_map':mapping,'archives':archives,'skill_archive_count':35,
        'distribution_sha256':relative(downloads/'distribution-sha256.txt'),
        'download_manifest':relative(downloads/'download-index.json'),
        'starter_registry':relative(starter.parent/'plot-starter.json'),
        'installer_contract':{'entry_point':'render_existing.py','metadata_path':'<id>/metadata.json',
            'source_and_data':'Extract both components into the same NEW folder, preserving paths.'}}
    old_pointer=DOCS/'assets/cycling-rule-v1.0.0/skill-downloads.json'
    evidence=ROOT.parent/'deployment/evidence/2026-10-03/cycling-science-rule'/current.get('package_revision',current['revision']).replace('cycling-rule-','')
    evidence.mkdir(parents=True,exist_ok=True)
    if old_pointer.exists():
        previous=json.loads(old_pointer.read_text(encoding='utf-8'))
        dump(evidence/'previous-current-pointer.json',previous)
    dump(old_pointer,pointer)
    dump(evidence/'current-download-overlay.json',pointer)
    print(json.dumps({'current_pointer':str(old_pointer),'revision':current['revision'],'example_overrides':len(current['affected_examples']),'skill_archives':35},ensure_ascii=False))
    return pointer

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision-root',type=Path,required=True)
    parser.add_argument('--download-root',type=Path,required=True)
    args=parser.parse_args()
    promote(args.revision_root.resolve(),args.download_root.resolve())
