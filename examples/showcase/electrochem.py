"""Four independent synthetic electrochemistry demos; no measured values.

python examples/showcase/electrochem.py all [--name RECIPE]
Rendering does not regenerate CSV input.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'skills/battery-review-figure/scripts'))
sys.path.insert(0, str(ROOT.parents[1] / 'examples/recipe_packs/_runtime'))
from generate_demo import reference, GAMRY, LI_PROTOCOL
from batteryplot.electrochem import ELECTROCHEM_RECIPES
from batteryplot.specialist import render_recipe

SOURCES = {
    'aurbach_protocol': ('10.1038/s41467-025-66197-7', 'Nature Communications', 2025, 'Fig. 4c caption / Methods',
                         'Stage grammar only. The figure caption places Aurbach in 4c; the article body contains an inconsistent 4b pointer. No paper numbers copied.'),
    'eis_frequency': ('10.1038/s41467-022-29596-8', 'Nature Communications', 2022, 'Fig. 2e',
                      'Frequency-resolved Bode view accompanies impedance spectra; real and signed imaginary components are displayed here as a distinct optional view.'),
    'chronoamperometry': ('10.1038/s41467-022-32139-w', 'Nature Communications', 2022, 'Fig. 2a',
                          'Potentiostatic current-time transients can be displayed without fitting a nucleation model.'),
    'ocv_rest': ('10.1038/s41467-022-29837-w', 'Nature Communications', 2022, 'Fig. 1a,b',
                 'Voltage relaxation after charge is time-resolved; voltage drop alone does not measure capacity lost.'),
}


def scientific_basis(name):
    basis = {'schema_version': 1, 'model_class': 'analytic_model',
             'data_origin': 'original_synthetic',
             'parameter_origin': 'Explicit original teaching parameters, not measured values',
             'validation_scope': 'Declared teaching model; no experimental/material certification'}
    if name == 'aurbach_protocol':
        basis.update(equations=['Qstage=abs(j)*duration_h; plated/stripped charge integrates the zero-order-hold current',
                                'Plating: active_new=active_old+eta*Qplate; trapped_new=trapped_old+(1-eta)*Qplate',
                                'Stripping: active_new=active_old-Qstrip; trapped inventory is not recovered',
                                'After conditioning: CE_reservoir_demo=100*(n*Qc+Qfinal)/(n*Qc+Qreservoir)'],
                     assumptions=['Formation is excluded from the reservoir metric and ends with no recoverable active Li.',
                                  'Reservoir and subsequent deposits share eta=0.995; stripping recovers available active Li exactly.',
                                  'Partial strips remove Qc before redepositing Qc, always leaving positive active inventory.',
                                  'No calendar corrosion, crossover or additional parasitic stripping process is simulated.'],
                     parameters={'formation_plate_mAh_cm2': 1, 'formation_recovery': .97,
                                 'reservoir_plate_mAh_cm2': 2, 'Qc_mAh_cm2': .25, 'n': 10,
                                 'j_mA_cm2': .5, 'deposit_recovery': .995, 'final_cutoff_V': 1},
                     references=[reference('https://www.nature.com/articles/s41467-025-66197-7',
                                           'De-solvation of heteroalkali cations enabling stable solid electrolyte interphase for dendrite-free lithium metal batteries',
                                           'Fig. 4c caption/Methods define stage grammar; no times, efficiencies, capacities or curve artwork copied.'),
                                 reference(LI_PROTOCOL, 'Understanding and applying coulombic efficiency in lithium metal batteries',
                                           'Protocol and cell-configuration boundaries of reservoir versus cycle-by-cycle efficiency.')],
                     limitations=['The reservoir result is an algebraic check of the chosen ledger, not measured electrolyte CE or a universal protocol.',
                                  'Voltage is an explicit bounded display relation, not SEI or nucleation physics.'])
    elif name == 'eis_frequency':
        basis.update(equations=['omega=2*pi*f; Z=Rs+Rct/(1+j*omega*Rct*C)',
                                'Nyquist circle: (Re Z-Rs-Rct/2)^2+(Im Z)^2=(Rct/2)^2',
                                'Stored real and signed imaginary components come from the same complex values'],
                     assumptions=['Positive passive resistors/capacitor; linear stationary small-signal response.',
                                  'No Warburg, inductance, CPE or microscopic assignment is present in this ideal RC example.'],
                     parameters={'A': {'Rs_ohm': 3.6, 'Rct_ohm': 22, 'C_F': .0008},
                                 'B': {'Rs_ohm': 4.8, 'Rct_ohm': 41, 'C_F': .0007},
                                 'frequency_Hz': [.01, 1e5]},
                     references=[reference(GAMRY, 'Basics of Electrochemical Impedance Spectroscopy',
                                           'Complex circuit equations and the ideal Randles RC semicircle; original parameter values.')],
                     limitations=['No fitted cell resistance, active area, diffusion coefficient or material evidence.'])
    elif name == 'chronoamperometry':
        basis.update(equations=['j(t)=-jsteady-j0*exp(-t/tau)',
                                'Qpassed(t)=(jsteady*t+j0*tau*(1-exp(-t/tau)))/3600 in mAh cm^-2',
                                'An ideal voltage-step RC branch gives j0=abs(deltaV)/Rs and tau=Rs*C; a parallel resistor gives jsteady=abs(deltaV)/Rf'],
                     assumptions=['Stationary passive voltage-step RC plus a constant resistive branch.',
                                  'All passed charge is external; no deposited mass or nucleation mechanism is assigned.'],
                     parameters={'step_V': -.05, 'A': {'jsteady_mA_cm2': .045, 'j0_mA_cm2': .68, 'tau_s': 45},
                                 'B': {'jsteady_mA_cm2': .0324, 'j0_mA_cm2': .4896, 'tau_s': 80}},
                     references=[reference(GAMRY, 'Basics of Electrochemical Impedance Spectroscopy',
                                           'Passive resistor/capacitor current-voltage laws; not a nucleation model or paper fit.')],
                     limitations=['Not Cottrell diffusion or Scharifker-Hills nucleation; cannot infer deposited Li, passivation or stability.'])
    elif name == 'ocv_rest':
        basis.update(equations=['V(t)=V0-a_fast*(1-exp(-t/tau_fast))-a_slow*(1-exp(-t/tau_slow))',
                                'External rest current is zero; internal polarization states relax with positive RC time constants'],
                     assumptions=['A terminal open-circuit display with two decaying initial polarization states.',
                                  'No leakage current or capacity measurement is provided; voltage relaxation is not quantified self-discharge.'],
                     parameters={'V0_V': 4.15, 'tau_fast_h': 2.5, 'tau_slow_h': 60,
                                 'A': {'a_fast_V': .045, 'a_slow_V': .08},
                                 'B': {'a_fast_V': .065, 'a_slow_V': .13}},
                     references=[reference(GAMRY, 'Basics of Electrochemical Impedance Spectroscopy',
                                           'Passive RC relations only; parameters are chosen display amplitudes, not recovered capacity.')],
                     limitations=['No material thermodynamics, leakage rate, state of charge or retained charge can be inferred.'])
    else:
        raise ValueError('Unknown electrochemistry teaching model: ' + name)
    return basis


def aurbach_rows():
    """Explicit charge ledger with unique times and no invented Li recovery."""
    eta, formation_eta, j, reservoir, qc, count = .995, .97, .5, 2.0, .25, 10
    stages = [('formation plate', -j, 1.0, formation_eta),
              ('formation strip', j, formation_eta, 1.0),
              ('reservoir plate', -j, reservoir, eta)]
    for _ in range(count):
        stages += [('partial cycles', j, qc, 1.0), ('partial cycles', -j, qc, eta)]
    final_capacity = eta * reservoir - count * (1 - eta) * qc
    stages += [('final strip', j, final_capacity, 1.0)]
    rows, intervals = [], []
    time, active, trapped, plated, stripped = 0.0, 0.0, 0.0, 0.0, 0.0
    for index, (stage, current, charge, recovery) in enumerate(stages):
        if stage == 'final strip':
            charge = final_capacity = active  # actual available state, not an independent arbitrary endpoint
        duration = charge / abs(current)
        interval = {'stage': stage, 'start_h': time, 'end_h': time + duration,
                    'current_mA_cm2': current, 'passed_mAh_cm2': charge,
                    'deposit_recovery': recovery if current < 0 else None,
                    'active_before_mAh_cm2': active, 'trapped_before_mAh_cm2': trapped}
        if current > 0 and charge > active + 1e-12:
            raise ValueError('Aurbach strip exceeds available active lithium.')
        for point in range(61 if index == len(stages) - 1 else 60):
            fraction = point / 60
            q = fraction * charge
            a = active + recovery * q if current < 0 else active - q
            d = trapped + (1 - recovery) * q if current < 0 else trapped
            qp = plated + q if current < 0 else plated
            qs = stripped + q if current > 0 else stripped
            complete_strip = stage in {'formation strip', 'final strip'}
            voltage = (-.035 - .010 * fraction if current < 0
                       else .05 + (.95 * fraction ** 12 if complete_strip else .012 * fraction))
            rows.append((stage, time + fraction * duration, voltage, current, q, a, d, qp, qs))
        time += duration
        if current < 0:
            active += recovery * charge
            trapped += (1 - recovery) * charge
            plated += charge
        else:
            active -= charge
            stripped += charge
        interval.update(active_after_mAh_cm2=active, trapped_after_mAh_cm2=trapped)
        intervals.append(interval)
    ledger = {'reservoir_plate_mAh_cm2': reservoir, 'partial_strip_mAh_cm2': qc,
              'partial_plate_mAh_cm2': qc, 'partial_cycles': count,
              'final_strip_mAh_cm2': final_capacity,
              'CE_reservoir_demo_pct': 100 * (count * qc + final_capacity) / (count * qc + reservoir),
              'final_active_inventory_mAh_cm2': active, 'final_trapped_inventory_mAh_cm2': trapped,
              'all_plated_mAh_cm2': plated, 'all_stripped_mAh_cm2': stripped,
              'excluded_formation': True, 'stage_intervals': intervals,
              'sampling': 'Right-continuous stage current; transition endpoint belongs to the new stage. Final endpoint included; stage charge comes from exact intervals, not trapezoidal interpolation across jumps.',
              'scientific_basis': scientific_basis('aurbach_protocol')}
    return rows, ledger


def write_csv(path, columns, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)


def generate(name):
    folder = ROOT / name
    folder.mkdir(exist_ok=True)
    if name == 'aurbach_protocol':
        data, ledger = aurbach_rows()
        columns = ['stage', 'time_h', 'voltage_V', 'current_density_mA_cm2',
                   'passed_stage_capacity_mAh_cm2', 'active_inventory_mAh_cm2',
                   'trapped_inventory_mAh_cm2', 'cumulative_plated_mAh_cm2', 'cumulative_stripped_mAh_cm2']
        (folder/'protocol.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        opt = {'protocol_name': 'Original modified Aurbach-like charge-ledger teaching sequence',
               'cell_configuration': 'Synthetic Li||Cu-like cell',
               'current_sign_convention': 'negative=plating, positive=stripping; invented for this demo',
               'capacity_schedule_mAh_cm2': 'Conditioning: plate 1, recover 0.97; reservoir plate 2; ten partial strip/plate pairs of 0.25; final strip equals actual recoverable inventory 1.9775. Values original, not measured.',
               'cutoff_description': 'Final stripping reaches the stored 1 V endpoint. Formation stripping has a 1 V analytic left limit at transition; the right-continuous trace samples the new stage at that boundary. Partial cycles retain active inventory.',
               'stage_sequence': ['formation plate', 'formation strip', 'reservoir plate', 'partial cycles', 'final strip']}
        conditions = 'Original Li||Cu-like ledger at nominal 25 °C and |j|=0.5 mA cm−2; 2 mAh cm−2 reservoir, ten 0.25 mAh cm−2 partial strip/plate pairs, deposit recovery 99.5%. This algebraic model is not a measured CE or an exact experimental Aurbach protocol.'
    elif name == 'eis_frequency':
        f = np.logspace(5, -2, 120)
        data = []
        for sample, rs, rct, capacitance in (('A', 3.6, 22, .0008), ('B', 4.8, 41, .0007)):
            z = rs + rct/(1+2j*np.pi*f*rct*capacitance)
            data.extend((sample, float(fi), float(zi.real), float(zi.imag)) for fi, zi in zip(f, z))
        columns = ['sample', 'frequency_Hz', 'z_real_ohm', 'z_imag_ohm']
        opt = {'cell_configuration': 'Invented two-electrode cell', 'measurement_state': 'Invented same rest state',
               'temperature_C': 25, 'perturbation_mV': 10, 'frequency_direction': 'descending'}
        conditions = 'Invented R_s+(R_ct||C) complex impedance at 25 °C, 10 mV, 100 kHz–0.01 Hz. Parameters not fitted to experimental data; no circuit assignment to a real cell.'
    elif name == 'chronoamperometry':
        t = np.linspace(0, 900, 300)
        data = []
        for sample, scale, transient in (('A', 1.0, 45), ('B', .72, 80)):
            current = -.045*scale - .68*scale*np.exp(-t/transient)
            charge = (.045*scale*t + .68*scale*transient*(1-np.exp(-t/transient)))/3600
            data.extend((sample, float(ti), float(ii), float(qi)) for ti, ii, qi in zip(t, current, charge))
        columns = ['sample', 'time_s', 'current_density_mA_cm2', 'passed_charge_mAh_cm2']
        opt = {'cell_configuration': 'Invented Li||Cu-like cell', 'reference_electrode': 'Li metal, synthetic only',
               'current_sign_convention': 'cathodic current plotted negative',
               'applied_potential_V': -.05, 'zoom_time_s': [0, 180]}
        conditions = 'Synthetic constant-potential current transients at −0.05 V vs an invented Li reference. No measured nucleation, passivation, deposited charge or stability.'
    else:
        t = np.linspace(0, 48, 250)
        data = []
        for sample, initial, fast, slow in (('A', 4.15, .045, .08), ('B', 4.15, .065, .13)):
            voltage = initial - fast*(1-np.exp(-t/2.5)) - slow*(1-np.exp(-t/60))
            data.extend((sample, float(ti), float(vi)) for ti, vi in zip(t, voltage))
        columns = ['sample', 'time_h', 'voltage_V']
        opt = {'cell_configuration': 'Invented full cells A/B', 'initial_state': 'Invented fully charged rest start',
               'rest_condition': 'Open circuit, no load; no recovered capacity measurement',
               'temperature_C': 25, 'zoom_time_h': [0, 8]}
        conditions = 'Synthetic open-circuit voltage relaxation for 48 h at nominal 25 °C. No actual capacity or self-discharge rate can be inferred from these voltages.'
    write_csv(folder/'data.csv', columns, data)
    doi, journal, year, panel, observation = SOURCES[name]
    metadata = {'data_status': 'synthetic_demo', 'not_experimental_data': True,
                'figure_grammar_id': f'optional:{name}', 'source_files': ['data.csv', 'protocol.json'] if name == 'aurbach_protocol' else ['data.csv'],
                'test_conditions': conditions, 'variables_and_units': columns,
                'render_options': opt,
                'reference': {'doi': doi, 'journal': journal, 'year': year,
                              'figure_panel': panel, 'observation': observation,
                              'review_scope': 'Paper text/figure checked; display idea only, no numerical values or artwork copied',
                              'default_template': False},
                'reproduce': f'python render_specialist.py --recipe {name} --input-folder {name} --output-dir brf-output --style forge',
                'creator': 'BatteryReviewForge original synthetic analytic demonstration',
                'generator_version': '1.6', 'scientific_basis': scientific_basis(name)}
    (folder/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def render(name):
    folder = ROOT/name
    fig, report = render_recipe(name, folder)
    from batteryplot.qa import data_plot_checks
    checks = data_plot_checks(fig)
    report['actual_artist_checks'] = checks
    metadata = json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    metadata.update(generator_version='1.6', actual_artist_checks=checks)
    (folder/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with matplotlib.rc_context(fig.brf_export_rc):
        for ext in ('png', 'svg', 'pdf'):
            fig.savefig(folder/f'figure.{ext}', dpi=300, facecolor='white')
    plt.close(fig)
    report['resolved_font_path'] = Path(report['resolved_font_path']).name
    (folder/'render-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (folder/'alignment.json').write_text(json.dumps(report['alignment'], indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('generate', 'render', 'all'))
    parser.add_argument('--name', choices=ELECTROCHEM_RECIPES)
    args = parser.parse_args()
    for name in ([args.name] if args.name else ELECTROCHEM_RECIPES):
        if args.action in ('generate', 'all'): generate(name)
        if args.action in ('render', 'all'): render(name)
        print(args.action, name)
