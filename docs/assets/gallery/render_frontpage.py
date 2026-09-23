"""Reproducible, deliberately synthetic front-page electrochemistry examples.

These equations illustrate figure design. They do not simulate or report a cell.
Keep names generic so no particular chemistry is presented as measured evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)
INK = "#173147"
MUTED = "#627383"
BLUE = "#286bb7"
TEAL = "#008f85"
CORAL = "#d65c55"
PALETTE = (CORAL, BLUE, TEAL)
NAMES = ("Reference", "Formulation B", "Formulation C")

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.2,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": "#8295a3",
    "axes.linewidth": 0.8,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "savefig.facecolor": "white",
})


def clean(ax, *, grid=True):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=3.5, width=0.8, labelsize=9.7)
    if grid:
        ax.grid(axis="y", color="#dfe8ed", lw=0.7, zorder=0)
    ax.set_axisbelow(True)


def panel(ax, label):
    ax.text(-0.085, 1.035, label, transform=ax.transAxes, fontsize=15,
            fontweight="bold", color=INK, va="bottom")


def write_csv(name, header, rows):
    with (DATA / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def save(fig, stem, extra):
    for suffix in ("svg", "pdf", "png"):
        fig.savefig(HERE / f"{stem}.{suffix}", dpi=240,
                    bbox_inches="tight", pad_inches=0.16)
    svg = HERE / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    (HERE / f"{stem}.layout.json").write_text(
        json.dumps({
            "status": "synthetic test-only; rejected front-page prototype, no measured cell data",
            "showcase_eligible": False,
            "source": "render_frontpage.py",
            "transformations": "Deterministic equations and seeded small noise; no outlier removal or smoothing",
            "outputs": [f"{stem}.{x}" for x in ("png", "svg", "pdf")],
            **extra,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def full_cell():
    rng = np.random.default_rng(20260923)
    cycles = np.arange(1, 501)
    # Endpoints are illustrative only; all three traces have independent noise.
    endpoints = ((180, 110), (185, 145), (188, 165))
    fig = plt.figure(figsize=(12.4, 5.7), facecolor="white")
    ax = fig.add_axes([0.075, 0.18, 0.59, 0.72])
    profile = fig.add_axes([0.75, 0.18, 0.205, 0.72])
    rows = []
    for index, ((start, end), color, name) in enumerate(zip(endpoints, PALETTE, NAMES)):
        t = (cycles - 1) / 499
        trend = start - (start - end) * (0.15 * t + 0.85 * t**1.58)
        activation = 2.6 * (1 - np.exp(-(cycles - 1) / 13)) * np.exp(-cycles / 105)
        noise = rng.normal(0, 0.54 + 0.10 * index, len(cycles))
        noise = noise - (1 - t) * noise[0] - t * noise[-1]
        capacity = trend + activation + noise
        capacity[0], capacity[-1] = start, end
        rows.extend((name, int(c), round(float(v), 4)) for c, v in zip(cycles, capacity))
        ax.plot(cycles, capacity, color=color, lw=2.15 if index == 2 else 1.65,
                alpha=1 if index == 2 else .88, label=name, zorder=3 + index)
        ax.scatter([500], [capacity[-1]], color=color, s=29, zorder=8, edgecolor="white", lw=.7)
        ax.text(510, capacity[-1], f"{name}  {end}", va="center", ha="left",
                color=color, fontsize=9.5, fontweight="medium")
    clean(ax)
    ax.set(xlim=(0, 655), ylim=(98, 199), xticks=[0, 100, 200, 300, 400, 500],
           yticks=[100, 120, 140, 160, 180], xlabel="Cycle number",
           ylabel="Specific capacity (mAh g$^{-1}$)")
    panel(ax, "a")
    ax.text(.02, .07, "500 cycles", transform=ax.transAxes, color=MUTED,
            fontsize=9.3, va="bottom")

    # Illustrative selected discharge profiles for one named series. The
    # capacity endpoint matches its corresponding synthetic cycling value.
    curve_rows = []
    for cycle, color, alpha in ((1, TEAL, 1), (250, TEAL, .7), (500, TEAL, .47)):
        cap = next(v for n, c, v in rows if n == "Formulation C" and c == cycle)
        q = np.linspace(0, cap, 260)
        frac = q / cap
        voltage = 4.23 - .45 * (1 - np.exp(-frac / .13)) - .18 * frac \
            - .61 / (1 + np.exp(-(frac - .92) / .023)) - .00013 * (cycle - 1)
        profile.plot(q, voltage, color=color, lw=2 if cycle == 1 else 1.5,
                     alpha=alpha, label=f"Cycle {cycle}")
        curve_rows.extend((cycle, round(float(x), 4), round(float(y), 5))
                          for x, y in zip(q, voltage))
    clean(profile)
    profile.set(xlim=(0, 205), ylim=(2.9, 4.35), xticks=[0, 50, 100, 150, 200],
                yticks=[3.0, 3.5, 4.0], xlabel="Specific capacity (mAh g$^{-1}$)",
                ylabel="Voltage (V)")
    profile.legend(loc="lower left", frameon=False, fontsize=8.5,
                   labelspacing=.55, handlelength=2.5)
    panel(profile, "b")
    write_csv("frontpage-full-cell-cycling-synthetic.csv",
              ["formulation", "cycle_number", "specific_capacity_mAh_g"], rows)
    write_csv("frontpage-full-cell-profiles-synthetic.csv",
              ["cycle_number", "specific_capacity_mAh_g", "cell_voltage_V"], curve_rows)
    save(fig, "full-cell-frontpage", {
        "panels": {"a": "500-cycle capacity; three invented formulations",
                   "b": "selected invented discharge profiles; formulation C"},
        "input_csv": ["data/frontpage-full-cell-cycling-synthetic.csv",
                      "data/frontpage-full-cell-profiles-synthetic.csv"],
        "note": "Capacity denominator is illustrative active-material mass; no chemistry, current, loading or temperature is asserted.",
    })


def coulombic_efficiency():
    rng = np.random.default_rng(20260924)
    cycle = np.arange(1, 301)
    targets = (98.47, 99.18, 99.74)
    starts = (94.6, 96.0, 96.8)
    fig = plt.figure(figsize=(12.4, 5.7), facecolor="white")
    ax = fig.add_axes([0.075, 0.18, 0.60, 0.72])
    bx = fig.add_axes([0.77, 0.18, 0.18, 0.72])
    rows = []
    late = []
    for index, (name, color, target, start) in enumerate(zip(NAMES, PALETTE, targets, starts)):
        drift = (start - target) * np.exp(-(cycle - 1) / (17 + 4 * index))
        noise = rng.normal(0, (0.19, 0.14, 0.09)[index], len(cycle))
        noise += .09 * np.sin(cycle * (.20 + index * .025))
        values = np.clip(target + drift + noise, 93, 99.98)
        rows.extend((name, int(c), round(float(v), 5)) for c, v in zip(cycle, values))
        ax.plot(cycle, values, color=color, lw=1.2, alpha=.84, label=name)
        ax.plot(cycle[::12], values[::12], linestyle="none", marker="o",
                color=color, ms=2.3, alpha=.92)
        subset = values[cycle >= 101]
        late.append(subset)
        x = np.full(len(subset), index + 1, dtype=float) + rng.uniform(-.13, .13, len(subset))
        bx.scatter(x[::3], subset[::3], s=6, color=color, alpha=.35, rasterized=False)
        bx.hlines(np.median(subset), index + .72, index + 1.28,
                  color=color, lw=2.7, zorder=5)
    clean(ax)
    ax.set(xlim=(0, 300), ylim=(93.5, 100.2), xticks=[0, 50, 100, 150, 200, 250, 300],
           yticks=[94, 96, 98, 100], xlabel="Cycle number", ylabel="Coulombic efficiency (%)")
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(.98, .04),
              fontsize=9.2, handlelength=2.4)
    panel(ax, "a")
    clean(bx)
    bx.set(xlim=(.5, 3.5), ylim=(97.6, 100.05),
           xticks=[1, 2, 3], xticklabels=["Ref.", "B", "C"],
           yticks=[98, 99, 100], ylabel="Coulombic efficiency (%)")
    bx.tick_params(axis="x", labelsize=9)
    panel(bx, "b")
    bx.text(.02, .04, "Cycles 101–300", transform=bx.transAxes, color=MUTED, fontsize=8.8)
    write_csv("frontpage-li-cu-ce-synthetic.csv",
              ["formulation", "cycle_number", "coulombic_efficiency_percent"], rows)
    save(fig, "ce-frontpage", {
        "panels": {"a": "invented Li||Cu cycling Coulombic efficiency",
                   "b": "individual synthetic values every third cycle and median; cycles 101–300"},
        "input_csv": ["data/frontpage-li-cu-ce-synthetic.csv"],
        "note": "Illustrative Li||Cu workflow only. Current density, capacity per cycle, electrolyte and test setup are not specified; do not compare as experimental performance.",
    })


def nyquist():
    """A complex-impedance model, with model curve and perturbed demo points."""
    rng = np.random.default_rng(20260925)
    freq = np.geomspace(1e5, .2, 400)
    fig = plt.figure(figsize=(12.4, 5.7), facecolor="white")
    ax = fig.add_axes([.075, .16, .55, .75])
    bx = fig.add_axes([.73, .16, .225, .75])
    rows = []
    for name, color, rs, rct, sigma in zip(NAMES, PALETTE,
                                            (3.1, 3.1, 3.1), (23.0, 16.0, 9.0),
                                            (1.45, 1.20, .95)):
        omega = 2 * np.pi * freq
        z = rs + rct / (1 + 1j * omega * rct * 1.7e-4) \
            + sigma * (1 - 1j) / np.sqrt(omega)
        x, y = z.real, -z.imag
        selection = np.linspace(0, len(freq) - 1, 35, dtype=int)
        measured_x = x[selection] + rng.normal(0, .11, len(selection))
        measured_y = y[selection] + rng.normal(0, .11, len(selection))
        ax.plot(x, y, color=color, lw=1.75, label=name)
        ax.scatter(measured_x, measured_y, s=13, facecolor="white",
                   edgecolor=color, lw=.9, zorder=5)
        bx.plot(x, y, color=color, lw=1.5)
        bx.scatter(measured_x, measured_y, s=11, facecolor="white",
                   edgecolor=color, lw=.8, zorder=5)
        rows.extend((name, round(float(f), 6), round(float(a), 5),
                     round(float(b), 5), "model") for f, a, b in zip(freq, x, y))
        rows.extend((name, round(float(freq[i]), 6), round(float(a), 5),
                     round(float(b), 5), "synthetic point")
                    for i, a, b in zip(selection, measured_x, measured_y))
    for axis in (ax, bx):
        clean(axis, grid=False)
        axis.set_aspect("equal", adjustable="box")
        axis.set(xlabel="$Z^\prime$ (Ω)", ylabel="$-Z^{\prime\prime}$ (Ω)")
        axis.axhline(0, color="#b9c8d2", lw=.7, zorder=0)
    ax.set(xlim=(0, 32), ylim=(0, 20), xticks=[0, 10, 20, 30],
           yticks=[0, 5, 10, 15, 20])
    bx.set(xlim=(2.5, 15.5), ylim=(0, 13), xticks=[5, 10, 15], yticks=[0, 5, 10])
    panel(ax, "a")
    panel(bx, "b")
    ax.text(.05, .91, "line  model\nopen circle  synthetic point", transform=ax.transAxes,
            color=MUTED, fontsize=8.5, va="top", linespacing=1.5)
    ax.legend(frameon=False, loc="upper right", fontsize=9.1, handlelength=2.8)
    write_csv("frontpage-eis-synthetic.csv",
              ["formulation", "frequency_Hz", "Z_real_ohm", "minus_Z_imag_ohm", "series"], rows)
    save(fig, "eis-frontpage", {
        "panels": {"a": "Nyquist plot from invented equivalent-circuit parameters",
                   "b": "high-frequency detail; same x/y scale"},
        "input_csv": ["data/frontpage-eis-synthetic.csv"],
        "note": "Line is the generating model, not a fit to empirical points. Circles are seeded perturbations of that model. No measured impedance or validated equivalent circuit is claimed.",
    })


def evidence_matrix():
    """An example of mapping reporting coverage, not actual studies."""
    matrix = np.array([
        [2, 2, 2, 0, 0, 1], [2, 2, 2, 2, 0, 1], [2, 2, 1, 0, 2, 2],
        [2, 1, 2, 2, 0, 0], [2, 2, 2, 0, 2, 1], [1, 2, 2, 2, 2, 2],
        [2, 0, 2, 0, 1, 2], [2, 2, 2, 2, 2, 1], [2, 2, 1, 0, 0, 2],
        [2, 1, 2, 2, 2, 2], [2, 2, 2, 2, 0, 2], [2, 2, 2, 1, 2, 2],
    ])
    fig, ax = plt.subplots(figsize=(12.4, 6.3), facecolor="white")
    fig.subplots_adjust(left=.19, right=.88, top=.89, bottom=.11)
    palette = ListedColormap(["#f0f3f5", "#e6b49b", "#1b777e"])
    ax.imshow(matrix, cmap=palette, vmin=-.5, vmax=2.5, aspect="auto",
              interpolation="nearest")
    ax.set_xticks(range(6), labels=["Cell type", "Loading", "Electrolyte",
                                    "Temperature", "Pressure", "Comparator"])
    ax.set_yticks(range(12), labels=[f"Example {i:02d}" for i in range(1, 13)])
    ax.tick_params(axis="x", length=0, labeltop=True, labelbottom=False, pad=13)
    ax.tick_params(axis="y", length=0, pad=14)
    ax.set_xticks(np.arange(-.5, 6, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 12, 1), minor=True)
    ax.grid(which="minor", color="white", lw=4)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.spines[:].set_visible(False)
    for label, color, y in (("Reported", "#1b777e", .66),
                            ("Partly specified", "#e6b49b", .53),
                            ("Not reported", "#f0f3f5", .40)):
        fig.text(.905, y, "■", color=color, fontsize=17, va="center")
        fig.text(.93, y, label, color=INK, fontsize=9.4, va="center")
    write_csv("frontpage-evidence-matrix-synthetic.csv",
              ["example_source", "field", "status"],
              ((f"Example {i+1:02d}", field, ("not reported", "partly specified", "reported")[int(matrix[i,j])])
               for i in range(12) for j, field in enumerate(
                   ("cell_type", "loading", "electrolyte", "temperature", "pressure", "comparator"))))
    save(fig, "evidence-matrix-frontpage", {
        "panels": {"matrix": "invented reporting-coverage states for 12 fictitious examples"},
        "input_csv": ["data/frontpage-evidence-matrix-synthetic.csv"],
        "note": "Rows are fictitious labels, not real papers. Matrix demonstrates a visual grammar for a verified literature map.",
    })


if __name__ == "__main__":
    full_cell()
    coulombic_efficiency()
    nyquist()
    evidence_matrix()
