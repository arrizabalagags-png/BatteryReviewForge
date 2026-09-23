---
name: battery-metrics-audit
description: Audit comparability of battery performance numbers and mechanism claims across papers, tables, or figures. Use when cell conditions and denominators matter.
---

# Battery evidence and comparison rules

Use this when extracting performance numbers, building a benchmark, interpreting a mechanism, or assessing translation claims. These are prompts for what to extract, not a universal requirement that every paper report every field. Use [BATTERY_COMPARISON.csv](assets/templates/BATTERY_COMPARISON.csv) when a project has no existing extraction schema. `NR` means *not reported after checking the relevant source*; `NV` means *not yet verified*; `NA` means not applicable. Never infer a reporting gap from an abstract-only paper or fill any gap by guesswork.

## Identify the observation before quoting the number

For a numerical claim, record the material and treatment, chemistry and electrode pair, cell configuration (`half`, `symmetric`, `full`) and package (`coin`, `pouch`, etc.) as separate axes, charge/discharge or insertion/extraction branch, cycle index and formation protocol, measurement method, value and uncertainty, and source page/figure/SI. A charge branch is not automatically evidence of fast charging. A plateau fraction at one current is not capacity retention across rates.

Record the denominator and boundary: active-material mass, composite electrode mass, electrode area/volume, cell mass/volume, or pack/system boundary. Distinguish specific capacity, areal capacity, energy density, power density, Coulombic efficiency, retention, calendar/cycle life, and throughput. If recalculating, save formula, inputs, assumptions, and propagation of uncertainty. Mark each entry `reported`, `recalculated`, or `modelled`. A theoretical value or projected production design must not be presented as a measured cell result.

Typical conditions that can determine interpretation include loading and areal capacity, electrode thickness/density, counter-electrode excess or N/P, electrolyte amount and formulation, separator, voltage window, C-rate definition or current density, temperature, pressure, state-of-charge/depth-of-discharge window, rest periods, cycle/retention baseline, sample count, and error bars. Use chemistry-specific additions below. The [ACS battery reporting checklist](https://pubs.acs.org/doi/10.1021/acsenergylett.1c00870) and the [academic-to-industrial metrics discussion](https://www.nature.com/articles/s41565-019-0371-8) explain why these conditions matter.

## Build a comparison, not a leaderboard

Group studies by the question and comparable boundary. Assign an explicit comparability label for *that comparison*:

| Label | Meaning | Suitable use |
| --- | --- | --- |
| A | Same chemistry, configuration, denominator, and key operating conditions are reported and aligned | Direct comparison with residual caveats |
| B | Partly aligned; a named variable still differs or is missing | Conditional comparison, sensitivity analysis |
| C | Useful to show context or a trend, but not to rank | Qualitative discussion |
| D | Different boundary or essential conditions make the requested comparison invalid | Exclude from that quantitative contrast |

State the rule used to assign labels and show `NR` and `NV` fields in the table. Do not invent universal pass/fail thresholds for “practical” cells; application, chemistry, and test format change the meaning. Missing methods can themselves be a finding, but calculate reporting rates only for the checked source set and name that denominator.

Hard interpretation boundaries:

- Half-cell capacity does not establish full-cell energy density; symmetric-cell stability does not establish full-cell lifetime.
- Coin-cell results and pouch-cell results are different package claims, independent of the half/full distinction.
- “Fast charging” requires the charging branch, a defined time/current and capacity or energy endpoint, and operating conditions.
- Cycle life needs the retention numerator and baseline cycle, current, temperature, depth of discharge, and cell type.
- Energy density needs measured versus modelled status and the included mass/volume boundary. Material-level, cell-level, and pack-level projections are separate.
- Scale-up, manufacturing energy, LCA, safety, and cost require their own system boundaries, assumptions, and source; laboratory measurements and models must be labeled separately.

## Chemistry profiles: load the relevant one

- **Lithium-sulfur:** sulfur fraction in composite, sulfur loading/areal capacity, electrolyte-to-sulfur ratio (E/S), lithium excess or N/P, shuttle and retention protocol. Do not rank only by specific capacity per gram of sulfur. See [Li-S benchmarking discussion](https://www.nature.com/articles/s41467-025-60528-4).
- **Solid-state batteries:** solid-electrolyte identity and thickness, fabrication pressure and *operating stack pressure* separately, interlayers, anode/reference (including In/Li), temperature, cycling protocol and reproducibility. “Solid-state” does not by itself imply a practical pressure or energy boundary. See [interlaboratory study](https://www.nature.com/articles/s41560-024-01634-3).
- **Aqueous zinc:** zinc thickness or inventory, Zn utilization/depth of discharge, cathode/anode balancing, electrolyte amount, loading, side-reaction/gas protocol, and replicates. An oversized zinc foil may hide poor utilization. See [experimental-practice analysis](https://www.nature.com/articles/s41467-022-28381-x).
- **Sodium-ion:** hard-carbon initial Coulombic efficiency, sodium inventory and presodiation, N/P, full-cell voltage, and energy normalization. Separate sodiation/desodiation branches and first/subsequent cycles. See [full-cell example](https://www.nature.com/articles/s41467-025-66492-3).
- **Flow batteries:** coulombic, voltage, and energy efficiency separately; state-of-charge range, concentration, membrane, current density, capacity utilization, cycle versus calendar time, symmetric versus full-cell setup, and whether pump power is included. See [performance assessment framework](https://www.nature.com/articles/s41560-020-00772-8).

For lithium-ion, lithium-metal, multivalent, metal-air, lead-acid, and emerging chemistries, derive an analogous condition set from the actual cell and claim. Add a profile only when repeated work justifies it; avoid assuming one chemistry's metric transfers unchanged to another.

## Mechanism and causal language

Separate what was directly measured from a correlation, computational support, or a hypothesis. A DFT adsorption-energy difference alone does not establish a kinetic catalytic pathway. Powder characterization may not represent an operating electrode. Ex situ, in situ, and operando experiments have different perturbations and limits; report those rather than using the labels as a hierarchy of prestige. [Operando methods discussion](https://www.nature.com/articles/s41467-022-32245-9) gives useful cautions. EIS fits are model-dependent; a smaller semicircle or assigned charge-transfer resistance is not stand-alone mechanism proof. Check measurement conditions and fit validity; see [EIS methods commentary](https://www.nature.com/articles/s43246-022-00284-w).

In prose and artwork, use calibrated language: `observed`, `consistent with`, `supports`, `suggests`, or `hypothesized`. Record contradictory results and likely causes, including configuration and protocol differences, before declaring consensus.
