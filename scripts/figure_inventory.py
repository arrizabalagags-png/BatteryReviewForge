"""Index figure-caption candidates in author-provided PDFs for manual review.

This script does not copy PDF artwork or publish caption text. Its output is a
finding aid, not a claim that each panel was visually or scientifically checked.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz


CAPTION = re.compile(r"(?m)^(?:Figure|Fig\.)[ \t]*([1-9]\d?)[ \t]*(?:[.:|]|\r?\n)")
DOI = re.compile(r"10\.\d{4,9}/[^\s<>\[\]{}]+", re.I)


def _doi(text: str) -> str | None:
    for match in DOI.finditer(text):
        value = match.group(0).rstrip(".,;:)")
        if value.lower().endswith(".pdf"):
            value = value[:-4]
        if len(value) < 90 and "onlinelibrary.wiley.com/doi" not in value:
            return value
    return None


def inventory_pdf(path: Path) -> dict:
    with fitz.open(path) as pdf:
        first_pages = "\n".join(page.get_text() for page in list(pdf)[:2])
        candidates = []
        seen = set()
        for page_number, page in enumerate(pdf, 1):
            for match in CAPTION.finditer(page.get_text()):
                figure = int(match.group(1))
                if figure not in seen:
                    seen.add(figure)
                    candidates.append({
                        "figure": figure,
                        "pdf_page": page_number,
                        "status": "caption_candidate_unverified",
                    })
        return {
            "source_file": path.name,
            "doi_candidate": _doi(first_pages),
            "page_count": len(pdf),
            "figure_candidates": candidates,
            "visual_review": "not_claimed",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Directory of author-provided PDFs")
    parser.add_argument("--out", type=Path, default=Path("outputs/figure-inventory.json"))
    args = parser.parse_args()
    if not args.source.is_dir():
        parser.error(f"Source directory does not exist: {args.source}")
    paths = sorted(args.source.glob("*.pdf"), key=lambda p: p.name.casefold())
    if not paths:
        parser.error("No PDFs found")
    records = [inventory_pdf(path) for path in paths]
    payload = {
        "status": "automated_caption_inventory_not_panel_validation",
        "source_count": len(records),
        "caption_candidate_count": sum(len(r["figure_candidates"]) for r in records),
        "sources": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{payload['source_count']} PDFs; {payload['caption_candidate_count']} caption candidates; {args.out}")


if __name__ == "__main__":
    main()
