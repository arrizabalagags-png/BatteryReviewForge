"""Original battery showcase plates: cell, spectral, and operando layouts.

All chart values below are generated from equations, not copied from a paper.
The cell is an idealized Li-metal full-cell stack, not a scale drawing.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap

from render_gallery import HERE, DATA, INK, MUTED, WHITE, LIGHT, csv_out, plate, save


def _top_point(x0, y0, width, depth, rise, u, v):
    return x0 + width*u + depth*v, y0 + rise*v


def _slab(ax, x0, y0, width, depth, rise, thick, top, front, side):
    a=_top_point(x0,y0,width,depth,rise,0,0)
    b=_top_point(x0,y0,width,depth,rise,1,0)
    c=_top_point(x0,y0,width,depth,rise,1,1)
    d=_top_point(x0,y0,width,depth,rise,0,1)
    ax.add_patch(patches.Polygon([(a[0],a[1]-thick),(b[0],b[1]-thick),b,a],
                                 fc=front,ec="none",zorder=3))
    ax.add_patch(patches.Polygon([b,(b[0],b[1]-thick),(c[0],c[1]-thick),c],
                                 fc=side,ec="none",zorder=3))
    shape=patches.Polygon([a,b,c,d],fc=top,ec="#8092A6",lw=.7,zorder=4)
    ax.add_patch(shape)
    ax.plot([a[0],b[0]],[a[1],b[1]],color="#657D97",lw=.8,zorder=7)
    return shape


def draw_cell_architecture():
    rng=np.random.default_rng(112)
    fig=plate("Cell stack", "", 9, kind="ORIGINAL SCHEMATIC", height=9)
    ax=fig.add_axes([.06,.12,.88,.67])
    ax.set(xlim=(0,13.5),ylim=(0,7.55));ax.set_aspect("equal");ax.axis("off")
    x0=1.05; width=6.35; depth=1.35; rise=.78
    ax.add_patch(patches.Ellipse((5.15,.78),8.2,.38,fc="#DCE7ED",ec="none",alpha=.56,zorder=0))
    layers=[
        (1.24,.18,"#C98967","#A85F42","#844631","Cu current collector"),
        (2.29,.31,"#DCC59B","#B89969","#9F7C52","Li metal"),
        (3.50,.18,"#E9FAF7","#B5DDD9","#9CC7C1","Separator + electrolyte"),
        (4.70,.44,"#456BA0","#284A7D","#223D6F","Cathode composite"),
        (6.00,.18,"#DCE6ED","#ACBEC9","#91A8B6","Al current collector"),
    ]
    for layer_index,(y,thick,top,front,side,label) in enumerate(layers):
        shape=_slab(ax,x0,y,width,depth,rise,thick,top,front,side)
        if layer_index==0:
            for u in np.linspace(.07,.94,12):
                a=_top_point(x0,y,width,depth,rise,u,.12)
                b=_top_point(x0,y,width,depth,rise,u,.89)
                ax.plot([a[0],b[0]],[a[1],b[1]],color="#E9BB9D",lw=.5,alpha=.65,zorder=5)
        elif layer_index==1:
            for _ in range(135):
                u,v=rng.uniform(.03,.97),rng.uniform(.08,.92)
                px,py=_top_point(x0,y,width,depth,rise,u,v)
                ax.add_patch(patches.Ellipse((px,py),rng.uniform(.06,.19),rng.uniform(.027,.066),
                             angle=15,fc=rng.choice(["#C5AA77","#F1DFC0","#BFA074"]),
                             ec="none",alpha=.75,zorder=5,clip_path=shape))
        elif layer_index==2:
            for _ in range(105):
                u,v=rng.uniform(.04,.96),rng.uniform(.08,.92)
                px,py=_top_point(x0,y,width,depth,rise,u,v)
                ax.add_patch(patches.Ellipse((px,py),.065,.039,fc="none",ec="#5DADA8",
                                             lw=.48,alpha=.75,zorder=5,clip_path=shape))
            for u,v in [(u,v) for u in (.16,.35,.56,.76,.89) for v in (.22,.58,.81)]:
                px,py=_top_point(x0,y,width,depth,rise,u,v)
                ax.add_patch(patches.Circle((px,py),.074,fc="#27A99E",ec="#F8FFFF",
                                            lw=.65,zorder=7,clip_path=shape))
        elif layer_index==3:
            for _ in range(84):
                u,v=rng.uniform(.04,.96),rng.uniform(.10,.9)
                px,py=_top_point(x0,y,width,depth,rise,u,v)
                r=rng.uniform(.055,.14)
                ax.add_patch(patches.Ellipse((px,py),r*2,r*1.28,angle=12,
                            fc=rng.choice(["#81A4D0","#7B96C2","#9EC0D8","#2D588D"]),
                            ec="#D4E4F0",lw=.26,zorder=5,clip_path=shape))
        elif layer_index==4:
            for u in np.linspace(.06,.94,13):
                a=_top_point(x0,y,width,depth,rise,u,.1)
                b=_top_point(x0,y,width,depth,rise,u,.89)
                ax.plot([a[0],b[0]],[a[1],b[1]],color="#F5FAFC",lw=.45,alpha=.8,zorder=5)
        leader_y=y+rise*.50
        ax.plot([9.12,9.78],[leader_y,leader_y],color="#9EB0BD",lw=.7,zorder=9)
        ax.text(9.96,leader_y,label,ha="left",va="center",fontsize=10.2,color=INK,zorder=9)
    # Vertical dashed guides explain that the offset is an exploded view.
    for u,v in [(0,0),(1,0),(0,1),(1,1)]:
        xx,_=_top_point(x0,0,width,depth,rise,u,v)
        ax.plot([xx,xx],[1.45,6.25],color="#9CB0BE",lw=.65,ls=(0,(2,4)),alpha=.6,zorder=1)
    save(fig,"cell-architecture-demo")


def draw_solvation_evidence():
    """A spectral + structural-data layout with independent synthetic traces."""
    x=np.linspace(670,1040,480)
    fig=plate("Solvation evidence", "", 10, height=8)
    ax=fig.add_axes([.105,.21,.46,.52])
    colors=["#295D9C","#198A87","#CA4F79","#D89145"]
    labels=["Formulation A","Formulation B","Formulation C","Formulation D"]
    yrows=[]
    for i,(color,label) in enumerate(zip(colors,labels)):
        p1=757+8*i; p2=871-5*i; p3=948+2*i
        y=(.76*np.exp(-.5*((x-p1)/12)**2)+.48*np.exp(-.5*((x-p2)/16)**2)
           +.34*np.exp(-.5*((x-p3)/11)**2)+.045*np.sin(x*.14+i)+.13*i)
        ax.plot(x,y+i*.72,color=color,lw=1.65)
        ax.text(1051,y[-1]+i*.72,label,color=color,fontsize=9.5,va="center",ha="left")
        yrows.extend((label,round(xv,3),round(yv+i*.72,5)) for xv,yv in zip(x,y))
    ax.set(xlim=(670,1125),ylim=(-.06,3.85),xticks=[700,800,900,1000],yticks=[],
           xlabel="Raman shift (cm⁻¹)",ylabel="Offset intensity (a.u.)")
    ax.text(-.11,1.06,"a",transform=ax.transAxes,fontsize=14,weight="bold",va="bottom")
    ax.plot([752,752],[-.02,3.58],color="#C8D3DC",lw=.65,ls=(0,(3,3)),zorder=0)
    ax.plot([875,875],[-.02,3.58],color="#C8D3DC",lw=.65,ls=(0,(3,3)),zorder=0)
    rr=np.linspace(1,8.5,380)
    bx=fig.add_axes([.655,.21,.25,.52])
    g1=.45+3.1*np.exp(-.5*((rr-2.10)/.24)**2)+1.1*np.exp(-.5*((rr-4.35)/.48)**2)
    g2=.36+2.25*np.exp(-.5*((rr-2.35)/.29)**2)+.77*np.exp(-.5*((rr-4.55)/.62)**2)
    g1 *= np.exp(-np.maximum(rr-6,0)*.16)
    g2 *= np.exp(-np.maximum(rr-6,0)*.14)
    bx.plot(rr,g1,color=colors[0],lw=1.9,label="Pair A")
    bx.plot(rr,g2,color=colors[2],lw=1.9,ls="--",label="Pair B")
    bx.fill_between(rr,0,g1,color=colors[0],alpha=.07)
    bx.set(xlim=(1,8.5),ylim=(0,4.05),xticks=[2,4,6,8],yticks=[0,1,2,3,4],
           xlabel="Distance r (Å)",ylabel="g(r)")
    bx.legend(frameon=False,loc="upper right",fontsize=9)
    bx.text(-.18,1.06,"b",transform=bx.transAxes,fontsize=14,weight="bold",va="bottom")
    csv_out("raman-waterfall-synthetic.csv",["formulation","raman_shift_cm_1","offset_intensity_au"],yrows)
    csv_out("rdf-synthetic.csv",["r_angstrom","pair_A_g_r","pair_B_g_r"],zip(rr,g1,g2))
    save(fig,"solvation-evidence-demo",[(0,1)])


def draw_operando_diffraction():
    """Show an invented state-resolved diffraction map with selected traces."""
    rng=np.random.default_rng(68)
    angle=np.linspace(18,55,300)
    state=np.linspace(0,1,116)
    aa,ss=np.meshgrid(angle,state)
    def intensity(x,s):
        return (.045
            +1.05*np.exp(-.5*((x-(24.4+2.7*s))/.38)**2)
            +.70*np.exp(-.5*((x-(35.1-1.35*s))/.58)**2)
            +(.22+.30*s)*np.exp(-.5*((x-46.8)/.48)**2)
            +.035*np.sin(x*.52+s*5)**2)
    values=intensity(aa,ss)+rng.normal(0,.013,aa.shape)
    values=np.clip(values,0,None)
    fig=plate("Operando diffraction","",11,height=8)
    cmap=LinearSegmentedColormap.from_list("xrd-ink",["#142339","#255A88","#20A7A8","#EBD7A4","#FFF3D4"])
    ax=fig.add_axes([.10,.19,.40,.55])
    im=ax.imshow(values,origin="lower",aspect="auto",extent=[angle[0],angle[-1],0,1],
                 cmap=cmap,vmin=0,vmax=1.13,interpolation="nearest")
    ax.set(xlabel="2θ (°)",ylabel="Normalized state",xticks=[20,30,40,50],
           yticks=[0,.25,.5,.75,1])
    ax.text(-.14,1.07,"a",transform=ax.transAxes,fontsize=14,weight="bold",va="bottom")
    for s in (.08,.51,.92):
        ax.axhline(s,color="white",lw=.8,ls=(0,(2,3)),alpha=.9)
    cb=fig.colorbar(im,ax=ax,fraction=.041,pad=.022,shrink=.92)
    cb.set_label("Relative intensity (a.u.)",fontsize=8)
    cb.ax.tick_params(labelsize=8)
    bx=fig.add_axes([.65,.19,.26,.55])
    selections=[(.08,"Early","#2858A5"),(.51,"Middle","#159B9A"),(.92,"Late","#C94E78")]
    rows=[]
    for i,(s,label,color) in enumerate(selections):
        curve=intensity(angle,s)
        offset=i*.85
        bx.plot(angle,curve+offset,lw=1.8,color=color)
        bx.text(52.2,offset+.22,label,color=color,fontsize=9,va="center")
        rows.extend((label,round(s,3),round(x,4),round(y,6)) for x,y in zip(angle,curve))
    bx.set(xlim=(18,62),ylim=(0,3.0),xlabel="2θ (°)",ylabel="Offset intensity (a.u.)",
           xticks=[20,30,40,50],yticks=[])
    bx.text(-.21,1.07,"b",transform=bx.transAxes,fontsize=14,weight="bold",va="bottom")
    csv_out("operando-xrd-map-synthetic.csv",["normalized_state","two_theta_deg","relative_intensity_au"],
            ((round(s,4),round(x,4),round(v,6)) for s,row in zip(state,values)
             for x,v in zip(angle,row)))
    csv_out("operando-xrd-traces-synthetic.csv",["selection","normalized_state","two_theta_deg","relative_intensity_au"],rows)
    save(fig,"operando-xrd-demo")


def render_all():
    draw_cell_architecture()
    draw_solvation_evidence()
    draw_operando_diffraction()
