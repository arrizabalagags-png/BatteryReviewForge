"""Read panel assets without changing the source files or their meaning."""

from __future__ import annotations

import hashlib
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageOps
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
import pypdfium2 as pdfium

from .layout import ComposeError


RASTER = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _raster_image(path: Path, crop: list[int] | None = None) -> Image.Image:
    with Image.open(path) as opened:
        if getattr(opened, "n_frames", 1) > 1:
            raise ComposeError(f"Multi-frame raster requires an explicit exported frame: {path}")
        image = ImageOps.exif_transpose(opened).copy()
    if crop is not None:
        left, top, right, bottom = crop
        if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
            raise ComposeError(f"Crop is outside the source image: {path}")
        image = image.crop((left, top, right, bottom))
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        rgba = image.convert("RGBA")
        white = Image.new("RGBA", rgba.size, "white")
        white.alpha_composite(rgba)
        image = white.convert("RGB")
    else:
        image = image.convert("RGB")
    return image


def _safe_svg(path: Path) -> bytes:
    data = path.read_bytes()
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper() or b"@import" in data.lower():
        raise ComposeError(f"SVG has external or entity declarations: {path}")
    for match in re.finditer(rb"url\(([^)]+)\)", data, re.I):
        target = match.group(1).strip().strip(b"\"'")
        if not target.startswith((b"#", b"data:")):
            raise ComposeError(f"SVG has an external style reference: {path}")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ComposeError(f"Invalid SVG: {path}") from exc
    for element in root.iter():
        for key, value in element.attrib.items():
            if key.endswith("href") and not value.startswith(("#", "data:")):
                raise ComposeError(f"SVG has an external reference: {path}")
        style = element.attrib.get("style", "")
        for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", style, re.I):
            if not match.group(1).startswith(("#", "data:")):
                raise ComposeError(f"SVG has an external style reference: {path}")
    return data


def _svg_pdf(path: Path) -> bytes:
    try:
        import cairosvg
    except ImportError as exc:
        raise ComposeError("SVG input requires CairoSVG") from exc
    return cairosvg.svg2pdf(bytestring=_safe_svg(path))


def load_asset(panel: dict) -> dict:
    path = Path(panel["resolved_path"])
    suffix = path.suffix.lower()
    base = {"path": str(path), "sha256": digest(path), "format": suffix.lstrip(".")}
    if suffix in RASTER:
        image = _raster_image(path, panel.get("crop_px"))
        return {**base, "kind": "raster", "image": image,
                "source_size_px": list(image.size), "page_count": None}
    if suffix == ".svg":
        payload = _svg_pdf(path)
        reader = PdfReader(io.BytesIO(payload))
        page = reader.pages[0]
        _apply_vector_crop(page, panel.get("crop_box_fraction"))
        return {**base, "kind": "vector", "pdf_bytes": payload,
                "pdf_page": page, "page_count": 1}
    if suffix == ".pdf":
        payload = path.read_bytes()
        reader = PdfReader(io.BytesIO(payload))
        count = len(reader.pages)
        page_number = panel.get("page_number")
        if count > 1 and page_number is None:
            raise ComposeError(f"Multi-page PDF needs page_number: {path}")
        page_number = 1 if page_number is None else page_number
        if type(page_number) is not int or not 1 <= page_number <= count:
            raise ComposeError(f"Invalid page_number for {path}")
        page = reader.pages[page_number - 1]
        _apply_vector_crop(page, panel.get("crop_box_fraction"))
        return {**base, "kind": "vector", "pdf_bytes": payload,
                "pdf_page": page, "page_count": count,
                "page_number": page_number}
    raise ComposeError(f"Unsupported input format: {path}")


def _apply_vector_crop(page, fraction: list[float] | None) -> None:
    if fraction is None:
        return
    left, top, right, bottom = map(float, fraction)
    box = page.cropbox
    x0, y0 = float(box.left), float(box.bottom)
    width, height = float(box.width), float(box.height)
    page.cropbox = RectangleObject((x0 + left * width, y0 + (1 - bottom) * height,
                                    x0 + right * width, y0 + (1 - top) * height))


def preview_loaded(asset: dict, max_side: int = 700) -> Image.Image:
    if asset["kind"] == "raster":
        image = asset["image"].copy()
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        return image
    writer = PdfWriter()
    writer.add_page(asset["pdf_page"])
    buffer = io.BytesIO()
    writer.write(buffer)
    with pdfium.PdfDocument(buffer.getvalue()) as pdf:
        page = pdf[0]
        bitmap = page.render(scale=max_side / max(page.get_size()))
        return bitmap.to_pil().convert("RGB").copy()


def preview_image(path: Path, max_side: int = 750) -> Image.Image:
    suffix = path.suffix.lower()
    if suffix in RASTER:
        image = _raster_image(path)
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        return image
    if suffix == ".svg":
        try:
            import cairosvg
        except ImportError as exc:
            raise ComposeError("SVG preview requires CairoSVG") from exc
        png = cairosvg.svg2png(bytestring=_safe_svg(path), output_width=max_side)
        with Image.open(io.BytesIO(png)) as opened:
            return opened.convert("RGB").copy()
    with pdfium.PdfDocument(str(path)) as pdf:
        if len(pdf) != 1:
            raise ComposeError(f"Inventory preview needs a single-page PDF: {path}")
        page = pdf[0]
        w, h = page.get_size()
        bitmap = page.render(scale=max_side / max(w, h))
        return bitmap.to_pil().convert("RGB").copy()


def white_inset_fraction(image: Image.Image) -> list[float]:
    """Suggest a white-margin review; never use this to crop automatically."""
    image = image.convert("RGB")
    image.thumbnail((600, 600), Image.Resampling.LANCZOS)
    pixels = image.load()
    x_min, y_min, x_max, y_max = image.width, image.height, -1, -1
    for y in range(image.height):
        for x in range(image.width):
            if min(pixels[x, y]) < 242:
                x_min, y_min = min(x_min, x), min(y_min, y)
                x_max, y_max = max(x_max, x), max(y_max, y)
    if x_max < 0:
        return [1.0, 1.0, 1.0, 1.0]
    return [round(x_min / image.width, 3), round(y_min / image.height, 3),
            round((image.width - 1 - x_max) / image.width, 3),
            round((image.height - 1 - y_max) / image.height, 3)]
