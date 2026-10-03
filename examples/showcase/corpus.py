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


def msd_diffusivity(temperature_C, electrolyte):
    """A known Brownian-model input, in Å²/ps; never a trajectory fit."""
    reference = {'A':.52/6, 'B':.31/6, 'C':.17/6}[electrolyte]
    return reference*np.exp(-.17/8.617333262e-5*(1/(temperature_C+273.15)-1/298.15))


def scientific_basis(name):
    normal=('https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm',
            'NIST e-Handbook: normal distribution','Gaussian mathematical bands only; no assignment or copied peak.')
    specs={
        'ftir': ('analytic_model',
            ['A(x)=-log10(0.92)+(0.09+0.012*index)*G(x;825+2.5*index,9)+(0.048-0.005*index)*G(x;758,6)+0.014*G(x;880,12)',
             'T_percent=100*10^(-A); A=-log10(T_percent/100)'],
            {'wavenumber_cm_1_range':[715,925], 'baseline_transmittance_percent':92,
             'samples':['A','B','C'], 'gaussian_widths_cm_1':[9,6,12]},
            ['Nonnegative additive absorbances with ideal Beer–Lambert transmission in a homogeneous, non-scattering medium.',
             'Absorbance strengths stand for original epsilon*c*l products; c, l and epsilon are not separately identified.'],
            ['Generic bands only; no compound identification, instrument response or measured concentration.'],
            [('https://goldbook.iupac.org/terms/view/B00626','IUPAC: Beer–Lambert law','Absorbance and transmittance relation; peak parameters are original.'),normal]),
        'nmr': ('phenomenological_model',
            ['L(x;mu,gamma)=1/(1+((x-mu)/gamma)^2)',
             'I(x)=L(x;-0.30+0.115*index,0.035+0.003*index)+0.08*L(x;0.42,0.075)',
             'Display-only offset=1.2 a.u. per series; raw intensities are unchanged'],
            {'chemical_shift_ppm_range':[-1,1], 'nucleus':'7Li-like teaching label',
             'reference':'original zero-point axis; no physical standard', 'samples':['A','B','C','D']},
            ['Generic absorptive Lorentzian bands, without phasing or integration claims.'],
            ['No molecular assignment, measured chemical shift, pulse sequence or T2 determination.'],
            [('https://goldbook.iupac.org/terms/view/L03628','IUPAC: Lorentzian band shape','Lorentzian half-width definition; original synthetic shifts and widths.')]),
        'rdf_coordination': ('analytic_model',
            ['g(r)=0 below 1.4 Å; above that: logistic((r-3.45)/0.23)+height*G(r;peak,0.18)',
             'CN(r)=4*pi*rho*integral_0^r[s^2*g(s) ds], stored using trapezoids on the same grid',
             'g(r)→1 in the far field; the excluded interval below the grid contributes zero to CN'],
            {'distance_A_range':[0.5,4.8], 'exclusion_A':1.4, 'cutoff_A':3.4,
             'pair_peak_A':[1.95,2.12,2.9], 'pair_number_density_A3':[0.025,0.012,0.007]},
            ['An isotropic analytic pair-distribution model with nonnegative g and declared neighbor number densities.'],
            ['No MD coordinates, uncertainty, chemical solvation-shell assignment or measured coordination number.'],
            [('https://manual.gromacs.org/current/reference-manual/analysis/radial-distribution-function.html',
              'GROMACS: radial distribution functions','RDF normalization and cumulative coordination relation; no GROMACS trajectory is supplied.')]),
        'msd': ('analytic_model',
            ['D(T)=D(298.15 K)*exp(-0.17 eV/kB*(1/T-1/298.15 K))',
             '<|r(t)-r(0)|^2>=6*D*t for isotropic three-dimensional drift-free Brownian motion',
             '1 Å²/ps=1e-4 cm²/s; D is a declared generator input, not fitted output'],
            {'dimensions':3, 'input_activation_energy_eV':0.17, 'reference_temperature_K':298.15,
             'input_D_A2_ps':{str(t):{s:float(msd_diffusivity(t,s)) for s in ('A','B','C')} for t in (25,-70)},
             'time_ps_range':[0,50]},
            ['The long-time Brownian relation is deliberately extended over this teaching grid.',
             'Temperature dependence is a chosen Arrhenius input; no actual electrolyte phase behavior is modeled.'],
            ['No MD trajectories or diffusion fit; no ballistic regime, confinement, crystallization or glass transition.',
             'The input D values are not measurements or chemistry predictions.'],
            [('https://manual.gromacs.org/current/reference-manual/analysis/mean-square-displacement.html',
              'GROMACS: mean square displacement','Three-dimensional Einstein relation; known model inputs are not simulated trajectories.'),
             ('https://goldbook.iupac.org/terms/view/A00446','IUPAC: Arrhenius equation','Temperature law only; original activation energy.')]),
        'lsv': ('analytic_model',
            ['j_anodic_uA_cm2=0.08+0.30*exp(alpha*F*(V-E0)/(R*T))',
             'E0_A,B,C=4.32,4.49,4.66 V; alpha=0.15, T=298.15 K'],
            {'alpha':0.15, 'j0_uA_cm2':0.30, 'baseline_uA_cm2':0.08,
             'R_J_mol_K':8.314462618, 'F_C_mol':96485.33212, 'temperature_K':298.15,
             'scan_rate_mV_s':0.1, 'reference':'Li/Li+', 'voltage_window_V':[3,5.1]},
            ['A one-way anodic charge-transfer term with negligible reverse product reaction and depletion.',
             'The baseline and forward-rate parameters are original; no onset threshold is assigned.'],
            ['No mass-transport limit, electrode passivation, iR correction, measured stability window or kinetic fit.',
             'A kinetic teaching turn-up is not a thermodynamic decomposition potential.'],
            [('https://www.gamry.com/electrochemistry-applications/cv-cyclic-voltammetry',
              'Gamry: electrochemical charge-transfer equations','The forward exponential term of charge-transfer kinetics, not a stability-window calibration.')]),
        'transference': ('analytic_model',
            ['I(t)=Iss+(I0-Iss)*exp(-t/95 s)',
             'Z(omega)=Rs+R_interface/(1+j*omega*R_interface*C); before/after R_interface is R0 and Rss',
             't_BV=Iss*(DeltaV-I0*R0)/(I0*(DeltaV-Iss*Rss)); current is converted mA→A'],
            {'DeltaV_V':0.01, 'tau_s':95, 'interface_C_F':5e-6, 'frequency_Hz_range':[1e6,1e-4],
             'series_R_ohm':{'A':18,'B':25}, 'interface_R0_ohm':{'A':65,'B':85},
             'interface_Rss_ohm':{'A':79.3,'B':103.7}, 'I0_mA':{'A':0.04,'B':0.05}, 'Iss_mA':{'A':0.03,'B':0.02}},
            ['Binary-electrolyte Bruce–Vincent-style demonstration with the supplied interfacial resistances.',
             'Semicircle diameter is R_interface; the separate Rs is not silently substituted for it.'],
            ['An apparent method-specific quantity, not a rigorous concentrated-solution transference measurement.',
             'No EIS optimizer, concentration corrections, activity coefficients or measured electrode evolution.'],
            [('https://doi.org/10.1016/0032-3861(87)90394-6','Evans, Vincent and Bruce: electrochemical measurement of transference numbers',
              'Resistance-corrected polarization method and its assumptions; all numeric inputs are original.'),
             ('https://www.gamry.com/application-notes/EIS/basics-of-electrochemical-impedance-spectroscopy/',
              'Gamry: electrochemical impedance spectroscopy','Ideal parallel-RC element and high/low-frequency resistance limits.')]),
    }
    model,equations,parameters,assumptions,limitations,sources=specs[name]
    return {'schema_version':1,'model_class':model,'data_origin':'original_synthetic',
            'equations':equations,'parameters':parameters,'assumptions':assumptions,
            'references':[{'url':u,'title':t,'supports':s,'scope':'model_definition_only'} for u,t,s in sources],
            'limitations':limitations,'validation_scope':'Declared teaching model and internal relationships only; no experimental or material certification.'}


