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
sys.path.insert(0, str(ROOT.parents[1] / 'skills' / 'voltpeer-plot' / 'scripts'))
from batteryplot.series_policy import apply_series_policy, check_series_policy
SITE = ROOT.parents[1] / "docs" / "assets" / "showcase"
SEED = 20260923
VERSION = "1.6"
sys.path.insert(0, str(ROOT.parents[1] / 'examples/recipe_packs/_runtime'))
from generate_demo import (inventory_cycles, halfcell_cycles, fullcell_voltage, symmetric_rc_rows,
                           bragg_angle, scientific_basis as recipe_scientific_basis,
                           reference, GAMRY, CE_CAUTION, LI_PROTOCOL, BRAGG)
HALFCELL_PARAMETERS = {
    "A": {"initial_capacity": 184, "activation_fraction": .012, "activation_cycles": 3,
          "fade_per_cycle": .00012, "late_fade_per_cycle2": .000002, "late_fade_start": 350,
          "steady_ce_loss": .0006, "transient_ce_loss": .004, "ce_decay_cycles": 4},
    "B": {"initial_capacity": 182, "activation_fraction": .018, "activation_cycles": 4,
          "fade_per_cycle": .00024, "late_fade_per_cycle2": .0000035, "late_fade_start": 350,
          "steady_ce_loss": .001, "transient_ce_loss": .006, "ce_decay_cycles": 4},
}
SYMMETRIC_PARAMETERS = {
    "A": {"Rs_ohm_cm2": 10, "Rp_ohm_cm2": 24, "tau_h": .08},
    "B": {"Rs_ohm_cm2": 12, "Rp_ohm_cm2": 35, "tau_h": .12},
}
EIS_PARAMETERS = {
    "A": {"Rs_ohm": 4.2, "Rct_ohm": 23, "CPE_Q": .00085, "CPE_alpha": .86, "Warburg_sigma": 3.0},
    "B": {"Rs_ohm": 5.1, "Rct_ohm": 43, "CPE_Q": .00067, "CPE_alpha": .83, "Warburg_sigma": 4.0},
}
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
    "integrated_study": "independent_model_assembly; no experimental cross-validation",
    "rate_capability": "rate_capability + selected_rate_profiles",
    "gcd_profiles": "charge_discharge_voltage_capacity_profiles",
    "pouch_thermal": "pouch_surface_temperature + linked_line_and_time",
    "literature_benchmark": "invented_record_layout_scatter; not actual literature benchmarking",
    "reporting_matrix": "categorical_reporting_audit",
    "capability_spread": "ten_panel_capability_spread",
    "style_presets": "same_full_cell_data_six_style_choices",
}
CONDITIONS = {
    "full_cell": "Illustrative NMC811||Li half-cell; 0.5 C; 2.8–4.3 V; 25 °C; cathode 3 mAh cm−2. These are invented settings, not a test report.",
    "li_cu_ce": "Illustrative Li||Cu repeated plating/stripping; 1 mA cm−2; 1 mAh cm−2 plated; 1 V stripping cutoff; 25 °C.",
    "li_li": "Illustrative Li||Li; ±1 mA cm−2; 1 mAh cm−2 per half-cycle; no rest; 25 °C.",
    "eis": "Illustrative two-electrode model; 100 kHz–10 mHz; Rs + (CPE || (Rct + semi-infinite Warburg)); Z_W = sigma*(1-j)/sqrt(2*pi*f). Values have no fitted experimental interpretation.",
    "operando_xrd": "Original synthetic cubic host: (111)/(200) derive from one lattice a(t); Cu Kα-equivalent wavelength 1.5406 Å; 180 mA g−1 for 3600 s; same charge/time/occupation ledger and assumed voltage; no acquired diffraction or material identity.",
    "tof_sims": "Original synthetic 20 × 20 µm secondary-ion signal fields at 30 s sputter time; F−/S− negative-mode and Li+ positive-mode channels are separate hypothetical acquisitions. Relative a.u. signal, not concentration; sputter time has no depth calibration.",
    "integrated_study": "Independent analytic teaching models reuse the source files above; A/B labels are local to each technique and do not establish cross-technique evidence.",
    "rate_capability": "Illustrative NMC811||Li half-cell; 0.2/0.5/1/2/5/0.2 C in ten-cycle stages; 2.8–4.3 V; 25 °C. Recovery stage is simulated, not measured.",
    "gcd_profiles": "Illustrative NMC811||Li half-cell at 0.5 C, 2.8–4.3 V, 25 °C; cycles 1/100/300/500 share the NMC811||Li half-cell capacity state.",
    "pouch_thermal": "Independent thermal nodes over a 100 × 70 mm rectangular display, 25 °C ambient, total heat capacity 90 J K−1 and conductance 1/6 W K−1; no IR measurement or heating inferred from a C-rate.",
    "literature_benchmark": "48 invented Li–S-like records, each at 0.2 C, 25 °C and cycle 100, with one consistent mAh g−1 sulfur basis; IDs are synthetic, never citations.",
    "reporting_matrix": "18 invented study IDs with seven reporting fields; status categories are examples, not an audit of real papers.",
    "capability_spread": "Ten independently labelled synthetic capability panels; shared styles do not imply one experiment across unlike cell and measurement types.",
    "style_presets": "Six presentations of the same synthetic NMC811||Li half-cell cycling CSV, with identical axes and values. Colours are selectable house presets, not journal endorsements.",
}
VARIABLES = {
    "full_cell": {"x": "cycle number", "y": "discharge capacity (mAh g−1)", "linked": "voltage (V) vs specific capacity (mAh g−1) at declared cycles"},
    "li_cu_ce": {"x": "cycle number", "y": "cycle-by-cycle CE (%)", "linked": "plating/stripping voltage (V) vs capacity (mAh cm−2)"},
    "li_li": {"x": "time (h)", "y": "symmetric-cell voltage (mV)", "linked": "zoom uses the same time series"},
    "eis": {"x": "Z′ (Ω)", "y": "−Z″ (Ω)", "linked": "frequency (Hz) and phase (°) from one circuit model"},
    "operando_xrd": {"x": "2θ (°); λ=1.5406 Å", "y": "time (h)", "linked": "same-time voltage (V), assumed charge occupation and cubic (111)/(200) peaks; model is synthetic, not measured SOC"},
    "tof_sims": {"x": "lateral position (µm)", "y": "lateral position (µm)", "linked": "ion intensity (a.u.) and sputter time (s), not calibrated depth"},
    "rate_capability": {"x": "cycle number", "y": "discharge capacity (mAh g−1)", "linked": "selected voltage (V) versus capacity (mAh g−1) at declared teaching stages"},
    "gcd_profiles": {"x": "specific capacity (mAh g−1)", "y": "voltage (V)", "linked": "cycle state shared with NMC811||Li half-cell demo"},
    "pouch_thermal": {"x": "pouch width (mm)", "y": "pouch height (mm)", "linked": "temperature (°C), same-map line profile, Tmax versus time (min)"},
    "literature_benchmark": {"x": "sulfur loading (mg cm−2)", "y": "capacity at cycle 100 (mAh g−1)", "linked": "48 invented comparable records; category by symbol"},
    "reporting_matrix": {"x": "reporting field", "y": "synthetic study ID", "linked": "reported/partial/NR/NV/NA categorical status"},
    "integrated_study": {"x": "model-specific axes", "y": "model-specific units", "linked": "six panels assembled from independent models; local A/B labels are not one shared study"},
    "capability_spread": {"x": "experiment-specific axes", "y": "experiment-specific units", "linked": "ten panels from explicitly separate demonstration sources"},
    "style_presets": {"x": "cycle number", "y": "discharge capacity (mAh g−1)", "linked": "same synthetic A/B series and axis limits in all six presets"},
}


