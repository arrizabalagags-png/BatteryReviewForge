"""Build the portable full package and independently installable Skills.

This archive contains the installers, public documentation, plugin manifest and
skills and original synthetic evaluation fixtures. Private papers, local outputs
and website demos are not included. Unpack and run install.ps1 or install.sh.
"""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from eval_provenance import source_provenance, tree_manifest


ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
OUTPUT = ROOT / "docs" / "downloads" / f"BatteryReviewForge-v{VERSION}.zip"
TOP_LEVEL = ["README.md", "AUTHORS.md", "LICENSE", "CITATION.cff", "install.ps1", "install.sh"]
PUBLIC_DOCS = ["docs/COMPATIBILITY.md", "docs/SKILL_NAMES.json", "docs/EVAL.md",
               "docs/SKILLS_QA_2026-09-30.md", "docs/RELEASE_STATUS.json",
               "docs/validation/FIGURE_FEEDBACK_2026-09-30.md",
               "docs/validation/2026-09-30-frame-final-regression.json",
               "docs/validation/2026-09-30-frame-regression-initial.json",
               "docs/validation/2026-09-30-schema-followup.json",
               "docs/validation/2026-09-30-recipe-eval-followup.json",
               "docs/validation/2026-09-30-recipe-font-followup.json",
               "docs/validation/2026-09-30-upload-metadata-followup.json",
               "docs/DEMO_METADATA_SCHEMA.json", "scripts/check_demo_metadata.py",
               "scripts/check_skill_dependencies.py", "scripts/diagnose_install.py", "scripts/check_skill_distribution.py",
               "scripts/workflow_eval.py", "scripts/eval_provenance.py", "scripts/runtime_contract/cli_runtime.py", "docs/SOURCE_PROVENANCE.json"]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source_record = {**source_provenance(ROOT), 'skill_tree': tree_manifest(ROOT / 'skills'),
                     'scope': 'Source commit plus worktree state at packaging; complete Skill file hashes identify the effective tree.'}
    (ROOT / 'docs/SOURCE_PROVENANCE.json').write_text(json.dumps(source_record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = [ROOT / name for name in TOP_LEVEL + PUBLIC_DOCS]
    files += sorted((ROOT / ".codex-plugin").rglob("*"))
    files += sorted((ROOT / "skills").rglob("*"))
    files += sorted((ROOT / "evals").rglob("*"))
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for path in files:
            if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            archive.write(path, path.relative_to(ROOT).as_posix())
    with ZipFile(OUTPUT) as archive:
        names = set(archive.namelist())
        assert {"install.ps1", "install.sh", "skills/battery-review-figure/SKILL.md"} <= names
        expected = {f"skills/{folder.name}/SKILL.md" for folder in (ROOT / "skills").iterdir() if (folder / "SKILL.md").is_file()}
        packaged = {name for name in names if name.startswith("skills/") and name.endswith("/SKILL.md")}
        assert packaged == expected, "Every source skill must be included exactly once"
    single_root = OUTPUT.parent / "single"
    single_root.mkdir(exist_ok=True)
    for folder in sorted((ROOT / "skills").iterdir()):
        if not (folder / "SKILL.md").is_file():
            continue
        with ZipFile(single_root / f"{folder.name}-v{VERSION}.zip", "w", ZIP_DEFLATED) as archive:
            for path in sorted(folder.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}:
                    archive.write(path, path.relative_to(folder.parent).as_posix())
    print(f"Built {OUTPUT.name} ({OUTPUT.stat().st_size:,} bytes) and {len(expected)} portable single-Skill ZIPs")


if __name__ == "__main__":
    main()
