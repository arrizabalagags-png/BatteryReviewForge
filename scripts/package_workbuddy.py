"""Build one WorkBuddy-importable ZIP per BatteryReviewForge skill.

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
VERSION = "0.5.0"
AUTHOR = "郭硕、姜金龙｜上海理工大学能源材料科学研究院"

ZH = {
    "battery-claim-check": "逐条核对综述中的引用、数字与原文证据。",
    "battery-figure-assemble": "把已有图片和图表对齐、拼版，并检查成图清晰度。",
    "battery-literature-map": "检索和筛选电池文献，记录哪些论文真的读过。",
    "battery-metrics-audit": "检查不同电池数据的测试条件，判断能否公平比较。",
    "battery-review-audit": "投稿前检查整篇电池综述的论点、证据、图表与一致性。",
    "battery-review-figure": "用实验数据绘制电池图表，并规划综述示意图。",
    "battery-review-forge": "给电池综述全流程分工，按任务调用合适的小技能。",
    "battery-review-plan": "确定综述角度、范围、创新点和章节逻辑。",
    "battery-review-polish": "润色现有综述段落，保留原始科学含义和引文。",
    "battery-review-response": "逐条整理审稿意见、修改内容与回复。",
    "battery-review-submission": "核对目标期刊要求并准备投稿材料。",
    "battery-review-write": "根据已核查的证据起草或重组综述正文。",
    "battery-reviewer": "对定稿综述做独立的审稿式评估。",
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


def build(output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    archives: list[Path] = []
    folders = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if set(path.name for path in folders) != set(ZH):
        raise ValueError("Update the WorkBuddy descriptions when the skill list changes")
    for folder in folders:
        archive = output / f"{folder.name}-workbuddy-v{VERSION}.zip"
        with ZipFile(archive, "w", ZIP_DEFLATED) as target:
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
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "workbuddy")
    args = parser.parse_args()
    archives = build(args.output)
    collection = args.output.parent / f"BatteryReviewForge-WorkBuddy-v{VERSION}.zip"
    with ZipFile(collection, "w", ZIP_DEFLATED) as target:
        for archive in archives:
            target.write(archive, archive.name)
    print(f"Built {len(archives)} WorkBuddy-format skill archives and {collection}")


if __name__ == "__main__":
    main()
