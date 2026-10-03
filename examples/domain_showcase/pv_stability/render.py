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
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from series_policy import apply_series_policy, check_series_policy
except ImportError:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/voltpeer-plot/scripts'))
    from batteryplot.series_policy import apply_series_policy, check_series_policy

SEED = 20260930
RECIPES = [
    ('na_metal_ce', '钠金属逐圈 CE', 'alkali', 'ce', 'Original Na|Cu teaching charge ledger; 1 mA/cm2, 1 mAh/cm2 plated, nominal 1 V vs Na/Na+ stripping endpoint; no voltage trace or experimental protocol validation'),
    ('k_ion_rate', '钾离子倍率与恢复', 'alkali', 'rate', 'Original working-electrode capacity model vs excess K metal; capacity per gram of unnamed active material, current in mA/g; not a full-cell energy or material record'),
    ('zn_plating_ce', 'Zn|Cu 镀剥逐圈 CE', 'zinc', 'ce', 'Original Zn|Cu teaching charge ledger; 1 mA/cm2, 1 mAh/cm2 plated, nominal 0.5 V vs Zn/Zn2+ stripping endpoint; unnamed aqueous electrolyte, no voltage trace'),
    ('zn_symmetric', 'Zn|Zn 对称电池极化', 'zinc', 'symmetric', 'Original two-terminal Zn|Zn model; +/-1 mA/cm2, 1 h half-cycles, 1 mAh/cm2 transfer each half-cycle; cell voltage is not a single-electrode overpotential or lifetime claim'),
    ('zn_air_power', 'Zn-air 极化与功率密度', 'zinc', 'polarization', 'Original effective discharge polarization model; geometric air-electrode area basis, 25 C; p=jV; no oxygen-transport or real catalyst calibration'),
    ('zn_i2_cycle', 'Zn-I₂ 长循环与 CE', 'zinc', 'cycling', 'Original Zn-I2 accessible-cathode-capacity model with excess zinc; per gram I2, I2+2e->2I- only, no carbon/extra redox capacity; independent charge/discharge ledger, no CE-product lifetime law'),
    ('flow_efficiency', '液流电池效率关系', 'storage', 'efficiency', 'Original unnamed flow-cell ledger; Q and integral(V dQ) are supplied for each branch; voltage means are capacity-weighted; excludes pump/auxiliary energy and all system-level claims'),
    ('pv_jv', '光伏 J–V 与最大功率', 'photovoltaic', 'jv', 'Original ideal single-junction diode model, Rs=0 and Rsh=infinity; 100 mW/cm2 incident power, 25 C, no spectral/material calibration; MPP/FF/efficiency are model outputs only'),
    ('pv_stability', '光伏稳态功率与稳定性', 'photovoltaic', 'stability', 'Invented fixed operating point; normalized to t=0; temperature and atmosphere required for real tests'),
    ('pv_trpl', 'TRPL 原始信号与衰减', 'general', 'trpl', 'Synthetic biexponential decay; no instrument response, no fitted lifetime or mechanistic conclusion'),
]

FARADAY_C_MOL=96485.33212
IODINE_MOLAR_MASS_G_MOL=253.80894
PV_PARAMETERS={'photocurrent_mA_cm2':23.5,'ideality_factor':1.5,'temperature_K':298.15,
               'open_circuit_voltage_V':1.08,'incident_power_mW_cm2':100.0,
               'series_resistance_ohm_cm2':0.0,'shunt_resistance_ohm_cm2':'infinite',
               'kB_J_K':1.380649e-23,'electron_charge_C':1.602176634e-19}


def pv_thermal_voltage():
    return PV_PARAMETERS['kB_J_K']*PV_PARAMETERS['temperature_K']/PV_PARAMETERS['electron_charge_C']


def pv_saturation_current():
    p=PV_PARAMETERS
    return p['photocurrent_mA_cm2']/np.expm1(p['open_circuit_voltage_V']/(p['ideality_factor']*pv_thermal_voltage()))


