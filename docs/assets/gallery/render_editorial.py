"""Render a synthetic, evidence-led battery figure for the public gallery.

All curves come from the repository's invented CSV examples. This layout is a
composition example, not a connected experiment or evidence for a mechanism.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
BLUE = "#1d5d80"
CORAL = "#bd4f66"
INK = "#1b3040"
MUTED = "#657887"
LINE = "#cbd6de"


def numeric(name: str) -> np.ndarray:
    return np.genfromtxt(DATA / name, delimiter=",", names=True)


def finish(ax, xlabel: str, ylabel: str, letter: str, label_x: float = -0.08) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(INK)
        ax.spines[spine].set_linewidth(0.85)
    ax.tick_params(colors=MUTED, labelsize=8, width=0.8, length=3.5, pad=5)
    ax.set_xlabel(xlabel, fontsize=9.2, color=INK, labelpad=7)
    ax.set_ylabel(ylabel, fontsize=9.2, color=INK, labelpad=8)
    ax.text(label_x, 1.07, letter, transform=ax.transAxes, fontsize=13, weight="bold", color=INK)


def draw_stack(ax) -> None:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.text(-0.25, 4.08, "a", fontsize=13, weight="bold", color=INK)
    # Generic cell boundaries only; no unverified SEI or molecule is drawn.
    ax.add_patch(Rectangle((0.45, 0.95), 1.65, 2.0, facecolor="#d7e1e7", edgecolor="#9eafba", linewidth=1.1))
    ax.add_patch(Rectangle((2.1, 0.95), 2.3, 2.0, facecolor="#e9f2f5", edgecolor=LINE, linewidth=1.1))
    ax.add_patch(Rectangle((4.4, 0.95), 0.55, 2.0, facecolor="#f5f8f9", edgecolor="#a9b9c4", hatch="////", linewidth=1.1))
    ax.add_patch(Rectangle((4.95, 0.95), 2.3, 2.0, facecolor="#f4f1ef", edgecolor=LINE, linewidth=1.1))
    ax.add_patch(Rectangle((7.25, 0.95), 1.65, 2.0, facecolor="#c8d4da", edgecolor="#9eafba", linewidth=1.1))
    for x, y, size in ((5.55, 1.47, .17), (6.1, 2.38, .19), (6.65, 1.78, .14), (5.9, 1.94, .13)):
        ax.add_patch(Circle((x, y), size, facecolor="#b7c5cb", edgecolor="#8ca0a9", linewidth=.7))
    for x, y in ((2.55, 1.7), (3.25, 2.25), (3.75, 1.4), (5.35, 2.35), (6.7, 2.5)):
        ax.add_patch(Circle((x, y), .11, facecolor=BLUE, edgecolor="none", alpha=.75))
    ax.add_patch(FancyArrowPatch((3.9, 3.28), (5.65, 3.28), arrowstyle="-|>", mutation_scale=12,
                                 linewidth=1.4, color=BLUE, connectionstyle="arc3,rad=.05"))
    ax.text(4.5, 3.48, r"Li$^+$", ha="center", va="bottom", fontsize=9.2, color=BLUE)
    for x, label in ((1.27, "Anode"), (3.3, "Electrolyte"), (4.68, "Separator"), (6.15, "Electrolyte"), (8.05, "Cathode")):
        ax.text(x, .54, label, ha="center", va="top", fontsize=8.2, color=MUTED)


def draw() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "pdf.fonttype": 42})
    fig = plt.figure(figsize=(13, 8.2), facecolor="white")
    gs = fig.add_gridspec(3, 4, left=.065, right=.97, top=.94, bottom=.095,
                          height_ratios=[1.06, 1.05, 1.36], hspace=.58, wspace=.72)
    ax_a = fig.add_subplot(gs[0, :2])
    ax_b = fig.add_subplot(gs[0, 2])
    ax_c = fig.add_subplot(gs[0, 3])
    ax_d = fig.add_subplot(gs[1, :2])
    ax_e = fig.add_subplot(gs[1, 2:])
    ax_f = fig.add_subplot(gs[2, :])
    draw_stack(ax_a)

    spectra: dict[str, tuple[list[float], list[float]]] = {"Formulation A": ([], []), "Formulation B": ([], [])}
    with (DATA / "raman-waterfall-synthetic.csv").open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            if row["formulation"] in spectra:
                x, y = spectra[row["formulation"]]
                x.append(float(row["raman_shift_cm_1"]))
                y.append(float(row["offset_intensity_au"]))
    for name, color in (("Formulation A", BLUE), ("Formulation B", CORAL)):
        x, y = spectra[name]
        ax_b.plot(x, y, color=color, linewidth=1.7)
    ax_b.set_xlim(680, 1030)
    ax_b.set_yticks([])
    ax_b.text(.98, .21, "A", color=BLUE, transform=ax_b.transAxes, ha="right", fontsize=8.5)
    ax_b.text(.98, .69, "B", color=CORAL, transform=ax_b.transAxes, ha="right", fontsize=8.5)
    finish(ax_b, r"Raman shift (cm$^{-1}$)", "Offset intensity (a.u.)", "b")

    rdf = numeric("rdf-synthetic.csv")
    ax_c.plot(rdf["r_angstrom"], rdf["pair_A_g_r"], color=BLUE, linewidth=1.7)
    ax_c.plot(rdf["r_angstrom"], rdf["pair_B_g_r"], color=CORAL, linewidth=1.7)
    ax_c.set_xlim(1, 8.5)
    ax_c.set_ylim(bottom=0)
    ax_c.text(.93, .87, "A", color=BLUE, transform=ax_c.transAxes, ha="right", fontsize=8.5)
    ax_c.text(.93, .71, "B", color=CORAL, transform=ax_c.transAxes, ha="right", fontsize=8.5)
    finish(ax_c, r"Distance ($\mathrm{\AA}$)", r"$g(r)$", "c")

    ce = numeric("ce-synthetic.csv")
    ax_d.plot(ce["cycle"], ce["electrolyte_A_CE_percent"], color=BLUE, linewidth=1.55, label="Electrolyte A")
    ax_d.plot(ce["cycle"], ce["electrolyte_B_CE_percent"], color=CORAL, linewidth=1.55, label="Electrolyte B")
    ax_d.set_xlim(1, 300)
    ax_d.set_ylim(92, 100.2)
    ax_d.legend(frameon=False, loc="lower right", fontsize=8, labelcolor=INK, handlelength=2.3)
    finish(ax_d, "Cycle number", "Coulombic efficiency (%)", "d")

    sym = numeric("symmetric-synthetic.csv")
    ax_e.plot(sym["time_h"], sym["electrolyte_A_mV"], color=BLUE, linewidth=.72, alpha=.9)
    ax_e.plot(sym["time_h"], sym["electrolyte_B_mV"], color=CORAL, linewidth=.72, alpha=.9)
    ax_e.set_xlim(0, 240)
    ax_e.set_ylim(-105, 105)
    ax_e.axhline(0, color=LINE, linewidth=.75, zorder=0)
    ax_e.text(.87, .65, "A", color=BLUE, transform=ax_e.transAxes, ha="right", fontsize=8.5)
    ax_e.text(.87, .13, "B", color=CORAL, transform=ax_e.transAxes, ha="right", fontsize=8.5)
    finish(ax_e, "Time (h)", "Cell voltage (mV)", "e")

    full = numeric("full-cell-cycling-synthetic.csv")
    ax_f.plot(full["cycle"], full["electrolyte_A_mAh_g"], color=BLUE, linewidth=2.2)
    ax_f.plot(full["cycle"], full["electrolyte_B_mAh_g"], color=CORAL, linewidth=2.2)
    ax_f.set_xlim(1, 322)
    ax_f.set_ylim(112, 162)
    ax_f.set_xticks([1, 50, 100, 150, 200, 250, 300])
    ax_f.text(306, full["electrolyte_A_mAh_g"][-1], "A", color=BLUE, va="center", fontsize=11, weight="bold")
    ax_f.text(306, full["electrolyte_B_mAh_g"][-1], "B", color=CORAL, va="center", fontsize=11, weight="bold")
    finish(ax_f, "Cycle number", r"Discharge capacity (mAh g$^{-1}$)", "f", label_x=-.025)

    output = HERE / "editorial-assembly-demo"
    fig.savefig(output.with_suffix(".png"), dpi=180, facecolor="white")
    fig.savefig(output.with_suffix(".svg"), facecolor="white")
    fig.savefig(output.with_suffix(".pdf"), facecolor="white")
    # The before/after website illustration uses crops of these exact six
    # panels, so it does not imply that unrelated figures were assembled.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for letter, axis in zip("abcdef", (ax_a, ax_b, ax_c, ax_d, ax_e, ax_f)):
        bounds = axis.get_tightbbox(renderer).transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(HERE / f"editorial-panel-{letter}.png", dpi=180,
                    bbox_inches=bounds.expanded(1.05, 1.08), facecolor="white")
    svg = output.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    metadata = {
        "status": "synthetic test-only layout exercise; not experimental data or one connected study",
        "showcase_eligible": False,
        "panels": {
            "a": "generic battery stack schematic; original geometry",
            "b": "raman-waterfall-synthetic.csv; formulations A and B only; intensities offset",
            "c": "rdf-synthetic.csv",
            "d": "ce-synthetic.csv",
            "e": "symmetric-synthetic.csv",
            "f": "full-cell-cycling-synthetic.csv",
        },
        "purpose": "Demonstrate panel hierarchy, grouping and a full-width performance endpoint; no causal interpretation is licensed.",
        "panel_previews": [f"editorial-panel-{letter}.png" for letter in "abcdef"],
    }
    output.with_suffix(".layout.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Wrote", output.name, "PNG/SVG/PDF and layout metadata")


if __name__ == "__main__":
    draw()
