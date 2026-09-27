# CSV mapping contract

Input must be a UTF-8 or UTF-8-BOM comma-separated file with one header row. The helper keeps input row order and raw cell strings. It never merges sheets, interprets timestamps or changes units.

Example `mapping.json`:

```json
{
  "columns": {"cycle": "Cycle Index", "capacity": "Discharge capacity"},
  "units": {"cycle": "count", "capacity": "mAh g-1"},
  "numeric_columns": ["cycle", "capacity"],
  "author_confirmed": true,
  "plot_context": "Author checked cell identity, formation cycles, capacity mass basis and test conditions in the lab record",
  "plot_context_confirmed": true,
  "exclude_rows": [{"row_number": 4, "reason": "Author identified instrument setup row, not a measurement"}]
}
```

`columns` maps new column names to exact raw headers. `units` must name every mapped column; use `unitless` for IDs/categories, or `unknown` until the author confirms a scientific unit. `numeric_columns` identifies fields that must contain finite numbers in retained rows. `exclude_rows` is optional; each number is one-based after the header and requires a nonempty reason. An empty cell or invalid number in a retained numeric field fails with its row number. Unmapped source columns remain in the raw file and are listed in the preparation record, never silently mistaken for analyzed variables.

Set `author_confirmed: true` only after the author has checked the column meanings and units. Without it, `ready_for_plot` stays false even when the machine parsing checks pass.
Set `plot_context_confirmed: true` only after checking the relevant cell, step/branch, sign convention, normalization basis and test conditions against a lab record; describe what was checked in nonempty `plot_context`. A true flag is a record of author review, not machine verification. Without both fields, `ready_for_plot` stays false.

Inspect: `python scripts/prepare_csv.py inspect --input RAW.csv`.

Prepare: `python scripts/prepare_csv.py prepare --input RAW.csv --mapping mapping.json --output-dir NEW_DIRECTORY`.

The output directory contains `mapped.csv`, `prepare-record.json` and, if exclusions were requested, `excluded-rows.csv`. A preparation record is an audit trail, not proof that mapping or units are scientifically correct. Review the mapped table with the author before plotting.