def showcase_scientific_basis(name: str) -> dict:
    """Physical teaching assumptions or explicit non-physical layout fixture."""
    if name == 'operando_xrd':
        return {'schema_version':1,'model_class':'analytic_model','data_origin':'original_synthetic',
            'parameter_origin':'independently chosen teaching inputs, no fitted material or copied paper values',
            'equations':['Q(t)=I*t/3600; x(t)=Q(t)/Qhost; I=180 mA/g, Qhost=180 mAh/g, 0<=t<=3600 s',
                'a(x)=4.16*(1-0.012*x) Å; d_hkl=a/sqrt(h²+k²+l²); hkl=(111),(200)',
                '2theta=2*asin(lambda/(2d)); lambda=1.5406 Å',
                'I(2theta,t)=background+sum A_hkl*exp[-0.5*((2theta-two_theta_hkl(t))/sigma_hkl)²]',
                'V(t)=3.20+0.83*x(t)+0.18*x(t)^7 (declared phenomenological voltage, not derived from crystal energy)'],
            'parameters':{'wavelength_A':1.5406,'lattice_a0_A':4.16,'fractional_lattice_change_at_x1':-.012,
                'hkl':[[1,1,1],[2,0,0]],'sigma_deg':[.13,.15],'amplitudes_au':[.9,.77],'background_au':.045,
                'current_mA_g':180,'host_capacity_mAh_g':180,'duration_s':3600},
            'assumptions':['One fictitious cubic host, shared lattice at each timestamp; no independent peak motion.',
                'The legacy soc_fraction field stores assumed site progress derived from the declared current ledger; no measured SOC.',
                'Time, occupation, peak positions and voltage use the same recorded timestamps.',
                'Gaussian line profiles and assumed voltage are teaching specializations; no instrument or chemical fit.'],
            'references':[reference('https://www.nature.com/articles/s41467-022-33931-4',
                'On the nanoscale structural evolution of solid discharge products in lithium-sulfur batteries using operando scattering',
                'Figure 2e–g and Methods support pairing scattering/time with electrochemical records and separately inspecting peak width/strain. No Li-S phase, measured point or material parameter is transferred.'),
                reference('https://iupac.org/wp-content/uploads/2019/05/IUPAC-GB3-2012-2ndPrinting-PDFsearchable.pdf',
                    'IUPAC Green Book, third edition',
                    'Section 2.8 defines reciprocal crystal geometry; cubic d_hkl and first-order Bragg specialization are independently calculated.')],
            'limitations':['No phase identification, lattice refinement, measured SOC, operando acquisition or experimental voltage fit.',
                'Peak intensity is arbitrary signal; its amplitude is not a phase fraction or concentration.'],
            'validation_scope':'Common-lattice Bragg identities, finite nonnegative signals and exact time/charge/voltage indexing; no material validation.'}
    if name in {"li_li", "operando_xrd"}:
        basis = recipe_scientific_basis(name)
        if name == "li_li":
            basis["parameters"].update(half_cycles=200)
        else:
            basis["parameters"] = {"wavelength_A": 1.5406, "d1_initial_A": 2.425, "d2_initial_A": 2.075,
                                   "strain1_at_p1": -.022, "strain2_at_p1": .018,
                                   "sigma_deg": [.13, .15], "amplitudes_au": [.9, .77], "background_au": .045}
            basis["equations"][1] = "d1(p)=2.425*(1-0.022*p) A; d2(p)=2.075*(1+0.018*p) A"
            basis["equations"][-1] = "V(p)=3.20+0.83*p+0.18*p^7"
            basis["assumptions"].append("Legacy soc_fraction field stores display progress, not measured state of charge.")
        return basis
    basis = {"schema_version": 1, "model_class": "phenomenological_model",
             "data_origin": "original_synthetic", "parameter_origin": "self-chosen teaching values; never paper measurements",
             "validation_scope": "Declared teaching model; no experimental/material certification"}
    if name == "full_cell":
        basis.update(equations=["a_n=(1-a0*exp(-(n-1)/tau_a))*exp(-k*(n-1)-k_late*max(n-n_late,0)^2)",
                                "Qdis_n=Q0*a_n; eta_n=1-l_ss-l_tr*exp(-(n-1)/tau_CE)",
                                "Qchg_n=Qdis_n/eta_n; CE_n=100*Qdis_n/Qchg_n; side_charge_n=Qchg_n-Qdis_n",
                                "s(f)=0.55*f+0.45*f^7; Vdis=4.3-1.5*s(f); Vchg=2.8+1.5*s(f)"],
                     assumptions=["Excess lithium counterelectrode remains available; no finite Li inventory bottleneck is imposed.",
                                  "Accessible cathode activity and external coulombic loss are separate chosen functions.",
                                  "The active fraction is a positive phenomenological display law, not a fitted NMC811 mechanism; CE products cannot predict this capacity.",
                                  "Specific capacity uses cathode active-material mass; voltage endpoints respect the declared window."],
                     parameters={"count_cycles": 500, **HALFCELL_PARAMETERS, "voltage_window_V": [2.8, 4.3]},
                     references=[reference(CE_CAUTION, "Deciphering coulombic loss in lithium-ion batteries and beyond",
                                           "Coulombic loss, electrode compensation and capacity fade are distinct; does not provide the numerical activity model."),
                                 reference(LI_PROTOCOL, "Understanding and applying coulombic efficiency in lithium metal batteries",
                                           "Excess-Li half-cell versus full-cell interpretation boundaries; all demo values are original.")],
                     limitations=["No NMC811 material performance, cycle-life forecast, electrode mechanism or lithium reservoir mass is inferred.",
                                  "Legacy resource_id full_cell is retained for file compatibility; this gallery example is a half-cell, not the full-cell recipe."])
    elif name == "li_cu_ce":
        basis.update(equations=["CE=100*Qstrip/Qplate; Qplate=abs(jplate)*tplate; Qstrip=abs(jstrip)*tstrip",
                                "eta_A=0.9945-0.012*exp(-(n-1)/8)-0.0008*(n/300)^2",
                                "eta_B=0.991-0.018*exp(-(n-1)/9)-0.004*max((n-218)/82,0)^1.5; eta_B(n=264)-=0.0047",
                                "Vstrip=b+(1-b)*f^12; b=0.045+sample_offset+0.006*n/300; end Vstrip=1 V"],
                     assumptions=["Chosen recoverable-charge fractions; excess Li counterelectrode so CE is not full-cell retention.",
                                  "Negative applied current is plating; positive is stripping; cutoff is reached at the CE-derived endpoint.",
                                  "Voltage is a display relation, not a fitted nucleation, SEI or depletion mechanism."],
                     parameters={"j_mA_cm2": 1, "Qplate_mAh_cm2": 1, "cutoff_V": 1, "cycles": 300,
                                 "sample_offset_V": {"A": 0, "B": .020}},
                     references=[reference(LI_PROTOCOL, "Understanding and applying coulombic efficiency in lithium metal batteries",
                                           "CE charge accounting and protocol/cell-configuration boundaries; not the source of demo numbers.")],
                     limitations=["Cannot infer dead Li versus electrolyte consumption, dendrites, full-cell life or a material benefit."])
    elif name == "eis":
        basis.update(model_class="analytic_model",
                     equations=["omega=2*pi*f; ZW=sigma*(1-j)/sqrt(omega)",
                                "Y_CPE=Q*(j*omega)^alpha",
                                "Z=Rs+1/(Y_CPE+1/(Rct+ZW))",
                                "Nyquist=(Re Z,-Im Z); Bode=(abs(Z),arg(Z)) from the same stored complex values"],
                     assumptions=["Linear small-signal stationary passive circuit, f>0, Rs>=0, Rct/Q>0, 0<alpha<=1, sigma>=0.",
                                  "Semi-infinite planar diffusion is an assumed boundary; finite diffusion or nonstationary spectra require another model.",
                                  "CPE is empirical; its Q with units S*s^alpha is not a measured capacitance unless alpha=1."],
                     parameters={"frequency_Hz": [1e-2, 1e5], **EIS_PARAMETERS},
                     references=[reference(GAMRY, "Basics of Electrochemical Impedance Spectroscopy",
                                           "Complex impedance, series/parallel Randles topology, CPE and semi-infinite Warburg conventions; numbers self-chosen.")],
                     limitations=["No circuit fit, experimental validation, transport coefficient or microscopic mechanism."])
    elif name in {"integrated_study", "capability_spread", "style_presets", "gcd_profiles"}:
        members = {"integrated_study": ["li_cu_ce", "li_li", "eis", "full_cell"],
                   "capability_spread": ["li_cu_ce", "li_li", "eis", "full_cell", "rate_capability", "gcd_profiles",
                                         "operando_xrd", "literature_benchmark", "pouch_thermal", "reporting_matrix"],
                   "style_presets": ["full_cell"], "gcd_profiles": ["full_cell"]}[name]
        basis.update(model_class="composite", dependency_ids=members,
                     equations=["Inherited source equations; read scientific_basis of the declared dependency IDs."],
                     assumptions=["Reusing a color or label does not make independent models one experimental study.",
                                  "GCD charge and discharge endpoints use their own charge ledger; styles change no data."],
                     parameters={"source_files": source_names(name)},
                     references=[reference(CE_CAUTION, "Deciphering coulombic loss in lithium-ion batteries and beyond",
                                           "Charge/retention interpretation boundary only; component physics is in dependency records.")],
                     limitations=["Layout/style linking does not establish cross-technique corroboration or causality."])
    elif name == "rate_capability":
        basis.update(equations=["inventory_n=Q0*exp(-k*n)",
                                "Qaccessible_n=inventory_n/(1+(rate_C/r_limit_C)^0.8)",
                                "Voltage uses the declared bounded 2.8..4.3 V display shape."],
                     assumptions=["Separate reversible rate-accessible fraction and irreversible inventory decrease.",
                                  "Both functions are chosen phenomenological responses, not a measured or universal rate law."],
                     parameters={"A": {"Q0_mAh_g": 185, "k_per_cycle": .0004, "r_limit_C": 12},
                                 "B": {"Q0_mAh_g": 181, "k_per_cycle": .0006, "r_limit_C": 9},
                                 "stages_C": [.2, .5, 1, 2, 5, .2], "cycles_per_stage": 10},
                     references=[reference(CE_CAUTION, "Deciphering coulombic loss in lithium-ion batteries and beyond",
                                           "Inventory loss and measured available capacity need separate assumptions; chosen rate response is not a paper fit.")],
                     limitations=["No transport constant, rate capability of a named cathode or full-cell life forecast."])
    elif name == "pouch_thermal":
        basis.update(model_class="analytic_model",
                     equations=["Cnode*dT/dt=Pnode(x,y)-Gnode*(T-Tamb); T(x,y,0)=Tamb",
                                "T=Tamb+(P/Gnode)*(1-exp(-t/tau)); tau=Cnode/Gnode",
                                "Each equally weighted node has Cnode=Ctotal/N and Gnode=Gtotal/N; Ctotal=m*cp=90 J/K; Gtotal=1/6 W/K; tau=540 s",
                                "P/Gnode=5.5+9.6*Gaussian_center+3.2*Gaussian_tab+0.40*sin(x/15)*cos(y/12) K"],
                     assumptions=["Independent uncoupled thermal nodes, constant positive heating and thermal conductance.",
                                  "Spatial heating distribution is a chosen positive function, not a solved pouch conduction problem."],
                     parameters={"Tamb_C": 25, "tau_min": 9, "total_mass_kg": .10,
                                 "specific_heat_J_kg_K": 900, "Gtotal_W_K": 1/6, "Ctotal_J_K": 90,
                                 "geometry_mm": [100, 70]},
                     references=[reference("https://openstax.org/books/university-physics-volume-2/pages/1-4-heat-transfer-specific-heat-and-calorimetry",
                                           "OpenStax University Physics: Heat Transfer, Specific Heat, and Calorimetry",
                                           "Heat capacity and energy balance; demo node geometry and powers are self-chosen."),
                                 reference("https://openstax.org/books/university-physics-volume-2/pages/1-6-mechanisms-of-heat-transfer",
                                           "OpenStax University Physics: Mechanisms of Heat Transfer",
                                           "Linear thermal conductance interpretation; no experimental cell parameters copied.")],
                     limitations=["No IR measurement, cell electrical-to-heat mapping, lateral coupling, thermal-runaway prediction or inferred 2 C heating."])
    elif name == "tof_sims":
        basis.update(model_class="layout_fixture",
                     equations=["Nonnegative chosen lateral fields times declared sputter-time functions; not an ion-yield or composition law."],
                     assumptions=["F− and S− are hypothetical negative-mode channels; Li+ is a separate positive-mode acquisition; no simultaneous cross-mode quantitative overlay.",
                                  "Species labels are ion channels, not elemental concentration, compound abundance or SEI proof.",
                                  "Sputter time is not depth; matrix-dependent ion yield, crater-depth and sputter-rate calibration are absent."],
                     parameters={"geometry_um": [20, 20], "map_sputter_time_s": 30, "intensity_unit": "relative a.u."},
                     references=[reference("https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication427.pdf",
                                           "NIST/NBS SP 427: Secondary ion mass spectrometry",
                                           "Matrix-dependent secondary-ion yields and empirical calibration limits; arbitrary demonstration signals are not calibrated concentrations."),
                                 reference('https://www.nature.com/articles/s41467-025-58110-z',
                                           'Dynamic doping and interphase stabilization for cobalt-free and high-voltage Lithium metal batteries',
                                           'Figure 4 supports the role of ion-channel/depth-profile evidence only; none of its pixels, chemical assignments or signal values are copied.')],
                     limitations=["Original signal-field demonstration, no physical ion-yield fit, elemental concentration or chemical composition.",
                                  "No calibrated depth, 3D volume concentration, cross-mode quantitative co-location or inferred interphase mechanism."])
    elif name in {"literature_benchmark", "reporting_matrix"}:
        basis.update(model_class="layout_fixture",
                     equations=["No physical equations; categorical/scatter fixtures only."],
                     assumptions=["SIM IDs are invented and are never citations or source-supported performance claims."],
                     parameters={"seed": SEED, "source_files": source_names(name)},
                     references=[reference("https://www.nature.com/nchem/editorial-policies/reporting-standards",
                                           "Nature Chemistry: reporting standards and availability of data, materials, code and protocols",
                                           "Why source provenance/reporting are required; fixture values and categories are invented, not audited papers.")],
                     limitations=["No real literature benchmarking, material ranking or evidence audit."])
    else:
        raise ValueError("Unknown scientific basis: " + name)
    return basis


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
    # Legacy folder ID; actual cell type is NMC811||Li HALF-cell. Excess Li
    # and independently chosen active-capacity fade must not inherit the
    # full-cell recipe's restrictive finite-inventory CE product model.
    ledgers = {sample: halfcell_cycles(count=500, **p)
               for sample, p in HALFCELL_PARAMETERS.items()}
    rows = []
    for index in range(500):
        a, b = ledgers["A"][index], ledgers["B"][index]
        rows.append((index + 1, a["discharge"], b["discharge"], a["charge"], b["charge"],
                     a["ce_pct"], b["ce_pct"], a["lost"], b["lost"]))
    csv_write(path / "data.csv", ["cycle", "A_mAh_g", "B_mAh_g", "A_charge_mAh_g", "B_charge_mAh_g",
                                  "A_ce_pct", "B_ce_pct", "A_loss_mAh_g", "B_loss_mAh_g"], rows)
    profile_rows = []
    for cycle in (1, 100, 300, 500):
        q = ledgers["A"][cycle - 1]["discharge"]
        for fraction in np.linspace(0, 1, 180):
            profile_rows.append((cycle, float(fraction * q), fullcell_voltage(float(fraction), low=2.8, high=4.3), q))
    csv_write(path / "voltage_profiles.csv",
              ["cycle", "capacity_mAh_g", "voltage_V", "cycling_endpoint_mAh_g"], profile_rows)


