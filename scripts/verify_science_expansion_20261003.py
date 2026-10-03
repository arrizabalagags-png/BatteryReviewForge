"""Science/closure QA and actual source+CSV replay of every new example.

Model checks are bounded numerical/physical identities. This is neither an
author-data validation nor a claim that synthetic examples establish mechanisms.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'examples'))
from science_models_20261003 import catalogue,F,R,T,KB,EPS0,stress_equilibrium_shift
sys.path.insert(0,str(ROOT/'scripts'))
from check_demo_metadata import validate_metadata

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def verify(output,replay=True,replay_subdir='replayed'):
    output=output.resolve();models=catalogue();results=[]
    runner=load_module('science_bundle_replay',ROOT/'examples/demo_bundle_runner.py')
    for index,m in enumerate(models):
        slug='science_'+m.ident;folder=output/'showcase'/slug
        meta=validate_metadata(json.loads((folder/'metadata.json').read_text(encoding='utf-8')))
        config=json.loads((folder/'model.json').read_text(encoding='utf-8'))
        with (folder/'data.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        xx=np.array([float(r['x']) for r in rows]);yy=np.array([float(r['y']) for r in rows])
        basis=meta['scientific_basis'];checks={
            'complete_rows':len(rows)==len(m.rows),'finite':bool(np.all(np.isfinite(xx)) and np.all(np.isfinite(yy))),
            'exact_declared_axis_units':config['panels']==m.panels,
            'parameters_and_boundary_present':bool(basis['parameters'] and basis['assumptions'] and basis['limitations']),
            'source_method_scope_present':bool(basis['references'][0]['url'].startswith('https://') and basis['references'][0]['supports'] and basis['references'][0]['figure_panel']),
            'no_experimental_claim':meta['data_status']=='synthetic_demo' and meta['not_experimental_data'] is True,
            'all_four_spines':all(all(a['spines'].values()) for a in meta['data_frame_checks']),
            'declared_sampling_artists':all(
                (a['line_style'] in ('None','',' ') and a['marker'] not in (None,'None','',' ')) if a.get('sampling')=='cycle_scatter'
                else (a['line_style']=='-' and a['marker'] in (None,'None','',' '))
                for a in meta['continuous_curve_style_checks'])}
        if basis['validation']['nonnegative']:checks['declared_nonnegative_response']=bool(np.min(yy)>=-1e-10)
        if basis['validation']['unit_interval']:checks['declared_probability_or_fraction_bounds']=bool(np.min(yy)>=-1e-10 and np.max(yy)<=1+1e-10)
        if m.panels[0]['yscale']=='log':checks['positive_log_domain']=bool(np.min(yy)>0)
        report=json.loads((folder/'render-report.json').read_text(encoding='utf-8'))
        checks['actual_text_bounds']=not report['text_bbox_outside'] and not report['title_legend_overlap']
        with Image.open(folder/'figure.png') as image:checks['png_readable_dimensions']=image.width>=1200 and image.height>=900
        checks['svg_vector_text']=b'<text' in (folder/'figure.svg').read_bytes()
        checks['pdf_header']=(folder/'figure.pdf').read_bytes().startswith(b'%PDF-')
        archive=output/f'BRF-demo-{slug}.zip'
        with zipfile.ZipFile(archive) as z:
            manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
            checks['manifest_hash_closure']=all(hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256'] for r in manifest['files'])
            checks['source_manifest_closure']=all(hashlib.sha256(z.read(r['archive_path'])).hexdigest()==r['sha256'] for r in manifest['code'])
            checks['input_manifest_closure']=all(hashlib.sha256(z.read(r['archive_path'])).hexdigest()==r['sha256'] for r in manifest['inputs'])
        # Selected independent physical limiting identities complement the
        # per-record equation/unit/boundary contract checks above.
        groups={s:np.array([(float(r['x']),float(r['y'])) for r in rows if r['series']==s]) for s in dict.fromkeys(r['series'] for r in rows)}
        first=next(iter(groups.values()))
        if m.ident=='np_inventory':checks['electrode_inventory_bound']=bool(np.max(yy)<=3+1e-12)
        if m.ident=='porosity_volumetric':checks['active_binder_pore_sum']=bool(np.allclose(first[:,1]/(4.5*180)+first[:,0]+.05,1))
        if m.ident=='stoichiometric_window':checks['one_electron_faradaic_endpoint']=bool(np.isclose(first[-1,1]*3.6*100,F))
        if m.ident=='exchange_site_occupation':checks['reactant_vacancy_symmetry']=bool(np.allclose(first[:,1],first[::-1,1]))
        if m.ident=='kinetic_transport_limit':checks['current_cannot_exceed_limit']=bool(np.max(groups['Transport-limited'][:,1])<20)
        if m.ident=='fick_flux_gradient':checks['diffusion_down_gradient']=bool(np.all(first[:,0]*first[:,1]<=0))
        if m.ident=='migration_field_flux':checks['opposite_valence_opposite_flux']=bool(np.allclose(groups['Monovalent cation'][:,1],-groups['Monovalent anion'][:,1]))
        if m.ident=='advection_diffusion_ratio':checks['flux_scale_fraction_sum']=bool(np.allclose(sum(v[:,1] for v in groups.values()),1))
        if m.ident=='debye_screening_length':checks['screening_concentration_invariant']=bool(np.ptp(first[:,1]**2*first[:,0])<1e-10)
        if m.ident in ('sphere_diffusion_uptake','slab_diffusion_uptake'):checks['monotonic_fixed_boundary_uptake']=bool(np.all(np.diff(first[:,1])>=0))
        if m.ident=='joule_current_heat':checks['heat_even_and_nonnegative']=bool(np.allclose(first[:,1],first[::-1,1]) and np.min(first[:,1])>=0)
        if m.ident=='entropy_soc_heat':checks['charge_discharge_heat_sign_reversal']=bool(np.allclose(sum(v[:,1] for v in groups.values()),0))
        if m.ident=='slab_internal_heating':checks['equal_temperature_faces']=bool(np.allclose(first[[0,-1],1],0))
        if m.ident=='cylinder_radial_heat':checks['fixed_sidewall_temperature']=bool(np.isclose(first[-1,1],0))
        if m.ident=='guinier_radius':checks['guinier_low_q_only']=bool(np.sqrt(np.max(xx))*16<1)
        if m.ident=='q_realspace_scale':checks['reciprocal_period_identity']=bool(np.allclose(first[:,0]*first[:,1],2*np.pi))
        if m.ident=='nmr_longitudinal_recovery':checks['initial_saturation_zero']=all(np.isclose(v[0,1],0) for v in groups.values())
        if m.ident in ('nmr_transverse_echo','pfg_diffusion_attenuation'):checks['initial_signal_unity']=all(np.isclose(v[0,1],1) for v in groups.values())
        if m.ident=='xps_sensitivity_normalization':checks['calibrated_fraction_recovered']=bool(np.allclose(groups['Sensitivity-corrected'][:,0],groups['Sensitivity-corrected'][:,1]))
        if m.ident=='competitive_coordination':checks['site_conservation']=bool(np.allclose(sum(v[:,1] for v in groups.values()),1))
        if m.ident=='boltzmann_two_states':checks['thermal_population_conservation']=bool(np.allclose(sum(v[:,1] for v in groups.values()),1))
        if m.ident=='parasitic_charge_ledger':checks['inventory_conservation']=bool(np.allclose(sum(v[:,1] for v in groups.values()),1000))
        if m.ident=='sphere_diffusion_stress':checks['traction_free_surface']=bool(np.isclose(groups['Radial'][-1,1],0));checks['center_radial_tangential_equal']=bool(np.isclose(groups['Radial'][0,1],groups['Tangential'][0,1]))
        if m.ident=='stress_potential_coupling':
            # Independent thermodynamic contract from Sethuraman Eq. 1/14:
            # positive tensile stress decreases inserted-Li chemical potential.
            omega=float(basis['parameters']['Omega_m3_mol']);sigma=first[:,0]*1e6
            chemical_shift=-omega*sigma
            checks['tensile_positive_equilibrium_shift']=bool(np.all(first[first[:,0]>0,1]>0))
            checks['compressive_negative_equilibrium_shift']=bool(np.any(first[:,0]<0) and np.all(first[first[:,0]<0,1]<0))
            checks['fixed_composition_chemical_potential_balance']=bool(np.allclose(F*first[:,1]/1000+chemical_shift,0,atol=1e-10))
            checks['stress_free_zero_shift']=bool(np.any(first[:,0]==0) and np.all(first[first[:,0]==0,1]==0))
            checks['odd_stress_response']=bool(np.allclose(first[:,0],-first[::-1,0]) and np.allclose(first[:,1],-first[::-1,1]))
            checks['zero_partial_volume_limit']=bool(np.all(stress_equilibrium_shift(first[:,0],0.0)==0))
            checks['independently_recovered_partial_volume']=bool(np.isclose(F*(first[-1,1]-first[0,1])/1000/(sigma[-1]-sigma[0]),omega))
            checks['source_exact_stress_sign_equations']=basis['references'][0]['doi']=='10.1149/1.3489378' and 'Eq. 1' in basis['references'][0]['figure_panel'] and '14' in basis['references'][0]['figure_panel']
        if m.ident=='charge_quadrature_convergence':checks['integration_error_decreases']=bool(first[-1,1]<first[0,1]/100)
        if m.ident=='ce_correlated_uncertainty':checks['shared_error_reduces_ratio_uncertainty']=bool(first[-1,1]<first[0,1])
        if m.ident=='student_coverage_factor':checks['finite_sample_coverage_above_normal']=bool(np.all(groups['Student t'][:,1]>1.95996398454))
        if not all(checks.values()):raise ValueError('Failed scientific/closure QA '+slug+': '+str([k for k,v in checks.items() if not v]))
        before=sha(folder/'data.csv');replay_record=None
        if replay:
            with tempfile.TemporaryDirectory(prefix='voltpeer-science-components-') as tmp:
                bundle=Path(tmp)
                for kind in ('source','data'):
                    with zipfile.ZipFile(output/'split-demos'/slug/f'{slug}-{kind}.zip') as z:z.extractall(bundle)
                runner.BUNDLE=bundle
                target=(output/replay_subdir/slug).resolve()
                if not target.is_relative_to(output):raise ValueError('Unsafe replay path')
                result=runner.redraw(target)
                run=json.loads((target/'RUN_RECORD.json').read_text(encoding='utf-8'))
                checks['source_csv_actual_redraw']=result['status']=='redrawn' and run['regenerated_inputs'] is False and run['original_inputs_written'] is False
                checks['redraw_preserves_provenance']=run['changed_from_demo'] is False and run['data_scope']=='original_synthetic_teaching_model'
                checks['original_csv_unchanged']=sha(folder/'data.csv')==before
                replay_record=dict(run_record=str((target/'RUN_RECORD.json').relative_to(output)),sha256=sha(target/'RUN_RECORD.json'))
        if not all(checks.values()):raise ValueError('Replay QA failed '+slug)
        results.append(dict(id=slug,title=m.zh,relationship=basis['relationship'],equation=basis['equations'][0],checks=checks,reference=basis['references'][0],replay=replay_record))
        print(f'QA {index+1:03d}/100 {slug}',flush=True)
    # Five pages of independently rendered thumbnails make actual inspection
    # manageable; original full-resolution plots remain alongside them.
    for page in range(5):
        sheet=Image.new('RGB',(1920,1900),'#ffffff');d=ImageDraw.Draw(sheet)
        for n,m in enumerate(models[page*20:(page+1)*20]):
            with Image.open(output/'showcase'/('science_'+m.ident)/'figure.png') as src:
                src.thumbnail((465,340));x=(n%4)*480+(480-src.width)//2;y=(n//4)*380
                sheet.paste(src,(x,y));d.text(((n%4)*480+8,y+342),f'{page*20+n+1:03d} {m.ident}',fill='#172c40')
        sheet.save(output/f'contact-sheet-{page+1:02d}.png')
    report=dict(status='PASS',examples=len(results),checks=sum(len(r['checks']) for r in results),all_100_actual_source_csv_replayed=replay,
        scope='Original analytic teaching model, source method/equation scope, numerical physical boundaries, actual artist/readability, component ZIP hash closure and unchanged-input replay; no experimental validation.',
        results=results)
    dump(output/'science-qa-20261003.json',report);return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-root',type=Path,default=ROOT.parent/'deployment/evidence/2026-10-03/science-expansion/generated');p.add_argument('--no-replay',action='store_true');p.add_argument('--replay-subdir',default='replayed')
    a=p.parse_args();verify(a.output_root,not a.no_replay,a.replay_subdir)
