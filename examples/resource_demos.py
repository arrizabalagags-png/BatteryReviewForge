"""Deterministic teaching data, never experimental measurements.

Run: python resource_demos.py --output OUTPUT
The same renderer is included inside each downloadable example.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SEED = 20260930
RECIPES = [
    ('na_metal_ce', '钠金属逐圈 CE', 'alkali', 'ce', 'Na|Cu; illustrative 1 mA/cm2, 1 mAh/cm2; stripping endpoint must be declared'),
    ('k_ion_rate', '钾离子倍率与恢复', 'alkali', 'rate', 'Invented K-ion cell; capacity per gram of illustrative active material; rate in mA/g'),
    ('zn_plating_ce', 'Zn|Cu 镀剥逐圈 CE', 'zinc', 'ce', 'Zn|Cu; illustrative 1 mA/cm2, 1 mAh/cm2; aqueous electrolyte is unspecified'),
    ('zn_symmetric', 'Zn|Zn 对称电池极化', 'zinc', 'symmetric', 'Illustrative Zn|Zn; 1 mA/cm2, alternating 1 h half-cycles; no lifetime inference'),
    ('zn_air_power', 'Zn-air 极化与功率密度', 'zinc', 'polarization', 'Invented discharge curve; geometric air electrode area basis; p=jV'),
    ('zn_i2_cycle', 'Zn-I₂ 长循环与 CE', 'zinc', 'cycling', 'Invented Zn-I2; capacity per gram of iodine; iodine loading and electrolyte must be supplied for real data'),
    ('flow_efficiency', '液流电池效率关系', 'storage', 'efficiency', 'Invented flow cell; CE=Qdis/Qchg, VE=Vdis_mean/Vchg_mean, EE=CE*VE; no named chemistry'),
    ('pv_jv', '光伏 J–V 与最大功率', 'photovoltaic', 'jv', 'Illustrative 100 mW/cm2 incident light; 25 C; steady toy curve, no hysteresis or device efficiency claim'),
    ('pv_stability', '光伏稳态功率与稳定性', 'photovoltaic', 'stability', 'Invented fixed operating point; normalized to t=0; temperature and atmosphere required for real tests'),
    ('pv_trpl', 'TRPL 原始信号与衰减', 'general', 'trpl', 'Synthetic biexponential decay; no instrument response, no fitted lifetime or mechanistic conclusion'),
]


def data(kind, rng):
    if kind == 'ce':
        x = np.arange(1, 201); charge = np.ones(len(x)); ce = 98.4 + .9*(1-np.exp(-x/25)) + rng.normal(0,.11,len(x))
        ce[145:151] -= np.linspace(.2, 1.3, 6)
        return ['cycle','q_plating_mAh_cm2','q_stripping_mAh_cm2','ce_percent'], np.column_stack([x,charge,charge*ce/100,ce])
    if kind == 'rate':
        x = np.arange(1, 61); current = np.repeat([50,100,200,500,1000,50],10)
        q = np.repeat([245,220,189,151,112,237],10)+rng.normal(0,2,len(x))
        return ['cycle','current_mA_g','capacity_mAh_g'], np.column_stack([x,current,q])
    if kind == 'symmetric':
        x = np.arange(0, 120, .05); half = np.floor(x).astype(int); v = np.where(half % 2 == 0, 1.,-1.)*(35+.13*x+5*np.exp(-(x%1)/.04))
        return ['time_h','overpotential_mV'], np.column_stack([x,v])
    if kind == 'polarization':
        j = np.linspace(0,350,176); v=1.58-.002*j-.075*np.log1p(j)
        return ['current_density_mA_cm2','voltage_V','power_density_mW_cm2'], np.column_stack([j,v,j*v])
    if kind == 'cycling':
        x=np.arange(1,501); q=175*np.exp(-x/1600)+rng.normal(0,.8,len(x)); ce=99.2+rng.normal(0,.1,len(x))
        return ['cycle','capacity_mAh_g_iodine','ce_percent'], np.column_stack([x,q,ce])
    if kind == 'efficiency':
        x=np.arange(1,151); ce=(.982-.00002*x); ve=(.84-.0003*x)
        return ['cycle','ce_percent','ve_percent','ee_percent'], np.column_stack([x,ce*100,ve*100,ce*ve*100])
    if kind == 'jv':
        v=np.linspace(0,1.1,221); j=23.5*(1-(v/1.08)**9); p=v*j
        return ['voltage_V','current_density_mA_cm2','power_density_mW_cm2'], np.column_stack([v,j,p])
    if kind == 'stability':
        x=np.linspace(0,1000,201); p=1-.10*(x/1000)**.75+.002*np.sin(x/27); p[0]=1
        return ['time_h','normalized_power'], np.column_stack([x,p])
    x=np.linspace(0,400,401); signal=.7*np.exp(-x/18)+.3*np.exp(-x/90)+.002
    return ['time_ns','signal_a_u'], np.column_stack([x,signal])


def draw(kind, fields, values, target):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':True,'axes.spines.right':True,'axes.spines.bottom':True,'axes.spines.left':True})
    panels = 2 if kind in {'rate','polarization','cycling','jv'} else 1
    fig, axes=plt.subplots(1,panels,figsize=(7.087,3.1),layout='constrained'); axes=np.atleast_1d(axes); a=axes[0]
    x=values[:,0]
    if kind=='ce': a.plot(x,values[:,3],color='#185cbd',lw=1); a.set(xlabel='Cycle',ylabel='Coulombic efficiency (%)')
    elif kind=='rate':
        a.plot(x,values[:,2],'-',marker=None,color='#185cbd'); a.set(xlabel='Cycle',ylabel='Capacity (mAh g$^{-1}$)')
        axes[1].step(x,values[:,1],where='mid',color='#187f84'); axes[1].set(xlabel='Cycle',ylabel='Current (mA g$^{-1}$)')
    elif kind=='symmetric': a.plot(x,values[:,1],color='#185cbd',lw=.7); a.set(xlabel='Time (h)',ylabel='Overpotential (mV)')
    elif kind=='polarization':
        a.plot(x,values[:,1],color='#185cbd'); a.set(xlabel='Current density (mA cm$^{-2}$)',ylabel='Voltage (V)')
        axes[1].plot(x,values[:,2],color='#187f84'); axes[1].set(xlabel='Current density (mA cm$^{-2}$)',ylabel='Power density (mW cm$^{-2}$)')
    elif kind=='cycling':
        a.plot(x,values[:,1],color='#185cbd',lw=1); a.set(xlabel='Cycle',ylabel='Capacity (mAh g$^{-1}_{iodine}$)')
        axes[1].plot(x,values[:,2],color='#187f84',lw=1); axes[1].set(xlabel='Cycle',ylabel='CE (%)')
    elif kind=='efficiency':
        for i,label,c in [(1,'CE','#185cbd'),(2,'VE','#187f84'),(3,'EE','#a85e37')]: a.plot(x,values[:,i],label=label,color=c)
        a.legend(frameon=False); a.set(xlabel='Cycle',ylabel='Efficiency (%)')
    elif kind=='jv':
        a.plot(x,values[:,1],color='#185cbd'); a.axhline(0,color='#59687c',lw=.7); a.set(xlabel='Voltage (V)',ylabel='Current density (mA cm$^{-2}$)')
        axes[1].plot(x,values[:,2],color='#187f84'); m=np.argmax(values[:,2]); axes[1].annotate('MPP',(x[m],values[m,2]),xytext=(4,6),textcoords='offset points',fontsize=8,color='#a85e37'); axes[1].set(xlabel='Voltage (V)',ylabel='Power density (mW cm$^{-2}$)')
    elif kind=='stability': a.plot(x,values[:,1],color='#185cbd'); a.set(xlabel='Time (h)',ylabel='Power / initial power')
    else: a.semilogy(x,values[:,1],color='#185cbd'); a.set(xlabel='Time (ns)',ylabel='Signal (a.u.)')
    checks=[]
    for i, ax in enumerate(axes):
        frame={side:ax.spines[side].get_visible() for side in ('top','right','bottom','left')}
        if not all(frame.values()): raise ValueError('Data axes must show four frame spines')
        for trace in ax.lines:
            if trace.get_linestyle()!='-' or trace.get_marker() not in (None,'None','',' '):
                raise ValueError('Continuous curves must be solid without markers')
        checks.append({'panel':i,'frame_spines':frame,'curve_styles':[
            {'linestyle':line.get_linestyle(),'marker':line.get_marker(),'points':len(line.get_xdata())}
            for line in ax.lines]})
        if panels>1: ax.text(-.16,1.05,chr(97+i),transform=ax.transAxes,weight='bold')
        ax.margins(x=.02)
    for fmt in ['svg','pdf','png']: fig.savefig(target / f'figure.{fmt}',dpi=160,facecolor='white')
    plt.close(fig)
    return checks


def validate_demo(kind, fields, values, expected):
    if fields != expected or values.ndim != 2 or values.shape[0] < 2 or values.shape[1] != len(expected) or not np.all(np.isfinite(values)):
        raise ValueError('Teaching input requires the declared columns and at least two finite, complete rows')
    if np.any(np.diff(values[:,0]) <= 0):
        raise ValueError('Teaching coordinate must increase without duplicate rows')
    if kind == 'ce':
        if np.any(values[:,1] <= 0) or not np.allclose(values[:,3],values[:,2]/values[:,1]*100):
            raise ValueError('Teaching CE must match stripping/plating capacity')
    if kind in {'polarization','jv'} and not np.allclose(values[:,2],values[:,0]*values[:,1]):
        raise ValueError('Teaching power must match the declared current and voltage units')
    if kind == 'efficiency' and not np.allclose(values[:,3],values[:,1]*values[:,2]/100):
        raise ValueError('Teaching EE must equal CE times VE on the percent scale')


def main():
    p=argparse.ArgumentParser(description='Synthetic teaching examples only; use a contracted plot pack for experimental inputs.')
    p.add_argument('--output',type=Path,required=True); p.add_argument('--recipe',choices=[r[0] for r in RECIPES]); p.add_argument('--demo-input','--input',dest='input',type=Path,help='Replay a teaching CSV, not experimental data')
    p.add_argument('--replace-demo',action='store_true',help='Maintainer opt-in to rebuilding known demonstration assets')
    args=p.parse_args()
    if args.input and not args.recipe: p.error('--demo-input requires one --recipe')
    if args.output.exists() and any(args.output.iterdir()) and not args.replace_demo:
        base=args.output;counter=2
        while args.output.exists(): args.output=base.with_name(base.name+f'_v{counter:03d}');counter+=1
    for index,(slug,title,domain,kind,conditions) in enumerate(RECIPES):
        if args.recipe and args.recipe!=slug: continue
        folder=args.output/slug
        if args.input:
            with args.input.open(encoding='utf-8-sig',newline='') as handle: rows=list(csv.reader(handle))
            fields=rows[0]; values=np.array(rows[1:],dtype=float)
            expected=data(kind,np.random.default_rng(SEED+index))[0]
            validate_demo(kind,fields,values,expected)
        else: fields,values=data(kind,np.random.default_rng(SEED+index))
        validate_demo(kind,fields,values,data(kind,np.random.default_rng(SEED+index))[0])
        folder.mkdir(parents=True,exist_ok=True)
        with (folder/'data.csv').open('w',encoding='utf-8',newline='') as handle:
            w=csv.writer(handle); w.writerow(fields); w.writerows(values)
        frame_checks=draw(kind,fields,values,folder)
        shutil.copyfile(__file__,folder/'render.py')
        meta={'id':slug,'title':title,'domain':domain,'type':'demo','data_status':'synthetic_demo','not_experimental_data':True,'random_seed':SEED+index,'source_files':['data.csv'],'variables_and_units':fields,'test_conditions':conditions,'render_options':{'recipe':slug},'reproduce':f'python render.py --output rebuilt --recipe {slug} --demo-input data.csv','creator':'VoltPeer maintainers','license':'MIT','generator_version':'0.10.0','limitations':'Toy teaching replay only; no model fit, measured device, or scientific validation. This generator does not adapt experimental data.'}
        meta['actual_artist_checks']=frame_checks
        (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'README.txt').write_text(f'{title}\nAll numeric data are synthetic teaching values. Never use them as experimental results.\n{meta["reproduce"]}\nRequires Python >=3.10, numpy and matplotlib in an isolated environment.\n',encoding='utf-8')
        with ZipFile(args.output/f'BRF-demo-{slug}.zip','w',ZIP_DEFLATED) as z:
            z.writestr('README.txt',f'Open {slug}/README.txt, metadata.json and data.csv.\nSynthetic teaching data only.\n')
            for file in sorted(folder.iterdir()): z.write(file,f'{slug}/{file.name}')
    print('Generated explicitly synthetic domain examples.')


if __name__=='__main__': main()
