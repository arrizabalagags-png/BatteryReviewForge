> This is a copied science guide. Its executable commands require a separately installed `battery-review-figure`; `<installed-battery-review-figure>` means that Skill's actual root. Those scripts and Python dependencies are not supplied by this guide.

# Six optional plots from checked battery papers

Use the installed `<installed-battery-review-figure>/<installed-battery-review-figure>/scripts/render_specialist.py`. Ask what the data columns and test conditions mean before rendering. These are optional display choices; their scientific axes and test identities were checked in primary papers. Layout details such as a separate zoom or splitting two axes are display variants, not an assertion that the cited paper used the identical layout. No class has the three independent papers required for default-template promotion.

All bundled data are synthetic. They establish no measured peak assignment, chemistry, stability window, transport property or performance claim. Never infer experiment identity from `.csv` alone.

Command: `python <installed-battery-review-figure>/<installed-battery-review-figure>/scripts/render_specialist.py --recipe NAME --input-folder INPUT --output-dir NEW_OUTPUT --style forge`. Read the supplied metadata and ask the user for a preferred style first. Do not overwrite their input or output.

## ftir

Source: https://doi.org/10.1002/aenm.202101775 · Figure 1 c.

Input files: data.csv.
CSV fields: sample, wavenumber_cm_1, transmittance_percent.

Declared options (example values are synthetic, never defaults for an experiment):
```json
{
  "zoom_wavenumber_cm_1": [
    790,
    855
  ],
  "wavenumber_direction": "descending"
}
```

Checks: Do not assign a vibrational band or coordination state from a visible trough alone; retain the paper's assignment and sample composition. Do not convert transmittance to absorbance or normalize traces without the raw spectra and a stated transform. This one example does not establish a universal FTIR peak window or default color mapping.

## nmr

Source: https://doi.org/10.1016/j.cej.2022.139398 · Fig. 1 b.

Input files: data.csv.
CSV fields: sample, chemical_shift_ppm, intensity_au.

Declared options (example values are synthetic, never defaults for an experiment):
```json
{
  "nucleus": "$^7$Li",
  "chemical_shift_reference": "Synthetic axis reference at 0 ppm; no real standard used",
  "display_offset_au": 1.2,
  "zoom_chemical_shift_ppm": [
    -0.55,
    0.25
  ]
}
```

Checks: Vertical offsets and trace heights are not quantitative concentration comparisons unless acquisition, processing and normalization are supplied. Do not turn the peak-shift ordering into a complete solvation mechanism without the Raman/MD evidence and stated referencing. The y-axis unit is unknown, not assumed to be arbitrary units.

## rdf_coordination

Source: https://doi.org/10.1016/j.cej.2022.139398 · Fig. 1 d,e,f.

Input files: data.csv.
CSV fields: pair, distance_A, g_r, coordination_number.

Declared options (example values are synthetic, never defaults for an experiment):
```json
{
  "species_definition": "Invented Li-O (solvent), Li-O (anion), Li-F (diluent) pair labels",
  "coordination_source": "Numerical trapezoidal integration of the synthetic g(r) grid from 0.5 Å using stated pair densities",
  "pair_number_density_A3": {
    "Li-O (solvent)": 0.025,
    "Li-O (anion)": 0.012,
    "Li-F (diluent)": 0.007
  },
  "coordination_cutoff_A": 3.4
}
```

Checks: Do not derive a coordination number by reading the RDF peak height; integration requires density, species definition and cutoff radius. Do not mix the left G(r) scale with the right coordination-number scale. Do not treat MD-derived curves as direct experimental measurement or copy the published trajectories.

## msd

Source: https://doi.org/10.1002/anie.201900266 · Figure 3 c,d.

Input files: data.csv.
CSV fields: temperature_C, electrolyte, time_ps, msd_A2.

Declared options (example values are synthetic, never defaults for an experiment):
```json
{
  "simulated_species": "Li+",
  "simulation_method": "Invented analytic trajectories; not molecular dynamics",
  "diffusion_fit": false
}
```

Checks: Do not claim an ion diffusion coefficient from a decorative line or a single end point; a stated linear fit interval, simulation conditions, dimensionality and unit conversion are needed. Do not compare slopes between the temperature panels without accounting for their different y-axis ranges. The paper shows simulated Li+ MSD, not an experimentally measured diffusion curve.

## lsv

Source: https://doi.org/10.1016/j.cej.2022.139398 · Fig. 1 a.

Input files: data.csv.
CSV fields: electrolyte, voltage_V, current_density_uA_cm2.

Declared options (example values are synthetic, never defaults for an experiment):
```json
{
  "working_electrode": "Al, synthetic illustration only",
  "counter_reference_electrode": "Li metal, synthetic illustration only",
  "scan_rate_mV_s": 0.1,
  "zoom_voltage_V": [
    4.0,
    4.9
  ]
}
```

Checks: An oxidation onset or electrochemical window cannot be read as an intrinsic material constant without a stated threshold, electrode/cell configuration, reference and scan rate. Do not compare this current-density scale with LSV from another study lacking equivalent area and setup. Do not infer full-cell cycle life from LSV alone.

## transference

Source: https://doi.org/10.1002/aenm.202101775 · Figure 6 c.

Input files: data.csv, eis.csv.
CSV fields: electrolyte, time_s, current_mA.

Declared options (example values are synthetic, never defaults for an experiment):
```json
{
  "calculation_method": "Bruce-Vincent style, supplied ΔV/I0/Iss/R0/Rss only",
  "known_parameters": {
    "A": {
      "polarization_voltage_V": 0.01,
      "initial_current_mA": 0.04,
      "steady_current_mA": 0.03,
      "initial_resistance_ohm": 65,
      "steady_resistance_ohm": 79.3
    },
    "B": {
      "polarization_voltage_V": 0.01,
      "initial_current_mA": 0.05,
      "steady_current_mA": 0.02,
      "initial_resistance_ohm": 85,
      "steady_resistance_ohm": 103.7
    }
  }
}
```

Checks: Do not read tLi+ directly from the final current level; calculation also needs the polarization voltage and initial/steady currents and resistances under the stated method. Do not invent numerical transference values when only the plotted transients and insets are available. Do not replace the impedance insets with unrelated EIS traces or present them as a second current axis.

## Coverage beyond these recipes

SEM/TEM/EDS/AFM/CT images go to calibrated image assembly. XANES/EXAFS, SAXS/WAXS, DFT/DOS, thermal analysis and mechanics still require an explicit data/method mapping; the library does not claim validated automated scientific analysis for every figure in the 51-paper corpus. The corpus scan is an index, not a completed panel audit.
