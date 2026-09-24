"""Assemble a fixed-size PDF and review PNG with geometry/provenance QA."""

from __future__ import annotations

import io
import json
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter, Transformation
import pypdfium2 as pdfium
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .assets import load_asset, preview_loaded, white_inset_fraction
from .fonts import audit_fonts
from .layout import ComposeError, resolve_layout


PT_PER_MM = 72 / 25.4


def _fit(source_w: float, source_h: float, slot: list[float]) -> list[float]:
    x, y, width, height = slot
    factor = min(width / source_w, height / source_h)
    actual_w, actual_h = source_w * factor, source_h * factor
    return [x + (width - actual_w) / 2, y + (height - actual_h) / 2, actual_w, actual_h]


def _fraction_rect(fraction: list[float], placed: list[float]) -> list[float]:
    left, top, right, bottom = map(float, fraction)
    x, y, width, height = placed
    return [x + left * width, y + top * height,
            (right - left) * width, (bottom - top) * height]


def _auto_rows(manifest: dict) -> dict:
    """Opt-in row sizing from the supplied panels' actual page/image aspect ratios.

    Spanning rows need editorial choice, so their heights remain explicit.
    This never crops or stretches an input.
    """
    if manifest.get("layout_mode") != "editorial_pack" or manifest.get("row_heights_mm") != "auto":
        return manifest
    weights = manifest.get("col_weights")
    panels = manifest.get("panels")
    if not isinstance(weights, list) or not isinstance(panels, list) or not panels:
        raise ComposeError("editorial_pack auto rows need col_weights and panels")
    if any(p.get("rowspan", 1) != 1 for p in panels):
        raise ComposeError("editorial_pack auto rows cannot contain row-spanning panels; set row heights explicitly")
    width = float(manifest["width_mm"])
    margin = float(manifest.get("margin_mm", 3))
    gutter = float(manifest.get("gutter_mm", 2))
    label = float(manifest.get("label_band_mm", 4))
    usable = width - 2 * margin - gutter * (len(weights) - 1)
    col_widths = [usable * float(w) / sum(map(float, weights)) for w in weights]
    base = Path(manifest.get("_manifest_path", "manifest.json")).resolve().parent
    heights = [0.0] * (1 + max(int(p["row"]) for p in panels))
    for panel in panels:
        path = Path(panel["path"])
        path = (path if path.is_absolute() else base / path).resolve()
        asset = load_asset({**panel, "resolved_path": str(path)})
        if asset["kind"] == "raster":
            source_w, source_h = asset["image"].size
        else:
            box = asset["pdf_page"].cropbox
            source_w, source_h = float(box.width), float(box.height)
        col, span = int(panel["col"]), int(panel.get("colspan", 1))
        slot_w = sum(col_widths[col:col + span]) + gutter * (span - 1)
        if panel.get("content_box_fraction"):
            l, t, r, b = map(float, panel["content_box_fraction"])
            source_w *= r - l
            source_h *= b - t
        desired = slot_w * source_h / source_w + label
        if panel.get("compound_panel"):
            desired = max(desired, 55)
        heights[int(panel["row"])] = max(heights[int(panel["row"])], desired)
    if any(h <= label for h in heights):
        raise ComposeError("editorial_pack auto rows need at least one panel in every row")
    return {**manifest, "row_heights_mm": [round(h, 3) for h in heights],
            "auto_row_heights_mm": [round(h, 3) for h in heights]}


def _top_to_pdf(rect: list[float], page_height_mm: float) -> tuple[float, float, float, float]:
    x, y, width, height = rect
    return (x * PT_PER_MM, (page_height_mm - y - height) * PT_PER_MM,
            width * PT_PER_MM, height * PT_PER_MM)


def _plot_rect(panel: dict, placed: list[float]) -> list[float] | None:
    fraction = panel.get("plot_box_fraction")
    if fraction is None:
        return None
    if not isinstance(fraction, list) or len(fraction) != 4:
        raise ComposeError(f"Panel {panel['label']}: plot_box_fraction must be [left, top, right, bottom]")
    try:
        left, top, right, bottom = map(float, fraction)
    except (TypeError, ValueError) as exc:
        raise ComposeError(f"Panel {panel['label']}: invalid plot_box_fraction") from exc
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ComposeError(f"Panel {panel['label']}: plot_box_fraction outside image")
    x, y, width, height = placed
    return [x + left * width, y + top * height,
            (right - left) * width, (bottom - top) * height]


