"""Inspect or plot author-supplied CSV/TSV/TXT/XLSX battery data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from batteryplot import (
    DataContractError, coulombic_efficiency, cycling_capacity, cycle_retention,
    nyquist, rate_capability, save_bundle, symmetric_voltage, voltage_capacity,
    tofsims_map, tofsims_depth,
)
from batteryplot.ingest import PLOT_COLUMNS, apply_mapping, inspect_table, read_table
from batteryplot.style import PRESETS, register_community_style


METADATA_FIELDS = frozenset({
    "kind", "style", "community_style_lock", "sheet", "columns", "common",
    "mode", "condition_note", "width_mm", "height_mm", "sample_id", "fragment",
    "claim", "caption_notes",
})


def render_from_metadata(data: Path, metadata: Path, *, style_override: str | None = None):
    """Validate author mappings and render; journal/export choices are separate."""
    config = json.loads(metadata.read_text(encoding="utf-8-sig"))
    if not isinstance(config, dict):
        raise DataContractError("Metadata must be a JSON object")
    unknown = set(config) - METADATA_FIELDS
    if unknown:
        hints = []
        if "figure_size_mm" in unknown:
            hints.append("Use width_mm and height_mm for figure size")
        if "dpi" in unknown:
            hints.append("Pass raster resolution with the --dpi CLI argument")
        raise DataContractError(
            f"Unknown metadata keys: {', '.join(sorted(unknown))}. "
            f"Allowed keys: {', '.join(sorted(METADATA_FIELDS))}. "
            + "; ".join(hints)
        )
    kind = config.get("kind")
    metadata_style = config.get("style")
    style = metadata_style if style_override is None else style_override
    config["style"] = style
    if not style:
        raise DataContractError("Missing style; ask the author to choose one shown by 'styles' and record it in metadata")
    community_provenance = None
    if style.startswith("community:"):
        if not config.get("community_style_lock"):
            raise DataContractError("Community style requires an explicitly selected local lock file")
        lock_path = Path(config["community_style_lock"])
        if not lock_path.is_absolute():
            lock_path = metadata.resolve().parent / lock_path
        pin, community_provenance = register_community_style(lock_path)
        if pin != style:
            raise DataContractError("Style name and community lock select different versions")
    if style not in PRESETS:
        raise DataContractError(f"Unknown style {style!r}; choose one of {', '.join(PRESETS)}")
    if kind not in PLOT_COLUMNS:
        raise DataContractError(f"Unknown plot kind {kind!r}; choose one of {', '.join(PLOT_COLUMNS)}")
    rows = apply_mapping(read_table(data, sheet=config.get("sheet")), config.get("columns", {}), config.get("common", {}))
    if not rows or not any(set(option) <= set(rows[0]) for option in PLOT_COLUMNS[kind]):
        raise DataContractError(f"Mapped table lacks core columns for {kind}")
    options = {key: config[key] for key in ("mode", "condition_note", "width_mm", "height_mm", "style") if key in config}
    if kind in {"tofsims_map", "tofsims_depth"}:
        if "sample_id" not in config or (kind == "tofsims_map" and "fragment" not in config):
            raise DataContractError("ToF-SIMS metadata needs sample_id and map plots also need fragment")
        tof_options = {key: config[key] for key in ("width_mm", "height_mm", "style") if key in config}
        fig, _ = (tofsims_map(rows, sample_id=config["sample_id"], fragment=config["fragment"], **tof_options)
                  if kind == "tofsims_map" else tofsims_depth(rows, sample_id=config["sample_id"], **tof_options))
    elif kind in {"full_cell_cycling", "half_cell_cycling"}:
        fig, _ = cycling_capacity(rows, cell_configuration=kind.split("_")[0], **options)
    else:
        handlers = {"coulombic_efficiency": coulombic_efficiency, "symmetric_cell_voltage": symmetric_voltage,
                    "voltage_capacity": voltage_capacity, "nyquist": nyquist, "cycle_retention": cycle_retention,
                    "rate_capability": rate_capability}
        fig, _ = handlers[kind](rows, **options)
    if not config.get("claim") or not config.get("caption_notes"):
        raise DataContractError("Metadata needs claim and caption_notes; preserve unknown scientific information explicitly")
    fig.batteryplot_meta["source_sha256"] = hashlib.sha256(data.read_bytes()).hexdigest()
    fig.batteryplot_meta["style_selection"] = {
        "metadata_style": metadata_style, "cli_style": style_override, "effective_style": style,
        "explicit_change": style_override is not None and style_override != metadata_style,
    }
    if community_provenance:
        fig.batteryplot_meta["community_style"] = community_provenance
    return fig, config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("styles", help="List named palette/style choices before plotting")
    inspect_cmd = sub.add_parser("inspect", help="Show sheets/columns and candidate plot families")
    inspect_cmd.add_argument("--data", type=Path, required=True)
    inspect_cmd.add_argument("--sheet")
    plot_cmd = sub.add_parser("plot", help="Render an author-reviewed mapping")
    plot_cmd.add_argument("--data", type=Path, required=True)
    plot_cmd.add_argument("--metadata", type=Path, required=True)
    plot_cmd.add_argument("--out", type=Path, required=True)
    plot_cmd.add_argument("--dpi", type=int, default=300, help="Raster preview DPI; a journal claim requires verified requirements")
    plot_cmd.add_argument("--style", help="Explicit author-selected palette change; omitted preserves metadata.style, input JSON is unchanged")
    args = parser.parse_args()
    try:
        if args.command == "styles":
            print(json.dumps({name: {key: preset[key] for key in ("label_zh", "label_en", "purpose", "swatches")}
                              for name, preset in PRESETS.items()}, ensure_ascii=False, indent=2))
            return
        if args.command == "inspect":
            rows = read_table(args.data, sheet=args.sheet)
            print(json.dumps(inspect_table(rows), ensure_ascii=False, indent=2))
            return
        fig, config = render_from_metadata(args.data, args.metadata, style_override=args.style)
        files = save_bundle(fig, args.out, claim=config["claim"], source_data=str(args.data),
                            caption_notes=config["caption_notes"], dpi=args.dpi, close=True)
        print(json.dumps({"kind": config["kind"], "files": [str(path) for path in files]}, ensure_ascii=False, indent=2))
    except (DataContractError, ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    from cli_runtime import configure_utf8
    configure_utf8()
    main()
