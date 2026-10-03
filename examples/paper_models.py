"""Fifty declared analytic teaching tasks, not fifty recolourings.

Journal references were catalogued in paper_references.py before generation.
Every synthetic row is calculated here from a stated model. Parameters are ours;
labels never assign a fictitious material, fit, experiment or mechanism.
The downloaded plot entry reads existing CSV only. This generator is separate.
"""
from __future__ import annotations
import numpy as np
from paper_references import reference

F=96485.33212; R=8.314462618; KB=1.380649e-23; E=1.602176634e-19; NA=6.02214076e23

# id, Chinese title, English title, family, reference. Each has a different
# scientific question / input contract / derived relationship, not just colours.
TASKS = [
 ('eis_rc','单时间常数阻抗','Single-time-constant impedance','eis','eis'),
 ('eis_two_rc','两个弛豫过程','Two relaxation processes','eis','eis'),
 ('eis_cpe','非理想电容弧','Constant-phase-element arc','eis','eis'),
 ('eis_warburg','半无限扩散尾','Semi-infinite diffusion tail','eis','eis'),
 ('eis_transmissive','有限扩散：透过边界','Finite diffusion: transmissive boundary','eis','eis'),
 ('eis_blocking','有限扩散：阻挡边界','Finite diffusion: blocking boundary','eis','eis'),
 ('eis_temperature','温度与阻抗','Temperature-dependent impedance','eis','eis'),
 ('eis_relaxation','弛豫分布与同源阻抗','Relaxation distribution and paired impedance','eis','eis'),
 ('peak_diffusion','峰电流与扫速平方根','Peak current and square-root scan rate','kinetics','diffusion_equations'),
 ('current_b_power','扫速幂律分析','Scan-rate power-law analysis','kinetics','cv'),
 ('dunn_fraction','电流贡献随扫速变化','Scan-rate current contributions','kinetics','cv'),
 ('bv_transfer','过电位与电流','Overpotential and current','kinetics','eis'),
 ('tafel_branch','Tafel 单支路与适用区间','Tafel branch and valid range','kinetics','eis'),
 ('cottrell_current','平面扩散电流瞬态','Planar-diffusion current transient','kinetics','diffusion_equations'),
 ('rdf_cn','RDF 与积分配位数','RDF and integrated coordination number','solvation','solvation'),
 ('rdf_cutoff','配位数与截断半径','Coordination number and cutoff radius','solvation','solvation'),
 ('rdf_density','数密度与配位积分','Number density and coordination integral','solvation','solvation'),
 ('solvation_population','结构分类占比','Structural-class populations','solvation','solvation'),
 ('raman_components','谱线、组分与残差','Spectrum, components and residual','solvation','transport'),
 ('ir_absorbance','吸光度与透过率','Absorbance and transmittance','solvation','transport'),
 ('nmr_lorentzian','核磁线宽与峰面积','NMR linewidth and peak area','solvation','solvation'),
 ('angle_distribution','角分布与归一化','Angular distribution and normalisation','solvation','solvation'),
 ('xrd_fcc','理想立方晶格衍射','Ideal cubic-lattice diffraction','structure','structure'),
 ('scherrer_width','峰宽与晶粒尺寸','Peak width and crystallite size','structure','structure'),
 ('xrd_lattice_shift','晶格变化与峰位','Lattice change and peak position','structure','structure'),
 ('xrd_operando','衍射序列与同源截线','Diffraction sequence and paired profiles','structure','structure'),
 ('xps_doublet','通用 p 双峰约束','Generic p-doublet constraints','structure','surface'),
 ('sputter_components','溅射时间与信号分布','Sputter time and signal distribution','structure','surface'),
 ('ionic_arrhenius','温度与离子电导','Temperature and ionic conductivity','transport','transport'),
 ('activation_fit','Arrhenius 斜率与活化能','Arrhenius slope and activation energy','transport','transport'),
 ('msd_diffusion','均方位移与扩散','Mean-squared displacement and diffusion','transport','transport'),
 ('nernst_einstein','理想自扩散与电导','Ideal self-diffusion and conductivity','transport','correlations'),
 ('polarization_resistance','极化电流与界面电阻','Polarisation current and interface resistance','transport','polarisation'),
 ('conductivity_cellconstant','阻抗、几何与电导率','Resistance, geometry and conductivity','transport','correlations'),
 ('ce_ledger','库伦效率与电荷账本','Coulombic efficiency and charge ledger','performance','performance'),
 ('capacity_areal','质量容量与面容量','Specific and areal capacity','performance','reporting'),
 ('energy_integration','电压与放电能量积分','Voltage and discharge-energy integral','performance','reporting'),
 ('capacity_repeat','合成电池记录与误差','Synthetic cell records and uncertainty','performance','reporting'),
 ('rate_tau','特征时间与倍率容量','Characteristic time and rate capacity','performance','rate'),
 ('rate_exponent','倍率模型的衰减指数','Rate-model decay exponent','performance','rate'),
 ('rate_recovery','倍率序列与回归步骤','Rate sequence and recovery step','performance','rate'),
 ('thickness_timescale','厚度与扩散时间尺度','Thickness and diffusion timescale','performance','rate'),
 ('flow_efficiency','液流电池三种效率','Three flow-battery efficiencies','flow-pv','flow'),
 ('flow_power','极化、电流与功率','Polarisation, current and power','flow-pv','flow'),
 ('pv_jv','理想光伏 J–V 与功率','Ideal photovoltaic J–V and power','flow-pv','pv'),
 ('pv_light','光照强度与 J–V','Illumination and J–V','flow-pv','pv'),
 ('pv_temperature','理想二极管的温度响应','Ideal-diode temperature response','flow-pv','pv'),
 ('pv_series_resistance','串联电阻与填充因子','Series resistance and fill factor','flow-pv','pv'),
 ('pv_shunt_resistance','并联电阻与漏电','Shunt resistance and leakage','flow-pv','pv'),
 ('pv_fill_factor','最大功率点与效率','Maximum-power point and efficiency','flow-pv','pv'),
]
assert len(TASKS)==50 and len({r[0] for r in TASKS})==50

def integral(y,x):
    return np.concatenate(([0.],np.cumsum(.5*(y[1:]+y[:-1])*np.diff(x))))

