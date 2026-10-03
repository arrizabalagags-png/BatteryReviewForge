"""Run the actual current full-cell recipe and Plot Starter plus rejection gates."""
from __future__ import annotations
from collections import Counter
import copy,csv,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
EVIDENCE=ROOT.parent/'deployment/evidence/2026-10-03/cycling-science-rule/v1.2.0'
ENV={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1','MPLBACKEND':'Agg'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def command(args,cwd,label):
    run=subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=cwd,env=ENV,capture_output=True,text=True,encoding='utf-8')
    (EVIDENCE/(label+'-stdout.txt')).write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
    if run.returncode:raise ValueError(label+': '+run.stdout+run.stderr)
    return run.stdout
def svg_check(path):
    ids=[n.attrib['id'] for n in ET.parse(path).getroot().iter() if 'id' in n.attrib]
    bad=[k for k,n in Counter(ids).items() if n>1]
    if bad:raise ValueError('Duplicate SVG IDs: '+str(bad))
    return {'file':str(path),'ids':len(ids),'duplicate_ids':[]}
def input_hashes(root):return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*.csv')}

def main():
    pointer=json.loads((DOCS/'assets/cycling-rule-v1.0.0/skill-downloads.json').read_text(encoding='utf-8'))
    registry=DOCS/pointer['recipe_registry']
    recipe=next(row for row in json.loads(registry.read_text(encoding='utf-8'))['packs'] if row['resource_id']=='full_cell')
    recipe_archive=registry.parent/recipe['file']
    if sha(recipe_archive)!=recipe['sha256']:raise ValueError('Recipe archive SHA mismatch')
    extracted=EVIDENCE/'extracted-recipe'
    if extracted.exists():raise FileExistsError('Preserve earlier evidence; use a new evidence directory')
    with ZipFile(recipe_archive) as z:z.extractall(extracted)
    pack=extracted/'full_cell';before=input_hashes(pack)
    out=EVIDENCE/'recipe-working'
    command([pack/'src/plot.py','--config',pack/'config.demo.json','--out',out],pack,'recipe-render')
    command([pack/'checks.py','--working',out],pack,'recipe-file-check')
    if before!=input_hashes(pack):raise ValueError('Recipe original CSV changed')
    checks=json.loads((out/'.voltpeer/records/data_checks.json').read_text(encoding='utf-8'))
    cycle=[r for r in checks['exact_data_artist_checks'] if r['style_check']=='cycle_scatter']
    continuous=[r for r in checks['exact_data_artist_checks'] if r['style_check']=='solid_without_markers']
    if not (len(cycle)==6 and continuous):raise ValueError('Need capacity, CE, retention for both samples plus voltage profiles')
    if not all(r['line_style'] in ('None','',' ') and r['marker']=='o' for r in cycle):raise ValueError('Cycle artists are not point-only')
    for sample in dict.fromkeys(r['identity'].split(':')[0] for r in cycle):
        cap=next(r for r in cycle if r['identity']==sample+':capacity')
        ce=next(r for r in cycle if r['identity']==sample+':CE')
        ret=next(r for r in cycle if r['identity']==sample+':retention')
        if not (cap['x']==ce['x']==ret['x']):raise ValueError('Cycle axes diverged')
        qref=cap['y'][cap['x'].index(1.0)]
        if not np.allclose(ret['y'],100*np.array(cap['y'])/qref):raise ValueError('Retention does not use explicit model reference')
    recipe_svg=svg_check(out/'results/figure.svg')
    starter_archive=DOCS/pointer['starter_archive'];starter_extract=EVIDENCE/'extracted-starter'
    with ZipFile(starter_archive) as z:z.extractall(starter_extract)
    starter=starter_extract/'plot_starter';before_starter=input_hashes(starter)
    command([starter/'start.py','check'],starter,'starter-package-check')
    starter_out=EVIDENCE/'starter-working'
    command([starter/'start.py','demo','--kind','full_cell_cycling','--out',starter_out],starter,'starter-full-render')
    command([starter/'start.py','check','--working',starter_out],starter,'starter-working-check')
    if before_starter!=input_hashes(starter):raise ValueError('Starter original CSV changed')
    starter_svg=svg_check(starter_out/'results/figure.svg')
    sys.path.insert(0,str(starter/'skills/voltpeer-plot/scripts'))
    from batteryplot.cycling import full_cell_quantities
    from batteryplot.ingest import apply_mapping,read_table
    from batteryplot.data import DataContractError
    demo=json.loads((starter/'demo/full_cell_cycling.json').read_text(encoding='utf-8'))
    rows=apply_mapping(read_table(starter/'demo/full_cell_cycling.csv'),demo['columns'],demo['common'])
    derived,references=full_cell_quantities(rows)
    if len(derived)!=len(rows):raise ValueError('Full-cell quantity transformation drops rows')
    cases={}
    cases['missing CE']=lambda rr:[r.pop(k,None) for r in rr for k in ('ce_pct','charge_capacity')]
    cases['missing reference cycle']=lambda rr:[r.pop('reference_cycle',None) for r in rr]
    cases['missing reference capacity']=lambda rr:[r.pop('reference_capacity',None) for r in rr]
    cases['absent reference record']=lambda rr:[r.update(reference_cycle='999999') for r in rr]
    cases['wrong reference capacity']=lambda rr:[r.update(reference_capacity=float(r['reference_capacity'])+1) for r in rr]
    cases['wrong CE ledger']=lambda rr:rr[0].update(ce_pct=float(rr[0]['ce_pct'])+1)
    cases['different rate']=lambda rr:rr[-1].update(rate='changed rate')
    cases['different temperature']=lambda rr:rr[-1].update(temperature_c='30')
    failures=[]
    for name,change in cases.items():
        bad=copy.deepcopy(rows);change(bad)
        try:full_cell_quantities(bad)
        except DataContractError as error:failures.append({'case':name,'rejected':True,'reason':str(error)})
        else:raise ValueError('Missing scientific requirement accepted: '+name)
    anomaly=copy.deepcopy(rows)
    anomaly[0]['charge_capacity']=float(anomaly[0]['discharge_capacity'])/.1*0.099
    anomaly[0]['ce_pct']=100*float(anomaly[0]['discharge_capacity'])/float(anomaly[0]['charge_capacity'])
    retained,_=full_cell_quantities(anomaly)
    if not (retained[0]['ce_pct']>100 and retained[0]['ce_pct']==anomaly[0]['ce_pct']):raise ValueError('CE anomaly clipped')
    # Exercise the downloaded implementation with exactly two observations,
    # including the empty-xlabel twin CE axis and explicit guide/cap artists.
    from batteryplot.battery_charts import cycling_capacity
    from batteryplot.series_policy import apply_series_policy,check_series_policy,reference_or_cap
    import matplotlib.pyplot as plt
    two=[r for r in rows if float(r['cycle']) in (1,2)]
    fig,_=cycling_capacity(two,cell_configuration='full',width_mm=180,height_mm=120)
    two_artists=[]
    for index,ax in enumerate(fig.axes):
        if ax.get_ylabel()=='Capacity retention (%)' and ax.get_ylim()[1]<=100:
            raise ValueError('Retention reference marker clipped by upper axis limit')
        original=[(np.array(line.get_xdata(),copy=True),np.array(line.get_ydata(),copy=True)) for line in ax.lines]
        apply_series_policy(ax)
        for line,(xs,ys) in zip(ax.lines,original):
            sampling=check_series_policy(ax,line)
            if not (sampling=='cycle_scatter' and len(line.get_xdata())==2 and np.array_equal(xs,line.get_xdata()) and np.array_equal(ys,line.get_ydata())):raise ValueError('Downloaded two-cycle full-cell artist changed or retained line')
            two_artists.append({'axis':index,'xlabel':ax.get_xlabel(),'ylabel':ax.get_ylabel(),'points':len(xs),'sampling':sampling,'linestyle':line.get_linestyle(),'marker':line.get_marker(),'x':xs.tolist(),'y':ys.tolist()})
    if len(two_artists)!=6 or not any(r['xlabel']=='' and r['ylabel']=='Coulombic efficiency (%)' for r in two_artists):raise ValueError('Downloaded two-cycle twin CE not covered')
    fig.savefig(EVIDENCE/'two-cycle-downloaded-full-cell.png',dpi=180);plt.close(fig)
    fixture,ax=plt.subplots();ax.set(xlabel='Cycle number',ylabel='Capacity (mAh)')
    observations=ax.plot([1,2],[2,1.9],label='Two observed cycles')[0]
    reference=ax.axhline(2,linestyle='--',label='Declared reference')
    errorbar=ax.errorbar([1,2],[2,1.9],yerr=[.01,.02],fmt='o',capsize=3,label='Repeated observations')
    ax.legend();apply_series_policy(ax)
    if not reference_or_cap(ax,reference) or check_series_policy(ax,reference)!='reference_solid':raise ValueError('Reference identity/style failed')
    if check_series_policy(ax,observations)!='cycle_scatter' or check_series_policy(ax,errorbar.lines[0])!='cycle_scatter':raise ValueError('Two observed cycles were treated as reference')
    if not all(check_series_policy(ax,cap)=='uncertainty_caps' for cap in errorbar.lines[1]):raise ValueError('Errorbar cap treated as observation')
    fixture.savefig(EVIDENCE/'two-cycle-reference-cap-fixture.png',dpi=180);plt.close(fixture)
    dump(EVIDENCE/'two-cycle-downloaded-runtime-check.json',{'status':'PASS','starter_archive':str(starter_archive),'starter_sha256':sha(starter_archive),'actual_artists':two_artists,'capacity_CE_retention_artist_count':6,'original_arrays_unchanged':True,'twin_CE_shared_cycle_axis':True,'retention_reference_markers_inside_axis':True,'reference_line_solid_unmarked':True,'errorbar_caps_separately_identified':True,'single_two_cycle_observations':'no reference heuristic by array length'})
    report={'status':'PASS','scope':'Actual extracted current full-cell recipe and Starter; eight explicit input-contract rejection cases. No acquired data or native/model certification.',
        'recipe_archive':str(recipe_archive),'recipe_sha256':sha(recipe_archive),'recipe_original_csv_unchanged':True,
        'recipe_cycle_artist_count':len(cycle),'recipe_continuous_voltage_artist_count':len(continuous),
        'capacity_CE_retention_same_cycles':True,'retention_reference_cycle':1,'retention_uses_recorded_Qref':True,
        'recipe_svg':recipe_svg,'starter_archive':str(starter_archive),'starter_sha256':sha(starter_archive),
        'starter_original_csv_unchanged':True,'starter_svg':starter_svg,'full_cell_reference_records':references,
        'rejections':failures,'above_100_CE_preserved':True,'native_host_discovery':'NOT_RUN','model_behavior':'NOT_RUN'}
    report['two_cycle_downloaded_runtime']='two-cycle-downloaded-runtime-check.json'
    dump(EVIDENCE/'full-cell-delivery-check.json',report)
    print(json.dumps({'status':'PASS','rejections':len(failures),'recipe_and_starter_actual_commands':True},ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
