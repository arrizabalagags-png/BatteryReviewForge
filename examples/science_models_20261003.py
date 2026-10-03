"""100 different analytic research relationships, with declared teaching inputs.

This module GENERATES synthetic teaching records. The downloadable plotting
entry does not call it: that entry redraws the unchanged existing CSV only.
Parameters below are independently selected, never fitted to a cited paper.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.special import erf, erfc, voigt_profile
from scipy.stats import t as student_t
from science_references_20261003 import reference

F=96485.33212; R=8.314462618; KB=1.380649e-23; NA=6.02214076e23
EPS0=8.8541878128e-12; H=6.62607015e-34; C=299792458.; T=298.15

@dataclass
class Model:
    ident: str
    zh: str
    en: str
    family: str
    panels: list
    rows: list
    basis: dict

def grid(a,b,n=241): return np.linspace(a,b,n)
def lg(a,b,n=241): return np.logspace(a,b,n)
def cumulative(y,x): return np.r_[0,np.cumsum((y[1:]+y[:-1])/2*np.diff(x))]
def stress_equilibrium_shift(stress_mpa,omega_m3_mol):
    """mV shift at fixed composition/activity, tensile-positive hydrostatic stress."""
    return np.asarray(stress_mpa,dtype=float)*1e6*omega_m3_mol/F*1000
def sphere(q,r):
    u=np.asarray(q)*r
    return (3*(np.sin(u)-u*np.cos(u))/u**3)**2

def catalogue():
    out=[]
    def add(ident,zh,en,fam,ref,relation,equation,params,limit,xlabel,ylabel,x,series,*,yscale='linear',xscale='linear',positive=False,unit_interval=False):
        # These narrower references supersede a family-level reference where
        # the exact measurement method has its own original/official source.
        ref={
            'rotating_disk_levich':'levich','koutecky_levich':'levich',
            'nucleation_transients':'nucleation','sand_depletion_time':'sand',
            'line_shape_tails':'line','xas_linear_mixture':'line',
            'raman_thermal_ratio':'raman','raman_polarization':'raman',
            'isotope_frequency_shift':'harmonic','boltzmann_two_states':'thermo',
            'competitive_coordination':'thermo','residence_survival':'thermo',
            'vanthoff_equilibrium':'thermo','exchange_signal_correlation':'thermo',
            'student_coverage_factor':'coverage','mean_uncertainty_samplecount':'coverage',
        }.get(ident,ref)
        rows=[]
        for label,y in series.items():
            y=np.asarray(y,dtype=float); xx=np.asarray(x,dtype=float)
            if y.ndim==0:y=np.full_like(xx,y)
            assert len(y)==len(xx)>1 and np.all(np.isfinite(y)) and np.all(np.isfinite(xx)),ident
            if positive:assert np.min(y)>=-1e-10,ident
            if unit_interval:assert np.min(y)>=-1e-10 and np.max(y)<=1+1e-10,ident
            if yscale=='log':assert np.min(y)>0,ident
            rows.extend(dict(panel=0,series=label,x=float(a),y=float(b)) for a,b in zip(xx,y))
        bounds=['Finite numerical values and explicit physical units.','Continuous plotted curves are solid without markers; data axes retain four borders.']
        if positive:bounds+=['All plotted responses are nonnegative.']
        if unit_interval:bounds+=['All plotted fractions lie between zero and one.']
        basis=dict(schema_version=1,model_class='analytic_model',data_origin='original_synthetic',
            relationship=relation,equations=[equation],parameters=params,
            assumptions=['Independently declared parameters; no experimental or material fit.',limit],
            limitations=[limit,'A numerical/model QA pass does not validate author data or a physical mechanism.'],
            constraints=bounds,references=[reference(ref,relation)],validation={'finite':True,'nonnegative':positive,'unit_interval':unit_interval},
            validation_scope='Source method/principle and explicitly derived restricted teaching specialization checked; equation, units and numerical constraints only. No copied paper measurements, material parameters, experimental fit or mechanism certification.')
        out.append(Model(ident,zh,en,fam,[dict(title=en,xlabel=xlabel,ylabel=ylabel,yscale=yscale,xscale=xscale)],rows,basis))

    # 1–10: electrode design / thermodynamic bookkeeping; neither the old
    # areal-capacity plot nor a repeat of its parameter sweep.
    x=grid(.6,1.8)
    add('np_inventory','N/P 与有限锂库存','Electrode balance and lithium inventory','design','battery','Limiting electrode and lithium inventory jointly bound cell capacity.','Qcell=min(Qp,Qn,Qli); Qn=(N/P)Qp',{'Qp_mAh':3,'Qli_mAh':[2.5,3,3.5]},'Ideal accessible capacities; no kinetic or first-cycle loss.','Negative/positive capacity ratio','Accessible cell capacity (mAh)',x,{f'Li inventory {q:g} mAh':np.minimum(np.minimum(3,3*x),q) for q in [2.5,3,3.5]},positive=True)
    x=grid(1,10)
    add('electrolyte_mass_energy','电解液量与整电池比能','Electrolyte mass and whole-cell energy','design','battery','Added inactive electrolyte mass dilutes whole-cell specific energy.','Egrav=1000*V*Q/(mfixed+rho*VE)',{'V_V':3.7,'Q_Ah':1,'mfixed_g':12,'rho_g_mL':1.2},'All other masses and accessible charge fixed; electrolyte starvation not represented.','Electrolyte volume (mL)','Whole-cell specific energy (Wh kg$^{-1}$)',x,{'Fixed 1 Ah inventory':3700/(12+1.2*x)},positive=True)
    x=grid(.1,.7)
    add('porosity_volumetric','孔隙率与体积容量','Porosity and volumetric capacity','design','battery','Active-solid fraction bounds dry-electrode volumetric capacity.','Qvol=(1-epsilon-fbinder)*rho_s*Qmass',{'binder_volume_fraction':.05,'rho_s_g_cm3':4.5,'Qmass_mAh_g':180},'No tortuosity/kinetic penalty; binder and pore fractions explicitly sum with active solid.','Porosity (fraction)','Electrode capacity (mAh cm$^{-3}$)',x,{'Fixed 5% binder':(1-x-.05)*4.5*180},positive=True)
    x=grid(5,40)
    add('collector_mass_penalty','集流体厚度与比能','Collector thickness and specific energy','design','battery','Current-collector mass changes cell-normalized specific energy.','mCC=rho*A*L; Egrav=1000*E/(mfixed+mCC)',{'rho_g_cm3':8.96,'area_cm2':100,'E_Wh':3.7,'mfixed_g':15},'No resistance/strength optimization; a uniform Cu collector is an assumed bookkeeping component.','Collector thickness (µm)','Specific energy (Wh kg$^{-1}$)',x,{'Fixed active stack':3700/(15+8.96*100*x*1e-4)},positive=True)
    x=grid(1,30)
    add('stack_packaging_overhead','堆叠层数与封装开销','Stack count and package overhead','design','battery','Fixed package volume is amortized over active stack count.','Evol=N*Estack/(Vpackage+N*Vstack)',{'E_stack_Wh':.2,'V_stack_mL':.4,'V_package_mL':2},'Continuous N only illustrates design scaling; physical layer counts are integers.','Stack count (model coordinate)','Volumetric energy (Wh L$^{-1}$)',x,{'Fixed package':1000*.2*x/(2+.4*x)},positive=True)
    x=grid(0,1)
    add('ohmic_cutoff','欧姆降与截止容量','Ohmic drop and voltage cutoff','design','battery','Cutoff truncates an otherwise identical linear open-circuit profile.','U(q)=4.2-1.2q; V=U-I*R; qcut=(4.2-Vcut-I*R)/1.2',{'R_ohm':.12,'Vcut_V':3,'Q0_Ah':1},'Linear illustrative OCV; no concentration polarization or real electrode assignment.','Discharged fraction','Terminal voltage (V)',x,{f'{i:g} A':4.2-1.2*x-i*.12 for i in [0,.5,1]},positive=True)
    x=grid(0,1)
    add('stoichiometric_window','嵌入窗口与理论容量','Occupation window and theoretical capacity','design','battery','Only a declared site-occupation window contributes accessible theoretical charge.','Q=Delta_x*n*F/(3.6*M)',{'n':1,'molar_mass_g_mol':100},'One electron per occupied site; no practical utilization or material identity.','Accessible occupation window','Theoretical specific capacity (mAh g$^{-1}$)',x,{'One-electron 100 g/mol host':x*F/360},positive=True)
    x=grid(.02,.98)
    add('regular_solution_ocv','规则溶液占位与电位','Regular-solution occupation and potential','design','nernst','Mixing chemical potential sets a hypothetical insertion potential.','mu=RT ln(x/(1-x))+Omega(1-2x); U=Uref-mu/F',{'Omega_J_mol':2500,'Uref_V':3.5,'T_K':T},'Homogeneous stable branch only; this choice Omega<2RT has no two-phase miscibility gap.','Occupied-site fraction','Equilibrium potential (V)',x,{'Stable homogeneous host':3.5-(R*T*np.log(x/(1-x))+2500*(1-2*x))/F},positive=True)
    x=lg(-3,3)
    add('activity_redox_potential','氧化还原活度比与电位','Redox activity ratio and potential','design','nernst','Equilibrium potential depends on redox activities rather than raw signal.','E=E0+(RT/nF)ln(aOx/aRed)',{'E0_V':.3,'n':1,'T_K':T},'Equilibrium and unit-consistent activities; concentrated solutions need activity coefficients.','Oxidized/reduced activity ratio','Equilibrium potential (V)',x,{'Ideal activity ratio':.3+R*T/F*np.log(x)},xscale='log')
    x=grid(0,120)
    add('pulse_overpotential_partition','电流脉冲的欧姆与弛豫分量','Pulse voltage contributions','design','capacitance','Instantaneous ohmic and time-dependent RC drops have different temporal roles.','eta_Rs=I Rs; eta_RC=I Rp(1-exp(-t/tau))',{'I_A':1,'Rs_ohm':.02,'Rp_ohm':.08,'tau_s':30},'Linear stationary RC surrogate; no diffusion coefficient extraction.','Pulse time (s)','Overpotential (mV)',x,{'Ohmic':20+0*x,'RC relaxation':80*(1-np.exp(-x/30)),'Total':20+80*(1-np.exp(-x/30))},positive=True)

    # 11–20: interfacial electrochemistry and reaction/flux measurement.
    x=grid(0,.3)
    ik=np.expm1(.5*F*x/(R*T))
    add('kinetic_transport_limit','动力学电流与传质上限','Kinetic current and mass-transfer limit','kinetics2','kinetics','Transport caps a single-direction kinetic current.','i=ik/(1+ik/ilim)',{'i0_A_m2':1,'ilim_A_m2':20,'alpha':.5},'Unidirectional high-overpotential approximation, not near-equilibrium full BV.','Anodic overpotential (V)','Current density (A m$^{-2}$)',x,{'Kinetic only':ik,'Transport-limited':ik/(1+ik/20)},positive=True)
    x=grid(.01,.99)
    add('exchange_site_occupation','占位与交换电流','Occupation and exchange current','kinetics2','kinetics','Reactant and vacancy availability jointly set an exchange-current surrogate.','i0=k*sqrt(x(1-x))',{'k_A_m2':20,'alpha':.5},'Single-step ideal activity model; multi-step reaction orders need evidence.','Occupied-site fraction','Exchange current density (A m$^{-2}$)',x,{'Symmetric one-electron model':20*np.sqrt(x*(1-x))},positive=True)
    x=grid(0,20)
    add('faraday_deposit_thickness','沉积电荷与厚度','Deposition charge and film thickness','kinetics2','flux','Faraday charge fixes a uniform deposit thickness if efficiency and density are known.','L=eta*Q_A*M/(nF rho)',{'M_g_mol':6.94,'rho_g_cm3':.534,'n':1,'efficiency':1},'Ideal uniform Li-equivalent film; porosity, alloying and dead metal excluded.','Areal charge (C cm$^{-2}$)','Equivalent film thickness (µm)',x,{'100% Faraday yield':x*6.94/(F*.534)*1e4},positive=True)
    x=grid(100,3000)
    add('rotating_disk_levich','旋转速率与极限电流','Rotation and limiting current','kinetics2','flux','Rotating-disk transport yields a square-root angular-speed limit.','iL=0.62*nF*D^(2/3)*nu^(-1/6)*omega^(1/2)*c',{'D_m2_s':1e-9,'nu_m2_s':1e-6,'c_mol_m3':10,'n':1},'Laminar ideal RDE boundary layer; not a porous battery-electrode equation.','Rotation rate (rpm)','Limiting current density (A m$^{-2}$)',x,{'Ideal disk':.62*F*(1e-9)**(2/3)*(1e-6)**(-1/6)*np.sqrt(x*2*np.pi/60)*10},positive=True)
    x=grid(.05,.5)
    add('koutecky_levich','倒数旋转速率与电流分离','Koutecky-Levich current separation','kinetics2','kinetics','Series kinetic/transport inverse currents separate the two limiting contributions.','1/i=1/ik+(1/B)*omega^(-1/2)',{'ik_A_m2':30,'B_A_s05_m2':8},'Steady one-direction RDE model; no multi-path interpretation.','Inverse square-root speed (s$^{1/2}$)','Inverse current density (m$^2$ A$^{-1}$)',x,{'Kinetic plus diffusion':1/30+x/8},positive=True)
    x=grid(260,360)
    add('tafel_temperature_slope','温度与 Tafel 斜率','Temperature and Tafel slope','kinetics2','kinetics','The kinetic slope scales with temperature and transfer coefficient.','b=2.303RT/(alpha*nF)',{'alpha':[.35,.5,.65],'n':1},'One-direction Tafel region; slopes alone cannot prove a mechanism.','Temperature (K)','Tafel slope (mV decade$^{-1}$)',x,{f'α = {a:g}':2.303*R*x/(a*F)*1000 for a in [.35,.5,.65]},positive=True)
    x=grid(.01,.5)
    add('capacitive_scan_current','扫描速率与双层电流','Scan speed and double-layer current','kinetics2','capacitance','Ideal double-layer charging current is proportional to potential sweep rate.','i=Cdl*v',{'Cdl_F_m2':[.1,.3,.5]},'Pure nonfaradaic constant capacitance; no active-area estimation without calibration.','Scan speed (V s$^{-1}$)','Nonfaradaic current (A m$^{-2}$)',x,{f'{c:g} F/m²':c*x for c in [.1,.3,.5]},positive=True)
    x=grid(-.06,.06)
    lam=np.sqrt(EPS0*78.4*R*T/(2*F**2*10))
    add('diffuse_capacitance','双层电位与微分电容','Diffuse potential and differential capacitance','kinetics2','doublelayer','Dilute diffuse-layer capacitance changes with potential.','Cd=(epsilon/lambdaD)*cosh(F psi/(2RT))',{'epsilon_r':78.4,'c_mol_m3':10,'T_K':T},'Dilute symmetric monovalent ions; neglects finite ion size and Stern capacitance.','Diffuse-layer potential (V)','Differential capacitance (F m$^{-2}$)',x,{'Gouy-Chapman diffuse part':EPS0*78.4/lam*np.cosh(F*x/(2*R*T))},positive=True)
    x=grid(-1.5,.3)
    add('marcus_activation','电子转移驱动力与势垒','Electron-transfer driving force and barrier','kinetics2','marcus','Classical outer-sphere barrier is quadratic in reaction driving force.','DeltaGact=(lambda+DeltaG0)^2/(4lambda)',{'lambda_eV':.7},'Classical teaching barrier; inverted-region quantitative rates require vibronic treatment.','Reaction free energy (eV)','Activation free energy (eV)',x,{'λ = 0.7 eV':(.7+x)**2/(4*.7)},positive=True)
    x=grid(.02,4)
    inst=1.9542/x*(1-np.exp(-1.2564*x))**2
    prog=1.2254/x*(1-np.exp(-2.3367*x**2))**2
    add('nucleation_transients','成核瞬态的归一化形状','Normalized nucleation transients','kinetics2','kinetics','Instantaneous and progressive nucleation assumptions produce distinct normalized current shapes.','SH: (i/im)^2=1.9542/u*(1-exp(-1.2564u))^2 or 1.2254/u*(1-exp(-2.3367u^2))^2',{'u':'t/tmax','normalization':'i²/imax²'},'Ideal diffusion-controlled 3D nucleation; a shape match alone does not establish nucleation mode.','Time / peak time','Squared current / squared peak current',x,{'Instantaneous assumption':inst,'Progressive assumption':prog},positive=True)

    # 21–30: continuum transport; spatial profiles, boundaries and flux terms.
    x=grid(0,150)
    add('fick_penetration_profile','扩散时间与浓度剖面','Diffusion time and penetration profile','transport2','flux','A maintained planar surface concentration generates an erfc profile.','c/cs=erfc(z/(2sqrt(Dt)))',{'D_m2_s':1e-10,'times_s':[5,20,80]},'Semi-infinite planar medium, fixed surface value and initially zero solute.','Distance from surface (µm)','Concentration / surface concentration',x,{f'{tt:g} s':erfc(x*1e-6/(2*np.sqrt(1e-10*tt))) for tt in [5,20,80]},unit_interval=True)
    x=grid(-1e6,1e6)
    add('fick_flux_gradient','浓度梯度与扩散通量','Concentration gradient and diffusion flux','transport2','flux','Diffusive flux opposes the concentration gradient.','J=-D*dc/dz',{'D_m2_s':1e-10},'Constant D, continuum concentration and no migration/convection.','Concentration gradient (mol m$^{-4}$)','Molar flux (µmol m$^{-2}$ s$^{-1}$)',x,{'Fick flux':-1e-10*x*1e6})
    x=grid(.002,1)
    uptake=1-6/np.pi**2*sum(np.exp(-n*n*np.pi**2*x)/n**2 for n in range(1,101))
    add('sphere_diffusion_uptake','球形粒子的扩散吸收','Spherical diffusion uptake','transport2','battery','Spherical diffusion gives a boundary/geometry-dependent fractional uptake.','M/M∞=1-(6/pi²)sum(exp(-n²pi²Dt/a²)/n²)',{'terms':100},'Constant surface concentration, constant D and initially uniform empty sphere.','Fourier time Dt / radius$^2$','Fractional uptake',x,{'Sphere':uptake},unit_interval=True)
    x=grid(.002,1)
    uptake=1-8/np.pi**2*sum(np.exp(-(2*n+1)**2*np.pi**2*x/4)/(2*n+1)**2 for n in range(100))
    add('slab_diffusion_uptake','平板扩散的边界响应','Slab diffusion uptake','transport2','flux','A symmetric slab has different diffusion eigenvalues from a sphere.','M/M∞=1-(8/pi²)sum(exp(-(2n+1)²pi²Dt/(4a²))/(2n+1)²)',{'terms':100},'Two fixed-concentration faces and half-thickness a; no reaction.','Fourier time Dt / half-thickness$^2$','Fractional uptake',x,{'Slab':uptake},unit_interval=True)
    x=grid(-2000,2000)
    add('migration_field_flux','电场与迁移通量','Electric field and migration flux','transport2','flux','Opposite ionic valences give opposite migration directions.','Jmig=z*D*F*c*E/(RT)',{'D_m2_s':1e-10,'c_mol_m3':100,'T_K':T},'Dilute mobility relation; concentration held fixed, no electroneutral transport closure.','Electric field (V m$^{-1}$)','Migrative flux (µmol m$^{-2}$ s$^{-1}$)',x,{'Monovalent cation':1e-10*F*100*x/(R*T)*1e6,'Monovalent anion':-1e-10*F*100*x/(R*T)*1e6})
    x=lg(-2,3)
    add('advection_diffusion_ratio','Péclet 数与输运占比','Peclet number and transport balance','transport2','flux','Peclet number compares advective and diffusive flux scales.','Pe=uL/D; fraction_adv=Pe/(1+Pe)',{'definition':'magnitudes of characteristic fluxes'},'Scale comparison only; not a solved concentration field or measured transference number.','Peclet number','Characteristic flux fraction',x,{'Advection':x/(1+x),'Diffusion':1/(1+x)},xscale='log',unit_interval=True)
    x=lg(-5,-1)
    add('debye_screening_length','离子强度与屏蔽长度','Ionic strength and screening length','transport2','doublelayer','Dilute screening length decreases with square-root ion concentration.','lambdaD=sqrt(epsilon*RT/(2F²c))',{'epsilon_r':78.4,'T_K':T,'c_conversion':'mol/L × 1000 = mol/m³'},'Ideal symmetric monovalent aqueous-like dielectric; high concentration excluded.','Salt concentration (mol L$^{-1}$)','Debye length (nm)',x,{'Dilute 1:1 model':np.sqrt(EPS0*78.4*R*T/(2*F**2*x*1000))*1e9},xscale='log',yscale='log',positive=True)
    x=grid(.1,.8)
    add('tortuosity_effective_diffusion','孔隙率、曲折度与有效扩散','Porosity, tortuosity and effective diffusion','transport2','battery','An assumed tortuosity closure changes continuum effective transport.','Deff=D0*epsilon/tau; tau=epsilon^-0.5',{'D0_m2_s':1e-10,'closure':'Bruggeman exponent 1.5'},'Isotropic phenomenological closure; morphology and anisotropy not established.','Porosity (fraction)','Effective diffusivity (10$^{-11}$ m$^2$ s$^{-1}$)',x,{'Bruggeman closure':10*x**1.5,'Straight pores τ=1':10*x},positive=True)
    x=grid(5,100)
    add('separator_area_resistance','隔膜厚度与面积电阻','Separator thickness and area resistance','transport2','battery','Effective electrolyte conduction causes a separator geometry penalty.','RA=L/kappaeff',{'kappaeff_S_m':.2},'Uniform wetted separator and area-normalized ohmic resistance; interfaces excluded.','Separator thickness (µm)','Area-specific resistance (Ω cm$^2$)',x,{'Uniform ionic conductor':x*1e-6/.2*1e4},positive=True)
    x=grid(10,200)
    add('sand_depletion_time','电流与表面耗尽时间','Current and surface depletion time','transport2','flux','Planar constant-current diffusion reaches a nonnegative-concentration limit.','tsand=pi*D*(nF*c0/(2i))²',{'D_m2_s':1e-10,'c0_mol_m3':1000,'n':1},'No migration/convection and semi-infinite planar diffusion; stop before negative concentration.','Current density (A m$^{-2}$)','Surface depletion time (s)',x,{'Diffusion-only limit':np.pi*1e-10*(F*1000/(2*x))**2},positive=True,yscale='log')

    # 31–40: heat-source decomposition and bounded energy-balance solutions.
    x=grid(-5,5)
    add('joule_current_heat','电流平方与焦耳热','Current squared and Joule heating','thermal2','heat','Ohmic heat is nonnegative and even in current.','Pohm=I²R',{'R_ohm':.04},'Fixed resistance; no temperature feedback or electrochemical reaction heat.','Current (A)','Ohmic heating (W)',x,{'R = 40 mΩ':.04*x*x},positive=True)
    x=grid(0,1)
    entropy=.0003*np.cos(2*np.pi*x)
    add('entropy_soc_heat','荷电状态与可逆热符号','State of charge and reversible heat sign','thermal2','heat','An explicitly assumed entropy coefficient reverses reversible heat sign.','Prev=-I*T*dUeq/dT; dUeq/dT=A cos(2pi SOC)',{'I_A':1,'T_K':T,'A_V_K':.0003,'sign':'positive I = discharge'},'Synthetic entropy function, no material assignment; charge reverses the heat sign.','Model state of charge','Reversible heat (W)',x,{'Discharge 1 A':-T*entropy,'Charge 1 A':T*entropy})
    x=grid(0,1800)
    add('lumped_heat_balance','集总温升与散热','Lumped heating and cooling conductance','thermal2','thermal','Heat capacity and cooling conductance set a bounded heating transient.','DeltaT=P/G*(1-exp(-Gt/C))',{'P_W':1.5,'C_J_K':80,'G_W_K':.2},'Uniform temperature requires small Biot number; constant coefficients.','Time (s)','Temperature rise (K)',x,{'Lumped energy balance':7.5*(1-np.exp(-.2*x/80))},positive=True)
    x=grid(0,1800)
    add('cooling_decay','停止发热后的温度衰减','Temperature decay after heating stops','thermal2','thermal','Stored sensible heat decays through a specified cooling conductance.','DeltaT=DeltaT0 exp(-Gt/C)',{'DeltaT0_K':12,'G_W_K':.2,'C_J_K':80},'No heat generation or changing ambient after t=0.','Cooling time (s)','Temperature above ambient (K)',x,{'Cooling only':12*np.exp(-.2*x/80)},positive=True)
    x=grid(-5,5)
    add('slab_internal_heating','均匀内热源的厚度温度场','Slab temperature with internal heating','thermal2','thermal','Uniform volumetric heat creates a parabolic steady temperature field.','DeltaT=qvol*(L²-z²)/(2k)',{'half_thickness_m':.005,'qvol_W_m3':2e5,'k_W_mK':1.2},'Both faces fixed at the same temperature; constant isotropic k.','Through-thickness position (mm)','Temperature rise (K)',x,{'Steady slab':2e5*(.005**2-(x*1e-3)**2)/(2*1.2)},positive=True)
    x=grid(0,10)
    add('cylinder_radial_heat','圆柱电池径向稳态温度','Cylindrical radial temperature','thermal2','thermalcell','Radial conduction yields a cylindrical internal-heating temperature profile.','DeltaT=qvol*(a²-r²)/(4k)',{'radius_m':.01,'qvol_W_m3':1e5,'k_W_mK':1},'Long cylinder, fixed sidewall temperature, no end effects or anisotropy.','Radial position (mm)','Temperature above sidewall (K)',x,{'Steady radial conduction':1e5*(.01**2-(x*1e-3)**2)/4},positive=True)
    x=grid(0,2000)
    add('thermal_contact_jump','界面热流与温度跳变','Interface heat flux and temperature jump','thermal2','thermal','A contact thermal resistance causes a finite temperature discontinuity.','DeltaT=qflux*Rcontact',{'Rcontact_m2K_W':[.001,.003,.006]},'Uniform contact resistance, steady flux and no temperature-dependent contact.','Interface heat flux (W m$^{-2}$)','Temperature jump (K)',x,{f'{rr:g} m² K/W':rr*x for rr in [.001,.003,.006]},positive=True)
    x=grid(5,100)
    add('convection_steady_temperature','换热系数与稳态温升','Convective coefficient and steady temperature','thermal2','thermalcell','Convective cooling sets a heat-source/area-dependent steady temperature rise.','DeltaT=P/(hA)',{'P_W':2,'area_m2':.015},'Single surface and uniform ambient; radiation and internal gradients excluded.','Convective coefficient (W m$^{-2}$ K$^{-1}$)','Steady temperature rise (K)',x,{'2 W / 0.015 m²':2/(x*.015)},positive=True)
    x=grid(0,20)
    add('thermal_wave_penetration','周期加热的穿透与相位','Thermal-wave penetration and phase','thermal2','thermal','A periodic temperature boundary creates depth-dependent thermal-wave attenuation.','Tamp/T0=exp(-z/delta); delta=sqrt(2alpha/omega)',{'alpha_m2_s':1e-6,'period_s':[60,300,1200]},'Semi-infinite homogeneous solid, sinusoidal boundary, linear heat equation.','Depth (mm)','Temperature amplitude / boundary amplitude',x,{f'{p:g} s period':np.exp(-x*1e-3/np.sqrt(2*1e-6/(2*np.pi/p))) for p in [60,300,1200]},unit_interval=True)
    x=grid(300,450)
    add('heat_generation_removal','发热与散热的稳态交点','Heat generation and removal balance','thermal2','heat','Assumed temperature-dependent reaction heat can exceed linear removal.','Pgen=P0 exp[-Ea/R(1/T-1/Tref)]; Prem=G(T-Tamb)',{'P0_W':.05,'Ea_J_mol':30000,'Tref_K':300,'G_W_K':.015,'Tamb_K':300},'Scalar illustration only, not thermal-runaway onset or a safety prediction.','Temperature (K)','Heat rate (W)',x,{'Assumed reaction heat':.05*np.exp(-30000/R*(1/x-1/300)),'Linear removal':.015*(x-300)},positive=True)

    # 41–50: scattering relationships distinct from the previous cubic/Bragg
    # examples. No real phase intensity or fitted radius is assigned.
    x=grid(0,.06)
    add('guinier_radius','Guinier 斜率与回转半径','Guinier slope and radius of gyration','scattering2','scattering','Low-q log intensity slope gives an assumed radius of gyration.','ln(I/I0)=-q²Rg²/3',{'Rg_nm':[8,12,16]},'Only qRg<1 is displayed; dilute noninteracting particles.','Scattering vector squared (nm$^{-2}$)','Log relative intensity',x*x,{f'Rg = {rg:g} nm':-x*x*rg*rg/3 for rg in [8,12,16]})
    x=lg(-2,0)
    add('sphere_form_minima','球体半径与形状因子极小值','Sphere radius and form-factor minima','scattering2','sphere','Sphere form-factor minima shift with inverse particle radius.','P(q)=[3(sin(qR)-qRcos(qR))/(qR)^3]²; plotted response=P+1e-8',{'R_nm':[8,14,22],'declared_dimensionless_display_floor':1e-8},'Monodisperse dilute spheres; arbitrary intensity, no structure factor. The declared positive display floor permits log axes and is not physical background.','Scattering vector (nm$^{-1}$)','Normalized form factor + floor',x,{f'R = {rr:g} nm':sphere(x,rr)+1e-8 for rr in [8,14,22]},xscale='log',yscale='log',positive=True)
    x=lg(-2,0)
    u=x*10; v=x*15
    f1=3*(np.sin(u)-u*np.cos(u))/u**3
    f2=3*(np.sin(v)-v*np.cos(v))/v**3
    add('core_shell_contrast','核壳散射的对比度干涉','Core-shell scattering contrast interference','scattering2','sphere','Coherent core and shell amplitudes interfere before intensity is squared.','A=(rhoc-rhos)Vc Fc+(rhos-rhosolv)Vtot Ftot; plotted response=(A/Vcore)²+1e-8',{'Rcore_nm':10,'Rtotal_nm':15,'core_minus_shell_contrast':1,'shell_minus_solvent_contrasts':[.5,-.5],'declared_dimensionless_display_floor':1e-8},'Dilute concentric spheres; independently chosen contrast, not a battery material fit. The declared log-display floor is not physical background.','Scattering vector (nm$^{-1}$)','Relative intensity + floor',x,{'Same-sign contrast':(f1+.5*(15/10)**3*f2)**2+1e-8,'Opposite-sign contrast':(f1-.5*(15/10)**3*f2)**2+1e-8},xscale='log',yscale='log',positive=True)
    x=lg(-1,1)
    add('porod_compensation','Porod 区域的补偿图','Porod compensated intensity','scattering2','scattering','A sharp-interface q^-4 asymptote is tested by a q^4 compensated plot.','I=K/q^4+B; q^4 I=K+Bq^4',{'K_relative':1,'B_relative':.0002},'Asymptotic illustrative region, not a measured specific surface area.','Scattering vector (nm$^{-1}$)','q$^4$ × intensity (relative)',x,{'Sharp interface + background':1+.0002*x**4,'Background-free asymptote':np.ones_like(x)},xscale='log',positive=True)
    x=lg(-2,0)
    add('fractal_scattering','幂律散射与分形指数','Scattering power law and fractal exponent','scattering2','scattering','Different power-law exponents represent distinct correlation scaling assumptions.','I(q)=(q/q0)^(-D)',{'D':[1.5,2,2.5],'q0_nm_inv':.1},'Restricted scaling interval only; no claim that exponent identifies a real morphology.','Scattering vector (nm$^{-1}$)','Relative intensity',x,{f'Exponent {d:g}':(x/.1)**(-d) for d in [1.5,2,2.5]},xscale='log',yscale='log',positive=True)
    x=lg(-2,0); rr=grid(8,22,101); weights=np.exp(-.5*((rr-15)/3)**2); weights/=weights.sum()
    add('size_polydispersity','粒径分布与散射振荡','Size distribution and scattering oscillations','scattering2','sphere','A declared number-size distribution changes the volume-squared weighted scattering.','I(q)=sum[p(R) R^6 P(q,R)]/sum[p(R)R^6]; plotted response=I+1e-8',{'mean_radius_nm':15,'sd_radius_nm':3,'integration_points':101,'declared_dimensionless_display_floor':1e-8},'Truncated Gaussian number distribution, dilute spheres; inversion is not unique. The declared log-display floor is not physical background.','Scattering vector (nm$^{-1}$)','Normalized intensity + floor',x,{'Monodisperse R=15 nm':sphere(x,15)+1e-8,'Number-polydisperse':sum(w*r**6*sphere(x,r) for w,r in zip(weights,rr))/sum(weights*rr**6)+1e-8},xscale='log',yscale='log',positive=True)
    x=grid(.1,.6)
    add('williamson_hall_strain','峰展宽与尺寸/应变分离','Peak broadening and size-strain separation','scattering2','structure','Williamson-Hall separates intercept size and slope strain under restricted assumptions.','beta*cos(theta)=K*lambda/D+4*epsilon*sin(theta)',{'K':.9,'lambda_nm':.15406,'D_nm':40,'strain':[0,.001,.002]},'Instrument-corrected breadth in radians; isotropic size/strain and simple additive profile assumption.','4 sin(θ)','β cos(θ) (rad)',4*x,{f'Strain {e:g}':.9*.15406/40+4*e*x for e in [0,.001,.002]},positive=True)
    x=grid(0,12)
    add('debye_waller_attenuation','原子位移与衍射强度衰减','Atomic displacement and intensity attenuation','scattering2','scattering','An assumed displacement factor attenuates high-q coherent intensity.','I/Istatic=exp(-q²<u²>/3)',{'mean_square_displacement_A2':[.01,.03,.06]},'Isotropic independent-displacement factor only; no actual temperature or phase assigned.','Scattering vector (Å$^{-1}$)','Intensity / static intensity',x,{f'⟨u²⟩ = {u:g} Å²':np.exp(-x*x*u/3) for u in [.01,.03,.06]},unit_interval=True)
    x=grid(.5,5)
    add('q_realspace_scale','散射矢量与实空间周期','Scattering vector and real-space period','scattering2','scattering','Reciprocal-space location is converted to a characteristic spatial period.','d=2*pi/q',{'conversion':'q in nm^-1 gives d in nm'},'A period conversion is not particle size, bond length or phase identification by itself.','Scattering vector (nm$^{-1}$)','Characteristic period (nm)',x,{'Reciprocal-space conversion':2*np.pi/x},positive=True)
    x=grid(0,1)
    add('two_phase_scattering_weights','两相数量与校准强度权重','Two-phase fraction and calibrated intensity weights','scattering2','structure','Known hypothetical intensity factors make phase intensity proportional to phase amount.','IA=sA*f; IB=sB*(1-f)',{'sA_relative':1.2,'sB_relative':.7},'Hypothetical calibrated factors only; real fractions need texture, absorption and refinement controls.','Assumed phase-A volume fraction','Integrated intensity (a.u.)',x,{'Phase A factor 1.2':1.2*x,'Phase B factor 0.7':.7*(1-x)},positive=True)

    # 51–60: signal formation / time-domain spectroscopy.
    x=grid(-8,8)
    add('line_shape_tails','谱线尾部与展宽形式','Spectral tails and broadening form','spectroscopy2','beer','Normalized equal-area Gaussian, Lorentzian and Voigt lines have different tails.','G=exp(-x²/(2sigma²))/(sigma sqrt(2pi)); L=gamma/[pi(x²+gamma²)]; V=G*L',{'sigma':1,'gamma':1,'coordinate_unit':'relative frequency unit'},'Analytic line-shape comparison only; no chemical assignment or fit.','Frequency offset (relative unit)','Probability-density line shape',x,{'Gaussian':np.exp(-x*x/2)/np.sqrt(2*np.pi),'Lorentzian':1/(np.pi*(x*x+1)),'Voigt convolution':voigt_profile(x,1,1)},positive=True)
    x=grid(250,700)
    wn=500.; laser=1e7/532
    add('raman_thermal_ratio','温度与反 Stokes/Stokes 比','Temperature and anti-Stokes/Stokes ratio','spectroscopy2','solvation','Thermal occupation sets an ideal Raman intensity ratio after optical-frequency factors.','IAS/IS=[(nu0+nuv)/(nu0-nuv)]^4 exp(-hc nuv/kBT)',{'raman_shift_cm_inv':wn,'laser_nm':532},'Equilibrium spontaneous Raman and calibrated instrument response; no SERS enhancement or local-temperature validation.','Temperature (K)','Anti-Stokes / Stokes intensity',x,{'Ideal thermal occupation':((laser+wn)/(laser-wn))**4*np.exp(-H*C*wn*100/(KB*x))},positive=True)
    x=grid(0,.002)
    add('beer_path_concentration','浓度、光程与吸光度','Concentration, path length and absorbance','spectroscopy2','beer','Absorbance scales with concentration and declared optical path length.','A=epsilon*c*l',{'epsilon_L_mol_cm':600,'path_cm':[.2,.5,1]},'Homogeneous narrow-band dilute absorber; scattering and detector saturation excluded.','Concentration (mol L$^{-1}$)','Absorbance',x,{f'{ll:g} cm path':600*x*ll for ll in [.2,.5,1]},positive=True)
    x=grid(0,5)
    add('nmr_longitudinal_recovery','核磁纵向恢复','NMR longitudinal recovery','spectroscopy2','relaxation','Longitudinal magnetization recovery depends on repetition delay.','Mz/M0=1-exp(-t/T1)',{'T1_s':[.4,.8,1.2]},'Ideal saturation recovery; one relaxation component, no exchange or pulse imperfection.','Recovery delay (s)','Longitudinal magnetization / equilibrium',x,{f'T1 = {tt:g} s':1-np.exp(-x/tt) for tt in [.4,.8,1.2]},unit_interval=True)
    x=grid(0,.3)
    add('nmr_transverse_echo','核磁回波与横向弛豫','NMR echo time and transverse relaxation','spectroscopy2','relaxation','Echo amplitude decays with total echo time, distinct from repetition delay.','S/S0=exp(-TE/T2)',{'T2_s':[.03,.06,.1]},'Single-component ideal spin echo; T2 differs from inhomogeneous free-induction T2*.','Echo time (s)','Echo signal / initial signal',x,{f'T2 = {tt:g} s':np.exp(-x/tt) for tt in [.03,.06,.1]},unit_interval=True)
    x=grid(0,5e9)
    add('pfg_diffusion_attenuation','PFG 编码与扩散信号衰减','PFG encoding and diffusion attenuation','spectroscopy2','pfg','Gradient encoding attenuates a free-diffusion NMR signal.','S/S0=exp(-bD); b=gamma²g²delta²(Delta-delta/3)',{'D_m2_s':[2e-10,5e-10,8e-10]},'Gaussian free diffusion and rectangular gradient pulses; restricted/exchanging systems need an adapted model.','Diffusion encoding b (s m$^{-2}$)','NMR signal / unencoded signal',x,{f'D = {d/1e-10:g} × 10⁻¹⁰ m²/s':np.exp(-x*d) for d in [2e-10,5e-10,8e-10]},unit_interval=True)
    x=grid(0,180)
    add('raman_polarization','平行偏振角与 Raman 信号','Parallel polarization angle and Raman signal','spectroscopy2','solvation','Parallel incident and detected polarizations rotate together relative to a declared diagonal Raman tensor.','e_in=e_out=(cos(theta),sin(theta)); I(theta)∝|e_out^T diag(a,b) e_in|²=|a cos²(theta)+b sin²(theta)|²',{'tensor_diagonal_relative':[1,.3],'polarizer_configuration':'parallel, incident and detected axes rotated together'},'Single aligned tensor and ideal parallel polarizers; no structural assignment or powder average.','Parallel polarization angle (degree)','Relative Raman intensity',x,{'Parallel tensor projection':(np.cos(np.deg2rad(x))**2+.3*np.sin(np.deg2rad(x))**2)**2},positive=True)
    x=grid(1,4)
    add('isotope_frequency_shift','同位素质量与振动频率','Isotope mass and vibration frequency','spectroscopy2','beer','Harmonic frequency changes with reduced mass when the force constant is fixed.','nu=(1/(2pi c))*sqrt(k/mu); mu=m1m2/(m1+m2)',{'m2_u':12,'k_N_m':500,'u_kg':1.66053906660e-27},'Harmonic diatomic illustration; no real bond assignment or anharmonic isotope correction.','Variable isotope mass (u)','Vibration wavenumber (cm$^{-1}$)',x,{'Fixed force constant':np.sqrt(500/((x*12/(x+12))*1.66053906660e-27))/(2*np.pi*C*100)},positive=True)
    x=grid(7100,7140)
    a=.5*(1+erf((x-7118)/1.2));b=.5*(1+erf((x-7124)/1.2))
    add('xas_linear_mixture','XAS 参考态的线性混合','XAS reference-state linear mixture','spectroscopy2','surface','A declared convex mixture retains normalized weights of two hypothetical edge shapes.','mu_mix=f*muA+(1-f)*muB',{'f':[.2,.5,.8],'edge_positions_eV':[7118,7124]},'Fictitious edge positions; valid linear-combination assumptions do not prove oxidation-state fractions.','Photon energy (eV)','Normalized absorption',x,{f'Fraction A = {f:g}':f*a+(1-f)*b for f in [.2,.5,.8]},unit_interval=True)
    x=grid(0,3)
    add('optical_stray_light','杂散光与吸光度非线性','Stray light and absorbance nonlinearity','spectroscopy2','beer','Additive stray light biases large absorbance even when intrinsic Beer law is linear.','Aobs=-log10[(10^-Atrue+s)/(1+s)]',{'stray_fraction':[0,.001,.01]},'Declared instrument nuisance, no correction of real spectra without calibration.','True absorbance','Apparent absorbance',x,{f'Stray fraction {s:g}':-np.log10((10**(-x)+s)/(1+s)) for s in [0,.001,.01]},positive=True)

    # 61–70: surface sensitivity and instrument response. SIMS intensities
    # remain signals; depth and concentration only appear as explicit inputs.
    x=grid(0,12)
    add('xps_overlayer_attenuation','覆层厚度与基底 XPS 信号','Overlayer thickness and substrate XPS signal','surface2','xps','Known attenuation length controls substrate signal through a uniform overlayer.','I/I0=exp[-d/(lambda*cos(theta))]',{'lambda_nm':3,'angle_from_normal_deg':[0,45,70]},'Illustrative EAL, flat uniform overlayer; elastic scattering and roughness excluded.','Overlayer thickness (nm)','Substrate signal / bare signal',x,{f'{ang:g}° from normal':np.exp(-x/(3*np.cos(np.deg2rad(ang)))) for ang in [0,45,70]},unit_interval=True)
    x=grid(0,12)
    add('xps_depth_kernel','出射角与深度灵敏度核','Takeoff angle and depth-sensitivity kernel','surface2','xps','Takeoff geometry changes the normalized depth response rather than a sharp sampling depth.','w(z)=exp[-z/(lambda*cos(theta))]/(lambda*cos(theta))',{'lambda_nm':3,'angle_from_normal_deg':[0,45,70]},'Semi-infinite uniform medium and illustrative EAL; information depth is cumulative.','Depth (nm)','Depth kernel (nm$^{-1}$)',x,{f'{ang:g}° from normal':np.exp(-x/(3*np.cos(np.deg2rad(ang))))/(3*np.cos(np.deg2rad(ang))) for ang in [0,45,70]},positive=True)
    x=grid(.01,8)
    add('xps_layer_peak_ratio','薄层厚度与层/基底峰比','Overlayer thickness and layer/substrate ratio','surface2','xps','Finite overlayer and attenuated substrate produce a nonlinear peak-intensity ratio.','Iover/Isub=(1-exp(-d/lambda))/exp(-d/lambda)',{'lambda_nm':3,'relative_sensitivity':1},'Equal hypothetical sensitivity/attenuation factors; actual thickness needs known densities and EALs.','Overlayer thickness (nm)','Layer / substrate peak ratio',x,{'Equal-sensitivity illustration':np.expm1(x/3)},positive=True)
    x=grid(0,1)
    add('sims_matrix_response','SIMS 基体效应与离子响应','SIMS matrix effect and ion response','surface2','sims','The same composition input can yield different secondary-ion signals in different matrices.','S=Y(matrix)*c; illustrative nonlinear S=Y*c²',{'relative_yields':[.2,1,3]},'c is a declared calibration input; plotted S is signal, not a measured concentration.','Declared analyte fraction (calibration input)','Secondary-ion signal (a.u.)',x,{'Matrix yield 0.2':.2*x,'Matrix yield 1':x,'Cluster nonlinear response':3*x*x},positive=True)
    x=grid(0,100)
    add('sputter_interface_broadening','溅射界面与展宽卷积','Sputter interface and response broadening','surface2','sims','An abrupt signal interface is broadened by an explicitly declared response kernel.','S=0.5 erfc[(t-t0)/(sqrt(2)*sigma_t)]',{'interface_time_s':50,'sigma_s':[2,5,10]},'Kernel combines illustrative mixing/roughness; sputter time remains uncalibrated depth.','Sputter time (s)','Normalized ion signal',x,{f'Kernel σ = {ss:g} s':.5*erfc((x-50)/(np.sqrt(2)*ss)) for ss in [2,5,10]},unit_interval=True)
    x=grid(0,100)
    add('sputter_rate_depth','可变溅射速率与深度标定','Variable sputter rate and depth calibration','surface2','sims','Depth is the integral of a separately declared/calibrated sputter rate.','z(t)=integral(vsputter dt)',{'v_initial_nm_s':.4,'v_final_nm_s':.8,'change_time_s':50},'Synthetic calibrated-rate illustration; must measure crater depth/material rate for author data.','Sputter time (s)','Hypothetically calibrated depth (nm)',x,{'Constant rate':.4*x,'Two-layer rate':.4*np.minimum(x,50)+.8*np.maximum(x-50,0)},positive=True)
    x=grid(27.8,28.3,601)
    add('sims_mass_resolution','质量分辨率与离子峰重叠','Mass resolution and ion-peak overlap','surface2','sims','Resolving power controls overlap of two hypothetical mass peaks.','sigma=m/(2.355*R); S=sum A exp[-(m-mi)²/(2sigma²)]',{'m_over_z_centers':[28,28.05],'resolving_power':[500,1500,5000]},'Illustrative mass-to-charge peaks; no species assignment or measured resolving power.','Mass-to-charge ratio (u/e)','Ion signal (a.u.)',x,{f'R = {rp:g}':np.exp(-.5*((x-28)/(28/(2.355*rp)))**2)+.6*np.exp(-.5*((x-28.05)/(28.05/(2.355*rp)))**2) for rp in [500,1500,5000]},positive=True)
    x=grid(-5,5)
    add('lateral_psf_resolution','空间响应与边界分辨率','Lateral response and edge resolution','surface2','sims','An ion-image point-spread function broadens a step edge.','S(x)=0.5[1+erf(x/(sqrt(2)*sigma))]',{'psf_sigma_um':[.2,.5,1]},'One-dimensional illustrative imaging response; not quantitative 3D reconstruction.','Lateral edge position (µm)','Normalized ion-image signal',x,{f'PSF σ = {ss:g} µm':.5*(1+erf(x/(np.sqrt(2)*ss))) for ss in [.2,.5,1]},unit_interval=True)
    x=grid(280,290)
    add('xps_charge_shift','表面充电与结合能位移','Surface charging and binding-energy shift','surface2','surface','Electrostatic charging shifts a generic XPS peak without changing its chemical model.','Eapparent=Etrue+e*Vcharge',{'generic_peak_eV':284.5,'sigma_eV':.45,'charge_shift_eV':[0,1,2]},'Fictitious peak with no species label; chemical assignment requires charge/reference controls.','Apparent binding energy (eV)','XPS signal (a.u.)',x,{f'Charge shift {s:g} eV':np.exp(-.5*((x-284.5-s)/.45)**2) for s in [0,1,2]},positive=True)
    x=grid(.05,.95)
    add('xps_sensitivity_normalization','灵敏度因子与原子占比','Sensitivity factors and atomic-fraction normalization','surface2','xps','Unequal sensitivity factors bias raw intensity fractions.','IA=sA*x; IB=sB*(1-x); xcorrected=(IA/sA)/(IA/sA+IB/sB)',{'sA':2,'sB':.6},'Ideal homogeneous binary composition and known sensitivity factors; no real compositional result.','Declared atomic fraction A','Recovered fraction A',x,{'Raw intensity fraction':2*x/(2*x+.6*(1-x)),'Sensitivity-corrected':x},unit_interval=True)

    # 71–80: thermodynamics, association and dynamical signal interpretation.
    x=grid(.001,2)
    free=(np.sqrt(1+4*3*x)-1)/(2*3)
    add('ion_pair_mass_action','盐浓度与离子配对质量作用','Salt concentration and ion-pair mass action','solvation2','correlation','An ideal association equilibrium changes free-ion fraction with total salt.','ctot=cfree+K cfree²; ffree=cfree/ctot',{'K_L_mol':3},'Ideal neutral-pair association only; activities and clusters excluded.','Total salt (mol L$^{-1}$)','Free-ion fraction',x,{'Ideal pair equilibrium':free/x},unit_interval=True)
    x=grid(250,500)
    p=1/(1+np.exp(3000/(R*x)))
    add('boltzmann_two_states','温度与两态热占比','Temperature and two-state thermal population','solvation2','correlation','A declared free-energy separation sets a two-state thermal population.','pB=1/[1+exp(DeltaG/(RT))]',{'DeltaG_J_mol':3000,'degeneracy_ratio':1},'Two equilibrium states and temperature-independent free-energy gap; no solvent-state assignment.','Temperature (K)','State population fraction',x,{'Higher-free-energy B':p,'Lower-free-energy A':1-p},unit_interval=True)
    x=grid(0,4)
    add('competitive_coordination','竞争配位与占位守恒','Competitive coordination and site conservation','solvation2','correlation','Competing ideal ligands share a conserved population of independent sites.','thetaA=KA aA/(1+KA aA+KB aB); thetaB=KB aB/denominator',{'KA':2,'KB':1,'aB':1},'Ideal independent sites, one ligand per site; not an inferred coordination shell.','Ligand-A activity','Site occupation fraction',x,{'A-bound':2*x/(2+2*x),'B-bound':1/(2+2*x),'Vacant':1/(2+2*x)},unit_interval=True)
    x=grid(0,5)
    add('residence_survival','配位驻留的生存函数','Coordination-residence survival function','solvation2','correlation','A stretched survival model separates mean residence from one exponential time.','S(t)=exp[-(t/tau)^beta]',{'tau_ns':1,'beta':[.6,1,1.4]},'Declared stochastic model; continuous/intermittent definitions must be chosen for author trajectories.','Residence time (ns)','Survival probability',x,{f'β = {b:g}':np.exp(-x**b) for b in [.6,1,1.4]},unit_interval=True)
    x=grid(1/400,1/260)
    add('vanthoff_equilibrium','逆温度与平衡常数','Inverse temperature and equilibrium constant','solvation2','correlation','Assumed constant reaction enthalpy sets an equilibrium-temperature slope.','ln K=-DeltaH/(RT)+DeltaS/R',{'DeltaH_J_mol':-12000,'DeltaS_J_molK':-35},'Fixed standard states, constant enthalpy/entropy; not a fitted association enthalpy.','Inverse temperature (K$^{-1}$)','Log equilibrium constant',x,{'Declared equilibrium':12000*x/R-35/R})
    x=grid(.2,1.2)
    g=1+2*np.exp(-.5*((x-.45)/.06)**2)-.6*np.exp(-.5*((x-.65)/.07)**2)
    add('rdf_potential_mean_force','RDF 与平均力势','RDF and potential of mean force','solvation2','correlation','A normalized radial distribution can be mapped to a reference-zero mean-force potential.','W(r)=-RT ln g(r)',{'T_K':T,'analytic_rdf':'baseline 1 with positive peak and trough'},'Equilibrium pair distribution, chosen zero at g=1; pair PMF is not bare interaction energy.','Pair separation (nm)','Mean-force potential (kJ mol$^{-1}$)',x,{'From analytic g(r)':-R*T*np.log(g)/1000})
    x=lg(5,11)
    w=2*np.pi*x; tau=1e-8
    add('dielectric_relaxation','频率与介电弛豫损耗','Frequency and dielectric relaxation loss','solvation2','dispersion','A Debye relaxation separates real permittivity and a positive loss peak.','epsilon*=epsiloninf+Deltaepsilon/(1+i omega tau)',{'epsilon_inf':3,'Delta_epsilon':20,'tau_s':tau},'Single isotropic Debye pole; ionic dc conduction excluded.','Frequency (Hz)','Relative permittivity / loss',x,{'Real permittivity':3+20/(1+(w*tau)**2),'Positive dielectric loss':20*w*tau/(1+(w*tau)**2)},xscale='log',positive=True)
    x=grid(.5,10)
    add('stokes_einstein_viscosity','黏度与示踪扩散','Viscosity and tracer diffusion','solvation2','correlation','A continuum hydrodynamic radius produces inverse-viscosity tracer diffusion.','D=kBT/(6pi eta r)',{'T_K':T,'radius_nm':.3},'Continuum dilute no-slip sphere; small ions and concentrated electrolytes can violate this relation.','Dynamic viscosity (mPa s)','Tracer diffusivity (10$^{-10}$ m$^2$ s$^{-1}$)',x,{'r = 0.3 nm':KB*T/(6*np.pi*x*1e-3*.3e-9)*1e10},positive=True)
    x=grid(.001,1)
    add('thermodynamic_factor','活度模型与热力学因子','Activity model and thermodynamic factor','solvation2','correlation','A declared activity coefficient changes the concentration derivative governing thermodynamic transport.','gamma=exp(Ac); Gamma=1+dln(gamma)/dln(c)=1+Ac',{'A_L_mol':1.5},'Illustrative activity model, not Debye-Huckel or a measured electrolyte factor.','Salt concentration (mol L$^{-1}$)','Thermodynamic factor',x,{'Ideal Γ=1':np.ones_like(x),'Declared nonideal activity':1+1.5*x},positive=True)
    x=grid(0,5)
    add('exchange_signal_correlation','两态交换与相关信号','Two-state exchange and correlation signal','solvation2','correlation','A stationary two-state exchange model has an exponential covariance time.','C(t)/C(0)=exp[-(kAB+kBA)t]',{'kAB_ns_inv':.4,'kBA_ns_inv':.6},'Markov two-state model; a correlation decay alone cannot identify solvation states.','Correlation delay (ns)','Normalized state covariance',x,{'Two-state Markov exchange':np.exp(-x)},unit_interval=True)

    # 81–90: aging / mechanical coupling; each boundary is explicit.
    x=grid(0,400)
    add('sei_diffusion_growth','扩散受限膜厚增长','Diffusion-limited film growth','degradation2','growth','A diffusion-limited planar film model grows with square-root time.','L=sqrt(L0²+2Kt)',{'L0_nm':5,'K_nm2_h':2},'Single stable passivating film and fixed transport; not a universal SEI law.','Aging time (h)','Film thickness (nm)',x,{'Restricted diffusion model':np.sqrt(25+4*x)},positive=True)
    x=grid(0,100)
    add('film_resistance_thickness','膜厚与电阻电位损失','Film thickness and resistance loss','degradation2','sei','A film conductivity links thickness to area resistance and voltage loss.','RA=L/kappa; eta=i*RA',{'kappa_S_m':1e-6,'i_A_m2':10},'Uniform ohmic film, fixed conductivity; a fitted resistance does not determine chemistry.','Film thickness (nm)','Film potential loss (V)',x,{'Uniform resistive film':10*x*1e-9/1e-6},positive=True)
    x=grid(0,1000)
    add('inventory_compounding','逐圈效率与库存累积','Cycle efficiency and inventory compounding','degradation2','aging','Multiplicative fixed fractional inventory loss differs from a constant absolute loss ledger.','Qn/Q0=CE^n',{'CE_fraction':[.999,.9995,.9998]},'Simplified inventory-limited cell with fixed fractional loss; real CE cannot uniquely forecast life.','Equivalent cycle count','Retained inventory fraction',x,{f'CE = {100*ce:g}%':ce**x for ce in [.999,.9995,.9998]},unit_interval=True)
    x=grid(0,1000)
    add('parasitic_charge_ledger','寄生电流与容量损失账本','Parasitic current and capacity-loss ledger','degradation2','aging','Integrated parasitic current consumes an explicit finite capacity inventory.','Qloss=Ipar*t; Qremain=Q0-Qloss',{'Q0_mAh':1000,'Ipar_mA':.15},'Constant absolute parasitic current; plotted horizon stops before inventory exhaustion.','Calendar time (h)','Capacity inventory (mAh)',x,{'Consumed inventory':.15*x,'Remaining inventory':1000-.15*x},positive=True)
    x=grid(0,90)
    add('self_discharge_relaxation','漏电与静置自放电','Leakage and rest self-discharge','degradation2','aging','An assumed linear leakage pathway gives exponential charge decay.','Q/Q0=exp(-t/tau)',{'tau_days':[60,120,240]},'Lumped leakage surrogate; no real battery self-discharge or recovery prediction.','Rest duration (day)','Retained charge fraction',x,{f'τ = {tt:g} days':np.exp(-x/tt) for tt in [60,120,240]},unit_interval=True)
    x=grid(0,1)
    add('chemical_expansion','锂占位与化学膨胀','Lithium occupation and chemical expansion','degradation2','stress','Declared volumetric expansion gives isotropic linear strain.','linear_strain=(1+beta*x)^(1/3)-1',{'beta_volume_fraction':.09},'Isotropic free expansion only; no stress when unconstrained and uniform.','Occupied-site fraction','Free linear strain (%)',x,{'9% full-occupation volume change':((1+.09*x)**(1/3)-1)*100},positive=True)
    x=grid(0,1)
    # Eigenstrain e(r)=e0+a r², isotropic sphere, traction-free boundary.
    E=10e9; nu=.3; a=.006; pref=E/(1-nu)
    sr=2*pref*a*(1-x*x)/5; st=pref*a*(2-4*x*x)/5
    add('sphere_diffusion_stress','球内浓度梯度与弹性应力','Spherical concentration gradient and stress','degradation2','stress','A quadratic eigenstrain field produces radial/tangential stresses with a traction-free surface.','sigma_r=2E*a/(5(1-nu))*(1-r²); sigma_t=E*a/(5(1-nu))*(2-4r²)',{'E_Pa':E,'nu':nu,'quadratic_eigenstrain_coefficient':a},'Normalized radius, isotropic small-strain elasticity; assumed concentration profile, not a coupled diffusion solution.','Radius / particle radius','Elastic stress (MPa)',x,{'Radial':sr/1e6,'Tangential':st/1e6})
    x=grid(0,.02)
    add('elastic_energy_strain','约束应变与弹性能密度','Constrained strain and elastic energy density','degradation2','stress','A uniaxial elastic constraint stores a quadratic energy density.','W=0.5*E*epsilon²',{'E_Pa':10e9},'Uniaxial linear elasticity; not a fracture threshold or life prediction.','Constrained elastic strain','Elastic energy density (MJ m$^{-3}$)',x,{'E = 10 GPa':.5*10e9*x*x/1e6},positive=True)
    x=grid(-500,500);x[len(x)//2]=0.0
    add('stress_potential_coupling','静水应力与平衡电位','Hydrostatic stress and equilibrium potential','degradation2','stresspotential','At fixed composition and electrolyte activity, tensile-positive hydrostatic stress lowers the inserted neutral Li chemical potential and raises the Li-referenced equilibrium electrode potential.','sigma_h=tr(sigma)/3; Delta_mu=-Omega*sigma_h; Delta_U=-Delta_mu/F=+Omega*sigma_h/F',{'Omega_m3_mol':3e-6,'sign':'sigma_h positive in tension, negative in compression','fixed':'composition and electrolyte activity','approximation':'first-order isotropic small-strain coupling; composition-dependent elastic-compliance term neglected'},'Hydrostatic specialization of the first-order Larche-Cahn stress term. Omega=3 cm³/mol is an independently assumed teaching value, not a Si fit or the paper biaxial-film coefficient. Fixed composition/activity, small-strain isotropic thermodynamics; excludes elastic-compliance derivatives, finite-strain corrections, hysteresis and kinetic overpotential.','Hydrostatic stress (MPa; tensile +)','Equilibrium potential shift (mV)',x,{'Ω = 3 cm³/mol':stress_equilibrium_shift(x,3e-6)})
    x=grid(0,1000)
    add('sei_pore_consumption','界面膜增长与孔隙消耗','Interphase growth and pore-volume consumption','degradation2','sei','A declared internal area converts film growth to a bounded pore-volume loss.','epsilon=epsilon0-av*(L-L0)',{'epsilon0':.35,'av_m_inv':3e5,'L0_nm':5,'growth_K_nm2_h':2},'Uniform fixed surface area and film; no evolving cracks or isolated domains.','Aging time (h)','Remaining pore volume fraction',x,{'Area-based volume ledger':.35-3e5*(np.sqrt(25+4*x)-5)*1e-9},unit_interval=True)

    # 91–100: scientific measurement / metrology plots, with declared input
    # uncertainty. These are not invented replicate experiments.
    x=np.arange(2,151,dtype=float)
    exact=1.2+0.4*(1-np.cos(1))/1
    vals=[]
    for n in x.astype(int):
        tt=grid(0,1,n);vals.append(abs(np.trapz(1.2+.4*np.sin(tt),tt)-exact))
    add('charge_quadrature_convergence','电流积分的采样误差','Current integration and sampling error','metrology2','uncertainty','Trapezoidal sampling of a known smooth current gives a calculable charge-integration error.','Q=integral[I(t)dt]; error=|Qtrap-Qanalytic|',{'I_A':'1.2+0.4 sin(t)','time_s':[0,1]},'Known analytic current without noise; empirical bandwidth and timestamp errors excluded.','Number of sampling points','Absolute charge error (C)',x,{'Trapezoidal integration':vals},yscale='log',positive=True)
    x=grid(0,.1)
    add('spectral_baseline_area_bias','谱基线与积分偏差','Spectral baseline and integrated-area bias','metrology2','calibration','An unremoved baseline contributes window-width-dependent integrated area.','Aobs=Atrue+b*W',{'true_area':1,'window_width_relative':[5,10,20]},'Uniform baseline nuisance and fixed integration window; not an automated spectral correction.','Unremoved baseline (a.u.)','Relative integrated area',x,{f'Window width {w:g}':1+x*w for w in [5,10,20]},positive=True)
    x=grid(-.9,.9)
    uc=.005;ud=.005;qch=1;qdis=.995
    var=(ud/qch)**2+(qdis*uc/qch**2)**2-2*qdis/qch**3*x*ud*uc
    add('ce_correlated_uncertainty','电荷协方差与 CE 不确定度','Charge covariance and CE uncertainty','metrology2','uncertainty','Correlated charge uncertainties change a ratio uncertainty.','u²(CE)=(ud/Qc)²+(Qd uc/Qc²)²-2 Qd cov(Qd,Qc)/Qc³',{'Qc_mAh':qch,'Qd_mAh':qdis,'uc_mAh':uc,'ud_mAh':ud},'First-order standard uncertainty of Qd/Qc; covariance needs an actual calibration model.','Charge-error correlation coefficient','CE standard uncertainty (percentage points)',x,{'Ratio propagation':100*np.sqrt(var)},positive=True)
    x=grid(.5,10)
    add('mass_capacity_uncertainty','称量与质量容量不确定度','Weighing and specific-capacity uncertainty','metrology2','uncertainty','A fixed absolute mass uncertainty has larger relative effect at smaller mass.','u(q)/q=sqrt[(uQ/Q)²+(um/m)²]',{'relative_charge_uncertainty':.005,'mass_uncertainty_mg':.02},'Independent charge/mass errors; denominator remains positive and small-error approximation applies.','Active mass (mg)','Relative standard uncertainty (%)',x,{'Charge and weighing':100*np.sqrt(.005**2+(.02/x)**2)},positive=True)
    x=grid(0,5)
    add('inverse_calibration','校准斜率与反演不确定度','Calibration slope and inverse uncertainty','metrology2','calibration','Inverse calibration magnifies a fixed signal uncertainty when sensitivity is small.','u(x)=u(y)/|slope|',{'signal_standard_uncertainty':.02,'slope':'0.2+coordinate'},'Known linear slope/intercept for this teaching form; fitted-coefficient covariance excluded.','Calibration sensitivity (signal/unit)','Input standard uncertainty (unit)',.2+x,{'Inverse linear response':.02/(.2+x)},positive=True)
    x=np.arange(1,101,dtype=float)
    add('mean_uncertainty_samplecount','重复数与均值标准不确定度','Replicate count and mean uncertainty','metrology2','quadrature','Independent repeatability decreases with count while a shared calibration floor persists.','u_mean=sqrt(s_repeat²/n+u_shared²)',{'s_repeat':.03,'u_shared':.01,'unit':'normalized measurement unit'},'The curves are formulas, no invented replicate observations or reported sample experiment.','Independent repeat count','Standard uncertainty (relative unit)',x,{'Repeatability only':.03/np.sqrt(x),'With shared calibration':np.sqrt(.03**2/x+.01**2)},positive=True)
    x=grid(0,24)
    add('instrument_drift_reference','漂移校准与参考通道','Instrument drift and reference correction','metrology2','calibration','A shared drift can be removed only if the reference follows the same nuisance.','ymeas=ytrue+d*t; ycorrected=ymeas-dref*t',{'true_signal':1,'drift_per_h':.004,'reference_drift_per_h':.004},'Known drift illustration; no arbitrary detrending of acquired signal.','Elapsed time (h)','Normalized signal',x,{'Measured with drift':1+.004*x,'Known shared-reference correction':np.ones_like(x)},positive=True)
    x=lg(-4,-1)
    add('digitization_uncertainty','读数分辨率与量化不确定度','Readout resolution and quantization uncertainty','metrology2','quadrature','Uniform quantization error has a resolution-dependent standard uncertainty.','u_resolution=delta/sqrt(12)',{'distribution':'uniform within +/- delta/2'},'Uniform rounding phase assumption; resolution alone is not total instrument uncertainty.','Readout increment (unit)','Quantization standard uncertainty (unit)',x,{'Uniform rounding':x/np.sqrt(12)},xscale='log',yscale='log',positive=True)
    x=np.arange(3,61,dtype=float)
    add('student_coverage_factor','小样本均值与覆盖因子','Small-sample mean and coverage factor','metrology2','quadrature','Student-t coverage differs from an asymptotic normal coverage factor.','k=t_(0.975,n-1)',{'coverage':.95,'degrees_of_freedom':'n-1'},'Independent normal repeated measurements and estimated variance; k is not a universal coverage guarantee.','Independent repeat count','Two-sided 95% coverage factor',x,{'Student t':student_t.ppf(.975,x-1),'Normal asymptote':np.full_like(x,1.95996398454)},positive=True)
    x=grid(-2,2)
    add('linear_calibration_leverage','校准区间与均值预测不确定度','Calibration interval and prediction uncertainty','metrology2','calibration','Uncertainty in the fitted mean response grows away from the calibration center.','u_mean=s*sqrt(1/n+(x-xbar)²/Sxx); u_pred=s*sqrt(1+1/n+(x-xbar)²/Sxx)',{'n':10,'xbar':0,'Sxx':4,'s_signal':.02},'Fixed illustrative linear calibration design; mean confidence and new-observation prediction are distinct.','Input offset from calibration center','Response standard uncertainty',x,{'Fitted mean':.02*np.sqrt(.1+x*x/4),'New observation':.02*np.sqrt(1.1+x*x/4)},positive=True)
    assert len(out)==100 and len({m.ident for m in out})==100
    return out

SCIENCE_TASKS=[(m.ident,m.zh,m.en,m.family,m.basis['references'][0]) for m in catalogue()]
def generate(ident):
    return next(m for m in catalogue() if m.ident==ident)
