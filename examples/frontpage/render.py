"""Homepage plates from existing synthetic CSVs; no experimental results.

python render.py --data-root ../showcase --output-dir ../../docs/assets/frontpage
Uses numpy, pandas, matplotlib and PyMuPDF (font QA). No random generation.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, colors
import fitz
from series_policy import apply_series_policy, check_series_policy

P = argparse.ArgumentParser()
P.add_argument('--data-root', type=Path, default=Path(__file__).resolve().parent / 'data')
P.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent / 'output')
args = P.parse_args()
DATA, OUT = args.data_root.resolve(), args.output_dir.resolve()
FONT = font_manager.findfont('Arial', fallback_to_default=False)
INK, A, B = '#20282e', '#167d8d', '#cb5267'
SHADES = ['#99c9d2', '#459cae', '#24658a', '#302b68']
plt.rcParams.update({'font.family':'Arial','font.size':6.5,'axes.labelsize':6.5,
    'xtick.labelsize':6,'ytick.labelsize':6,'legend.fontsize':5.7,
    'axes.linewidth':.55,'lines.linewidth':.85,'svg.fonttype':'none','pdf.fonttype':42,
    'mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic',
    'mathtext.bf':'Arial:bold','text.color':INK,'axes.labelcolor':INK,
    'axes.edgecolor':INK,'xtick.color':INK,'ytick.color':INK})
USED = set()
def data(group, name='data.csv'):
    p = DATA / group / name
    USED.add(p)
    return pd.read_csv(p)

def canvas(height):
    f = plt.figure(figsize=(183/25.4,height/25.4),facecolor='white')
    f.brf_height = height
    f.brf_axes = []
    return f

def ax(f, box, letter=None, shared=None):
    x,y,w,h = box # millimetres from top left; drawing frames, not file borders
    a = f.add_axes([x/183,1-(y+h)/f.brf_height,w/183,h/f.brf_height],sharey=shared)
    a.spines[['top','right','bottom','left']].set_visible(True)
    a.tick_params(direction='out',length=2.2,width=.55,pad=2)
    a.grid(False)
    if letter: f.text((x-7)/183,1-(y-2)/f.brf_height,letter,fontsize=8,weight='bold',va='bottom')
    f.brf_axes.append({'panel':letter,'plot_box_mm':box,'axis':a})
    return a

def note(a,text,where=(.04,.94)):
    a.text(*where,text,transform=a.transAxes,va='top',fontsize=6.1)

def legend(a,**kw):
    a.legend(frameon=False,handlelength=1.8,borderpad=.1,labelspacing=.35,**kw)

def full(a, b):
    d = data('full_cell')
    for key,c in [('A',A),('B',B)]:
        a.plot(d.cycle,d[f'{key}_mAh_g'],color=c,ls='-',marker=None,label=f'Electrolyte {key}')
    a.set(xlabel='Cycle number',ylabel='Discharge capacity (mAh g$^{-1}$)',xlim=(0,510),ylim=(145,190))
    note(a,'NMC811 || Li · half cell')
    legend(a,loc='lower left')
    d = data('full_cell','voltage_profiles.csv')
    for (cycle,g),c in zip(d.groupby('cycle',sort=True),SHADES):
        b.plot(g.capacity_mAh_g,g.voltage_V,color=c,label=str(cycle))
    b.set(xlabel='Specific capacity (mAh g$^{-1}$)',ylabel='Voltage (V)',xlim=(0,190),ylim=(2.75,4.4))
    legend(b,title='Electrolyte A · cycle',title_fontsize=6,loc='lower left',ncol=2)
    # The selected discharge curve must end at its original cycling capacity.
    for cycle,g in d.groupby('cycle'):
        q=float(data('full_cell').set_index('cycle').loc[cycle,'A_mAh_g'])
        assert abs(g.capacity_mAh_g.max()-q)<1e-4

def rate(a,b):
    d = data('rate_capability')
    for key,c in [('A',A),('B',B)]:
        g=d[d['sample']==key]
        a.plot(g.cycle,g.capacity_mAh_g,color=c,ls='-',marker=None,label=key)
    for start,label in zip(range(0,60,10),['0.2','0.5','1','2','5','0.2']):
        a.text(start+5.5,184,label,ha='center',fontsize=5.7)
    note(a,'C rate',(.02,.985))
    a.set(xlabel='Cycle number',ylabel='Discharge capacity (mAh g$^{-1}$)',xlim=(0,61),ylim=(105,196))
    legend(a,loc='lower left',ncol=2)
    d=data('rate_capability','voltage_profiles.csv')
    for cycle,c in zip([7,27,47,57],SHADES):
        g=d[d.cycle==cycle]
        b.plot(g.capacity_mAh_g,g.voltage_V,color=c,label=f'{g.rate_C.iloc[0]:g} C · {cycle}')
        q=float(data('rate_capability').query('sample == "A" and cycle == @cycle').capacity_mAh_g.iloc[0])
        assert abs(g.capacity_mAh_g.max()-q)<1e-4
    b.set(xlabel='Specific capacity (mAh g$^{-1}$)',ylabel='Voltage (V)',xlim=(0,185),ylim=(2.75,4.4))
    legend(b,title='Electrolyte A · C rate / cycle',title_fontsize=5.7,loc='lower left')

def ce(a,b):
    d=data('li_cu_ce')
    for key,c in [('A',A),('B',B)]:
        a.plot(d.cycle,d[f'{key}_ce_pct'],color=c,ls='-',lw=.8,label=f'Electrolyte {key}')
    a.set(xlabel='Cycle number',ylabel='Coulombic efficiency (%)',xlim=(0,305),ylim=(97.0,100.0))
    assert d[['A_ce_pct','B_ce_pct']].min().min()>=97
    assert d[['A_ce_pct','B_ce_pct']].max().max()<=100
    note(a,'Li || Cu')
    legend(a,loc='lower right',ncol=2)
    d=data('li_cu_ce','profiles.csv')
    for key,c in [('A',A),('B',B)]:
        for cycle in (1,300):
            g=d[(d['sample']==key)&(d.cycle==cycle)&(d.stage=='strip')]
            b.plot(g.capacity_mAh_cm2,g.voltage_V,color=c if cycle==300 else {'A':'#7396b5','B':'#885369'}[key],ls='-',label=f'{key} · {cycle}')
            assert abs(float(g.voltage_V.iloc[-1])-1.0)<1e-8
    b.set(xlabel='Stripped capacity (mAh cm$^{-2}$)',ylabel='Voltage (V)',xlim=(0,1.02),ylim=(0,1.05))
    legend(b,loc='upper left',ncol=2,fontsize=5.3)

def symmetric(a,b):
    d=data('li_li')
    for key,c in [('A',A),('B',B)]:
        g=d[d['sample']==key]
        # Offset-free traces; all original points are retained.
        a.plot(g.time_h,g.voltage_mV,color=c,lw=.35,label=key)
        g=g[g.time_h.between(101,105)]
        b.plot(g.time_h,g.voltage_mV,color=c,lw=.75)
    a.axvspan(101,105,facecolor='#dddce9',alpha=.7,zorder=-2)
    a.set(xlabel='Time (h)',ylabel='Cell voltage (mV)',xlim=(0,200),ylim=(-80,80))
    b.set(xlabel='Time (h)',ylabel='Cell voltage (mV)',xlim=(101,105),ylim=(-80,80))
    note(a,'Li || Li',(.04,.98))
    note(b,'101–105 h',(.04,.98))

def eis(a,b):
    d=data('eis')
    for key,c in [('A',A),('B',B)]:
        g=d[d['sample']==key]
        a.plot(g.Zreal_ohm,-g.Zimag_ohm,color=c,ls='-',lw=.85,label=f'Model {key}')
        z=np.hypot(g.Zreal_ohm,g.Zimag_ohm)
        b.loglog(g.frequency_Hz,z,color=c,ls='-',label=f'Model {key}')
    # x/y use identical physical scale without changing the declared frame.
    width,height=a.get_position().width*183,a.get_position().height*a.figure.brf_height
    a.set(xlabel='Z′ (Ω)',ylabel='−Z″ (Ω)',xlim=(0,70),ylim=(0,70*height/width))
    b.set(xlabel='Frequency (Hz)',ylabel='|Z| (Ω)',xlim=(.01,1e5))
    b.set_xticks([.01,1,100,10000])
    b.set_yticks([5,10,20,40],labels=['5','10','20','40'])
    b.minorticks_off()
    legend(a,loc='upper right',ncol=2)
    legend(b,loc='upper right',ncol=2)

def structure():
    f=canvas(132)
    a=ax(f,[15,12,86,48],'a'); b=ax(f,[136,12,35,48],'b',a)
    d=data('operando_xrd')
    grid=d.pivot(index='soc_fraction',columns='two_theta_deg',values='intensity_au')
    state=data('operando_xrd','state.csv').set_index('soc_fraction')
    times=state.loc[grid.index,'time_s'].to_numpy()/3600
    if not np.allclose(state.index,grid.index):raise ValueError('Homepage XRD lattice/time index differs')
    im=a.pcolormesh(grid.columns,times,grid.values,cmap='viridis',shading='nearest',rasterized=True,
                    vmin=float(grid.values.min()),vmax=float(grid.values.max()))
    a.set(xlabel='2θ (°) · λ = 1.5406 Å',ylabel='Time (h)',ylim=(0,1),xlim=(grid.columns.min(),grid.columns.max()))
    a.text(.02,.98,'Synthetic cubic host',transform=a.transAxes,va='top',fontsize=6.1,
           bbox={'facecolor':'white','edgecolor':'none','alpha':.88,'pad':1.4})
    cb=f.add_axes([105/183,1-60/132,2/183,48/132]); bar=f.colorbar(im,cax=cb)
    bar.set_label('Intensity (a.u.)',size=6); bar.ax.tick_params(labelsize=5.5,length=2,width=.5)
    v=data('operando_xrd','voltage.csv')
    if not np.allclose(v.soc_fraction,grid.index):raise ValueError('Homepage voltage/XRD time index differs')
    b.plot(v.voltage_V,times,color=B,lw=1,ls='-',marker=None)
    b.set(xlabel='Voltage (V)',ylabel='Time (h)',xlim=(3.1,4.3)); b.set_xticks([3.2,3.6,4,4.2])
    note(b,'Charge\n180 mA g$^{-1}$',(.05,.2))
    c=ax(f,[15,85,43,34],'c'); r=ax(f,[72,85,43,34],'d'); x=ax(f,[130,85,43,34],'e')
    selected=np.linspace(0,len(grid)-1,5).astype(int)
    for i,(idx,col) in enumerate(zip(selected,plt.get_cmap('magma')(np.linspace(.2,.8,5)))):
        c.plot(grid.columns,grid.iloc[idx]+i*.72,color=col,lw=.7)
        c.text(46.5,i*.72+.16,f'{times[idx]:.2f} h',ha='right',fontsize=5.2)
    c.set(xlabel='2θ (°)',ylabel='Intensity + offset (a.u.)',xlim=(35.3,46.7),ylim=(0,4.2))
    c.text(.03,.98,'Same times\n+0.72 a.u. per trace',transform=c.transAxes,va='top',fontsize=5.7,
           bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1})
    c.set_yticks([0,2,4])
    d=data('raman_series')
    for i,((key,g),col) in enumerate(zip(d.groupby('sample'),[A,'#49668f','#886099',B])):
        offset=i*340
        r.plot(g.wavenumber_cm_1,g.intensity_counts+offset,color=col,lw=.8)
        r.text(g.wavenumber_cm_1.max(),offset+100,key,ha='right',fontsize=5.7)
    r.set(xlabel='Raman shift (cm$^{-1}$)',ylabel='Counts + offset',xlim=(d.wavenumber_cm_1.min(),d.wavenumber_cm_1.max()))
    d=data('xps_components'); energy=d.binding_energy_eV
    model=d.background_counts+d[['component_1','component_2','component_3']].sum(axis=1)
    for i,col in enumerate([A,'#8f78b3','#e7a154'],1):
        x.fill_between(energy,d.background_counts,d.background_counts+d[f'component_{i}'],color=col,alpha=.48,linewidth=0)
    x.plot(energy,d.intensity_counts,color='#6d7881',lw=.4,alpha=.75,label='Input')
    x.plot(energy,model,color=INK,lw=.85,label='Model')
    x.plot(energy,d.background_counts,color='#8a9296',ls='-',lw=.6)
    x.set(xlabel='Binding energy (eV)',ylabel='Intensity (counts)',xlim=(energy.max(),energy.min()))
    legend(x,loc='upper right',fontsize=5)
    return f, {'a':'operando_xrd/data.csv + state.csv (same-time cubic peaks)','b':'operando_xrd/voltage.csv + state.csv (identical time/charge index)','c':'operando_xrd/data.csv (five recorded timestamps; +0.72 a.u. labelled display offset)',
               'd':'raman_series/data.csv (+340 counts per series)','e':'xps_components/data.csv (analytic components, not an experimental fit)'}, [[0,1],[2,3,4]]

def cycling():
    f=canvas(123)
    axes=[ax(f,b,l) for b,l in zip([[15,11,70,43],[108,11,63,43],[15,76,70,34],[108,76,63,34]],'abcd')]
    full(*axes[:2]); rate(*axes[2:])
    return f,dict(zip('abcd',['full_cell/data.csv','full_cell/voltage_profiles.csv','rate_capability/data.csv','rate_capability/voltage_profiles.csv'])),[[0,1],[2,3]]

def assembly():
    f=canvas(141)
    boxes=[[15,11,102,29],[135,11,38,29],
           [15,58,43,29],[73,58,43,29],[131,58,43,29],
           [15,105,43,25],[73,105,43,25],[131,105,43,25]]
    axes=[ax(f,b,l) for b,l in zip(boxes,'abcdefgh')]
    ce(*axes[:2]); symmetric(*axes[2:4]); full(*axes[5:7]); eis(axes[4],axes[7])
    for a in axes: a.xaxis.label.set_size(5.7); a.yaxis.label.set_size(5.7); a.tick_params(labelsize=5.4)
    return f,dict(zip('abcdefgh',['li_cu_ce/data.csv','li_cu_ce/profiles.csv','li_li/data.csv','li_li/data.csv (101–105 h exact subset)',
                                'eis/data.csv','full_cell/data.csv','full_cell/voltage_profiles.csv','eis/data.csv (absolute complex impedance)'])),[[0,1],[2,3,4],[5,6,7]]

def export(name,builder):
    USED.clear(); f,panels,rows=builder()
    target=OUT/name; target.mkdir(parents=True,exist_ok=True)
    f.canvas.draw()
    report=[]
    for record in f.brf_axes:
        axis=record['axis']
        apply_series_policy(axis)
        r=axis.get_position()
        actual=[r.x0*183,(1-r.y1)*f.brf_height,r.width*183,r.height*f.brf_height]
        assert np.max(np.abs(np.array(actual)-record['plot_box_mm']))<.01
        frame={side:axis.spines[side].get_visible() for side in ('top','right','bottom','left')}
        if not all(frame.values()):
            raise ValueError(f"{name} panel {record['panel']}: data axes must show all four frame spines")
        traces=[]
        for line in axis.lines:
            sampling=check_series_policy(axis,line)
            traces.append({'label':line.get_label(),'line_style':line.get_linestyle(),
                           'marker':line.get_marker(),'points':len(line.get_xdata()),
                           'colour':colors.to_hex(line.get_color()),'sampling':sampling})
        report.append({'panel':record['panel'],'actual_plot_box_mm':actual,
                       'curve_style':'cycle_scatter_or_continuous_solid','frame_spines':frame,'traces':traces})
    for row in rows:
        top=[report[i]['actual_plot_box_mm'][1] for i in row]
        bottom=[sum(report[i]['actual_plot_box_mm'][j] for j in [1,3]) for i in row]
        assert max(top)-min(top)<.01 and max(bottom)-min(bottom)<.01
    for suffix in ['svg','pdf','png']: f.savefig(target/f'figure.{suffix}',dpi=400,facecolor='white')
    fonts=[]
    with fitz.open(target/'figure.pdf') as pdf:
        for page in pdf:
            fonts += [list(font) for font in page.get_fonts(full=True)]
    assert any('Arial' in str(font) for font in fonts)
    assert not any('DejaVu' in str(font) for font in fonts)
    sources=[{'path':p.relative_to(DATA).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(USED)]
    models={}
    for source in sorted(USED):
        meta_path=source.parent/'metadata.json'
        if meta_path.exists():
            meta=json.loads(meta_path.read_text(encoding='utf-8'))
            models[source.parent.name]={'metadata_sha256':hashlib.sha256(meta_path.read_bytes()).hexdigest(),
                                        'scientific_basis':meta['scientific_basis']}
    metadata={'status':'synthetic_demo','not_experimental_data':True,'panel_sources':panels,'sources':sources,
        'source_model_records':models,
        'scope':'Independent synthetic measurement families; layout does not establish one real study or a mechanism.',
        'font_requested':'Arial','font_resolved':Path(FONT).name,'pdf_fonts':fonts,'width_mm':183,'height_mm':f.brf_height,
        'raster_note':'Only the diffraction intensity matrix is rasterized; axes, labels and traces remain vectors.',
        'alignment_tolerance_mm':.01,'alignment':report,'rows_checked':rows,
        'curve_style_check':'Cycle capacity/CE: marker-only. Continuous voltage/spectra: solid, unmarked. User display preference.',
        'data_frame_check':'pass: actual data axes show top/right/bottom/left spines',
        'display_changes':'No smoothing, downsampling or input rewriting. Explicit offsets only in the labelled stacked spectra. Every input row is rendered for the XPS trace and model.',
        'known_model_limitations':[
            'Source metadata defines original teaching models, not acquired measurements. Discharge curves include their declared lower endpoint; Li||Cu stripping includes 1 V. These endpoint identities do not establish a material model.',
            'Independent measurement families are shown together only to demonstrate layout; no common experimental cell or mechanism is implied.',
            'No real phase or XPS chemical assignment is made. A/B identities are synthetic and cannot establish performance or a mechanism.'],
        'reference':'https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/'}
    (target/'metadata.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')
    plt.close(f)
    return USED.copy()

all_sources=set()
for name, builder in [('structure',structure),('cycling',cycling),('assembly',assembly)]:
    all_sources |= export(name,builder)
with zipfile.ZipFile(OUT/'homepage-figures.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write(Path(__file__),'render.py')
    z.write(Path(__file__).parent/'series_policy.py','series_policy.py')
    z.writestr('requirements.txt','numpy\npandas\nmatplotlib\nPyMuPDF\n')
    z.writestr('README.txt','SYNTHETIC DEMONSTRATION / 虚构演示，非实验结果\n'
        'Run: python render.py --data-root data --output-dir output\n'
        'Requires Arial installed; missing fonts raise an error rather than silently changing type.\n'
        'All CSVs are unchanged copies of the existing BRF synthetic examples. Never use them as experimental evidence.\n'
        'Panel sources, display offsets, font checks and millimetre frames are recorded in each metadata.json.\n'
        'The original source metadata beside each CSV defines its simulated conditions.\n'
        '结构与光谱包含三个独立演示；日常电化学包含循环和倍率两组；组合图是虚构 A/B 对照。\n')
    for p in sorted(all_sources): z.write(p,'data/'+p.relative_to(DATA).as_posix())
    for group in sorted({p.parent for p in all_sources}):
        if (group/'metadata.json').exists(): z.write(group/'metadata.json','data/'+group.name+'/metadata.json')
    for p in sorted(OUT.glob('*/*')):
        if p.is_file(): z.write(p,'output/'+p.relative_to(OUT).as_posix())
print('Three plates exported with source hashes, matched-data checks, embedded-font and drawing-frame checks.')
