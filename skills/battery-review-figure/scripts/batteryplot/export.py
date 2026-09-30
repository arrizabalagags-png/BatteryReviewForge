"""Export vector masters, a review PNG, and a provenance sidecar."""

from __future__ import annotations

import json
from datetime import datetime, timezone
import importlib.metadata
import platform
from pathlib import Path
from typing import Mapping

import matplotlib as mpl
from matplotlib.figure import Figure

from .data import DataContractError
from .style import PLOT_STYLE
from output_safety import reserve_stem


def save_bundle(
    fig: Figure, stem: str | Path, *, claim: str, source_data: str,
    caption_notes: str, dpi: int = 300, formats: tuple[str, ...] = ("pdf", "svg", "png"),
    close: bool = False, dpi_by_format: Mapping[str, int] | None = None,
    tiff_compression: str = "tiff_lzw", specification: Mapping | None = None,
) -> list[Path]:
    """Save at the figure's physical size. DPI applies to raster output only.

    The caller supplies a one-sentence claim, traceable input path, and notes for
    the caption. The JSON is a provenance aid, not a scientific validation stamp.
    """
    if not claim.strip() or not source_data.strip() or not caption_notes.strip():
        raise DataContractError("claim, source_data and caption_notes are required")
    if type(dpi) is not int or dpi < 300:
        raise DataContractError("Raster review export needs at least 300 dpi")
    if not formats or set(formats) - {"pdf", "svg", "png", "tiff"}:
        raise DataContractError("Formats must be pdf, svg, png or tiff")
    if len(set(formats)) != len(formats):
        raise DataContractError("Export formats must be unique")
    dpi_by_format = dict(dpi_by_format or {})
    if set(dpi_by_format) - {"png", "tiff"}:
        raise DataContractError("Per-format DPI applies only to PNG/TIFF, not vector PDF/SVG")
    if any(type(value) is not int or value < 300 for value in dpi_by_format.values()):
        raise DataContractError("Each raster format needs an integer DPI >=300")
    if tiff_compression not in {"tiff_lzw", "tiff_adobe_deflate", "raw"}:
        raise DataContractError("Use tiff_lzw, tiff_adobe_deflate or raw TIFF compression")
    meta = getattr(fig, "batteryplot_meta", None)
    if not isinstance(meta, Mapping):
        raise DataContractError("Use a batteryplot chart before exporting")
    outputs: list[Path] = []
    release_path = Path(__file__).resolve().parents[2] / 'assets/SKILL_RELEASE.json'
    release = json.loads(release_path.read_text(encoding='utf-8-sig')) if release_path.is_file() else {'version': 'unreported'}
    suffixes = (".pdf", ".svg", ".png", ".tiff", ".provenance.json")
    with reserve_stem(stem, suffixes) as (reserved, version):
        with mpl.rc_context(PLOT_STYLE):
            fig.canvas.draw()
            for fmt in formats:
                target = Path(str(reserved) + f".{fmt}")
                effective = dpi_by_format.get(fmt, dpi)
                extra = {"pil_kwargs": {"compression": tiff_compression}} if fmt == "tiff" else {}
                fig.savefig(target, format=fmt, dpi=effective, facecolor="white", **extra)
                outputs.append(target)
        sidecar = Path(str(reserved) + ".provenance.json")
        sidecar.write_text(json.dumps({
        **dict(meta),
        "claim": claim,
        "source_data": source_data,
        "caption_notes": caption_notes,
        "raster_dpi": dpi,
        "dpi_by_format": {fmt: dpi_by_format.get(fmt, dpi) if fmt in {"png", "tiff"} else None for fmt in formats},
        "tiff_compression": tiff_compression if "tiff" in formats else None,
        "specification": dict(specification or {"status": "journal_neutral_preview", "journal_requirements": "needs_confirmation", "note": f"{dpi} dpi is the requested working preview resolution, not a verified publisher requirement."}),
        "output_version": version,
        "parent_version": version - 1 if version > 1 else None,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "environment": {"skill_version": release['version'], "python": platform.python_version(), "os": platform.system(), "matplotlib": mpl.__version__, "numpy": importlib.metadata.version("numpy"), "renderer": "batteryplot"},
        "physical_size_mm": [round(v * 25.4, 2) for v in fig.get_size_inches()],
        "outputs": [str(path.name) for path in outputs],
        "qa_status": "requires_human_review",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs.append(sidecar)
    if close:
        import matplotlib.pyplot as plt
        plt.close(fig)
    return outputs