def generate(name, output_root=None):
    if name not in CORPUS_RECIPES:
        raise ValueError(name)
    folder = Path(output_root or ROOT) / name
    folder.mkdir(exist_ok=True, parents=True)
    opt = {}
    data = []
    fields = []
    extra = []
    if name == 'ftir':
        x = np.linspace(715, 925, 500)
        for idx, sample in enumerate(('A', 'B', 'C')):
            absorbance = -np.log10(.92)+(0.09+idx*.012)*gaussian(x,825+idx*2.5,9)
            absorbance += (.048-idx*.005)*gaussian(x,758,6)+.014*gaussian(x,880,12)
            transmittance = 100*10**(-absorbance)
            data.extend((sample,float(xv),float(tv),float(av)) for xv,tv,av in zip(x,transmittance,absorbance))
        fields = ['sample', 'wavenumber_cm_1', 'transmittance_percent','absorbance']
        opt = {'zoom_wavenumber_cm_1': [790, 855], 'wavenumber_direction': 'descending'}
        conditions = 'Original additive Gaussian absorbances converted through T=100*10^(-A), 715–925 cm^-1; baseline 92%. Generic bands only; no chemical assignment, concentration or copied paper peak.'
    elif name == 'nmr':
        x = np.linspace(-1, 1, 550)
        for idx, sample in enumerate(('A', 'B', 'C', 'D')):
            y = 1/(1+((x-(-.30+idx*.115))/(.035+idx*.003))**2)+.08/(1+((x-.42)/.075)**2)
            data.extend((sample, float(xv), float(yv)) for xv, yv in zip(x, y))
        fields = ['sample', 'chemical_shift_ppm', 'intensity_au']
        opt = {'nucleus': '$^7$Li', 'chemical_shift_reference': 'Synthetic axis reference at 0 ppm; no real standard used',
               'display_offset_au': 1.2, 'zoom_chemical_shift_ppm': [-.55, .25]}
        conditions = 'Original generic absorptive Lorentzian spectra A–D on a 7Li-like ppm axis. No real chemical reference, pulse sequence, concentration, integration or molecular assignment.'
    elif name == 'rdf_coordination':
        x = np.linspace(.5, 4.8, 550)
        pairs = (('Li-O (solvent)', 1.95, 3.2, .025),
                 ('Li-O (anion)', 2.12, 2.1, .012),
                 ('Li-F (diluent)', 2.9, .7, .007))
        densities = {}
        for pair, peak, height, rho in pairs:
            # Excluded short-range region, first-shell peak and a far-field g(r) -> 1.
            gr = 1/(1+np.exp(-(x-3.45)/.23)) + height*gaussian(x, peak, .18)
            gr[x<1.4]=0
            integrand = x*x*gr
            cn = 4*np.pi*rho*np.r_[0, np.cumsum((integrand[1:]+integrand[:-1])*np.diff(x)/2)]
            densities[pair] = rho
            data.extend((pair, float(xv), float(gv), float(cv)) for xv, gv, cv in zip(x, gr, cn))
        fields = ['pair', 'distance_A', 'g_r', 'coordination_number']
        opt = {'species_definition': 'Invented Li-O (solvent), Li-O (anion), Li-F (diluent) pair labels',
               'coordination_source': 'Numerical trapezoidal integration of the same synthetic g(r) grid; g=0 below 1.4 Å, including the omitted 0–0.5 Å interval',
               'pair_number_density_A3': densities, 'coordination_cutoff_A': 3.4}
        conditions = 'Original isotropic pair-distribution model at nominal 25 °C, g=0 below 1.4 Å and g→1 far away. Pair densities are original Å^-3 inputs; CN=4πρ∫r²g(r)dr on the same grid. Not MD or an assigned chemical solvation shell.'
    elif name == 'msd':
        t = np.linspace(0, 50, 250)
        for temp in (25,-70):
            for electrolyte in ('A','B','C'):
                diffusivity=msd_diffusivity(temp,electrolyte)
                msd=6*diffusivity*t
                data.extend((temp,electrolyte,float(tv),float(mv),float(diffusivity)) for tv,mv in zip(t,msd))
        fields = ['temperature_C', 'electrolyte', 'time_ps', 'msd_A2','input_diffusivity_A2_ps']
        opt = {'simulated_species': 'Li+-like teaching label', 'simulation_method': 'Analytic 3D Brownian ensemble mean with known D; no trajectories or molecular dynamics',
               'diffusion_fit': False}
        conditions = 'Original drift-free 3D Brownian mean, MSD=6Dt, 25 and −70 °C, 0–50 ps. D is a stored input with a chosen 0.17 eV Arrhenius temperature law; no MD trajectories, fitted D or real electrolyte phase prediction.'
    elif name == 'lsv':
        x = np.linspace(3.0, 5.1, 450)
        for idx, electrolyte in enumerate(('A', 'B', 'C')):
            y = .08+.30*np.exp(.15*96485.33212*(x-(4.32+idx*.17))/(8.314462618*298.15))
            data.extend((electrolyte, float(xv), float(yv)) for xv, yv in zip(x, y))
        fields = ['electrolyte', 'voltage_V', 'current_density_uA_cm2']
        opt = {'working_electrode': 'Al, synthetic illustration only',
               'counter_reference_electrode': 'Li metal, synthetic illustration only',
               'scan_rate_mV_s': .1, 'zoom_voltage_V': [4.0, 4.9]}
        conditions = 'Original one-way anodic exponential response, nominal 25 °C, 0.1 mV/s, vs Li/Li+. Negligible reverse reaction/depletion assumed; no oxidation-onset or stability-window determination.'
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
            frequency=np.geomspace(1e6,1e-4,240)
            for stage, factor in (('before', 1), ('after', 1.22)):
                resistance=rct*factor
                z=rs+resistance/(1+1j*2*np.pi*frequency*resistance*5e-6)
                eis_rows.extend((name_i,stage,float(zv.real),float(-zv.imag),float(f)) for zv,f in zip(z,frequency))
        fields = ['electrolyte', 'time_s', 'current_mA']
        write_csv(folder/'eis.csv', ['electrolyte', 'stage', 'z_real_ohm', 'z_imag_negative_ohm','frequency_Hz'], eis_rows)
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
                'creator': 'BatteryReviewForge original synthetic analytic demonstration',
                'generator_version':'1.6','scientific_basis':scientific_basis(name)}
    (folder/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def render(name, input_root=None):
    folder = Path(input_root or ROOT) / name
    fig, report = render_recipe(name, folder)
    from batteryplot.qa import data_plot_checks
    checks = data_plot_checks(fig)
    report['actual_artist_checks'] = checks
    metadata = json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    metadata.update(generator_version='1.6', actual_artist_checks=checks)
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