def photovoltaic_metrics(values):
    """Only a generating-quadrant MPP; negative current is retained in the CSV."""
    generating=(values[:,0]>=0)&(values[:,1]>=0)
    valid=np.flatnonzero(generating)
    if not len(valid): raise ValueError('PV teaching curve has no generating quadrant')
    index=int(valid[np.argmax(values[valid,2])])
    voc=PV_PARAMETERS['open_circuit_voltage_V']; jsc=float(values[0,1]); pmax=float(values[index,2])
    return {'data_status':'synthetic_demo','scope':'Original ideal diode only; not measured device performance',
            'Jsc_mA_cm2':jsc,'Voc_V':voc,'Vmpp_V':float(values[index,0]),'Jmpp_mA_cm2':float(values[index,1]),
            'Pmax_mW_cm2':pmax,'fill_factor':pmax/(voc*jsc),
            'model_efficiency_percent':100*pmax/PV_PARAMETERS['incident_power_mW_cm2'],
            'MPP_domain':'V>=0 and J>=0, delivered-power convention','grid_step_V':0.002}


def flow_profiles(values):
    """Complete original V(Q) branches whose integrals generate the ledger."""
    rows=[]; u=np.linspace(0,1,51)
    for row in values:
        cycle=int(row[0])
        for branch,charge,mean,tilt in [('charge',row[4],row[6],.08),('discharge',row[5],row[7],-.06)]:
            rows.extend((cycle,branch,float(charge*x),float(mean+tilt*(2*x-1))) for x in u)
    return ['cycle','branch','branch_capacity_mAh','voltage_V'],rows


