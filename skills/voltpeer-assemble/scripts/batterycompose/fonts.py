"""Measure extractable PDF text after the final physical-size assembly."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import median

import pdfplumber

PT_PER_MM = 72 / 25.4


def audit_fonts(pdf_path: str | Path, panels: list[dict], *, threshold_pt: float = 6.0) -> dict:
    """Report visible vector-text sizes; raster/outlined text remains unauditable."""
    with pdfplumber.open(str(pdf_path)) as document:
        page = document.pages[0]
        glyphs = [char for char in page.chars if char.get("text", "").strip()]
        outcomes = []
        for panel in panels:
            result = {"label": panel["label"], "source_kind": panel["kind"]}
            if panel["kind"] == "raster":
                result["status"] = "raster_text_unmeasurable"
                outcomes.append(result)
                continue
            x, y, width, height = panel["placed_mm"]
            left, top = x * PT_PER_MM, y * PT_PER_MM
            right, bottom = (x + width) * PT_PER_MM, (y + height) * PT_PER_MM
            selected = [char for char in glyphs if
                        left <= (char["x0"] + char["x1"]) / 2 <= right and
                        top <= (char["top"] + char["bottom"]) / 2 <= bottom]
            sizes = [float(char["size"]) for char in selected]
            if not sizes:
                result["status"] = "no_extractable_text"
            else:
                result.update({
                    "status": "review_small_text" if any(size < threshold_pt for size in sizes) else "measured",
                    "glyph_count": len(sizes),
                    "min_pt": round(min(sizes), 2),
                    "median_pt": round(median(sizes), 2),
                    "below_threshold_count": sum(size < threshold_pt for size in sizes),
                    "fonts": [name for name, _ in Counter(char["fontname"] for char in selected).most_common(4)],
                })
            outcomes.append(result)
        return {
            "method": "pdfplumber extractable glyphs in final composed PDF",
            "threshold_pt": threshold_pt,
            "panels": outcomes,
            "limitations": "Raster or outlined text cannot be measured. PDF transforms can make extracted sizes misleading; inspect rendered glyphs at final size.",
        }
