---
name: battery-figure-assemble
description: Assemble supplied PNG, TIFF, PDF, and SVG panels into aligned, source-traceable multi-panel figures for battery papers and Reviews; inspect layout, labels, resolution, rights, and final-size readability.
---

# Assemble battery manuscript figures

Use this specialist when an author supplies several finished plots, microscopy images, spectra, diagrams, or exported panels and asks for a coherent manuscript figure. For drawing a new quantitative panel from data, use `battery-review-figure` first. Read [the composition guide](references/COMPOSITION.md) for the manifest and CLI only when assembling or auditing files. When panel order or grid choice is unclear, use the [plain-language layout recipes](references/LAYOUT_RECIPES.md) before writing the manifest.

If the task is only to place existing panels, preserve their data encoding and ask for a style choice only when the author wants a redesign and no manuscript style is recorded. If editable panels need a shared palette, route their regeneration to `battery-review-figure` and its [style choices](../battery-review-figure/references/STYLE_PRESETS.md) before assembly. Do not recolor microscopy, spectra intensity, heatmaps or published panels merely to make them match a decorative palette.

For an author request to make the composite look less generic or less AI-made, apply the figure skill's [visual finishing guide](../battery-review-figure/references/VISUAL_FINISH.md) to hierarchy, typography and decoration. Keep the supplied panels' scientific content and provenance intact; visual polish never authorizes changing data or hiding AI assistance.

## Figure contract before layout

Write one sentence stating the whole figure's claim. For each candidate panel, record its distinct evidence role, source file and source ID, test conditions, intended letter, copyright/permission state, and whether it contains existing labels, scale bars or legends. Remove redundant panels or move them to another figure before shrinking everything to fit. Preserve the author's approved panel order where it supports the argument.

For battery evidence, check that the assembly does not imply unsupported comparability: half versus full cell, coin versus pouch, charge versus discharge, normalization basis, sulfur/active loading, E/S, N/P, stack pressure, temperature, current/rate, cycle window and areal capacity as relevant. Do not visually merge results with different boundaries into a ranking without a stated comparison rule. Microscopy panels need an intact scale bar and calibration; paired images need comparable acquisition/display settings or a clear caption caveat.

## Assemble and iterate

1. Run the bundled `compose_figure.py inventory` on the figure-level source folder. Inspect the contact sheets and every candidate at readable size. The white-border estimates are hints, never automatic crop instructions.
2. Set target width from the current journal guide when a venue is named; use an explicitly provisional width otherwise. Choose a grid in millimetres with one hero panel only when its evidence role warrants it. Give comparable plots the same slot class and record their actual plot-area rectangles for alignment audit.
3. Make a project-local JSON manifest. The script requires exact grid occupancy, source IDs, rights states and physical sizes. It never stretches artwork. Cropping is explicit and requires a reason; keep axes, uncertainty, legends, scale bars and all relevant image content. If source margins prevent a clean assembly, regenerate the source panel at a fixed canvas where possible.
4. Run `compose_figure.py compose`. Inspect the PDF and PNG at final print size, the alignment overlay, each panel crop, and the JSON report. Fix unequal visual margins, mismatched plot areas, letter placement, typography, color semantics, ambiguous legends, low effective DPI and unintended overlaps. Recompose after every adjustment.
5. Deliver the manifest, untouched originals or their project-local references, composite PDF, PNG preview, caption, source/rights ledger and QA report. A clean grid is a geometry check, not proof that the science or rights are correct. Mark unresolved source, permission or visual issues as a draft rather than a submission-ready figure.

The script preserves PDF/SVG vectors when feasible and uses raster content as raster. Its geometry report can verify frames and declared plot boxes; a human must still inspect all rendered marks and text. Never describe a raster panel inside a PDF as fully editable.
