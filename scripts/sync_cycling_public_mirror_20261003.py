"""Sync owned scientific sources/current assets without replacing historical ZIPs."""
from __future__ import annotations
import argparse,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT.parent/'deployment/evidence/2026-10-03/cycling-science-rule/final'
IDS=('full_cell','li_cu_ce','rate_capability','integrated_study','capability_spread','style_presets','paper_capacity_repeat','paper_ce_ledger','paper_flow_efficiency','paper_rate_recovery','science_inventory_compounding')
DOMAIN=('na_metal_ce','zn_plating_ce','k_ion_rate','zn_i2_cycle','flow_efficiency')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def eligible(p):return p.is_file() and not any(s in ('__pycache__','.git') for s in p.parts) and p.suffix not in ('.pyc','.pyo')
def main(pub):
    EVIDENCE.mkdir(exist_ok=True)
    if (EVIDENCE/'public-mirror-sync.json').exists():raise FileExistsError('Preserve earlier sync evidence')
    old=[{'path':p.relative_to(pub).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for base in ('docs','outputs') for p in (pub/base).rglob('*.zip') if eligible(p)]
    dump(EVIDENCE/'public-before-zip-hashes.json',old)
    folders=['skills/voltpeer-plot','examples/recipe_packs','examples/plot_starter','scripts/starter','docs/assets/cycling-rule-v1.2.0','docs/assets/cycling-rule-v1.2.1','docs/downloads/v0.12.0-cycling-rule-v1.2.1']
    folders += ['examples/showcase/'+s for s in IDS]
    folders += ['examples/domain_showcase/'+s for s in DOMAIN]
    files=['examples/showcase/build.py','examples/paper_renderer.py','examples/paper_models.py','examples/science_renderer_20261003.py','examples/science_models_20261003.py','examples/science_references_20261003.py','examples/series_policy.py','examples/resource_demos.py','examples/domain_component_renderer.py','examples/demo_bundle_runner.py','examples/frontpage/render.py','examples/frontpage/series_policy.py','skills/voltpeer-assemble/references/shared/voltpeer-plot/references/PLOT_QA_CHECKLIST.md','docs/assets/cycling-rule-v1.0.0/CYCLING_REVISION.json','docs/assets/cycling-rule-v1.0.0/skill-downloads.json']
    files += ['scripts/'+s for s in ('package_release.py','package_workbuddy.py','package_recipe_packs.py','package_plot_starter.py','package_demo_bundles.py','build_paper_examples.py','build_science_expansion_20261003.py','verify_science_expansion_20261003.py','revise_cycling_science_20261003.py','finish_cycling_delivery_20261003.py','promote_cycling_delivery_20261003.py','verify_cycling_revision_20261003.py','check_current_full_cell_delivery_20261003.py','verify_distribution.py','sync_cycling_public_mirror_20261003.py')]
    # All ten domain standalone generators use the same current policy.
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'examples/domain_showcase').glob('*/render.py')]
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'examples/domain_showcase').glob('*/series_policy.py')]
    paths={ROOT/f for f in files}
    for folder in folders:paths.update(p for p in (ROOT/folder).rglob('*') if eligible(p))
    changes=[];same=0
    for source in sorted(paths):
        if not eligible(source):raise FileNotFoundError(str(source))
        rel=source.relative_to(ROOT);target=pub/rel
        if target.exists() and sha(source)==sha(target):same+=1;continue
        if target.exists() and target.suffix in ('.zip','.csv'):raise ValueError('Immutable/archive or original CSV differs: '+str(target))
        before=None
        if target.exists():
            before=sha(target);backup=EVIDENCE/'public-mirror-before-files'/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        if sha(source)!=sha(target):raise ValueError('Public mirror byte mismatch '+str(rel))
        changes.append({'path':rel.as_posix(),'previous_sha256':before,'current_sha256':sha(target),'bytes':target.stat().st_size})
    bad=[r['path'] for r in old if not (pub/r['path']).is_file() or sha(pub/r['path'])!=r['sha256']]
    report={'status':'PASS' if not bad else 'FAIL','failed':len(bad),'scope':'Owned scientific sources, final new assets and current download pointer only. Existing different source files saved under internal before-files evidence. Historical public ZIPs never overwritten.',
      'public_root':str(pub),'mirrored_file_count':len(paths),'changed_or_added':changes,'already_equal':same,'historical_zip_count':len(old),'historical_zip_changes':bad,'pushed':'NOT_PUSHED'}
    dump(EVIDENCE/'public-mirror-sync.json',report)
    print(json.dumps({'status':report['status'],'mirrored':len(paths),'old_public_zip_count':len(old),'historical_zip_changes':bad},ensure_ascii=False))
    if bad:raise ValueError('Historical public ZIP byte change')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--public-root',type=Path,required=True);a=p.parse_args();main(a.public_root.resolve())