def generate_li_cu() -> None:
    path = ROOT / "li_cu_ce"
    n = np.arange(1, 301)
    # A declared phenomenological recoverable-charge fraction, not a fitted
    # electrolyte claim. Protocol accounting defines the CE denominator.
    a = .9945 - .012 * np.exp(-(n - 1) / 8) - .0008 * (n / 300) ** 2
    b = .9910 - .018 * np.exp(-(n - 1) / 9) - .004 * np.maximum((n - 218) / 82, 0) ** 1.5
    b[263] -= .0047  # Explicit model excursion, retained without filtering.
    csv_write(path / "data.csv", ["cycle", "A_ce_pct", "B_ce_pct", "plated_mAh_cm2",
                                  "A_stripped_mAh_cm2", "B_stripped_mAh_cm2"],
              zip(n, 100 * a, 100 * b, np.ones(len(n)), a, b))
    rows = []
    for sample, series in (("A", a), ("B", b)):
        for cycle in (1, 100, 300):
            ce = 100 * float(series[cycle - 1])
            for stage in ("plate", "strip"):
                endpoint = 1.0 if stage == "plate" else ce / 100
                current = -1.0 if stage == "plate" else 1.0  # mA cm^-2
                for fraction in np.linspace(0, 1, 100):
                    baseline = .045 + (.020 if sample == "B" else 0) + .006 * cycle / 300
                    voltage = (-baseline - .028 * np.exp(-fraction / .07) - .018 * fraction
                               if stage == "plate" else baseline + (1 - baseline) * fraction ** 12)
                    # Q=abs(j)*t in each stage; stripping reaches the declared
                    # 1 V cutoff at the exact CE-linked recovered endpoint.
                    capacity = float(fraction * endpoint)
                    rows.append((sample, cycle, stage, capacity, float(voltage), ce,
                                 capacity / abs(current), current))
    csv_write(path / "profiles.csv", ["sample", "cycle", "stage", "capacity_mAh_cm2",
                                      "voltage_V", "cycle_ce_pct", "stage_time_h", "current_mA_cm2"], rows)


