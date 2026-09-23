"""Make an asset inventory and contact sheets before choosing a panel layout."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

from .assets import RASTER, digest, preview_image, white_inset_fraction
from .layout import ComposeError


SUPPORTED = RASTER | {".pdf", ".svg"}


def inventory(folder: str | Path, output: str | Path) -> dict:
    folder = Path(folder).resolve()
    output = Path(output).resolve()
    if not folder.is_dir():
        raise ComposeError(f"Input is not a directory: {folder}")
    if output == folder or folder in output.parents:
        raise ComposeError("Put inventory output outside the input directory")
    files = sorted(path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED)
    if not files:
        raise ComposeError("No supported PNG/JPEG/TIFF/PDF/SVG assets found")
    if len(files) > 200:
        raise ComposeError("More than 200 assets; split the batch into figure-level folders")
    output.mkdir(parents=True, exist_ok=True)
    records = []
    previews = []
    for path in files:
        record = {"path": str(path.relative_to(folder)), "sha256": digest(path),
                  "format": path.suffix.lower().lstrip(".")}
        try:
            if path.suffix.lower() == ".pdf":
                reader = PdfReader(path)
                record["pages"] = len(reader.pages)
                record["dimensions_pt"] = [round(float(reader.pages[0].cropbox.width), 2),
                                           round(float(reader.pages[0].cropbox.height), 2)]
            with_preview = preview_image(path, max_side=650)
            record["preview_px"] = list(with_preview.size)
            record["white_inset_fraction_candidate"] = white_inset_fraction(with_preview.copy())
            previews.append(with_preview)
        except Exception as exc:
            record["inspection_error"] = str(exc)
            previews.append(None)
        records.append(record)
    contact_paths = []
    tile_w, tile_h, columns, batch_size = 320, 250, 3, 24
    font = ImageFont.load_default()
    for start in range(0, len(records), batch_size):
        subset = records[start:start + batch_size]
        rows = (len(subset) + columns - 1) // columns
        sheet = Image.new("RGB", (tile_w * columns, tile_h * rows), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, record in enumerate(subset):
            index = start + offset
            x, y = (offset % columns) * tile_w, (offset // columns) * tile_h
            draw.rectangle((x + 2, y + 2, x + tile_w - 3, y + tile_h - 3), outline="#A8B0B5", width=1)
            preview = previews[index]
            if preview is not None:
                thumb = preview.copy()
                thumb.thumbnail((tile_w - 20, tile_h - 52), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (x + (tile_w - thumb.width) // 2, y + 8 + (tile_h - 52 - thumb.height) // 2))
            title = f"{index + 1:03d}  {record['path']}"
            draw.text((x + 9, y + tile_h - 40), title[:44], fill="#202A30", font=font)
            if "inspection_error" in record:
                draw.text((x + 9, y + tile_h - 22), "INSPECTION ERROR", fill="#A3342A", font=font)
        path = output / f"contact-{start // batch_size + 1:02d}.png"
        sheet.save(path)
        contact_paths.append(str(path))
    report = {"input_dir": str(folder), "count": len(records), "assets": records,
              "contact_sheets": contact_paths,
              "note": "White-inset estimates are review hints, never automatic crops."}
    (output / "inventory.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
