"""Six optional specialist demonstrations. Invented CSVs, never paper data.

Generation and rendering are separate so a redraw never regenerates inputs.
Run: python examples/showcase/advanced.py generate|render|publish|all
"""
import argparse
import csv
import json
from pathlib import Path
import shutil
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO/'skills/battery-review-figure/scripts'))
from batteryplot.specialist import BASE_RECIPES as RECIPES, render_recipe

SOURCES = {
 'cyclic_voltammetry': ('10.1038/s41467-023-40374-y', 'Fig. 2a–d and Supplementary Fig. 9', 'CV retains reference electrode and scan-rate identity; zoom is an optional editorial view'),
 'differential_capacity': ('10.1038/s41598-025-88019-y', 'Fig. 6a–f', 'Voltage profiles paired with differential capacity; demo uses an explicitly selected charge branch'),
 'gitt_pulse': ('10.1038/s43246-025-00866-4', 'Fig. 6a,b', 'Pulse potential and complete GITT trace; our current panel exposes the declared schedule, not a diffusion fit'),
 'ionic_conductivity': ('10.1038/s41467-024-45372-2', 'ionic transport figure, panels c,f', 'Conductivity and Arrhenius expression; no activation energy inferred in this demo'),
 'xps_components': ('10.1038/s41467-024-47522-y', 'Fig. 5a–d', 'XPS spectra and component fits; our labels remain generic because no chemical assignment is evidenced'),
 'raman_series': ('10.1038/s41467-024-47522-y', 'Fig. 3a,f', 'Raman spectra across electrolytes/states; offsets and zoom are disclosed optional display choices'),
}

GAUSSIAN_SOURCE = ('https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm',
                   'NIST e-Handbook: normal distribution',
                   'The Gaussian mathematical line shape only; no material peak assignment or numeric data.')
CV_SOURCE = ('https://www.gamry.com/electrochemistry-applications/cv-cyclic-voltammetry',
             'Gamry: cyclic voltammetry',
             'Triangular acquisition order and the square-root scan-rate trend, not these phenomenological peak shapes.')