def scientific_basis(slug,kind):
    metrics_source=('https://www.nature.com/articles/s41467-022-28381-x',
                    'Open challenges and good experimental practices in the research field of aqueous Zn-ion batteries',
                    'Electrode configuration, inventory and denominator reporting boundaries; no numeric data is copied.')
    ce_source=('https://www.nature.com/articles/s41560-020-0648-z','Understanding Coulombic efficiency in lithium metal batteries',
               'Charge-ratio definitions and protocol limitations only; not calibration of this Na or Zn model.')
    sources=[]; common_limits=['All numeric material/rate parameters are original teaching assumptions, not measured or copied paper data.']
    if kind=='ce':
        equations=['Q_plating=1 mAh/cm2; Q_stripping=Q_plating*(1-loss_fraction)',
                   'loss_fraction=0.016-0.009*(1-exp(-cycle/25))+Uniform(-0.0011,0.0011)+declared local loss event',
                   'CE_percent=100*Q_stripping/Q_plating']
        params={'nominal_current_mA_cm2':1,'plating_capacity_mAh_cm2':1,'cycles':200,
                'stripping_endpoint_V':1.0 if slug=='na_metal_ce' else 0.5,
                'reference':'Na/Na+' if slug=='na_metal_ce' else 'Zn/Zn2+',
                'event_cycles':[146,151],'event_additional_loss_fraction':[.002,.013]}
        model='phenomenological_model'; assumptions=['Each teaching cycle has positive irreversible charge loss; no negative-capacity or >100% CE fixture.',
                                                    'Fresh plating charge is available each cycle; CE does not predict a full-cell life.']
        limits=['Only charge accounting is modeled; no nucleation, voltage trace, gas evolution or validated stripping protocol.']
        sources=[ce_source,metrics_source] if slug=='zn_plating_ce' else [ce_source]
    elif kind=='rate':
        equations=['Q_cycle=260*exp(-(cycle-1)/1800)/(1+(current_mA_g/500)^0.7)',
                   'Current steps are 50,100,200,500,1000,50 mA/g, 10 cycles each']
        params={'accessible_Q0_mAh_g':260,'current_scale_mA_g':500,'exponent':.7,'fade_constant_cycles':1800}
        model='phenomenological_model'; assumptions=['Rate-limited accessible capacity plus a small separate active-capacity loss.',
                                                    'Capacity is per gram of working active material vs excess potassium counter metal.']
        limits=['No named cathode/theoretical capacity, ion-diffusion fit or full-cell energy inference.']
        sources=[('https://pubs.acs.org/doi/10.1021/acsenergylett.1c00870','Battery reporting checklist',
                  'Current-rate, mass-basis and cell-configuration reporting boundaries; the accessibility law is an original phenomenological assumption.')]
    elif kind=='symmetric':
        equations=['j=(-1)^floor(time_h)*1 mA/cm2',
                   'V_cell_mV=sign(j)*(35+0.13*time_h+5*exp(-(time_h mod 1)/0.04))',
                   'Transferred_areal_Q=|j|*1 h=1 mAh/cm2 for each complete half-cycle']
        params={'half_cycle_h':1,'current_density_mA_cm2':1,'initial_two_terminal_plateau_mV':35,
                'illustrative_drift_mV_h':.13,'transient_mV':5,'transient_tau_h':.04}
        model='phenomenological_model'; assumptions=['Two-terminal symmetric-cell polarization combines both interfaces and electrolyte drop.',
                                                    'An instantaneous ohmic voltage reversal is allowed at a commanded current switch.']
        limits=['Cannot divide by two to assign electrode overpotentials without additional evidence.',
                'No short-circuit, dendrite, Zn utilization or full-cell lifetime claim.']; sources=[metrics_source]
    elif kind=='polarization':
        equations=['V=1.58-0.050*asinh(j/(2*0.5))-0.0018*j; j in mA/cm2',
                   'P_mW_cm2=j_mA_cm2*V_V']
        params={'original_open_circuit_V':1.58,'effective_activation_coefficient_V':.050,
                'effective_exchange_current_mA_cm2':.5,'area_resistance_ohm_cm2':1.8,'temperature_C':25}
        model='phenomenological_model'; assumptions=['Lumped activation plus ohmic losses at nonnegative discharge current.',
                                                    'The asinh relation is the effective symmetric charge-transfer form; it is not an oxygen reaction electron count.']
        limits=['No oxygen-transport limit, catalyst/electrode calibration, recharge branch or stack power claim.']
        sources=[('https://www.gamry.com/electrochemistry-applications/cv-cyclic-voltammetry',
                  'Gamry: charge-transfer equations','Symmetric charge-transfer/asinh form only; all effective device parameters are original.')]
    elif kind=='cycling':
        equations=['I2+2e- -> 2I-; Q_theoretical=2*F/(3.6*M_I2) mAh/g_I2',
                   'Q_discharge=175*exp(-cycle/1600)+Normal(0,0.8) mAh/g_I2',
                   'CE=99.2+Normal(0,0.1) percent; Q_charge=Q_discharge/(CE/100)']
        params={'F_C_mol':FARADAY_C_MOL,'M_I2_g_mol':IODINE_MOLAR_MASS_G_MOL,
                'theoretical_Q_mAh_g_I2':2*FARADAY_C_MOL/(3.6*IODINE_MOLAR_MASS_G_MOL),
                'initial_accessible_Q_mAh_g_I2':175,'excess_Zn_counter_inventory':True}
        model='phenomenological_model'; assumptions=['Only the two-electron iodine couple contributes capacity; carbon/other redox contributions are zero.',
                                                    'Fade represents inaccessible iodine capacity; independent CE loss can be buffered by excess zinc.']
        limits=['No four-electron iodine, shuttle mechanism, loading/volume claim or full-cell CE-product life law.']
        sources=[('https://www.nature.com/articles/s41467-020-20331-9','A four-electron Zn-I2 aqueous battery',
                  'Explicit distinction between ordinary two-electron and additional four-electron iodine couples; no reported capacity is copied.'),
                 ('https://physics.nist.gov/cgi-bin/cuu/Value?f','NIST CODATA: Faraday constant','Charge per mole of electrons for theoretical iodine capacity.'),metrics_source]
    elif kind=='efficiency':
        equations=['CE=Q_discharge/Q_charge; Vmean_branch=integral(V dQ)/Q_branch',
                   'VE=Vmean_discharge/Vmean_charge; EE=E_discharge/E_charge=CE*VE',
                   'Q_charge=100-0.01*cycle mAh; CE=0.982-0.00002*cycle; VE=0.84-0.0003*cycle',
                   'V_charge_mean=1.42+0.00012*cycle; V_discharge_mean=VE*V_charge_mean',
                   'Branch V(Q)=Vmean+tilt*(2*Q/Qtotal-1), tilt_charge=0.08 V, tilt_discharge=-0.06 V']
        params={'cycles':150,'initial_charge_mAh':100,'charge_capacity_drift_mAh_cycle':.01,
                'nominal_charge_mean_V':1.42,'voltage_grid_points_per_branch':51,
                'auxiliary_pump_energy_included':False,'voltage_average':'capacity-weighted'}
        model='analytic_model'; assumptions=['Positive capacity and energy in both branches over identical declared cycle boundaries.',
                                            'Cell DC energy only; linear V(Q) permits an exact trapezoidal integral.']
        limits=['No pump/inverter/thermal loss or named electrolyte chemistry; no system round-trip efficiency claim.']
        sources=[('https://www.nature.com/articles/s41560-020-00772-8','Assessment methods and performance metrics for redox flow batteries',
                  'CE/VE/EE reporting boundaries; the charge-voltage-energy ledger is original.')]
    elif kind=='jv':
        equations=['VT=kB*T/q; J0=Jph/expm1(Voc/(n*VT))',
                   'J=Jph-J0*expm1(V/(n*VT)); ideal single diode, Rs=0 and Rsh=infinity',
                   'P_delivered=V*J; MPP=max(P) within V>=0,J>=0; FF=Pmax/(Voc*Jsc)',
                   'model_efficiency_percent=100*Pmax/incident_power_mW_cm2']
        params=dict(PV_PARAMETERS, thermal_voltage_V=pv_thermal_voltage(), saturation_current_mA_cm2=pv_saturation_current())
        model='analytic_model'; assumptions=['One ideal single junction with uniform fixed illumination and temperature.',
                                            'Delivered-current sign convention; negative current past Voc is retained, excluded from generating MPP.']
        limits=['No measured device efficiency, calibrated spectrum, resistance extraction, hysteresis or material-specific prediction.',
                'A sampled MPP is within the stated 0.002 V grid resolution, not an experimental maximum-power tracker.']
        sources=[('https://pvpmc.sandia.gov/modeling-guide/2-dc-module-iv/single-diode-equivalent-circuit-models/',
                  'Sandia/NIST PVPMC: single diode equivalent circuit models','Governing single-diode equation and thermal voltage; all numerical parameters are original.')]
    elif kind=='stability':
        equations=['P_normalized(t)=exp(-0.12*(t/1000 h)^0.75); P_normalized(0)=1']
        params={'time_h_range':[0,1000],'decay_amplitude':.12,'stretch_exponent':.75,'normalization_time_h':0}
        model='phenomenological_model'; assumptions=['An original positive stretched-exponential teaching trace at one fixed operating point.']
        limits=['No measured T80/T95, MPP tracking, encapsulation, atmosphere or extrapolated device lifetime.']
        sources=[('https://www.nature.com/articles/s41560-019-0529-5','Consensus statement for stability assessment and reporting for perovskite photovoltaics',
                  'Operating-point, environment and normalization reporting boundaries; not these teaching decay parameters.')]
    else:
        equations=['I(t)=0.7*exp(-t/18 ns)+0.3*exp(-t/90 ns)+0.002']
        params={'amplitudes_a_u':[.7,.3],'input_time_constants_ns':[18,90],'background_a_u':.002,'time_ns_range':[0,400]}
        model='analytic_model'; assumptions=['Two independent first-order decays with constant background and nonnegative amplitudes.']
        limits=['No IRF convolution, instrument timing, fitted lifetime, carrier recombination mechanism or material assignment.']
        sources=[('https://downloads.picoquant.com/manuals/SymPhoTime64_Manual.pdf','PicoQuant SymPhoTime64 manual: lifetime analysis',
                  'Exponential lifetime modeling and the need for instrument-response-aware fitting; original known decay constants.')]
    return {'schema_version':1,'model_class':model,'data_origin':'original_synthetic',
            'equations':equations,'assumptions':assumptions,'parameters':params,
            'references':[{'url':u,'title':t,'supports':s,'scope':'model_definition_only'} for u,t,s in sources],
            'limitations':common_limits+limits,
            'validation_scope':'Original teaching-model equations, charge/energy/units and declared boundaries only; no experimental or material certification.'}


