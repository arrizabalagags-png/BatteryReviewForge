# Optional Battery Commons resources

Battery Commons is an opt-in collection of versioned palettes and layouts maintained at the [public catalog](https://arrizabalagags-png.github.io/BatteryReviewForge/commons/catalog.json). The six presets in `assets/figure_theme.json` remain the default for regular work. A public submission is not automatically a scientific recommendation. `community`, `reviewed`, `verified`, and `core` are distinct stages; no resource may claim a higher status merely from popularity or a passing JSON check.

Only when the author asks to browse or use community resources:

1. Show at most three resources and their exact `id@version`, author, license, review status, and relevant preview. Ask which one fits the manuscript's existing style; never silently substitute a newer version.
2. Resolve the exact choice with `python scripts/community_registry.py community:ocean-electrolyte@1.0.0 --allow-network --out <project>/commons-locks`. The script fetches only official HTTPS JSON, checks SHA-256 against the catalog and creates a local `.lock.json`. If the author provided a local catalog, use `--catalog <path>` without network access.
3. For an uploaded-data plot set `"style": "community:ocean-electrolyte@1.0.0"` and `"community_style_lock": "<project>/commons-locks/ocean-electrolyte@1.0.0.lock.json"` in the mapping file. Plotting reads the local JSON only, verifies its hash again, and records asset ID, version, source URL, SHA-256, retrieval time and review status in `.provenance.json`.
4. Check series distinction, line styles, final-size readability, print output and the manuscript's color identity before release. An automated color-vision preview is only a screening aid.

For community layouts, inspect the panel evidence and physical ruler as usual. The layout JSON never overrides experimental grammar, panel pairing, required scale bars or author approval. Do not download or execute community code. Any future parser must be included in a reviewed release with tests, not run directly from the registry.

Public submissions need author credit and license. Public display, inclusion in the library, automated testing and future model training are separate permissions; training must be independently opted into and defaults off. Do not upload unpublished data or copied paper figures to public Issues. Community feedback improves rules and presets; this project does not call that model training.
