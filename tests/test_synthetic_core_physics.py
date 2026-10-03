"""Concrete conservation/model checks of original teaching data, not real cells.

All generation/rendering runs in temporary roots. This test never republishes
the gallery or modifies a downloaded historical release. Run this file with
--report PATH to save scoped evidence and exact generator SHA256s.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


CORE = module('voltpeer_core_science', REPO / 'examples/showcase/build.py')
ECHEM = module('voltpeer_optional_science', REPO / 'examples/showcase/electrochem.py')
DEMO = module('voltpeer_pure_demo', REPO / 'examples/recipe_packs/_runtime/generate_demo.py')
PACKAGER = module('voltpeer_recipe_science', REPO / 'scripts/package_recipe_packs.py')
METADATA = module('voltpeer_metadata_science', REPO / 'scripts/check_demo_metadata.py')
SCHEMA = json.loads((REPO / 'docs/DEMO_METADATA_SCHEMA.json').read_text(encoding='utf-8'))


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SyntheticCorePhysicsTests(unittest.TestCase):
    evidence = {}

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='VoltPeer scoped scientific fixtures ')
        cls.root = Path(cls.temp.name)
        cls.original = (CORE.ROOT, ECHEM.ROOT, PACKAGER.ROOT, PACKAGER.PACKS)
        cls.showcase = cls.root / 'examples/showcase'
        cls.showcase.mkdir(parents=True)
        CORE.ROOT = ECHEM.ROOT = cls.showcase
        for name in CORE.GENERATORS:
            (cls.showcase / name).mkdir()
        # Each call explicitly generates a test fixture in the temporary root.
        for name in ('full_cell', 'li_cu_ce', 'li_li', 'eis', 'operando_xrd',
                     'tof_sims', 'rate_capability', 'gcd_profiles', 'pouch_thermal',
                     'literature_benchmark', 'reporting_matrix', 'integrated_study',
                     'capability_spread', 'style_presets'):
            CORE.GENERATORS[name]()
        for name in ECHEM.SOURCES:
            ECHEM.generate(name)
        cls.pack_root = cls.root / 'recipe-fixture'
        shutil.copytree(REPO / 'examples/recipe_packs/_runtime', cls.pack_root / 'examples/recipe_packs/_runtime',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copytree(REPO / 'scripts/runtime_contract', cls.pack_root / 'scripts/runtime_contract',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copy2(REPO / 'LICENSE', cls.pack_root / 'LICENSE')
        PACKAGER.ROOT = cls.pack_root
        PACKAGER.PACKS = cls.pack_root / 'examples/recipe_packs'
        # Source preparation only: no ZIPs, current gallery copies or publication.
        PACKAGER.prepare_sources('0.10.2')

    @classmethod
    def tearDownClass(cls):
        CORE.ROOT, ECHEM.ROOT, PACKAGER.ROOT, PACKAGER.PACKS = cls.original
        cls.temp.cleanup()

    def note(self, **values):
        self.evidence[self._testMethodName] = values

    def test_fullcell_recipe_inventory_and_ce_accounting(self):
        """Two 40-cycle full-cell toy ledgers conserve charge under stated assumptions."""
        rows = read_csv(self.pack_root / 'examples/recipe_packs/full_cell/demo/cycling.csv')
        ce_series = {}
        for sample in sorted({r['sample'] for r in rows}):
            selected = [r for r in rows if r['sample'] == sample]
            self.assertEqual(len(selected), 40)
            initial = 170 if sample.endswith('A') else 164
            product = initial
            for row in selected:
                charge, discharge = float(row['charge_capacity']), float(row['capacity'])
                ce, loss = float(row['ce']), float(row['irreversible_loss'])
                self.assertAlmostEqual(charge, product, places=10)
                self.assertAlmostEqual(100 * discharge / charge, ce, places=10)
                self.assertAlmostEqual(charge - discharge, loss, places=10)
                product *= ce / 100
                self.assertAlmostEqual(product, discharge, places=10)
                self.assertAlmostEqual(float(row['inventory_after']), discharge, places=10)
                self.assertGreater(loss, 0)
            ce_series[sample] = [float(r['ce']) for r in selected]
        self.assertNotEqual(*ce_series.values())
        self.note(cycles_per_sample=40, samples=2, relationship_scope='No excess/compensation; not an author-data acceptance rule')

    def test_halfcell_capacity_does_not_inherit_ce_product(self):
        """Excess-Li half-cell accessible activity and independent CE ledger remain distinct."""
        rows = read_csv(self.showcase / 'full_cell/data.csv')
        for sample in 'AB':
            p = CORE.HALFCELL_PARAMETERS[sample]
            for row in rows:
                n = int(row['cycle'])
                a = ((1 - p['activation_fraction'] * math.exp(-(n - 1)/p['activation_cycles']))
                     * math.exp(-p['fade_per_cycle']*(n - 1)
                                - p['late_fade_per_cycle2']*max(n - p['late_fade_start'], 0)**2))
                q = float(row[f'{sample}_mAh_g'])
                chg = float(row[f'{sample}_charge_mAh_g'])
                self.assertAlmostEqual(q, p['initial_capacity']*a, places=10)
                self.assertAlmostEqual(float(row[f'{sample}_ce_pct']), 100*q/chg, places=10)
                self.assertAlmostEqual(float(row[f'{sample}_loss_mAh_g']), chg-q, places=10)
                self.assertGreater(q, 0)
                self.assertLessEqual(q, p['initial_capacity'])
            ratio = float(rows[-1][f'{sample}_mAh_g'])/float(rows[0][f'{sample}_mAh_g'])
            product = np.prod([float(r[f'{sample}_ce_pct'])/100 for r in rows[1:]])
            self.assertGreater(abs(ratio-product), .05)
        self.assertIn('half-cell', CORE.showcase_scientific_basis('full_cell')['limitations'][-1])
        self.note(cycles_per_sample=500, samples=2, legacy_id='full_cell', actual_configuration='Excess-Li half-cell')

    def test_capacity_voltage_profiles_cover_declared_window(self):
        """Gallery/recipe voltage endpoints match their own capacity ledger and cutoffs."""
        sources = [('full_cell/voltage_profiles.csv', 'cycle', 'capacity_mAh_g', 'voltage_V'),
                   ('gcd_profiles/data.csv', 'cycle', 'capacity_mAh_g', 'voltage_V')]
        cycling = read_csv(self.showcase / 'full_cell/data.csv')
        for filename, cycle_key, qkey, vkey in sources:
            data = read_csv(self.showcase / filename)
            groups = sorted({(r[cycle_key], r.get('direction', 'discharge')) for r in data})
            for cycle, direction in groups:
                series = [r for r in data if r[cycle_key] == cycle and r.get('direction', 'discharge') == direction]
                expected = cycling[int(cycle)-1]['A_charge_mAh_g' if direction == 'charge' else 'A_mAh_g']
                self.assertAlmostEqual(float(series[-1][qkey]), float(expected), places=10)
                self.assertAlmostEqual(float(series[0][vkey]), 2.8 if direction == 'charge' else 4.3, places=10)
                self.assertAlmostEqual(float(series[-1][vkey]), 4.3 if direction == 'charge' else 2.8, places=10)
                self.assertTrue(all(2.8 <= float(r[vkey]) <= 4.3 for r in series))
        demo = read_csv(self.pack_root / 'examples/recipe_packs/full_cell/demo/profiles.csv')
        for key in sorted({(r['sample'], r['cycle']) for r in demo}):
            series = [r for r in demo if (r['sample'], r['cycle']) == key]
            self.assertAlmostEqual(float(series[0]['voltage']), 4.2)
            self.assertAlmostEqual(float(series[-1]['voltage']), 2.9)
        self.note(gallery_window_V=[2.8, 4.3], own_fullcell_recipe_window_V=[2.9, 4.2], no_substitution_between_cell_types=True)

    def test_li_cu_ce_and_true_one_volt_endpoint(self):
        """Li||Cu Qstrip/Qplate, current-time integrals and stored 1 V endpoint agree."""
        cycling = read_csv(self.showcase / 'li_cu_ce/data.csv')
        for row in cycling:
            qplate = float(row['plated_mAh_cm2'])
            for sample in 'AB':
                self.assertAlmostEqual(100*float(row[f'{sample}_stripped_mAh_cm2'])/qplate,
                                       float(row[f'{sample}_ce_pct']), places=10)
                self.assertGreater(float(row[f'{sample}_ce_pct']), 0)
                self.assertLess(float(row[f'{sample}_ce_pct']), 100)
        profiles = read_csv(self.showcase / 'li_cu_ce/profiles.csv')
        for sample, cycle, stage in sorted({(r['sample'], int(r['cycle']), r['stage']) for r in profiles}):
            selected = [r for r in profiles if r['sample']==sample and int(r['cycle'])==cycle and r['stage']==stage]
            final = selected[-1]
            self.assertAlmostEqual(float(final['capacity_mAh_cm2']),
                                   abs(float(final['current_mA_cm2']))*float(final['stage_time_h']), places=10)
            if stage == 'strip':
                self.assertEqual(float(final['voltage_V']), 1.0)
                self.assertAlmostEqual(float(final['capacity_mAh_cm2']),
                                       float(cycling[cycle-1][f'{sample}_stripped_mAh_cm2']), places=10)
        self.note(cycles=300, selected_cycles=[1,100,300], samples=2, stored_strip_cutoff_V=1)

    def test_symmetric_rc_unique_time_continuous_state_and_charge(self):
        """Li||Li terminal RC state is continuous; timestamps and external charge are exact."""
        for sample, p in CORE.SYMMETRIC_PARAMETERS.items():
            rows = DEMO.symmetric_rc_rows(sample, 200, 50, 1, 1, p['Rs_ohm_cm2'], p['Rp_ohm_cm2'], p['tau_h'])
            times = np.array([r['time_h'] for r in rows])
            self.assertTrue(np.all(np.diff(times)>0))
            currents = np.array([r['current_mA_cm2'] for r in rows])
            passed = float(np.sum(currents[:-1]*np.diff(times)))
            self.assertAlmostEqual(passed, rows[-1]['cumulative_signed_mAh_cm2'], places=10)
            self.assertAlmostEqual(times[-1], 200)
            for half in range(1, 200):
                previous_start = rows[(half-1)*50]
                switch = rows[half*50]
                target = previous_start['current_mA_cm2']*p['Rp_ohm_cm2']
                left_state = target + (previous_start['polarization_mV']-target)*math.exp(-1/p['tau_h'])
                self.assertAlmostEqual(switch['polarization_mV'], left_state, places=10)
                self.assertAlmostEqual(switch['voltage_mV']-switch['current_mA_cm2']*p['Rs_ohm_cm2'], left_state, places=10)
                self.assertAlmostEqual(switch['passed_in_half_mAh_cm2'], 0)
        self.note(samples=2, hours=200, trace_rows_per_sample=10001, switching='Voltage IR jump allowed; RC state continuous; current integrated as zero-order hold')

    def test_eis_passive_limits_and_independent_semicircle(self):
        """Randles CPE/Warburg has correct signed impedance and ideal-RC limiting semicircle."""
        f = np.logspace(12, -8, 1000)
        rs, rct, c = 4.2, 23, .00085
        z = CORE.impedance(f, rs, rct, c, 1, 0)
        self.assertAlmostEqual(float(z[0].real), rs, places=8)
        self.assertAlmostEqual(float(z[-1].real), rs+rct, places=8)
        np.testing.assert_allclose((z.real-rs-rct/2)**2+z.imag**2, (rct/2)**2, rtol=1e-12)
        for p in CORE.EIS_PARAMETERS.values():
            z = CORE.impedance(f, p['Rs_ohm'], p['Rct_ohm'], p['CPE_Q'], p['CPE_alpha'], p['Warburg_sigma'])
            self.assertTrue(np.all(z.real>=p['Rs_ohm']))
            self.assertTrue(np.all(z.imag<0))
            self.assertTrue(np.all(np.angle(z)<=0))
            self.assertAlmostEqual(float(z[0].real), p['Rs_ohm'], places=6)
        self.note(frequency_boundary_Hz=[1e-8,1e12], Nyquist_convention='Re Z, -Im Z', CPE_alpha_one_Warburg_zero_limit='Ideal RC semicircle')

    def test_eis_csv_bode_use_same_complex_values(self):
        """Stored EIS real/imaginary data and optional ideal-RC frequency view match analytic circuits."""
        rows = read_csv(self.showcase / 'eis/data.csv')
        for sample,p in CORE.EIS_PARAMETERS.items():
            selected=[r for r in rows if r['sample']==sample]
            freqs=np.array([float(r['frequency_Hz']) for r in selected])
            actual=np.array([complex(float(r['Zreal_ohm']),float(r['Zimag_ohm'])) for r in selected])
            expected=CORE.impedance(freqs,p['Rs_ohm'],p['Rct_ohm'],p['CPE_Q'],p['CPE_alpha'],p['Warburg_sigma'])
            np.testing.assert_allclose(actual, expected, rtol=1e-13, atol=1e-13)
        optional=read_csv(self.showcase/'eis_frequency/data.csv')
        for sample,rs,rct,c in [('A',3.6,22,.0008),('B',4.8,41,.0007)]:
            selected=[r for r in optional if r['sample']==sample]
            f=np.array([float(r['frequency_Hz']) for r in selected])
            z=np.array([complex(float(r['z_real_ohm']),float(r['z_imag_ohm'])) for r in selected])
            np.testing.assert_allclose(z,rs+rct/(1+2j*np.pi*f*rct*c),rtol=1e-13)
        self.note(core_points_per_sample=86, optional_points_per_sample=120, no_independent_drawn_bode_curve=True)

    def test_bragg_angle_and_diffraction_grid(self):
        """First-order Bragg inversion and complete nonnegative peak grids hold in gallery and recipe."""
        for d in (1.9,2.075,2.425,3.2):
            two_theta=DEMO.bragg_angle(d)
            self.assertAlmostEqual(2*d*math.sin(math.radians(two_theta/2)),1.5406,places=12)
        self.assertGreater(DEMO.bragg_angle(2.425*(1-.022)),DEMO.bragg_angle(2.425))
        rows=read_csv(self.showcase/'operando_xrd/data.csv')
        coords={(r['soc_fraction'],r['two_theta_deg']) for r in rows}
        self.assertEqual(len(coords),len(rows))
        self.assertEqual(len(rows),105*240)
        for progress in (0.0,1.0):
            selected=[r for r in rows if float(r['soc_fraction'])==progress]
            angles=np.array([float(r['two_theta_deg']) for r in selected])
            peak=angles[np.argmax([float(r['intensity_au']) for r in selected])]
            expected=DEMO.bragg_angle(2.425*(1-.022*progress))
            self.assertLess(abs(peak-expected),.049)
        self.assertTrue(all(float(r['intensity_au'])>=0 for r in rows))
        self.note(grid=[105,240], wavelength_A=1.5406, interpretation='Fictitious independent spacings; progress is not measured SOC or phase assignment')

    def test_tofsims_same_field_mean_and_nonnegative_limits(self):
        """Sputter profile at 30 s equals shown channel mean; arbitrary intensity is not concentration."""
        image=read_csv(self.showcase/'tof_sims/data.csv')
        profile=read_csv(self.showcase/'tof_sims/depth.csv')
        for species in ('F-','Li+','S-'):
            selected=[r for r in image if r['species']==species]
            values=np.array([float(r['normalized_intensity']) for r in selected])
            self.assertEqual(len(selected),72*72)
            self.assertTrue(np.all((0<=values)&(values<=1)))
            row=next(r for r in profile if r['species']==species and float(r['sputter_time_s'])==30)
            self.assertAlmostEqual(float(row['mean_normalized_intensity']),float(values.mean()),places=6)
        self.assertTrue(all(0<=float(r['mean_normalized_intensity'])<=1 for r in profile))
        self.assertEqual(CORE.showcase_scientific_basis('tof_sims')['model_class'],'layout_fixture')
        fig=CORE.figure('tof_sims')
        map_artists=[ax.images[0] for ax in fig.axes if ax.images and np.asarray(ax.images[0].get_array()).ndim==2]
        self.assertEqual(len(map_artists),3)
        for artist in map_artists:
            values=np.asarray(artist.get_array(),dtype=float)
            low,high=artist.get_clim()
            self.assertGreaterEqual(float(values.min()),low)
            self.assertLessEqual(float(values.max()),high)
        for ax in fig.axes:
            low,high=sorted(ax.get_ylim())
            for line in ax.lines:
                if line.get_transform() is ax.transData:
                    y=np.asarray(line.get_ydata(),dtype=float)
                    self.assertTrue(np.all((y>=low)&(y<=high)))
        plt.close(fig)
        self.note(channels=3, grid=[72,72], linkage_time_s=30, no_map_or_profile_display_clipping=True,
                  physical_claim='None: nonnegative layout field; matrix/yield effects not simulated')

    def test_rate_accessibility_recovery_and_linked_cutoffs(self):
        """Rate-stage response separates reversible access from irreversible loss without arbitrary recovery bonuses."""
        rows=read_csv(self.showcase/'rate_capability/data.csv')
        parameters=CORE.showcase_scientific_basis('rate_capability')['parameters']
        for row in rows:
            p=parameters[row['sample']]
            q=p['Q0_mAh_g']*math.exp(-p['k_per_cycle']*int(row['cycle']))/(1+(float(row['discharge_rate_C'])/p['r_limit_C'])**.8)
            self.assertAlmostEqual(float(row['capacity_mAh_g']),q,places=4)
        for sample in 'AB':
            selected=[r for r in rows if r['sample']==sample]
            self.assertLess(float(selected[-1]['capacity_mAh_g']),float(selected[0]['capacity_mAh_g']))
            self.assertGreater(float(selected[50]['capacity_mAh_g']),float(selected[49]['capacity_mAh_g']))
        profiles=read_csv(self.showcase/'rate_capability/voltage_profiles.csv')
        for cycle in (7,27,47,57):
            group=[r for r in profiles if int(r['cycle'])==cycle]
            self.assertEqual(float(group[0]['voltage_V']),4.3)
            self.assertEqual(float(group[-1]['voltage_V']),2.8)
        self.note(stages_C=[.2,.5,1,2,5,.2], cycles=60, scope='Chosen rate response, no transport/material fit')

    def test_aurbach_inventory_balance_and_integrated_current(self):
        """Formation, reservoir, ten partial pairs and final strip obey recoverable inventory and charge conservation."""
        rows=read_csv(self.showcase/'aurbach_protocol/data.csv')
        ledger=json.loads((self.showcase/'aurbach_protocol/protocol.json').read_text(encoding='utf-8'))
        times=np.array([float(r['time_h']) for r in rows])
        currents=np.array([float(r['current_density_mA_cm2']) for r in rows])
        self.assertTrue(np.all(np.diff(times)>0))
        self.assertAlmostEqual(float(np.sum(currents[:-1]*np.diff(times))),
                               ledger['all_stripped_mAh_cm2']-ledger['all_plated_mAh_cm2'],places=10)
        for row in rows:
            active=float(row['active_inventory_mAh_cm2'])
            trapped=float(row['trapped_inventory_mAh_cm2'])
            net=float(row['cumulative_plated_mAh_cm2'])-float(row['cumulative_stripped_mAh_cm2'])
            self.assertGreaterEqual(active,0)
            self.assertGreaterEqual(trapped,0)
            self.assertAlmostEqual(active+trapped,net,places=10)
        for interval in ledger['stage_intervals']:
            self.assertAlmostEqual(abs(interval['current_mA_cm2'])*(interval['end_h']-interval['start_h']),interval['passed_mAh_cm2'],places=10)
        self.assertEqual(float(rows[-1]['voltage_V']),1)
        self.assertAlmostEqual(ledger['final_active_inventory_mAh_cm2'],0,places=12)
        self.assertAlmostEqual(ledger['CE_reservoir_demo_pct'],99.5,places=10)
        self.assertAlmostEqual(ledger['final_strip_mAh_cm2'],1.9775,places=10)
        self.note(partial_cycles=10, final_strip_mAh_cm2=ledger['final_strip_mAh_cm2'], chosen_reservoir_efficiency_pct=ledger['CE_reservoir_demo_pct'], excluded_formation=True)

    def test_rc_current_transient_charge_and_ocv_limits(self):
        """Voltage-step current has an analytic integrated charge; open-circuit RC relaxation has a finite limit."""
        rows=read_csv(self.showcase/'chronoamperometry/data.csv')
        for sample,scale,tau in [('A',1,45),('B',.72,80)]:
            selected=[r for r in rows if r['sample']==sample]
            for row in selected:
                t=float(row['time_s'])
                expected=(.045*scale*t+.68*scale*tau*(1-math.exp(-t/tau)))/3600
                self.assertAlmostEqual(float(row['passed_charge_mAh_cm2']),expected,places=12)
                self.assertLess(float(row['current_density_mA_cm2']),0)
        rest=read_csv(self.showcase/'ocv_rest/data.csv')
        for sample,fast,slow in [('A',.045,.08),('B',.065,.13)]:
            series=[r for r in rest if r['sample']==sample]
            voltages=[float(r['voltage_V']) for r in series]
            self.assertTrue(np.all(np.diff(voltages)<=0))
            self.assertTrue(all(4.15-fast-slow<=v<=4.15 for v in voltages))
        self.note(transient_rows_per_sample=300, ocv_rows_per_sample=250, limitation='No deposited mass/nucleation or voltage-derived self-discharge capacity')

    def test_thermal_node_first_law_and_linked_values(self):
        """Thermal field obeys positive node balance and exact linked line/history at plausible declared scale."""
        p=CORE.showcase_scientific_basis('pouch_thermal')['parameters']
        self.assertAlmostEqual(p['Ctotal_J_K'],p['total_mass_kg']*p['specific_heat_J_kg_K'])
        self.assertAlmostEqual(p['Ctotal_J_K']/p['Gtotal_W_K'],p['tau_min']*60)
        xx,yy=np.meshgrid(np.linspace(0,100,101),np.linspace(0,70,71))
        total_conductance=p['Gtotal_W_K']
        for minute in (0,9,30):
            h=.00001
            temp=CORE.thermal_field(xx,yy,minute)
            derivative=(CORE.thermal_field(xx,yy,minute+h)-CORE.thermal_field(xx,yy,minute-h))/(2*h*60)
            equilibrium_rise=(CORE.thermal_field(xx,yy,minute+200)-25)
            heating=total_conductance*equilibrium_rise
            np.testing.assert_allclose(p['Ctotal_J_K']*derivative,heating-total_conductance*(temp-25),atol=1e-8)
        data=read_csv(self.showcase/'pouch_thermal/data.csv')
        history=read_csv(self.showcase/'pouch_thermal/history.csv')
        values=[float(r['surface_temperature_C']) for r in data]
        self.assertAlmostEqual(float(history[-1]['Tmax_C']),max(values),places=4)
        self.assertAlmostEqual(float(history[-1]['Tmean_C']),float(np.mean(values)),places=4)
        self.note(total_heat_capacity_J_K=90, total_conductance_W_K=1/6, mass_kg=.1, limitation='Uncoupled teaching nodes; no IR, C-rate heat inference or thermal-runaway calculation')

    def test_model_metadata_and_composite_source_closure(self):
        """All 18 core model records have source-scoped basis; composite lists its actual ten input data files."""
        basis_schema=SCHEMA['properties']['scientific_basis']
        for name in CORE.GENERATORS:
            basis=CORE.showcase_scientific_basis(name)
            METADATA.validate_schema(basis,basis_schema,name)
            for filename in CORE.source_names(name):
                self.assertTrue((self.showcase/name/filename).is_file(),(name,filename))
        for name in ECHEM.SOURCES:
            basis=ECHEM.scientific_basis(name)
            METADATA.validate_schema(basis,basis_schema,name)
            METADATA.validate_schema(json.loads((self.showcase/name/'metadata.json').read_text(encoding='utf-8')),SCHEMA,name)
        source_files=CORE.source_names('capability_spread')
        self.assertEqual(sum(p.startswith('../') for p in source_files),10)
        self.assertIn('../pouch_thermal/history.csv',source_files)
        dependencies={Path(p).parts[1] for p in source_files if p.startswith('../')}
        self.assertEqual(dependencies,set(CORE.showcase_scientific_basis('capability_spread')['dependency_ids']))
        self.note(core_metadata_templates=18, composite_input_dependencies=10, references_scope='Model definition/interpretation boundaries only; never paper numbers')

    def test_own_recipe_reference_data_and_schema(self):
        """Three adaptable reference images are rendered from their own CSV/config; raw artist arrays match."""
        for kind in PACKAGER.IDS:
            pack=self.pack_root/'examples/recipe_packs'/kind
            meta=json.loads((pack/'reference/metadata.json').read_text(encoding='utf-8'))
            METADATA.validate_metadata(meta)
            sources=json.loads((pack/'sources.json').read_text(encoding='utf-8'))
            record=json.loads((pack/'reference/data_checks.json').read_text(encoding='utf-8'))
            self.assertEqual(record['resource_id'],kind)
            self.assertEqual(record['scientific_review'],'pending_author_review')
            for name,sha in sources['demo_inputs_sha256'].items():
                self.assertEqual(digest(pack/name),sha)
            for curve in record['exact_data_artist_checks']:
                if curve['check']=='exact_quadmesh_array':
                    self.assertEqual(len(curve['intensity']),len(curve['progress']))
                    self.assertTrue(all(len(r)==len(curve['two_theta']) for r in curve['intensity']))
                else:
                    self.assertEqual(curve['line_style'],'-')
                    self.assertIn(curve['marker'],(None,'None','',' '))
                    self.assertEqual(curve['points'],len(curve['x']))
                    self.assertEqual(curve['points'],len(curve['y']))
            if kind=='full_cell':
                cycling=read_csv(pack/'demo/cycling.csv')
                for curve in record['exact_data_artist_checks']:
                    if curve['identity'].endswith(':capacity'):
                        sample=curve['identity'].removesuffix(':capacity')
                        selected=[r for r in cycling if r['sample']==sample]
                        self.assertEqual(curve['y'],[float(r['capacity']) for r in selected])
                self.assertEqual(meta['scientific_basis']['parameters']['count_cycles'],40)
        self.note(recipes=3, source_origin='Each own generator/config/CSV, no copying the canonical half-cell image into a full-cell demo', engineering_validation='Exact artist arrays, frame checks and schema only')

    def test_electrochem_generate_render_source_contract(self):
        """All four optional paths actually render; mandatory CSV and optional ledger must exist, be unique and stay local."""
        from batteryplot.electrochem import _metadata
        for name in ECHEM.SOURCES:
            ECHEM.generate(name)
            ECHEM.render(name)
            folder=self.showcase/name
            meta,_=_metadata(folder,name)
            METADATA.validate_metadata(meta)
            self.assertTrue(meta['actual_artist_checks'])
            for ext in ('png','svg','pdf'):
                self.assertGreater((folder/f'figure.{ext}').stat().st_size,1000)
            report=json.loads((folder/'render-report.json').read_text(encoding='utf-8'))
            self.assertTrue(report['actual_artist_checks'])
            self.assertTrue((folder/'alignment.json').is_file())
        name='aurbach_protocol'
        original=json.loads((self.showcase/name/'metadata.json').read_text(encoding='utf-8'))
        bad=self.root/'bad-electrochem-source'
        bad.mkdir()
        shutil.copy2(self.showcase/name/'data.csv',bad/'data.csv')
        failures=([],['protocol.json'],['data.csv','data.csv'],
                  ['data.csv','../protocol.json'],['data.csv','unlisted.json'],['data.csv','protocol.json'])
        for sources in failures:
            meta={**original,'source_files':sources}
            (bad/'metadata.json').write_text(json.dumps(meta),encoding='utf-8')
            with self.assertRaises(ValueError):
                _metadata(bad,name)
        (bad/'metadata.json').write_text(json.dumps({**original,'source_files':['data.csv']}),encoding='utf-8')
        self.assertEqual(_metadata(bad,name)[0]['source_files'],['data.csv'])
        self.note(rendered_optional_paths=list(ECHEM.SOURCES), optional_ledger='aurbach_protocol/protocol.json',
                  source_contract_rejected_cases=len(failures), outputs=['PNG','SVG','PDF','alignment','actual_artist_checks'],
                  gap_closed='Old 17 checks validated generation/schema/physics but did not execute four optional render paths')

    def test_selected_figures_do_not_clip_new_endpoints(self):
        """Affected scientific Line2D endpoints remain inside saved figure axes and use four-sided solid-line display."""
        checked=[]
        for name in ('full_cell','li_cu_ce','li_li','eis','gcd_profiles','rate_capability'):
            fig=CORE.figure(name)
            CORE.curve_style_audit(fig)
            CORE.data_frame_audit(fig)
            for ax in fig.axes:
                low,high=sorted(ax.get_ylim())
                for line in ax.lines:
                    if line.get_transform() is not ax.transData:
                        continue  # axvline stage annotations use axis-fraction y=0..1, not data values
                    y=np.asarray(line.get_ydata(),dtype=float)
                    self.assertTrue(np.all(y>=low-1e-10),(name,low,float(y.min())))
                    self.assertTrue(np.all(y<=high+1e-10),(name,high,float(y.max())))
            checked.append(name)
            plt.close(fig)
        self.note(figures=checked, check='Actual y arrays remain in y-limits; four-sided frames, solid lines, no markers')

    def test_invalid_model_parameters_stop(self):
        """Analytic generators refuse nonfinite/unphysical coefficients rather than fabricating outputs."""
        bad=[lambda:DEMO.inventory_cycles(170,40,.5,.6,5),
             lambda:DEMO.inventory_cycles(float('nan'),40,.001,0,5),
             lambda:DEMO.halfcell_cycles(170,40,.01,3,.001,0,0,.5,.6,5),
             lambda:DEMO.halfcell_cycles(170,40,.01,3,float('nan'),0,0,.001,0,5),
             lambda:DEMO.fullcell_voltage(.5,high=float('inf')),
             lambda:DEMO.fullcell_voltage(float('nan')),
             lambda:DEMO.symmetric_rc_rows('A',3,20,0,1,10,20,.1),
             lambda:DEMO.bragg_angle(.1),
             lambda:CORE.impedance(np.array([0.0]),1,2,.01,.8,1),
             lambda:CORE.impedance(np.array([1.0]),1,2,.01,1.1,1)]
        for function in bad:
            with self.assertRaises(ValueError): function()
        self.note(rejected_cases=len(bad), scope='Only known demo functions; measured author anomalies are not silently clipped or replaced')


class EvidenceResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cases=[]
    def addSuccess(self,test):
        super().addSuccess(test)
        self.cases.append({'case':test._testMethodName,'description':test.shortDescription(),'status':'PASS'})
    def addFailure(self,test,err):
        super().addFailure(test,err)
        self.cases.append({'case':test._testMethodName,'description':test.shortDescription(),'status':'FAIL'})
    def addError(self,test,err):
        super().addError(test,err)
        self.cases.append({'case':str(test),'description':test.shortDescription(),'status':'ERROR'})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticCorePhysicsTests)
    result=unittest.TextTestRunner(verbosity=2,resultclass=EvidenceResult).run(suite)
    if args.report:
        sources=['examples/recipe_packs/_runtime/generate_demo.py','examples/showcase/build.py',
                 'examples/showcase/electrochem.py','scripts/package_recipe_packs.py',
                 'skills/voltpeer-plot/scripts/batteryplot/electrochem.py',
                 'tests/test_synthetic_core_physics.py']
        report={'schema_version':1,'checked_date':'2026-10-01','status':'PASS' if result.wasSuccessful() else 'FAIL',
                'scope':'Temporary original teaching fixtures, analytic equations/charge inventories/units/linkage and actual selected artists; no real cell/material/experimental certification.',
                'not_validated':['Experimental data','Named material performance','All native desktop/model behavior','Independent human visual review'],
                'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                'source_sha256':{p:digest(REPO/p) for p in sources},
                'cases':[{**c,'evidence':SyntheticCorePhysicsTests.evidence.get(c['case'],{})} for c in result.cases]}
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
