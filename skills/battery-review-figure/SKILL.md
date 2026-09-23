---
name: battery-review-figure
description: Plan or audit battery Review figures, and turn author-uploaded battery test data into traceable plots; check claims, test conditions, rights, and final-size quality.
---

# Figures for battery Reviews

The data-plotting route also works for author-owned experimental battery data when the manuscript is not a Review. Handle that plotting request here without invoking the whole Review writing workflow.

If a beginner asks vaguely to “make a battery figure,” read [the one-page figure router](references/FIGURE_ROUTER.md) and classify the input before choosing a specialist. Existing finished panels belong to `battery-figure-assemble`; raw numeric data and newly drawn diagrams belong here. The file extension only selects an ingestion method. Do not infer cell configuration, units, CE definition, test conditions, or the intended scientific claim from a filename.

Use this for conceptual diagrams, mechanism schemes, evidence maps, quantitative plots, visual abstracts, or figure audits. First read the owning section and decide the *one judgement* the figure helps the reader make. Use [FIGURE_LEDGER.md](assets/templates/FIGURE_LEDGER.md) only when the project lacks a figure record. For author-uploaded data, read [the plain-language upload route](references/UPLOADED_DATA.md), run `scripts/plot_uploaded.py inspect`, map columns and test conditions, then plot. For custom Python quantitative figures, read [the plotting library guide](references/PYTHON_PLOTTING.md) and import `scripts/batteryplot`. This does not require a second skill.

When the author supplies a set of existing image/PDF/SVG panels and wants them assembled, route the composition to `battery-figure-assemble`. It owns asset inventory, millimetre-grid placement, final panel labels, source/crop provenance and alignment QA. Keep this skill responsible for the figure's scientific claim, battery-specific comparability, caption and rights decisions.

For uploaded PPT/AI/PSD/reference collections, run `scripts/asset_inventory.py` to make a private metadata catalog. Read [the resource and redraw guide](references/RESOURCE_LIBRARY.md) before adapting a diagram. The bundled editable SVGs and theme are original starting points, not evidence. Never redistribute an unverified third-party asset or trace its pixels as a substitute for permission.

Before **final drawing or recoloring**, ask the author one short style question using the six options in [STYLE_PRESETS.md](references/STYLE_PRESETS.md), preferably with its preview. Reuse an already selected manuscript style; if the author explicitly delegates the choice, select and record one. Continue data inspection while waiting, but do not silently choose a final style. The upload CLI requires `style` in its metadata; original SVG templates can use `scripts/render_template.py`. Style never changes measurements, axes or evidence status.

When the chart family is unclear or a Review needs a planned figure set, use [the battery figure atlas](references/BATTERY_FIGURE_ATLAS.md) to choose the evidence role, axes, conditions and display type. Read only the relevant entries; it separates what the upload script can draw directly from figures needing raw spectra, image calibration, modelling details or a newly drawn schematic.

For illustrations based on author-supplied visual packs, read [the asset pattern atlas](references/ASSET_PATTERN_ATLAS.md) to distinguish useful battery components from decorative textures and unrelated subjects. Use original geometry and verified labels; do not move a licensed icon or an outdated mechanism into the public resource library by changing its color.

When the author asks for a more polished, less generic, or “less AI-looking” figure, use the [visual finishing guide](references/VISUAL_FINISH.md) before final drawing. Keep the request about editorial clarity and scientific fidelity: remove unhelpful effects and template clutter, show the source of every scientific detail, and preserve any journal-required AI-use disclosure. Render, inspect at final size, revise, and recheck rather than declaring the first preview finished.

## Plan the figure

Record the figure's audience, section owner, claim, panel purposes, underlying source IDs, and whether it shows an observation, a conditional comparison, a model, or a hypothesis. Match the target journal's current display-item count and format before creating artwork. If a figure has no distinct claim, combine or remove it. If the plan changes item numbering or ownership, update the manuscript brief and caption references together.

For cross-study plots, use like-for-like denominators and cell/test conditions. Label `NR` for a value checked and unreported, `NV` for not yet verified, uncertainty where available, and measured versus recalculated/modelled values. A direct ranking needs a stated comparability rule; when conditions differ, use grouped case studies or a conditions matrix. Mechanism arrows should distinguish observed steps from inferred pathways; visual confidence must not exceed the cited experiments.

## Python plotting route

1. Write the figure claim, panel role, final physical size, source-data path, and candidate caption before drawing. Use the original data; demo data in this skill is only for checking the package.
2. For cycle, rate, or bar plots, use the matching `batteryplot` function. Its field contract rejects missing required fields, nonnumeric values, mixed units, repeated indices, and differences among declared conditions. `evidence_state=verified` is the author's assertion, not an independent check by the code. A passing contract is only a starting point: confirm chemistry-specific conditions with `battery-metrics-audit` and inspect source data or cited pages. If important loading, N/P, electrolyte amount or protocol fields are absent, do not claim the program has established comparability.
3. When conditions differ, use `conditions_matrix` or an explicitly contextual line plot with a visible note. Do not use `comparison_bars` to rank unlike test conditions. Keep `NR`, `NV`, and zero distinct.
4. Export with `save_bundle` to a project workspace. It writes vector PDF/SVG, a 300 dpi or higher review raster, and a provenance JSON. PDF/SVG DPI is not a resolution claim. Inspect the final-size render for clipping, text, uncertainty, color and panel alignment; verify current journal format rules before submitting.
5. Put code, input data, output figures, caption and figure ledger entry together in the manuscript workspace. Preserve source permissions for adapted artwork. No automated style or geometry check can certify the scientific interpretation.

## Four release checks

1. **Science:** every number, arrow, maturity label, “absent” cell, and causal connector has a source trace and appropriate uncertainty or caveat. Check half/full, coin/pouch, charge/discharge, cycle index, normalization, electrolyte, loading, pressure, and temperature as relevant.
2. **Editorial:** the item supports its section, the panel order tells a clear story, the caption defines symbols and boundaries, and no table cell silently means zero when it means unreported.
3. **Production:** inspect the *final submission size* for text and line readability, effective raster resolution, font embedding, color contrast, and the journal's accepted formats. An editable SVG wrapper does not repair low-resolution embedded image panels.
4. **Rights:** document original creation, adapted source, license, permission status and evidence, and exact required credit. A polished credit line is not proof of permission. Prefer original diagrams derived from cited findings when possible, while tracing those findings.

For a newly created item, deliver the source artwork or reproducible plotting file when feasible, export in the requested formats, caption, source/data and rights ledger, and any remaining checks. For an audit, report specific panel-level failures and fixes. Keep project figures in the user's manuscript workspace, not in the installed skill folder.
