"""Report actual embedded PDF fonts; fail on an unexpected silent fallback.

Usage: python audit_pdf_fonts.py figure.pdf --expect Arial
The command checks PDF font resources, not just Matplotlib rcParams. Symbols or
non-Latin glyphs may legitimately need additional fonts; review those explicitly.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz


def audit(path: Path, expected: str | None = None) -> dict:
    with fitz.open(path) as pdf:
        fonts: dict[tuple[int, str], dict] = {}
        for page_index in range(len(pdf)):
            for xref, extension, font_type, base_name, *_ in pdf.get_page_fonts(page_index, full=True):
                key = (xref, base_name)
                if key in fonts:
                    fonts[key]["pages"].append(page_index + 1)
                    continue
                try:
                    embedded = bool(pdf.extract_font(xref)[3])
                except (ValueError, RuntimeError):
                    embedded = False
                fonts[key] = {
                    "base_name": base_name,
                    "family": re.sub(r"^[A-Z]{6}\+", "", base_name),
                    "format": extension,
                    "pdf_type": font_type,
                    "embedded": embedded,
                    "pages": [page_index + 1],
                }
    families = [font["family"].casefold() for font in fonts.values()]
    unexpected = bool(expected) and any(expected.casefold() not in family for family in families)
    missing_embedding = any(not font["embedded"] for font in fonts.values())
    return {
        "pdf": str(path),
        "expected_family": expected,
        "fonts": list(fonts.values()),
        "status": ("no_editable_font_found" if not fonts else
                   "review_fallback" if unexpected else
                   "font_not_embedded" if missing_embedding else "pass"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--expect", help="Required family name, for example Arial")
    args = parser.parse_args()
    if not args.pdf.is_file():
        parser.error(f"PDF not found: {args.pdf}")
    result = audit(args.pdf, args.expect)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
