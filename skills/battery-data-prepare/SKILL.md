---
name: battery-data-prepare
description: Inspect author-owned battery instrument CSV exports, map columns and units explicitly, and prepare a traceable clean table without silently deleting or converting observations.
---

# Prepare battery test data

Use this before plotting when the author brings raw cycling, impedance, spectroscopy or other instrument tables. Start by inventorying files and reading a few rows; an extension or instrument filename does not identify the experiment, voltage reference, capacity basis or units. Keep the raw export untouched in the author's workspace. Do not upload unpublished data to a public repository or issue.

For a plain CSV, run `python scripts/prepare_csv.py inspect --input RAW.csv`. It reports headers, row count, blanks and whether values are parseable as numbers; it does **not** assign scientific meanings. Ask the author to confirm the mapping, units and protocol where they are ambiguous. Then make a mapping JSON following [the exact schema and example](references/MAPPING_CONTRACT.md) and run `python scripts/prepare_csv.py prepare --input RAW.csv --mapping MAP.json --output-dir NEW_DIRECTORY`. The helper refuses an existing output directory, preserves row order and cell values, and writes `mapped.csv` plus a machine-readable record of hashes, mapping, units and every explicitly excluded row. It never converts units or drops a bad value on its own. For Excel or proprietary formats, inspect/export with a suitable available reader and document the export step before using this CSV helper.

Treat preparation as ready for quantitative plotting only after the author confirms cell configuration, branch/step identity, time or cycle basis, sign convention, normalization denominator and relevant test conditions. Record that review in `plot_context` and set `plot_context_confirmed: true` only after the author checks it; this is required for the helper's `ready_for_plot` flag. The flag records a human decision and does not prove the conditions correct. Unknown units remain `unknown` in the record and also block readiness. Do not guess units from magnitudes or convert mA to mA cm⁻² without measured area. Keep zero, missing, instrument flags and rejected points distinct. An exclusion requires a specific row number and reason supplied by the author; report how many rows remain and show exclusions for approval.

Return the raw file path/hash, mapped column table, declared units, unresolved questions, any exclusions and the prepared file path. Route plotting to `battery-review-figure`; route cross-study metric comparisons to `battery-metrics-audit`. This skill prepares evidence, not a scientific interpretation.