def data(kind, rng):
    if kind == 'ce':
        x = np.arange(1, 201); charge = np.ones(len(x))
        loss=.016-.009*(1-np.exp(-x/25))+rng.uniform(-.0011,.0011,len(x))
        loss[145:151]+=np.linspace(.002,.013,6)
        ce=100*(1-loss)
        return ['cycle','q_plating_mAh_cm2','q_stripping_mAh_cm2','ce_percent'], np.column_stack([x,charge,charge*ce/100,ce])
    if kind == 'rate':
        x = np.arange(1, 61); current = np.repeat([50,100,200,500,1000,50],10)
        q = 260*np.exp(-(x-1)/1800)/(1+(current/500)**.7)
        return ['cycle','current_mA_g','capacity_mAh_g'], np.column_stack([x,current,q])
    if kind == 'symmetric':
        x = np.arange(0, 120, .05); half = np.floor(x).astype(int); v = np.where(half % 2 == 0, 1.,-1.)*(35+.13*x+5*np.exp(-(x%1)/.04))
        return ['time_h','cell_voltage_mV','current_density_mA_cm2','half_cycle'], np.column_stack([x,v,np.where(half%2==0,1.,-1.),half])
    if kind == 'polarization':
        j = np.linspace(0,350,176); v=1.58-.050*np.arcsinh(j/(2*.5))-.0018*j
        return ['current_density_mA_cm2','voltage_V','power_density_mW_cm2'], np.column_stack([j,v,j*v])
    if kind == 'cycling':
        x=np.arange(1,501); q=175*np.exp(-x/1600)+rng.normal(0,.8,len(x)); ce=99.2+rng.normal(0,.1,len(x))
        return ['cycle','capacity_mAh_g_iodine','ce_percent','charge_capacity_mAh_g_iodine'], np.column_stack([x,q,ce,q/(ce/100)])
    if kind == 'efficiency':
        x=np.arange(1,151); ce=(.982-.00002*x); ve=(.84-.0003*x)
        qcharge=100-.01*x; qdischarge=qcharge*ce; vcharge=1.42+.00012*x; vdischarge=vcharge*ve
        return ['cycle','ce_percent','ve_percent','ee_percent','q_charge_mAh','q_discharge_mAh',
                'capacity_weighted_charge_V','capacity_weighted_discharge_V','charge_energy_mWh','discharge_energy_mWh'], np.column_stack([x,ce*100,ve*100,ce*ve*100,qcharge,qdischarge,vcharge,vdischarge,qcharge*vcharge,qdischarge*vdischarge])
    if kind == 'jv':
        v=np.unique(np.r_[np.linspace(0,1.1,551),PV_PARAMETERS['open_circuit_voltage_V']])
        j=PV_PARAMETERS['photocurrent_mA_cm2']-pv_saturation_current()*np.expm1(v/(PV_PARAMETERS['ideality_factor']*pv_thermal_voltage()))
        p=v*j
        return ['voltage_V','current_density_mA_cm2','power_density_mW_cm2'], np.column_stack([v,j,p])
    if kind == 'stability':
        x=np.linspace(0,1000,201); p=np.exp(-.12*(x/1000)**.75)
        return ['time_h','normalized_power'], np.column_stack([x,p])
    x=np.linspace(0,400,401); fast=.7*np.exp(-x/18); slow=.3*np.exp(-x/90); background=np.full_like(x,.002)
    return ['time_ns','signal_a_u','fast_component_a_u','slow_component_a_u','background_a_u'], np.column_stack([x,fast+slow+background,fast,slow,background])


