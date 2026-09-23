# Maintainer guide: design decisions and release gates

This document records why the skill is shaped as it is and what to inspect before a release. It is not an extra instruction file for every user task.

## Questions the design must answer

1. **What is the requested stage?** A topic pitch, performance-table audit, paragraph edit, figure, preflight, and reviewer response need different outputs. Each has a separate skill; the coordinator is for multi-stage work.
2. **What kind of Review is claimed?** Narrative, scoping, systematic, and Perspective articles have different evidence and reporting obligations. Apply PRISMA only to a review designed for it.
3. **How is novelty demonstrated?** Compare actual inspected content of close Reviews. “First,” “comprehensive,” and “more references” are not a contribution by themselves.
4. **How much primary evidence was truly read?** Count discovery records, verified metadata, full texts, SI, extracted studies, and claim-used studies separately. Do not confuse library size with evidence depth.
5. **Which numbers can be compared?** Battery results change with cell architecture, normalization, loading, electrolyte, rate, temperature, pressure, and cycling protocol. Missing conditions must remain visible. A and B are comparison-specific labels, never a global quality grade for a paper.
6. **What does a figure actually assert?** A polished schematic can still overclaim a mechanism; an editable wrapper can contain unusable raster panels; a credit line can exist without reuse permission. Check science, editing, production, and rights separately.
7. **What controls long projects?** A current brief plus a decision log prevents old outlines, figure numbers, or titles from silently returning. The brief can be amended when evidence warrants it.
8. **Which journal rules apply now?** Article type and date matter. Conflicting requirements stay unresolved until checked with the official source or corresponding author.
9. **What counts as independent review?** Freeze the input, keep the original assessment, and distinguish responding to comments from re-reviewing a revised version.
10. **How does the workflow survive model updates?** Define outcomes and evidence standards, route detail on demand, and test behavior with realistic tasks. Do not encode model names, quotas, or mandatory rereading rituals in the skill.
11. **What may be public?** Only original general instructions, blank templates, and shareable examples belong here. Keep project manuscripts, PDFs, figures, reviewer materials, and institutional access details outside this repository.
12. **Which figure specialist owns the request?** `battery-review-figure` owns scientific claims, uploaded-table plotting, captions and source rights; `battery-figure-assemble` owns supplied-panel geometry and final-size composite QA. A narrow primary-data plot does not trigger the full Review coordinator.
13. **How are reference asset packs handled?** Hash and index them in a private output, deduplicate logically, verify rights, then redraw original editable templates from checked facts. Never import a third-party PPT/AI/PSD pack into the public plugin merely because it is present locally.
14. **How does a novice get one coherent style?** Route by raw data, new schematic or completed panel rather than extension; ask for one named style before final drawing, reuse it across the manuscript, and record it in provenance. Light swatches may be backgrounds but plotted series should remain legible at final size.

## Release checklist

- Skill name, description, and file layout validate; all reference links resolve.
- Direct and implicit battery-Review requests reach the right specialist; the coordinator does not swallow figure or polish requests; unrelated primary-paper requests do not.
- At least one comparison fixture makes the skill reject a misleading ranking and mark missing fields.
- At least one incomplete-source case makes the skill report uncertainty instead of inventing data or citations.
- A reviewer-response case maps every point to a verified manuscript location.
- Journal checks use current official guidance for the exact article type and preserve unresolved conflicts.
- Public-diff inspection finds no unpublished research data, downloaded PDFs, private paths, credentials, or third-party artwork.
- README installation instructions and both language sections still match the actual package.
- Uploaded CSV and XLSX examples render all supported battery-specific plot families; condition mismatches, uncertain CE definitions and mixed full/half-cell inputs fail visibly.
- Multi-panel PDF/PNG/SVG composition passes grid/plot-area tests and a human visual check at final size; PDF text scanners with transformed SVG fonts are investigated, not blindly ignored.
- All named figure styles render with series contrast on white, are selectable through the upload CLI, and recolor only original SVG templates; the workflow asks rather than guesses when no style is recorded.
- Public sample figures use reproducible drawing sources and clearly marked invented data, have a visible evidence hierarchy at both website and print sizes, and avoid decorative effects that distract from axes, scales or provenance. Apply the [visual finishing guide](../skills/battery-review-figure/references/VISUAL_FINISH.md) to sample and manuscript figures.

Use [test scenarios](../tests/scenarios.md) to evaluate an update. Record the observed artifact and decision, not just whether wording matched an expected phrase. Fix demonstrated failure modes narrowly; do not grow the entry point with another universal rule for every edge case.

## Versioning

The `plugin.json` version describes this package, not the maturity of battery science. A patch release clarifies or corrects an existing workflow; a minor release adds a profile or mode without breaking old behavior; a major release changes public structure or interpretation rules. Re-check links and venue-dependent claims before tagging any release. Keep chemistry examples and standards tied to their source and applicable scope.
