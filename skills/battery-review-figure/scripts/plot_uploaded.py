"""Inspect or plot author-supplied CSV/TSV/TXT/XLSX battery data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from batteryplot import (
    DataContractError, coulombic_efficiency, cycling_capacity, cycle_retention,
    nyquist, rate_capability, save_bundle, symmetric_voltage, voltage_capacity,
)
from batteryplot.ingest import PLOT_COLUMNS, apply_mapping, inspect_table, read_table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_cmd = sub.add_parser("inspect", help="Show sheets/columns and candidate plot families")
    inspect_cmd.add_argument("--data", type=Path, required=True)
    inspect_cmd.add_argument("--sheet")
    plot_cmd = sub.add_parser("plot", help="Render an author-reviewed mapping")
    plot_cmd.add_argument("--data", type=Path, required=True)
    plot_cmd.add_argument("--metadata", type=Path, required=True)
    plot_cmd.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            rows = read_table(args.data, sheet=args.sheet)
            print(json.dumps(inspect_table(rows), ensure_ascii=False, indent=2))
            return
        config = json.loads(args.metadata.read_text(encoding="utf-8"))
        kind = config.get("kind")
        if kind not in PLOT_COLUMNS:
            raise DataContractError(f"Unknown plot kind {kind!r}; choose one of {', '.join(PLOT_COLUMNS)}")
        rows = apply_mapping(read_table(args.data, sheet=config.get("sheet")),
                             config.get("columns", {}), config.get("common", {}))
        if not any(set(option) <= set(rows[0]) for option in PLOT_COLUMNS[kind]):
            raise DataContractError(f"Mapped table lacks core columns for {kind}")
        options = {key: config[key] for key in ("mode", "condition_note", "width_mm", "height_mm") if key in config}
        if kind in {"full_cell_cycling", "half_cell_cycling"}:
            fig, _ = cycling_capacity(rows, cell_configuration=kind.split("_")[0], **options)
        elif kind == "coulombic_efficiency":
            fig, _ = coulombic_efficiency(rows, **options)
        elif kind == "symmetric_cell_voltage":
            fig, _ = symmetric_voltage(rows, **options)
        elif kind == "voltage_capacity":
            fig, _ = voltage_capacity(rows, **options)
        elif kind == "nyquist":
            fig, _ = nyquist(rows, **options)
        elif kind == "cycle_retention":
            fig, _ = cycle_retention(rows, **options)
        else:
            fig, _ = rate_capability(rows, **options)
        fig.batteryplot_meta["source_sha256"] = hashlib.sha256(args.data.read_bytes()).hexdigest()
        files = save_bundle(fig, args.out, claim=config["claim"], source_data=str(args.data),
                            caption_notes=config["caption_notes"], close=True)
        print(json.dumps({"kind": kind, "files": [str(path) for path in files]}, ensure_ascii=False, indent=2))
    except (DataContractError, KeyError, json.JSONDecodeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