def _alignment_audit(panels: list[dict], tolerance_mm: float = 1.5 / PT_PER_MM) -> dict:
    """Measure final-size plot rectangles, never just equal outer grid cells.

    A mixed-content panel may be independent, but the author must say why.
    This prevents a missing group from silently turning a comparison into PASS.
    """
    issues: list[str] = []
    checks: list[dict] = []
    groups: dict[str, list[dict]] = {}
    if len(panels) > 1:
        for panel in panels:
            intent = panel.get("alignment_intent")
            if intent not in {"compare", "independent"}:
                issues.append(f"Panel {panel['label']}: alignment_intent is required (compare or independent)")
            elif intent == "independent" and not panel.get("alignment_reason"):
                issues.append(f"Panel {panel['label']}: independent panel needs alignment_reason")
            elif intent == "compare" and not panel.get("alignment_group"):
                issues.append(f"Panel {panel['label']}: comparable panel needs alignment_group")
            elif intent == "compare" and panel.get("plot_rect_mm") is None:
                issues.append(f"Panel {panel['label']}: comparable panel needs measured plot_box_fraction")
    for panel in panels:
        if panel.get("alignment_group"):
            groups.setdefault(str(panel["alignment_group"]), []).append(panel)
    for name, members in groups.items():
        if len(members) < 2:
            issues.append(f"Alignment group {name} has only one panel")
            continue
        if any(member["plot_rect_mm"] is None for member in members):
            issues.append(f"Alignment group {name} needs plot_box_fraction on every panel")
            continue
        group_check_count = len(checks)
        for i, first in enumerate(members):
            for second in members[i + 1:]:
                a, b = first["plot_rect_mm"], second["plot_rect_mm"]
                a_slot, b_slot = first["slot_mm"], second["slot_mm"]
                same_row = abs(a_slot[1] - b_slot[1]) < 1e-6 and abs(a_slot[3] - b_slot[3]) < 1e-6
                same_col = abs(a_slot[0] - b_slot[0]) < 1e-6 and abs(a_slot[2] - b_slot[2]) < 1e-6
                for direction, comparable, edge_names, values in (
                    ("row", same_row, ("top", "bottom", "height"),
                     ((a[1], b[1]), (a[1] + a[3], b[1] + b[3]), (a[3], b[3]))),
                    ("column", same_col, ("left", "right", "width"),
                     ((a[0], b[0]), (a[0] + a[2], b[0] + b[2]), (a[2], b[2]))),
                ):
                    if not comparable:
                        continue
                    for edge, (first_value, second_value) in zip(edge_names, values):
                        delta = abs(first_value - second_value)
                        checks.append({"group": name, "panels": [first["label"], second["label"]],
                                       "direction": direction, "edge": edge,
                                       "first_mm": round(first_value, 4),
                                       "second_mm": round(second_value, 4),
                                       "delta_mm": round(delta, 4),
                                       "pass": delta <= tolerance_mm})
                        if delta > tolerance_mm:
                            issues.append(f"Group {name}: panels {first['label']}/{second['label']} plot-area {direction} {edge} differs by {delta:.2f} mm")
        if len(checks) == group_check_count:
            issues.append(f"Group {name}: no members share a row or column; declare a meaningful comparison or independent reasons")
    if len(panels) > 1 and not groups and not issues:
        # Mixed content can be valid, but it has no common plot ruler.
        status = "independent_panels_visual_review_required"
    else:
        status = "fix_before_delivery" if issues else "geometry_pass_visual_review_required"
    return {"status": status, "tolerance_pt": 1.5,
            "tolerance_mm": round(tolerance_mm, 4), "checks": checks, "issues": issues}