def generate_li_li() -> None:
    rows = []
    for sample, parameters in SYMMETRIC_PARAMETERS.items():
        trace = symmetric_rc_rows(sample, 200, 50, 1, 1, parameters["Rs_ohm_cm2"],
                                  parameters["Rp_ohm_cm2"], parameters["tau_h"])
        rows.extend((r["sample"], r["time_h"], r["half_cycle"], r["current_mA_cm2"],
                     r["fraction_of_half_cycle"], r["voltage_mV"], r["polarization_mV"],
                     r["passed_in_half_mAh_cm2"], r["cumulative_signed_mAh_cm2"]) for r in trace)
    csv_write(ROOT / "li_li" / "data.csv",
              ["sample", "time_h", "half_cycle", "current_mA_cm2", "fraction_of_half_cycle",
               "voltage_mV", "polarization_mV", "passed_in_half_mAh_cm2", "cumulative_signed_mAh_cm2"], rows)


def impedance(frequency: np.ndarray, rs: float, rct: float, cpe: float, alpha: float, sigma: float) -> np.ndarray:
    # Diffusion belongs to the faradaic branch, not a second unrelated curve.
    frequency = np.asarray(frequency, dtype=float)
    if (np.any(~np.isfinite(frequency)) or np.any(frequency <= 0)
            or not all(np.isfinite(x) for x in (rs, rct, cpe, alpha, sigma))
            or rs < 0 or rct <= 0 or cpe <= 0 or not 0 < alpha <= 1 or sigma < 0):
        raise ValueError("Passive Randles model requires f>0, Rs>=0, Rct/Q>0, 0<alpha<=1, sigma>=0.")
    omega = 2 * np.pi * frequency
    warburg = sigma * (1 - 1j) / np.sqrt(omega)
    return rs + 1 / (cpe * (1j * omega) ** alpha + 1 / (rct + warburg))


def eis_model():
    return {"circuit": "Rs + (CPE || (Rct + semi-infinite Warburg))",
            "formula": "Z=Rs+1/(Q*(j*omega)^alpha+1/(Rct+sigma*(1-j)/sqrt(omega))); omega=2*pi*f",
            "parameter_units": {"Rs_ohm": "ohm", "Rct_ohm": "ohm", "CPE_Q": "S s^alpha",
                                "CPE_alpha": "1", "Warburg_sigma": "ohm s^(-1/2)"},
            "parameters": EIS_PARAMETERS,
            "scientific_basis": showcase_scientific_basis("eis"),
            "status": "original synthetic teaching model; no fitted experimental or material certification"}


def generate_eis() -> None:
    path = ROOT / "eis"
    frequencies = np.logspace(5, -2, 86)
    rows = []
    for sample, p in EIS_PARAMETERS.items():
        values = impedance(frequencies, p["Rs_ohm"], p["Rct_ohm"], p["CPE_Q"],
                           p["CPE_alpha"], p["Warburg_sigma"])
        rows.extend((sample, float(f), float(z.real), float(z.imag)) for f, z in zip(frequencies, values))
    csv_write(path / "data.csv", ["sample", "frequency_Hz", "Zreal_ohm", "Zimag_ohm"], rows)
    (path / "model.json").write_text(json.dumps(eis_model(), indent=2) + "\n", encoding="utf-8")


