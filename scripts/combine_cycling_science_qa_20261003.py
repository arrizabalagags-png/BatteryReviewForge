"""Bind already completed checks to the current immutable cycling delivery."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT.parent
BASE=WEB/'deployment/evidence/2026-10-03/cycling-science-rule'
FINAL=BASE/'final'
DOCS=ROOT/'docs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def record(p):return {'path':p.relative_to(WEB).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def main():
    replay_path=BASE/'v1.2.0/actual-current-replay.json'
    full_path=BASE/'v1.2.1/full-cell-delivery-check.json'
    skill_path=BASE/'v1.2.1/skill-distribution-check.json'
    one_two_path=FINAL/'one-two-cycle-downloaded-artist-check.json'
    historical_path=FINAL/'historical-byte-preservation.json'
    public_path=FINAL/'public-mirror-sync.json'
    reports={name:(path,read(path)) for name,path in [('16_source_data_replays',replay_path),('current_recipe_and_starter',full_path),('current_35_skill_packages',skill_path),('actual_one_two_cycle_artists',one_two_path),('original_historical_zip_bytes',historical_path),('public_mirror_and_historical_zip_bytes',public_path)]}
    checks=[]
    def check(name,ok,evidence):
        checks.append({'name':name,'status':'PASS' if ok else 'FAIL','evidence':evidence})
        if not ok:raise ValueError(name)
    for name,(path,value) in reports.items():
        ok=value.get('status')=='PASS' and not value.get('errors') and not value.get('failed',0)
        if name=='current_35_skill_packages':
            archives=value.get('archives',[]);downloads=DOCS/'downloads/v0.12.0-cycling-rule-v1.2.1'
            ok=len(archives)==35 and value.get('isolated_skill_checks')==66 and all(sha(downloads/r['file'])==r['sha256'] and (downloads/r['file']).stat().st_size==r['bytes'] for r in archives)
        check(name,ok,record(path))
    replay=reports['16_source_data_replays'][1];full=reports['current_recipe_and_starter'][1]
    check('16 exact affected downloads actually executed',replay['replayed_example_count']==16 and all(r['all_cycle_artists_marker_only'] and r['original_csv_unchanged'] and not r['public_dashed_artists'] for r in replay['checks']),record(replay_path))
    before=read(BASE/'v1.2.0/inventory-190-before.json');after=read(BASE/'v1.2.0/inventory-190-after.json')
    check('all 190 original CSV inventories retained',len(before)==len(after)==190 and all(a['id']==b['id'] and a['original_csv']==b['original_csv'] for a,b in zip(before,after)),{'before':record(BASE/'v1.2.0/inventory-190-before.json'),'after':record(BASE/'v1.2.0/inventory-190-after.json')})
    pointer_path=DOCS/'assets/cycling-rule-v1.0.0/skill-downloads.json';pointer=read(pointer_path)
    check('final delivery identity',pointer['revision']=='cycling-rule-v1.2.0' and pointer['package_revision']=='cycling-rule-v1.2.1' and full['starter_sha256']==sha(DOCS/pointer['starter_archive']),record(pointer_path))
    rows={r['id']:r for r in pointer['affected_examples']}
    check('all 16 current ZIP identities match actual replay',len(rows)==16 and all(rows[r['id']]['archive_sha256']==r['archive_sha256']==sha(DOCS/r['archive']) for r in replay['checks']),record(pointer_path))
    components=[]
    for row in rows.values():
        for kind in ('source','data','figures','prompt'):
            value=row['component_records'][kind];path=DOCS/value['url']
            check('current component identity '+row['id']+' '+kind,value['sha256']==sha(path) and value['bytes']==path.stat().st_size,{'url':value['url'],'sha256':value['sha256']})
            components.append({'id':row['id'],'kind':kind,**value})
    retained=[]
    for version in ('v1.0.0','v1.1.0','v1.2.0'):
        manifest=DOCS/('assets/cycling-rule-'+version+'/CYCLING_REVISION.json')
        if not manifest.exists():continue
        value=read(manifest)
        for row in value['affected_examples']:
            path=DOCS/row['archive'];assert sha(path)==row['archive_sha256']
            retained.append({'version':version,'archive':row['archive'],'sha256':row['archive_sha256']})
        starter_registry=(DOCS/value['starter_archive']).parent/'plot-starter.json'
        if starter_registry.exists():
            value=read(starter_registry);entries=value if isinstance(value,list) else value.get('packs',[value])
            for entry in entries:
                if 'sha256' in entry:
                    path=starter_registry.parent/entry['file'];assert sha(path)==entry['sha256'];retained.append({'version':version,'archive':path.relative_to(DOCS).as_posix(),'sha256':entry['sha256']})
    check('previous generated revisions remain immutable',bool(retained),{'recorded_archive_identities':retained})
    report={'schema_version':1,'status':'PASS','failed':0,'checks':checks,
      'scope':'Completed local cycle-quantity delivery checks, actual extracted execution, actual artists/SVG, bounded visual review and byte preservation. This is not measured battery validation, journal acceptance or native/model certification.',
      'plugin_version':'0.12.0 Beta','example_delivery_revision':'cycling-rule-v1.2.0','skill_and_starter_package_revision':'cycling-rule-v1.2.1',
      'current_pointer':record(pointer_path),'current_starter':record(DOCS/pointer['starter_archive']),
      'current_recipe_archive':{'path':full['recipe_archive'],'sha256':full['recipe_sha256']},
      'current_skill_archive_count':35,'actual_example_replays':16,'current_components':components,
      'evidence':{name:record(path) for name,(path,value) in reports.items()},
      'scientific_quantity_checks':replay['quantity_checks'],'full_cell_contract_rejections':full['rejections'],
      'capacity_CE_retention_same_cycles':full['capacity_CE_retention_same_cycles'],'above_100_CE_preserved':full['above_100_CE_preserved'],
      'one_two_cycle_twin_legend_and_reference_marker_checks':record(one_two_path),
      'original_csv_inventory_count':190,'original_csv_changes':[],
      'original_web_zip_preservation_count':reports['original_historical_zip_bytes'][1]['archive_count'],
      'original_public_zip_preservation_count':reports['public_mirror_and_historical_zip_bytes'][1]['historical_zip_count'],
      'visual_review':{'actually_viewed':['v1.2.0/recipe-working/results/figure.png','v1.2.1/starter-working/results/figure.png','v1.2.0/replayed-current/zn_i2_cycle/figure.png','v1.2.0/replayed-current/flow_efficiency/figure.png','v1.2.0/replayed-current/full_cell/figure.png','v1.2.0/replayed-current/li_cu_ce/figure.png','final/current-16-overview-1.png','final/current-16-overview-2.png'],
        'verified':'Marker-only capacity/CE/retention, hollow CE, boxed axes, full-cell reference quantities, continuous voltage/spectra, corrected Starter label and complete 100% reference markers. Dense 200/500-cycle markers overlap at overview scale; no connecting data paths exist in checked SVGs.',
        'limits':'Contact sheets are overview checks; author scientific interpretation and exact target-journal submission review remain required.'},
      'known_missing_physical_conditions':[{'id':'zn_i2_cycle','missing':'Acquired physical current/rate, actual cell protocol and experimental retention reference. Current plot is an explicitly declared synthetic model; cycle-1 reference capacity 174.64425068346046 mAh/g iodine.'},
        {'id':'flow_efficiency','missing':'Acquired cell chemistry, physical rate/current and experimental protocol/reference. Current original charge/energy ledger is a teaching model; cycle-1 discharge reference 98.18818019999999 mAh.'}],
      'quantity_boundaries':['Specific capacity remains mAh/g, distinct from dimensionless retention percentage.','Historical full_cell gallery ID is the declared excess-Li NMC811||Li half-cell model.','Li||Cu/Na||Cu/Zn||Cu plating CE does not require capacity retention.','The inventory-compounding figure is an idealized retained-inventory law sampled on an equivalent-cycle grid; it is not measured capacity retention or a prediction of lifetime from CE.'],
      'style_authority':'Explicit user choice, not a universal journal mandate.',
      'publication':{'GitHub':'NOT_PUSHED','ECS':'NOT_DEPLOYED','native_host_discovery':'NOT_RUN','full_model_gate':'NOT_RUN'}}
    (FINAL/'SCIENCE_CYCLING_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','failed':0,'report':str(FINAL/'SCIENCE_CYCLING_QA.json'),'current_starter_sha256':report['current_starter']['sha256'],'replayed':16,'skill_packages':35},ensure_ascii=False))
if __name__=='__main__':main()
