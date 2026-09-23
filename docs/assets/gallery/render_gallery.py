"""Render original BatteryReviewForge gallery plates.

Every numeric observation is synthetic, generated below from explicit equations.
These are design examples, not electrochemical models or experimental evidence.
Run from any directory: python docs/assets/gallery/render_gallery.py
Requires numpy and matplotlib. The exported SVGs retain editable text.
"""

from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.transforms import Bbox
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)
ROOT = HERE.parents[2]
THEME = json.loads((ROOT / "skills/battery-review-figure/assets/figure_theme.json").read_text(encoding="utf-8"))
INK = "#202B3F"
MUTED = "#59677A"
LIGHT = "#DDE3EA"
BLUE = "#2858A5"
ROSE = "#D04E78"
TEAL = "#16877F"
PALE_BLUE = "#E4ECF8"
PALE_ROSE = "#F8E6ED"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": ["Arial", "DejaVu Sans"],
    "font.size": 11, "text.color": INK, "axes.labelcolor": INK,
    "axes.edgecolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": .8, "xtick.major.width": .7, "ytick.major.width": .7,
    "xtick.major.size": 3.5, "ytick.major.size": 3.5,
    "xtick.labelsize": 10, "ytick.labelsize": 10,
    "axes.labelsize": 11, "axes.labelpad": 8,
    "legend.frameon": False, "legend.fontsize": 10,
    "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
    "svg.fonttype": "none", "pdf.fonttype": 42,
    "figure.facecolor": WHITE, "savefig.facecolor": WHITE,
})


def line(fig, x1, y1, x2, y2, color=LIGHT, lw=.7):
    fig.add_artist(Line2D([x1, x2], [y1, y2], transform=fig.transFigure, color=color, lw=lw))


def plate(title, subtitle, number, kind="SYNTHETIC DATA", height=8):
    """Create a journal figure canvas. Story/title/conditions live in its caption."""
    return plt.figure(figsize=(12, height))


def save(fig, name, comparable=()):
    fig.canvas.draw()
    # Record actual axes rectangles. Comparable pairs must share height and top edge.
    geometry = []
    for ax in fig.axes:
        box = ax.get_position()
        geometry.append({"bounds_in": [round(box.x0*12, 5), round(box.y0*fig.get_figheight(), 5),
                                       round(box.width*12, 5), round(box.height*fig.get_figheight(), 5)]})
    for group in comparable:
        boxes = [fig.axes[i].get_position() for i in group]
        assert max(b.y1 for b in boxes)-min(b.y1 for b in boxes) < 1e-6
        assert max(b.height for b in boxes)-min(b.height for b in boxes) < 1e-6
    # Gallery plates have no brand header, narrative subtitle or footer. Trim the
    # old poster bands; keep a consistent publication-size outer white margin.
    crop = Bbox.from_bounds(.42, fig.get_figheight()*.09, 11.16, fig.get_figheight()*.72)
    (HERE / f"{name}.layout.json").write_text(json.dumps({"canvas_inches":list(fig.get_size_inches()),
        "crop_inches":[round(v,4) for v in crop.bounds], "data_status":"synthetic_demo",
        "axes":geometry,"comparable_groups":comparable}, indent=2), encoding="utf-8")
    fig.savefig(HERE / f"{name}.png", dpi=200, bbox_inches=crop)
    svg_path = HERE / f"{name}.svg"
    fig.savefig(svg_path, bbox_inches=crop)
    # Matplotlib writes trailing spaces in multiline SVG path attributes.
    # Strip them so the regenerated source remains clean in Git.
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_bytes(("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n").encode("utf-8"))
    fig.savefig(HERE / f"{name}.pdf", bbox_inches=crop,
        metadata={"Title":name, "Author":"BatteryReviewForge contributors",
                  "Subject":"Original schematic or synthetic demonstration data; not experimental evidence"})
    plt.close(fig)


def panel(ax, letter, title):
    ax.text(-.13, 1.08, letter, transform=ax.transAxes, weight="bold", fontsize=14, va="bottom")