def generate_xrd() -> None:
    path = ROOT / "operando_xrd"
    angles = np.linspace(35.3, 46.7, 240)
    rows, volts, states = [], [], []
    for progress in np.linspace(0, 1, 105):
        # Shared cubic lattice for BOTH peaks, not independently chosen shifts.
        lattice = 4.16*(1-.012*progress)
        p1 = bragg_angle(lattice/np.sqrt(3))
        p2 = bragg_angle(lattice/2)
        time_s = 3600*progress
        capacity = 180*progress
        intensity = (.045 + .90 * np.exp(-.5 * ((angles - p1) / .13) ** 2)
                     + .77 * np.exp(-.5 * ((angles - p2) / .15) ** 2))
        rows.extend((float(progress), float(angle), float(value)) for angle, value in zip(angles, intensity))
        volts.append((float(progress), float(3.20 + .83 * progress + .18 * progress ** 7)))
        states.append((float(progress),float(time_s),float(capacity),180.,float(lattice),float(p1),float(p2)))
    # Legacy column name retained for backward file compatibility. Metadata and
    # plotted label define this synthetic coordinate as progression, NOT SOC.
    csv_write(path / "data.csv", ["soc_fraction", "two_theta_deg", "intensity_au"], rows)
    csv_write(path / "voltage.csv", ["soc_fraction", "voltage_V"], volts)
    csv_write(path / 'state.csv',['soc_fraction','time_s','charge_mAh_g','current_mA_g','lattice_a_A','peak111_deg','peak200_deg'],states)


def generate_tofsims() -> None:
    path = ROOT / "tof_sims"
    coordinates = np.linspace(0, 20, 72)
    xx, yy = np.meshgrid(coordinates, coordinates)
    domain = np.exp(-((xx - 7.2) ** 2 + (yy - 11.4) ** 2) / 15) + .7 * np.exp(-((xx - 15) ** 2 + (yy - 6) ** 2) / 20)
    ring = np.exp(-((np.sqrt((xx - 10) ** 2 + (yy - 10) ** 2) - 7.0) / 2.0) ** 2)
    # Positive original display fields. Clipping fields before averaging would
    # make the linked sputter profile differ from the actual shown image.
    texture = .03 * (np.sin(xx * 1.2 + yy * .8) + np.sin(xx * .42 - yy * 1.4))
    bases = {"F-": .12 + .70 * ring + .10 * domain + texture,
             "Li+": .16 + .60 * domain + texture,
             "S-": .12 + .40 * (1 - np.minimum(domain, 1)) + .20 * np.exp(-((xx - 14) ** 2 + (yy - 15) ** 2) / 13) + texture}
    factors = {"F-": lambda t: .26 + .70 * np.exp(-t / 58), "Li+": lambda t: .22 + .55 * (1 - np.exp(-t / 43)), "S-": lambda t: .18 + .32 * np.exp(-((t - 76) / 43) ** 2)}
    maps = []
    for species, base in bases.items():
        image = base * factors[species](30)
        maps.extend((species, 30, round(float(x), 5), round(float(y), 5), round(float(v), 7)) for x, y, v in zip(xx.flat, yy.flat, image.flat))
    csv_write(path / "data.csv", ["species", "sputter_time_s", "x_um", "y_um", "normalized_intensity"], maps)
    depth_rows = []
    for t in np.unique(np.r_[np.linspace(0, 180, 100), 30.0]):
        depth_rows.extend((species, round(float(t), 6), round(float((base * factors[species](t)).mean()), 7)) for species, base in bases.items())
    csv_write(path / "depth.csv", ["species", "sputter_time_s", "mean_normalized_intensity"], depth_rows)


def generate_integrated() -> None:
    path = ROOT / "integrated_study"
    path.mkdir(exist_ok=True)
    manifest = {"source_study": "independent teaching models; not a shared experimental study",
                "uses": ["../li_cu_ce/data.csv", "../li_cu_ce/profiles.csv", "../li_li/data.csv",
                         "../eis/data.csv", "../full_cell/data.csv", "../full_cell/voltage_profiles.csv"],
                "identity_rule": "A/B are display labels local to each model, not one electrolyte or material across tests",
                "dependency_ids": ["li_cu_ce", "li_li", "eis", "full_cell"],
                "scientific_basis": showcase_scientific_basis("integrated_study"),
                "status": "synthetic_demo; no mechanistic inference"}
    (path / "sources.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    csv_write(path / "data_index.csv", ["sample", "test", "source_csv"],
              ((sample, test, source) for sample in ("A", "B")
               for test, source in (("LiCu CE teaching model", "../li_cu_ce/data.csv"),
                                    ("LiLi terminal RC model", "../li_li/data.csv"),
                                    ("EIS Randles model", "../eis/data.csv"),
                                    ("Excess-Li half-cell accessible-capacity model", "../full_cell/data.csv"))))


def generate_rate() -> None:
    path = ROOT / "rate_capability"
    parameters = showcase_scientific_basis("rate_capability")["parameters"]
    stages = [(0.2, 10), (0.5, 10), (1.0, 10), (2.0, 10), (5.0, 10), (0.2, 10)]
    rows, profiles = [], []
    cycle = 0
    for stage, (rate, count) in enumerate(stages):
        for offset in range(count):
            cycle += 1
            for sample in ("A", "B"):
                p = parameters[sample]
                inventory = p["Q0_mAh_g"] * np.exp(-p["k_per_cycle"] * cycle)
                q = inventory / (1 + (rate / p["r_limit_C"]) ** .8)
                rows.append((cycle, sample, stage + 1, rate, round(float(q), 5)))
                if sample == "A" and cycle in (7, 27, 47, 57):
                    for fraction in np.linspace(0, 1, 160):
                        voltage = fullcell_voltage(float(fraction), low=2.8, high=4.3)
                        profiles.append((cycle, rate, round(float(fraction * q), 6), round(float(voltage), 6), round(float(q), 6)))
    csv_write(path / "data.csv", ["cycle", "sample", "stage", "discharge_rate_C", "capacity_mAh_g"], rows)
    csv_write(path / "voltage_profiles.csv", ["cycle", "rate_C", "capacity_mAh_g", "voltage_V", "cycling_endpoint_mAh_g"], profiles)


