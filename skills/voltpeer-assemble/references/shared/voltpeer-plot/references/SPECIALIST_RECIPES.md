# Optional specialist recipes

These six recipes have runnable renderers and explicit fields. They are **optional variants**, not new default pairings validated across three independent papers. Source observations are in each showcase's `metadata.json`; no paper data or artwork is redistributed. For actual author data, select the matching experiment and read only its row below.

Run from the installed figure skill's `scripts` directory:

```text
python render_specialist.py --recipe xps_components --input-folder <prepared-folder> --output-dir <new-output-folder> --style forge
```

The folder contains `data.csv` and `metadata.json`. Supply `test_conditions`, `source_files: ["data.csv"]`, and the matching `render_options`. Do not silently fill unknown conditions; the text can explicitly name a missing condition while the author resolves it. Choose the style once with the author; `--community-style-lock` accepts an already selected, exact local version. No network downloads occur. The output folder must be new, preserving originals and earlier figures.

| Recipe | Numeric CSV columns / additional field | Required render_options | What the script does |
|---|---|---|---|
| `cyclic_voltammetry` | scan_rate_mV_s, sequence, voltage_V, current_mA | reference_electrode, zoom_voltage_V: [lo,hi] | Preserves acquisition order including reverse scan; plots full curves and same-data voltage zoom. Never sorts voltage or infers reference electrode. |
| `differential_capacity` | cycle, voltage_V, capacity_mAh_g | branch: "charge" | This particular renderer takes strictly increasing charge branches; computes `np.gradient(Q,V,edge_order=2)` with no smoothing. Repeated/reversing V requires an explicit method/branch decision outside this recipe. No discharge absolute-value conversion. |
| `gitt_pulse` | time_min, voltage_V, current_mA | {} | Aligns voltage and supplied current on the same time axis. Diffusion coefficient, equilibrium, pulse selection and material geometry are separate analyses. |
| `ionic_conductivity` | temperature_C, conductivity_mS_cm; sample | {} | Plots σ(T) and ln[σ/(S/cm)] against 1000/T (K). Requires positive Kelvin and conductivity. No fitted activation energy. σT-based Arrhenius is a different expression. |
| `xps_components` | binding_energy_eV, intensity_counts, background_counts, component_1, component_2, component_3 | component_labels: 3 strings, fit_method, charge_reference | Displays supplied baseline-subtracted components plus background, sum and data−sum residual. No optimizer or chemical peak assignment. Uses descending binding-energy display. A raw spectrum alone is insufficient for a fitted-components panel. |
| `raman_series` | wavenumber_cm_1, intensity_counts; sample | display_offset_counts, zoom_wavenumber_cm_1: [lo,hi] | Stacks original intensity by declared constant offsets and reproduces the same spectra in a zoom. No normalization, baseline subtraction or molecular assignment. |

Outputs: PNG, editable SVG, vector PDF, provenance JSON with transformations, source hashes, actual font and alignment measurements. Run `audit_pdf_fonts.py` and visually inspect the final-size export; an export path is not a visual approval. XPS legend must avoid data peaks. Long axis labels, dense ticks or more series may require a different physical recipe.

## Choosing among the larger figure library

| Author's input/question | First route | Current support |
|---|---|---|
| CE, full/half cell, symmetric cell, rate, capacity/voltage, EIS, CV | Uploaded-data contract and matching batteryplot function | Executable after metadata and units are mapped; exact protocols matter |
| dQ/dV, GITT, conductivity, XPS components, Raman | Recipe table above | Optional executable recipes with specific input contracts |
| Operando XRD, ToF-SIMS, temperature field | SHOWCASE_RECIPES + PHYSICAL_LAYOUT | Source-backed display planning and reproducible **demo** code; instrument exports require explicit calibration/mapping |
| SEM/TEM/cryo/AFM/EDS/X-ray CT | Figure atlas + assembly | Assemble supplied acquired images and scale bars; no synthesis of measurement content |
| XANES/EXAFS, PDF scattering, SAXS/WAXS, NMR, FTIR | Figure atlas + source methods | Plan and display supplied processed arrays; no automatic fitting/assignment claim |
| MD snapshots, RDF, coordination number, MSD, DFT/ESP/DOS | Figure atlas | Use supplied simulation output and computation conditions; do not invent molecular/energy evidence |
| LSV, transference number, stress/strain, DSC/TGA/ARC, gas evolution | Figure grammar/atlas + explicit method | Protocol-specific plotting after mapping; no generic automatic scientific inference |
| Ragone, retention, cross-paper performance | Metrics audit + matching plot | Require denominator/reference cycle/comparability; no inferred normalization |
| Review wheel, mechanism/evidence chain, process schematic | Original assets + figure planning | Original explanatory geometry from confirmed evidence; distinguish measured and proposed steps |
| Several finished images | voltpeer-assemble | Inventory, physical placement, edge audit, final-size review |

Tell a beginner what file to supply next. Do not ask them to choose between internal renderer names. Detect file structure first; `.csv` does not tell you whether the experiment is CV, CE or Aurbach. If columns/units/protocol are ambiguous, show what was read and ask the one scientific question that changes the plot.

## Additional optional recipes

FTIR, NMR, RDF/coordination number, MSD, LSV and polarization/EIS transference plots have explicit CSV renderers. Read [their input contracts and paper-level evidence](CORPUS_RECIPES.md). These new routes supersede the general planning-only status for those six names in the broad table above; other analyses remain as stated.
