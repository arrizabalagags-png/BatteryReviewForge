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
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
from matplotlib.patches import Rectangle, Patch
from matplotlib.transforms import Bbox
import numpy as np


ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[1] / "docs" / "assets" / "showcase"
SEED = 20260923
VERSION = "1.2"
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
    "rate_capability": "rate_capability + selected_rate_profiles",
    "gcd_profiles": "charge_discharge_voltage_capacity_profiles",
    "pouch_thermal": "pouch_surface_temperature + linked_line_and_time",
    "literature_benchmark": "source_linked_comparable_literature_scatter",
    "reporting_matrix": "categorical_reporting_audit",
    "capability_spread": "ten_panel_capability_spread",
    "style_presets": "same_full_cell_data_six_style_choices",
}
CONDITIONS = {
    "full_cell": "Illustrative NMC811||Li; 0.5 C; 2.8–4.3 V; 25 °C; cathode 3 mAh cm−2. These are invented settings, not a test report.",
    "li_cu_ce": "Illustrative Li||Cu repeated plating/stripping; 1 mA cm−2; 1 mAh cm−2 plated; 1 V stripping cutoff; 25 °C.",
    "li_li": "Illustrative Li||Li; ±1 mA cm−2; 1 mAh cm−2 per half-cycle; no rest; 25 °C.",
    "eis": "Illustrative two-electrode model; 100 kHz–10 mHz; Rs + (Rct||CPE) + semi-infinite Warburg. Values have no fitted experimental interpretation.",
    "operando_xrd": "Illustrative angle-by-SOC model with moving and splitting Gaussian peaks; no phase assignment or acquired diffraction.",
    "tof_sims": "Illustrative 20 × 20 µm ion maps at 30 s sputter time; arbitrary intensity, common 0–0.65 display scale; time is not depth.",
    "integrated_study": "One invented A/B electrolyte comparison reuses the source files and identities above; panels do not establish a real mechanism.",
    "rate_capability": "Illustrative NMC811||Li; 0.2/0.5/1/2/5/0.2 C in ten-cycle stages; 2.8–4.3 V; 25 °C. Recovery stage is simulated, not measured.",
    "gcd_profiles": "Illustrative NMC811||Li at 0.5 C, 2.8–4.3 V, 25 °C; cycles 1/100/300/500 share the full-cell capacity state.",
    "pouch_thermal": "Illustrative 100 × 70 mm pouch surface at 2 C and 25 °C ambient; modelled 0–30 min temperature, not an IR measurement.",
    "literature_benchmark": "48 invented Li–S-like records, each at 0.2 C, 25 °C and cycle 100, with one consistent mAh g−1 sulfur basis; IDs are synthetic, never citations.",
    "reporting_matrix": "18 invented study IDs with seven reporting fields; status categories are examples, not an audit of real papers.",
    "capability_spread": "Ten independently labelled synthetic capability panels; shared styles do not imply one experiment across unlike cell and measurement types.",
    "style_presets": "Six presentations of the same synthetic full-cell cycling CSV, with identical axes and values. Colours are selectable house presets, not journal endorsements.",
}
VARIABLES = {
    "full_cell": {"x": "cycle number", "y": "discharge capacity (mAh g−1)", "linked": "voltage (V) vs specific capacity (mAh g−1) at declared cycles"},
    "li_cu_ce": {"x": "cycle number", "y": "cycle-by-cycle CE (%)", "linked": "plating/stripping voltage (V) vs capacity (mAh cm−2)"},
    "li_li": {"x": "time (h)", "y": "symmetric-cell voltage (mV)", "linked": "zoom uses the same time series"},
    "eis": {"x": "Z′ (Ω)", "y": "−Z″ (Ω)", "linked": "frequency (Hz) and phase (°) from one circuit model"},
    "operando_xrd": {"x": "state of charge (%)", "y": "2θ (°)", "linked": "model intensity (a.u.) and voltage (V) on the same SOC axis"},
    "tof_sims": {"x": "lateral position (µm)", "y": "lateral position (µm)", "linked": "ion intensity (a.u.) and sputter time (s), not calibrated depth"},
    "rate_capability": {"x": "cycle number", "y": "discharge capacity (mAh g−1)", "linked": "selected voltage (V) versus capacity (mAh g−1) at measured stages"},
    "gcd_profiles": {"x": "specific capacity (mAh g−1)", "y": "voltage (V)", "linked": "cycle state shared with full-cell demo"},
    "pouch_thermal": {"x": "pouch width (mm)", "y": "pouch height (mm)", "linked": "temperature (°C), same-map line profile, Tmax versus time (min)"},
    "literature_benchmark": {"x": "sulfur loading (mg cm−2)", "y": "capacity at cycle 100 (mAh g−1)", "linked": "48 invented comparable records; category by symbol"},
    "reporting_matrix": {"x": "reporting field", "y": "synthetic study ID", "linked": "reported/partial/NR/NV/NA categorical status"},
    "integrated_study": {"x": "experiment-specific axes", "y": "experiment-specific units", "linked": "six panels from same A/B synthetic study"},
    "capability_spread": {"x": "experiment-specific axes", "y": "experiment-specific units", "linked": "ten panels from explicitly separate demonstration sources"},
    "style_presets": {"x": "cycle number", "y": "discharge capacity (mAh g−1)", "linked": "same synthetic A/B series and axis limits in all six presets"},
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


def generate_rate() -> None:
    path = ROOT / "rate_capability"
    rng = np.random.default_rng(SEED + 8)
    stages = [(0.2, 10), (0.5, 10), (1.0, 10), (2.0, 10), (5.0, 10), (0.2, 10)]
    rows, profiles = [], []
    cycle = 0
    for stage, (rate, count) in enumerate(stages):
        for offset in range(count):
            cycle += 1
            for sample, base, sensitivity in (("A", 185, 13.5), ("B", 181, 18.5)):
                loss = sensitivity * np.log1p(rate / .2) + .038 * cycle
                recovery = 1.2 if stage == 5 else 0.0
                q = base - loss - 1.6 * np.exp(-offset / 1.8) + recovery + rng.normal(0, .26)
                rows.append((cycle, sample, stage + 1, rate, round(float(q), 5)))
                if sample == "A" and cycle in (7, 27, 47, 57):
                    for fraction in np.linspace(0, 1, 160):
                        voltage = 4.23 - .66 * fraction - .38 * fraction ** 7 - .025 * np.log1p(rate)
                        profiles.append((cycle, rate, round(float(fraction * q), 6), round(float(voltage), 6), round(float(q), 6)))
    csv_write(path / "data.csv", ["cycle", "sample", "stage", "discharge_rate_C", "capacity_mAh_g"], rows)
    csv_write(path / "voltage_profiles.csv", ["cycle", "rate_C", "capacity_mAh_g", "voltage_V", "cycling_endpoint_mAh_g"], profiles)


def generate_gcd() -> None:
    path = ROOT / "gcd_profiles"
    cycling = csv_read(ROOT / "full_cell" / "data.csv")
    rows = []
    for cycle in (1, 100, 300, 500):
        endpoint = float(cycling[cycle - 1]["A_mAh_g"])
        for direction in ("charge", "discharge"):
            for fraction in np.linspace(0, 1, 180):
                capacity = fraction * endpoint
                if direction == "discharge":
                    voltage = 4.26 - .69 * fraction - .37 * fraction ** 7 - .002 * cycle / 500
                else:
                    voltage = 3.01 + .62 * fraction + .63 * (1 - np.exp(-fraction / .16)) + .015 * cycle / 500
                rows.append((cycle, direction, round(float(capacity), 6), round(float(voltage), 6), round(endpoint, 6)))
    csv_write(path / "data.csv", ["cycle", "direction", "capacity_mAh_g", "voltage_V", "cycling_endpoint_mAh_g"], rows)


def thermal_field(xx: np.ndarray, yy: np.ndarray, minute: float) -> np.ndarray:
    """Bounded illustrative thermal field; tabs and geometry are separate metadata."""
    rise = 1 - np.exp(-minute / 9.0)
    center = 9.6 * np.exp(-((xx - 52) / 25) ** 2 - ((yy - 35) / 20) ** 2)
    tab = 3.2 * np.exp(-((xx - 18) / 17) ** 2 - ((yy - 65) / 16) ** 2)
    return 25 + rise * (5.5 + center + tab + .40 * np.sin(xx / 15) * np.cos(yy / 12))


def generate_thermal() -> None:
    path = ROOT / "pouch_thermal"
    xs, ys = np.linspace(0, 100, 101), np.linspace(0, 70, 71)
    xx, yy = np.meshgrid(xs, ys)
    final = thermal_field(xx, yy, 30)
    csv_write(path / "data.csv", ["time_min", "x_mm", "y_mm", "surface_temperature_C"],
              ((30, round(float(x), 3), round(float(y), 3), round(float(t), 5))
               for x, y, t in zip(xx.ravel(), yy.ravel(), final.ravel())))
    csv_write(path / "line_profile.csv", ["time_min", "path", "distance_mm", "surface_temperature_C"],
              ((30, "y=35 mm", round(float(x), 3), round(float(t), 5)) for x, t in zip(xs, final[35, :])))
    history = []
    for minute in np.linspace(0, 30, 61):
        field = thermal_field(xx, yy, minute)
        history.append((round(float(minute), 3), round(float(field.max()), 5),
                        round(float(field.min()), 5), round(float(field.mean()), 5)))
    csv_write(path / "history.csv", ["time_min", "Tmax_C", "Tmin_C", "Tmean_C"], history)
    (path / "geometry.json").write_text(json.dumps({"pouch_width_mm": 100, "pouch_height_mm": 70,
        "tabs": [{"name": "+", "x_mm": [12, 25], "y_mm": [70, 76]},
                 {"name": "−", "x_mm": [75, 88], "y_mm": [70, 76]}],
        "surface_model": "illustrative bounded heat field; not a measured thermogram",
        "colorbar_range_C": [25, 45]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate_benchmark() -> None:
    path = ROOT / "literature_benchmark"
    rng = np.random.default_rng(SEED + 9)
    rows = []
    for i in range(48):
        family = ("Porous carbon", "Polar host", "Catalytic host")[i % 3]
        cluster = i // 3
        loading = (1.0 + .07 * cluster) if cluster < 9 else (2.0 + .23 * (cluster - 9))
        loading += rng.normal(0, .11)
        es = np.clip(20 - 2.0 * loading + rng.normal(0, 2.2), 4.5, 22)
        family_offset = {"Porous carbon": -90, "Polar host": 0, "Catalytic host": 85}[family]
        capacity = 1250 - 62 * loading + 7.0 * es + family_offset + rng.normal(0, 65)
        rows.append((f"SIM-{i + 1:03d}", family, round(float(loading), 4),
                     round(float(es), 4), round(float(capacity), 3), 0.2, 100, 25))
    csv_write(path / "data.csv", ["synthetic_id", "host_family", "sulfur_loading_mg_cm2",
        "electrolyte_to_sulfur_uL_mg", "capacity_mAh_g_sulfur", "discharge_rate_C",
        "cycle", "temperature_C"], rows)


REPORT_FIELDS = ("Loading", "E/S", "Rate", "Temp.", "CE protocol", "N/P", "Cell format")
REPORT_STATUS = ("R", "P", "NR", "NV", "NA")


def generate_matrix() -> None:
    path = ROOT / "reporting_matrix"
    rng = np.random.default_rng(SEED + 10)
    rows = []
    for i in range(18):
        paper = f"SIM-{i + 1:03d}"
        for col, field in enumerate(REPORT_FIELDS):
            status = rng.choice(REPORT_STATUS, p=[.48, .18, .20, .10, .04])
            if field == "Cell format":
                status = "R" if i % 3 else "P"
            rows.append((paper, field, str(status)))
    csv_write(path / "data.csv", ["synthetic_id", "field", "status"], rows)
    (path / "status_key.json").write_text(json.dumps({
        "R": "Reported", "P": "Partially reported", "NR": "Not reported",
        "NV": "Not verifiable from supplied source", "NA": "Not applicable by stated review rule",
        "warning": "Synthetic IDs are not DOIs or real papers; missing does not mean zero"},
        indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate_capability() -> None:
    path = ROOT / "capability_spread"
    path.mkdir(exist_ok=True)
    members = ["operando_xrd", "full_cell", "li_cu_ce", "eis", "literature_benchmark",
               "pouch_thermal", "li_li", "rate_capability", "gcd_profiles", "reporting_matrix"]
    csv_write(path / "data_index.csv", ["panel", "source_folder", "evidence_state"],
              zip("abcdefghij", members, ["synthetic_demo"] * len(members)))
    (path / "sources.json").write_text(json.dumps({"members": members,
        "interpretation": "Ten capabilities; unrelated panels are not one experimental study",
        "status": "synthetic_demo"}, indent=2) + "\n", encoding="utf-8")


def generate_styles() -> None:
    path = ROOT / "style_presets"
    path.mkdir(exist_ok=True)
    shutil.copy2(ROOT / "full_cell" / "data.csv", path / "data.csv")
    (path / "source.json").write_text(json.dumps({
        "source": "../full_cell/data.csv", "dataset": "same synthetic A/B full-cell cycling",
        "xlim": [0, 500], "ylim": [130, 190],
        "meaning": "Only colour and strokes vary; values and scales do not."},
        indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


GENERATORS = {"full_cell": generate_full_cell, "li_cu_ce": generate_li_cu, "li_li": generate_li_li,
              "eis": generate_eis, "operando_xrd": generate_xrd, "tof_sims": generate_tofsims,
              "rate_capability": generate_rate, "gcd_profiles": generate_gcd,
              "pouch_thermal": generate_thermal, "literature_benchmark": generate_benchmark,
              "reporting_matrix": generate_matrix, "integrated_study": generate_integrated,
              "capability_spread": generate_capability, "style_presets": generate_styles}


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
    for index, (ax, species, cmap, label) in enumerate(zip(axes[:3], ("F-", "Li+", "S-"), map_palettes, (r"F$^{-}$", r"Li$^{+}$", r"S$^{-}$"))):
        r = [row for row in maps if row["species"] == species]
        side = int(np.sqrt(len(r)))
        img = arr(r, "normalized_intensity").reshape(side, side)
        channels[species] = img
        image = ax.imshow(img, origin="lower", extent=(0, 20, 0, 20), cmap=cmap, vmin=0, vmax=.65, interpolation="nearest")
        ax.set(xlabel="x (µm)", ylabel="y (µm)", xlim=(0, 20), ylim=(0, 20))
        if index:
            ax.set_ylabel("")
            ax.set_yticks([])
        ax.text(.96, .94, label, transform=ax.transAxes, ha="right", va="top", color=INK, fontsize=7, weight="bold", bbox={"facecolor": "white", "edgecolor": "none", "alpha": .88, "pad": 1.4})
        cax = fig.add_axes([(.07, .29, .51)[index] + .185, .54, .006, .36])
        bar = fig.colorbar(image, cax=cax)
        bar.ax.set_yticks([])
    fig.text(.07, .445, "Ion-map intensity: normalized 0–0.65; common numeric range", fontsize=6, color=MUTED)
    f = np.clip(channels["F-"] / .65, 0, 1)
    li = np.clip(channels["Li+"] / .65, 0, 1)
    s = np.clip(channels["S-"] / .65, 0, 1)
    rgb = np.stack((1 - .63 * li - .48 * s, 1 - .57 * f - .48 * s, 1 - .54 * f - .59 * li), axis=-1)
    overlay = axes[3]
    overlay.imshow(np.clip(rgb, 0, 1), origin="lower", extent=(0, 20, 0, 20), interpolation="nearest")
    overlay.set(xlabel="x (µm)", ylabel="y (µm)", xlim=(0, 20), ylim=(0, 20))
    overlay.set_ylabel("")
    overlay.set_yticks([])
    overlay.text(.96, .94, "Overlay", transform=overlay.transAxes, ha="right", va="top", color=INK, fontsize=7, weight="bold", bbox={"facecolor": "white", "edgecolor": "none", "alpha": .88, "pad": 1.4})
    ax = axes[4]
    for species, color, label in (("F-", COLORS["B"], r"F$^{-}$"), ("Li+", COLORS["C"], r"Li$^{+}$"), ("S-", COLORS["A"], r"S$^{-}$")):
        r = [row for row in depth if row["species"] == species]
        ax.plot(arr(r, "sputter_time_s"), arr(r, "mean_normalized_intensity"), color=color, lw=1, label=label)
    ax.axvline(30, color=MUTED, lw=.55, ls=(0, (2, 2)))
    ax.set(xlabel="Sputter time (s)", ylabel="Mean normalized intensity", xlim=(0, 180), ylim=(0, .9))
    ax.legend(frameon=False, loc="upper right", ncol=3, handlelength=1.2)


def plot_rate(ax1, ax2) -> None:
    rows = csv_read(ROOT / "rate_capability" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        ax1.plot(arr(r, "cycle"), arr(r, "capacity_mAh_g"), color=COLORS[sample],
                 marker="o", ms=2, lw=.8, label=f"Electrolyte {sample}")
    for boundary in (10.5, 20.5, 30.5, 40.5, 50.5):
        ax1.axvline(boundary, color="#ccd4dc", lw=.5)
    for x, label in zip((5.5, 15.5, 25.5, 35.5, 45.5, 55.5),
                        ("0.2 C", "0.5 C", "1 C", "2 C", "5 C", "0.2 C")):
        ax1.text(x, 182, label, ha="center", va="top", fontsize=5.7, color=MUTED)
    ax1.set(xlabel="Cycle number", ylabel="Discharge capacity (mAh g$^{-1}$)",
            xlim=(0, 61), ylim=(105, 185))
    ax1.legend(frameon=False, loc="lower left")
    profiles = csv_read(ROOT / "rate_capability" / "voltage_profiles.csv")
    for cycle, shade in ((7, "#a2bacd"), (27, "#668aa8"), (47, COLORS["A"]), (57, COLORS["C"])):
        r = [row for row in profiles if int(row["cycle"]) == cycle]
        ax2.plot(arr(r, "capacity_mAh_g"), arr(r, "voltage_V"), color=shade, lw=.9,
                 label=f"{r[0]['rate_C']} C · cycle {cycle}")
    ax2.set(xlabel="Specific capacity (mAh g$^{-1}$)", ylabel="Voltage (V)",
            xlim=(0, 185), ylim=(2.9, 4.35))
    ax2.legend(frameon=False, loc="lower left", fontsize=5.4, handlelength=1.1)


def plot_gcd(ax, compact=False) -> None:
    rows = csv_read(ROOT / "gcd_profiles" / "data.csv")
    shades = {1: "#b6cadd", 100: "#88abc8", 300: "#5d83a4", 500: COLORS["A"]}
    for cycle in ((300,) if compact else (1, 100, 300, 500)):
        for direction in ("discharge", "charge"):
            r = [row for row in rows if int(row["cycle"]) == cycle and row["direction"] == direction]
            ax.plot(arr(r, "capacity_mAh_g"), arr(r, "voltage_V"), color=shades[cycle],
                    lw=.9, ls="-" if direction == "discharge" else (0, (3, 2)),
                    label=f"Cycle {cycle}" if direction == "discharge" else None)
    ax.set(xlabel="Specific capacity (mAh g$^{-1}$)", ylabel="Voltage (V)",
           xlim=(0, 190), ylim=(2.85, 4.37))
    if compact:
        ax.text(.98, .04, "Cycle 300 · solid/discharge · dashed/charge",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=4.5, color=MUTED)
    else:
        ax.legend(frameon=False, loc="lower left", ncol=2, fontsize=5.7)
        ax.text(.98, .04, "solid: discharge    dashed: charge", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=5.5, color=MUTED)


def plot_thermal(axes, fig) -> None:
    map_ax, line_ax, history_ax = axes
    rows = csv_read(ROOT / "pouch_thermal" / "data.csv")
    image = arr(rows, "surface_temperature_C").reshape(71, 101)
    cmap = LinearSegmentedColormap.from_list("pouch_heat", ["#e9f3f5", "#a8cfd4", "#e9c2a9", "#bb5870", "#6b2948"])
    im = map_ax.imshow(image, origin="lower", extent=(0, 100, 0, 70), cmap=cmap,
                       vmin=25, vmax=45, interpolation="nearest", aspect="equal")
    map_ax.add_patch(Rectangle((0, 0), 100, 70, fill=False, edgecolor=INK, lw=.9))
    for x, sign in ((12, "+"), (75, "−")):
        map_ax.add_patch(Rectangle((x, 70), 13, 5, facecolor="#b9c4cb", edgecolor=INK, lw=.6))
        map_ax.text(x + 6.5, 72.5, sign, ha="center", va="center", fontsize=6, color=INK)
    map_ax.axhline(35, color="white", lw=.7, ls=(0, (4, 2)))
    map_ax.set(xlabel="Pouch width (mm)", ylabel="Pouch height (mm)",
               xlim=(0, 100), ylim=(0, 76))
    bar = fig.colorbar(im, ax=map_ax, fraction=.036, pad=.028)
    bar.ax.set_ylabel("Surface temperature (°C)", fontsize=6)
    bar.ax.tick_params(labelsize=5.5, width=.5)
    line = csv_read(ROOT / "pouch_thermal" / "line_profile.csv")
    line_ax.plot(arr(line, "distance_mm"), arr(line, "surface_temperature_C"),
                 color=COLORS["B"], lw=1.0)
    line_ax.set(xlabel="Position across pouch (mm)", ylabel="Temperature (°C)",
                xlim=(0, 100), ylim=(25, 44))
    history = csv_read(ROOT / "pouch_thermal" / "history.csv")
    history_ax.plot(arr(history, "time_min"), arr(history, "Tmax_C"),
                    color=COLORS["B"], lw=.95, label="Maximum")
    history_ax.plot(arr(history, "time_min"), arr(history, "Tmean_C"),
                    color=COLORS["A"], lw=.95, label="Surface mean")
    history_ax.set(xlabel="Time (min)", ylabel="Temperature (°C)",
                   xlim=(0, 30), ylim=(24, 44))
    history_ax.legend(frameon=False, loc="lower right", fontsize=5.7)


def plot_benchmark(ax, fig, compact=False) -> None:
    rows = csv_read(ROOT / "literature_benchmark" / "data.csv")
    shapes = {"Porous carbon": "o", "Polar host": "s", "Catalytic host": "^"}
    for family, marker in shapes.items():
        r = [row for row in rows if row["host_family"] == family]
        tone = {"Porous carbon": COLORS["A"], "Polar host": COLORS["C"],
                "Catalytic host": COLORS["B"]}[family]
        points = ax.scatter(arr(r, "sulfur_loading_mg_cm2"), arr(r, "capacity_mAh_g_sulfur"),
            c=tone if compact else arr(r, "electrolyte_to_sulfur_uL_mg"),
            cmap=None if compact else "viridis", vmin=None if compact else 4,
            vmax=None if compact else 22,
            s=15 if compact else 25, marker=marker, edgecolor=INK, linewidth=.25, label=family)
    ax.set(xlabel="Sulfur loading (mg cm$^{-2}$)",
           ylabel="Capacity at cycle 100 (mAh g$^{-1}_{S}$)", xlim=(.6, 4.1), ylim=(700, 1550))
    ax.legend(frameon=False, loc="lower left", fontsize=5.5, handletextpad=.2)
    if not compact:
        bar = fig.colorbar(points, ax=ax, fraction=.035, pad=.02)
        bar.ax.set_ylabel("E/S (µL mg$^{-1}$)", fontsize=6)
        bar.ax.tick_params(labelsize=5.5)


def plot_matrix(ax, compact=False) -> None:
    rows = csv_read(ROOT / "reporting_matrix" / "data.csv")
    labels = [f"SIM-{i:03d}" for i in range(1, 11 if compact else 19)]
    lookup = {(r["synthetic_id"], r["field"]): r["status"] for r in rows}
    values = np.array([[REPORT_STATUS.index(lookup[(paper, field)]) for field in REPORT_FIELDS]
                       for paper in labels])
    palette = ["#267d77", "#9cc8c2", "#e4e7e9", "#8b94a4", "#ffffff"]
    cmap = ListedColormap(palette)
    ax.imshow(values, cmap=cmap, norm=BoundaryNorm(np.arange(-.5, 5.5), 5),
              aspect="auto", interpolation="nearest")
    ax.set_xticks(range(len(REPORT_FIELDS)), REPORT_FIELDS, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)), labels, fontsize=4.2 if compact else 5.2)
    ax.set_xticks(np.arange(-.5, 7, 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", lw=.55)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(which="major", length=0)
    ax.set_xlabel("Reported test information")
    if not compact:
        patches = [Patch(facecolor=c, edgecolor=INK if k == "NA" else "none", lw=.35,
                         label=k) for k, c in zip(REPORT_STATUS, palette)]
        ax.legend(handles=patches, frameon=False, ncol=5, bbox_to_anchor=(0, 1.01),
                  loc="lower left", fontsize=5.7, handlelength=.9, columnspacing=.7)


def compact_capability_figure():
    """Ten independent capabilities on one shared physical-size ruler."""
    configure()
    fig = plt.figure(figsize=(300 / 25.4, 142 / 25.4))
    grid = fig.add_gridspec(2, 5, left=.068, right=.975, bottom=.145, top=.94,
                           wspace=.58, hspace=.52)
    axes = [fig.add_subplot(grid[i, j]) for i in range(2) for j in range(5)]
    xrd = csv_read(ROOT / "operando_xrd" / "data.csv")
    soc = sorted({float(row["soc_fraction"]) for row in xrd})
    angle = sorted({float(row["two_theta_deg"]) for row in xrd})
    intensity = arr(xrd, "intensity_au").reshape(len(soc), len(angle))
    axes[0].imshow(intensity.T, origin="lower", aspect="auto", extent=(0, 100, min(angle), max(angle)), cmap="magma", rasterized=True)
    axes[0].set(xlabel="SOC (%)", ylabel=r"2θ (°)")
    full = csv_read(ROOT / "full_cell" / "data.csv")
    ce = csv_read(ROOT / "li_cu_ce" / "data.csv")
    eis = csv_read(ROOT / "eis" / "data.csv")
    for sample in "AB":
        axes[1].plot(arr(full, "cycle"), arr(full, f"{sample}_mAh_g"), color=COLORS[sample], lw=.8)
        axes[2].plot(arr(ce, "cycle"), arr(ce, f"{sample}_ce_pct"), color=COLORS[sample], lw=.75)
        r = [row for row in eis if row["sample"] == sample]
        axes[3].plot(arr(r, "Zreal_ohm"), -arr(r, "Zimag_ohm"), color=COLORS[sample], lw=.65)
    axes[1].set(xlabel="Cycle number", ylabel="Capacity (mAh g$^{-1}$)", xlim=(0, 500), ylim=(130, 190))
    axes[2].set(xlabel="Cycle number", ylabel="Li‖Cu CE (%)", xlim=(0, 300), ylim=(96.5, 100.2))
    axes[3].set(xlabel="Z′ (Ω)", ylabel="−Z″ (Ω)", xlim=(0, 76), ylim=(0, 60))
    plot_benchmark(axes[4], fig, compact=True)
    history = csv_read(ROOT / "pouch_thermal" / "history.csv")
    axes[5].plot(arr(history, "time_min"), arr(history, "Tmax_C"), color=COLORS["B"], lw=.8)
    axes[5].plot(arr(history, "time_min"), arr(history, "Tmean_C"), color=COLORS["A"], lw=.8)
    axes[5].set(xlabel="Time (min)", ylabel="Temperature (°C)")
    sym = csv_read(ROOT / "li_li" / "data.csv")
    for sample in "AB":
        r = [row for row in sym if row["sample"] == sample and 101 <= float(row["time_h"]) <= 108]
        axes[6].plot(arr(r, "time_h"), arr(r, "voltage_mV"), color=COLORS[sample], lw=.65)
    axes[6].set(xlabel="Time (h)", ylabel="Li‖Li voltage (mV)", xlim=(101, 108), ylim=(-75, 75))
    rate = csv_read(ROOT / "rate_capability" / "data.csv")
    for sample in "AB":
        r = [row for row in rate if row["sample"] == sample]
        axes[7].plot(arr(r, "cycle"), arr(r, "capacity_mAh_g"), color=COLORS[sample], lw=.65, marker="o", ms=1.5)
    axes[7].set(xlabel="Cycle number", ylabel="Capacity (mAh g$^{-1}$)", xlim=(0, 61), ylim=(105, 185))
    plot_gcd(axes[8], compact=True)
    plot_matrix(axes[9], compact=True)
    for letter, ax in zip("abcdefghij", axes):
        axis(ax, letter)
        ax.tick_params(labelsize=5.2)
        ax.xaxis.label.set_size(5.8)
        ax.yaxis.label.set_size(5.8)
    fig._capability_axes = dict(zip("abcdefghij", axes))
    return fig


def style_presets_figure():
    """Same CSV and scales across six selectable visual treatments."""
    configure()
    themes = json.loads((ROOT.parents[1] / "skills" / "battery-review-figure" / "assets" / "figure_theme.json").read_text(encoding="utf-8"))["presets"]
    rows = csv_read(ROOT / "style_presets" / "data.csv")
    n = arr(rows, "cycle")
    fig, axes = plt.subplots(2, 3, figsize=(270 / 25.4, 133 / 25.4))
    fig.subplots_adjust(left=.072, right=.983, bottom=.12, top=.9, wspace=.36, hspace=.62)
    for ax, (key, theme) in zip(axes.flat, themes.items()):
        first, second = theme["series"][:2]
        for sample, colour, line in (("A", first, "-"), ("B", second, "--")):
            ax.plot(n, arr(rows, f"{sample}_mAh_g"), color=colour, lw=.9, ls=line, label=sample)
        ax.set(xlim=(0, 500), ylim=(130, 190), xlabel="Cycle number", ylabel="Capacity (mAh g$^{-1}$)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(False)
        ax.tick_params(direction="out", length=2, width=.55, labelsize=5.8)
        ax.set_title(theme["label_en"], fontsize=9, fontweight="bold", loc="left", pad=12, color=INK)
        ax.plot([0, 1], [1.07, 1.07], transform=ax.transAxes, color=first, lw=4, clip_on=False)
        ax.plot([.52, 1], [1.07, 1.07], transform=ax.transAxes, color=second, lw=4, clip_on=False)
        ax.legend(frameon=False, loc="upper right", ncol=2, fontsize=6)
    return fig


def figure(name: str):
    configure()
    if name == "capability_spread":
        return compact_capability_figure()
    if name == "style_presets":
        return style_presets_figure()
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
        fig = plt.figure(figsize=(180 / 25.4, 91 / 25.4))
        axes = [fig.add_axes([x, .54, .18, .36]) for x in (.07, .29, .51, .73)]
        axes.append(fig.add_axes([.07, .13, .845, .29]))
        plot_tofsims(axes, fig)
    elif name == "rate_capability":
        fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 92 / 25.4),
                                 gridspec_kw={"width_ratios": [1.5, 1]}, layout="constrained")
        plot_rate(*axes)
    elif name == "gcd_profiles":
        fig, ax = plt.subplots(figsize=(180 / 25.4, 100 / 25.4), layout="constrained")
        plot_gcd(ax)
        axes = [ax]
    elif name == "pouch_thermal":
        fig = plt.figure(figsize=(180 / 25.4, 101 / 25.4))
        axes = [fig.add_axes([.105, .49, .36, .40]), fig.add_axes([.61, .49, .32, .40]),
                fig.add_axes([.105, .12, .825, .23])]
        plot_thermal(axes, fig)
    elif name == "literature_benchmark":
        fig, ax = plt.subplots(figsize=(180 / 25.4, 105 / 25.4), layout="constrained")
        plot_benchmark(ax, fig)
        axes = [ax]
    elif name == "reporting_matrix":
        fig, ax = plt.subplots(figsize=(180 / 25.4, 122 / 25.4), layout="constrained")
        plot_matrix(ax)
        axes = [ax]
    elif name == "integrated_study":
        fig = plt.figure(figsize=(180 / 25.4, 157 / 25.4), layout="constrained")
        grid = fig.add_gridspec(3, 2, width_ratios=[1.35, 1], height_ratios=[1, .61, 1.07])
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
    for letter, ax in zip("abcdefghijklmnopqrstuvwxyz", axes):
        axis(ax, letter)
    if name == "integrated_study":
        # Constrained layout can center an equal-aspect image inside a taller
        # grid cell. Freeze the final layout, then match the *rendered axes*.
        fig.canvas.draw()
        fig.set_layout_engine(None)
        source = axes[3].get_position()
        target = axes[2].get_position()
        axes[2].set_position([target.x0, source.y0, target.width, source.height])
        fig.canvas.draw()
    return fig


def ruler_audit(name: str, fig) -> dict:
    """Check rendered plot edges in physical units before publishing samples."""
    fig.canvas.draw()
    if name == "capability_spread":
        width_mm, height_mm = fig.get_size_inches() * 25.4
        rects = {letter: obj.get_position().bounds for letter, obj in fig._capability_axes.items()}
        comparisons = []
        for row in ("abcde", "fghij"):
            comparisons += [(row[0], other, "row") for other in row[1:]]
        comparisons += [(upper, lower, "column") for upper, lower in zip("abcde", "fghij")]
        checks = []
        for first, second, direction in comparisons:
            a, b = rects[first], rects[second]
            if direction == "row":
                fields = (("top", a[1] + a[3], b[1] + b[3], height_mm),
                          ("bottom", a[1], b[1], height_mm), ("height", a[3], b[3], height_mm))
            else:
                fields = (("left", a[0], b[0], width_mm),
                          ("right", a[0] + a[2], b[0] + b[2], width_mm),
                          ("width", a[2], b[2], width_mm))
            for edge, av, bv, scale in fields:
                delta = abs(av - bv) * scale * 72 / 25.4
                checks.append({"panels": [first, second], "direction": direction,
                               "edge": edge, "delta_pt": round(float(delta), 4),
                               "pass": bool(delta <= 1.5)})
        failures = [item for item in checks if not item["pass"]]
        return {"figure": name, "tolerance_pt": 1.5,
                "status": "fix_before_publish" if failures else "pass",
                "checks": checks, "failures": failures,
                "plot_rectangles_mm": [
                    {"panel": letter, "left": round(box[0] * width_mm, 3),
                     "top": round((1 - box[1] - box[3]) * height_mm, 3),
                     "width": round(box[2] * width_mm, 3),
                     "height": round(box[3] * height_mm, 3)} for letter, box in rects.items()],
                "note": "All ten plot rectangles measured after final draw on one 2-by-5 physical-size grid."}
    ax = fig.axes
    rows = {"full_cell": [(0, 1)], "li_cu_ce": [(0, 1)],
            "li_li": [(0, 1)], "operando_xrd": [(0, 1)],
            "rate_capability": [(0, 1)],
            "integrated_study": [(0, 1), (2, 3), (4, 5)],
            "tof_sims": [(0, 1), (1, 2), (2, 3)]}.get(name, [])
    columns = {"integrated_study": [(0, 2), (2, 4), (1, 3), (3, 5)]}.get(name, [])
    bounds = [axis.get_position().bounds for axis in ax]
    width_mm, height_mm = fig.get_size_inches() * 25.4
    checks = []
    for direction, pairs, edges in (("row", rows, ("top", "bottom", "height")),
                                    ("column", columns, ("left", "right", "width"))):
        for first, second in pairs:
            a, b = bounds[first], bounds[second]
            if direction == "row":
                values = ((a[1] + a[3], b[1] + b[3], height_mm),
                          (a[1], b[1], height_mm), (a[3], b[3], height_mm))
            else:
                values = ((a[0], b[0], width_mm),
                          (a[0] + a[2], b[0] + b[2], width_mm),
                          (a[2], b[2], width_mm))
            for edge, (av, bv, scale) in zip(edges, values):
                delta_pt = abs(av - bv) * scale * 72 / 25.4
                checks.append({"panels": ["abcdef"[first], "abcdef"[second]],
                               "direction": direction, "edge": edge,
                               "delta_pt": round(float(delta_pt), 3), "pass": bool(delta_pt <= 1.5)})
    failures = [c for c in checks if not c["pass"]]
    letters = "abcdefghijklmnopqrstuvwxyz"
    return {"figure": name, "tolerance_pt": 1.5,
            "status": "fix_before_publish" if failures else ("pass" if checks else "independent_panels"),
            "checks": checks, "failures": failures,
            "plot_rectangles_mm": [
                {"panel": letters[i], "left": round(x * width_mm, 3),
                 "top": round((1 - y - h) * height_mm, 3),
                 "width": round(w * width_mm, 3), "height": round(h * height_mm, 3)}
                for i, (x, y, w, h) in enumerate(bounds[:len(letters)])],
            "note": "Measured after final Matplotlib draw. Colorbars are excluded."}


def source_names(name: str) -> list[str]:
    if name == "style_presets":
        return ["data.csv", "source.json"]
    if name == "integrated_study":
        return ["data_index.csv", "sources.json", "../li_cu_ce/data.csv", "../li_cu_ce/profiles.csv", "../li_li/data.csv", "../eis/data.csv", "../full_cell/data.csv", "../full_cell/voltage_profiles.csv"]
    if name == "eis":
        return ["data.csv", "model.json"]
    if name == "pouch_thermal":
        return ["data.csv", "line_profile.csv", "history.csv", "geometry.json"]
    if name == "reporting_matrix":
        return ["data.csv", "status_key.json"]
    if name == "capability_spread":
        return ["data_index.csv", "sources.json"]
    return sorted(p.name for p in (ROOT / name).glob("*.csv"))


def render(name: str) -> None:
    destination = ROOT / name
    fig = figure(name)
    ruler = ruler_audit(name, fig)
    (destination / "alignment.json").write_text(json.dumps(ruler, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if ruler["failures"]:
        plt.close(fig)
        raise ValueError(f"{name}: rendered panel edges exceed 1.5 pt: {ruler['failures']}")
    for suffix in ("svg", "pdf", "png"):
        fig.savefig(destination / f"figure.{suffix}", dpi=300, facecolor="white")
    if name == "style_presets":
        themes = json.loads((ROOT.parents[1] / "skills" / "battery-review-figure" / "assets" / "figure_theme.json").read_text(encoding="utf-8"))["presets"]
        for ax, (key, theme) in zip(fig.axes, themes.items()):
            one = plt.figure(figsize=(112 / 25.4, 65 / 25.4))
            target = one.add_axes([.12, .17, .82, .65])
            for original in ax.lines[:2]:
                target.plot(original.get_xdata(), original.get_ydata(), color=original.get_color(),
                            lw=.95, ls=original.get_linestyle(), label=original.get_label())
            target.set(xlim=(0, 500), ylim=(130, 190), xlabel="Cycle number", ylabel="Capacity (mAh g$^{-1}$)")
            target.spines[["top", "right"]].set_visible(False)
            target.grid(False)
            target.tick_params(direction="out", length=2, width=.55, labelsize=6)
            target.legend(frameon=False, loc="upper right", ncol=2, fontsize=6)
            for suffix in ("svg", "pdf", "png"):
                one.savefig(destination / f"style_{key}.{suffix}", dpi=300, facecolor="white")
            plt.close(one)
    svg = destination / "figure.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    meta = {"data_status": "synthetic_demo", "not_experimental_data": True, "random_seed": SEED, "generator_version": VERSION, "figure_grammar_id": GRAMMAR[name], "journal_preset": "six selectable presets" if name == "style_presets" else "journal_neutral_180mm", "variables_and_units": VARIABLES[name], "sample_identity": "A/B are invented formulations; SIM IDs are invented studies; colors retain their assigned identity within each panel group.", "test_conditions": CONDITIONS[name], "source_files": source_names(name), "creator": "BatteryReviewForge original code", "review": {"science": "models and data-to-panel links inspected; no experimental interpretation", "display": "internal PNG and final-size inspection completed; independent author review remains required"}}
    (destination / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def publish(name: str) -> None:
    target = SITE / name
    target.mkdir(parents=True, exist_ok=True)
    for filename in ("figure.svg", "figure.pdf", "figure.png", "metadata.json", "alignment.json", *source_names(name)):
        if filename.startswith("../"):
            continue
        source = ROOT / name / filename
        if source.exists():
            shutil.copy2(source, target / source.name)
    if name == "style_presets":
        for source in (ROOT / name).glob("style_*.*"):
            if source.suffix in {".svg", ".pdf", ".png"}:
                shutil.copy2(source, target / source.name)


def assembly_demo() -> None:
    """Export six aligned panels and a strict, reproducible assembly example."""
    out = ROOT / "assembly_demo"
    out.mkdir(exist_ok=True)
    fig = figure("integrated_study")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axes = fig.axes
    figw, figh = fig.get_size_inches()
    tight = [ax.get_tightbbox(renderer).transformed(fig.dpi_scale_trans.inverted()) for ax in axes[:6]]
    pad = .045  # inches; all crop boundaries remain shared by row or column
    x_ranges = [(min(tight[i].x0 for i in ids) - pad,
                 max(tight[i].x1 for i in ids) + pad) for ids in ((0, 2, 4), (1, 3, 5))]
    y_ranges = [(min(tight[i].y0 for i in ids) - pad,
                 max(tight[i].y1 for i in ids) + pad) for ids in ((0, 1), (2, 3), (4, 5))]
    widths = [high - low for low, high in x_ranges]
    scale_mm_per_in = (180 - 8 - 2) / sum(widths)
    rows_mm = [(high - low) * scale_mm_per_in for low, high in y_ranges]
    roles = ("Li||Cu cycling CE", "Li||Cu voltage profiles",
             "Li||Li symmetric cycling", "EIS Nyquist",
             "full-cell cycling", "selected full-cell voltage profiles")
    panels = []
    for i, (letter, ax) in enumerate(zip("abcdef", axes[:6])):
        row, col = divmod(i, 2)
        xlo, xhi = x_ranges[col]
        ylo, yhi = y_ranges[row]
        crop = Bbox.from_extents(xlo, ylo, xhi, yhi)
        fig.savefig(out / f"panel-{letter}.png", dpi=400, bbox_inches=crop,
                    pad_inches=0, facecolor="white")
        box = ax.get_position().bounds
        left = (box[0] * figw - xlo) / (xhi - xlo)
        right = ((box[0] + box[2]) * figw - xlo) / (xhi - xlo)
        top = (yhi - (box[1] + box[3]) * figh) / (yhi - ylo)
        bottom = (yhi - box[1] * figh) / (yhi - ylo)
        panels.append({"label": letter, "path": f"panel-{letter}.png",
                       "row": row, "col": col, "role": roles[i],
                       "source_id": "SYNTHETIC-DEMO-SHARED-STUDY",
                       "rights_status": "original", "alignment_intent": "compare",
                       "alignment_group": "shared-axes-ruler",
                       "plot_box_fraction": [round(v, 7) for v in (left, top, right, bottom)]})
    plt.close(fig)
    manifest = {"version": 1, "figure_id": "Synthetic assembly exercise",
                "claim": "A shared synthetic A/B study illustrates six electrochemical panel roles; no experimental claim.",
                "width_mm": 180, "margin_mm": 4, "gutter_mm": 2,
                "label_band_mm": 0, "draw_labels": False,
                "row_heights_mm": [round(v, 5) for v in rows_mm],
                "col_weights": [round(v, 6) for v in widths],
                "dpi": 300, "min_effective_dpi": 300, "panels": panels}
    manifest_path = out / "figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    script = ROOT.parents[1] / "skills" / "battery-figure-assemble" / "scripts" / "compose_figure.py"
    subprocess.run([sys.executable, str(script), "compose", "--manifest", str(manifest_path),
                    "--out", str(out / "assembled-example"), "--strict"], check=True)
    shutil.copy2(out / "assembled-example.png", SITE / "assembly-example.png")
    shutil.copy2(out / "assembled-example.pdf", SITE / "assembly-example.pdf")
    readme = {"data_status": "synthetic_demo", "source": "integrated_study",
              "panels": list("abcdef"), "instruction": "Assemble a–f without panel subtitles or data changes.",
              "ready_manifest": "figure_manifest.json",
              "alignment_report": "assembled-example.qa.json",
              "note": "Panel crops use common column x-rulers and row y-rulers; measured plot boxes are recorded in the manifest."}
    (out / "README.json").write_text(json.dumps(readme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = SITE / "assembly-demo.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w", ZIP_DEFLATED) as z:
        for file in sorted(out.iterdir()):
            if file.suffix not in {".png", ".pdf", ".json"} or file.name.endswith(".alignment.png"):
                continue
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