def generate_gcd() -> None:
    path = ROOT / "gcd_profiles"
    cycling = csv_read(ROOT / "full_cell" / "data.csv")
    rows = []
    for cycle in (1, 100, 300, 500):
        source = cycling[cycle - 1]
        discharge_endpoint = float(source["A_mAh_g"])
        charge_endpoint = float(source["A_charge_mAh_g"])
        for direction, endpoint in (("charge", charge_endpoint), ("discharge", discharge_endpoint)):
            for fraction in np.linspace(0, 1, 180):
                rows.append((cycle, direction, float(fraction * endpoint),
                             fullcell_voltage(float(fraction), direction, low=2.8, high=4.3), endpoint,
                             discharge_endpoint, charge_endpoint, float(source["A_ce_pct"])))
    csv_write(path / "data.csv", ["cycle", "direction", "capacity_mAh_g", "voltage_V",
                                  "cycling_endpoint_mAh_g", "discharge_endpoint_mAh_g",
                                  "charge_endpoint_mAh_g", "cycle_ce_pct"], rows)


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
        "surface_model": "Uncoupled positive thermal-node balances; not a measured thermogram or electrical-to-heat model",
        "thermal_parameters": showcase_scientific_basis("pouch_thermal")["parameters"],
        "colorbar_range_C": [25, 45]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate_benchmark() -> None:
    path = ROOT / "literature_benchmark"
    rng = np.random.default_rng(SEED + 9)
    rows = []
    for i in range(48):
        family = ("Group A", "Group B", "Group C")[i % 3]
        cluster = i // 3
        loading = (1.0 + .07 * cluster) if cluster < 9 else (2.0 + .23 * (cluster - 9))
        loading += rng.normal(0, .11)
        es = np.clip(20 - 2.0 * loading + rng.normal(0, 2.2), 4.5, 22)
        family_offset = {"Group A": -90, "Group B": 0, "Group C": 85}[family]
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
        "source": "../full_cell/data.csv", "dataset": "same synthetic A/B NMC811||Li half-cell cycling",
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
    ax.spines[["top", "right", "bottom", "left"]].set_visible(True)
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
    ax1.set(xlabel="Cycle number", ylabel="Discharge capacity (mAh g$^{-1}$)", xlim=(0, 505), ylim=(145, 188))
    ax1.text(.98,.94,'NMC811 || Li · half cell',transform=ax1.transAxes,ha='right',va='top',fontsize=6)
    ax1.legend(frameon=False, loc="lower left", handlelength=1.7)
    profiles = csv_read(ROOT / "full_cell" / "voltage_profiles.csv")
    for cycle, color in ((1, "#c6d7e6"), (100, "#92b4d0"), (300, "#6389aa"), (500, COLORS["A"])):
        r = [row for row in profiles if int(row["cycle"]) == cycle]
        ax2.plot(arr(r, "capacity_mAh_g"), arr(r, "voltage_V"), color=color, lw=.9, label=str(cycle))
    ax2.set(xlabel="Specific capacity (mAh g$^{-1}$)", ylabel="Voltage (V)", xlim=(0, 190), ylim=(2.75, 4.36))
    ax2.legend(frameon=False, title="Electrolyte A · cycle", title_fontsize=6, ncol=2 if compact else 1, loc="lower left", handlelength=1.3)


def plot_ce(ax1, ax2) -> None:
    rows = csv_read(ROOT / "li_cu_ce" / "data.csv")
    n = arr(rows, "cycle")
    for sample in "AB":
        ax1.plot(n, arr(rows, f"{sample}_ce_pct"), color=COLORS[sample], lw=.9, ls="-", label=f"Electrolyte {sample}")
    ax1.set(xlabel="Cycle number", ylabel="Coulombic efficiency (%)", xlim=(0, 305), ylim=(96.5, 100.25))
    ax1.legend(frameon=False, loc="lower right", handlelength=1.4)
    profiles = csv_read(ROOT / "li_cu_ce" / "profiles.csv")
    for sample in "AB":
        for cycle in (1, 300):
            r = [row for row in profiles if row["sample"] == sample and int(row["cycle"]) == cycle and row["stage"] == "strip"]
            ax2.plot(arr(r, "capacity_mAh_cm2"), arr(r, "voltage_V"), color=COLORS[sample] if cycle == 300 else {"A": "#7396b5", "B": "#885369"}[sample], lw=.9, ls="-", label=f"{sample} · {cycle}")
    ax2.set(xlabel="Stripped capacity (mAh cm$^{-2}$)", ylabel="Voltage (V)", xlim=(0, 1.02), ylim=(0, 1.05))
    ax2.legend(frameon=False, ncol=2, loc="upper left", handlelength=1.3)