def compose(manifest: dict, stem: str | Path, *, strict: bool = False) -> dict:
    """Produce PDF, PNG, and JSON. In strict mode, review warnings block output."""
    layout = resolve_layout(_auto_rows(manifest))
    prepared = []
    warnings = []
    for panel in layout["panels"]:
        asset = load_asset(panel)
        if asset["kind"] == "raster":
            source_w, source_h = asset["image"].size
        else:
            box = asset["pdf_page"].cropbox
            source_w, source_h = float(box.width), float(box.height)
        if source_w <= 0 or source_h <= 0:
            raise ComposeError(f"Panel {panel['label']}: invalid source dimensions")
        placed = _fit(source_w, source_h, panel["art_mm"])
        effective_dpi = None
        if asset["kind"] == "raster":
            effective_dpi = min(source_w / (placed[2] / 25.4), source_h / (placed[3] / 25.4))
            if effective_dpi < layout["min_effective_dpi"]:
                warnings.append(f"Panel {panel['label']}: effective raster resolution {effective_dpi:.0f} dpi is below {layout['min_effective_dpi']}")
        insets = white_inset_fraction(preview_loaded(asset))
        if max(insets) > 0.18:
            warnings.append(f"Panel {panel['label']}: source has a large white edge ({max(insets):.0%}); inspect before an explicit crop")
        visible = [placed[0] + insets[0] * placed[2], placed[1] + insets[1] * placed[3],
                   (1 - insets[0] - insets[2]) * placed[2],
                   (1 - insets[1] - insets[3]) * placed[3]]
        measured_content = (_fraction_rect(panel["content_box_fraction"], placed)
                            if panel.get("content_box_fraction") else None)
        content = measured_content or visible
        content_basis = "declared" if measured_content else "white_edge_estimate"
        fill = (placed[2] * placed[3]) / (panel["art_mm"][2] * panel["art_mm"][3])
        slot_fill = (content[2] * content[3]) / (panel["art_mm"][2] * panel["art_mm"][3])
        if fill < 0.65:
            warnings.append(f"Panel {panel['label']}: artwork fills only {fill:.0%} of its slot; inspect whitespace or redesign the grid")
        if layout.get("layout_mode") == "editorial_pack" and slot_fill < .78 and not panel.get("whitespace_reason"):
            warnings.append(f"Panel {panel['label']}: visible content fills only {slot_fill:.0%} of its slot; rerender native plots at slot size or record a scientific whitespace_reason")
        if panel.get("compound_panel") and panel["art_mm"][2] < 70:
            warnings.append(f"Panel {panel['label']}: compound panel is under 70 mm wide; split/rerender its children or allocate a hero slot")
        if panel["rights_status"] in {"pending", "unknown"}:
            warnings.append(f"Panel {panel['label']}: reuse rights are {panel['rights_status']}")
        info = {"label": panel["label"], "role": panel["role"], "source_id": panel["source_id"],
                "rights_status": panel["rights_status"], "source_path": panel["path"],
                "license": panel.get("license"), "credit": panel.get("credit"),
                "permission_record": panel.get("permission_record"),
                "sha256": asset["sha256"], "format": asset["format"],
                "kind": asset["kind"], "slot_mm": panel["slot_mm"],
                "placed_mm": [round(v, 4) for v in placed],
                "visible_content_estimate_mm": [round(v, 4) for v in visible],
                "content_bbox_mm": [round(v, 4) for v in content],
                "content_bbox_basis": content_basis,
                "white_inset_fraction_candidate": insets,
                "plot_rect_mm": _plot_rect(panel, placed),
                "effective_dpi": round(effective_dpi, 1) if effective_dpi is not None else None,
                "fill_fraction": round(fill, 3), "crop_px": panel.get("crop_px"),
                "slot_fill_ratio": round(slot_fill, 3),
                "compound_panel": panel.get("compound_panel", False),
                "whitespace_reason": panel.get("whitespace_reason"),
                "crop_box_fraction": panel.get("crop_box_fraction"),
                "crop_reason": panel.get("crop_reason"),
                "alignment_group": panel.get("alignment_group"),
                "alignment_intent": panel.get("alignment_intent"),
                "alignment_reason": panel.get("alignment_reason")}
        prepared.append((panel, asset, placed, info))
    infos = [item[3] for item in prepared]
    gap_measurements = []
    for index, first in enumerate(infos):
        for second in infos[index + 1:]:
            a, b = first["content_bbox_mm"], second["content_bbox_mm"]
            sa, sb = first["slot_mm"], second["slot_mm"]
            same_row = abs(sa[1] - sb[1]) < 1e-6
            between_in_row = any(abs(other["slot_mm"][1] - sa[1]) < 1e-6 and
                                 sa[0] < other["slot_mm"][0] < sb[0]
                                 for other in infos if other is not first and other is not second)
            if same_row and sa[0] < sb[0] and not between_in_row:
                gap_measurements.append({"panels": [first["label"], second["label"]],
                                         "direction": "horizontal", "interpanel_gap_mm": round(b[0] - a[0] - a[2], 3)})
            same_column = abs(sa[0] - sb[0]) < 1e-6
            between_in_column = any(abs(other["slot_mm"][0] - sa[0]) < 1e-6 and
                                    sa[1] < other["slot_mm"][1] < sb[1]
                                    for other in infos if other is not first and other is not second)
            if same_column and sa[1] < sb[1] and not between_in_column:
                gap_measurements.append({"panels": [first["label"], second["label"]],
                                         "direction": "vertical", "interpanel_gap_mm": round(b[1] - a[1] - a[3], 3)})
    if infos:
        x0 = min(p["content_bbox_mm"][0] for p in infos)
        y0 = min(p["content_bbox_mm"][1] for p in infos)
        x1 = max(p["content_bbox_mm"][0] + p["content_bbox_mm"][2] for p in infos)
        y1 = max(p["content_bbox_mm"][1] + p["content_bbox_mm"][3] for p in infos)
        outer_whitespace_ratio = round(1 - (x1 - x0) * (y1 - y0) /
                                       (layout["width_mm"] * layout["height_mm"]), 3)
    else:
        outer_whitespace_ratio = 1.0
    if layout.get("layout_mode") == "editorial_pack":
        for gap in gap_measurements:
            if gap["interpanel_gap_mm"] > 4 and not all(
                next(p for p in infos if p["label"] == letter).get("whitespace_reason")
                for letter in gap["panels"]):
                warnings.append(f"Panels {'/'.join(gap['panels'])}: visible gap is {gap['interpanel_gap_mm']:.1f} mm; review editorial packing")
    alignment_audit = _alignment_audit(infos)
    warnings.extend(alignment_audit["issues"])
    if strict and warnings:
        raise ComposeError("Strict assembly blocked: " + "; ".join(warnings))
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    pdf_path, png_path, qa_path = (stem.with_suffix(suffix) for suffix in (".pdf", ".png", ".qa.json"))
    page_width_pt, page_height_pt = layout["width_mm"] * PT_PER_MM, layout["height_mm"] * PT_PER_MM
    buffer = io.BytesIO()
    base = canvas.Canvas(buffer, pagesize=(page_width_pt, page_height_pt), pageCompression=1)
    base.setFillColorRGB(1, 1, 1)
    base.rect(0, 0, page_width_pt, page_height_pt, stroke=0, fill=1)
    vector_assets = []
    draw_labels = layout.get("draw_labels", True)
    for panel, asset, placed, _ in prepared:
        if draw_labels:
            x, y, _, _ = panel["slot_mm"]
            base.setFont("Helvetica-Bold", 8)
            base.setFillColorRGB(0.13, 0.18, 0.22)
            base.drawString((x + 0.4) * PT_PER_MM,
                            page_height_pt - (y + min(layout["label_band_mm"] - 0.7, 3.0)) * PT_PER_MM,
                            panel["label"])
        x_pt, y_pt, w_pt, h_pt = _top_to_pdf(placed, layout["height_mm"])
        if asset["kind"] == "raster":
            base.drawImage(ImageReader(asset["image"]), x_pt, y_pt, w_pt, h_pt,
                           preserveAspectRatio=False, mask="auto")
        else:
            vector_assets.append((asset, x_pt, y_pt, w_pt, h_pt))
    base.showPage()
    base.save()
    buffer.seek(0)
    writer = PdfWriter()
    writer.add_page(PdfReader(buffer).pages[0])
    output_page = writer.pages[0]
    for asset, x_pt, y_pt, w_pt, h_pt in vector_assets:
        source = asset["pdf_page"]
        box = source.cropbox
        left, bottom = float(box.left), float(box.bottom)
        scale = w_pt / float(box.width)
        if abs(h_pt / float(box.height) - scale) > 1e-7:
            raise ComposeError("Vector aspect ratio changed unexpectedly")
        transform = Transformation().translate(-left, -bottom).scale(scale).translate(x_pt, y_pt)
        output_page.merge_transformed_page(source, transform, over=True, expand=False)
    with pdf_path.open("wb") as handle:
        writer.write(handle)
    with pdfium.PdfDocument(str(pdf_path)) as pdf:
        page = pdf[0]
        bitmap = page.render(scale=layout["dpi"] / 72)
        preview = bitmap.to_pil().convert("RGB").copy()
    preview.save(png_path, dpi=(layout["dpi"], layout["dpi"]))
    overlay = preview.copy()
    overlay_draw = ImageDraw.Draw(overlay)
    scale_px = layout["dpi"] / 25.4
    for info in infos:
        for key, color in (("slot_mm", "#BF4F43"), ("placed_mm", "#2B6AAB"),
                           ("visible_content_estimate_mm", "#20A6A0"),
                           ("plot_rect_mm", "#2E8B57")):
            rect = info.get(key)
            if rect is None:
                continue
            x, y, width, height = rect
            if width <= 0 or height <= 0:
                continue
            box = tuple(round(v * scale_px) for v in (x, y, x + width, y + height))
            overlay_draw.rectangle(box, outline=color, width=3)
            if key == "plot_rect_mm":
                # Coordinate rulers expose the final plotted edge in millimetres.
                for px, py, horizontal in ((box[0], box[1], False), (box[2], box[1], False),
                                           (box[0], box[1], True), (box[0], box[3], True)):
                    if horizontal:
                        overlay_draw.line((0, py, overlay.width, py), fill="#2E8B5788", width=1)
                    else:
                        overlay_draw.line((px, 0, px, overlay.height), fill="#2E8B5788", width=1)
    # Physical millimetre ticks, longer every 5 mm, on the diagnostic overlay.
    for mm in range(0, int(layout["width_mm"]) + 1):
        px = round(mm * scale_px)
        overlay_draw.line((px, 0, px, 16 if mm % 5 == 0 else 7), fill="#405469", width=1)
        if mm % 10 == 0:
            overlay_draw.text((px + 2, 17), str(mm), fill="#405469")
    for mm in range(0, int(layout["height_mm"]) + 1):
        py = round(mm * scale_px)
        overlay_draw.line((0, py, 16 if mm % 5 == 0 else 7, py), fill="#405469", width=1)
        if mm % 10 == 0:
            overlay_draw.text((18, py + 2), str(mm), fill="#405469")
    overlay_path = stem.with_suffix(".alignment.png")
    overlay.save(overlay_path)
    crop_dir = stem.parent / f"{stem.name}_panel_checks"
    crop_dir.mkdir(exist_ok=True)
    for stale in crop_dir.glob("panel_*.png"):
        stale.unlink()
    for panel, _, _, _ in prepared:
        x, y, width, height = panel["slot_mm"]
        scale_px = layout["dpi"] / 25.4
        box = tuple(round(v * scale_px) for v in (x, y, x + width, y + height))
        preview.crop(box).save(crop_dir / f"panel_{panel['label']}.png")
    font_audit = audit_fonts(pdf_path, infos)
    report = {"figure_id": layout["figure_id"], "claim": layout["claim"],
              "status": "review_required" if warnings else "geometry_pass_visual_review_required",
              "width_mm": layout["width_mm"], "height_mm": layout["height_mm"],
              "dpi": layout["dpi"], "warnings": warnings, "panels": infos,
              "output_purpose": layout.get("output_purpose", "manuscript"),
              "layout_mode": layout.get("layout_mode", "fixed"),
              "auto_row_heights_mm": layout.get("auto_row_heights_mm"),
              "interpanel_gaps": gap_measurements,
              "outer_whitespace_ratio": outer_whitespace_ratio,
              "alignment_audit": alignment_audit,
              "font_audit": font_audit,
              "outputs": {"pdf": str(pdf_path), "png": str(png_path),
                          "panel_checks": str(crop_dir),
                          "alignment_overlay": str(overlay_path)}}
    qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
