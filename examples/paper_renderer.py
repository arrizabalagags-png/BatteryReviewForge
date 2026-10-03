"""Input-only plotting entry for the paper-informed teaching collection.

The default entry never synthesises data. Panel/series/x/y[/z] rows and the
axis contract are read from the selected directory. Scientific model selection
belongs to the assistant and author; this renderer cannot validate a mechanism.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

ROOT = Path(__file__).resolve().parent / 'showcase'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from series_policy import apply_series_policy, check_series_policy
COLOURS = ['#287D8E', '#BA5574', '#4868A8', '#A46D35', '#655AA0', '#387F64']


def read_inputs(folder):
    config=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    panels=config['panels']
    if not 1<=len(panels)<=6: raise ValueError('Expected one to six declared panels')
    rows=[]
    with (folder/'data.csv').open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream)
        if not {'panel','series','x','y'}<=set(reader.fieldnames or []):
            raise ValueError('CSV needs panel, series, x, y columns; read the input contract first')
        for raw in reader:
            p=int(raw['panel'])
            if not 0<=p<len(panels): raise ValueError('CSV panel outside axis contract')
            row=dict(panel=p,series=raw['series'],x=float(raw['x']),y=float(raw['y']))
            if raw.get('z','').strip(): row['z']=float(raw['z'])
            if not all(np.isfinite(v) for key,v in row.items() if key not in ('series','panel')):
                raise ValueError('Non-finite CSV value: ask the author, never interpolate silently')
            rows.append(row)
    if not rows or any(not any(r['panel']==p for r in rows) for p in range(len(panels))):
        raise ValueError('Every declared panel needs actual CSV rows')
    return config,rows


def render(name):
    folder=ROOT/name
    config,rows=read_inputs(folder)
    colours=config.get('colours',COLOURS)
    if len(colours)<2 or len(set(colours))!=len(colours): raise ValueError('Distinct colours required')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':10,
        'axes.titlesize':10,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':8.3,
        'axes.linewidth':.9,'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
    count=len(config['panels']);columns=min(2,count);height=4.25*((count+columns-1)//columns)
    fig,grid=plt.subplots((count+columns-1)//columns,columns,figsize=(5.4*columns,height),squeeze=False,layout='constrained')
    axes=list(grid.flat);checks=[];curves=[];titles=[]
    for index,panel in enumerate(config['panels']):
        ax=axes[index];selected=[r for r in rows if r['panel']==index]
        ax.set_xlabel(panel['xlabel']);ax.set_ylabel(panel['ylabel'])
        titles.append(ax.set_title(chr(97+index)+'   '+panel.get('title',''),loc='left',fontweight='bold',pad=35))
        if panel.get('kind')=='heatmap':
            xs=sorted({r['x'] for r in selected});zs=sorted({r['z'] for r in selected})
            values={(r['z'],r['x']):r['y'] for r in selected}
            if len(values)!=len(xs)*len(zs): raise ValueError('Heatmap needs a complete, nonduplicate rectangular grid')
            image=np.array([[values[z,x] for x in xs] for z in zs])
            mesh=ax.pcolormesh(xs,zs,image,shading='nearest',cmap=panel.get('cmap','viridis'),
                vmin=panel.get('vmin'),vmax=panel.get('vmax'),rasterized=True)
            cb=fig.colorbar(mesh,ax=ax,pad=.03);cb.set_label(panel.get('value_label','Intensity (a.u.)'))
        else:
            groups=list(dict.fromkeys(r['series'] for r in selected))
            for n,label in enumerate(groups):
                group=[r for r in selected if r['series']==label]
                x=[r['x'] for r in group];y=[r['y'] for r in group]
                # Point order is the CSV order; neither sorting nor smoothing is
                # introduced behind the author's back.
                kwargs=dict(color=colours[n%len(colours)],lw=1.8,linestyle='-',marker=None,label=label)
                if panel.get('kind')=='step':ax.step(x,y,where='post',**kwargs)
                else:ax.plot(x,y,**kwargs)
            if groups:ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),ncol=min(2,len(groups)),frameon=False,borderaxespad=0)
        for spine in ax.spines.values():spine.set_visible(True);spine.set_color('#45535D')
        ax.tick_params(direction='out',length=3.5,color='#45535D')
        ax.set_xscale(panel.get('xscale','linear'));ax.set_yscale(panel.get('yscale','linear'))
        if panel.get('equal'):ax.set_aspect('equal',adjustable='box')
        if panel.get('invert_x'):ax.invert_xaxis()
        if 'xlim' in panel:ax.set_xlim(*panel['xlim'])
        if 'ylim' in panel:ax.set_ylim(*panel['ylim'])
        if panel.get('annotation') and not panel.get('equal'):ax.text(.03,.05,panel['annotation'],transform=ax.transAxes,fontsize=8,
            va='bottom',ha='left',bbox={'facecolor':'white','edgecolor':'none','alpha':.9})
        apply_series_policy(ax)
        actual=[]
        for line in ax.lines:
            record=dict(panel_index=index,label=line.get_label(),points=len(line.get_xdata()),
                line_style=line.get_linestyle(),marker=line.get_marker(),colour=to_hex(line.get_color()))
            record['sampling'] = check_series_policy(ax, line)
            curves.append(record)
            actual.append(dict(label=record['label'],linestyle=record['line_style'],marker=record['marker'],points=record['points'],sampling=record['sampling']))
        checks.append(dict(panel_index=index,spines={k:ax.spines[k].get_visible() for k in ('left','right','top','bottom')},continuous_curves=actual,xlabel=ax.get_xlabel(),ylabel=ax.get_ylabel()))
    for ax in axes[count:]:ax.set_visible(False)
    fig.canvas.draw();renderer=fig.canvas.get_renderer();outside=[]
    for index,ax in enumerate(axes[:count]):
        legend=ax.get_legend()
        if legend:
            # Use the actual rendered legend height: five labels use three rows.
            pad=legend.get_window_extent(renderer).height*72/fig.dpi+16
            ax.set_title(titles[index].get_text(),loc='left',fontweight='bold',pad=max(35,pad))
        if config['panels'][index].get('equal') and ax.get_window_extent(renderer).width<90:
            # A physical equal-scale full-domain plot can be a narrow strip.
            # One labelled high-frequency intercept avoids overlapping numbers;
            # the declared RC-region view provides the readable horizontal scale.
            ax.set_xticks([float(ax.lines[0].get_xdata()[-1])])
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    # Rendered text bounds include axes labels and legends, not guessed padding.
    for index,ax in enumerate(axes[:count]):
        # get_tightbbox excludes cached logarithmic ticks lying outside the
        # displayed range; findobj(Text) includes those undrawn tick artists.
        bbox=ax.get_tightbbox(renderer)
        if bbox.x0<-.5 or bbox.y0<-.5 or bbox.x1>fig.bbox.x1+.5 or bbox.y1>fig.bbox.y1+.5:outside.append('panel '+str(index))
        legend=ax.get_legend()
        if legend and titles[index].get_window_extent(renderer).overlaps(legend.get_window_extent(renderer)):
            raise ValueError('Panel title overlaps its legend: '+str(index))
    if outside:plt.close(fig);raise ValueError('Clipped figure text: '+str(outside))
    for ext in ('png','svg','pdf'):fig.savefig(folder/('figure.'+ext),dpi=180,metadata={'Creator':'VoltPeer'} if ext=='pdf' else None)
    meta=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    meta.update(actual_artist_checks=checks,data_frame_checks=checks,continuous_curve_style_checks=curves,
        curve_style_check='Cycle capacity/CE/charge ledger: marker-only; continuous profiles: solid/unmarked; user display preference.',
        data_frame_check='All four spines visible on every data axis.')
    (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=dict(renderer='paper_renderer.py',operation='render_existing_inputs_only',data_sha256=hashlib.sha256((folder/'data.csv').read_bytes()).hexdigest(),
        axis_count=count,text_bbox_outside=outside,curve_count=len(curves),synthetic_scope='Original analytic teaching record; not author-data or scientific-mechanism certification')
    (folder/'render-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    plt.close(fig)
    return report
