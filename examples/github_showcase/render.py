"""Render the GitHub gallery from the exact, versioned synthetic input files.

python examples/github_showcase/render.py
No data generation, smoothing, interpolation, circuit fitting or image reuse.
Requires numpy, pandas and matplotlib. The input manifest is checked before use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INK, MUTED = "#1d2c38", "#586878"
COLOURS = ["#087f8c", "#b34b72", "#4267a2", "#a16d2f"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply_figure_style() -> str:
    """Use a role-based type scale, boxed frames and solid continuous curves."""
    available = {f.name for f in font_manager.fontManager.ttflist}
    family = "Arial" if "Arial" in available else "DejaVu Sans"
    plt.rcParams.update({
        "font.family": family, "font.size": 10, "axes.labelsize": 10,
        "axes.titlesize": 11, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "legend.fontsize": 9, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.titlepad": 12,
        "axes.spines.top": True, "axes.spines.right": True,
        "axes.spines.bottom": True, "axes.spines.left": True,
        "axes.linewidth": .8, "axes.grid": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.width": .8, "ytick.major.width": .8,
        "xtick.major.size": 3.5, "ytick.major.size": 3.5,
        "lines.linewidth": 1.7, "lines.linestyle": "-", "lines.marker": "None",
        "legend.frameon": False, "pdf.fonttype": 42, "svg.fonttype": "none",
        "svg.hashsalt": "VoltPeer-GitHub-gallery-20261001",
        "mathtext.fontset": "dejavusans", "text.color": INK,
        "axes.edgecolor": INK, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK, "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })
    return family


class Gallery:
    def __init__(self, data_root: Path, output: Path):
        self.data_root, self.output = data_root.resolve(), output.resolve()
        self.font = apply_figure_style()
        self.manifest = json.loads((self.data_root / "PROVENANCE.json").read_text(encoding="utf-8"))
        self.input_before = {}
        for relative, record in self.manifest["files"].items():
            path = (self.data_root / relative).resolve()
            if not path.is_relative_to(self.data_root):
                raise ValueError("Input path escapes the data folder")
            actual = digest(path)
            if actual != record["sha256"]:
                raise ValueError(f"Synthetic input changed: {relative}")
            self.input_before[relative] = actual
        self.checks = []
        self.figure_checks = []
        self.output.mkdir(parents=True, exist_ok=True)

    def frame(self, group: str) -> pd.DataFrame:
        return pd.read_csv(self.data_root / group / "data.csv")

    def basis(self, group: str) -> dict:
        return json.loads((self.data_root / group / "basis.json").read_text(encoding="utf-8"))

    def check(self, name: str, actual, expected, *, atol=1e-9, rtol=1e-10):
        x, y = np.asarray(actual), np.asarray(expected)
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
            raise AssertionError(f"{name}: nonfinite input")
        if not np.allclose(x, y, atol=atol, rtol=rtol):
            raise AssertionError(f"{name}: model relation mismatch")
        self.checks.append({"name": name, "values": int(x.size),
                            "max_absolute_error": float(np.max(np.abs(x-y)))})

    def validate_models(self):
        for group in ("eis", "eis_frequency"):
            d, p = self.frame(group), self.basis(group)["parameters"]
            for key in "AB":
                g = d[d["sample"] == key]
                omega = 2*np.pi*g.frequency_Hz.to_numpy()
                prm = p[key]
                if group == "eis":
                    zw = prm["Warburg_sigma"]*(1-1j)/np.sqrt(omega)
                    z = prm["Rs_ohm"] + 1 / (prm["CPE_Q"]*(1j*omega)**prm["CPE_alpha"]
                                               + 1/(prm["Rct_ohm"] + zw))
                    real, imag = g.Zreal_ohm, g.Zimag_ohm
                else:
                    z = prm["Rs_ohm"] + prm["Rct_ohm"]/(1+1j*omega*prm["Rct_ohm"]*prm["C_F"])
                    real, imag = g.z_real_ohm, g.z_imag_ohm
                    circle = (real-prm["Rs_ohm"]-prm["Rct_ohm"]/2)**2 + imag**2
                    self.check(f"{group}/{key}: ideal RC circle", circle,
                               np.full(len(g), (prm["Rct_ohm"]/2)**2))
                self.check(f"{group}/{key}: Re Z", real, z.real)
                self.check(f"{group}/{key}: Im Z", imag, z.imag)
                assert np.all(real > 0) and np.all(imag <= 0)
                assert np.all(g.frequency_Hz > 0)

        ce = self.frame("li_cu_ce")
        for key in "AB":
            self.check(f"Li || Cu/{key}: charge ledger", ce[f"{key}_ce_pct"],
                       100*ce[f"{key}_stripped_mAh_cm2"]/ce.plated_mAh_cm2)
        half = self.frame("full_cell")
        for key in "AB":
            self.check(f"NMC811 || Li/{key}: charge ledger", half[f"{key}_ce_pct"],
                       100*half[f"{key}_mAh_g"]/half[f"{key}_charge_mAh_g"])
        xps = self.frame("xps_components")
        self.check("Generic spectrum: expected count sum", xps.expected_counts,
                   xps.background_counts+xps.component_1+xps.component_2+xps.component_3)
        assert np.all(xps.select_dtypes("number") >= 0)
        xp = self.basis("xps_components")["parameters"]
        for i,(center,width,height) in enumerate(zip(xp["peak_centers_eV"],xp["shape_width_eV"],xp["peak_heights_counts"]),1):
            scaled=(xps.binding_energy_eV-center)/width
            mix=(1-xp["lorentzian_fraction"])*np.exp(-.5*scaled**2)+xp["lorentzian_fraction"]/(1+scaled**2)
            self.check(f"Generic spectrum: known component {i}",xps[f"component_{i}"],height*mix)
        xrd = self.frame("operando_xrd")
        assert xrd.duplicated(["soc_fraction", "two_theta_deg"]).sum() == 0
        assert np.all(xrd.intensity_au >= 0)
        assert np.all(xrd.soc_fraction.between(0, 1))
        xp = self.basis("operando_xrd")["parameters"]
        progress=xrd.soc_fraction.to_numpy()
        centers=[2*np.degrees(np.arcsin(xp["wavelength_A"]/(2*xp[f"d{i}_initial_A"]*(1+xp[f"strain{i}_at_p1"]*progress)))) for i in (1,2)]
        prediction=np.full(len(xrd),xp["background_au"])
        for center,width,height in zip(centers,xp["sigma_deg"],xp["amplitudes_au"]):
            prediction+=height*np.exp(-.5*((xrd.two_theta_deg.to_numpy()-center)/width)**2)
        self.check("Diffraction: first-order Bragg angles and original Gaussian intensity",xrd.intensity_au,prediction)
        raman=self.frame("raman_series")
        for i,key in enumerate("ABCD"):
            g=raman[raman["sample"]==key];x=g.wavenumber_cm_1.to_numpy()
            gaussian=lambda center,width:np.exp(-.5*((x-center)/width)**2)
            prediction=45+.14*(x-680)+(330-45*i)*gaussian(730,4.5)+(100+55*i)*gaussian(745+.6*i,5.2)+55*gaussian(783,6)
            self.check(f"Raman/{key}: original Gaussian bands and background",g.intensity_counts,prediction)

    @staticmethod
    def finish_axis(ax, letter: str, title: str):
        ax.set_title(f"{letter}   {title}", loc="left")
        for spine in ax.spines.values():
            spine.set_visible(True)
        ax.tick_params(pad=4)

    @staticmethod
    def legend(ax, **kwargs):
        options = {"handlelength": 2.0, "borderpad": .15, "labelspacing": .5}
        options.update(kwargs)
        ax.legend(**options)

    @staticmethod
    def heading(fig, title: str, subtitle: str):
        fig.text(.075, .955, title, fontsize=16, weight="bold", va="top")
        fig.text(.075, .895, subtitle, fontsize=9.5, color=MUTED, va="top")

    @staticmethod
    def footer(fig, text: str):
        fig.text(.075, .035, text, color=MUTED, fontsize=8.5, va="bottom")

    def xrd_map(self, ax):
        d = self.frame("operando_xrd")
        grid = d.pivot(index="soc_fraction", columns="two_theta_deg", values="intensity_au")
        im = ax.pcolormesh(grid.columns, grid.index, grid.values, cmap="magma", shading="nearest",
                           vmin=float(grid.values.min()), vmax=float(grid.values.max()), rasterized=True)
        ax.set(xlabel="2θ (°)", ylabel="Model progress", xlim=(grid.columns.min(), grid.columns.max()), ylim=(0, 1))
        return im

    def xrd_traces(self, ax):
        d = self.frame("operando_xrd")
        progresses = np.unique(d.soc_fraction)
        choices = progresses[[0, 26, 52, 78, 104]]
        palette = plt.colormaps["viridis"](np.linspace(.13, .80, len(choices)))
        for i, (progress, colour) in enumerate(zip(choices, palette)):
            g = d[d.soc_fraction == progress]
            ax.plot(g.two_theta_deg, g.intensity_au+i*.72, color=colour, label=f"p = {progress:g}")
            ax.text(46.2, .15+i*.72, f"p = {progress:g}", color=INK,
                    ha="right", va="bottom", fontsize=8)
        ax.set(xlabel="2θ (°)", ylabel="Intensity + display offset (a.u.)")
        ax.margins(x=.025, y=.055)

    def raman(self, ax):
        d = self.frame("raman_series")
        for i, (key, colour) in enumerate(zip("ABCD", COLOURS)):
            g = d[d["sample"] == key]
            ax.plot(g.wavenumber_cm_1, g.intensity_counts+340*i, color=colour, label=f"Model {key}")
            ax.text(801,340*i+105,f"Model {key}",color=colour,ha="right",va="bottom",fontsize=8)
        ax.set(xlabel="Raman shift (cm$^{-1}$)", ylabel="Counts + display offset")
        ax.margins(x=.03, y=.055)

    def xps(self, ax, compact=False):
        d = self.frame("xps_components")
        e, base = d.binding_energy_eV, d.background_counts
        ax.plot(e, d.intensity_counts, color="#a7b0ba", lw=.65, label="Poisson counts", zorder=1)
        for i, colour in enumerate(COLOURS[:3], 1):
            top = base + d[f"component_{i}"]
            ax.fill_between(e, base, top, color=colour, alpha=.18, linewidth=0)
            ax.plot(e, top, color=colour, lw=1.15, label=f"Component {i} + background")
        ax.plot(e, d.expected_counts, color=INK, lw=1.25, label="Expected total")
        ax.set(xlabel="Binding energy (eV)", ylabel="Counts", xlim=(294.4,279.6))
        ax.margins(y=.06)
        if compact:
            self.legend(ax, loc="upper left", fontsize=6.4, handlelength=1.6)
        else:
            self.legend(ax, loc="upper left", fontsize=7.6, handlelength=1.6)

    def eis_views(self, axes, group: str):
        ny, mag, phase = axes
        d = self.frame(group)
        xr, yi = ("Zreal_ohm", "Zimag_ohm") if group == "eis" else ("z_real_ohm", "z_imag_ohm")
        xmax, ymax = 0., 0.
        for key, colour in zip("AB", COLOURS):
            g = d[d["sample"] == key]
            real, imag = g[xr].to_numpy(), g[yi].to_numpy()
            z = real + 1j*imag
            ny.plot(real, -imag, color=colour, label=f"Model {key}")
            mag.loglog(g.frequency_Hz, np.abs(z), color=colour, label=f"Model {key}")
            phase.semilogx(g.frequency_Hz, np.angle(z, deg=True), color=colour)
            xmax, ymax = max(xmax, float(real.max())), max(ymax, float((-imag).max()))
        ny.set(xlabel="Z′ (Ω)", ylabel="−Z″ (Ω)", xlim=(0, xmax*1.055), ylim=(0, ymax*1.28))
        ny.set_aspect("equal", adjustable="box")
        ny.xaxis.set_major_locator(ticker.MaxNLocator(5))
        ny.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.legend(ny, loc="upper left", ncol=2, fontsize=9)
        mag.set(xlabel="", ylabel="|Z| (Ω)", xlim=(.0075, 1.3e5))
        mag.yaxis.set_major_locator(ticker.LogLocator(base=10, subs=[1,2,5]))
        mag.yaxis.set_major_formatter(ticker.ScalarFormatter())
        mag.tick_params(labelbottom=False)
        phase.set(xlabel="Frequency (Hz)", ylabel="Phase (°)", xlim=(.0075,1.3e5))
        phase.margins(y=.12)
        for a in (mag, phase):
            a.xaxis.set_major_locator(ticker.LogLocator(base=10, numticks=5))
            a.xaxis.set_minor_locator(ticker.NullLocator())
            a.yaxis.set_minor_locator(ticker.NullLocator())

    def save(self, fig, slug: str, sources: list[str], transformations: list[str]):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        checks = {"slug": slug, "sources": sources, "display_transformations": transformations, "axes": []}
        for i, ax in enumerate(fig.axes):
            if getattr(ax, "_colorbar", None) is not None:
                continue
            lines = []
            for line in ax.lines:
                x, y = np.asarray(line.get_xdata(), dtype=float), np.asarray(line.get_ydata(), dtype=float)
                assert line.get_linestyle() == "-" and line.get_marker() in ("None", "", None)
                assert len(x) == len(y) and np.all(np.isfinite(x)) and np.all(np.isfinite(y))
                xl, yl = sorted(ax.get_xlim()), sorted(ax.get_ylim())
                assert x.min() >= xl[0]-1e-7 and x.max() <= xl[1]+1e-7, (slug,i,"x clipped")
                assert y.min() >= yl[0]-1e-7 and y.max() <= yl[1]+1e-7, (slug,i,"y clipped")
                lines.append({"label": line.get_label(), "points": len(x), "linestyle": "-", "marker": "None"})
            frames = {key: spine.get_visible() for key,spine in ax.spines.items()}
            assert all(frames.values())
            box = ax.get_window_extent(renderer)
            is_nyquist = ax.get_xlabel() == "Z′ (Ω)"
            equal_scale = None
            if is_nyquist:
                sx = box.width/abs(np.diff(ax.get_xlim())[0])
                sy = box.height/abs(np.diff(ax.get_ylim())[0])
                assert abs(sx/sy-1) < 1e-8
                equal_scale = float(sx/sy)
            checks["axes"].append({"index":i,"frame":frames,"curves":lines,
                                  "equal_nyquist_scale_ratio":equal_scale})
        # Labels must remain inside the output canvas. No bbox="tight" resizing hides defects.
        outside_ticks = set()
        for ax in fig.axes:
            for axis, limits in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
                low, high = sorted(limits)
                for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                    if not low <= tick.get_loc() <= high:
                        outside_ticks.update((tick.label1, tick.label2))
        for artist in fig.findobj(matplotlib.text.Text):
            if artist in outside_ticks:
                continue  # Matplotlib does not draw locator ticks outside the view limits.
            if artist.get_visible() and artist.get_text():
                box = artist.get_window_extent(renderer)
                assert box.x0 >= -1 and box.y0 >= -1 and box.x1 <= fig.bbox.width+1 and box.y1 <= fig.bbox.height+1, (slug, artist.get_text(), list(box.bounds))
        protected = list(fig.texts)
        for ax in fig.axes:
            protected.extend((ax._left_title, ax.xaxis.label, ax.yaxis.label))
        protected = [a for a in protected if a.get_visible() and a.get_text()]
        for i, first in enumerate(protected):
            b1 = first.get_window_extent(renderer)
            for second in protected[i+1:]:
                b2 = second.get_window_extent(renderer)
                overlap = matplotlib.transforms.Bbox.intersection(b1,b2)
                assert overlap is None or overlap.width*overlap.height < 1, (slug,"labels overlap",first.get_text(),second.get_text())
        checks["panel_title_axis_label_overlap"] = "PASS"
        for extension in ("png", "svg"):
            destination = self.output / f"{slug}.{extension}"
            if extension == "svg":
                fig.savefig(destination, dpi=250, metadata={"Date": None})
                # Canonicalize XML whitespace only; data/path coordinates are unchanged.
                xml = destination.read_text(encoding="utf-8")
                destination.write_text("\n".join(line.rstrip() for line in xml.splitlines())+"\n",
                                       encoding="utf-8", newline="\n")
            else:
                fig.savefig(destination, dpi=250)
        checks["png_dimensions"] = list(plt.imread(self.output/f"{slug}.png").shape[:2][::-1])
        checks["output_sha256"] = {ext:digest(self.output/f"{slug}.{ext}") for ext in ("png","svg")}
        self.figure_checks.append(checks)
        plt.close(fig)

    def structure(self):
        fig = plt.figure(figsize=(9.2,7.4))
        self.heading(fig, "Structure & spectra", "Original synthetic models · no material assignment")
        axes = [fig.add_axes(box) for box in ((.085,.555,.34,.28),(.605,.555,.345,.28),(.085,.14,.34,.28),(.605,.14,.345,.28))]
        image = self.xrd_map(axes[0])
        cb = fig.colorbar(image, cax=fig.add_axes((.445,.555,.012,.28)))
        cb.set_label("Intensity (a.u.)", fontsize=8.5)
        cb.ax.tick_params(labelsize=7.5)
        self.xrd_traces(axes[1]); self.raman(axes[2]); self.xps(axes[3])
        for a, letter, title in zip(axes,"abcd",("Bragg-law peak evolution","Five model-progress traces","Generic Raman bands","Known spectral components")):
            self.finish_axis(a,letter,title)
        self.footer(fig, "Display offsets: diffraction +0.72 a.u. / trace; Raman +340 counts / trace. No raw values changed.")
        self.save(fig,"structure-spectra",["operando_xrd","raman_series","xps_components"],
                  ["Five existing diffraction progress rows selected; +0.72 a.u. offset per trace", "Raman +340 counts per trace", "Known spectral components shown on their common background; no fitting"])

    def eis(self, group: str, slug: str, subtitle: str):
        fig = plt.figure(figsize=(9.2,4.6))
        self.heading(fig,"Impedance spectroscopy",subtitle)
        axes = [fig.add_axes(box) for box in ((.085,.23,.425,.48),(.635,.55,.30,.23),(.635,.205,.30,.23))]
        self.eis_views(axes,group)
        for a,letter,title in zip(axes,"abc",("Nyquist","Impedance magnitude","Signed phase")):
            self.finish_axis(a,letter,title)
        self.footer(fig,"Same complex Z(f) in every panel · equal Ω scale in Nyquist · synthetic model, no circuit fit")
        self.save(fig,slug,[group],["Re Z, −Im Z, abs(Z) and arg(Z) calculated from the same saved complex values; no smoothing or interpolation"])

    def assembly(self):
        fig = plt.figure(figsize=(9.2,10.0))
        self.heading(fig,"One figure, consistent panels", "Six independent teaching examples · a layout demonstration, not one experimental study")
        boxes = [(x,y,.335,.18) for y in (.650,.390,.130) for x in (.095,.62)]
        axes = [fig.add_axes(box) for box in boxes]
        ce, half, impedance = self.frame("li_cu_ce"), self.frame("full_cell"), self.frame("eis")
        for key,colour in zip("AB",COLOURS):
            axes[0].plot(ce.cycle,ce[f"{key}_ce_pct"],color=colour,label=f"Model {key}")
            axes[1].plot(half.cycle,half[f"{key}_mAh_g"],color=colour,label=f"Model {key}")
            g=impedance[impedance["sample"]==key]
            axes[2].plot(g.Zreal_ohm,-g.Zimag_ohm,color=colour,label=f"Model {key}")
            axes[3].semilogx(g.frequency_Hz,np.angle(g.Zreal_ohm+1j*g.Zimag_ohm,deg=True),color=colour)
        axes[0].set(xlabel="Cycle number",ylabel="Coulombic efficiency (%)",ylim=(97,100.05)); axes[0].margins(x=.035)
        axes[1].set(xlabel="Cycle number",ylabel="Capacity (mAh g$^{-1}$)");axes[1].margins(x=.035,y=.08)
        axes[2].set(xlabel="Z′ (Ω)",ylabel="−Z″ (Ω)",xlim=(0,68),ylim=(0,68*(10*.18)/(9.2*.335)));axes[2].set_aspect("equal",adjustable="box")
        axes[3].set(xlabel="Frequency (Hz)",ylabel="Phase (°)"); axes[3].margins(y=.13)
        axes[3].xaxis.set_major_locator(ticker.LogLocator(base=10,numticks=4));axes[3].xaxis.set_minor_locator(ticker.NullLocator())
        image=self.xrd_map(axes[4]);cb=fig.colorbar(image,cax=fig.add_axes((.45,.130,.009,.18)));cb.ax.tick_params(labelsize=7)
        self.xps(axes[5],compact=True)
        for a in axes[:3]: self.legend(a,loc="upper right" if a is not axes[0] else "lower right",fontsize=8)
        titles=("Li || Cu: coulombic efficiency","NMC811 || Li: capacity","Model impedance: Nyquist","Same Z(f): phase","Bragg-law diffraction model","Generic count spectrum")
        for a,letter,title in zip(axes,"abcdef",titles): self.finish_axis(a,letter,title)
        self.footer(fig,"Each technique has its own declared model and parameters. Local A/B labels do not connect different techniques.")
        self.save(fig,"six-panel-layout",["li_cu_ce","full_cell","eis","operando_xrd","xps_components"],
                  ["Independent panels assembled without claiming one shared material or mechanism", "Same EIS complex values in panels c/d", "Known spectral components displayed on common background"])

    def run(self):
        self.validate_models()
        self.structure()
        self.eis("eis","eis-cpe-warburg","Original passive CPE / Warburg model · all 86 frequencies per model")
        self.eis("eis_frequency","eis-ideal-rc","Original ideal RC model · all 120 frequencies per model")
        self.assembly()
        for relative,expected in self.input_before.items():
            assert digest(self.data_root/relative)==expected, f"Input modified: {relative}"
        report={"schema_version":1,"status":"PASS","data_status":"original_synthetic",
                "font":self.font,"raw_inputs_unchanged":True,"inputs_sha256":self.input_before,
                "model_relations":self.checks,"figures":self.figure_checks,
                "scope":"Exact declared model/data and display checks only; no experimental validation, circuit fit, chemical assignment or host/model behavior certification"}
        (self.output/"render-checks.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
        print(json.dumps({"status":"PASS","figures":len(self.figure_checks),"model_checks":len(self.checks),"raw_inputs_unchanged":True}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root",type=Path,default=ROOT/"assets/github-showcase/data")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"assets/github-showcase")
    args=parser.parse_args()
    Gallery(args.data_root,args.output_dir).run()


if __name__=="__main__":
    main()