def rate_capacity(rate,tau=.08,n=.7,q0=170.):
    a=(np.asarray(rate)*tau)**n
    return q0*(1+a*np.expm1(-1/a))

def diode(v,light=1.,temp=298.15,rs=0.,rsh=1e9):
    """Delivered-positive J [mA/cm²]; V+J*Rs uses J in A/cm².

    Unique root of J=JL-J0(expm1((V+J Rs)/(n kT/q)))-(V+J Rs)/Rsh.
    Bisection avoids a silently diverging Newton solution. Temperature scaling
    is declared an ideal barrier model with Eg=1.1eV, not measured device data.
    """
    v=np.asarray(v); vt=1.3*KB*temp/E
    j0=1e-10*(temp/298.15)**3*np.exp(-1.1*E/KB*(1/temp-1/298.15))
    jl=.022*light
    lo=np.full_like(v,-.5);hi=np.full_like(v,.1)
    def residual(j):
        internal=v+j*rs
        return j-jl+j0*np.expm1(np.clip(internal/vt,-700,700))+internal/rsh
    for _ in range(20):
        low=residual(lo)>=0;high=residual(hi)<=0
        if not low.any() and not high.any():break
        lo=np.where(low,lo*2,lo);hi=np.where(high,hi*2,hi)
    if not (np.all(residual(lo)<0) and np.all(residual(hi)>0)):
        raise ValueError('Diode current root could not be bracketed for declared inputs')
    for _ in range(90):
        mid=(lo+hi)/2;mask=residual(mid)>0;hi=np.where(mask,mid,hi);lo=np.where(mask,lo,mid)
    return (lo+hi)*500,dict(n=1.3,J0_A_cm2=float(j0),JL_A_cm2=jl,T_K=temp,Rs_ohm_cm2=rs,Rsh_ohm_cm2=rsh)

def open_circuit(light=1.,temp=298.15,rsh=1e9,**_):
    vt=1.3*KB*temp/E
    j0=1e-10*(temp/298.15)**3*np.exp(-1.1*E/KB*(1/temp-1/298.15))
    lo=0.;hi=1.
    for _ in range(80):
        mid=(lo+hi)/2
        if .022*light-j0*np.expm1(mid/vt)-mid/rsh>0:lo=mid
        else:hi=mid
    return (lo+hi)/2

class Model:
    def __init__(self,task):
        self.ident,self.zh,self.en,self.family,self.ref=task
        self.rows=[];self.panels=[];self.equations=[];self.params={};self.assumptions=[];self.limits=[]
    def panel(self,xlabel,ylabel,title='',**options):
        self.panels.append(dict(xlabel=xlabel,ylabel=ylabel,title=title,**options));return len(self.panels)-1
    def trace(self,panel,label,x,y,**options):
        x,y=np.asarray(x,dtype=float),np.asarray(y,dtype=float)
        if x.ndim!=1 or x.shape!=y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError(self.ident+': invalid analytic series')
        for xx,yy in zip(x,y):self.rows.append(dict(panel=panel,series=label,x=float(xx),y=float(yy),**options))
    def basis(self,*equations,parameters=None,assumptions=(),limits=()):
        self.equations=list(equations);self.params=parameters or {};self.assumptions=list(assumptions);self.limits=list(limits)
        if not self.assumptions:self.assumptions=['Original explicitly idealised model; parameters are illustrative and do not describe the referenced experiment.']
        if not self.limits:self.limits=['A teaching representation cannot establish a material identity or electrochemical mechanism. Author data require verified units, conditions and model applicability.']
        return self

