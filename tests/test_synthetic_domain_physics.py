"""Physical identities of 22 ORIGINAL teaching models, never experimental QA.

The fixtures are generated in a temporary directory. Nothing served or packaged
is rewritten by these tests. --report writes the actual checks and input hashes.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_demo_metadata import validate_metadata


def load(name,relative):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def csv_rows(path):
    with path.open(encoding='utf-8',newline='') as handle:
        return list(csv.DictReader(handle))


def column(rows,key):
    return np.array([float(r[key]) for r in rows])


def integral(y,x):
    function=getattr(np,'trapezoid',None)
    return float((function if function is not None else np.trapz)(y,x))


class SyntheticDomainPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.advanced=load('scientific_advanced','examples/showcase/advanced.py')
        cls.corpus=load('scientific_corpus','examples/showcase/corpus.py')
        cls.domains=load('scientific_domains','examples/resource_demos.py')
        cls.temp=tempfile.TemporaryDirectory(prefix='voltpeer-domain-physics-')
        cls.base=Path(cls.temp.name)
        cls.showcase=cls.base/'showcase'; cls.domain_output=cls.base/'domain'
        cls.checks=[]
        cls.recipes={}
        for module,names in [(cls.advanced,cls.advanced.RECIPES),(cls.corpus,cls.corpus.CORPUS_RECIPES)]:
            for name in names:
                module.generate(name,cls.showcase)
                module.render(name,cls.showcase)
                cls.recipes[name]=cls.showcase/name
        subprocess.run([sys.executable,str(ROOT/'examples/resource_demos.py'),'--output',str(cls.domain_output)],
                       check=True,capture_output=True,text=True,encoding='utf-8')
        cls.recipes.update({r[0]:cls.domain_output/r[0] for r in cls.domains.RECIPES})

    @classmethod
    def tearDownClass(cls):
        report=os.environ.get('VOLTPEER_DOMAIN_REPORT')
        if report:
            path=Path(report); path.parent.mkdir(parents=True,exist_ok=True)
            sources=['examples/showcase/advanced.py','examples/showcase/corpus.py','examples/resource_demos.py',
                     'tests/test_synthetic_domain_physics.py']
            payload={'schema_version':1,'date':'2026-10-01','scope':'Declared original synthetic models and physical identities only; not experimental/material/mechanistic certification.',
                     'status':'FAIL' if any(c['status']=='FAIL' for c in cls.checks) else 'PASS',
                     'recipes':22,'checks':cls.checks,
                     'generator_sha256':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},
                     'fixture_sha256':{name:{str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir()) if p.suffix in ('.csv','.json')}
                                       for name,folder in cls.recipes.items()},
                     'not_run':['Human scientific/material review','Experimental replication','New model/host behavior EVAL','DSC/TGA/EQE: no such resource is part of these 22 examples']}
            path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        cls.temp.cleanup(); plt.close('all')

    @contextlib.contextmanager
    def checked(self,recipe,assertion):
        record={'recipe':recipe,'assertion':assertion,'status':'PASS'}
        try:
            yield record
        except Exception as error:
            record.update(status='FAIL',error=f'{type(error).__name__}: {error}')
            raise
        finally:
            self.checks.append(record)

    def rows(self,name,file='data.csv'):
        return csv_rows(self.recipes[name]/file)

    def meta(self,name):
        return json.loads((self.recipes[name]/'metadata.json').read_text(encoding='utf-8'))

    def test_01_all_metadata_scope_sources_and_frame_checks(self):
        for name,folder in self.recipes.items():
            with self.subTest(recipe=name),self.checked(name,'Metadata schema, original provenance, declared units/conditions, source closure and actual four-sided data frames') as record:
                meta=self.meta(name); validate_metadata(meta)
                basis=meta['scientific_basis']
                self.assertEqual(basis['data_origin'],'original_synthetic')
                self.assertTrue(basis['equations'] and basis['assumptions'] and basis['limitations'])
                for reference in basis['references']:
                    self.assertEqual(reference['scope'],'model_definition_only')
                self.assertTrue(all((folder/file).is_file() for file in meta['source_files']))
                self.assertTrue(all((folder/f'figure.{fmt}').stat().st_size>1000 for fmt in ('png','svg','pdf')))
                checks=meta['actual_artist_checks']
                panels=checks.get('data_frame_checks',[]) if isinstance(checks,dict) else checks
                self.assertTrue(panels)
                for panel in panels:
                    frame=panel.get('frame_spines',panel.get('spines',{}))
                    self.assertEqual(set(frame),{'top','right','bottom','left'})
                    self.assertTrue(all(frame.values()))
                record.update(model_class=basis['model_class'],source_files=meta['source_files'])

    def test_02_cv_order_and_honest_model_scope(self):
        with self.checked('cyclic_voltammetry','Triangular acquisition order, both current branches and explicitly phenomenological non-kinetic scope'):
            rows=self.rows('cyclic_voltammetry')
            for rate in {r['scan_rate_mV_s'] for r in rows}:
                group=[r for r in rows if r['scan_rate_mV_s']==rate]
                v=column(group,'voltage_V'); current=column(group,'current_mA')
                self.assertTrue(np.all(np.diff(v[:400])>0) and np.all(np.diff(v[399:])<0))
                self.assertAlmostEqual(v[0],v[-1]); self.assertTrue(current.max()>0 and current.min()<0)
            self.assertEqual(self.meta('cyclic_voltammetry')['scientific_basis']['model_class'],'phenomenological_model')
            self.assertIn('not a diffusion solution',' '.join(self.meta('cyclic_voltammetry')['scientific_basis']['assumptions']))

    def test_03_differential_capacity_integral(self):
        with self.checked('differential_capacity','Integral of the same-branch finite-difference dQ/dV recalls charge capacity; no branch mixing') as record:
            rows=self.rows('differential_capacity'); errors=[]
            for cycle in {r['cycle'] for r in rows}:
                group=[r for r in rows if r['cycle']==cycle]
                v=column(group,'voltage_V'); q=column(group,'capacity_mAh_g')
                self.assertTrue(np.all(np.diff(q)>0) and q[0]==0)
                area=integral(np.gradient(q,v,edge_order=2),v)
                errors.append(abs(area-(q[-1]-q[0])))
            self.assertLess(max(errors),0.001)
            record['max_capacity_recall_error_mAh_g']=max(errors)

    def test_04_gitt_charge_and_rc_state(self):
        with self.checked('gitt_pulse','Twelve 6-min pulses/24-min rests, 0.12 mAh integration and one continuous RC state through switching') as record:
            rows=self.rows('gitt_pulse'); t=column(rows,'time_min'); i=column(rows,'current_mA')
            q=column(rows,'passed_charge_mAh'); u=column(rows,'rc_polarization_V')
            v=column(rows,'voltage_V'); ocv=column(rows,'equilibrium_model_V')
            passed=np.sum(i[:-1]*np.diff(t))/60
            self.assertAlmostEqual(passed,.12,places=11); self.assertAlmostEqual(q[-1],passed,places=11)
            self.assertTrue(np.all(np.diff(q)>=-1e-12))
            starts=np.sum((i[1:]>0)&(i[:-1]==0))+int(i[0]>0); self.assertEqual(starts,12)
            np.testing.assert_allclose(v-ocv,u+340*i/1000,atol=1e-12)
            dt=np.diff(t)*60; decay=np.exp(-dt/300)
            np.testing.assert_allclose(u[1:],u[:-1]*decay+850*i[:-1]/1000*(1-decay),rtol=1e-12,atol=1e-12)
            off=np.flatnonzero((i[1:]==0)&(i[:-1]>0))+1
            self.assertTrue(np.all(u[off]>0))
            record.update(pulses=int(starts),integrated_charge_mAh=float(passed))

    def test_05_arrhenius_units_and_input_energy(self):
        with self.checked('ionic_conductivity','Known Arrhenius input activation energies recalled with kelvin and mS→S conversion') as record:
            rows=self.rows('ionic_conductivity'); recalled={}
            for sample,ea in self.meta('ionic_conductivity')['scientific_basis']['parameters']['activation_energy_eV'].items():
                group=[r for r in rows if r['sample']==sample]
                t=column(group,'temperature_C')+273.15; sigma=column(group,'conductivity_mS_cm')/1000
                self.assertTrue(np.all(sigma>0) and np.all(np.diff(sigma)>0))
                slope=np.polyfit(1/t,np.log(sigma),1)[0]
                recalled[sample]=float(-slope*8.617333262e-5)
                self.assertAlmostEqual(recalled[sample],ea,places=10)
            record['input_energy_recall_eV']=recalled

    def test_06_xps_components_are_known_not_fit(self):
        with self.checked('xps_components','Nonnegative integer photon counts and known-component expectation; residual is counting noise, no chemical fit') as record:
            rows=self.rows('xps_components'); observed=column(rows,'intensity_counts'); expected=column(rows,'expected_counts')
            parts=sum(column(rows,k) for k in ('background_counts','component_1','component_2','component_3'))
            np.testing.assert_allclose(expected,parts,rtol=1e-12)
            self.assertTrue(np.all(observed>=0) and np.all(observed==np.floor(observed)))
            ratio=float(np.mean((observed-expected)**2)/np.mean(expected))
            self.assertTrue(.5<ratio<1.6)
            self.assertIn('no optimizer',self.meta('xps_components')['render_options']['fit_method'])
            record['poisson_mean_square_residual_over_mean_counts']=ratio

    def test_07_raman_keeps_generic_positive_bands(self):
        with self.checked('raman_series','Positive same-scale generic Raman intensities; display offset has no molecular/concentration assignment'):
            rows=self.rows('raman_series'); self.assertTrue(np.all(column(rows,'intensity_counts')>0))
            self.assertIn('No molecule',' '.join(self.meta('raman_series')['scientific_basis']['limitations']))

    def test_08_beer_lambert_transmission(self):
        with self.checked('ftir','Stored absorbance independently recalls -log10(T/100), with 0<T<=100') as record:
            rows=self.rows('ftir'); transmission=column(rows,'transmittance_percent'); absorbance=column(rows,'absorbance')
            self.assertTrue(np.all((transmission>0)&(transmission<=100)) and np.all(absorbance>=0))
            error=float(np.max(np.abs(-np.log10(transmission/100)-absorbance)))
            self.assertLess(error,1e-12); record['max_absorbance_recall_error']=error

    def test_09_nmr_generic_lorentzian_scope(self):
        with self.checked('nmr','Generic nonnegative Lorentzian bands with explicit ppm reference and no molecular/T2 assignment'):
            self.assertTrue(np.all(column(self.rows('nmr'),'intensity_au')>=0))
            self.assertTrue(self.meta('nmr')['render_options']['chemical_shift_reference'])
            self.assertIn('T2',' '.join(self.meta('nmr')['scientific_basis']['limitations']))

    def test_10_rdf_coordination_integral_and_exclusion(self):
        with self.checked('rdf_coordination','CN independently recalls 4πrho integral(r²gdr); nonnegative/excluded short range and g→1') as record:
            rows=self.rows('rdf_coordination'); density=self.meta('rdf_coordination')['render_options']['pair_number_density_A3']; errors=[]
            for pair,rho in density.items():
                group=[r for r in rows if r['pair']==pair]; r=column(group,'distance_A'); g=column(group,'g_r'); cn=column(group,'coordination_number')
                self.assertTrue(np.all(g>=0) and np.all(g[r<1.4]==0)); self.assertAlmostEqual(g[-1],1,delta=.02)
                self.assertTrue(np.all(np.diff(cn)>=0))
                errors.append(abs(cn[-1]-4*np.pi*rho*integral(r*r*g,r)))
            self.assertLess(max(errors),1e-10); record['max_coordination_recall_error']=max(errors)

    def test_11_three_dimensional_msd(self):
        with self.checked('msd','3D drift-free Brownian MSD=6Dt and Å²/ps→cm²/s; input D is not a fitted/MD result') as record:
            rows=self.rows('msd'); input_values={}
            for temp in (25,-70):
                for sample in ('A','B','C'):
                    group=[r for r in rows if float(r['temperature_C'])==temp and r['electrolyte']==sample]
                    t=column(group,'time_ps'); y=column(group,'msd_A2'); d=column(group,'input_diffusivity_A2_ps')
                    self.assertTrue(np.all(d>0) and y[0]==0); np.testing.assert_allclose(y[1:]/t[1:],6*d[1:],rtol=1e-12)
                    recalled=np.polyfit(t,y,1)[0]/6; self.assertAlmostEqual(recalled,d[0],places=12)
                    input_values[f'{temp}/{sample}']=float(recalled*1e-4)
            self.assertLess(input_values['-70/A'],input_values['25/A'])
            record['known_D_recall_cm2_s']=input_values

    def test_12_lsv_anodic_exponential_scope(self):
        with self.checked('lsv','Forward anodic log-current slope uses declared temperature/transfer coefficient; no decomposition-onset inference'):
            rows=self.rows('lsv')
            for sample in ('A','B','C'):
                group=[r for r in rows if r['electrolyte']==sample]
                v=column(group,'voltage_V'); j=column(group,'current_density_uA_cm2')
                self.assertTrue(np.all(np.diff(j)>0))
                slope=np.polyfit(v,np.log(j-.08),1)[0]
                self.assertAlmostEqual(slope,.15*96485.33212/(8.314462618*298.15),places=8)

    def test_13_transference_current_units_and_rc(self):
        with self.checked('transference','Frequency-derived RC complex impedances and resistance-corrected apparent t_BV using A, not mA') as record:
            meta=self.meta('transference'); parameters=meta['render_options']['known_parameters']; rows=self.rows('transference','eis.csv'); results={}
            for sample,known in parameters.items():
                i0=known['initial_current_mA']/1000; iss=known['steady_current_mA']/1000; dv=known['polarization_voltage_V']
                r0=known['initial_resistance_ohm']; rss=known['steady_resistance_ohm']
                value=iss*(dv-i0*r0)/(i0*(dv-iss*rss)); self.assertTrue(0<value<1); self.assertNotAlmostEqual(value,iss/i0)
                results[sample]=value
                rs=meta['scientific_basis']['parameters']['series_R_ohm'][sample]
                for stage,resistance in [('before',r0),('after',rss)]:
                    group=[r for r in rows if r['electrolyte']==sample and r['stage']==stage]
                    real=column(group,'z_real_ohm')-rs; imag=column(group,'z_imag_negative_ohm')
                    frequency=column(group,'frequency_Hz')
                    # The parallel-RC semicircle identity is independent of how
                    # the complex impedance generator is evaluated.
                    np.testing.assert_allclose((real-resistance/2)**2+imag**2,(resistance/2)**2,rtol=1e-10)
                    self.assertTrue(np.all(np.diff(frequency)<0) and np.all(imag>=0))
            record['apparent_t_BV_model_values']=results

    def test_14_na_zn_ce_charge_ledgers(self):
        for name in ('na_metal_ce','zn_plating_ce'):
            with self.checked(name,'Positive strip/plating charge ledger, bounded teaching loss and full-cell-life interpretation explicitly excluded') as record:
                rows=self.rows(name); qin=column(rows,'q_plating_mAh_cm2'); qout=column(rows,'q_stripping_mAh_cm2'); ce=column(rows,'ce_percent')
                self.assertTrue(np.all(qin>0) and np.all((qout>=0)&(qout<=qin)))
                np.testing.assert_allclose(ce,100*qout/qin,rtol=1e-12)
                record.update(CE_min_percent=float(ce.min()),CE_max_percent=float(ce.max()))

    def test_15_potassium_rate_and_recovery(self):
        with self.checked('k_ion_rate','Rate steps reduce accessible capacity, recovery at original current respects independent active-capacity loss') as record:
            rows=self.rows('k_ion_rate'); q=column(rows,'capacity_mAh_g'); current=column(rows,'current_mA_g')
            groups=[float(np.mean(q[i:i+10])) for i in range(0,60,10)]
            self.assertTrue(all(a>b for a,b in zip(groups[:4],groups[1:5])))
            self.assertTrue(groups[4]<groups[5]<groups[0]); self.assertTrue(current[0]==current[-1]==50)
            self.assertTrue(np.all((q>0)&(q<=260))); record['rate_step_capacity_means_mAh_g']=groups

    def test_16_zinc_symmetric_two_terminal_voltage(self):
        with self.checked('zn_symmetric','Cell-voltage/current signs, exact 1-hour half-cycle schedule and area charge; no single-electrode interpretation'):
            rows=self.rows('zn_symmetric'); t=column(rows,'time_h'); v=column(rows,'cell_voltage_mV'); j=column(rows,'current_density_mA_cm2')
            np.testing.assert_array_equal(np.sign(v),np.sign(j)); np.testing.assert_array_equal(abs(j),np.ones_like(j))
            self.assertTrue(np.all(np.diff(t)>0))
            halves=column(rows,'half_cycle'); self.assertTrue(np.all(halves==np.floor(t)))
            self.assertIn('two-terminal',' '.join(self.meta('zn_symmetric')['scientific_basis']['assumptions']).lower())

    def test_17_zinc_air_power(self):
        with self.checked('zn_air_power','Delivered areal power recalls jV in mW/cm²; voltage decreases, power maximum is interior and positive') as record:
            rows=self.rows('zn_air_power'); j=column(rows,'current_density_mA_cm2'); v=column(rows,'voltage_V'); p=column(rows,'power_density_mW_cm2')
            np.testing.assert_allclose(p,j*v,rtol=1e-12); self.assertTrue(np.all(v>0) and np.all(np.diff(v)<0))
            index=int(np.argmax(p)); self.assertTrue(0<index<len(p)-1)
            record.update(model_Pmax_mW_cm2=float(p[index]),current_at_sampled_Pmax_mA_cm2=float(j[index]))

    def test_18_iodine_theory_and_charge_ledger(self):
        with self.checked('zn_i2_cycle','Iodine-only I2+2e→2I− theoretical bound and CE=Qdis/Qchg; excludes four-electron/carbon contributions') as record:
            rows=self.rows('zn_i2_cycle'); q=column(rows,'capacity_mAh_g_iodine'); charge=column(rows,'charge_capacity_mAh_g_iodine'); ce=column(rows,'ce_percent')
            theoretical=2*96485.33212/(3.6*253.80894)
            self.assertTrue(np.all(q>0) and np.all(q<=theoretical) and np.all(charge<=theoretical))
            np.testing.assert_allclose(ce,100*q/charge,rtol=1e-12)
            record.update(theoretical_mAh_g_I2=theoretical,max_discharge_mAh_g_I2=float(q.max()))

    def test_19_flow_capacity_weighted_energy(self):
        with self.checked('flow_efficiency','All 150 complete V(Q) branches independently recall capacity-weighted voltages, energy and CE×VE=EE without pump energy') as record:
            rows=self.rows('flow_efficiency'); traces=self.rows('flow_efficiency','cycle_profiles.csv'); error=0
            for entry in rows:
                cycle=float(entry['cycle']); energy={}; capacity={}
                for branch in ('charge','discharge'):
                    group=[r for r in traces if float(r['cycle'])==cycle and r['branch']==branch]
                    q=column(group,'branch_capacity_mAh'); v=column(group,'voltage_V')
                    self.assertEqual(q[0],0); self.assertTrue(np.all(np.diff(q)>0) and np.all(v>0))
                    energy[branch]=integral(v,q); capacity[branch]=q[-1]
                    error=max(error,abs(energy[branch]-float(entry[branch+'_energy_mWh'])))
                ce=100*capacity['discharge']/capacity['charge']
                ve=100*(energy['discharge']/capacity['discharge'])/(energy['charge']/capacity['charge'])
                ee=100*energy['discharge']/energy['charge']
                self.assertAlmostEqual(ce,float(entry['ce_percent']),places=10)
                self.assertAlmostEqual(ve,float(entry['ve_percent']),places=10)
                self.assertAlmostEqual(ee,float(entry['ee_percent']),places=10)
                self.assertAlmostEqual(ee,ce*ve/100,places=10)
            self.assertLess(error,1e-10); record['max_branch_energy_recall_error_mWh']=error

    def test_20_pv_single_diode_and_quadrants(self):
        with self.checked('pv_jv','Ideal single-diode governing equation, Voc zero, Jsc positive, valid generating-quadrant MPP/FF and model efficiency') as record:
            rows=self.rows('pv_jv'); v=column(rows,'voltage_V'); j=column(rows,'current_density_mA_cm2'); power=column(rows,'power_density_mW_cm2')
            parameters=self.meta('pv_jv')['scientific_basis']['parameters']; metrics=json.loads((self.recipes['pv_jv']/'metrics.json').read_text(encoding='utf-8'))
            a=parameters['ideality_factor']*parameters['kB_J_K']*parameters['temperature_K']/parameters['electron_charge_C']
            # Rearranged diode equation independently exposes the previous
            # ninth-order toy curve even if its p=jV relationship was valid.
            loss=parameters['photocurrent_mA_cm2']-j
            np.testing.assert_allclose(loss,parameters['saturation_current_mA_cm2']*np.expm1(v/a),rtol=1e-10,atol=1e-10)
            self.assertTrue(np.all(np.diff(j)<0) and j[0]>0 and np.any(j<0))
            self.assertAlmostEqual(j[np.argmin(abs(v-metrics['Voc_V']))],0,places=10)
            np.testing.assert_allclose(power,v*j,rtol=1e-12)
            index=int(np.argmax(np.where((v>=0)&(j>=0),power,-np.inf)))
            self.assertAlmostEqual(metrics['Pmax_mW_cm2'],power[index],places=10)
            self.assertTrue(0<metrics['fill_factor']<1 and 0<metrics['model_efficiency_percent']<100)
            self.assertLess(abs(j[index]-v[index]*(parameters['photocurrent_mA_cm2']-j[index]+parameters['saturation_current_mA_cm2'])/a),.8)
            record.update(metrics=metrics)

    def test_21_stability_scope_and_normalization(self):
        with self.checked('pv_stability','Positive normalized fixed-operating-point teaching power, no measured T80/MPP lifetime claim'):
            rows=self.rows('pv_stability'); p=column(rows,'normalized_power')
            self.assertEqual(p[0],1); self.assertTrue(np.all(p>0) and np.all(np.diff(p)<0))
            self.assertIn('No measured T80',' '.join(self.meta('pv_stability')['scientific_basis']['limitations']))

    def test_22_trpl_components_and_known_rates(self):
        with self.checked('pv_trpl','Nonnegative biexponential components plus background; known first-order rates recalled, no fit/IRF/mechanism claim'):
            rows=self.rows('pv_trpl'); t=column(rows,'time_ns'); total=column(rows,'signal_a_u')
            fast=column(rows,'fast_component_a_u'); slow=column(rows,'slow_component_a_u'); background=column(rows,'background_a_u')
            np.testing.assert_allclose(total,fast+slow+background,rtol=1e-12)
            self.assertAlmostEqual(np.polyfit(t,np.log(fast),1)[0],-1/18,places=12)
            self.assertAlmostEqual(np.polyfit(t,np.log(slow),1)[0],-1/90,places=12)
            self.assertTrue(np.all(total>0) and np.all(np.diff(total)<0))

    def test_23_tampered_physical_links_are_rejected(self):
        for name,kind,mutation in [('na_metal_ce','ce',lambda a:a.__setitem__((10,2),a[10,2]*1.1)),
                                   ('zn_i2_cycle','cycling',lambda a:a.__setitem__((10,3),a[10,3]*1.1)),
                                   ('flow_efficiency','efficiency',lambda a:a.__setitem__((10,9),a[10,9]*1.1)),
                                   ('pv_jv','jv',lambda a:(a.__setitem__((10,1),a[10,1]*.9),a.__setitem__((10,2),a[10,0]*a[10,1])))]:
            with self.checked(name,'Tampering with an actual charge/energy/diode relation is rejected, including p=jV-consistent fake PV current'):
                fields,values=self.domains.data(kind,np.random.default_rng(123)); mutation(values)
                with self.assertRaises(ValueError): self.domains.validate_demo(kind,fields,values,fields)
        with self.checked('flow_efficiency','A tampered V(Q) trace is rejected even if summary CE×VE remains unchanged'):
            fields,values=self.domains.data('efficiency',np.random.default_rng(123)); _,traces=self.domains.flow_profiles(values)
            changed=list(traces); cycle,branch,q,v=changed[20]; changed[20]=(cycle,branch,q,v*2)
            with self.assertRaises(ValueError): self.domains.validate_flow_profiles(values,changed)

    def test_24_standalone_cli_replay_and_provenance(self):
        for slug,_,_,_,_ in self.domains.RECIPES:
            with self.checked(slug,'Actual standalone CLI replays the original CSV and retains source closure; no arbitrary-input provenance stamping'):
                original=self.recipes[slug]; output=self.base/'replayed'/slug
                result=subprocess.run([sys.executable,str(original/'render.py'),'--output',str(output),'--recipe',slug,
                                       '--demo-input',str(original/'data.csv')],capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(result.returncode,0,result.stderr)
                rebuilt=output/slug
                self.assertEqual(csv_rows(original/'data.csv'),csv_rows(rebuilt/'data.csv'))
                meta=json.loads((rebuilt/'metadata.json').read_text(encoding='utf-8'))
                self.assertTrue(all((rebuilt/file).is_file() for file in meta['source_files']))
        with self.checked('na_metal_ce','A CE-ratio-consistent but altered numeric CSV is rejected instead of claiming the original teaching model'):
            rows=self.rows('na_metal_ce'); altered=self.base/'altered.csv'
            rows[10]['q_stripping_mAh_cm2']='0.99'; rows[10]['ce_percent']='99'
            with altered.open('w',encoding='utf-8',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
            result=subprocess.run([sys.executable,str(self.recipes['na_metal_ce']/'render.py'),'--output',str(self.base/'rejected'),
                                   '--recipe','na_metal_ce','--demo-input',str(altered)],capture_output=True,text=True,encoding='utf-8')
            self.assertNotEqual(result.returncode,0); self.assertIn('unchanged original numeric CSV',result.stderr)


if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False); parser.add_argument('--report',type=Path)
    args,remainder=parser.parse_known_args()
    if args.report: os.environ['VOLTPEER_DOMAIN_REPORT']=str(args.report)
    unittest.main(argv=[sys.argv[0]]+remainder)