def draw(kind, fields, values, target):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':True,'axes.spines.right':True,'axes.spines.bottom':True,'axes.spines.left':True})
    panels = 3 if kind=='efficiency' else 2 if kind in {'rate','polarization','cycling','jv'} else 1
    fig, axes=plt.subplots(1,panels,figsize=(7.087,3.1),layout='constrained'); axes=np.atleast_1d(axes); a=axes[0]
    x=values[:,0]
    if kind=='ce': a.plot(x,values[:,3],color='#185cbd',lw=1); a.set(xlabel='Cycle',ylabel='Coulombic efficiency (%)')
    elif kind=='rate':
        a.plot(x,values[:,2],'-',marker=None,color='#185cbd'); a.set(xlabel='Cycle',ylabel='Capacity (mAh g$^{-1}$)')
        axes[1].step(x,values[:,1],where='mid',color='#187f84'); axes[1].set(xlabel='Cycle',ylabel='Current (mA g$^{-1}$)')
    elif kind=='symmetric': a.plot(x,values[:,1],color='#185cbd',lw=.7); a.set(xlabel='Time (h)',ylabel='Cell voltage (mV)')
    elif kind=='polarization':
        a.plot(x,values[:,1],color='#185cbd'); a.set(xlabel='Current density (mA cm$^{-2}$)',ylabel='Voltage (V)')
        axes[1].plot(x,values[:,2],color='#187f84'); axes[1].set(xlabel='Current density (mA cm$^{-2}$)',ylabel='Power density (mW cm$^{-2}$)')
    elif kind=='cycling':
        a.plot(x,values[:,1],color='#185cbd',lw=1); a.set(xlabel='Cycle',ylabel='Capacity (mAh g$^{-1}_{iodine}$)')
        ce_axis=a.twinx()
        ce_axis.plot(x,values[:,2],color='#187f84',lw=1,label='CE')
        ce_axis.set_ylabel('CE (%)');ce_axis.set_ylim(95,101)
        axes[1].plot(x,100*values[:,1]/values[0,1],color='#185cbd',label='Reference: cycle 1 = 100%')
        axes[1].set(xlabel='Cycle',ylabel='Model capacity retention (%)')
        axes[1].legend(frameon=False,fontsize=8)
        axes=np.r_[axes,ce_axis]
    elif kind=='efficiency':
        for i,label,c in [(1,'CE','#185cbd'),(2,'VE','#187f84'),(3,'EE','#a85e37')]: a.plot(x,values[:,i],label=label,color=c)
        a.legend(frameon=False); a.set(xlabel='Cycle',ylabel='Efficiency (%)')
        for index,label,color in [(4,'Charge','#185cbd'),(5,'Discharge','#187f84')]:
            axes[1].plot(x,values[:,index],label=label,color=color)
        axes[1].set(xlabel='Cycle',ylabel='Capacity (mAh)');axes[1].legend(frameon=False,fontsize=8)
        axes[2].plot(x,100*values[:,5]/values[0,5],color='#187f84',label='Reference: cycle 1 = 100%')
        axes[2].set(xlabel='Cycle',ylabel='Model capacity retention (%)');axes[2].legend(frameon=False,fontsize=8)
    elif kind=='jv':
        a.plot(x,values[:,1],color='#185cbd'); a.axhline(0,color='#59687c',lw=.7); a.set(xlabel='Voltage (V)',ylabel='Current density (mA cm$^{-2}$)')
        metrics=photovoltaic_metrics(values)
        axes[1].plot(x,values[:,2],color='#187f84'); axes[1].annotate('MPP',(metrics['Vmpp_V'],metrics['Pmax_mW_cm2']),xytext=(4,6),textcoords='offset points',fontsize=8,color='#a85e37'); axes[1].set(xlabel='Voltage (V)',ylabel='Power density (mW cm$^{-2}$)')
    elif kind=='stability': a.plot(x,values[:,1],color='#185cbd'); a.set(xlabel='Time (h)',ylabel='Power / initial power')
    else: a.semilogy(x,values[:,1],color='#185cbd'); a.set(xlabel='Time (ns)',ylabel='Signal (a.u.)')
    checks=[]
    for i, ax in enumerate(axes):
        apply_series_policy(ax)
        frame={side:ax.spines[side].get_visible() for side in ('top','right','bottom','left')}
        if not all(frame.values()): raise ValueError('Data axes must show four frame spines')
        for trace in ax.lines:
            check_series_policy(ax,trace)
        checks.append({'panel':i,'frame_spines':frame,'curve_styles':[
            {'linestyle':line.get_linestyle(),'marker':line.get_marker(),'points':len(line.get_xdata()),'sampling':check_series_policy(ax,line)}
            for line in ax.lines], 'xlabel':ax.get_xlabel(),'ylabel':ax.get_ylabel()})
        if panels>1 and ax is not locals().get('ce_axis'): ax.text(-.16,1.05,chr(97+i),transform=ax.transAxes,weight='bold')
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
        if np.any(values[:,1] <= 0) or np.any(values[:,2]<0) or np.any((values[:,3]<0)|(values[:,3]>100)) or not np.allclose(values[:,3],values[:,2]/values[:,1]*100):
            raise ValueError('Teaching CE must match stripping/plating capacity')
    if kind in {'polarization','jv'} and not np.allclose(values[:,2],values[:,0]*values[:,1]):
        raise ValueError('Teaching power must match the declared current and voltage units')
    if kind == 'symmetric':
        if not np.allclose(np.abs(values[:,2]),1) or not np.all(np.sign(values[:,1])==np.sign(values[:,2])):
            raise ValueError('Symmetric teaching cell voltage must follow the commanded +/-1 mA/cm2 current')
    if kind == 'rate' and (np.any(values[:,1:]<=0) or np.any(values[:,2]>260)):
        raise ValueError('Teaching rate capacity must stay within the declared accessible capacity')
    if kind == 'cycling':
        theoretical=2*FARADAY_C_MOL/(3.6*IODINE_MOLAR_MASS_G_MOL)
        if np.any(values[:,1]<=0) or np.any(values[:,1]>theoretical) or np.any(values[:,3]>theoretical):
            raise ValueError('This two-electron iodine-only teaching capacity cannot exceed its declared theoretical bound')
        if np.any(values[:,3]<=0) or not np.allclose(values[:,2],100*values[:,1]/values[:,3]):
            raise ValueError('Teaching Zn-I2 CE must be recalled from charge/discharge capacities')
    if kind == 'efficiency':
        if np.any(values[:,4:]<=0) or np.any((values[:,1:4]<=0)|(values[:,1:4]>100)):
            raise ValueError('Teaching flow capacities, voltages, energies and efficiencies must be positive')
        recalled=np.column_stack([values[:,5]/values[:,4],values[:,7]/values[:,6],values[:,9]/values[:,8]])*100
        if not np.allclose(values[:,1:4],recalled) or not np.allclose(values[:,3],values[:,1]*values[:,2]/100):
            raise ValueError('Teaching CE/VE/EE must recall from the charge/voltage/energy ledger')
        if not np.allclose(values[:,8],values[:,4]*values[:,6]) or not np.allclose(values[:,9],values[:,5]*values[:,7]):
            raise ValueError('Teaching capacity-weighted voltage means must recall each branch energy')
    if kind == 'jv':
        diode=PV_PARAMETERS['photocurrent_mA_cm2']-pv_saturation_current()*np.expm1(values[:,0]/(PV_PARAMETERS['ideality_factor']*pv_thermal_voltage()))
        if values[0,0]!=0 or not np.allclose(values[:,1],diode,rtol=1e-10,atol=1e-10):
            raise ValueError('PV teaching current must satisfy its declared ideal single-diode model')
        metrics=photovoltaic_metrics(values)
        if not 0<metrics['fill_factor']<1 or not 0<metrics['model_efficiency_percent']<100:
            raise ValueError('PV teaching generating-quadrant FF/efficiency is outside its physical boundary')
    if kind == 'stability' and (not np.isclose(values[0,1],1) or np.any(values[:,1]<=0)):
        raise ValueError('Teaching stability power must be positive and normalized to t=0')
    if kind == 'trpl' and (np.any(values[:,1:]<=0) or not np.allclose(values[:,1],np.sum(values[:,2:],axis=1))):
        raise ValueError('Teaching decay signal must equal its nonnegative components plus background')