def generate(task):
    m=Model(task);k=m.ident
    if k.startswith('eis_'):
        f=np.geomspace(1e-3,1e5,501);w=2*np.pi*f
        p=m.panel("Z′ (Ω)","−Z″ (Ω)",'Complex impedance',equal=True)
        q=m.panel('Frequency (Hz)','|Z| (Ω)','Same frequency record',xscale='log',yscale='log')
        if k=='eis_relaxation':
            logtau=np.linspace(-7,4,801);tau=np.exp(logtau)
            gamma=18*np.exp(-.5*((logtau-np.log(.003))/.33)**2)/(.33*np.sqrt(2*np.pi))+42*np.exp(-.5*((logtau-np.log(.8))/.5)**2)/(.5*np.sqrt(2*np.pi))
            z=4+np.trapezoid(gamma[None,:]/(1+1j*w[:,None]*tau[None,:]),logtau,axis=1)
            d=m.panel('Relaxation time (s)','γ (Ω)','Declared distribution',xscale='log')
            m.trace(d,'Distribution',tau,gamma);m.trace(p,'Integrated DRT',z.real,-z.imag);m.trace(q,'Integrated DRT',f,np.abs(z))
            return m.basis('Z(ω)=Rs+∫γ(lnτ)/(1+jωτ)dlnτ','∫γdlnτ=polarisation resistance',parameters={'Rs_ohm':4,'peak_R_ohm':[18,42],'peak_tau_s':[.003,.8],'log_tau_sigma':[.33,.5]},limits=['This is forward integration of a declared DRT, not a fitted or recovered DRT. Peaks are not named as physical mechanisms.'])
        groups=[]
        if k=='eis_rc':groups=[('C = 1 mF',35,.001,1),('C = 3 mF',35,.003,1)]
        elif k=='eis_two_rc':groups=[('Separated processes',35,.003,1),('Overlapping processes',35,.0008,1)]
        elif k=='eis_cpe':groups=[('α = 1.00',35,.003,1),('α = 0.85',35,.003,.85),('α = 0.70',35,.003,.7)]
        elif k=='eis_temperature':
            for t in (278.15,298.15,318.15):groups.append((f'{t:.0f} K',35*np.exp(28000/R*(1/t-1/298.15)),.003,1))
        else:groups=[('RC + diffusion',35,.003,1)]
        params=[]
        for label,res,cap,alpha in groups:
            z=4+1/(1/res+cap*(1j*w)**alpha)
            if k=='eis_two_rc':z+=18/(1+1j*w*(.004 if label.startswith('Separated') else .05))
            if k=='eis_warburg':z+=8*(1-1j)/np.sqrt(w)
            elif k in ('eis_transmissive','eis_blocking'):
                u=np.sqrt(1j*w*2);tanh=np.ones_like(u);normal=u.real<20;tanh[normal]=np.tanh(u[normal])
                z+=20*(tanh if k=='eis_transmissive' else 1/tanh)/u
            m.trace(p,label,z.real,-z.imag);m.trace(q,label,f,np.abs(z));params.append(dict(label=label,R_ohm=res,Q_S_s_alpha=cap,alpha=alpha))
        equations=['Z=Rs+(1/R+Q(jω)^α)^−1'];parameters={'Rs_ohm':4,'branches':params,'frequency_Hz':[.001,100000]}
        if k=='eis_warburg':equations.append('Z_W=σ(1−j)/sqrt(ω)');parameters['Warburg_sigma_ohm_s_minus_half']=8
        if k in ('eis_transmissive','eis_blocking'):
            equations.append('Z_D=Rd*'+('tanh' if k=='eis_transmissive' else 'coth')+'(sqrt(jωτd))/sqrt(jωτd)');parameters.update(diffusion_tau_s=2,diffusion_R_ohm=20)
        if k=='eis_two_rc':parameters['second_RC']={'R_ohm':18,'tau_s_by_case':[.004,.05]};equations.append('Second branch: R2/(1+jωτ2)')
        if k=='eis_temperature':parameters.update(Ea_J_mol=28000,Tref_K=298.15,T_K=[278.15,298.15,318.15]);equations.append('R(T)=Rref*exp(Ea/Rg*(1/T−1/Tref))')
        if k in ('eis_warburg','eis_blocking'):
            zoom=m.panel("Z′ (Ω)","−Z″ (Ω)",'Same complete rows, RC-region zoom',equal=True,xlim=[0,85],ylim=[0,85],annotation='Low-frequency branch continues\nbeyond this equal-scale window.')
            m.trace(zoom,label,z.real,-z.imag)
        return m.basis(*equations,parameters=parameters,limits=['Passive lumped circuit, not a unique battery mechanism. Q is a capacitance only when α=1. Finite-diffusion low-frequency limits depend on the declared boundary. The complete equal-scale Nyquist and frequency record are retained alongside any declared zoom. No Kramers–Kronig or measured-data fit is claimed.'])
    if k in ('peak_diffusion','current_b_power','dunn_fraction'):
        v=np.geomspace(.001,.1,40)
        p=m.panel('Scan rate (V s⁻¹)','Peak current (mA)','Forward model',xscale='log' if k=='current_b_power' else 'linear',yscale='log' if k=='current_b_power' else 'linear')
        if k=='peak_diffusion':
            coeff=.4463*F*.07*1e-6*np.sqrt(F*1e-6/(R*298.15))*1000
            for scale in (1,1.5):m.trace(p,f'c = {scale:.1f} mM',v,coeff*scale*np.sqrt(v))
            q=m.panel('√scan rate ((V s⁻¹)½)','Peak current (mA)','Same current')
            for scale in (1,1.5):m.trace(q,f'c = {scale:.1f} mM',np.sqrt(v),coeff*scale*np.sqrt(v))
            return m.basis('ip=0.4463*n*F*A*c*sqrt(n*F*D*v/(R*T))',parameters={'n':1,'A_cm2':.07,'D_cm2_s':1e-6,'c_mol_cm3':[1e-6,1.5e-6],'T_K':298.15},assumptions=['Reversible one-electron planar semi-infinite diffusion; n, A, c, D, T explicitly specified. No CV waveform is fabricated.'],limits=['A sqrt(v) trend alone does not prove diffusion control in an actual porous battery electrode.'])
        if k=='current_b_power':
            for b in (.5,.75,1):m.trace(p,f'b = {b:.2f}',v,2*v**b)
            q=m.panel('log₁₀ [v / (1 V s⁻¹)]','log₁₀ [i / (1 mA)]','Logarithmic slope')
            for b in (.5,.75,1):m.trace(q,f'b = {b:.2f}',np.log10(v),np.log10(2*v**b))
            return m.basis('i=a*v^b; log(i)=log(a)+b*log(v)',parameters={'a_mA_per_V_s_power':2,'b':[.5,.75,1]},limits=['Known forward exponent, not a fit. b alone cannot uniquely identify a transport mechanism.'])
        cap=3*v;diff=.4*np.sqrt(v);total=cap+diff
        m.panels[p]['ylabel']='Current at fixed potential (mA)'
        for label,y in [('Total',total),('v contribution',cap),('√v contribution',diff)]:m.trace(p,label,v,y)
        q=m.panel('Scan rate (V s⁻¹)','Current contribution (%)','Same current components')
        m.trace(q,'v contribution',v,100*cap/total);m.trace(q,'√v contribution',v,100*diff/total)
        return m.basis('i(v)=k1*v+k2*sqrt(v); fractions use the same total',parameters={'k1_mA_s_V':3,'k2_mA_s_half_V_half':.4},limits=['Illustrative decomposition at one fixed potential. It is not a fitted CV, and capacitive current fraction is not automatically stored-charge fraction.'])
    if k in ('bv_transfer','tafel_branch'):
        eta=np.linspace(-.22,.22,401);j=.1*(np.exp(.5*F*eta/(R*298.15))-np.exp(-.5*F*eta/(R*298.15)))
        p=m.panel('Overpotential (V)','Current density (mA cm⁻²)','Symmetric charge transfer');m.trace(p,'Butler–Volmer',eta,j)
        q=m.panel('log₁₀ [j / (1 mA cm⁻²)]','Overpotential (V)','Positive branch only')
        mask=eta>=.1 if k=='tafel_branch' else eta>=.025
        m.trace(q,'Exact positive branch',np.log10(j[mask]),eta[mask])
        if k=='tafel_branch':m.trace(q,'High-η approximation',np.log10(.1*np.exp(.5*F*eta[mask]/(R*298.15))),eta[mask])
        return m.basis('j=j0*[exp(αnFη/RT)−exp(−(1−α)nFη/RT)]','Tafel: η=RT/(αnF)*ln(j/j0), positive high-overpotential branch only',parameters={'j0_mA_cm2':.1,'alpha':.5,'n':1,'T_K':298.15},assumptions=['No ohmic drop or mass-transfer limitation. η is overpotential relative to equilibrium, not a reference-electrode absolute potential.'])
    if k=='cottrell_current':
        t=np.geomspace(.05,100,300);a=F*.07*1e-6*np.sqrt(1e-6/np.pi)*1000
        p=m.panel('Time (s)','Current (mA)','Planar diffusion');m.trace(p,'Ideal step',t,a/np.sqrt(t))
        q=m.panel('t⁻½ (s⁻½)','Current (mA)','Same transient');m.trace(q,'Ideal step',1/np.sqrt(t),a/np.sqrt(t))
        return m.basis('i=nFAc*sqrt(D/(πt))',parameters={'n':1,'A_cm2':.07,'c_mol_cm3':1e-6,'D_cm2_s':1e-6},assumptions=['Instantaneous potential step, semi-infinite planar diffusion; t>0; charging and finite geometry excluded.'],limits=['Do not apply to electrodeposition, convection or arbitrary porous-cell transients without validating the assumptions.'])
    if k.startswith('rdf_'):
        r=np.linspace(0,1,501);g=(1-np.exp(-(r/.24)**8))*(1+5*np.exp(-.5*((r-.285)/.03)**2)+1.2*np.exp(-.5*((r-.49)/.06)**2))
        if k=='rdf_cutoff':
            mask=(r>=.25)&(r<=.44);density=18;cn=4*np.pi*density*integral(g*r*r,r)
            p=m.panel('Cutoff radius (nm)','Coordination number','First-shell cutoff sensitivity')
            m.trace(p,'Integrated first region',r[mask],cn[mask])
            q=m.panel('Cutoff radius (nm)','dCN / dr (nm⁻¹)','Same integral, local sensitivity')
            m.trace(q,'4πρr²g(r)',r[mask],4*np.pi*density*r[mask]**2*g[mask])
            return m.basis('CN(rc)=4πρ∫₀ʳᶜ g(r)r²dr','dCN/drc=4πρrc²g(rc)',parameters={'number_density_nm_minus3':18,'distance_unit':'nm','first_peak_nm':.285,'first_width_nm':.03,'cutoff_sensitivity_window_nm':[.25,.44]},limits=['Analytic first-shell sensitivity, not a fitted MD coordination. Real shell boundaries must be selected from the actual RDF minimum and reported; this window is not a universal cutoff.'])
        densities=[12,18,24] if k=='rdf_density' else [18]
        p=m.panel('Distance (nm)','g(r)','Declared radial model');m.trace(p,'Pair distribution',r,g)
        q=m.panel('Cutoff radius (nm)' if k=='rdf_cutoff' else 'Distance (nm)','Coordination number','Integral of same g(r)')
        for density in densities:m.trace(q,f'ρ = {density} nm⁻³',r,4*np.pi*density*integral(g*r*r,r))
        return m.basis('CN(rc)=4πρ∫₀ʳᶜ g(r)r²dr',parameters={'number_density_nm_minus3':densities,'distance_unit':'nm','first_peak_nm':.285,'first_width_nm':.03},assumptions=['Nonnegative analytic pair function tending toward 1; number density belongs to the selected neighbour species.'],limits=['RDFs are analytic illustration, not MD trajectories. Choose the first-shell cutoff from the actual distribution, not an arbitrary entire box.'])
    if k=='solvation_population':
        c=np.linspace(.2,3,50);weights=np.column_stack([np.exp(-c),1+.2*c,.15*np.exp(c)]);frac=weights/weights.sum(axis=1)[:,None]
        p=m.panel('Model composition coordinate','Population (%)','Declared class partition')
        for i,name in enumerate(('Class I','Class II','Class III')):m.trace(p,name,c,100*frac[:,i])
        q=m.panel('Model composition coordinate','Population sum (%)','Partition check');m.trace(q,'All classes',c,100*frac.sum(axis=1))
        return m.basis('pi=wi/Σwj; mutually exclusive classes with a common denominator',parameters={'w1':'exp(-c)','w2':'1+0.2c','w3':'0.15exp(c)'},limits=['c is a dimensionless design coordinate, not measured concentration. Classes are not called SSIP/CIP/AGG without an actual classification/trajectory.'])
    if k in ('raman_components','ir_absorbance','nmr_lorentzian'):
        if k=='nmr_lorentzian':
            x=np.linspace(-2,2,1001);p=m.panel('Shift relative to centre (ppm)','Intensity (a.u.)','Equal-area Lorentzians',invert_x=True)
            areas=[]
            for width in (.08,.16,.32):
                y=width/(np.pi*(x*x+width*width));m.trace(p,f'HWHM = {width:.2f} ppm',x,y);areas.append(np.trapezoid(y,x))
            q=m.panel('HWHM (ppm)','Integrated area in shown window','Finite-window integral');m.trace(q,'Window integral',[.08,.16,.32],areas)
            return m.basis('L(x)=γ/[π(x²+γ²)]; integral over infinite x is 1',parameters={'HWHM_ppm':[.08,.16,.32],'centre_offset_ppm':0},limits=['Generic line-shape study with no nucleus or chemical-shift assignment. Finite-window area is smaller than the infinite integral; no population is inferred.'])
        x=np.linspace(650,950,601);c1=.6*np.exp(-.5*((x-730)/12)**2);c2=.35*np.exp(-.5*((x-810)/22)**2);bg=.05+.0001*(x-650);a=c1+c2+bg
        p=m.panel('Wavenumber (cm⁻¹)','Absorbance' if k=='ir_absorbance' else 'Intensity (a.u.)','Generic spectral model')
        m.trace(p,'Total',x,a)
        if k=='ir_absorbance':
            q=m.panel('Wavenumber (cm⁻¹)','Transmittance (%)','Same absorbance',invert_x=True);m.trace(q,'10⁻ᴬ',x,100*10**(-a))
            return m.basis('A=−log10(T); T%=100*10^(−A)',parameters={'centres_cm_minus1':[730,810],'sigma_cm_minus1':[12,22],'heights':[.6,.35]},limits=['Illustrative bands are not a vibrational or chemical assignment. Absorbance and arbitrary-intensity Raman signals are not interchangeable.'])
        for label,y in [('Band I',c1),('Band II',c2),('Background',bg)]:m.trace(p,label,x,y)
        q=m.panel('Wavenumber (cm⁻¹)','Residual (a.u.)','Forward sum check');m.trace(q,'Total − components − background',x,a-c1-c2-bg)
        return m.basis('S=Σ Gaussian components + declared baseline; residual=S−model',parameters={'centres_cm_minus1':[730,810],'sigma_cm_minus1':[12,22],'heights':[.6,.35]},limits=['This is a known forward sum with zero residual, not a successful experimental fit or identification of chemical species.'])
    if k=='angle_distribution':
        x=np.linspace(0,180,721);p=m.panel('Angle (°)','Probability density (degree⁻¹)','Normalised illustrative orientations')
        q=m.panel('Angle (°)','Cumulative probability','Same distribution')
        for centre in (65,110):
            y=np.sin(np.deg2rad(x))*np.exp(-.5*((x-centre)/18)**2);y/=np.trapezoid(y,x);m.trace(p,f'Centre {centre}°',x,y);m.trace(q,f'Centre {centre}°',x,integral(y,x))
        return m.basis('p(θ)∝sin(θ)*exp[−(θ−μ)²/(2s²)]; normalised per degree over 0–180°',parameters={'mu_deg':[65,110],'sigma_deg':18},limits=['An original orientation hypothesis, not a measured / simulated electrolyte distribution; angle definition requires actual vector pairs.'])
    if k.startswith('xrd_') or k=='scherrer_width':
        x=np.linspace(20,85,1301);hkl=[(1,1,1),(2,0,0),(2,2,0)];a0=.55;lam=.154
        def pattern(a,width=.24):
            peaks=[2*np.rad2deg(np.arcsin(lam*np.sqrt(sum(i*i for i in h))/(2*a))) for h in hkl]
            y=sum(amp*np.exp(-.5*((x-c)/width)**2) for c,amp in zip(peaks,[1,.62,.42]))
            return y,peaks
        p=m.panel('2θ (°)','Intensity (a.u.)','Ideal cubic lattice')
        if k=='scherrer_width':
            x=np.linspace(25,31,901);theta=np.deg2rad(14);sizes=[8,16,32]
            for d in sizes:
                beta=.9*lam/(d*np.cos(theta));width=np.rad2deg(beta);m.trace(p,f'D = {d} nm',x,1/(1+((x-28)/(width/2))**2))
            q=m.panel('Crystallite size (nm)','FWHM (°)','Size-only broadening');dd=np.linspace(5,50,100);m.trace(q,'K = 0.9',dd,np.rad2deg(.9*lam/(dd*np.cos(theta))))
            return m.basis('D=Kλ/(βcosθ), β=FWHM in radians of 2θ','Lorentzian peak with FWHM β',parameters={'lambda_nm':lam,'K':.9,'two_theta_deg':28,'D_nm':sizes},assumptions=['Size-only broadening; zero strain and no instrument broadening.'],limits=['Crystallite size is not particle size. Author data need instrument broadening / strain assessment; shape factor is not universal.'])
        if k=='xrd_operando':
            coordinate=np.linspace(0,1,51);matrix=[]
            for c in coordinate:
                y,_=pattern(a0*(1+.012*c));matrix.append(y)
                if c in (0,.5,1):m.trace(p,f'Process {c:.1f}',x,y)
            q=m.panel('2θ (°)','Process coordinate','Same patterns',kind='heatmap',vmin=0,vmax=1,cmap='viridis')
            for c,y in zip(coordinate,matrix):m.trace(q,'Intensity',x,y,z=float(c))
        else:
            aa=[a0] if k=='xrd_fcc' else [a0,a0*1.01,a0*1.02]
            for a in aa:y,peaks=pattern(a);m.trace(p,f'a = {a:.4f} nm',x,y)
            q=m.panel('Lattice constant (nm)','(111) peak 2θ (°)','Bragg geometry');a=np.linspace(a0*.98,a0*1.03,100);m.trace(q,'(111)',a,2*np.rad2deg(np.arcsin(lam*np.sqrt(3)/(2*a))))
        return m.basis('d(hkl)=a/sqrt(h²+k²+l²); 2d sinθ=λ','Allowed FCC reflections have all-even or all-odd h,k,l',parameters={'a0_nm':a0,'lambda_nm':lam,'hkl':hkl,'relative_amplitudes':[1,.62,.42],'sigma_2theta_deg':.24},limits=['Hypothetical cubic lattice: a0 is not assigned to Li₂S, Cu or any material. Relative intensities are illustrative, not atomic scattering calculations. Process coordinate is not measured SOC/time.'])
    if k=='xps_doublet':
        x=np.linspace(-3,4,901);w=.45;first=np.exp(-.5*(x/w)**2);second=.5*np.exp(-.5*((x-1.2)/w)**2);bg=.03+.002*(x+3)
        p=m.panel('Binding-energy offset (eV)','Intensity (a.u.)','Generic p doublet',invert_x=True)
        for name,y in [('Total',first+second+bg),('p₃/₂',first),('p₁/₂',second),('Background',bg)]:m.trace(p,name,x,y)
        q=m.panel('Binding-energy offset (eV)','Residual (a.u.)','Known forward model',invert_x=True);m.trace(q,'Residual',x,np.zeros_like(x))
        return m.basis('S=G(E,0,σ)+0.5G(E,Δ,σ)+baseline',parameters={'delta_eV':1.2,'sigma_eV':w,'area_ratio':2},limits=['Generic p-level doublet with equal widths and 2:1 degeneracy, not F 1s (a singlet), not a material binding-energy assignment, and not an experimental fit.'])
    if k=='sputter_components':
        t=np.linspace(0,120,241);a=np.exp(-t/28);b=(1-a)*np.exp(-t/250)
        p=m.panel('Sputter time (s)','Normalised signal (a.u.)','Analytic layered-signal hypothesis')
        m.trace(p,'Fragment I',t,a);m.trace(p,'Fragment II',t,b)
        q=m.panel('Sputter time (s)','Normalised signal (a.u.)','Same records, expanded region')
        for name,y in [('Fragment I',a),('Fragment II',b)]:m.trace(q,name,t[:81],y[:81])
        return m.basis('Signal I=exp(−t/28); II=(1−I)*exp(−t/250)',parameters={'time_unit':'s','decay_s':[28,250]},limits=['Nonnegative phenomenological signals, not concentration fractions. No sputter-rate calibration: time is not depth. Ion yield / matrix effects are excluded.'])
    if k in ('ionic_arrhenius','activation_fit'):
        t=np.linspace(253.15,333.15,65);p=m.panel('Temperature (K)','Conductivity (mS cm⁻¹)','Ideal Arrhenius',yscale='log')
        q=m.panel('1000/T (K⁻¹)','ln[σ/(S cm⁻¹)]','Same conductivities')
        for ea in (18000,24000,30000):
            s=.004*np.exp(-ea/R*(1/t-1/298.15));label=f'Ea = {ea/1000:.0f} kJ mol⁻¹';m.trace(p,label,t,s*1000);m.trace(q,label,1000/t,np.log(s))
        if k=='activation_fit':
            m=Model(task);p=m.panel('1000/T (K⁻¹)','ln[σ/(S cm⁻¹)]','Declared Arrhenius slope')
            q=m.panel('Interval midpoint T (K)','Recovered Ea (kJ mol⁻¹)','Finite-difference slope; same σ')
            for ea in (18000,24000,30000):
                s=.004*np.exp(-ea/R*(1/t-1/298.15));label=f'Input Ea = {ea/1000:.0f} kJ mol⁻¹'
                m.trace(p,label,1000/t,np.log(s));m.trace(q,label,(t[1:]+t[:-1])/2,-R*np.diff(np.log(s))/np.diff(1/t)/1000)
        return m.basis('σ(T)=σref*exp[−Ea/Rg*(1/T−1/Tref)]','Slope of lnσ vs 1000/T = −Ea/(1000 Rg)',parameters={'Ea_J_mol':[18000,24000,30000],'sigma_ref_S_cm':.004,'Tref_K':298.15},limits=['Fixed activation energy, no phase transition and no VTF curvature. The plotted activation energies are known inputs, not fitted experimental results.'])
    if k=='msd_diffusion':
        t=np.linspace(0,10,201);p=m.panel('Time (ns)','MSD (nm²)','Three-dimensional self-diffusion')
        q=m.panel('Time (ns)','MSD / (6t) (nm² ns⁻¹)','Same MSD; t > 0')
        for d in (.01,.025,.05):m.trace(p,f'D = {d:g}',t,6*d*t);m.trace(q,f'D = {d:g}',t[1:],6*d*t[1:]/(6*t[1:]))
        return m.basis('MSD=6Dt for isotropic 3D long-time diffusion','1 nm²/ns = 10⁻⁹ m²/s',parameters={'D_nm2_ns':[.01,.025,.05]},limits=['Analytic long-time limit, not a trajectory with ballistic / caging behaviour. A actual D requires an appropriate fitted window and independent uncertainty.'])
    if k=='nernst_einstein':
        c=np.linspace(100,1800,100);p=m.panel('Salt concentration (mol m⁻³)','Ideal conductivity (mS cm⁻¹)','Uncorrelated 1:1 electrolyte')
        q=m.panel('Salt concentration (mol m⁻³)','σ / concentration (S m² mol⁻¹)','Same conductivity')
        for dplus,dminus in [(1e-10,1.5e-10),(2e-10,2.5e-10)]:
            s=F**2*c*(dplus+dminus)/(R*298.15);name=f'Dsum = {(dplus+dminus)/1e-10:g} ×10⁻¹⁰';m.trace(p,name,c,s*10);m.trace(q,name,c,s/c)
        return m.basis('σNE=F² c (D+ + D−)/(R T), monovalent ideal salt','1 S/m = 10 mS/cm',parameters={'T_K':298.15,'D_pair_m2_s':[[1e-10,1.5e-10],[2e-10,2.5e-10]]},limits=['Uncorrelated ideal limit; concentration-independent D is a teaching assumption. Actual concentrated electrolytes include cross-correlations and cannot be assigned this conductivity from MSD alone.'])
    if k=='polarization_resistance':
        t=np.linspace(0,3600,300);i0=.06;iss=.025;cur=iss+(i0-iss)*np.exp(-t/500)
        p=m.panel('Time (s)','Current (mA)','Declared DC relaxation');m.trace(p,'Polarisation current',t,cur)
        q=m.panel('Interface resistance (Ω)','Steady-state ratio estimate','Only declared ideal conditions')
        ri=np.linspace(5,40,50);value=iss*(.005-i0*.001*ri)/(i0*(.005-iss*.001*25));m.trace(q,'Corrected ratio',ri,value)
        return m.basis('IBV ratio=Iss*(ΔV−I0R0)/(I0*(ΔV−IssRss)); current uses A','I(t)=Iss+(I0−Iss)exp(−t/τ)',parameters={'deltaV_V':.005,'I0_A':i0*.001,'Iss_A':iss*.001,'Rss_ohm':25,'tau_s':500},limits=['The corrected steady-state estimate is not a universally valid concentrated-solution transference number. Requires ideal / immobilised electrolyte assumptions, negligible convection and small DC bias. No interface resistance was fitted.'])
    if k=='conductivity_cellconstant':
        l=np.linspace(.005,.05,100);p=m.panel('Thickness (cm)','Bulk resistance (Ω)','Declared geometry')
        q=m.panel('Thickness (cm)','Recovered conductivity (mS cm⁻¹)','Same bulk resistance')
        for area in (.5,1.):res=l/(.004*area);m.trace(p,f'Area = {area:g} cm²',l,res);m.trace(q,f'Area = {area:g} cm²',l,l/(res*area)*1000)
        return m.basis('σ=L/(Rb*A)',parameters={'sigma_S_cm':.004,'area_cm2':[.5,1]},limits=['Bulk-only uniform geometry; measured contact / interface / lead resistance must be separated. No arbitrary EIS semicircle is treated as bulk resistance.'])
    if k=='ce_ledger':
        cyc=np.arange(1,201);p=m.panel('Cycle number','Charge (mAh)','Per-cycle ledger');q=m.panel('Cycle number','Coulombic efficiency (%)','Same charge pairs')
        for i,name in enumerate(('Protocol A','Protocol B')):
            charge=np.ones_like(cyc,dtype=float);eff=99.7-.2*np.exp(-cyc/15)-i*(.2+.001*cyc);dis=charge*eff/100
            m.trace(p,name+' charge',cyc,charge);m.trace(p,name+' recovered',cyc,dis);m.trace(q,name,cyc,100*dis/charge)
        return m.basis('CE(n)=100*Qrecovered(n)/Qsupplied(n)',parameters={'supplied_mAh':1,'cycles':200,'formula':'99.7-0.2exp(-n/15)-i(0.2+0.001n)'},limits=['A declared per-cycle charge protocol, not Aurbach reservoir CE. Efficiency is not capacity retention; no injected random failures or measured performance.'])
    if k=='capacity_areal':
        loading=np.linspace(1,15,100);p=m.panel('Active loading (mg cm⁻²)','Areal capacity (mAh cm⁻²)','Consistent active-mass basis');q=m.panel('Active loading (mg cm⁻²)','Specific capacity (mAh g⁻¹)','Same normalisation')
        for cap in (120,160,190):m.trace(p,f'{cap} mAh g⁻¹',loading,cap*loading/1000);m.trace(q,f'{cap} mAh g⁻¹',loading,np.full_like(loading,cap))
        return m.basis('QA=Qs*mloading/1000 (loading in mg/cm²)',parameters={'specific_capacity_mAh_g':[120,160,190]},limits=['An accounting conversion assuming utilisation is independent of loading. Not a prediction that thick practical electrodes retain identical capacity. Whole-cell mass is not active-material mass.'])
    if k=='energy_integration':
        capacity=np.linspace(0,160,401);voltage=4.2-.004*capacity-.15*(capacity/160)**6;energy=integral(voltage,capacity)
        p=m.panel('Specific capacity (mAh g⁻¹)','Voltage (V)','Declared discharge branch');m.trace(p,'Voltage',capacity,voltage)
        q=m.panel('Specific capacity (mAh g⁻¹)','Specific energy (Wh kg⁻¹)','Integral of same voltage');m.trace(q,'Cumulative energy',capacity,energy)
        return m.basis('E=∫V dQ; 1 mWh/g=1 Wh/kg',parameters={'Qmax_mAh_g':160,'V_model':'4.2-0.004Q-0.15(Q/160)^6','mass_basis':'1 g of an unnamed active material; excludes inactive parts / counter electrode / packaging'},limits=['Energy is normalised to active-material mass, not cell-level energy density. Teaching voltage function has no electrode/material assignment.'])
    if k=='capacity_repeat':
        n=np.arange(1,301);p=m.panel('Cycle number','Specific capacity (mAh g⁻¹)','Five synthetic cell records')
        traces=[]
        for i,(q0,decay) in enumerate(zip([161,159,162,158,160],[.026,.032,.029,.035,.028])):
            y=q0-decay*(n-1);traces.append(y);m.trace(p,f'Cell {i+1}',n,y)
        q=m.panel('Cycle number','Specific capacity (mAh g⁻¹)','Mean and sample SD (n = 5)');arr=np.array(traces)
        m.trace(q,'Mean',n,arr.mean(axis=0));m.trace(q,'Mean + SD',n,arr.mean(axis=0)+arr.std(axis=0,ddof=1));m.trace(q,'Mean − SD',n,arr.mean(axis=0)-arr.std(axis=0,ddof=1))
        return m.basis('Mean=ΣQi/n; sample SD=sqrt(Σ(Qi−mean)²/(n−1))',parameters={'n_independent_model_cells':5,'q0_mAh_g':[161,159,162,158,160],'slope_per_cycle':[.026,.032,.029,.035,.028]},limits=['Five explicitly declared synthetic cell identities, not a claim of experimental replication. Cycles within a cell are not independent samples.'])
    if k in ('rate_tau','rate_exponent','rate_recovery','thickness_timescale'):
        if k=='thickness_timescale':
            thickness=np.linspace(10,180,200);p=m.panel('Electrode thickness (μm)','Diffusion time (s)','Single transport contribution');q=m.panel('Thickness² (μm²)','Diffusion time (s)','Same relationship')
            for d in (2e-11,5e-11,1e-10):tau=(thickness*1e-6)**2/d;m.trace(p,f'D = {d:.0e} m²/s',thickness,tau);m.trace(q,f'D = {d:.0e} m²/s',thickness**2,tau)
            return m.basis('τ=L²/D',parameters={'D_m2_s':[2e-11,5e-11,1e-10]},limits=['One ideal diffusive timescale, not total electrode time constant; electrical, separator, geometry and kinetic contributions are excluded.'])
        rr=np.geomspace(.05,30,180);p=m.panel('Measured inverse discharge time R (h⁻¹)','Specific capacity (mAh g⁻¹)','Rate model',xscale='log');q=m.panel('Measured R (h⁻¹)','Normalised capacity','Same low-rate basis',xscale='log')
        for tau,n in ([(.03,.7),(.08,.7),(.2,.7)] if k=='rate_tau' else [(.08,.5),(.08,.75),(.08,1.)]):
            y=rate_capacity(rr,tau,n);label=f'τ = {tau:g} h, n = {n:g}';m.trace(p,label,rr,y);m.trace(q,label,rr,y/170)
        if k=='rate_recovery':
            m=Model(task);p=m.panel('Cycle in declared sequence','Specific capacity (mAh g⁻¹)','Reversible rate protocol');q=m.panel('Cycle in declared sequence','Measured R (h⁻¹)','Actual rate sequence',kind='step')
            seq=np.repeat([.2,.5,1,2,5,.2],10);cyc=np.arange(1,len(seq)+1)
            m.trace(p,'Model capacity',cyc,rate_capacity(seq));m.trace(q,'Protocol R',cyc,seq)
        cases=[{'tau_h':tau,'n':n} for tau,n in ([(.03,.7),(.08,.7),(.2,.7)] if k=='rate_tau' else [(.08,.5),(.08,.75),(.08,1.)])]
        if k=='rate_recovery':cases=[{'tau_h':.08,'n':.7}]
        return m.basis('Q=Q0*[1−(Rτ)^n*(1−exp(−(Rτ)^−n))]','R=I/Qmeasured is measured inverse time; not nominal C-rate',parameters={'Q0_mAh_g':170,'cases':cases,'return_protocol_h_minus1':[.2,.5,1,2,5,.2] if k=='rate_recovery' else None},limits=['Semi-empirical forward model, no fit; rate recovery assumes no permanent degradation. Values of τ/n do not uniquely establish a mechanism.'])
    if k=='flow_efficiency':
        cycles=np.arange(1,101);ce=.985-.0001*cycles;vch=1.6+.0005*cycles;vdis=1.35-.0005*cycles;qch=np.ones_like(cycles)*10;qdis=qch*ce
        p=m.panel('Cycle number','Efficiency (%)','Same charge / energy ledger')
        for name,y in [('CE',100*ce),('VE',100*vdis/vch),('EE',100*qdis*vdis/(qch*vch))]:m.trace(p,name,cycles,y)
        q=m.panel('Cycle number','Mean voltage (V)','Capacity-weighted means');m.trace(q,'Charge',cycles,vch);m.trace(q,'Discharge',cycles,vdis)
        return m.basis('CE=Qdis/Qch; VE=(Edis/Qdis)/(Ech/Qch); EE=Edis/Ech=CE*VE',parameters={'Qcharge_mAh':10,'constant_current_branch':True,'charge_voltage':'1.6+0.0005n','discharge_voltage':'1.35-0.0005n'},limits=['Constant branch voltage model; real voltage means are charge-weighted integrals. Not arithmetic means from unmatched time series; no chemistry assignment.'])
    if k=='flow_power':
        j=np.linspace(0,300,501);v=1.5-.12*np.arcsinh(j/(2*25))-.003*j;p=m.panel('Current density (mA cm⁻²)','Voltage (V)','Declared activation + ohmic losses');m.trace(p,'Delivered voltage',j,v)
        q=m.panel('Current density (mA cm⁻²)','Power density (mW cm⁻²)','Same voltage');m.trace(q,'P = jV',j,j*v)
        return m.basis('V=E0−b*asinh(j/(2j0))−j*Rarea/1000; P=jV',parameters={'E0_V':1.5,'b_V':.12,'j0_mA_cm2':25,'Rarea_ohm_cm2':3},limits=['Illustrative symmetric activation + ohmic model; no mass-transport limit or actual flow architecture is claimed.'])
    if k.startswith('pv_'):
        p=m.panel('Voltage (V)','Delivered current (mA cm⁻²)','Ideal single-diode circuit');q=m.panel('Voltage (V)','Delivered power (mW cm⁻²)','Same current record')
        configs=[('Reference',{})]
        if k=='pv_light':configs=[(f'{l:g} sun',dict(light=l)) for l in (.2,.5,1)]
        elif k=='pv_temperature':configs=[(f'{t:.0f} K',dict(temp=t)) for t in (278.15,298.15,318.15)]
        elif k=='pv_series_resistance':configs=[(f'Rs = {rs:g} Ω cm²',dict(rs=rs)) for rs in (0,3,8)]
        elif k=='pv_shunt_resistance':configs=[(f'Rsh = {rs:g} Ω cm²',dict(rsh=rs)) for rs in (100,500,5000)]
        allparams=[]
        for name,kw in configs:
            voc=open_circuit(**kw);v=np.linspace(0,1.012*voc,501)
            j,params=diode(v,**kw);m.trace(p,name,v,j);m.trace(q,name,v,j*v);allparams.append(dict(label=name,Voc_V=voc,display_Vmax=float(v[-1]),**params))
        if k=='pv_fill_factor':
            voc=open_circuit();v=np.linspace(0,1.012*voc,501);j,params=diode(v);valid=(v>=0)&(j>=0);ix=np.flatnonzero(valid)[np.argmax((v*j)[valid])];pmax=v[ix]*j[ix];ff=pmax/(j[0]*voc)
            m.panels[q]['annotation']=f'Voc {voc:.3f} V · FF {ff:.3f}\nPmax {pmax:.2f} mW/cm² · PCE {pmax:.2f}%'
            third=m.panel('Series resistance (Ω cm²)','Fill factor','MPP from each generating quadrant')
            resistances=np.linspace(0,12,49);ffs=[]
            for rs in resistances:
                vv=np.linspace(0,voc,501);jj,_=diode(vv,rs=rs);ffs.append(float(np.max(vv*jj)/(voc*jj[0])))
            m.trace(third,'Ideal-circuit FF',resistances,ffs)
        return m.basis('J=JL−J0[exp((V+JRs)/(n kBT/q))−1]−(V+JRs)/Rsh; J in A/cm²','P=VJ; FF=Pmax/(Voc*Jsc); PCE=Pmax/Pin','J0(T)=J0ref*(T/Tref)^3*exp[−Eg/kB*(1/T−1/Tref)]',parameters={'cases':allparams,'illumination_mW_cm2_at_1sun':100,'Eg_eV':1.1,'FF_resistance_sweep_ohm_cm2':list(resistances) if k=='pv_fill_factor' else None,'MPP_method':'501-point voltage grid from 0 to Voc'},assumptions=['Delivered-positive sign convention; ideal circuit, no scan hysteresis, carrier transport or spectral response. Illustrative diode parameters are not fitted.'],limits=['The reference explicitly warns against Shockley fitting of low-mobility organic photovoltaics. These examples only teach an ideal circuit; they are NOT an organic device transport model, certified efficiency, AM1.5 spectral simulation or material-specific prediction.'])
    raise ValueError('Undefined task: '+k)

def scientific_basis(m):
    ref=reference(m.ref)
    ref['support_level']='equation and conditions' if m.ref in {'diffusion_equations','rate','eis'} else 'measurement caveat' if m.ref in {'correlations','polarisation','reporting'} else 'plot form / caption'
    ref['formula_scope']='The listed equations are declared teaching assumptions. A plot-form reference does not independently verify every analytic line shape, parameter or inference.'
    return dict(schema_version=1,model_class='analytic_model' if m.ident not in {'capacity_repeat','solvation_population','sputter_components'} else 'phenomenological_model',
        data_origin='original_synthetic',equations=m.equations,assumptions=m.assumptions,parameters=m.params,
        references=[ref],limitations=m.limits,validation_scope='Analytic consistency / dimensional accounting / original synthetic redraw only. Not validation of an actual material or author-supplied measurement.')
