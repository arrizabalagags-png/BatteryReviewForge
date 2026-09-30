"""Generate six independent synthetic demos for optional corpus grammars.

Run: python examples/showcase/corpus.py generate|render|all [--name RECIPE]
Rendering never regenerates data. No publisher figure coordinates or artwork.
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
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / 'skills/battery-review-figure/scripts'))
from batteryplot.corpus import CORPUS_RECIPES
from batteryplot.specialist import render_recipe

SOURCES = {
    'ftir': ('10.1002/aenm.202101775', 'Advanced Energy Materials', 2021,
             'Figure 1c', 'Overlaid FTIR transmittance spectra; this demo does not reuse measured peaks or assignments.'),
    'nmr': ('10.1016/j.cej.2022.139398', 'Chemical Engineering Journal', 2023,
            'Fig. 1b', 'Vertically offset 7Li NMR comparison; synthetic shifts are not the published shifts.'),
    'rdf_coordination': ('10.1016/j.cej.2022.139398', 'Chemical Engineering Journal', 2023,
                         'Fig. 1d-f', 'RDF and cumulative coordination on distinct axes; synthetic curves are not MD results.'),
    'msd': ('10.1002/anie.201900266', 'Angewandte Chemie International Edition', 2019,
            'Figure 3c,d', 'Two-temperature Li+ MSD comparison; synthetic slopes have no measured diffusion meaning.'),
    'lsv': ('10.1016/j.cej.2022.139398', 'Chemical Engineering Journal', 2023,
            'Fig. 1a', 'Shared-axis electrolyte LSV traces; synthetic current/voltage values are not published results.'),
    'transference': ('10.1002/aenm.202101775', 'Advanced Energy Materials', 2021,
                    'Figure 6c', 'Current polarization paired with before/after EIS; synthetic known parameters only.'),
}


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        writer.writerows(rows)


def gaussian(x, center, width):
    return np.exp(-.5*((x-center)/width)**2)


def generate(name):
    if name not in CORPUS_RECIPES:
        raise ValueError(name)
    folder = ROOT / name
    folder.mkdir(exist_ok=True)
    opt = {}
    data = []
    fields = []
    extra = []
    if name == 'ftir':
        x = np.linspace(715, 925, 500)
        for idx, sample in enumerate(('A', 'B', 'C')):
            y = 92 - (16+idx*2)*gaussian(x, 825+idx*2.5, 9) - (9-idx)*gaussian(x, 758, 6)
            y -= 3*gaussian(x, 880, 12)
            data.extend((sample, float(xv), float(yv)) for xv, yv in zip(x, y))
        fields = ['sample', 'wavenumber_cm_1', 'transmittance_percent']
        opt = {'zoom_wavenumber_cm_1': [790, 855], 'wavenumber_direction': 'descending'}
        conditions = 'Synthetic A/B/C electrolyte-like transmittance, 715-925 cm^-1. Gaussian troughs are visual examples only; no chemical assignment, measured transmittance or paper peak position.'
    elif name == 'nmr':
        x = np.linspace(-1, 1, 550)
        for idx, sample in enumerate(('A', 'B', 'C', 'D')):
            y = gaussian(x, -.30+idx*.115, .035+idx*.003) + .08*gaussian(x, .42, .075)
            data.extend((sample, float(xv), float(yv)) for xv, yv in zip(x, y))
        fields = ['sample', 'chemical_shift_ppm', 'intensity_au']
        opt = {'nucleus': '$^7$Li', 'chemical_shift_reference': 'Synthetic axis reference at 0 ppm; no real standard used',
               'display_offset_au': 1.2, 'zoom_chemical_shift_ppm': [-.55, .25]}
        conditions = 'Synthetic 7Li-like spectra A-D with invented positions and widths. No pulse sequence, concentration, integration or molecular assignment implied.'
    elif name == 'rdf_coordination':
        x = np.linspace(.5, 4.8, 550)
        pairs = (('Li-O (solvent)', 1.95, 3.2, .025),
                 ('Li-O (anion)', 2.12, 2.1, .012),
                 ('Li-F (diluent)', 2.9, .7, .007))
        densities = {}
        for pair, peak, height, rho in pairs:
            # Excluded short-range region, first-shell peak and a far-field g(r) -> 1.
            gr = 1/(1+np.exp(-(x-3.45)/.23)) + height*gaussian(x, peak, .18)
            integrand = x*x*gr
            cn = 4*np.pi*rho*np.r_[0, np.cumsum((integrand[1:]+integrand[:-1])*np.diff(x)/2)]
            densities[pair] = rho
            data.extend((pair, float(xv), float(gv), float(cv)) for xv, gv, cv in zip(x, gr, cn))
        fields = ['pair', 'distance_A', 'g_r', 'coordination_number']
        opt = {'species_definition': 'Invented Li-O (solvent), Li-O (anion), Li-F (diluent) pair labels',
               'coordination_source': 'Numerical trapezoidal integration of the synthetic g(r) grid from 0.5 Å using stated pair densities',
               'pair_number_density_A3': densities, 'coordination_cutoff_A': 3.4}
        conditions = 'Synthetic pair-distribution curves at nominal 25 °C: short-range exclusion and far-field g(r) approaching 1. Pair densities are invented and in Å^-3; CN is 4πρ∫r²g(r)dr from 0.5 Å. Not an MD trajectory or quantitative solvation shell.'
    elif name == 'msd':
        t = np.linspace(0, 50, 250)
        for temp, scale in ((25, 1.0), (-70, .29)):
            for electrolyte, slope in (('A', .52), ('B', .31), ('C', .17)):
                msd = scale*slope*t*(1+.025*np.sin(t/6))
                data.extend((temp, electrolyte, float(tv), float(mv)) for tv, mv in zip(t, msd))
        fields = ['temperature_C', 'electrolyte', 'time_ps', 'msd_A2']
        opt = {'simulated_species': 'Li+', 'simulation_method': 'Invented analytic trajectories; not molecular dynamics',
               'diffusion_fit': False}
        conditions = 'Synthetic Li+-like mean-square displacement at 25 and -70 °C over 0-50 ps. No simulation box, ensemble, uncertainty or diffusion coefficient claim.'
    elif name == 'lsv':
        x = np.linspace(3.0, 5.1, 450)
        for idx, electrolyte in enumerate(('A', 'B', 'C')):
            y = .08 + (1.8+idx*.3)*np.logaddexp(0, (x-(4.32+idx*.17))*14)
            data.extend((electrolyte, float(xv), float(yv)) for xv, yv in zip(x, y))
        fields = ['electrolyte', 'voltage_V', 'current_density_uA_cm2']
        opt = {'working_electrode': 'Al, synthetic illustration only',
               'counter_reference_electrode': 'Li metal, synthetic illustration only',
               'scan_rate_mV_s': .1, 'zoom_voltage_V': [4.0, 4.9]}
        conditions = 'Synthetic Li||Al-like oxidative sweep at nominal 25 °C and 0.1 mV/s; all current densities and turn-up positions invented. No onset or stability-window determination.'
    else:
        t = np.linspace(0, 2000, 300)
        specs = [('A', .04, .03, 18, 65), ('B', .05, .02, 25, 85)]
        known = {}
        eis_rows = []
        for name_i, initial, steady, rs, rct in specs:
            current = steady + (initial-steady)*np.exp(-t/95)
            data.extend((name_i, float(tv), float(iv)) for tv, iv in zip(t, current))
            known[name_i] = {'polarization_voltage_V': .01,
                             'initial_current_mA': initial, 'steady_current_mA': steady,
                             'initial_resistance_ohm': rct, 'steady_resistance_ohm': rct*1.22}
            theta = np.linspace(0, np.pi, 100)
            for stage, factor in (('before', 1), ('after', 1.22)):
                zr = rs + rct*factor*(1-np.cos(theta))/2
                zi = rct*factor*np.sin(theta)/2
                eis_rows.extend((name_i, stage, float(x), float(y)) for x, y in zip(zr, zi))
        fields = ['electrolyte', 'time_s', 'current_mA']
        write_csv(folder/'eis.csv', ['electrolyte', 'stage', 'z_real_ohm', 'z_imag_negative_ohm'], eis_rows)
        extra = ['eis.csv']
        opt = {'calculation_method': 'Bruce-Vincent style, supplied ΔV/I0/Iss/R0/Rss only',
               'known_parameters': known}
        conditions = 'Synthetic polarization transients and before/after EIS for A/B at nominal 25 °C, 10 mV. Explicit resistance parameters match invented semicircle diameters; tLi+ is not an Isteady/Iinitial ratio.'
    write_csv(folder/'data.csv', fields, data)
    doi, journal, year, panel, observation = SOURCES[name]
    metadata = {'data_status': 'synthetic_demo', 'not_experimental_data': True,
                'figure_grammar_id': f'optional:{name}', 'source_files': ['data.csv']+extra,
                'test_conditions': conditions, 'variables_and_units': fields,
                'render_options': opt,
                'reference': {'doi': doi, 'journal': journal, 'year': year,
                              'figure_panel': panel, 'observation': observation,
                              'review_scope': 'Original PDF figure and caption visually checked; no numerical values or artwork copied',
                              'default_template': False},
                'reproduce': f'python render_specialist.py --recipe {name} --input-folder {name} --output-dir brf-output --style forge',
                'creator': 'BatteryReviewForge original synthetic analytic demonstration'}
    (folder/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def render(name):
    folder = ROOT / name
    fig, report = render_recipe(name, folder)
    from batteryplot.qa import data_plot_checks
    checks = data_plot_checks(fig)
    report['actual_artist_checks'] = checks
    metadata = json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    metadata.update(generator_version='1.5', actual_artist_checks=checks)
    (folder/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with matplotlib.rc_context(fig.brf_export_rc):
        for suffix in ('png', 'svg', 'pdf'):
            fig.savefig(folder/f'figure.{suffix}', dpi=300, facecolor='white')
    plt.close(fig)
    report['resolved_font_path'] = Path(report['resolved_font_path']).name
    (folder/'render-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (folder/'alignment.json').write_text(json.dumps(report['alignment'], indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('generate', 'render', 'all'))
    parser.add_argument('--name', choices=CORPUS_RECIPES)
    args = parser.parse_args()
    for recipe in ([args.name] if args.name else CORPUS_RECIPES):
        if args.action in ('generate', 'all'): generate(recipe)
        if args.action in ('render', 'all'): render(recipe)
        print(args.action, recipe)
