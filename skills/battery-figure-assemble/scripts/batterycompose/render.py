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


def _alignment_issues(panels: list[dict], tolerance_mm: float = 1.5 / PT_PER_MM) -> list[str]:
    issues = []
    groups: dict[str, list[dict]] = {}
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
        for i, first in enumerate(members):
            for second in members[i + 1:]:
                a, b = first["plot_rect_mm"], second["plot_rect_mm"]
                a_slot, b_slot = first["slot_mm"], second["slot_mm"]
                same_row = abs(a_slot[1] - b_slot[1]) < 1e-6 and abs(a_slot[3] - b_slot[3]) < 1e-6
                same_col = abs(a_slot[0] - b_slot[0]) < 1e-6 and abs(a_slot[2] - b_slot[2]) < 1e-6
                if same_row:
                    delta = max(abs(a[1] - b[1]), abs(a[1] + a[3] - b[1] - b[3]))
                    if delta > tolerance_mm:
                        issues.append(f"Group {name}: panels {first['label']}/{second['label']} plot-area rows differ by {delta:.2f} mm")
                if same_col:
                    delta = max(abs(a[0] - b[0]), abs(a[0] + a[2] - b[0] - b[2]))
                    if delta > tolerance_mm:
                        issues.append(f"Group {name}: panels {first['label']}/{second['label']} plot-area columns differ by {delta:.2f} mm")
    return issues


def compose(manifest: dict, stem: str | Path, *, strict: bool = False) -> dict:
    """Produce PDF, PNG, and JSON. In strict mode, review warnings block output."""
    layout = resolve_layout(manifest)
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
        fill = (placed[2] * placed[3]) / (panel["art_mm"][2] * panel["art_mm"][3])
        if fill < 0.65:
            warnings.append(f"Panel {panel['label']}: artwork fills only {fill:.0%} of its slot; inspect whitespace or redesign the grid")
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
                "white_inset_fraction_candidate": insets,
                "plot_rect_mm": _plot_rect(panel, placed),
                "effective_dpi": round(effective_dpi, 1) if effective_dpi is not None else None,
                "fill_fraction": round(fill, 3), "crop_px": panel.get("crop_px"),
                "crop_box_fraction": panel.get("crop_box_fraction"),
                "crop_reason": panel.get("crop_reason"),
                "alignment_group": panel.get("alignment_group")}
        prepared.append((panel, asset, placed, info))
    infos = [item[3] for item in prepared]
    warnings.extend(_alignment_issues(infos))
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
                           ("plot_rect_mm", "#2E8B57")):
            rect = info.get(key)
            if rect is None:
                continue
            x, y, width, height = rect
            box = tuple(round(v * scale_px) for v in (x, y, x + width, y + height))
            overlay_draw.rectangle(box, outline=color, width=3)
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
              "font_audit": font_audit,
              "outputs": {"pdf": str(pdf_path), "png": str(png_path),
                          "panel_checks": str(crop_dir),
                          "alignment_overlay": str(overlay_path)}}
    qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
