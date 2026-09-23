# BatteryReviewForge

![BatteryReviewForge wordmark](assets/brand.svg)

**An evidence-first skill suite for battery review articles, from the first question to the final response letter.**

English · [简体中文](#简体中文)

BatteryReviewForge is a modular set of Codex skills for battery researchers writing Reviews and Perspectives. Each skill has one job, so a request to polish a paragraph does not launch a submission workflow, and a figure audit does not silently rewrite the article. A small coordinator handles full projects. The repository contains a Codex plugin manifest at `.codex-plugin/plugin.json`, a portable `plugin.json`, and an original Python plotting library inside the figure skill. No MCP server or paid database is required.

**Collaboration:** 郭硕 and 姜金龙 · 上海理工大学能源材料科学研究院
**License:** [MIT](LICENSE)

## Choose a skill

| Category | Skill | Use it for |
| --- | --- | --- |
| Full project | [`battery-review-forge`](skills/battery-review-forge/SKILL.md) | Coordinate a Review across stages and sessions |
| Plan | [`battery-review-plan`](skills/battery-review-plan/SKILL.md) | Scope, novelty, close Reviews, argument map |
| Evidence | [`battery-literature-map`](skills/battery-literature-map/SKILL.md) | Search, screen, deduplicate, count source states |
| Evidence | [`battery-claim-check`](skills/battery-claim-check/SKILL.md) | Verify claim-to-source support and references |
| Evidence | [`battery-metrics-audit`](skills/battery-metrics-audit/SKILL.md) | Check cell conditions, denominators, mechanisms, comparisons |
| Create | [`battery-review-write`](skills/battery-review-write/SKILL.md) | Draft or restructure evidence-led sections |
| Create | [`battery-review-figure`](skills/battery-review-figure/SKILL.md) | Plan, plot, export, and audit figures and rights |
| Refine | [`battery-review-polish`](skills/battery-review-polish/SKILL.md) | Polish, translate, or compress existing prose |
| Quality | [`battery-review-audit`](skills/battery-review-audit/SKILL.md) | Whole-manuscript scientific and structural preflight |
| Quality | [`battery-reviewer`](skills/battery-reviewer/SKILL.md) | Independent referee-style report on a frozen draft |
| Publish | [`battery-review-submission`](skills/battery-review-submission/SKILL.md) | Journal fit, current rules, and initial submission package |
| Revise | [`battery-review-response`](skills/battery-review-response/SKILL.md) | Point-by-point editor/reviewer response and change trace |

Use a specialist for one task and `battery-review-forge` when the work genuinely spans stages. The skill descriptions are deliberately narrow so Codex can choose without loading the whole suite. The battery metrics skill contains chemistry-specific checks for lithium-sulfur, solid-state, aqueous zinc, sodium-ion, and flow batteries; other chemistries use the shared evidence rules and claim-specific conditions.

## Why it matters

A battery Review can look complete while comparing unlike evidence. Half-cell capacity, projected pouch-cell energy, and symmetric-cell lifetime answer different questions. A hundred search records are also not a hundred checked experiments. This suite records source states separately, carries test conditions with every number, and keeps `NR` (checked but not reported) distinct from `NV` (not yet verified). It asks what a figure claims, whether that claim is supported, whether the artwork is legible at submission size, and whether reuse is actually permitted.

The aim is a useful scientific synthesis: a bounded question, a visible contribution relative to close Reviews, evidence for and against each key judgement, and a manuscript that still answers its original question after many editing sessions.

## Python figures for battery Reviews

The `battery-review-figure` skill includes an importable [Matplotlib library](skills/battery-review-figure/references/PYTHON_PLOTTING.md) for cycle retention, rate capability, comparable metric bars, and literature conditions matrices. Direct cross-study charts require verified values, source IDs, consistent units and matching declared cell/test conditions. `NR` and `NV` remain separate states. Exports include PDF, SVG, a 300 dpi review image, and a provenance sidecar. The code does not supply literature values or replace source checks and final-size visual review.

Run the synthetic demonstration after installing Matplotlib:

```bash
python skills/battery-review-figure/examples/demo_figures.py --output outputs/figure-demo
```

The sample values are invented for testing and must not enter a manuscript.

## Install locally

Install the complete package through its repository marketplace:

```bash
codex plugin marketplace add arrizabalagags-png/BatteryReviewForge
codex plugin add battery-review-forge@battery-review-forge
```

Start a new Codex task after installation so its skills are loaded. The package is also available as standalone skills: clone the repository and copy **all** skill folders using the commands below. The `$...` examples assume standalone installation; plugin skill names may be qualified by the plugin. See the [official skill documentation](https://learn.chatgpt.com/docs/build-skills) and [plugin packaging guide](https://developers.openai.com/plugins/build/plugins) for current distribution options.

**macOS / Linux**

```bash
git clone https://github.com/arrizabalagags-png/BatteryReviewForge.git
mkdir -p ~/.codex/skills
cp -R BatteryReviewForge/skills/* ~/.codex/skills/
```

**Windows PowerShell**

```powershell
git clone https://github.com/arrizabalagags-png/BatteryReviewForge.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Get-ChildItem ".\BatteryReviewForge\skills" -Directory | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination "$env:USERPROFILE\.codex\skills\" -Recurse -Force
}
```

Codex normally detects skill changes automatically; restart if newly copied skills do not appear.

## Try it

```text
Use $battery-review-plan to assess whether a Review on sodium-ion hard-carbon
presodiation has a distinct angle. State what you actually inspected in the
closest Reviews and produce a project brief before drafting prose.
```

```text
Use $battery-metrics-audit to audit this Li-S comparison table. Check sulfur
loading, E/S, lithium excess, cell configuration, and normalization. Mark NR
and NV separately and say which rows may be compared.
```

```text
Use $battery-review-figure to design a mechanism figure for our solid-state
battery Review. Trace each arrow to evidence and check rights and final-size
legibility before export.
```

```text
Use $battery-review-polish on these two existing paragraphs. Improve flow and
concision without changing numbers, citations, caveats, or technical terms.
```

```text
Use $battery-review-forge to coordinate this Review from topic selection to
submission. Start with scope and evidence feasibility, record decisions in
project files, and move stage by stage.
```

The skills adapt to existing project files. [Blank templates](skills/battery-review-plan/assets/templates/PROJECT_BRIEF.md) are optional starters, not a required new file tree. Read the [maintainer guide](docs/MAINTAINER_GUIDE.md) for design and release gates and the [behavioral scenarios](tests/scenarios.md) for examples of decisions the suite should make.

## Contribute

Bring an anonymized failure case, a sourced battery-specific correction, or a simpler workflow that improves a real task. See [CONTRIBUTING.md](CONTRIBUTING.md). Do not upload unpublished manuscripts, confidential review letters, licensed PDFs, private data, or institutional access details to issues or pull requests.

## 简体中文

**从选题到返修，把电池综述写成关键判断可追溯的论文。**

BatteryReviewForge 是面向电池领域 Review 和 Perspective 的 **模块化 Codex 技能组**。选题、检索、引文核验、性能比较、写作、图件、润色、整稿审计、投稿、独立审稿和返修都有独立入口；总入口只负责跨阶段协调。这样，要求“润色两段”时不会自动跑完整个投稿流程。

图件 skill 内置了 [Python 绘图库与使用说明](skills/battery-review-figure/references/PYTHON_PLOTTING.md)：支持循环保持率、倍率性能、同条件指标柱图与文献条件矩阵；要求来源 ID、已核数据和可比条件，导出 PDF/SVG、300 dpi 预览图及溯源记录。示例为明确标注的虚构数据，仅用于检查绘图库。

**合作署名：** 上海理工大学能源材料科学研究院 郭硕、姜金龙合作。
**开源协议：** [MIT](LICENSE)。

| 分类 | Skill | 任务 |
| --- | --- | --- |
| 全流程 | `battery-review-forge` | 跨阶段和跨会话协调 |
| 规划 | `battery-review-plan` | 选题边界、竞争综述、新意与大纲 |
| 证据 | `battery-literature-map` | 检索、筛选、去重、文献状态计数 |
| 证据 | `battery-claim-check` | 逐条核查论断、数字、引文和 DOI |
| 证据 | `battery-metrics-audit` | 电池指标、机制证据和跨论文可比性 |
| 创作 | `battery-review-write` | 基于证据起草、重构章节 |
| 创作 | `battery-review-figure` | 图件规划、制作、科学与版权审查 |
| 润色 | `battery-review-polish` | 润色、翻译、压缩已有文字 |
| 质控 | `battery-review-audit` | 整稿投稿前科学与一致性审计 |
| 质控 | `battery-reviewer` | 冻结稿件后的独立审稿意见 |
| 投稿 | `battery-review-submission` | 期刊匹配、最新官方要求、首次投稿包 |
| 返修 | `battery-review-response` | 编辑和审稿意见逐条回复、修改定位 |

### 核心做法

- 分开统计检索候选、已核元数据、已获全文、已读、已提取及真正支撑论点的文献。文献台账一篇一行，避免一篇论文因支持多个论断而重复计数。
- 对容量、倍率、寿命和能量保留电芯构型、测试方向和圈数、分母、载量、液量、温度等条件。`NR` 表示核过原文但未报告，`NV` 表示尚未核实；不同边界的结果不能无条件排名。
- 用近年相近综述的实际内容检验新意，不用“首篇”“全面”代替贡献。每个关键章节说清证据支持什么、哪里冲突、哪些结论仍有限制。
- 图件分别审查科学含义、版式可读性、有效分辨率和复用权利。写好了版权致谢，并不等于已经拿到许可。
- 投稿时按**目标期刊的具体文章类型**查询最新官方要求并记录网址与日期；审稿报告保留原件，返修逐条映射到正文。

### 安装与调用

可以先运行上方两条 `codex plugin` 命令安装整个插件，然后在新任务里调用各 skill；也可以克隆仓库，将 `skills` 下的**全部文件夹**复制到本机 `~/.codex/skills`（Windows 为用户目录下的 `.codex\skills`）。单项任务直接调用相应 skill：

```text
用 $battery-review-plan 规划一篇水系锌电池综述：先核查相近综述，
明确我们的新判断、证据缺口和每章职责。暂不写正文。
```

```text
用 $battery-review-figure 规划一张锂硫综述机制图：标清每个箭头是
实测、间接支持还是假说，并检查来源、复用许可和最终投稿尺寸。
```

```text
用 $battery-review-polish 润色以下已有段落，保持所有数值、引文、
限制条件和论断强度不变。
```

跨阶段项目调用 `$battery-review-forge`。已有项目文件优先；各 skill 的空模板只在缺少台账时使用。欢迎按[贡献指南](CONTRIBUTING.md)提交真实问题和可核验改进，不要公开上传未发表稿件、审稿信、下载的 PDF 或机构访问资料。
