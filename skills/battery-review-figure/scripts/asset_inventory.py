"""Catalog local reference artwork without redistributing or modifying it."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


SUPPORTED = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".svg", ".pdf",
             ".pptx", ".ppt", ".ai", ".eps", ".psd", ".vsdx", ".zip"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> dict:
    root = root.resolve()
    assets = []
    pending = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() in {".downloading", ".part", ".crdownload"}:
            pending.append(relative)
            continue
        if path.suffix.lower() not in SUPPORTED:
            continue
        item = {"relative_path": relative, "format": path.suffix.lower().lstrip("."),
                "bytes": path.stat().st_size, "sha256": _sha256(path),
                "rights_status": "unknown", "review_state": "not_reviewed"}
        if path.suffix.lower() == ".pptx":
            try:
                from pptx import Presentation
                item["slide_count"] = len(Presentation(path).slides)
            except Exception as exc:
                item["inspection_error"] = type(exc).__name__
        assets.append(item)
    hashes = Counter(item["sha256"] for item in assets)
    for item in assets:
        if hashes[item["sha256"]] > 1:
            item["duplicate_group"] = item["sha256"][:12]
    return {"root": str(root), "count": len(assets),
            "unique_content_count": len(hashes), "redundant_copy_count": len(assets) - len(hashes),
            "pending_count": len(pending),
            "pending": pending, "formats": dict(Counter(item["format"] for item in assets)),
            "assets": assets,
            "note": "Private inventory only. Rights are unknown until the owner verifies license or permission; no files are copied."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.input.is_dir():
        parser.error(f"Folder does not exist: {args.input}")
    report = inventory(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": report["count"], "unique_content": report["unique_content_count"],
                      "redundant_copies": report["redundant_copy_count"],
                      "pending": report["pending_count"],
                      "formats": report["formats"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
