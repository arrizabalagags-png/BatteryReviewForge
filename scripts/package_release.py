"""Build the portable full package and independently installable Skills.

This archive contains the installers, public documentation, plugin manifest and
skills and original synthetic evaluation fixtures. Private papers, local outputs
and website demos are not included. Unpack and run install.ps1 or install.sh.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from eval_provenance import source_provenance, tree_manifest


ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
OUTPUT = ROOT / "docs" / "downloads" / f"v{VERSION}" / f"VoltPeer-v{VERSION}.zip"
TOP_LEVEL = ["README.md", "README.en.md", "AUTHORS.md", "LICENSE", "CITATION.cff", "install.ps1", "install.sh", "skill-migration.tsv", "plugin.json", ".agents/plugins/marketplace.json", "assets/brand.svg", "assets/mechanism-showcase/desolvation.svg", "assets/mechanism-showcase/scientific-sources.json", "assets/mechanism-showcase/LICENSE.txt"]
PUBLIC_DOCS = ["docs/COMPATIBILITY.md", "docs/SKILL_NAMES.json", "docs/SKILL_MIGRATION.json", "docs/NAMING_MIGRATION.md", "docs/GETTING_STARTED.md", "docs/EVAL.md",
               f"docs/RELEASE_v{VERSION}.md",
               "docs/validation/2026-10-02-naming-installer-v0.11.0.json",
               "docs/validation/2026-10-02-naming-preservation-v0.11.0.json",
               "docs/validation/SCIENTIFIC_CORE_2026-10-01.md",
               "docs/validation/SCIENTIFIC_DOMAINS_2026-10-01.md",
               "docs/validation/DEMO_SOURCE_DELIVERY_2026-10-01.md",
               "docs/validation/SCIENCE_STARTER_2026-10-01.md",
               "docs/validation/2026-10-01-scientific-core.json",
               "docs/validation/2026-10-01-scientific-domains.json",
               "docs/validation/2026-10-01-scientific-inventory.json",
               "docs/validation/2026-10-01-demo-source-delivery.json",
               "docs/validation/2026-10-01-science-starter.json",
               "docs/SKILLS_QA_2026-09-30.md", "docs/RELEASE_STATUS.json",
               "docs/validation/FIGURE_FEEDBACK_2026-09-30.md",
               "docs/validation/2026-09-30-frame-final-regression.json",
               "docs/validation/2026-09-30-frame-regression-initial.json",
               "docs/validation/2026-09-30-schema-followup.json",
               "docs/validation/2026-09-30-recipe-eval-followup.json",
               "docs/validation/2026-09-30-recipe-font-followup.json",
               "docs/validation/2026-09-30-upload-metadata-followup.json",
               "docs/validation/2026-10-01-api-pilot.json", "docs/validation/2026-10-01-plot-starter.json",
               "docs/validation/2026-10-01-luna-starter-agent.json",
               "docs/validation/2026-10-01-luna-starter-agent-route-fix.json",
               "docs/validation/2026-10-01-flash-starter-route-fix.json",
               "docs/DEMO_METADATA_SCHEMA.json", "scripts/check_demo_metadata.py",
               "scripts/check_skill_dependencies.py", "scripts/diagnose_install.py", "scripts/check_skill_distribution.py",
               "scripts/workflow_eval.py", "scripts/eval_provenance.py", "scripts/runtime_contract/cli_runtime.py", f"docs/SOURCE_PROVENANCE_v{VERSION}.json"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', action='append', default=[], help='Rebuild only these single-Skill ZIPs along with the full package; preserve other candidate ZIP bytes.')
    parser.add_argument('--output-root', type=Path, default=OUTPUT.parent, help='New distribution directory; existing ZIPs are never overwritten.')
    args = parser.parse_args()
    selected = set(args.skill)
    available = {p.name for p in (ROOT/'skills').iterdir() if (p/'SKILL.md').is_file()}
    if not selected <= available:
        parser.error('Unknown canonical Skill: '+', '.join(sorted(selected-available)))
    output_root = args.output_root.resolve()
    output = output_root / OUTPUT.name
    pending_archives = [output] + [output_root/'single'/f'{identity}-v{VERSION}.zip' for identity in sorted(selected or available)]
    if any(path.exists() for path in pending_archives):
        parser.error('An archive already exists. Choose a new --output-root to preserve versioned bytes.')
    output_root.mkdir(parents=True, exist_ok=True)
    source_record = {**source_provenance(ROOT), 'skill_tree': tree_manifest(ROOT / 'skills'),
                     'scope': 'Source commit plus worktree state at packaging; complete Skill file hashes identify the effective tree.'}
    (ROOT / f'docs/SOURCE_PROVENANCE_v{VERSION}.json').write_text(json.dumps(source_record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = [ROOT / name for name in TOP_LEVEL + PUBLIC_DOCS]
    files += sorted((ROOT / ".codex-plugin").rglob("*"))
    files += sorted((ROOT / "skills").rglob("*"))
    files += sorted((ROOT / "evals").rglob("*"))
    with ZipFile(output, "x", ZIP_DEFLATED) as archive:
        for path in files:
            if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            archive.write(path, path.relative_to(ROOT).as_posix())
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert {"install.ps1", "install.sh", "skills/voltpeer-plot/SKILL.md"} <= names
        expected = {f"skills/{folder.name}/SKILL.md" for folder in (ROOT / "skills").iterdir() if (folder / "SKILL.md").is_file()}
        packaged = {name for name in names if name.startswith("skills/") and name.endswith("/SKILL.md")}
        assert packaged == expected, "Every source skill must be included exactly once"
    single_root = output_root / "single"
    single_root.mkdir(exist_ok=True)
    for folder in sorted((ROOT / "skills").iterdir()):
        if not (folder / "SKILL.md").is_file():
            continue
        if selected and folder.name not in selected:
            continue
        with ZipFile(single_root / f"{folder.name}-v{VERSION}.zip", "x", ZIP_DEFLATED) as archive:
            for path in sorted(folder.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}:
                    archive.write(path, path.relative_to(folder.parent).as_posix())
    print(f"Built {output} ({output.stat().st_size:,} bytes) and {len(selected or available)} portable single-Skill ZIPs")


if __name__ == "__main__":
    main()