def plot_symmetric(ax1, ax2) -> None:
    rows = csv_read(ROOT / "li_li" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        ax1.plot(arr(r, "time_h"), arr(r, "voltage_mV"), color=COLORS[sample], lw=.5, label=f"Electrolyte {sample}")
        z = [row for row in r if 101 <= float(row["time_h"]) <= 108]
        ax2.plot(arr(z, "time_h"), arr(z, "voltage_mV"), color=COLORS[sample], lw=.75)
    ax1.set(xlabel="Time (h)", ylabel="Cell voltage (mV)", xlim=(0, 200), ylim=(-70, 70))
    ax2.set(xlabel="Time (h)", ylabel="Cell voltage (mV)", xlim=(101, 108), ylim=(-65, 65))
    ax1.legend(frameon=False, loc="upper left", handlelength=1.4)
    ax1.axvspan(101, 108, color="#dce8ee", zorder=-3)


def plot_eis(ax1, ax2) -> None:
    rows = csv_read(ROOT / "eis" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        zr, zi, freq = arr(r, "Zreal_ohm"), arr(r, "Zimag_ohm"), arr(r, "frequency_Hz")
        ax1.plot(zr, -zi, color=COLORS[sample], lw=.9, ls="-", label=f"Model {sample}")
        ax2.semilogx(freq, np.degrees(np.arctan2(zi, zr)), color=COLORS[sample], lw=.95, ls="-", label=f"Model {sample}")
    ax1.set(xlabel="Z′ (Ω)", ylabel="−Z″ (Ω)", xlim=(0, 70), ylim=(0, 70/3))
    ax1.set_aspect("equal", adjustable="box")
    ax2.set(xlabel="Frequency (Hz)", ylabel="Phase angle (°)", xlim=(.01, 1e5), ylim=(-90, 0))
    ax1.legend(frameon=False, loc="upper right", handlelength=1.4)


def plot_eis_nyquist(ax) -> None:
    rows = csv_read(ROOT / "eis" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        ax.plot(arr(r, "Zreal_ohm"), -arr(r, "Zimag_ohm"), color=COLORS[sample], lw=.9, ls="-", label=f"Model {sample}")
    ax.set(xlabel="Z′ (Ω)", ylabel="−Z″ (Ω)", xlim=(0, 70), ylim=(0, 28))
    ax.set_aspect("equal", adjustable="box")
    ax.legend(frameon=False, loc="upper right", ncol=2, handlelength=1.1)


def plot_xrd(ax1, ax2, fig) -> None:
    rows = csv_read(ROOT / "operando_xrd" / "data.csv")
    soc = np.unique(arr(rows, "soc_fraction"))
    angles = np.unique(arr(rows, "two_theta_deg"))
    values = arr(rows, "intensity_au").reshape(len(soc), len(angles))
    state=csv_read(ROOT/'operando_xrd'/'state.csv')
    times=arr(state,'time_s')/3600
    if not np.allclose(soc,arr(state,'soc_fraction')):raise ValueError('XRD/time index mismatch')
    im=ax1.pcolormesh(angles,times,values,cmap='viridis',shading='nearest',vmin=float(values.min()),vmax=float(values.max()),rasterized=True)
    ax1.set(xlabel="2θ (°) · λ = 1.5406 Å", ylabel="Time (h)", xlim=(35.3,46.7),ylim=(0,1))
    voltage = csv_read(ROOT / "operando_xrd" / "voltage.csv")
    if not np.allclose(arr(voltage,'soc_fraction'),soc):raise ValueError('Voltage/XRD timestamps differ')
    ax2.plot(arr(voltage, "voltage_V"), times, color=COLORS["B"], lw=1.1,ls='-',marker=None)
    ax2.set(xlabel="Voltage (V)", ylabel="Time (h)", xlim=(3.1,4.3),ylim=(0,1))
    ax1.text(.02,.97,'Original synthetic cubic host',transform=ax1.transAxes,ha='left',va='top',fontsize=6,bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
    ax2.text(.05,.05,'Charge\n180 mA g$^{-1}$',transform=ax2.transAxes,fontsize=6)
    # Same source row / shared lattice labels; no fitted chemical phase claim.
    for label,key in [('(111)','peak111_deg'),('(200)','peak200_deg')]:
        ax1.text(float(state[0][key]),.035,label,ha='center',fontsize=6,color=INK,bbox={'facecolor':'white','edgecolor':'none','alpha':.8})
    bar = fig.colorbar(im, ax=ax1, fraction=.035, pad=.025)
    bar.ax.set_ylabel("Intensity (a.u.)", fontsize=6)
    bar.ax.tick_params(labelsize=5.5, width=.5)


def plot_tofsims(axes, fig) -> None:
    maps = csv_read(ROOT / "tof_sims" / "data.csv")
    depth = csv_read(ROOT / "tof_sims" / "depth.csv")
    map_palettes = ['viridis']*3
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
        ax.set_title(('Negative mode','Positive mode','Negative mode')[index],fontsize=6,pad=5)
        cax = fig.add_axes([(.075,.39,.705)[index]+.21,.55,.008,.34])
        bar = fig.colorbar(image, cax=cax)
        bar.ax.set_yticks([0, .65])
        bar.ax.tick_params(labelsize=5, length=1.8, width=.45, pad=1)
    fig.text(.08,.945,'Original synthetic ion signals · 30 s sputter time · a.u., not concentration',fontsize=6.3)
    ax = axes[3]
    for species, color, label in (("F-", COLORS["B"], r"F$^{-}$"), ("Li+", COLORS["C"], r"Li$^{+}$"), ("S-", COLORS["A"], r"S$^{-}$")):
        r = [row for row in depth if row["species"] == species]
        ax.plot(arr(r, "sputter_time_s"), arr(r, "mean_normalized_intensity"), color=color, lw=1, label=label)
    ax.axvline(30, color=MUTED, lw=.55, ls="-")
    ax.set(xlabel="Sputter time (s) · depth uncalibrated", ylabel="Mean ion signal (a.u.)", xlim=(0,180),ylim=(0,.48))
    ax.legend(frameon=False, loc="upper right", ncol=3, handlelength=1.2)
    ax.text(.02,.04,'Matrix-dependent yield · no 3D composition inferred',transform=ax.transAxes,fontsize=6)


def plot_rate(ax1, ax2) -> None:
    rows = csv_read(ROOT / "rate_capability" / "data.csv")
    for sample in "AB":
        r = [row for row in rows if row["sample"] == sample]
        ax1.plot(arr(r, "cycle"), arr(r, "capacity_mAh_g"), color=COLORS[sample],
                 marker=None, ls="-", lw=.8, label=f"Electrolyte {sample}")
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
            xlim=(0, 185), ylim=(2.75, 4.35))
    ax2.legend(frameon=False, loc="lower left", fontsize=5.4, handlelength=1.1)


def plot_gcd(ax, compact=False) -> None:
    rows = csv_read(ROOT / "gcd_profiles" / "data.csv")
    shades = {1: "#b6cadd", 100: "#88abc8", 300: "#5d83a4", 500: COLORS["A"]}
    for cycle in ((300,) if compact else (1, 100, 300, 500)):
        for direction in ("discharge", "charge"):
            r = [row for row in rows if int(row["cycle"]) == cycle and row["direction"] == direction]
            ax.plot(arr(r, "capacity_mAh_g"), arr(r, "voltage_V"), color=shades[cycle] if direction == "discharge" else {1: "#c893a0", 100: "#b66f86", 300: "#944462", 500: "#70384b"}[cycle],
                    lw=.9, ls="-", label=f"{cycle} · {direction}")
    ax.set(xlabel="Specific capacity (mAh g$^{-1}$)", ylabel="Voltage (V)",
           xlim=(0, 190), ylim=(2.75, 4.37))
    if compact:
        ax.text(.98, .04, "Cycle 300 · blue/discharge · rose/charge",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=4.5, color=MUTED)
    else:
        ax.legend(frameon=False, loc="lower left", ncol=2, fontsize=5.7)
        ax.text(.98, .04, "blue: discharge    rose: charge", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=5.5, color=MUTED)


def plot_thermal(axes, fig, colorbar_ax) -> None:
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
    map_ax.axhline(35, color="white", lw=.7, ls="-")
    map_ax.set(xlabel="Pouch width (mm)", ylabel="Pouch height (mm)",
               xlim=(0, 100), ylim=(0, 76))
    bar = fig.colorbar(im, cax=colorbar_ax)
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
    shapes = {"Group A": "o", "Group B": "s", "Group C": "^"}
    for family, marker in shapes.items():
        r = [row for row in rows if row["host_family"] == family]
        tone = {"Group A": COLORS["A"], "Group B": COLORS["C"],
                "Group C": COLORS["B"]}[family]
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
    axes[0].set(xlabel="Chosen progress (%)", ylabel=r"2θ (°)")
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
    axes[3].set(xlabel="Z′ (Ω)", ylabel="−Z″ (Ω)")
    box = axes[3].get_position()
    width, height = fig.get_size_inches()
    axes[3].set(xlim=(0, 70), ylim=(0, 70 * box.height * height / (box.width * width)))
    axes[3].set_aspect("equal", adjustable="box")
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
        axes[7].plot(arr(r, "cycle"), arr(r, "capacity_mAh_g"), color=COLORS[sample], lw=.65, marker=None, ls="-")
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
    themes = json.loads((Path(__file__).resolve().parents[2] / "skills" / "voltpeer-plot" / "assets" / "figure_theme.json").read_text(encoding="utf-8"))["presets"]
    rows = csv_read(ROOT / "style_presets" / "data.csv")
    n = arr(rows, "cycle")
    fig, axes = plt.subplots(2, 3, figsize=(270 / 25.4, 133 / 25.4))
    fig.subplots_adjust(left=.072, right=.983, bottom=.12, top=.9, wspace=.36, hspace=.62)
    for ax, (key, theme) in zip(axes.flat, themes.items()):
        first, second = theme["series"][:2]
        for sample, colour, line in (("A", first, "-"), ("B", second, "-")):
            ax.plot(n, arr(rows, f"{sample}_mAh_g"), color=colour, lw=.9, ls=line, label=sample)
        ax.set(xlim=(0, 500), ylim=(130, 190), xlabel="Cycle number", ylabel="Capacity (mAh g$^{-1}$)")
        ax.spines[["top", "right", "bottom", "left"]].set_visible(True)
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
        from batteryplot.layout import axes_mm
        fig = plt.figure(figsize=(180 / 25.4, 118 / 25.4))
        named = {'a': axes_mm(fig, left=19, top=6, width=150, height=50),
                 'b': axes_mm(fig, left=19, top=72, width=150, height=34)}
        axes = [named['a'], named['b']]
        fig._alignment_contract = (named, [('a', 'b', edge) for edge in ('left', 'right', 'width')])
        plot_eis(*axes)
    elif name == "operando_xrd":
        fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 98 / 25.4), gridspec_kw={"width_ratios": [1.95, .75]}, layout="constrained")
        plot_xrd(*axes, fig)
    elif name == "tof_sims":
        fig = plt.figure(figsize=(180/25.4,100/25.4))
        axes=[fig.add_axes([x,.55,.20,.34]) for x in (.075,.39,.705)]
        axes.append(fig.add_axes([.075,.14,.845,.27]))
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
        from batteryplot.layout import pouch_layout
        fig = plt.figure(figsize=(180 / 25.4, 106 / 25.4))
        named, relations = pouch_layout(fig)
        axes = [named[key] for key in 'abc']
        fig._alignment_contract = (named, relations)
        plot_thermal(axes, fig, named['colorbar'])
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
        if name == 'tof_sims':
            # A wide profile must use a fixed physical label inset; a fractional
            # axis-width inset would put its panel letter outside the canvas.
            ax.texts[-1].remove()
            box=ax.get_position()
            fig.text(box.x0-4/180,box.y1+1.5/100,letter,
                     fontsize=8,fontweight='bold',ha='left',va='bottom',color=INK)
        if name == 'pouch_thermal':
            # Letters use the same physical inset even when panel widths differ.
            ax.texts[-1].remove()
            box = ax.get_position()
            fig.text(box.x0 - 8/180, box.y1 + 2/106, letter,
                     fontsize=8, fontweight='bold', ha='left', va='bottom', color=INK)
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
    if hasattr(fig, '_alignment_contract'):
        from batteryplot.layout import measure_layout
        named, relations = fig._alignment_contract
        return {'figure': name, **measure_layout(fig, named, relations),
                'note': 'Actual plot boxes after draw; a separate colorbar never steals panel space.'}
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
            "tof_sims": [(0, 1), (1, 2)]}.get(name, [])
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
        return ["data_index.csv", "sources.json", "../operando_xrd/data.csv",
                "../full_cell/data.csv", "../li_cu_ce/data.csv", "../eis/data.csv",
                "../literature_benchmark/data.csv", "../pouch_thermal/history.csv",
                "../li_li/data.csv", "../rate_capability/data.csv", "../gcd_profiles/data.csv",
                "../reporting_matrix/data.csv"]
    return sorted(p.name for p in (ROOT / name).glob("*.csv"))