def validate_flow_profiles(ledger, rows):
    """Independently recall Q and integral(V dQ) from the complete branches."""
    integrate=getattr(np,'trapezoid',None)
    if integrate is None: integrate=np.trapz
    for entry in ledger:
        cycle=int(entry[0])
        for branch,qcolumn,ecolumn in [('charge',4,8),('discharge',5,9)]:
            values=np.array([[r[2],r[3]] for r in rows if int(r[0])==cycle and r[1]==branch],dtype=float)
            if len(values)<2 or values[0,0]!=0 or np.any(np.diff(values[:,0])<=0) or np.any(values[:,1]<=0):
                raise ValueError('Flow teaching branch needs a complete positive-voltage capacity grid from zero')
            q=float(values[-1,0]); energy=float(integrate(values[:,1],values[:,0]))
            if not np.isclose(q,entry[qcolumn],rtol=1e-11) or not np.isclose(energy,entry[ecolumn],rtol=1e-11):
                raise ValueError('Flow teaching branch Q/energy does not recall its ledger')


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
            expected,canonical=data(kind,np.random.default_rng(SEED+index))
            validate_demo(kind,fields,values,expected)
            # A replay cannot silently stamp our model provenance onto unrelated
            # data which merely happens to satisfy a charge-ratio identity.
            if values.shape!=canonical.shape or not np.allclose(values,canonical,rtol=1e-10,atol=1e-10):
                raise ValueError('Teaching replay requires the unchanged original numeric CSV for this recipe; use a contracted plot pack for author data')
        else: fields,values=data(kind,np.random.default_rng(SEED+index))
        validate_demo(kind,fields,values,data(kind,np.random.default_rng(SEED+index))[0])
        folder.mkdir(parents=True,exist_ok=True)
        with (folder/'data.csv').open('w',encoding='utf-8',newline='') as handle:
            w=csv.writer(handle); w.writerow(fields); w.writerows(values)
        source_files=['data.csv']
        if kind=='efficiency':
            profile_fields,profiles=flow_profiles(values)
            validate_flow_profiles(values,profiles)
            with (folder/'cycle_profiles.csv').open('w',encoding='utf-8',newline='') as handle:
                w=csv.writer(handle); w.writerow(profile_fields); w.writerows(profiles)
            source_files.append('cycle_profiles.csv')
        if kind=='jv':
            (folder/'metrics.json').write_text(json.dumps(photovoltaic_metrics(values),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            source_files.append('metrics.json')
        frame_checks=draw(kind,fields,values,folder)
        shutil.copyfile(__file__,folder/'render.py')
        source_policy=Path(__file__).resolve().parent/'series_policy.py'
        if not source_policy.exists():source_policy=Path(__file__).resolve().parents[1]/'skills/voltpeer-plot/scripts/batteryplot/series_policy.py'
        shutil.copyfile(source_policy,folder/'series_policy.py')
        meta={'id':slug,'title':title,'domain':domain,'type':'demo','data_status':'synthetic_demo','not_experimental_data':True,'random_seed':SEED+index,'source_files':source_files,'variables_and_units':fields,'test_conditions':conditions,'render_options':{'recipe':slug},'reproduce':f'python render.py --output rebuilt --recipe {slug} --demo-input data.csv','creator':'VoltPeer maintainers','license':'MIT','generator_version':'1.6','limitations':'Declared teaching model only; no measured device, mechanism or material certification. This generator does not adapt experimental data.',
              'scientific_basis':scientific_basis(slug,kind)}
        meta['actual_artist_checks']=frame_checks
        if kind in {'cycling','efficiency'}:
            col=1 if kind=='cycling' else 5
            meta['retention_reference']={'reference_cycle':1,'reference_capacity':float(values[0,col]),'quantity':'iodine-mass discharge capacity' if kind=='cycling' else 'absolute discharge capacity','formula':'100*Qdis(n)/Qdis(1)','conditions':'same original teaching-model scenario; physical current/rate and real cell validation not supplied; no acquired normalization'}
        (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'README.txt').write_text(f'{title}\nAll numeric data are synthetic teaching values. Never use them as experimental results.\n{meta["reproduce"]}\nRequires Python >=3.10, numpy and matplotlib in an isolated environment.\n',encoding='utf-8')
        with ZipFile(args.output/f'BRF-demo-{slug}.zip','w',ZIP_DEFLATED) as z:
            z.writestr('README.txt',f'Open {slug}/README.txt, metadata.json and data.csv.\nSynthetic teaching data only.\n')
            for file in sorted(folder.iterdir()): z.write(file,f'{slug}/{file.name}')
    print('Generated explicitly synthetic domain examples.')


if __name__=='__main__': main()
