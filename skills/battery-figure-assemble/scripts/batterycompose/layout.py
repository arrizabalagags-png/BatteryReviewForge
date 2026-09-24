"""Validate a physical-size panel grid before any input is transformed."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


class ComposeError(ValueError):
    """The source or layout contract cannot support a faithful composition."""


def _positive(value: object, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ComposeError(f"{name} must be a positive number") from exc
    if not math.isfinite(number) or number <= 0:
        raise ComposeError(f"{name} must be a positive finite number")
    return number


def _nonnegative(value: object, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ComposeError(f"{name} must be a non-negative number") from exc
    if not math.isfinite(number) or number < 0:
        raise ComposeError(f"{name} must be a non-negative finite number")
    return number


def load_manifest(path: str | Path) -> dict:
    path = Path(path).resolve()
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComposeError(f"Cannot read manifest: {path}") from exc
    if not isinstance(manifest, dict):
        raise ComposeError("Manifest must be a JSON object")
    manifest["_manifest_path"] = str(path)
    return manifest


def resolve_layout(manifest: dict) -> dict:
    if manifest.get("version") != 1:
        raise ComposeError("Manifest version must be 1")
    for key in ("figure_id", "claim"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ComposeError(f"{key} is required")
    width = _positive(manifest.get("width_mm"), "width_mm")
    if manifest.get("output_purpose", "manuscript") not in {"manuscript", "showcase"}:
        raise ComposeError("output_purpose must be manuscript or showcase")
    if manifest.get("layout_mode", "fixed") not in {"fixed", "editorial_pack"}:
        raise ComposeError("layout_mode must be fixed or editorial_pack")
    margin = _nonnegative(manifest.get("margin_mm", 4), "margin_mm")
    gutter = _nonnegative(manifest.get("gutter_mm", 2), "gutter_mm")
    label_band = _nonnegative(manifest.get("label_band_mm", 4), "label_band_mm")
    if type(manifest.get("draw_labels", True)) is not bool:
        raise ComposeError("draw_labels must be true or false")
    if manifest.get("draw_labels", True) and label_band < 3.5:
        raise ComposeError("draw_labels needs label_band_mm >= 3.5")
    row_heights = manifest.get("row_heights_mm")
    weights = manifest.get("col_weights")
    if not isinstance(row_heights, list) or not row_heights or len(row_heights) > 12:
        raise ComposeError("row_heights_mm must be a nonempty list of up to 12 rows")
    if not isinstance(weights, list) or not weights or len(weights) > 12:
        raise ComposeError("col_weights must be a nonempty list of up to 12 columns")
    row_heights = [_positive(value, "row height") for value in row_heights]
    weights = [_positive(value, "column weight") for value in weights]
    if label_band >= min(row_heights):
        raise ComposeError("label_band_mm must be smaller than every row")
    usable_width = width - 2 * margin - gutter * (len(weights) - 1)
    if usable_width <= 0:
        raise ComposeError("Margins and gutters leave no column width")
    col_widths = [usable_width * weight / sum(weights) for weight in weights]
    height = 2 * margin + sum(row_heights) + gutter * (len(row_heights) - 1)
    x_edges = [margin]
    for col_width in col_widths[:-1]:
        x_edges.append(x_edges[-1] + col_width + gutter)
    y_edges = [margin]
    for row_height in row_heights[:-1]:
        y_edges.append(y_edges[-1] + row_height + gutter)
    panels = manifest.get("panels")
    if not isinstance(panels, list) or not panels or len(panels) > 26:
        raise ComposeError("panels must contain 1 to 26 entries")
    occupancy = [[None] * len(weights) for _ in row_heights]
    ids: set[str] = set()
    paths: set[Path] = set()
    base = Path(manifest.get("_manifest_path", "manifest.json")).resolve().parent
    resolved = []
    for index, panel in enumerate(panels, 1):
        if not isinstance(panel, dict):
            raise ComposeError(f"Panel {index} must be an object")
        letter = panel.get("label")
        if not isinstance(letter, str) or not re.fullmatch(r"[a-z]", letter):
            raise ComposeError(f"Panel {index} needs a unique lowercase a-z label")
        if letter in ids:
            raise ComposeError(f"Duplicate panel label {letter}")
        ids.add(letter)
        for key in ("path", "role", "source_id", "rights_status"):
            if not isinstance(panel.get(key), str) or not panel[key].strip():
                raise ComposeError(f"Panel {letter}: {key} is required")
        rights = panel["rights_status"]
        if rights not in {"original", "licensed", "permission_granted", "pending", "unknown"}:
            raise ComposeError(f"Panel {letter}: invalid rights_status")
        if rights == "licensed" and not all(panel.get(k) for k in ("license", "credit")):
            raise ComposeError(f"Panel {letter}: licensed reuse needs license and credit")
        if rights == "permission_granted" and not panel.get("permission_record"):
            raise ComposeError(f"Panel {letter}: permission_granted needs permission_record")
        source = Path(panel["path"])
        source = (source if source.is_absolute() else base / source).resolve()
        if not source.is_file():
            raise ComposeError(f"Panel {letter}: source file does not exist: {source}")
        if source in paths and not panel.get("reuse_reason"):
            raise ComposeError(f"Panel {letter}: repeated source needs reuse_reason")
        paths.add(source)
        if source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".pdf", ".svg"}:
            raise ComposeError(f"Panel {letter}: unsupported input format")
        row, col = panel.get("row"), panel.get("col")
        rowspan, colspan = panel.get("rowspan", 1), panel.get("colspan", 1)
        if any(type(v) is not int for v in (row, col, rowspan, colspan)):
            raise ComposeError(f"Panel {letter}: row/col/spans must be integers")
        if row < 0 or col < 0 or rowspan < 1 or colspan < 1 or row + rowspan > len(row_heights) or col + colspan > len(weights):
            raise ComposeError(f"Panel {letter}: grid position is outside the canvas")
        for r in range(row, row + rowspan):
            for c in range(col, col + colspan):
                if occupancy[r][c] is not None:
                    raise ComposeError(f"Panel {letter} overlaps panel {occupancy[r][c]}")
                occupancy[r][c] = letter
        x = x_edges[col]
        y = y_edges[row]
        w = sum(col_widths[col:col + colspan]) + gutter * (colspan - 1)
        h = sum(row_heights[row:row + rowspan]) + gutter * (rowspan - 1)
        crop = panel.get("crop_px")
        vector_crop = panel.get("crop_box_fraction")
        if crop is not None and vector_crop is not None:
            raise ComposeError(f"Panel {letter}: use only one crop form")
        if crop is not None:
            if source.suffix.lower() in {".pdf", ".svg"}:
                raise ComposeError(f"Panel {letter}: crop_px is raster-only; edit vector source")
            if not isinstance(crop, list) or len(crop) != 4 or any(type(v) is not int for v in crop):
                raise ComposeError(f"Panel {letter}: crop_px must be four integer coordinates")
            if not panel.get("crop_reason"):
                raise ComposeError(f"Panel {letter}: explicit crop needs crop_reason")
        if vector_crop is not None:
            if source.suffix.lower() not in {".pdf", ".svg"}:
                raise ComposeError(f"Panel {letter}: crop_box_fraction is vector-only")
            if not isinstance(vector_crop, list) or len(vector_crop) != 4:
                raise ComposeError(f"Panel {letter}: crop_box_fraction needs four numbers")
            try:
                left, top, right, bottom = map(float, vector_crop)
            except (TypeError, ValueError) as exc:
                raise ComposeError(f"Panel {letter}: invalid crop_box_fraction") from exc
            if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
                raise ComposeError(f"Panel {letter}: crop_box_fraction outside the source")
            if not panel.get("crop_reason"):
                raise ComposeError(f"Panel {letter}: vector crop needs crop_reason")
        for field in ("content_box_fraction", "plot_box_fraction"):
            fraction = panel.get(field)
            if fraction is not None:
                if not isinstance(fraction, list) or len(fraction) != 4:
                    raise ComposeError(f"Panel {letter}: {field} needs [left, top, right, bottom]")
                try:
                    left, top, right, bottom = map(float, fraction)
                except (TypeError, ValueError) as exc:
                    raise ComposeError(f"Panel {letter}: invalid {field}") from exc
                if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
                    raise ComposeError(f"Panel {letter}: {field} outside the source")
        if type(panel.get("compound_panel", False)) is not bool:
            raise ComposeError(f"Panel {letter}: compound_panel must be true or false")
        resolved.append({**panel, "resolved_path": str(source),
                         "slot_mm": [x, y, w, h],
                         "art_mm": [x, y + label_band, w, h - label_band]})
    if not manifest.get("allow_empty_cells", False) and any(value is None for row in occupancy for value in row):
        raise ComposeError("Grid has unassigned cells; set allow_empty_cells with a reason if intentional")
    if manifest.get("allow_empty_cells") and not manifest.get("empty_cell_reason"):
        raise ComposeError("Empty cells need empty_cell_reason")
    dpi = manifest.get("dpi", 300)
    min_dpi = manifest.get("min_effective_dpi", 300)
    if type(dpi) is not int or dpi < 300 or type(min_dpi) is not int or min_dpi < 1:
        raise ComposeError("dpi must be >=300 and min_effective_dpi must be positive")
    return {**manifest, "width_mm": width, "height_mm": height,
            "margin_mm": margin, "gutter_mm": gutter, "label_band_mm": label_band,
            "col_widths_mm": col_widths, "panels": resolved,
            "occupancy": occupancy, "dpi": dpi, "min_effective_dpi": min_dpi}
