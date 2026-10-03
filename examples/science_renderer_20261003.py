"""Redraw existing science CSV inputs only; never import their generator.

The source/CSV components use demo_bundle_runner.py and its fresh-output,
hash-inventory and author-input provenance controls. This renderer validates
numeric input, axis units, cycle marker/continuous solid artists, all four spines and actual
text/legend bounds. It does not validate a physical mechanism.
"""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

ROOT=Path(__file__).resolve().parent/'showcase'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from series_policy import apply_series_policy, check_series_policy
COLOURS=['#287D8E','#BA5574','#4868A8','#A46D35','#655AA0','#387F64']

def apply_figure_style():
    """Boxed axes; discrete cycle quantities use the user's marker-only choice."""
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
        'axes.labelsize':10,'axes.titlesize':10,'xtick.labelsize':9,
        'ytick.labelsize':9,'legend.fontsize':9,'axes.linewidth':.8,
        'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white',
        'axes.spines.top':True,'axes.spines.right':True,'axes.spines.left':True,
        'axes.spines.bottom':True,'lines.linestyle':'-','lines.marker':'None'})

def render(name):
    folder=ROOT/name
    config=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    rows=[]
    with (folder/'data.csv').open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream)
        if not {'panel','series','x','y'}<=set(reader.fieldnames or []):raise ValueError('Expected panel,series,x,y CSV and its unit contract')
        for raw in reader:
            row=dict(panel=int(raw['panel']),series=raw['series'],x=float(raw['x']),y=float(raw['y']))
            if not np.isfinite(row['x']) or not np.isfinite(row['y']):raise ValueError('Nonfinite input: ask author; no interpolation')
            if raw.get('z','').strip():row['z']=float(raw['z'])
            rows.append(row)
    count=len(config['panels'])
    if not rows or not 1<=count<=6:raise ValueError('Missing rows or invalid panel contract')
    apply_figure_style()
    columns=min(2,count)
    fig,grid=plt.subplots((count+columns-1)//columns,columns,figsize=(6.8*columns,4.9*((count+columns-1)//columns)),squeeze=False,layout='constrained')
    axes=list(grid.flat);frames=[];curves=[]
    for i,p in enumerate(config['panels']):
        ax=axes[i];sel=[r for r in rows if r['panel']==i]
        if not sel:raise ValueError('Empty declared panel')
        ax.set(xlabel=p['xlabel'],ylabel=p['ylabel'])
        title=ax.set_title(p.get('title',''),loc='left',pad=55)
        groups=list(dict.fromkeys(r['series'] for r in sel))
        if p.get('kind')=='heatmap':
            xs=sorted({r['x'] for r in sel});zs=sorted({r['z'] for r in sel});values={(r['x'],r['z']):r['y'] for r in sel}
            if len(values)!=len(xs)*len(zs):raise ValueError('Heatmap must be rectangular and nonduplicate')
            image=np.array([[values[x,z] for x in xs] for z in zs])
            mesh=ax.pcolormesh(xs,zs,image,shading='nearest',cmap='viridis',vmin=p.get('vmin'),vmax=p.get('vmax'),rasterized=True)
            fig.colorbar(mesh,ax=ax,pad=.02).set_label(p.get('value_label','Signal (a.u.)'))
        else:
            for n,label in enumerate(groups):
                g=[r for r in sel if r['series']==label]
                ax.plot([r['x'] for r in g],[r['y'] for r in g],color=COLOURS[n%len(COLOURS)],lw=1.8,ls='-',marker=None,label=label)
            leg=ax.legend(loc='lower left',bbox_to_anchor=(0,1.015),ncol=1 if any(len(g)>29 for g in groups) else min(2,len(groups)),frameon=False,borderaxespad=0)
        ax.set_xscale(p.get('xscale','linear'));ax.set_yscale(p.get('yscale','linear'))
        if p.get('invert_x'):ax.invert_xaxis()
        if p.get('equal'):ax.set_aspect('equal',adjustable='box')
        if 'xlim' in p:ax.set_xlim(*p['xlim'])
        if 'ylim' in p:ax.set_ylim(*p['ylim'])
        for s in ax.spines.values():s.set_visible(True)
        ax.tick_params(direction='out',length=3.5)
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
        leg=ax.get_legend()
        if leg:title.set_position((0,1));ax.set_title(title.get_text(),loc='left',pad=leg.get_window_extent(renderer).height*72/fig.dpi+19)
        apply_series_policy(ax)
        actual=[]
        for line in ax.lines:
            rec=dict(panel_index=i,label=line.get_label(),points=len(line.get_xdata()),line_style=line.get_linestyle(),marker=line.get_marker(),colour=to_hex(line.get_color()))
            rec['sampling']=check_series_policy(ax,line)
            curves.append(rec);actual.append(dict(label=rec['label'],linestyle=rec['line_style'],marker=rec['marker'],points=rec['points'],sampling=rec['sampling']))
        frames.append(dict(panel_index=i,spines={s:ax.spines[s].get_visible() for s in ('left','right','top','bottom')},continuous_curves=actual,xlabel=ax.get_xlabel(),ylabel=ax.get_ylabel()))
    for a in axes[count:]:a.set_visible(False)
    fig.canvas.draw();renderer=fig.canvas.get_renderer();outside=[];overlap=[]
    for i,ax in enumerate(axes[:count]):
        bbox=ax.get_tightbbox(renderer)
        if bbox.x0<-.5 or bbox.y0<-.5 or bbox.x1>fig.bbox.x1+.5 or bbox.y1>fig.bbox.y1+.5:outside.append(i)
        leg=ax.get_legend()
        if leg and ax._left_title.get_window_extent(renderer).overlaps(leg.get_window_extent(renderer)):overlap.append(i)
    if outside or overlap:raise ValueError('Actual rendered text gate failed: '+str((outside,overlap)))
    for ext in ('png','svg','pdf'):fig.savefig(folder/('figure.'+ext),dpi=220,metadata={'Creator':'VoltPeer'} if ext=='pdf' else None)
    meta=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    meta.update(actual_artist_checks=frames,data_frame_checks=frames,continuous_curve_style_checks=curves,
        curve_style_check='Discrete cycle quantities marker-only; continuous functions solid/unmarked; user display preference.',
        data_frame_check='Actual data axes: all four spines visible.')
    if isinstance(meta.get('review'),dict):
        meta['review']['display']='Actual cycle-marker/continuous-solid artists, four-frame spines, legend/title and text bounds checked.'
    (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=dict(renderer='science_renderer_20261003.py',operation='render_existing_inputs_only',
        data_sha256=hashlib.sha256((folder/'data.csv').read_bytes()).hexdigest(),axis_count=count,curve_count=len(curves),
        text_bbox_outside=outside,title_legend_overlap=overlap,frame_count=len(frames),
        scientific_scope='Numerical, artist and input provenance QA; not acquired scientific validation.')
    (folder/'render-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    plt.close(fig);return report