def data_frame_audit(fig) -> list[dict]:
    checks = []
    for panel, ax in enumerate(fig.axes):
        if ax.axison and not hasattr(ax, "_colorbar"):
            spines = {side: bool(ax.spines[side].get_visible()) for side in ("top", "right", "bottom", "left")}
            if not all(spines.values()):
                raise ValueError(f"panel {panel}: data axes must show all four frame spines")
            checks.append({"panel_index": panel, "spines": spines})
    return checks


def curve_style_audit(fig) -> list[dict]:
    """Inspect actual continuous Line2D artists before saving the teaching plate."""
    data_frame_audit(fig)
    report = []
    for panel, ax in enumerate(fig.axes):
        apply_series_policy(ax)
        if ax.axison and not hasattr(ax, "_colorbar"):
            frame = {side: ax.spines[side].get_visible() for side in ("top", "right", "bottom", "left")}
            if not all(frame.values()):
                raise ValueError(f"panel {panel}: data axes must show all four frame spines")
        for line in ax.lines:
            marker, line_style = line.get_marker(), line.get_linestyle()
            sampling = check_series_policy(ax, line)
            report.append({"panel_index": panel, "label": line.get_label(),
                           "points": len(line.get_xdata()), "line_style": line_style,
                           "marker": marker, "colour": matplotlib.colors.to_hex(line.get_color()), "sampling": sampling})
    return report


def render(name: str) -> None:
    destination = ROOT / name
    fig = figure(name)
    curve_styles = curve_style_audit(fig)
    frames = data_frame_audit(fig)
    ruler = ruler_audit(name, fig)
    (destination / "alignment.json").write_text(json.dumps(ruler, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if ruler["failures"]:
        plt.close(fig)
        raise ValueError(f"{name}: rendered panel edges exceed 1.5 pt: {ruler['failures']}")
    for suffix in ("svg", "pdf", "png"):
        fig.savefig(destination / f"figure.{suffix}", dpi=300, facecolor="white")
    if name == "style_presets":
        themes = json.loads((Path(__file__).resolve().parents[2] / "skills" / "voltpeer-plot" / "assets" / "figure_theme.json").read_text(encoding="utf-8"))["presets"]
        for ax, (key, theme) in zip(fig.axes, themes.items()):
            one = plt.figure(figsize=(112 / 25.4, 65 / 25.4))
            target = one.add_axes([.12, .17, .82, .65])
            for original in ax.lines[:2]:
                target.plot(original.get_xdata(), original.get_ydata(), color=original.get_color(),
                            lw=.95, ls=original.get_linestyle(), marker=original.get_marker(),
                            markersize=2.7, label=original.get_label())
            target.set(xlim=(0, 500), ylim=(130, 190), xlabel="Cycle number", ylabel="Capacity (mAh g$^{-1}$)")
            target.spines[["top", "right", "bottom", "left"]].set_visible(True)
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
    meta["continuous_curve_style_checks"] = curve_styles
    meta["curve_style_check"] = "Cycle capacity/CE/retention are marker-only; continuous profiles are solid and unmarked; user display preference."
    meta["data_frame_check"] = "pass: actual data axes show top/right/bottom/left spines"
    meta["data_frame_checks"] = frames
    meta["scientific_basis"] = showcase_scientific_basis(name)
    meta["sample_identity"] = "A/B are local teaching-model labels, not one electrolyte across unlike techniques; SIM IDs are invented records, never citations."
    meta["review"] = {"science": "Declared model equations/units/linked-file relations have scoped automated tests; no experimental certification.",
                      "display": "Actual line/frame/alignment checks only; independent visual and author review remain pending."}
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
    curve_style_audit(fig)
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
             "NMC811||Li half-cell cycling", "selected NMC811||Li half-cell voltage profiles")
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
    process = subprocess.run([sys.executable, str(script), "compose", "--manifest", str(manifest_path),
                              "--out", str(out / "assembled-example"), "--strict"],
                             check=True, capture_output=True, encoding="utf-8")
    actual = json.loads(process.stdout)["outputs"]
    actual_png, actual_pdf = Path(actual["png"]), Path(actual["pdf"])
    actual_qa = actual_png.with_suffix(".qa.json")
    shutil.copy2(actual_png, SITE / "assembly-example.png")
    shutil.copy2(actual_pdf, SITE / "assembly-example.pdf")
    readme = {"data_status": "synthetic_demo", "source": "integrated_study",
              "panels": list("abcdef"), "instruction": "Assemble a–f without panel subtitles or data changes.",
              "ready_manifest": "figure_manifest.json",
              "alignment_report": actual_qa.name,
              "assembled_files": [actual_png.name, actual_pdf.name],
              "note": "Panel crops use common column x-rulers and row y-rulers; measured plot boxes are recorded in the manifest."}
    (out / "README.json").write_text(json.dumps(readme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = SITE / "assembly-demo.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w", ZIP_DEFLATED) as z:
        current = [out / f"panel-{letter}.png" for letter in "abcdef"]
        current += [manifest_path, out / "README.json", actual_png, actual_pdf, actual_qa]
        for file in sorted(current):
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