def csv_out(name, header, rows):
    with (DATA / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def plot_pair(ax, x, y_a, y_b, lw=1.6, every=15):
    ax.plot(x, y_a, color=BLUE, lw=lw, marker="o", markevery=every, ms=3.5, mfc=WHITE, mew=.8)
    ax.plot(x, y_b, color=ROSE, lw=lw, ls=(0,(4,2)), marker="s", markevery=every, ms=3.2, mfc=WHITE, mew=.8)


def pair_key(fig, y=.785):
    handles=[Line2D([],[],color=BLUE,lw=1.6,marker="o",mfc=WHITE,ms=4,label="Electrolyte A"),
             Line2D([],[],color=ROSE,lw=1.6,ls=(0,(4,2)),marker="s",mfc=WHITE,ms=4,label="Electrolyte B")]
    fig.legend(handles=handles, loc="upper right",bbox_to_anchor=(.946,y),ncol=2,handlelength=2.5,columnspacing=2.4)


def synthetic_ce():
    n=np.arange(1,301,dtype=float)
    # A and B are imaginary electrolyte labels; no performance claim is intended.
    a=99.73-5.0*np.exp(-(n-1)/2.25)+.022*np.sin(n*.71)+.014*np.cos(n*1.9)
    b=99.20-6.2*np.exp(-(n-1)/2.7)-.0008*n+.038*np.sin(n*.47)+.019*np.cos(n*1.63)
    return n,a,b


def draw_ce():
    n,a,b=synthetic_ce()
    fig=plate("Coulombic efficiency", "Separate formation behavior from long-term cycling.",1)
    pair_key(fig)
    left=fig.add_axes([.11,.215,.29,.465])
    right=fig.add_axes([.535,.215,.365,.465])
    panel(left,"a","Formation cycles")
    panel(right,"b","Extended cycling")
    plot_pair(left,n[:15],a[:15],b[:15],every=1)
    plot_pair(right,n[14:],a[14:],b[14:],every=22)
    left.set(xlim=(.5,15.5),ylim=(92.4,100.1),xticks=[1,5,10,15],yticks=[94,96,98,100],xlabel="Cycle number",ylabel="Coulombic efficiency (%)")
    right.set(xlim=(10,308),ylim=(98.85,100.05),xticks=[50,100,150,200,250,300],yticks=[99,99.5,100],xlabel="Cycle number",ylabel="Coulombic efficiency (%)")
    for ax in (left,right):
        ax.axhline(100,color=LIGHT,lw=.8,zorder=0)
    csv_out("ce-synthetic.csv",["cycle","electrolyte_A_CE_percent","electrolyte_B_CE_percent"],zip(n,a,b))
    save(fig,"ce-demo",[(0,1)])


def synthetic_capacity():
    n=np.arange(1,301,dtype=float)
    a=156.3-.051*n-1.3*(1-np.exp(-n/70))+.34*np.sin(n*.37)
    b=155.4-.118*n-1.1*(1-np.exp(-n/50))+.31*np.cos(n*.29)
    return n,a,b


def draw_full_cell():
    n,a,b=synthetic_capacity()
    fig=plate("Full-cell performance", "Keep voltage profiles and capacity retention in the same visual language.",2)
    left=fig.add_axes([.11,.22,.34,.465])
    right=fig.add_axes([.58,.22,.32,.465])
    panel(left,"a","Discharge profiles")
    panel(right,"b","Cycling stability")
    colors=[BLUE,"#6586A1","#A0B4C5"]
    profiles=[]
    for cycle,cap,c in zip([1,100,300],[156,149,140],colors):
        q=np.linspace(0,cap,220)
        v=3.33+.19*np.exp(-q/5)-.045*(q/cap)-.72*(q/cap)**20
        left.plot(q,v,color=c,lw=1.8,label=f"Cycle {cycle}")
        profiles.extend(zip([cycle]*len(q),q,v))
    left.legend(loc="lower left",bbox_to_anchor=(.015,.16),handlelength=2.6,labelspacing=.55)
    left.set(xlim=(-4,164),ylim=(2.5,3.6),xticks=[0,50,100,150],yticks=[2.6,2.8,3.0,3.2,3.4,3.6],xlabel="Specific capacity (mAh g⁻¹)",ylabel="Cell voltage (V)")
    plot_pair(right,n,a,b,every=25)
    right.set(xlim=(-8,310),ylim=(110,162),xticks=[0,100,200,300],yticks=[120,140,160],xlabel="Cycle number",ylabel="Discharge capacity (mAh g⁻¹)")
    right.text(180,149,"Electrolyte A",color=BLUE,fontsize=10)
    right.text(173,120,"Electrolyte B",color=ROSE,fontsize=10)
    csv_out("full-cell-cycling-synthetic.csv",["cycle","electrolyte_A_mAh_g","electrolyte_B_mAh_g"],zip(n,a,b))
    csv_out("discharge-profiles-synthetic.csv",["cycle","specific_capacity_mAh_g","cell_voltage_V"],profiles)
    save(fig,"full-cell-demo",[(0,1)])


def synthetic_symmetric():
    t=np.linspace(0,240,7201)
    phase=np.mod(t,4)
    sign=np.where(phase<2,1.,-1.)
    edge=np.mod(t,2)
    a=sign*(25+.017*t+7*np.exp(-edge/.10))
    b=sign*(33+.16*t+11*np.exp(-edge/.12))
    return t,a,b


def draw_symmetric():
    t,a,b=synthetic_symmetric()
    fig=plate("Symmetric-cell cycling", "Show the complete trace, then inspect a clearly identified time window.",3)
    pair_key(fig)
    left=fig.add_axes([.11,.22,.45,.465])
    right=fig.add_axes([.68,.22,.23,.465])
    panel(left,"a","Continuous cycling")
    panel(right,"b","200–208 h")
    left.plot(t,b,color=ROSE,lw=.65,alpha=.78)
    left.plot(t,a,color=BLUE,lw=.75)
    left.axvspan(200,208,color="#DDE3E7",zorder=-2)
    left.axhline(0,color=LIGHT,lw=.65,zorder=-1)
    right.axhline(0,color=LIGHT,lw=.65,zorder=-1)
    mask=(t>=200)&(t<=208)
    right.plot(t[mask],a[mask],color=BLUE,lw=1.4)
    right.plot(t[mask],b[mask],color=ROSE,lw=1.4,ls=(0,(4,2)))
    left.set(xlim=(-3,243),ylim=(-92,92),xticks=[0,60,120,180,240],yticks=[-80,-40,0,40,80],xlabel="Time (h)",ylabel="Cell voltage (mV)")
    right.set(xlim=(199.8,208.2),ylim=(-92,92),xticks=[200,204,208],yticks=[-80,-40,0,40,80],xlabel="Time (h)",ylabel="Cell voltage (mV)")
    csv_out("symmetric-synthetic.csv",["time_h","electrolyte_A_mV","electrolyte_B_mV"],zip(t,a,b))
    save(fig,"symmetric-demo",[(0,1)])


def blank_ax(fig, bounds):
    ax=fig.add_axes(bounds)
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.set_aspect("equal"); ax.axis("off")
    return ax


def rect(ax,x,y,w,h,fc=WHITE,ec=INK,lw=1,**kw):
    p=patches.Rectangle((x,y),w,h,facecolor=fc,edgecolor=ec,lw=lw,**kw);ax.add_patch(p);return p


def ellipse(ax,x,y,w,h,fc=WHITE,ec=INK,lw=1,**kw):
    p=patches.Ellipse((x,y),w,h,facecolor=fc,edgecolor=ec,lw=lw,**kw);ax.add_patch(p);return p


def poly(ax,points,fc=WHITE,ec=INK,lw=1,**kw):
    p=patches.Polygon(points,closed=True,facecolor=fc,edgecolor=ec,lw=lw,**kw);ax.add_patch(p);return p


def leader(ax,xy,textxy,text,ha="left",color=MUTED,size=8.5):
    ax.annotate(text,xy=xy,xytext=textxy,fontsize=size,color=color,ha=ha,va="center",
        arrowprops=dict(arrowstyle="-",color="#99A5AD",lw=.7,shrinkA=3,shrinkB=2))


def cell_cross_section(ax, labels=True):
    # Generic two-electrode geometry; no crystal structure or reaction claim.
    rect(ax,2.1,1.6,.89,3.7,fc="#C8A78B",ec="#99795F",lw=.8)
    rect(ax,2.99,1.6,3.0,3.7,fc="#F0F4F7",ec="none")
    rect(ax,4.35,1.6,.40,3.7,fc=WHITE,ec="#B3C0C9",lw=.8,hatch="////")
    rect(ax,5.99,1.6,.65,3.7,fc="#A8B3BA",ec="#87949E",lw=.8)
    rect(ax,6.64,1.6,.24,3.7,fc="#D3DADF",ec="#ADB8C0",lw=.8)
    for x,y in [(3.45,2.2),(3.65,3.65),(4.03,4.8),(5.2,2.55),(5.35,4.3),(5.7,3.2)]:
        ellipse(ax,x,y,.21,.21,fc=PALE_ROSE,ec=ROSE,lw=.6)
    if labels:
        ax.text(2.6,.95,"Cu",fontsize=10,ha="center",color="#99795F")
        ax.text(6.4,.95,"Li",fontsize=10,ha="center",color=MUTED)
        leader(ax,(4.55,5.25),(4.55,6.05),"Separator",ha="center",size=9)
        leader(ax,(5.4,3.2),(8.8,3.2),"Electrolyte",ha="right",size=9)


def draw_assembled():
    fig=plate("Lithium plating and stripping", "One aligned composition: cell geometry, cycling, repeatability and voltage.",4,height=9)
    a=blank_ax(fig,[.10,.465,.335,.277])
    a.text(-.13,1.08,"a",transform=a.transAxes,weight="bold",fontsize=14)
    a.text(0,1.08,"Two-electrode geometry",transform=a.transAxes,weight="bold",fontsize=12)
    cell_cross_section(a)
    b=fig.add_axes([.585,.477,.315,.255])
    c=fig.add_axes([.11,.18,.325,.19])
    d=fig.add_axes([.585,.18,.315,.19])
    panel(b,"b","Coulombic efficiency")
    panel(c,"c","Independent cell replicates")
    panel(d,"d","Plating / stripping profile")
    n,ca,cb=synthetic_ce()
    plot_pair(b,n[14:],ca[14:],cb[14:],every=30,lw=1.2)
    b.set(xlim=(10,310),ylim=(98.85,100.05),xticks=[50,150,250],yticks=[99,99.5,100],xlabel="Cycle number",ylabel="CE (%)")
    b.text(120,99.82,"Electrolyte A",color=BLUE,fontsize=9)
    b.text(115,99.32,"Electrolyte B",color=ROSE,fontsize=9)
    va=np.array([99.68,99.73,99.80,99.72]); vb=np.array([98.92,99.04,98.98,99.12])
    for i,(values,color,mark) in enumerate([(va,BLUE,"o"),(vb,ROSE,"s")]):
        c.scatter(i+np.array([-.13,-.04,.05,.14]),values,s=24,facecolors=WHITE,edgecolors=color,linewidths=1,marker=mark,zorder=3)
        c.plot([i-.23,i+.23],[values.mean()]*2,color=color,lw=1.5)
    c.set(xlim=(-.6,1.6),ylim=(98.8,100),xticks=[0,1],xticklabels=["Electrolyte A","Electrolyte B"],yticks=[99,99.5,100],ylabel="Mean CE, cycles 50–100 (%)")
    c.text(.99,.96,"n = 4 synthetic cells / group\nLine: group mean",transform=c.transAxes,ha="right",va="top",fontsize=8.5,color=MUTED)
    q=np.linspace(0,1,250)
    vp=-.035-.11*np.exp(-q/.012)+.008*q
    qs=np.linspace(0,.997,250)
    vs=.03+.009*qs+.13*(qs/.997)**28
    d.plot(q,vp,color=BLUE,lw=1.4)
    d.plot(qs,vs,color=ROSE,lw=1.4,ls=(0,(4,2)))
    d.axhline(0,color=LIGHT,lw=.7,zorder=0)
    d.set(xlim=(-.02,1.04),ylim=(-.17,.20),xticks=[0,.5,1],yticks=[-.1,0,.1,.2],xlabel="Areal capacity (mAh cm⁻²)",ylabel="Cell voltage (V)")
    d.text(.32,-.105,"Plating",color=BLUE,fontsize=9)
    d.text(.28,.09,"Stripping",color=ROSE,fontsize=9)
    csv_out("replicate-CE-synthetic.csv",["electrolyte","synthetic_cell","mean_CE_percent"],[(name,i+1,v) for name,vals in [("A",va),("B",vb)] for i,v in enumerate(vals)])
    csv_out("plating-stripping-synthetic.csv",["branch","areal_capacity_mAh_cm2","cell_voltage_V"],[("plating",x,y) for x,y in zip(q,vp)]+[("stripping",x,y) for x,y in zip(qs,vs)])
    save(fig,"assembled-demo",[(2,3)])


def draw_styles():
    fig=plate("Six palettes. One clear system.", "The same curves, scales and line styles — only the color changes.",5,height=9)
    n,a,b=synthetic_capacity()
    presets=list(THEME["presets"].items())
    bounds=[]
    for i,(key,preset) in enumerate(presets):
        col=i%2; row=i//2
        x=.10+col*.46; y=.57-row*.21
        ax=fig.add_axes([x,y,.29,.13])
        bounds.append(ax)
        colors=preset["series"]
        ax.plot(n,a,color=colors[0],lw=1.6)
        ax.plot(n,b,color=colors[1],lw=1.6,ls=(0,(4,2)))
        ax.set(xlim=(-6,308),ylim=(110,160),xticks=[0,150,300],yticks=[120,160])
        ax.tick_params(labelsize=8.5,pad=3)
        ax.text(0,1.12,preset["label_en"],transform=ax.transAxes,fontsize=11,weight="bold")
        ax.text(1.075,.95,f"0{i+1}",transform=ax.transAxes,fontsize=9,color=MUTED,va="top")
        for j,c in enumerate(preset["swatches"]):
            p=patches.Rectangle((1.075,.63-j*.113),.19,.074,transform=ax.transAxes,fc=c,ec="none",clip_on=False)
            ax.add_patch(p)
        if col==0: ax.set_ylabel("Capacity\n(mAh g⁻¹)",fontsize=9)
        if row==2: ax.set_xlabel("Cycle number",fontsize=9)
    save(fig,"style-preview",[(0,1),(2,3),(4,5)])


def laboratory_icon(ax,kind):
    if kind=="vial":
        # Screw-cap vial, liquid meniscus and a separate transfer pipette.
        verts=[(3.2,1.6),(3.2,4.9),(3.65,5.1),(3.65,5.8),(6.1,5.8),(6.1,5.1),(6.55,4.9),(6.55,1.6),(6.2,1.3),(3.55,1.3)]
        poly(ax,verts,fc="#F6F8FA",ec=INK,lw=1)
        rect(ax,3.33,1.6,3.08,1.65,fc=PALE_BLUE,ec="none")
        ax.plot([3.33,6.41],[3.25,3.25],color=BLUE,lw=.8)
        rect(ax,3.52,5.65,2.72,.62,fc="#DEE5E9",ec=INK,lw=.9)
        for x in np.linspace(3.75,6.0,9): ax.plot([x,x],[5.72,6.20],color="#8696A1",lw=.55)
        for y in [2,2.5,3,3.5,4]: ax.plot([5.9,6.25],[y,y],color="#AAB8C2",lw=.6)
        poly(ax,[(7.25,6.2),(7.60,6.07),(6.95,4.0),(6.58,3.55),(6.77,4.13)],fc=PALE_ROSE,ec=ROSE,lw=.8)
        leader(ax,(4,3.2),(1.15,2.15),"Electrolyte",ha="left",size=8)
    elif kind=="coin":
        layers=[(5.9,4.4,.65,"#DDE3E7",INK),(4.9,3.2,.38,"#D5DCE0",MUTED),(4.1,3.55,.45,PALE_ROSE,ROSE),(3.35,3.8,.4,WHITE,"#96A7B4"),(2.65,3.55,.45,PALE_BLUE,BLUE),(1.55,4.5,.7,"#DDE3E7",INK)]
        for y,w,h,fc,ec in layers:
            rect(ax,5-w/2,y-.12,w,.15,fc=fc,ec=ec,lw=.7)
            ellipse(ax,5,y,w,h,fc=fc,ec=ec,lw=.8)
        for x in [2.9,7.1]: ax.plot([x,x],[1.8,5.65],color=LIGHT,lw=.6,ls=(0,(3,3)),zorder=-1)
        leader(ax,(6.75,3.35),(8.1,3.35),"Separator",size=8)
    elif kind=="pouch":
        rect(ax,3.35,5.65,.63,.9,fc="#C7A88F",ec=INK,lw=.7)
        rect(ax,6.02,5.65,.63,.9,fc="#BDC9D1",ec=INK,lw=.7)
        rect(ax,2.55,1.2,4.9,4.65,fc="#E9EEF1",ec=INK,lw=.9)
        rect(ax,2.87,1.52,4.26,4.0,fc=WHITE,ec="#8C9DA9",lw=.6)
        rect(ax,3.28,2.03,3.45,2.98,fc=PALE_BLUE,ec="#C3D1DB",lw=.7)
        for x in np.arange(2.7,7.4,.17):
            ax.plot([x,x+.05],[1.22,1.5],color="#A9B6BE",lw=.45)
            ax.plot([x,x+.05],[5.54,5.82],color="#A9B6BE",lw=.45)
        ax.text(3.68,6.85,"−",ha="center",fontsize=13,color=BLUE)
        ax.text(6.34,6.85,"+",ha="center",fontsize=11,color=ROSE)
    elif kind=="stack":
        for y,fc,ec in [(1.5,"#C7A78E","#A58974"),(2.35,PALE_BLUE,BLUE),(3.2,WHITE,"#9AAEBB"),(4.05,PALE_ROSE,ROSE),(4.9,"#C3D0D8","#8E9FAC")]:
            poly(ax,[(2.25,y),(6.4,y),(7.65,y+.8),(3.5,y+.8)],fc=fc,ec=ec,lw=.8)
            ax.plot([2.25,2.25,6.4,7.65,7.65],[y,y-.16,y-.16,y+.64,y+.8],color=ec,lw=.8)
        leader(ax,(7.1,3.5),(8.0,3.4),"Separator",size=8)
    elif kind=="three":
        ax.plot([2.2,2.2,2.55,7.45,7.8,7.8],[5.8,1.6,1.25,1.25,1.6,5.8],color=INK,lw=1.1)
        rect(ax,2.33,1.6,5.34,2.4,fc=PALE_BLUE,ec="none")
        ax.plot([2.33,7.67],[4,4],color="#A8BDC9",lw=.65)
        for x,name,c,w in [(3.2,"WE",BLUE,.4),(5,"RE",MUTED,.2),(6.8,"CE",ROSE,.5)]:
            ax.plot([x,x],[2.2,5.95],color=c,lw=1.6)
            rect(ax,x-w/2,2.2,w,1.45,fc=c,ec=c,lw=.7)
            ax.text(x,6.4,name,fontsize=9,color=c,ha="center")
    elif kind=="cycler":
        rect(ax,1.2,1.7,4.9,4.4,fc="#F8FAFB",ec=INK,lw=1)
        rect(ax,1.68,3.55,3.95,1.95,fc=PALE_BLUE,ec="#93A6B5",lw=.7)
        ax.plot([2.0,2.4,2.85,3.3,3.8,4.25,4.7,5.3],[4.1,4.6,4.2,4.85,4.4,4.95,4.6,5.05],color=BLUE,lw=1.2)
        for x,c in [(2.1,BLUE),(2.8,ROSE)]: ellipse(ax,x,2.5,.28,.28,fc=c,ec=c,lw=.5)
        for y in [2.35,2.6,2.85]: ax.plot([3.8,5.4],[y,y],color="#B8C4CC",lw=.6)
        rect(ax,7.4,2.05,1.55,2.65,fc=WHITE,ec=INK,lw=.9)
        rect(ax,7.8,4.7,.72,.42,fc="#C6D3DD",ec=INK,lw=.7)
        ax.plot([6.1,6.5,6.5,8.16],[3.5,3.5,5.12,5.12],color=ROSE,lw=1)
        ax.plot([6.1,6.85,6.85,8.16,8.16],[2.8,2.8,1.6,1.6,2.05],color=BLUE,lw=1)


def draw_lab():
    fig=plate("A visual language for the battery lab", "Original vector elements with consistent strokes, spacing and material colors.",6,"ORIGINAL SCHEMATICS",height=9)
    items=[("vial","Electrolyte preparation"),("coin","Exploded coin cell"),("pouch","Pouch cell"),("stack","Electrode stack"),("three","Three-electrode cell"),("cycler","Cycling instrument")]
    for i,(kind,name) in enumerate(items):
        col=i%3; row=i//3
        x=.065+col*.306; y=.425-row*.315
        ax=blank_ax(fig,[x,y,.268,.275])
        laboratory_icon(ax,kind)
        fig.text(x,.748-row*.315,f"0{i+1}",fontsize=9,color=MUTED)
        fig.text(x+.028,.748-row*.315,name,fontsize=10.5,weight="bold")
    save(fig,"lab-primitives")


def morphology(ax,kind):
    if kind=="particles":
        circles=[(2.6,2.1,.78),(4.05,2.05,.78),(5.53,2.1,.78),(6.94,2.35,.73),(3.32,3.42,.80),(4.85,3.46,.84),(6.43,3.7,.74),(4.08,4.8,.8),(5.63,4.96,.75)]
        for x,y,r in circles:
            ellipse(ax,x,y,r*2,r*2,fc=PALE_BLUE,ec=BLUE,lw=.95)
            ellipse(ax,x,y,r*1.23,r*1.23,fc=WHITE,ec="#A0B5C6",lw=.55)
        leader(ax,(5.45,4.88),(8.65,5.6),"Core",ha="right",size=9)
        leader(ax,(6.95,3.8),(9,3.8),"Shell",ha="right",size=9)
    elif kind=="rods":
        for x,y in [(2.4,1.5),(3.7,1.85),(5.,1.35),(6.3,1.8),(7.5,1.45)]:
            dx=.25; w=.57; h=3.75
            poly(ax,[(x,y),(x+w,y+.22),(x+w+dx,y+h+.22),(x+dx,y+h)],fc=PALE_BLUE,ec=BLUE,lw=.8)
            poly(ax,[(x+w,y+.22),(x+w+.22,y+.46),(x+w+dx+.22,y+h+.46),(x+w+dx,y+h+.22)],fc="#B5C9D8",ec=BLUE,lw=.6)
            poly(ax,[(x+dx,y+h),(x+w+dx,y+h+.22),(x+w+dx+.22,y+h+.46),(x+dx+.22,y+h+.24)],fc=WHITE,ec=BLUE,lw=.6)
    elif kind=="sheets":
        for j in range(4):
            y=1.0+j*1.0
            poly(ax,[(1.8,y+.45),(6.1,y),(8.3,y+1.6),(4,y+2.05)],fc=["#DAE6EE","#D2E0E9","#E5EDF3","#EFF4F7"][j],ec=BLUE,lw=.75)
            for k in range(1,6):
                ax.plot([1.8+k*.71,4+k*.71],[y+.45-k*.074,y+2.05-k*.074],color="#B4C6D2",lw=.4)
                ax.plot([1.8+k*.367,6.1+k*.367],[y+.45+k*.267,y+k*.267],color="#B4C6D2",lw=.4)
    elif kind=="network":
        # Deliberate planar graph. Nodes/links are conceptual, not atomistic bonds.
        pts=np.array([[1.6,2.5],[2.2,4.25],[3.35,5.1],[4.8,4.6],[6.2,5.15],[7.8,4.5],
                      [8.6,2.9],[7.4,1.8],[5.9,1.35],[4.4,2.05],[2.9,1.5],[3.1,3.25],
                      [4.7,3.3],[6.5,3.3]])
        edges=[(0,1),(0,10),(0,11),(1,2),(1,11),(2,3),(3,4),(3,12),(4,5),(5,6),(5,13),(6,7),(6,13),(7,8),(8,9),(8,13),(9,10),(9,12),(10,11),(11,12),(12,13)]
        for u,v in edges: ax.plot(pts[[u,v],0],pts[[u,v],1],color="#A9C0D0",lw=9,solid_capstyle="round",zorder=1)
        for u,v in edges: ax.plot(pts[[u,v],0],pts[[u,v],1],color=PALE_BLUE,lw=6,solid_capstyle="round",zorder=2)
        for x,y in pts: ellipse(ax,x,y,.29,.29,fc=WHITE,ec=BLUE,lw=.65,zorder=3)


def draw_morphology():
    fig=plate("Material architecture", "Reusable idealized forms — draw the geometry, then state what the evidence supports.",7,"ORIGINAL SCHEMATICS",height=9)
    items=[("particles","Core–shell particles","Particle and shell are independently editable."),("rods","Aligned rods","A geometric ensemble; no crystal phase implied."),("sheets","Layered sheets","Layer spacing is illustrative."),("network","Open network","Links represent structure, not atomic bonds.")]
    for i,(kind,title,caption) in enumerate(items):
        col=i%2; row=i//2
        x=.075+col*.465; y=.475-row*.333
        ax=blank_ax(fig,[x,y,.36,.235])
        morphology(ax,kind)
        fig.text(x,.752-row*.34,chr(97+i),fontsize=13,weight="bold")
        fig.text(x+.03,.752-row*.34,title,fontsize=12,weight="bold")
    save(fig,"morphology-primitives")


def draw_tofsims():
    """Original simulated ion maps and sputter-time traces, never a micrograph."""
    rng = np.random.default_rng(118)
    grid = np.linspace(0, 100, 150)
    xx, yy = np.meshgrid(grid, grid)
    def spot(x, y, sx, sy):
        return np.exp(-.5 * (((xx-x)/sx)**2 + ((yy-y)/sy)**2))
    grain = rng.normal(0, .035, xx.shape)
    lif = (.13 + .74*spot(28,67,14,18) + .78*spot(73,34,19,13)
           + .32*spot(71,80,10,11) + .075*np.sin(xx*.22)*np.cos(yy*.15) + grain)
    organic = (.10 + .72*spot(69,69,17,19) + .76*spot(28,27,18,14)
               + .32*spot(33,76,8,11) + .07*np.cos(xx*.18)*np.sin(yy*.17) - grain*.5)
    lif = np.clip(lif/lif.max(), 0, 1)
    organic = np.clip(organic/organic.max(), 0, 1)
    rgb = np.stack([np.clip(organic*.95 + lif*.09,0,1),
                    np.clip(lif*.78 + organic*.18,0,1),
                    np.clip(lif*.95 + organic*.30,0,1)], axis=2)
    blue_cmap = LinearSegmentedColormap.from_list("ion-blue", ["#071622", "#0E426B", "#39BFD1", "#ECFAFB"])
    pink_cmap = LinearSegmentedColormap.from_list("ion-rose", ["#120F25", "#67265C", "#D9519B", "#FCEAF4"])
    fig = plate("ToF-SIMS", "", 8, height=8)
    for i,(signal,cmap,identity) in enumerate([(lif,blue_cmap,"LiF₂⁻"),
                                                (organic,pink_cmap,"C₂HO⁻"),
                                                (rgb,None,"Overlay")]):
        ax = fig.add_axes([.095+i*.294,.43,.25,.33])
        ax.imshow(signal,origin="lower",extent=(0,100,0,100),cmap=cmap,vmin=0,vmax=1,
                  interpolation="nearest")
        ax.set(xlim=(0,100),ylim=(0,100),xticks=[],yticks=[])
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.text(-.09,1.065,chr(97+i),transform=ax.transAxes,fontsize=14,
                fontweight="bold",color=INK,va="bottom")
        ax.text(.035,1.065,identity,transform=ax.transAxes,fontsize=11,
                fontweight="bold",color=INK,va="bottom")
        ax.plot([8,28],[9,9],color="white",lw=2.5,solid_capstyle="butt")
        ax.text(8,13,"20 μm",color="white",fontsize=8,weight="bold")
    t=np.linspace(0,240,241)
    f = .16+.79*np.exp(-((t-88)/59)**2)+.014*np.sin(t*.17)
    o = .10+.85*np.exp(-t/68)+.012*np.sin(t*.23+.8)
    li = .08+.78*(1-np.exp(-t/93))+.015*np.cos(t*.13)
    f=np.clip(f,0,1);o=np.clip(o,0,1);li=np.clip(li,0,1)
    ax=fig.add_axes([.12,.17,.77,.20])
    ax.text(-.065,1.08,"d",transform=ax.transAxes,weight="bold",fontsize=14,va="bottom")
    for y,c,label,ls in [(f,"#00AAB6","LiF₂⁻","-"),(o,"#C53E86","C₂HO⁻","--"),
                          (li,"#5066AE","⁷Li⁻","-.")]:
        ax.plot(t,y,color=c,lw=2.1,label=label,ls=ls)
    ax.set(xlim=(0,240),ylim=(0,1.08),xticks=[0,60,120,180,240],yticks=[0,.5,1],
           xlabel="Sputter time (s)",ylabel="Normalized ion signal (a.u.)")
    ax.legend(loc="upper right",ncol=3,bbox_to_anchor=(1.01,1.20),fontsize=9.5,
              handlelength=2.3,columnspacing=2)
    csv_out("tofsims-depth-synthetic.csv",["sputter_time_s","LiF2_minus_relative_signal",
        "C2HO_minus_relative_signal","Li7_minus_relative_signal"],zip(t,f,o,li))
    with (DATA/"tofsims-maps-synthetic.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.writer(handle)
        writer.writerow(["x_um","y_um","LiF2_minus_relative_signal","C2HO_minus_relative_signal"])
        for row in range(len(grid)):
            for col in range(len(grid)):
                writer.writerow([round(xx[row,col],4),round(yy[row,col],4),
                                 round(lif[row,col],5),round(organic[row,col],5)])
    save(fig,"tofsims-demo",[(0,1,2)])


def contact_sheet():
    names=["cell-architecture-demo","tofsims-demo","operando-xrd-demo","solvation-evidence-demo",
           "assembled-demo","ce-demo","full-cell-demo","symmetric-demo",
           "style-preview","lab-primitives","morphology-primitives"]
    fig,axes=plt.subplots(6,2,figsize=(12,24),facecolor="#E9EDF0")
    for ax in axes.flat: ax.axis("off")
    for ax,name in zip(axes.flat,names):
        ax.imshow(plt.imread(HERE/f"{name}.png"));ax.set_title(name,fontsize=10,color=INK,pad=5)
    fig.subplots_adjust(left=.025,right=.975,top=.975,bottom=.02,wspace=.05,hspace=.09)
    fig.savefig(HERE/"gallery-contact-sheet.png",dpi=130)
    plt.close(fig)


if __name__=="__main__":
    draw_ce();draw_full_cell();draw_symmetric();draw_assembled()
    draw_styles();draw_lab();draw_morphology();draw_tofsims()
    from render_showcases import render_all
    render_all();contact_sheet()
    print("Rendered eleven original publication plates, editable SVG/PDF, source CSVs and contact sheet.")
