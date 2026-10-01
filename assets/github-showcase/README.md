# VoltPeer · gallery data and code

These are **original synthetic teaching examples, not experimental data**. Parameters were chosen for these models; published sources explain the equations, not these numerical values. The gallery is supplied under the repository's [MIT license](../../LICENSE).

每张图保留原始 CSV、模型依据和绘图源码。图件用于展示绘图与排版，不证明材料性能或化学机理。不同技术的 A/B 标签各自独立。

## Reproduce

```bash
python -m venv .venv
# Activate the environment for your operating system, then:
python -m pip install -r examples/github_showcase/requirements.txt
python examples/github_showcase/render.py --output-dir outputs/github-gallery
```

[Plotting source](../../examples/github_showcase/render.py) · [Input hashes and origins](data/PROVENANCE.json) · [Actual render checks](render-checks.json)

The renderer reads the saved CSVs and checks their hashes. It does not regenerate, smooth, interpolate or fit data. Changing a synthetic input fails the provenance check; this dedicated gallery is not an author-data plotting tool. Use the plotting Skill and input contracts for your own files.

## Structure and spectra

[PNG](structure-spectra.png) · [SVG](structure-spectra.svg)

- [Diffraction data](data/operando_xrd/data.csv) · [model](data/operando_xrd/basis.json): two fictitious spacings obey first-order [Bragg's law, IUCr](https://dictionary.iucr.org/Bragg%27s_law). Progress is a chosen coordinate, not measured SOC; the peaks do not identify a refined crystal or a phase transition. Five existing progress traces are selected for the stacked view, with a declared +0.72 a.u. display offset per trace.
- [Generic Raman data](data/raman_series/data.csv) · [model](data/raman_series/basis.json): chosen Gaussian bands and a background, with +340 counts per trace for display. No molecule, concentration or measured shift is assigned.
- [Generic spectral components](data/xps_components/data.csv) · [model](data/xps_components/basis.json): known Gaussian/Lorentzian components, a linear background and synthetic Poisson counts. Components are displayed on their common background. This is not an experimental fit or chemical assignment.

## Impedance spectroscopy

[CPE / Warburg PNG](eis-cpe-warburg.png) · [SVG](eis-cpe-warburg.svg) · [exact CSV](data/eis/data.csv) · [circuit and units](data/eis/model.json) · [basis](data/eis/basis.json)

[Ideal RC PNG](eis-ideal-rc.png) · [SVG](eis-ideal-rc.svg) · [exact CSV](data/eis_frequency/data.csv) · [basis](data/eis_frequency/basis.json)

Nyquist, magnitude and phase come from the same saved complex impedance at every frequency. Nyquist uses equal physical scales for Ω on both axes; `−Im Z` is displayed upward, while the Bode phase retains its signed value. Each curve retains all original rows and uses a solid line without markers.

The CPE / Warburg example assumes a linear, stationary passive circuit with semi-infinite diffusion. The ideal RC example assumes positive passive resistors and a capacitor. Neither has been fitted to a cell or used to infer a transport coefficient. Circuit conventions and limits follow [Gamry's official EIS guide](https://www.gamry.com/application-notes/EIS/basics-of-electrochemical-impedance-spectroscopy/).

## Six-panel layout

[PNG](six-panel-layout.png) · [SVG](six-panel-layout.svg)

The figure assembles independent Li || Cu efficiency, NMC811 || Li half-cell capacity, model EIS, diffraction and generic count-spectrum panels. Local model labels do not imply one sample across techniques or mechanistic cross-validation.

[Efficiency CSV](data/li_cu_ce/data.csv) · [basis](data/li_cu_ce/basis.json) · [half-cell capacity CSV](data/full_cell/data.csv) · [basis](data/full_cell/basis.json)

The historical `full_cell` folder ID holds an NMC811 || Li **half-cell** example. Its declared capacity fade and charge ledger are not a limited-lithium full-cell inventory model.

## Validation scope

The renderer checks exact input hashes, declared complex circuit equations, the ideal RC semicircle, charge ratios, known count-component sums, all four data spines, solid marker-free curves, unclipped line values, label bounds and equal Nyquist scales. Raw input hashes are checked again after export.

These are model and display checks. They do not validate a real experiment, material, circuit fit, chemical assignment or any AI model's behavior. [Maintainer record](../../docs/validation/GITHUB_SHOWCASE_2026-10-01.md)
