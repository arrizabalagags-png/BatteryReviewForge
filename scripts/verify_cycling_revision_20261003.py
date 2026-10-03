"""Replay the 16 current source/data downloads, preserving all CSV inputs.

This is a bounded local delivery/scientific-quantity check. It neither calls a
model nor claims experimental validation or native Skill discovery.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,as_completed
import csv,hashlib,json,os,subprocess,sys
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from collections import Counter
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
EVIDENCE=ROOT.parent/'deployment/evidence/2026-10-03/cycling-science-rule'
ENV={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1','MPLBACKEND':'Agg'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def safe_unpack(path,target):
    with ZipFile(path) as archive:
        if archive.testzip():raise ValueError('Corrupt ZIP: '+str(path))
        names=archive.namelist()
        if len(set(names))!=len(names):raise ValueError('Duplicate ZIP members')
        for name in names:
            part=PurePosixPath(name)
            if part.is_absolute() or '..' in part.parts or '\\' in name or ':' in name:raise ValueError('Unsafe ZIP path')
        archive.extractall(target)

def frame_records(metadata):
    for key in ('data_frame_checks','actual_artist_checks','data_plot_checks'):
        value=metadata.get(key)
        if isinstance(value,list) and value:return value
    raise ValueError('No actual data-frame records')

def replay(row):
    ident=row['id'];bundle=EVIDENCE/'extracted-current'/ident;output=EVIDENCE/'replayed-current'/ident
    if bundle.exists() or output.exists():raise FileExistsError('Use a new evidence tree for repeated replay: '+ident)
    bundle.mkdir(parents=True)
    archive=DOCS/row['archive']
    if sha(archive)!=row['archive_sha256']:raise ValueError('Changed full archive '+ident)
    with ZipFile(archive) as z:
        manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
        closure=all(hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256'] for item in manifest['files'])
        if not closure:raise ValueError('Full-archive hash closure '+ident)
    for kind in ('source','data'):safe_unpack(DOCS/row[kind],bundle)
    manifest=json.loads((bundle/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    if manifest['entry_point']!='render_existing.py':raise ValueError('Unified entry absent '+ident)
    for item in manifest['code']+manifest['inputs']:
        if sha(bundle/item['archive_path'])!=item['sha256']:raise ValueError('Component dependency hash '+item['archive_path'])
    before={p.relative_to(bundle).as_posix():sha(p) for p in bundle.rglob('*.csv')}
    result=subprocess.run([sys.executable,'-X','utf8',str(bundle/'render_existing.py'),'--output',str(output)],cwd=bundle,env=ENV,capture_output=True,text=True,encoding='utf-8')
    (EVIDENCE/'replayed-current').mkdir(exist_ok=True)
    (EVIDENCE/'replayed-current'/(ident+'-stdout.txt')).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(ident+': '+result.stdout+result.stderr)
    after={p.relative_to(bundle).as_posix():sha(p) for p in bundle.rglob('*.csv')}
    if before!=after:raise ValueError('Original CSV changed '+ident)
    record=json.loads((output/'RUN_RECORD.json').read_text(encoding='utf-8'))
    if record['regenerated_inputs'] or record['original_inputs_written'] or record['changed_from_demo']:raise ValueError('Replay provenance altered '+ident)
    meta=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
    frames=frame_records(meta)
    if not all(all(item.get('spines',item.get('frame_spines',{})).values()) and len(item.get('spines',item.get('frame_spines',{})))==4 for item in frames):raise ValueError('Missing four data-axis spines '+ident)
    curves=meta.get('continuous_curve_style_checks') or [curve for frame in frames for curve in frame.get('continuous_curves',frame.get('curve_styles',[]))]
    points=[];continuous=[];references=[]
    empty=(None,'None','',' ')
    for curve in curves:
        style=curve.get('linestyle',curve.get('line_style'));marker=curve.get('marker');sampling=curve.get('sampling')
        if sampling=='cycle_scatter':
            if style not in empty or marker in empty:raise ValueError('Cycle artist has connecting line or no marker '+ident)
            points.append(curve)
        elif sampling in ('continuous_solid','reference_solid'):
            if style!='-' or marker not in empty:raise ValueError('Continuous/reference artist is not solid unmarked '+ident)
            (references if sampling=='reference_solid' else continuous).append(curve)
        elif sampling=='uncertainty_caps':
            if style not in empty or marker not in ('_','|'):raise ValueError('Invalid uncertainty cap '+ident)
        elif sampling=='independent_or_uncertainty_marks':
            if style not in empty:raise ValueError('Independent marks have connecting line '+ident)
        else:raise ValueError('Actual artist lacks declared sampling '+ident)
    if not points:raise ValueError('Affected example has no marker-only cycle artists '+ident)
    if ident=='zn_i2_cycle':
        ce_frame=[f for f in frames if f.get('ylabel')=='CE (%)']
        if len(ce_frame)!=1 or not all(c['sampling']=='cycle_scatter' for c in ce_frame[0]['curve_styles']):raise ValueError('Shared cycle twin CE not checked '+ident)
    svg=output/'figure.svg';text=svg.read_text(encoding='utf8')
    if 'stroke-dasharray' in text:raise ValueError('Public figure has dashed artist '+ident)
    tree=ET.parse(svg).getroot();ids=[node.attrib['id'] for node in tree.iter() if 'id' in node.attrib]
    if any(count>1 for count in Counter(ids).values()):raise ValueError('Duplicate actual SVG ID '+ident)
    groups=[node for node in tree.iter() if node.attrib.get('id','').startswith('voltpeer-cycle:')]
    def marker_group(node,in_defs=False):
        in_defs=in_defs or node.tag.rsplit('}',1)[-1]=='defs'
        if node.tag.rsplit('}',1)[-1]=='path' and not in_defs:raise ValueError('Cycle SVG contains connecting data path '+ident)
        for child in node:marker_group(child,in_defs)
    for group in groups:
        marker_group(group)
        if not any(n.tag.rsplit('}',1)[-1]=='use' for n in group.iter()):raise ValueError('Cycle SVG lacks actual marker uses '+ident)
    if not groups:raise ValueError('Actual SVG lacks cycle marker groups '+ident)
    return {'id':ident,'archive':row['archive'],'archive_sha256':sha(archive),'full_archive_manifest_closure':True,
        'source_data_actual_entry':manifest['entry_point'],'component_code_and_inputs_hashes':True,
        'csv_input_count':len(before),'original_csv_unchanged':True,'teaching_inputs_only':True,
        'all_data_spines_visible':True,'all_cycle_artists_marker_only':True,'cycle_artist_count':len(points),
        'continuous_artist_count':len(continuous),'reference_solid_artist_count':len(references),
        'svg_cycle_marker_group_count':len(groups),'svg_duplicate_ids':[],'public_dashed_artists':False,'run_record':str(output/'RUN_RECORD.json'),
        'figure_png':str(output/'figure.png'),'native_discovery':'NOT_RUN','model_behavior':'NOT_RUN'}

def quantity_checks():
    result=[]
    for ident in ('na_metal_ce','zn_plating_ce','zn_i2_cycle','flow_efficiency'):
        folder=ROOT/'examples/domain_showcase'/ident
        with (folder/'data.csv').open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
        values=lambda key:np.array([float(r[key]) for r in rows])
        if ident in ('na_metal_ce','zn_plating_ce'):
            ratio=100*values('q_stripping_mAh_cm2')/values('q_plating_mAh_cm2')
            ce=values('ce_percent')
        elif ident=='zn_i2_cycle':
            ratio=100*values('capacity_mAh_g_iodine')/values('charge_capacity_mAh_g_iodine');ce=values('ce_percent')
        else:
            ratio=100*values('q_discharge_mAh')/values('q_charge_mAh');ce=values('ce_percent')
        if not np.allclose(ratio,ce,rtol=1e-11,atol=1e-11):raise ValueError('CE source ledger mismatch '+ident)
        check={'id':ident,'CE_ratio':'100*same-cycle recovered charge / supplied charge','same_cycle_raw_ledger':True,'ce_max_abs_error':float(np.max(np.abs(ratio-ce)))}
        if ident in ('zn_i2_cycle','flow_efficiency'):
            cap=values('capacity_mAh_g_iodine' if ident=='zn_i2_cycle' else 'q_discharge_mAh')
            check.update(reference_cycle=int(float(rows[0]['cycle'])),reference_capacity=float(cap[0]),
                retention_definition='100*Qdis(n)/explicit Qdis(reference cycle 1)',
                physical_rate_protocol='NOT_SUPPLIED; original teaching model context only')
        result.append(check)
    folder=ROOT/'examples/showcase/paper_ce_ledger'
    with (folder/'data.csv').open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
    groups={s:{float(r['x']):float(r['y']) for r in rows if r['series']==s} for s in dict.fromkeys(r['series'] for r in rows)}
    result.append({'id':'paper_ce_ledger','series':list(groups),'quantity_scope':'Same original analytic charge pairs; no acquired full cell'})
    return result

def main():
    base=json.loads((DOCS/'assets/cycling-rule-v1.0.0/CYCLING_REVISION.json').read_text(encoding='utf-8'))
    overlay=json.loads((DOCS/'assets/cycling-rule-v1.0.0/skill-downloads.json').read_text(encoding='utf-8'))
    rows={r['id']:r for r in base['affected_examples']};rows.update({r['id']:r for r in overlay['affected_examples']})
    results=[];errors=[]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures={executor.submit(replay,row):ident for ident,row in rows.items()}
        for future in as_completed(futures):
            ident=futures[future]
            try:
                results.append(future.result());print('Replayed '+ident,flush=True)
            except Exception as error:
                errors.append({'id':ident,'error':str(error)});print('FAILED '+ident+': '+str(error),flush=True)
    report={'status':'PASS' if not errors else 'FAIL','scope':'16 affected current source+CSV downloads only; no experimental or model/native certification',
        'affected_example_count':len(rows),'replayed_example_count':len(results),'checks':sorted(results,key=lambda r:r['id']),
        'quantity_checks':quantity_checks(),'errors':errors,'full_model_gate':'NOT_RUN','native_host_discovery':'NOT_RUN'}
    dump(EVIDENCE/'actual-current-replay.json',report)
    print(json.dumps({'status':report['status'],'replayed':len(results),'errors':errors},ensure_ascii=False),flush=True)
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
