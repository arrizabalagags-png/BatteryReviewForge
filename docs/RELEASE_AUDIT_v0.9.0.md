# v0.9.0 scientific package audit

Date: 2026-09-27. The website is maintained separately; no new website development source or author payment image is included in this repository or skill ZIP.

## Delivered

- 15 narrowly scoped skills; new `battery-data-prepare` and `battery-experiment-plan` have explicit inputs, outputs, unknown-condition handling, and routes to plotting.
- 30 synthetic showcase groups, including four new optional protocols/displays. The new renderer contracts and primary-paper Figure/Panel references are in [ELECTROCHEM_RECIPES.md](../skills/battery-review-figure/references/ELECTROCHEM_RECIPES.md).
- Reworked existing full-cell, Li||Cu CE, Li||Li, EIS and ToF-SIMS display spacing/axis domains/legends. The operando XRD data display was reviewed and retained. EIS now records post-draw physical plot-box alignment.
- Full and WorkBuddy packages built for v0.9.0; all 15 skills are included in full packages. WorkBuddy Starter deliberately contains only figure and assembly; the website offers separate additional-skill import instructions.

## Verified

- Full Python suite: **78 tests passed**, including data interpretation guardrails, new protocols, plotting, layout, community records and installer backups.
- Initial package test caught missing ZIPs for four new sample groups. The bundles were generated; all four installation/package tests then passed, followed by the full 78-test run.
- ZIP extracted into a fresh temporary directory; its bundled `render_specialist.py` successfully generated Aurbach PNG/SVG/PDF/provenance from the saved demo CSV and metadata.
- Tracked source checks passed. The newly staged Matplotlib SVG exports contain generated path-line trailing spaces, with no rendering impact; a completely clean whitespace check over all exported artifacts is not claimed. New skills have valid skill frontmatter and local references.
- The original author payment image and private website files are absent from the downloadable scientific package.

## Practical limits

Examples remain synthetic and are never evidence for battery performance. Each new display is an optional variant, not a universal default supported by three independently audited papers. The 51-paper corpus has not been completely visually distilled into verified templates. Native AI-app installation, a real novice study, live WeChat payment and performance benchmarks were not performed in this release. Code tests are not those validations.
