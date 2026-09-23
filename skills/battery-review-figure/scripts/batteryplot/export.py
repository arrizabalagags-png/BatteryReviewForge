"""Export vector masters, a review PNG, and a provenance sidecar."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import matplotlib as mpl
from matplotlib.figure import Figure

from .data import DataContractError
from .style import PLOT_STYLE


def save_bundle(
    fig: Figure, stem: str | Path, *, claim: str, source_data: str,
    caption_notes: str, dpi: int = 300, formats: tuple[str, ...] = ("pdf", "svg", "png"),
    close: bool = False,
) -> list[Path]:
    """Save at the figure's physical size. DPI applies to raster output only.

    The caller supplies a one-sentence claim, traceable input path, and notes for
    the caption. The JSON is a provenance aid, not a scientific validation stamp.
    """
    if not claim.strip() or not source_data.strip() or not caption_notes.strip():
        raise DataContractError("claim, source_data and caption_notes are required")
    if dpi < 300:
        raise DataContractError("Raster review export needs at least 300 dpi")
    if not formats or set(formats) - {"pdf", "svg", "png", "tiff"}:
        raise DataContractError("Formats must be pdf, svg, png or tiff")
    meta = getattr(fig, "batteryplot_meta", None)
    if not isinstance(meta, Mapping):
        raise DataContractError("Use a batteryplot chart before exporting")
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    with mpl.rc_context(PLOT_STYLE):
        fig.canvas.draw()
        for fmt in formats:
            target = stem.with_suffix(f".{fmt}")
            fig.savefig(target, format=fmt, dpi=dpi, facecolor="white")
            outputs.append(target)
    sidecar = stem.with_suffix(".provenance.json")
    sidecar.write_text(json.dumps({
        **dict(meta),
        "claim": claim,
        "source_data": source_data,
        "caption_notes": caption_notes,
        "raster_dpi": dpi,
        "physical_size_mm": [round(v * 25.4, 2) for v in fig.get_size_inches()],
        "outputs": [str(path.name) for path in outputs],
        "qa_status": "requires_human_review",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs.append(sidecar)
    if close:
        import matplotlib.pyplot as plt
        plt.close(fig)
    return outputs
