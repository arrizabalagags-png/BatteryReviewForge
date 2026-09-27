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


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream); writer.writerow(fields); writer.writerows(rows)


def generate(name):
    folder = ROOT/name; folder.mkdir(exist_ok=True)
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
        eta=np.where(on,.034+.085*(1-np.exp(-phase/2)), .085*(1-np.exp(-3))*np.exp(-(phase-6)/5))
        rows=zip(t,ocv+eta,np.where(on,.1,0))
        fields=['time_min','voltage_V','current_mA']
        options={'pulse_min':6,'rest_min':24,'diffusion_calculation':False}
        conditions='Invented charging pulse schedule: 0.1 mA for 6 min, 24 min rest, 12 pulses, 25 °C. Relaxation model only; no diffusion coefficient or equilibrium claim.'
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
        parts=[1000*g(e,284.7,.50),460*g(e,286.4,.64),270*g(e,289,.71)]
        rng=np.random.default_rng(20260927)
        observed=background+sum(parts)+rng.normal(0,9,len(e))
        rows=zip(e,observed,background,*parts)
        fields=['binding_energy_eV','intensity_counts','background_counts','component_1','component_2','component_3']
        options={'component_labels':['Component 1','Component 2','Component 3'], 'fit_method':'Analytic invented components; no optimizer', 'charge_reference':'Synthetic energy axis; no measured calibration'}
        conditions='Invented C 1s-like binding-energy window, counts and 3 Gaussian components with known baseline. No compound identity, measured composition or fitting quality claim.'
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
              'creator':'BatteryReviewForge original synthetic model and drawing'}
    (folder/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def render(name):
    folder=ROOT/name
    fig, report=render_recipe(name,folder)
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
