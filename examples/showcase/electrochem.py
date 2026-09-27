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
from batteryplot.electrochem import ELECTROCHEM_RECIPES
from batteryplot.specialist import render_recipe

SOURCES = {
    'aurbach_protocol': ('10.1038/s41467-025-66197-7', 'Nature Communications', 2025, 'Fig. 4b / Methods',
                         'Reported modified Aurbach protocol separates formation, reservoir, partial cycling and final strip; this plot does not calculate CE.'),
    'eis_frequency': ('10.1038/s41467-022-29596-8', 'Nature Communications', 2022, 'Fig. 2e',
                      'Frequency-resolved Bode view accompanies impedance spectra; real and signed imaginary components are displayed here as a distinct optional view.'),
    'chronoamperometry': ('10.1038/s41467-022-32139-w', 'Nature Communications', 2022, 'Fig. 2a',
                          'Potentiostatic current-time transients can be displayed without fitting a nucleation model.'),
    'ocv_rest': ('10.1038/s41467-022-29837-w', 'Nature Communications', 2022, 'Fig. 1a,b',
                 'Voltage relaxation after charge is time-resolved; voltage drop alone does not measure capacity lost.'),
}


def write_csv(path, columns, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)


def generate(name):
    folder = ROOT / name
    folder.mkdir(exist_ok=True)
    if name == 'aurbach_protocol':
        stages = [('formation plate', -.5, -.035), ('formation strip', .5, .19),
                  ('reservoir plate', -.5, -.025), ('partial cycles', .25, .06),
                  ('final strip', .5, .17)]
        data = []
        time = 0.0
        for stage, current, baseline in stages:
            for idx, fraction in enumerate(np.linspace(0, 1, 61)):
                t = time + float(fraction)*2
                if stage == 'partial cycles':
                    signal = (-1 if int(fraction*6) % 2 else 1)
                    current_here = signal*abs(current)
                    voltage = signal*(.052 + .007*np.sin(2*np.pi*fraction*3))
                else:
                    current_here = current
                    voltage = baseline + (.035*fraction if current > 0 else -.008*fraction)
                    if stage == 'formation strip': voltage += .45*fraction**12
                    if stage == 'final strip': voltage += .32*fraction**12
                data.append((stage, t, voltage, current_here))
            time += 2.01
        columns = ['stage', 'time_h', 'voltage_V', 'current_density_mA_cm2']
        opt = {'protocol_name': 'Invented modified Aurbach-like sequence, display only',
               'cell_configuration': 'Synthetic Li||Cu-like cell',
               'current_sign_convention': 'negative=plating, positive=stripping; invented for this demo',
               'capacity_schedule_mAh_cm2': 'Invented signed-current trace: formation and reservoir 1 each; three partial cycles about 0.083 per half-step; final strip 1. These are demonstration integrals, not an Aurbach CE dataset',
               'cutoff_description': 'Synthetic end-of-strip voltage rise; no measured cutoff applied',
               'stage_sequence': [stage for stage, _, _ in stages]}
        conditions = 'Synthetic stage-resolved Li||Cu-like voltage/current sequence at nominal 25 °C. Times, capacities, currents, voltages and signs are invented; no exact experimental Aurbach protocol or CE value.'
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
            data.extend((sample, float(ti), float(ii)) for ti, ii in zip(t, current))
        columns = ['sample', 'time_s', 'current_density_mA_cm2']
        opt = {'cell_configuration': 'Invented Li||Cu-like cell', 'reference_electrode': 'Li metal, synthetic only',
               'current_sign_convention': 'cathodic current plotted negative',
               'applied_potential_V': -.05, 'zoom_time_s': [0, 180]}
        conditions = 'Synthetic constant-potential current transients at −0.05 V vs an invented Li reference. No measured nucleation, passivation, deposited charge or stability.'
    else:
        t = np.linspace(0, 48, 250)
        data = []
        for sample, initial, fast, slow in (('A', 4.15, .045, .002), ('B', 4.15, .065, .003)):
            voltage = initial - fast*(1-np.exp(-t/2.5)) - slow*t
            data.extend((sample, float(ti), float(vi)) for ti, vi in zip(t, voltage))
        columns = ['sample', 'time_h', 'voltage_V']
        opt = {'cell_configuration': 'Invented full cells A/B', 'initial_state': 'Invented fully charged rest start',
               'rest_condition': 'Open circuit, no load; no recovered capacity measurement',
               'temperature_C': 25, 'zoom_time_h': [0, 8]}
        conditions = 'Synthetic open-circuit voltage relaxation for 48 h at nominal 25 °C. No actual capacity or self-discharge rate can be inferred from these voltages.'
    write_csv(folder/'data.csv', columns, data)
    doi, journal, year, panel, observation = SOURCES[name]
    metadata = {'data_status': 'synthetic_demo', 'not_experimental_data': True,
                'figure_grammar_id': f'optional:{name}', 'source_files': ['data.csv'],
                'test_conditions': conditions, 'variables_and_units': columns,
                'render_options': opt,
                'reference': {'doi': doi, 'journal': journal, 'year': year,
                              'figure_panel': panel, 'observation': observation,
                              'review_scope': 'Paper text/figure checked; display idea only, no numerical values or artwork copied',
                              'default_template': False},
                'reproduce': f'python render_specialist.py --recipe {name} --input-folder {name} --output-dir brf-output --style forge',
                'creator': 'BatteryReviewForge original synthetic analytic demonstration'}
    (folder/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def render(name):
    folder = ROOT/name
    fig, report = render_recipe(name, folder)
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
