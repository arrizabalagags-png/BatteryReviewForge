"""Create an independent cycle-display revision; old downloads stay untouched.

Only explicitly synthetic examples are replayed. No experimental input is
changed and no online model is called. The JSON is consumed by the site build.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, shutil, subprocess, sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
from collections import Counter
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT.parent
EVIDENCE=WEB/'deployment/evidence/2026-10-03/cycling-science-rule'
REVISION='cycling-rule-v1.0.0'
DEST=ROOT/'docs/assets'/REVISION
CORE=('full_cell','li_cu_ce','rate_capability','integrated_study','capability_spread','style_presets')
PAPER=('paper_capacity_repeat','paper_ce_ledger','paper_flow_efficiency','paper_rate_recovery')
SCIENCE=('science_inventory_compounding',)
DOMAIN=('na_metal_ce','zn_plating_ce','k_ion_rate','zn_i2_cycle','flow_efficiency')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj;spec.loader.exec_module(obj);return obj

def svg_id_check(path):
    ids=[node.attrib['id'] for node in ET.parse(path).getroot().iter() if 'id' in node.attrib]
    duplicates=[name for name,count in Counter(ids).items() if count>1]
    if duplicates:raise ValueError('SVG artist IDs repeat: '+str(path)+' '+str(duplicates))
    return {'file':str(path),'ids':len(ids),'duplicate_ids':[]}


def inventory():
    records=[]
    for base in [ROOT/'examples/showcase',ROOT/'examples/domain_showcase']:
        for folder in sorted(base.iterdir()):
            path=folder/'metadata.json'
            if not folder.is_dir() or not path.exists():continue
            meta=json.loads(path.read_text(encoding='utf8'))
            conditions=str(meta.get('test_conditions',''))
            ident=folder.name
            if ident in DOMAIN[:2] or ident=='zn_plating_ce' or ident=='li_cu_ce':kind='metal_on_Cu_plating_stripping'
            elif 'half-cell' in conditions or 'half cell' in conditions or ident=='k_ion_rate':kind='half_cell'
            elif ident in PAPER+SCIENCE or ident.startswith(('science_','paper_')):kind='analytic_method_no_experimental_cell'
            elif ident=='zn_i2_cycle':kind='Zn_I2_model_with_excess_Zn'
            elif ident=='flow_efficiency':kind='unnamed_flow_charge_energy_model'
            elif 'symmetric' in conditions.lower():kind='symmetric_cell'
            else:kind='other_or_composite_declared_in_metadata'
            raw=[{'path':p.name,'sha256':sha(p)} for p in sorted(folder.glob('*.csv'))]
            records.append({'id':ident,'cell_scope':kind,'variables_and_units':meta.get('variables_and_units'),
                'data_status':meta.get('data_status'),'source_files':meta.get('source_files',[]),
                'cycle_revision':ident in CORE+PAPER+SCIENCE+DOMAIN,'original_csv':raw})
    if len(records)!=190:raise ValueError('Expected current 190-example collection; inspect actual inventory before revising')
    return records


def archive_payload(path,payload,manifest):
    if path.exists():raise ValueError('Refuse replacing an existing revision archive: '+str(path))
    manifest['files']=[{'path':p,'sha256':hashlib.sha256(v).hexdigest()} for p,v in sorted(payload.items())]
    payload['SOURCE_MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        for name,value in sorted(payload.items()):z.writestr(name,value)


def analytic_package(ident,family,folder):
    render_name='paper_renderer.py' if family=='paper' else 'science_renderer_20261003.py'
    code={'code/examples/showcase/'+family+'.py':(ROOT/'examples'/render_name).read_bytes(),
          'code/examples/showcase/series_policy.py':(ROOT/'skills/voltpeer-plot/scripts/batteryplot/series_policy.py').read_bytes(),
          'render_existing.py':(ROOT/'examples/demo_bundle_runner.py').read_bytes()}
    inputs={ident+'/'+name:(folder/name).read_bytes() for name in ['data.csv','model.json','metadata.json']}
    payload={**code,**inputs,'requirements.txt':b'numpy>=1.26,<3\nmatplotlib>=3.8,<4\n',
        'LICENSE':(ROOT/'LICENSE').read_bytes(),
        'README.txt':b'Synthetic model only. Run python render_existing.py --output new-result. Cycle quantities use points without connecting lines. Continuous voltage/spectra use solid unmarked traces. Check every axis contract before adapting author data.\n'}
    for ext in ['png','svg','pdf']:payload['reference/figure.'+ext]=(folder/('figure.'+ext)).read_bytes()
    payload['reference/metadata.json']=(folder/'metadata.json').read_bytes()
    manifest={'schema_version':1,'sample':ident,'renderer':'examples/showcase/'+family+'.py',
        'entry_point':'render_existing.py','operation':'render_existing_inputs_only','revision':REVISION,
        'source_snapshot':'archive-contained bytes; no remote publication asserted',
        'code':[{'archive_path':p,'sha256':hashlib.sha256(v).hexdigest()} for p,v in code.items()],
        'inputs':[{'archive_path':p,'render_path':p,'sha256':hashlib.sha256(v).hexdigest()} for p,v in inputs.items()]}
    target=DEST/'showcase'/('BRF-demo-'+ident+'.zip');archive_payload(target,payload,manifest);return target


def domain_package(ident,folder,destination=None,revision=None):
    """The same source/input entry used by all current downloadable examples.

    domain_component_renderer calls draw() on the existing CSV only. The
    model's random data generator and main() are never invoked by this entry.
    """
    destination=destination or DEST
    revision=revision or REVISION
    import resource_demos
    kind=next(row[3] for row in resource_demos.RECIPES if row[0]==ident)
    inputs={ident+'/'+p.name:p.read_bytes() for p in sorted(folder.iterdir())
        if p.is_file() and p.suffix in {'.csv','.json'} and not p.name.startswith('figure.')}
    code={'code/examples/showcase/domain.py':(ROOT/'examples/domain_component_renderer.py').read_bytes(),
        'code/examples/showcase/domain_model.py':(ROOT/'examples/resource_demos.py').read_bytes(),
        'code/examples/showcase/series_policy.py':(ROOT/'skills/voltpeer-plot/scripts/batteryplot/series_policy.py').read_bytes(),
        'render_existing.py':(ROOT/'examples/demo_bundle_runner.py').read_bytes()}
    closure={ident:{'kind':kind,'inputs':{name[len(ident)+1:]:hashlib.sha256(value).hexdigest() for name,value in inputs.items()}}}
    code['code/examples/showcase/domain_inputs.json']=(json.dumps(closure,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    payload={**code,**inputs,'LICENSE':(ROOT/'LICENSE').read_bytes(),
        'requirements.txt':b'numpy>=1.26,<3\nmatplotlib>=3.8,<4\n',
        'README.txt':b'Original synthetic teaching example only. Extract source and data ZIPs into the same new folder. Run python render_existing.py --output new-result. The entry reads the existing CSV and calls draw() only. It never regenerates inputs. Cycle CE/capacity/retention use points without connecting lines; continuous voltage/spectra use solid traces without markers. Check units, definition, reference capacity/cycle and matching conditions before adapting author data; the teaching replay intentionally rejects substituted inputs.\n'}
    for ext in ['png','svg','pdf']:payload['reference/figure.'+ext]=(folder/('figure.'+ext)).read_bytes()
    payload['reference/metadata.json']=(folder/'metadata.json').read_bytes()
    manifest={'schema_version':1,'sample':ident,'revision':revision,
        'renderer':'examples/showcase/domain.py','entry_point':'render_existing.py',
        'operation':'render_existing_inputs_only',
        'code':[{'archive_path':p,'sha256':hashlib.sha256(v).hexdigest()} for p,v in code.items()],
        'inputs':[{'archive_path':p,'render_path':p,'sha256':hashlib.sha256(v).hexdigest()} for p,v in inputs.items()]}
    target=destination/'showcase'/('BRF-demo-'+ident+'.zip')
    archive_payload(target,payload,manifest)
    return target


def components(ident,archive,folder,destination=None):
    target=(destination or DEST)/'split-demos'/ident;target.mkdir(parents=True,exist_ok=True)
    with ZipFile(archive) as z:payload={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    manifest=json.loads(payload.get('SOURCE_MANIFEST.json',b'{}'))
    input_names={r['archive_path'] for r in manifest.get('inputs',[])}
    source={n:v for n,v in payload.items() if n.startswith('code/') or n in {'render_existing.py','requirements.txt','LICENSE','README.txt','SOURCE_MANIFEST.json','render.py','series_policy.py','README.txt','metadata.json'}}
    data={n:v for n,v in payload.items() if (n in input_names or n.startswith(ident+'/') or n.endswith('.csv')) and not n.startswith('reference/')}
    # Both components include the same manifest; unzipping into one directory
    # leaves the executable's exact code/input inventory available for replay.
    for key,values in [('source',source),('data',data),('figures',{n:v for n,v in payload.items() if n.startswith('reference/') or n.startswith('figure.')})]:
        path=target/(ident+'-'+key+'.zip')
        if path.exists():continue
        with ZipFile(path,'w',ZIP_DEFLATED) as z:
            for name,value in values.items():z.writestr(name,value)
    prompt=target/(ident+'-prompt.txt')
    prompt.write_text('用我的源数据画这类图。先确认物理量、单位、样品、测试工况、CE定义和保持率参考圈/容量；逐圈CE/容量/保持率用散点，不加连线。连续电压/光谱用实线，保留四边框。不猜缺项，不平滑，不改原值。示例是教学合成数据。\n\nUse the source and CSV components to redraw the existing teaching inputs with render_existing.py into a new output folder. Before adapting author data, confirm quantities, units, samples, test conditions, the CE definition and retention reference cycle/capacity. Cycle CE/capacity/retention use points without connecting lines; continuous voltage/spectra use solid unmarked traces. Keep four borders and all original values. List real missing requirements; do not guess, smooth or fabricate. This display is the user preference, not a universal journal mandate.\n',encoding='utf8')
    return {k:str((target/(ident+'-'+k+'.zip')).relative_to(ROOT/'docs')).replace('\\','/') for k in ['source','data','figures']}


def build():
    if (DEST/'CYCLING_REVISION.json').exists():raise ValueError('Completed version is immutable; select a new revision')
    DEST.mkdir(parents=True,exist_ok=True)
    before=inventory();dump(EVIDENCE/'inventory-190-before.json',before)
    sys.path.insert(0,str(ROOT/'examples'));sys.path.insert(0,str(ROOT/'scripts'))
    import paper_renderer,science_renderer_20261003,resource_demos,package_demo_bundles
    core=module(ROOT/'examples/showcase/build.py','voltpeer_cycle_showcase')
    already_rendered=all((DEST/'showcase'/ident/'figure.png').exists() for ident in CORE+PAPER+SCIENCE+DOMAIN)
    if not already_rendered:
        for ident in CORE:core.render(ident);print('Rendered '+ident,flush=True)
        for ident in PAPER:paper_renderer.render(ident);print('Rendered '+ident,flush=True)
        for ident in SCIENCE:science_renderer_20261003.render(ident);print('Rendered '+ident,flush=True)
    policy=ROOT/'skills/voltpeer-plot/scripts/batteryplot/series_policy.py'
    for folder in sorted((ROOT/'examples/domain_showcase').iterdir()):
        if folder.is_dir() and (folder/'render.py').exists():
            shutil.copy2(ROOT/'examples/resource_demos.py',folder/'render.py');shutil.copy2(policy,folder/'series_policy.py')
    for ident in DOMAIN:
        if already_rendered:continue
        folder=ROOT/'examples/domain_showcase'/ident
        with (folder/'data.csv').open(encoding='utf8',newline='') as s:
            reader=csv.reader(s);fields=next(reader);values=np.array(list(reader),dtype=float)
        recipe=next(r for r in resource_demos.RECIPES if r[0]==ident);kind=recipe[3]
        checks=resource_demos.draw(kind,fields,values,folder)
        meta=json.loads((folder/'metadata.json').read_text(encoding='utf8'));meta['actual_artist_checks']=checks
        meta['curve_style_check']='Cycle quantities marker-only; continuous profiles solid/unmarked; user preference.'
        meta['reproduce']='python render_existing.py --output new-result'
        meta['current_bundle_entry']='render_existing.py; supplied CSV only; draw() called, never data() or main()'
        if kind in {'cycling','efficiency'}:
            col=1 if kind=='cycling' else 5
            meta['retention_reference']={'reference_cycle':1,'reference_capacity':float(values[0,col]),
                'formula':'100*Qdis(n)/Qdis(explicit cycle 1)',
                'conditions':'same original teaching model; physical current/rate not simulated or supplied; no acquired cell normalization'}
        dump(folder/'metadata.json',meta);print('Rendered '+ident,flush=True)
    rows=[];svg_records=[]
    for ident in CORE+PAPER+SCIENCE+DOMAIN:
        folder=ROOT/'examples'/('domain_showcase' if ident in DOMAIN else 'showcase')/ident
        svg_records.extend(svg_id_check(path) for path in sorted(folder.glob('*.svg')))
        target=DEST/'showcase'/ident
        archive=DEST/'showcase'/('BRF-demo-'+ident+'.zip')
        if not already_rendered:shutil.copytree(folder,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        if archive.exists():pass
        elif ident in CORE:
            row=package_demo_bundles.package_sample(ident,DEST/'showcase');archive=DEST/'showcase'/row['file']
        elif ident in PAPER+SCIENCE:archive=analytic_package(ident,'paper' if ident in PAPER else 'science',folder)
        else:archive=domain_package(ident,folder)
        split=components(ident,archive,folder)
        rows.append({'id':ident,'asset_root':target.relative_to(ROOT/'docs').as_posix(),
            'archive':archive.relative_to(ROOT/'docs').as_posix(),'archive_sha256':sha(archive),
            'metadata_sha256':sha(target/'metadata.json'),**split,
            'prompt':(DEST/'split-demos'/ident/(ident+'-prompt.txt')).relative_to(ROOT/'docs').as_posix()})
    import package_recipe_packs,package_plot_starter
    recipe_destination=package_recipe_packs.package(DEST/'recipes')
    svg_records.extend(svg_id_check(ROOT/'examples/recipe_packs'/kind/'reference/figure.svg') for kind in package_recipe_packs.IDS)
    starter=package_plot_starter.package(DEST/'starter')
    frontpage=DEST/'frontpage'
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'examples/frontpage/render.py'),
        '--data-root',str(ROOT/'examples/showcase'),'--output-dir',str(frontpage)],check=True)
    after=inventory();changed=[]
    for a,b in zip(before,after):
        if a['id']!=b['id']:raise ValueError('Inventory identities changed during revision')
        if a['original_csv']!=b['original_csv']:changed.append(a['id'])
    if changed:raise ValueError('Unexpected original CSV changes: '+str(changed))
    result={'schema_version':1,'revision':REVISION,'style_authority':'user preference; not universal journal mandate',
        'inventory_count':190,'affected_examples':rows,'original_csv_changes':changed,
        'recipe_registry':(recipe_destination/'recipe-packs.json').relative_to(ROOT/'docs').as_posix(),
        'starter_archive':starter.relative_to(ROOT/'docs').as_posix(),
        'frontpage_root':frontpage.relative_to(ROOT/'docs').as_posix(),
        'publication':{'GitHub':'NOT_PUSHED','ECS':'NOT_DEPLOYED'},
        'limits':['190 metadata/input inventories inspected; only affected examples replayed.',
            'Zn-I2 and unnamed flow diagrams have original model capacity/CE ledgers but no acquired rate/cell protocol; model retention explicitly uses recorded cycle 1.',
            'Inventory-compounding is an idealized retained-inventory formula, not measured capacity retention or a CE life prediction.',
            'NMC811||Li belongs to the declared half-cell demonstration; historical resource ID is preserved.',
            'No native desktop/model or experimental certification.']}
    dump(DEST/'CYCLING_REVISION.json',result);dump(EVIDENCE/'current-assets.json',result)
    dump(EVIDENCE/'svg-id-checks.json',svg_records)
    dump(EVIDENCE/'inventory-190-after.json',after)
    print(json.dumps({'revision':REVISION,'affected':len(rows),'csv_changes':changed,'registry':str(DEST/'CYCLING_REVISION.json')},ensure_ascii=False),flush=True)
    return result


if __name__=='__main__':
    build()