def scientific_basis(name):
    """Keep model definitions distinct from the separately recorded figure grammar."""
    specs = {
        'cyclic_voltammetry': ('phenomenological_model',
            ['v follows an ordered 2.8→4.4→2.8 V triangular sweep',
             'g(v;mu,s)=exp(-0.5*((v-mu)/s)^2); amplitude=0.7*sqrt(scan_rate_mV_s)',
             'i_forward=(amplitude*g(v;3.90+0.035*log10(rate/0.1),0.10)+0.015*rate)*sin(pi*(v-2.8)/1.6)^2',
             'i_reverse=(-0.91*amplitude*g(v;3.66-0.025*log10(rate/0.1),0.115)-0.015*rate)*same_gate'],
            {'scan_rates_mV_s':[0.1,0.2,0.5,1.0], 'reference_electrode':'Li/Li+',
             'temperature_C':25, 'voltage_window_V':[2.8,4.4], 'peak_amplitude_coefficient_mA':0.7},
            ['Illustrative separated oxidation/reduction peaks with rate-dependent shifts.',
             'The endpoint gate is an explicit plotting fixture, not a diffusion solution.'],
            ['No reversible-couple kinetic fit, diffusion coefficient, active concentration or charge-balance inference.',
             'A sqrt(rate) amplitude trend alone does not establish diffusion control.'], [CV_SOURCE,GAUSSIAN_SOURCE]),
        'differential_capacity': ('phenomenological_model',
            ['L(v;mu,s)=1/(1+exp(-(v-mu)/s))',
             'Q(v)=10*(v-3)+scale*(75*L(v;3.64+shift,0.048)+100*L(v;4.04+shift,0.064)); Q=Q-Q(v=3)',
             'dQ/dV is the finite-difference derivative of the same stored charge-branch Q,V pairs'],
            {'cycles':[1,100,300], 'peak_shift_V':[0,0.015,0.04], 'accessible_capacity_scale':[1,0.96,0.89],
             'temperature_C':25, 'current_rate_C':0.1, 'capacity_basis':'cathode active mass', 'voltage_window_V':[3,4.35]},
            ['Two monotonic charge-capacity transitions plus a positive background slope.',
             'The cycle scale represents accessible active capacity, not a CE-derived inventory model.'],
            ['Charge branch only; not complete charge/discharge hysteresis or a named phase assignment.',
             'No smoothing, experimental uncertainty or measured degradation mechanism.'],
            [('https://www.nature.com/articles/s41598-025-88019-y','Charge profiles and differential capacity',
              'The definition and paired presentation of dQ/dV; no source numerical curve is copied.')]),
        'gitt_pulse': ('analytic_model',
            ['Q_passed_mAh=0.1*on_time_min/60',
             'du/dt=(Rp*I-u)/tau; exact interval update u_next=u*exp(-dt/tau)+Rp*I*(1-exp(-dt/tau))',
             'Ueq=3.22+0.011*on_time_min+0.03*tanh((on_time_min-38)/10)',
             'V_cell=Ueq+R0*I+u; I is in A in resistance terms'],
            {'pulse_current_mA':0.1, 'pulse_min':6, 'rest_min':24, 'pulses':12,
             'R0_ohm':340, 'Rp_ohm':850, 'tau_s':300, 'sampling_interval_s':12,
             'temperature_C':25, 'total_charge_mAh':0.12},
            ['One linear RC polarization mode plus an original monotonic OCV function.',
             'Current is held constant on each recorded time interval and the RC state carries across switches.'],
            ['A GITT schedule example, not a Fickian diffusion solution or a fitted diffusion coefficient.',
             'A finite rest does not prove equilibrium; no geometry or material identity is inferred.'],
            [('https://www.gamry.com/application-notes/EIS/basics-of-electrochemical-impedance-spectroscopy/',
              'Gamry: electrochemical impedance spectroscopy','Ideal resistor/capacitor element definitions; original OCV and pulse parameters.')]),
        'ionic_conductivity': ('analytic_model',
            ['sigma_S_cm=pre_S_cm*exp(-Ea_eV/(kB_eV_K*T_K)); T_K=T_C+273.15',
             'stored conductivity_mS_cm=1000*sigma_S_cm; Arrhenius axes are ln(sigma_S_cm) and 1000/T_K'],
            {'activation_energy_eV':{'A':0.20,'B':0.24,'C':0.29},
             'prefactor_S_cm':{'A':22,'B':40,'C':72}, 'kB_eV_K':8.617333262e-5,
             'temperature_C_range':[-20,80]},
            ['Single thermally activated transport law, constant prefactor and Ea within the stated range.'],
            ['No VTF behavior, phase transition, contact/geometry uncertainty or measured conductivity claim.',
             'Input Ea is known by construction and is not an experimentally fitted activation energy.'],
            [('https://goldbook.iupac.org/terms/view/A00446','IUPAC: Arrhenius equation','Exponential temperature law; original conductivity prefactors and energies.')]),
        'xps_components': ('phenomenological_model',
            ['G(e)=exp(-0.5*((e-mu)/sigma)^2); L(e)=1/(1+((e-mu)/sigma)^2)',
             'component=height*(0.7*G+0.3*L); expected_counts=110+3*(e-280)+sum(components)',
             'observed_counts ~ Poisson(expected_counts); residual=observed-background-sum(known_components)'],
            {'peak_centers_eV':[284.7,286.4,289.0], 'shape_width_eV':[0.50,0.64,0.71],
             'peak_heights_counts':[1000,460,270], 'lorentzian_fraction':0.3, 'random_seed':20260927},
            ['Nonnegative independent counting statistics on known generic components and a linear background.',
             'The mixture width is a shape parameter; it is not claimed as a common Gaussian/Lorentzian FWHM.'],
            ['No optimizer, fitted composition, charge calibration, Shirley/Tougaard background or chemical assignment.',
             'Components are known inputs; residuals are not evidence of a successful experimental fit.'],
            [GAUSSIAN_SOURCE,('https://goldbook.iupac.org/terms/view/L03628','IUPAC: Lorentzian band shape','Lorentzian mathematical shape only; original energies and intensities.')]),
        'raman_series': ('phenomenological_model',
            ['I_A-D(x)=45+0.14*(x-680)+(330-45*index)*G(x;730,4.5)+(100+55*index)*G(x;745+0.6*index,5.2)+55*G(x;783,6)',
             'Display-only offset = 340 counts per series; raw intensities are unchanged'],
            {'wavenumber_cm_1_range':[680,810], 'samples':['A','B','C','D'], 'offset_counts':340},
            ['Generic nonnegative band shapes and background; common acquisition scale is assumed.'],
            ['No molecule, solvation state, concentration, measured shift or peak-area calibration is assigned.'], [GAUSSIAN_SOURCE]),
    }
    model, equations, parameters, assumptions, limitations, sources = specs[name]
    return {'schema_version':1, 'model_class':model, 'data_origin':'original_synthetic',
            'equations':equations, 'parameters':parameters, 'assumptions':assumptions,
            'references':[{'url':url,'title':title,'supports':supports,'scope':'model_definition_only'} for url,title,supports in sources],
            'limitations':limitations, 'validation_scope':'Declared teaching model and internal relationships only; no experimental or material certification.'}


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream); writer.writerow(fields); writer.writerows(rows)


