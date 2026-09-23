"""Build reproducible, explicitly synthetic BatteryReviewForge demonstrations.

Generation writes CSV first. Rendering reads those files back from disk; no
renderer draws directly from a freshly generated in-memory curve. These are
visual and workflow demonstrations, never acquired electrochemical evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np


ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[1] / "docs" / "assets" / "showcase"
SEED = 20260923
VERSION = "1.0"
COLORS = {"A": "#31577d", "B": "#bc4566", "C": "#00857f"}
INK = "#172c40"
MUTED = "#526476"
GRAMMAR = {
    "full_cell": "FULL_PROFILE_01",
    "li_cu_ce": "li_cu_cycle_ce + li_cu_voltage_profile",
    "li_li": "li_li_symmetric + linked_zoom",
    "eis": "nyquist + bode (optional model demonstration)",
    "operando_xrd": "operando_xrd + matched_voltage_trace",
    "tof_sims": "tof_sims_map + same-model_sputter_profile",
    "integrated_study": "same_synthetic_study_cross_validation",
}
CONDITIONS = {
    "full_cell": "Illustrative NMC811||Li; 0.5 C; 2.8–4.3 V; 25 °C; cathode 3 mAh cm−2. These are invented settings, not a test report.",
    "li_cu_ce": "Illustrative Li||Cu repeated plating/stripping; 1 mA cm−2; 1 mAh cm−2 plated; 1 V stripping cutoff; 25 °C.",
    "li_li": "Illustrative Li||Li; ±1 mA cm−2; 1 mAh cm−2 per half-cycle; no rest; 25 °C.",
    "eis": "Illustrative two-electrode model; 100 kHz–10 mHz; Rs + (Rct||CPE) + semi-infinite Warburg. Values have no fitted experimental interpretation.",
    "operando_xrd": "Illustrative angle-by-SOC model with moving and splitting Gaussian peaks; no phase assignment or acquired diffraction.",
    "tof_sims": "Illustrative 20 × 20 µm ion maps at 30 s sputter time; arbitrary intensity, common 0–0.65 display scale; time is not depth.",
    "integrated_study": "One invented A/B electrolyte comparison reuses the source files and identities above; panels do not establish a real mechanism.",
}


def csv_write(path: Path, header: list[str], rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def csv_read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def ar1(rng, count: int, scale: float, rho: float = .82) -> np.ndarray:
    out = np.zeros(count)
    for i in range(1, count):
        out[i] = rho * out[i - 1] + rng.normal(0, scale)
    return out


def generate_full_cell() -> None:
    path = ROOT / "full_cell"
    rng = np.random.default_rng(SEED + 1)
    n = np.arange(1, 501)
    q_a = 180.5 + 3.2 * (1 - np.exp(-(n - 1) / 3.2)) - 12.0 * (n / 500) ** 1.27 - 3.1 * np.maximum((n - 415) / 85, 0) ** 2 + ar1(rng, len(n), .075)
    q_b = 178.5 + 2.7 * (1 - np.exp(-(n - 1) / 4)) - 20.0 * (n / 500) ** 1.20 - 9.5 * np.maximum((n - 385) / 115, 0) ** 2 + ar1(rng, len(n), .095)
    csv_write(path / "data.csv", ["cycle", "A_mAh_g", "B_mAh_g"], zip(n, np.round(q_a, 5), np.round(q_b, 5)))
    profile_rows = []
    for cycle in (1, 100, 300, 500):
        q = float(q_a[cycle - 1])
        for fraction in np.linspace(0, 1, 180):
            voltage = 4.26 - .69 * fraction - .37 * fraction ** 7 - .002 * (cycle / 500)
            profile_rows.append((cycle, round(fraction * q, 6), round(voltage, 6), round(q, 6)))
    csv_write(path / "voltage_profiles.csv", ["cycle", "capacity_mAh_g", "voltage_V", "cycling_endpoint_mAh_g"], profile_rows)


def generate_li_cu() -> None:
    path = ROOT / "li_cu_ce"
    rng = np.random.default_rng(SEED + 2)
    n = np.arange(1, 301)
    a = 99.37 - 1.10 * np.exp(-(n - 1) / 8) - .12 * (n / 300) ** 2 + ar1(rng, len(n), .022)
    b = 99.04 - 1.50 * np.exp(-(n - 1) / 9) - .52 * np.maximum((n - 218) / 82, 0) ** 1.5 + ar1(rng, len(n), .037)
    b[263] -= .47  # A disclosed synthetic excursion; never filtered.
    csv_write(path / "data.csv", ["cycle", "A_ce_pct", "B_ce_pct", "plated_mAh_cm2"], zip(n, np.round(a, 5), np.round(b, 5), np.ones(len(n))))
    rows = []
    for sample, series in (("A", a), ("B", b)):
        for cycle in (1, 100, 300):
            ce = float(series[cycle - 1])
            for stage in ("plate", "strip"):
                endpoint = 1.0 if stage == "plate" else ce / 100
                for fraction in np.linspace(0, 1, 100):
                    interface = .0 if sample == "A" else .020
                    voltage = (-.045 - interface - .028 * np.exp(-fraction / .07) - .018 * fraction) if stage == "plate" else (.045 + interface + .065 * fraction ** 6 + .006 * cycle / 300)
                    rows.append((sample, cycle, stage, round(fraction * endpoint, 7), round(voltage, 6), round(ce, 5)))
    csv_write(path / "profiles.csv", ["sample", "cycle", "stage", "capacity_mAh_cm2", "voltage_V", "cycle_ce_pct"], rows)


def generate_li_li() -> None:
    path = ROOT / "li_li"
    rng = np.random.default_rng(SEED + 3)
    rows = []
    for sample, base in (("A", 34), ("B", 47)):
        drift = ar1(rng, 200, .24)
        for half in range(200):
            direction = 1 if half % 2 == 0 else -1
            polarization = base + (3 if sample == "A" else 10) * (half / 200) ** 1.3 + drift[half]
            for sub in range(50):
                phase = sub / 49
                current = direction * 1.0
                voltage = direction * polarization * (.83 + .17 * (1 - np.exp(-phase / .08)) + .08 * phase ** 4)
                rows.append((sample, round(half + phase, 6), half + 1, round(current, 5), round(phase, 6), round(voltage, 5)))
    csv_write(path / "data.csv", ["sample", "time_h", "half_cycle", "current_mA_cm2", "fraction_of_half_cycle", "voltage_mV"], rows)


def impedance(frequency: np.ndarray, rs: float, rct: float, cpe: float, alpha: float, sigma: float) -> np.ndarray:
    jw = 2j * np.pi * frequency
    return rs + 1 / (1 / rct + cpe * jw ** alpha) + sigma / np.sqrt(jw)


def generate_eis() -> None:
    path = ROOT / "eis"
    frequencies = np.logspace(5, -2, 86)
    rows = []
    for sample, params in (("A", (4.2, 23, .00085, .86, 3.0)), ("B", (5.1, 43, .00067, .83, 4.0))):
        values = impedance(frequencies, *params)
        rows.extend((sample, round(float(f), 8), round(float(z.real), 7), round(float(z.imag), 7)) for f, z in zip(frequencies, values))
    csv_write(path / "data.csv", ["sample", "frequency_Hz", "Zreal_ohm", "Zimag_ohm"], rows)
    (path / "model.json").write_text(json.dumps({"circuit": "Rs + (Rct || CPE) + semi-infinite Warburg", "parameters": {"A": {"Rs_ohm": 4.2, "Rct_ohm": 23, "CPE_Q": .00085, "CPE_alpha": .86, "Warburg_sigma": 3.0}, "B": {"Rs_ohm": 5.1, "Rct_ohm": 43, "CPE_Q": .00067, "CPE_alpha": .83, "Warburg_sigma": 4.0}}, "status": "invented model, not fitted data"}, indent=2) + "\n", encoding="utf-8")


def generate_xrd() -> None:
    path = ROOT / "operando_xrd"
    angles = np.linspace(35.3, 46.7, 240)
    rows = []
    volts = []
    for soc in np.linspace(0, 1, 105):
        p1 = 37.05 + .86 * soc
        p2 = 43.62 - .79 * soc
        split = max((soc - .55) / .45, 0)
        intensity = (.045 + .90 * np.exp(-.5 * ((angles - p1) / .13) ** 2)
                     + .77 * (1 - .36 * split) * np.exp(-.5 * ((angles - p2) / .15) ** 2)
                     + .54 * split * np.exp(-.5 * ((angles - (p2 + .70 * split)) / .12) ** 2))
        rows.extend((round(float(soc), 6), round(float(angle), 6), round(float(value), 7)) for angle, value in zip(angles, intensity))
        volts.append((round(float(soc), 6), round(float(3.20 + .83 * soc + .18 * soc ** 7), 6)))
    csv_write(path / "data.csv", ["soc_fraction", "two_theta_deg", "intensity_au"], rows)
    csv_write(path / "voltage.csv", ["soc_fraction", "voltage_V"], volts)


def generate_tofsims() -> None:
    path = ROOT / "tof_sims"
    coordinates = np.linspace(0, 20, 72)
    xx, yy = np.meshgrid(coordinates, coordinates)
    domain = np.exp(-((xx - 7.2) ** 2 + (yy - 11.4) ** 2) / 15) + .7 * np.exp(-((xx - 15) ** 2 + (yy - 6) ** 2) / 20)
    ring = np.exp(-((np.sqrt((xx - 10) ** 2 + (yy - 10) ** 2) - 7.0) / 2.0) ** 2)
    texture = .085 * (np.sin(xx * 1.2 + yy * .8) + np.sin(xx * .42 - yy * 1.4))
    bases = {"F-": .12 + .72 * ring + .11 * domain + texture, "Li+": .16 + .72 * domain + texture, "S-": .11 + .43 * (1 - np.minimum(domain, 1)) + .32 * np.exp(-((xx - 14) ** 2 + (yy - 15) ** 2) / 13) + texture}
    factors = {"F-": lambda t: .26 + .70 * np.exp(-t / 58), "Li+": lambda t: .22 + .55 * (1 - np.exp(-t / 43)), "S-": lambda t: .18 + .32 * np.exp(-((t - 76) / 43) ** 2)}
    maps = []
    for species, base in bases.items():
        image = np.clip(base * factors[species](30), 0, 1)
        maps.extend((species, 30, round(float(x), 5), round(float(y), 5), round(float(v), 7)) for x, y, v in zip(xx.flat, yy.flat, image.flat))
    csv_write(path / "data.csv", ["species", "sputter_time_s", "x_um", "y_um", "normalized_intensity"], maps)
    depth_rows = []
    for t in np.linspace(0, 180, 100):
        depth_rows.extend((species, round(float(t), 6), round(float(np.clip(base.mean() * factors[species](t), 0, 1)), 7)) for species, base in bases.items())
    csv_write(path / "depth.csv", ["species", "sputter_time_s", "mean_normalized_intensity"], depth_rows)


def generate_integrated() -> None:
    path = ROOT / "integrated_study"
    path.mkdir(exist_ok=True)
    manifest = {"source_study": "single invented A/B electrolyte comparison", "uses": ["../li_cu_ce/data.csv", "../li_cu_ce/profiles.csv", "../li_li/data.csv", "../eis/data.csv", "../full_cell/data.csv", "../full_cell/voltage_profiles.csv"], "identity_rule": "A and B retain the same color and label in every panel", "status": "synthetic_demo; no mechanistic inference"}
    (path / "sources.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    csv_write(path / "data_index.csv", ["sample", "test", "source_csv"], ((sample, test, source) for sample in ("A", "B") for test, source in (("LiCu CE", "../li_cu_ce/data.csv"), ("LiLi", "../li_li/data.csv"), ("EIS", "../eis/data.csv"), ("full cell", "../full_cell/data.csv"))))


GENERATORS = {"full_cell": generate_full_cell, "li_cu_ce": generate_li_cu, "li_li": generate_li_li, "eis": generate_eis, "operando_xrd": generate_xrd, "tof_sims": generate_tofsims, "integrated_study": generate_integrated}


def configure() -> None:
    matplotlib.rcParams.update({"font.family": "Arial", "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold", "mathtext.fallback": "None", "font.size": 6.5, "axes.labelsize": 6.5, "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6, "axes.linewidth": .55, "lines.linewidth": .9, "svg.fonttype": "none", "pdf.fonttype": 42, "savefig.facecolor": "white", "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "axes.edgecolor": INK})


def axis(ax, letter: str) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(direction="out", length=2.2, width=.55, pad=2.2)
    ax.grid(False)
    ax.text(-.09, 1.035, letter, transform=ax.transAxes, fontweight="bold", fontsize=8, va="bottom", ha="right", color=INK)


def arr(rows, field):
    return np.array([float(row[field]) for row in rows])


def plot_full(ax1, ax2, compact=False) -> None:
    rows = csv_read(ROOT / "full_cell" / "data.csv")
    n = arr(rows, "cycle")
    for sample in "AB":
        ax1.plot(n, arr(rows, f"{sample}_mAh_g"), color=COLORS[sample], lw=.95, label=f"Electrolyte {sample}")
    ax1.set(xlabel="Cycle number", ylabel="Discharge capacity (mAh g$^{-1}$)", xlim=(0, 505), ylim=(130, 190))
    ax1.legend(frameon=False, loc="lower left", handlelength=1.7)
    profiles = csv_read(ROOT / "full_cell" / "voltage_profiles.csv")
    for cycle, color in ((1, "#c6d7e6"), (100, "#92b4d0"), (300, "#6389aa"), (500, COLORS["A"])):
        r = [row for row in profiles if int(row["cycle"]) == cycle]
        ax2.plot(arr(r, "capacity_mAh_g"), arr(r, "voltage_V"), color=color, lw=.9, label=str(cycle))
    ax2.set(xlabel="Specific capacity (mAh g$^{-1}$)", ylabel="Voltage (V)", xlim=(0, 190), ylim=(2.95, 4.36))
    ax2.legend(frameon=False, title="Electrolyte A · cycle", title_fontsize=6, ncol=2 if compact else 1, loc="lower left", handlelength=1.3)


def plot_ce(ax1, ax2) -> None:
    rows = csv_read(ROOT / "li_cu_ce" / "data.csv")
    n = arr(rows, "cycle")
    for sample in "AB":
        ax1.plot(n, arr(rows, f"{sample}_ce_pct"), color=COLORS[sample], lw=.75, marker="o", ms=1.45, markevery=5, label=f"Electrolyte {sample}")
    ax1.set(xlabel="Cycle number", ylabel="Coulombic efficiency (%)", xlim=(0, 305), ylim=(96.5, 100.25))
    ax1.legend(frameon=False, loc="lower right", handlelength=1.4)
    profiles = csv_read(ROOT / "li_cu_ce" / "profiles.csv")
    for sample in "AB":
        for cycle in (1, 300):
            r = [row for row in profiles if row["sample"] == sample and int(row["cycle"]) == cycle and row["stage"] == "strip"]
            ax2.plot(arr(r, "capacity_mAh_cm2"), arr(r, "voltage_V") * 1000, color=COLORS[sample], lw=.9, ls="-" if cycle == 300 else (0, (3, 2)), label=f"{sample} · {cycle}")
    ax2.set(xlabel="Stripped capacity (mAh cm$^{-2}$)", ylabel="Voltage (mV)", xlim=(0, 1.02), ylim=(35, 145))
    ax2.legend(frameon=False, ncol=2, loc="upper left", handlelength=1.3)


def plot_symmetric(ax1, ax2) -> None:
    rows = csv_read(ROOT / "li_li" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        ax1.plot(arr(r, "time_h"), arr(r, "voltage_mV"), color=COLORS[sample], lw=.5, label=f"Electrolyte {sample}")
        z = [row for row in r if 101 <= float(row["time_h"]) <= 108]
        ax2.plot(arr(z, "time_h"), arr(z, "voltage_mV"), color=COLORS[sample], lw=.75)
    ax1.set(xlabel="Time (h)", ylabel="Cell voltage (mV)", xlim=(0, 200), ylim=(-90, 90))
    ax2.set(xlabel="Time (h)", ylabel="Cell voltage (mV)", xlim=(101, 108), ylim=(-75, 75))
    ax1.legend(frameon=False, loc="upper right", handlelength=1.4)
    ax1.axvspan(101, 108, color="#dce8ee", zorder=-3)


def plot_eis(ax1, ax2) -> None:
    rows = csv_read(ROOT / "eis" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        zr, zi, freq = arr(r, "Zreal_ohm"), arr(r, "Zimag_ohm"), arr(r, "frequency_Hz")
        ax1.plot(zr, -zi, color=COLORS[sample], lw=.65, marker="o", ms=2.0, markevery=5, label=f"Model {sample}")
        ax2.semilogx(freq, np.degrees(np.arctan2(-zi, zr)), color=COLORS[sample], lw=.95, label=f"Model {sample}")
    ax1.set(xlabel="Z′ (Ω)", ylabel="−Z″ (Ω)", xlim=(0, 76), ylim=(0, 26))
    ax1.set_aspect("equal", adjustable="box")
    ax2.set(xlabel="Frequency (Hz)", ylabel="Phase magnitude (°)", xlim=(.01, 1e5), ylim=(0, 85))
    ax1.legend(frameon=False, loc="upper right", handlelength=1.4)


def plot_eis_nyquist(ax) -> None:
    rows = csv_read(ROOT / "eis" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        ax.plot(arr(r, "Zreal_ohm"), -arr(r, "Zimag_ohm"), color=COLORS[sample], lw=.65, marker="o", ms=1.9, markevery=5, label=sample)
    ax.set(xlabel="Z′ (Ω)", ylabel="−Z″ (Ω)", xlim=(0, 76), ylim=(0, 26))
    ax.set_aspect("equal", adjustable="box")
    ax.legend(frameon=False, loc="upper right", ncol=2, handlelength=1.1)


def plot_xrd(ax1, ax2, fig) -> None:
    rows = csv_read(ROOT / "operando_xrd" / "data.csv")
    soc = np.unique(arr(rows, "soc_fraction"))
    angles = np.unique(arr(rows, "two_theta_deg"))
    values = arr(rows, "intensity_au").reshape(len(soc), len(angles))
    palette = LinearSegmentedColormap.from_list("battery_xrd", ["#f8fbfd", "#dce9ee", "#70a5b0", "#1f536d", "#243c61", "#bc4566"], N=256)
    im = ax1.pcolormesh(angles, soc, values, cmap=palette, shading="auto", vmin=.05, vmax=.88, rasterized=True)
    ax1.set(xlabel="2θ (°)", ylabel="SOC (fraction)", xlim=(35.3, 46.7), ylim=(0, 1))
    voltage = csv_read(ROOT / "operando_xrd" / "voltage.csv")
    ax2.plot(arr(voltage, "voltage_V"), arr(voltage, "soc_fraction"), color=COLORS["B"], lw=1.1)
    ax2.set(xlabel="Voltage (V)", ylabel="SOC (fraction)", xlim=(3.1, 4.3), ylim=(0, 1))
    bar = fig.colorbar(im, ax=ax1, fraction=.035, pad=.025)
    bar.ax.set_ylabel("Intensity (a.u.)", fontsize=6)
    bar.ax.tick_params(labelsize=5.5, width=.5)


def plot_tofsims(axes, fig) -> None:
    maps = csv_read(ROOT / "tof_sims" / "data.csv")
    depth = csv_read(ROOT / "tof_sims" / "depth.csv")
    map_palettes = [LinearSegmentedColormap.from_list("F_map", ["#fff9fb", "#edabc0", COLORS["B"]]), LinearSegmentedColormap.from_list("Li_map", ["#f7fcfb", "#9fd6d0", COLORS["C"]]), LinearSegmentedColormap.from_list("S_map", ["#f8fbfd", "#9fb9ce", COLORS["A"]])]
    channels = {}
    for ax, species, cmap, label in zip(axes[:3], ("F-", "Li+", "S-"), map_palettes, (r"F$^{-}$", r"Li$^{+}$", r"S$^{-}$")):
        r = [row for row in maps if row["species"] == species]
        side = int(np.sqrt(len(r)))
        img = arr(r, "normalized_intensity").reshape(side, side)
        channels[species] = img
        image = ax.imshow(img, origin="lower", extent=(0, 20, 0, 20), cmap=cmap, vmin=0, vmax=.65, interpolation="nearest")
        ax.set(xlabel="x (µm)", ylabel="y (µm)", xlim=(0, 20), ylim=(0, 20))
        ax.text(.96, .94, label, transform=ax.transAxes, ha="right", va="top", color=INK, fontsize=7, weight="bold", bbox={"facecolor": "white", "edgecolor": "none", "alpha": .88, "pad": 1.4})
        bar = fig.colorbar(image, ax=ax, fraction=.047, pad=.018)
        bar.ax.tick_params(labelsize=5.1, width=.5)
        bar.ax.set_ylabel("Norm. intensity", fontsize=5.5)
    f = np.clip(channels["F-"] / .65, 0, 1)
    li = np.clip(channels["Li+"] / .65, 0, 1)
    s = np.clip(channels["S-"] / .65, 0, 1)
    rgb = np.stack((1 - .63 * li - .48 * s, 1 - .57 * f - .48 * s, 1 - .54 * f - .59 * li), axis=-1)
    overlay = axes[3]
    overlay.imshow(np.clip(rgb, 0, 1), origin="lower", extent=(0, 20, 0, 20), interpolation="nearest")
    overlay.set(xlabel="x (µm)", ylabel="y (µm)", xlim=(0, 20), ylim=(0, 20))
    overlay.text(.96, .94, "Overlay", transform=overlay.transAxes, ha="right", va="top", color=INK, fontsize=7, weight="bold", bbox={"facecolor": "white", "edgecolor": "none", "alpha": .88, "pad": 1.4})
    ax = axes[4]
    for species, color, label in (("F-", COLORS["B"], r"F$^{-}$"), ("Li+", COLORS["C"], r"Li$^{+}$"), ("S-", COLORS["A"], r"S$^{-}$")):
        r = [row for row in depth if row["species"] == species]
        ax.plot(arr(r, "sputter_time_s"), arr(r, "mean_normalized_intensity"), color=color, lw=1, label=label)
    ax.axvline(30, color=MUTED, lw=.55, ls=(0, (2, 2)))
    ax.set(xlabel="Sputter time (s)", ylabel="Mean normalized intensity", xlim=(0, 180), ylim=(0, .9))
    ax.legend(frameon=False, loc="upper right", ncol=3, handlelength=1.2)


def figure(name: str):
    configure()
    if name == "full_cell":
        fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 88 / 25.4), gridspec_kw={"width_ratios": [1.55, 1]}, layout="constrained")
        plot_full(*axes)
    elif name == "li_cu_ce":
        fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 88 / 25.4), gridspec_kw={"width_ratios": [1.55, 1]}, layout="constrained")
        plot_ce(*axes)
    elif name == "li_li":
        fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 88 / 25.4), gridspec_kw={"width_ratios": [1.55, 1]}, layout="constrained")
        plot_symmetric(*axes)
    elif name == "eis":
        fig, axes = plt.subplots(2, 1, figsize=(180 / 25.4, 118 / 25.4), gridspec_kw={"height_ratios": [1, .76]}, layout="constrained")
        plot_eis(*axes)
    elif name == "operando_xrd":
        fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 98 / 25.4), gridspec_kw={"width_ratios": [1.95, .75]}, layout="constrained")
        plot_xrd(*axes, fig)
    elif name == "tof_sims":
        fig = plt.figure(figsize=(180 / 25.4, 165 / 25.4), layout="constrained")
        grid = fig.add_gridspec(3, 2, height_ratios=[1, 1, .68])
        axes = [fig.add_subplot(grid[i, j]) for i in range(2) for j in range(2)] + [fig.add_subplot(grid[2, :])]
        plot_tofsims(axes, fig)
    elif name == "integrated_study":
        fig = plt.figure(figsize=(180 / 25.4, 157 / 25.4), layout="constrained")
        grid = fig.add_gridspec(3, 2, width_ratios=[1.35, 1], height_ratios=[1, .9, 1.07])
        axes = [fig.add_subplot(grid[i, j]) for i in range(3) for j in range(2)]
        plot_ce(axes[0], axes[1])
        sym = csv_read(ROOT / "li_li" / "data.csv")
        for sample in "AB":
            r = [row for row in sym if row["sample"] == sample]
            axes[2].plot(arr(r, "time_h"), arr(r, "voltage_mV"), color=COLORS[sample], lw=.46, label=sample)
        axes[2].set(xlabel="Time (h)", ylabel="Cell voltage (mV)", xlim=(0, 200), ylim=(-90, 90))
        plot_eis_nyquist(axes[3])
        plot_full(axes[4], axes[5], compact=True)
        # The shared A/B identity is explicit; no cross-test causality is inferred.
    else:
        raise ValueError(name)
    for letter, ax in zip("abcdef", axes):
        axis(ax, letter)
    return fig


def source_names(name: str) -> list[str]:
    if name == "integrated_study":
        return ["data_index.csv", "sources.json", "../li_cu_ce/data.csv", "../li_cu_ce/profiles.csv", "../li_li/data.csv", "../eis/data.csv", "../full_cell/data.csv", "../full_cell/voltage_profiles.csv"]
    if name == "eis":
        return ["data.csv", "model.json"]
    return sorted(p.name for p in (ROOT / name).glob("*.csv"))


def render(name: str) -> None:
    destination = ROOT / name
    fig = figure(name)
    for suffix in ("svg", "pdf", "png"):
        fig.savefig(destination / f"figure.{suffix}", dpi=300, facecolor="white")
    svg = destination / "figure.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    meta = {"data_status": "synthetic_demo", "not_experimental_data": True, "random_seed": SEED, "generator_version": VERSION, "figure_grammar_id": GRAMMAR[name], "journal_preset": "journal_neutral_180mm", "test_conditions": CONDITIONS[name], "source_files": source_names(name), "creator": "BatteryReviewForge original code", "review": {"science": "models and data-to-panel links inspected; no experimental interpretation", "display": "internal PNG and final-size inspection completed; independent author review remains required"}}
    (destination / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def publish(name: str) -> None:
    target = SITE / name
    target.mkdir(parents=True, exist_ok=True)
    for filename in ("figure.svg", "figure.pdf", "figure.png", "metadata.json", *source_names(name)):
        if filename.startswith("../"):
            continue
        source = ROOT / name / filename
        if source.exists():
            shutil.copy2(source, target / source.name)


def assembly_demo() -> None:
    """Export six independent panels from one synthetic study for the novice exercise."""
    out = ROOT / "assembly_demo"
    out.mkdir(exist_ok=True)
    fig = figure("integrated_study")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axes = fig.axes
    for letter, ax in zip("abcdef", axes):
        bbox = ax.get_tightbbox(renderer).transformed(fig.dpi_scale_trans.inverted()).expanded(1.04, 1.06)
        fig.savefig(out / f"panel-{letter}.png", dpi=220, bbox_inches=bbox, facecolor="white")
    plt.close(fig)
    manifest = {"data_status": "synthetic_demo", "source": "integrated_study", "panels": list("abcdef"), "instruction": "Assemble in reading order a–f; do not add panel subtitles or alter source data."}
    (out / "README.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = SITE / "assembly-demo.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w", ZIP_DEFLATED) as z:
        for file in sorted(out.iterdir()):
            z.write(file, file.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("generate", "render", "publish", "all"))
    parser.add_argument("--name", choices=tuple(GENERATORS))
    args = parser.parse_args()
    names = [args.name] if args.name else list(GENERATORS)
    for name in names:
        folder = ROOT / name
        folder.mkdir(exist_ok=True)
        for filename, action in (("generate_data.py", "generate"), ("plot.py", "render")):
            entrypoint = folder / filename
            if not entrypoint.exists():
                call = f"GENERATORS['{name}']()" if action == "generate" else f"render('{name}')"
                entrypoint.write_text(
                    "\"\"\"Standalone reproducible showcase step.\"\"\"\n"
                    "import sys\nfrom pathlib import Path\n"
                    "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
                    "from build import GENERATORS, render\n"
                    f"if __name__ == '__main__':\n    {call}\n",
                    encoding="utf-8",
                )
    if "integrated_study" in names and args.action in {"all", "render"}:
        # Integrated figure reads the shared study's other source files.
        names = [n for n in GENERATORS if n != "integrated_study"] + ["integrated_study"]
    if args.action in {"generate", "all"}:
        for name in names: GENERATORS[name]()
    if args.action in {"render", "all"}:
        for name in names: render(name)
    if args.action in {"publish", "all"}:
        for name in names: publish(name)
    if not args.name and args.action in {"all", "render"}:
        assembly_demo()
    print(f"{args.action}: {', '.join(names)}")


if __name__ == "__main__":
    main()
