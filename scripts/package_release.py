"""Build the small, direct-download novice package served by GitHub Pages.

This archive contains the installers, public documentation, plugin manifest and
skills. Private papers, local outputs, test fixtures and website demos are not
included. The user can unpack it and run install.ps1 or install.sh.
"""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
OUTPUT = ROOT / "docs" / "downloads" / f"BatteryReviewForge-v{VERSION}.zip"
TOP_LEVEL = ["README.md", "AUTHORS.md", "LICENSE", "CITATION.cff", "install.ps1", "install.sh"]
PUBLIC_DOCS = ["docs/COMPATIBILITY.md"]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    files = [ROOT / name for name in TOP_LEVEL + PUBLIC_DOCS]
    files += sorted((ROOT / ".codex-plugin").rglob("*"))
    files += sorted((ROOT / "skills").rglob("*"))
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for path in files:
            if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            archive.write(path, path.relative_to(ROOT).as_posix())
    with ZipFile(OUTPUT) as archive:
        names = set(archive.namelist())
        assert {"install.ps1", "install.sh", "skills/battery-review-figure/SKILL.md"} <= names
        assert len([name for name in names if name.startswith("skills/") and name.endswith("/SKILL.md")]) == 13
    print(f"Built {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