def generate(name, output_root=None):
    folder = Path(output_root or ROOT)/name; folder.mkdir(exist_ok=True, parents=True)
    g = lambda x, mu, width: np.exp(-.5*((x-mu)/width)**2)
    options, units = {}, {}
    if name == 'cyclic_voltammetry':
        rows=[]
        for rate in (.1,.2,.5,1):
            v = np.r_[np.linspace(2.8,4.4,400), np.linspace(4.4,2.8,400)[1:]]
            forward = np.arange(len(v)) < 400
            gate = np.sin(np.pi*(v-2.8)/1.6)**2
            amp = .7*np.sqrt(rate)
            current = np.where(forward, amp*g(v,3.90+.035*np.log10(rate/.1),.10)+.015*rate,
                               -amp*.91*g(v,3.66-.025*np.log10(rate/.1),.115)-.015*rate)*gate
            rows += [[rate,i,float(x),float(y)] for i,(x,y) in enumerate(zip(v,current))]
        fields=['scan_rate_mV_s','sequence','voltage_V','current_mA']
        options={'reference_electrode':'Li/Li+', 'zoom_voltage_V':[3.45,4.15]}
        conditions='Invented intercalation half-cell response at 25 °C, 2.8–4.4 V vs Li/Li+; 0.1, 0.2, 0.5, 1 mV/s. Analytic visual model, not measured kinetics.'
    elif name == 'differential_capacity':
        rows=[]
        for cycle,shift,scale in ((1,0,1),(100,.015,.96),(300,.04,.89)):
            v=np.linspace(3,4.35,650)
            q=10*(v-3)+scale*(75/(1+np.exp(-(v-3.64-shift)/.048))+100/(1+np.exp(-(v-4.04-shift)/.064)))
            q-=q[0]
            rows += [[cycle,float(x),float(y)] for x,y in zip(v,q)]
        fields=['cycle','voltage_V','capacity_mAh_g']; options={'branch':'charge'}
        conditions='Invented charge-only curves, 25 °C, 0.1 C, specific capacity per cathode active mass. The derivative is computed from these same CSV values without smoothing.'
    elif name == 'gitt_pulse':
        t=np.arange(0,360.01,.2); segment=np.minimum(np.floor(t/30),11); phase=t-segment*30
        on=phase<6; passed=segment*6+np.minimum(phase,6)
        ocv=3.22+.011*passed+.03*np.tanh((passed-38)/10)
        current=np.where(on,.1,0)
        # One RC state, propagated through every pulse/rest interval. Only the
        # ohmic term jumps when the commanded current switches.
        polarization=np.zeros_like(t)
        for i, dt_s in enumerate(np.diff(t)*60):
            decay=np.exp(-dt_s/300)
            polarization[i+1]=polarization[i]*decay+850*(current[i]/1000)*(1-decay)
        rows=zip(t,ocv+340*current/1000+polarization,current,passed*.1/60,ocv,polarization)
        fields=['time_min','voltage_V','current_mA','passed_charge_mAh','equilibrium_model_V','rc_polarization_V']
        options={'pulse_min':6,'rest_min':24,'diffusion_calculation':False}
        conditions='Original RC charging model: 0.1 mA for 6 min, 24 min rest, 12 pulses, 25 °C; 0.12 mAh passed. Recorded OCV is a known model state, not a measured equilibrium or diffusion fit.'
    elif name == 'ionic_conductivity':
        rows=[]
        for sample,ea,pre in (('A',.20,22),('B',.24,40),('C',.29,72)):
            for t in np.arange(-20,81,10):
                sigma=pre*np.exp(-ea/(8.617333262e-5*(t+273.15)))
                rows.append([sample,t,sigma*1000])
        fields=['sample','temperature_C','conductivity_mS_cm']
        options={'arrhenius_expression':'ln(sigma_S_cm) vs 1000/T_K','fit':False}
        conditions='Invented A/B/C electrolyte conductivity; Arrhenius model over −20 to 80 °C. Geometry/contact uncertainties absent because this is not an impedance measurement.'
    elif name == 'xps_components':
        e=np.linspace(280,294,500); background=110+3*(e-280)
        peak=lambda mu,width: .7*g(e,mu,width)+.3/(1+((e-mu)/width)**2)
        parts=[1000*peak(284.7,.50),460*peak(286.4,.64),270*peak(289,.71)]
        rng=np.random.default_rng(20260927)
        expected=background+sum(parts)
        observed=rng.poisson(expected)
        rows=zip(e,observed,background,*parts,expected)
        fields=['binding_energy_eV','intensity_counts','background_counts','component_1','component_2','component_3','expected_counts']
        options={'component_labels':['Component 1','Component 2','Component 3'], 'fit_method':'Known Gaussian/Lorentzian mixtures plus Poisson counts; no optimizer', 'charge_reference':'Synthetic energy axis; no measured calibration'}
        conditions='Original generic 280–294 eV window with 3 known mixed-line-shape components and counting noise. No compound identity, measured composition or fitting quality claim.'
    else:
        rows=[]
        x=np.linspace(680,810,600)
        for idx,sample in enumerate(('A','B','C','D')):
            y=45+.14*(x-680)+(330-45*idx)*g(x,730,4.5)+(100+55*idx)*g(x,745+idx*.6,5.2)+55*g(x,783,6)
            rows += [[sample,float(v),float(yv)] for v,yv in zip(x,y)]
        fields=['sample','wavenumber_cm_1','intensity_counts']
        options={'display_offset_counts':340,'zoom_wavenumber_cm_1':[718,762]}
        conditions='Invented electrolyte-like Raman windows, A–D; unnormalized counts preserved, display offset 340 counts per series. No molecular assignment or concentration inference.'
    write_csv(folder/'data.csv', fields, rows)
    doi,panel,observation=SOURCES[name]
    metadata={'data_status':'synthetic_demo', 'not_experimental_data':True,
              'figure_grammar_id':f'optional:{name}', 'source_files':['data.csv'],
              'test_conditions':conditions, 'variables_and_units':fields, 'render_options':options,
              'reference':{'doi':doi,'panel':panel,'observation':observation,
                           'review_scope':'publisher text/caption; no numerical data or original artwork copied',
                           'default_template':False},
              'reproduce':f'python render_specialist.py --recipe {name} --input-folder {name} --output-dir brf-output --style forge',
              'creator':'BatteryReviewForge original synthetic model and drawing',
              'generator_version':'1.6','scientific_basis':scientific_basis(name)}
    (folder/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def render(name, input_root=None):
    folder=Path(input_root or ROOT)/name
    fig, report=render_recipe(name,folder)
    from batteryplot.qa import data_plot_checks
    checks = data_plot_checks(fig)
    report['actual_artist_checks'] = checks
    metadata = json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    metadata.update(generator_version='1.6', actual_artist_checks=checks)
    (folder/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with matplotlib.rc_context(fig.brf_export_rc):
        for suffix in ('png','svg','pdf'): fig.savefig(folder/f'figure.{suffix}',dpi=300,facecolor='white')
    plt.close(fig)
    # Avoid exporting machine-specific font paths in public source records.
    report['resolved_font_path']=Path(report['resolved_font_path']).name
    (folder/'render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (folder/'alignment.json').write_text(json.dumps(report['alignment'],indent=2)+'\n',encoding='utf-8')


def publish(name):
    dest=REPO/'docs/assets/showcase'/name; dest.mkdir(exist_ok=True,parents=True)
    for path in (ROOT/name).iterdir():
        if path.suffix in ('.csv','.json','.png','.svg','.pdf'): shutil.copy2(path,dest/path.name)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('generate','render','publish','all'))
    parser.add_argument('--name',choices=RECIPES)
    args=parser.parse_args()
    for name in ([args.name] if args.name else RECIPES):
        for stage in ('generate','render','publish'):
            if args.action in (stage,'all'): globals()[stage](name)
        print(args.action,name)
