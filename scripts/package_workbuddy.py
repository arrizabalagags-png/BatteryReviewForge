"""Build one WorkBuddy-importable ZIP per VoltPeer skill.

The source SKILL.md files remain portable. WorkBuddy's documented extra
frontmatter is added only inside the generated distribution archives.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
VERSION = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
AUTHOR = "郭硕、姜金龙｜上海理工大学能源材料科学研究院"

ZH = {
    "voltpeer-mechanism": "根据体系与证据绘制原创机理图，输出SVG、参数与源码。",
    "voltpeer-data": "核对原始数据的列名、单位和分组，保留原文件与整理记录。",
    "voltpeer-experiment-plan": "把电池研究问题拆成变量、对照和待确认的测试条件。",
    "voltpeer-claim-check": "逐条核对综述中的引用、数字与原文证据。",
    "voltpeer-assemble": "把已有图片和图表对齐、拼版，并检查成图清晰度。",
    "voltpeer-literature": "检索和筛选电池文献，记录哪些论文真的读过。",
    "voltpeer-metrics": "检查不同电池数据的测试条件，判断能否公平比较。",
    "voltpeer-review-audit": "投稿前检查整篇电池综述的论点、证据、图表与一致性。",
    "voltpeer-plot": "用实验数据绘制电池图表，并规划综述示意图。",
    "voltpeer-workflow": "给电池综述全流程分工，按任务调用合适的小技能。",
    "voltpeer-plan": "规划研究论文或综述的论证与提纲，核对输入证据和章节逻辑。",
    "voltpeer-polish": "润色研究论文或综述，保留原始科学含义、数据和引文。",
    "voltpeer-response": "逐条整理审稿意见、修改内容与回复。",
    "voltpeer-submission": "核对目标期刊要求并准备投稿材料。",
    "voltpeer-write": "根据作者证据或已核查文献起草研究论文与综述，交付可核对的章节。",
    "voltpeer-reviewer": "对定稿综述做独立的审稿式评估。",
}


def adapted_skill(original: str, chinese_description: str) -> str:
    if not original.startswith("---\n"):
        raise ValueError("SKILL.md lacks opening YAML frontmatter")
    close = original.find("\n---\n", 4)
    if close < 0:
        raise ValueError("SKILL.md lacks closing YAML frontmatter")
    front = original[4:close]
    description = next(
        (line.removeprefix("description: ") for line in front.splitlines() if line.startswith("description: ")),
        None,
    )
    if not description:
        raise ValueError("SKILL.md lacks description")
    added = "\n".join(
        [
            "description_zh: " + json.dumps(chinese_description, ensure_ascii=False),
            "description_en: " + json.dumps(description, ensure_ascii=False),
            f"version: {VERSION}",
            "author: " + json.dumps(AUTHOR, ensure_ascii=False),
        ]
    )
    return f"---\n{front}\n{added}\n---\n{original[close + 5:]}"


def build(output: Path, selected: set[str] | None = None) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    archives: list[Path] = []
    folders = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if set(path.name for path in folders) != set(ZH):
        raise ValueError("Update the WorkBuddy descriptions when the skill list changes")
    planned = [output / f"{folder.name}-workbuddy-v{VERSION}.zip" for folder in folders if not selected or folder.name in selected]
    if any(path.exists() for path in planned):
        raise FileExistsError("Choose a new output directory; existing WorkBuddy archive bytes are immutable")
    for folder in folders:
        if selected and folder.name not in selected:
            continue
        archive = output / f"{folder.name}-workbuddy-v{VERSION}.zip"
        with ZipFile(archive, "x", ZIP_DEFLATED) as target:
            for path in sorted(folder.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                    continue
                relative = Path(folder.name) / path.relative_to(folder)
                if path.name == "SKILL.md" and path.parent == folder:
                    target.writestr(relative.as_posix(), adapted_skill(path.read_text(encoding="utf-8"), ZH[folder.name]))
                else:
                    target.write(path, relative.as_posix())
        archives.append(archive)
    return archives


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / "downloads" / f"v{VERSION}" / "workbuddy")
    parser.add_argument("--collection", type=Path, default=ROOT / "docs" / "downloads" / f"v{VERSION}" / f"VoltPeer-WorkBuddy-v{VERSION}.zip")
    parser.add_argument('--skill', action='append', default=[], help='Rebuild only these individual Skill ZIPs and the full collection; preserve unrelated ZIPs and an unaffected Starter collection.')
    args = parser.parse_args()
    selected = set(args.skill)
    if not selected <= set(ZH):
        parser.error('Unknown canonical Skill: '+', '.join(sorted(selected-set(ZH))))
    starter = args.collection.parent / f"VoltPeer-WorkBuddy-Starter-v{VERSION}.zip"
    if args.collection.exists() or ((not selected or selected & {'voltpeer-plot', 'voltpeer-assemble'}) and starter.exists()):
        parser.error('Choose new output/collection paths; existing collection ZIP bytes are immutable.')
    archives = build(args.output, selected)
    collection_archives = [args.output/f'{identity}-workbuddy-v{VERSION}.zip' for identity in sorted(ZH)]
    if any(not path.is_file() for path in collection_archives):
        parser.error('A selective update requires the existing complete collection of individual ZIPs. Run a complete build first.')
    collection = args.collection
    collection.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(collection, "x", ZIP_DEFLATED) as target:
        for archive in collection_archives:
            target.write(archive, archive.name)
    starter = collection.parent / f"VoltPeer-WorkBuddy-Starter-v{VERSION}.zip"
    if not selected or selected & {'voltpeer-plot', 'voltpeer-assemble'}:
        with ZipFile(starter, "x", ZIP_DEFLATED) as target:
            for archive in collection_archives:
                if archive.name.startswith(("voltpeer-plot-", "voltpeer-assemble-")):
                    target.write(archive, archive.name)
            target.writestr("先读我.txt", "这是绘图与拼图的两个独立技能包。先解压本套装，再分别导入需要的 ZIP。\n每个包自带所需规则，不依赖另一个技能目录。\n本版 WorkBuddy 客户端导入到成图仍待实机验收。\n请确认宿主发现技能，再检查依赖并运行小示例。\n教程：https://dazi.gsarrizabalaga.xyz/install-workbuddy.html\n")
    print(f"Built {len(archives)} WorkBuddy-format skill archives and {collection}")


if __name__ == "__main__":
    main()
