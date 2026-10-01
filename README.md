# VoltPeer · 电研搭子

简体中文 · [English](README.en.md)

面向电池科研的开源 AI Skill 工具箱：整理数据、画科研图、拼 Figure、核查文献与写综述。

Skill 是给 AI 助手的一组科研工作说明和工具，需要在支持它的 AI 软件中使用。

[开始使用](#开始使用) · [看看效果](#看看实际效果) · [下载绘图包（Beta）](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip) · [项目网站](https://dazi.gsarrizabalaga.xyz/)

## 你现在想做什么

| 任务 | 可以从这里开始 |
| --- | --- |
| [整理实验数据](skills/battery-data-prepare/SKILL.md) | 核对 CSV / 仪器导出表的列名、单位与整理记录 |
| [画科研图](skills/battery-review-figure/SKILL.md) | 从作者数据绘制容量、库伦效率、EIS 等常用图 |
| [拼 Figure](skills/battery-figure-assemble/SKILL.md) | 统一已有面板的尺寸、标签、字号和留白 |
| [整理文献](skills/battery-literature-map/SKILL.md) | 建立筛选记录、文献台账与证据关系 |
| [写 Review](skills/battery-review-plan/SKILL.md) | 从选题、结构和证据，推进到正文与修改 |
| [投稿前检查](skills/battery-review-audit/SKILL.md) | 核查指标可比性、引用和全文一致性 |

## 看看实际效果

以下是开发分支中的**原创合成 Demo，非实验数据**。图件用于展示绘图与组合方式，不能作为材料性能证据。每个标题可打开对应数据、脚本和来源说明；素材按项目 [MIT 许可](LICENSE)提供。

| [库伦效率与剥离曲线](https://github.com/arrizabalagags-png/Voltpeer-skills/tree/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/li_cu_ce)<br><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/li_cu_ce/figure.png" alt="库伦效率与剥离曲线 — synthetic demo" width="420"> | [容量循环与电压曲线](https://github.com/arrizabalagags-png/Voltpeer-skills/tree/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/full_cell)<br><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/full_cell/figure.png" alt="容量循环与电压曲线 — synthetic demo" width="420"> |
| --- | --- |
| [EIS Nyquist 与相位](https://github.com/arrizabalagags-png/Voltpeer-skills/tree/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/eis)<br><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/eis/figure.png" alt="EIS Nyquist 与相位 — synthetic demo" width="420"> | [关联数据六面板](https://github.com/arrizabalagags-png/Voltpeer-skills/tree/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/integrated_study)<br><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase/integrated_study/figure.png" alt="关联数据六面板 — synthetic demo" width="420"> |

## 开始使用

**第一次用，推荐 DeepSeek Harness 桌面端。**

1. 从 [DeepSeek 官网](https://www.deepseek.com/harness/)安装软件，按[入门指南](docs/GETTING_STARTED.md)配置模型并打开自己的科研项目文件夹。
2. 下载上方绘图包并完整解压，把包内 `AGENT_GUIDE.md` 交给 AI，让它配置环境、安装绘图 Skill，并在新会话确认实际读到技能文件。
3. 先跑合成 Demo，打开结果里的 `index.html`；再换自己的数据，确认列名、单位和测试条件后画图。

绘图环境需要 Python ≥3.10 与下载依赖的网络，AI 可按包内指南配置隔离环境。包开源免费；使用 AI 的费用取决于所选软件与模型。[安装、费用与遇到问题的下一步](docs/GETTING_STARTED.md)。

<details>
<summary>我会安装，直接拿包 / 其他软件</summary>

- [绘图包：固定程序、一个绘图 Skill 与 Demo](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip)
- [全部 15 个技能的开发包](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/BatteryReviewForge-v0.10.1.zip) · [正式完整包](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/download/v0.9.2/BatteryReviewForge-v0.9.2.zip)
- Codex、Kimi Code、WorkBuddy 及单 Skill 安装见[软件适配](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/COMPATIBILITY.md)；用对应入口检查实际识别情况。
- 模型、宿主和工具能力分别核查；具体状态见下方版本与验证入口。

</details>

## 用哪个 Skill

| 手里的材料 | 对应入口 |
| --- | --- |
| 原始数据表 | [`battery-data-prepare`](skills/battery-data-prepare/SKILL.md) → [`battery-review-figure`](skills/battery-review-figure/SKILL.md) |
| 已画好的几个面板 | [`battery-figure-assemble`](skills/battery-figure-assemble/SKILL.md) |
| 综述主题与文献 | [`battery-review-plan`](skills/battery-review-plan/SKILL.md) → [`battery-literature-map`](skills/battery-literature-map/SKILL.md) → [`battery-review-write`](skills/battery-review-write/SKILL.md) |
| 待检查的稿件 | [`battery-review-audit`](skills/battery-review-audit/SKILL.md) |
| 需要分阶段推进的整个项目 | [`battery-review-forge`](skills/battery-review-forge/SKILL.md) |

<details>
<summary>查看全部 15 个 Skills</summary>

| Skill | 用途 |
| --- | --- |
| [`battery-data-prepare`](skills/battery-data-prepare/SKILL.md) | 整理数据 |
| [`battery-review-figure`](skills/battery-review-figure/SKILL.md) | 绘图、图注与科学核对 |
| [`battery-figure-assemble`](skills/battery-figure-assemble/SKILL.md) | 已有图件拼版 |
| [`battery-experiment-plan`](skills/battery-experiment-plan/SKILL.md) | 规划实验与对照 |
| [`battery-literature-map`](skills/battery-literature-map/SKILL.md) | 检索、筛选与文献台账 |
| [`battery-claim-check`](skills/battery-claim-check/SKILL.md) | 逐条核查论断与引用 |
| [`battery-metrics-audit`](skills/battery-metrics-audit/SKILL.md) | 性能数据可比性审查 |
| [`battery-review-plan`](skills/battery-review-plan/SKILL.md) | 综述选题与结构 |
| [`battery-review-write`](skills/battery-review-write/SKILL.md) | 基于证据写正文 |
| [`battery-review-polish`](skills/battery-review-polish/SKILL.md) | 润色、翻译与压缩 |
| [`battery-review-audit`](skills/battery-review-audit/SKILL.md) | 投稿前全文审查 |
| [`battery-review-submission`](skills/battery-review-submission/SKILL.md) | 期刊匹配与投稿材料 |
| [`battery-review-response`](skills/battery-review-response/SKILL.md) | 逐点返修与回复 |
| [`battery-reviewer`](skills/battery-reviewer/SKILL.md) | 独立审稿式评议 |
| [`battery-review-forge`](skills/battery-review-forge/SKILL.md) | 多阶段项目协调 |

</details>

## 复制一句话试试

> 这是我的循环数据.csv。先核对列名、单位和测试条件，再画容量—循环曲线；保留原始值。

> 这 6 张图准备拼成 Fig. 3。按投稿尺寸统一标签、字号和留白，保留原图。

> 这是综述大纲和文献。先整理已读证据与缺口，再讨论正文结构。

> 检查这张电池性能表能否横向比较；缺失条件先列出来。

> 检查这一段的数字和引用是否得到原文支持，未核查项明确标出。

## 数据与科研责任

- 绘图使用包内程序；先核对输入，缺失单位、条件或来源时先补材料。
- 本项目不要求把科研文件上传到网站，也不向你索取 API key；材料是否发送给模型取决于你选择的 AI 软件。
- 使用未公开数据前，检查所用软件的隐私政策；公开投稿或反馈前先脱敏并核实分享权利。
- 作者负责最终核对数据、引用、版权与科学结论。缺少报告和未经核查是不同状态，不能当成零或已验证。

## 文档与当前范围

本分支保留 **0.9.2 正式技能包**；上方绘图包与预览来自 **0.10.1 Beta** 开发分支。 原生桌面发现与完整行为验收仍待验证；Flash 有限 API 试次的交付表达为 PARTIAL。[版本说明](docs/RELEASE_v0.9.2.md) · [实际适配与验证范围](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/COMPATIBILITY.md)。

| 想深入了解 | 文档 |
| --- | --- |
| 安装和第一次画图 | [入门指南](docs/GETTING_STARTED.md) |
| 作者数据、配色与出图 | [绘图说明](skills/battery-review-figure/references/UPLOADED_DATA.md) |
| 投稿尺寸与多面板排版 | [拼版说明](skills/battery-figure-assemble/references/COMPOSITION.md) |
| 文献与证据 / 综述 / 实验规划 | [文献整理](skills/battery-literature-map/SKILL.md) · [综述流程](skills/battery-review-plan/SKILL.md) · [实验规划](skills/battery-experiment-plan/SKILL.md) |
| 软件检查与行为测试 | [验证协议与记录](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/EVAL.md) |
| 维护与完整技术资料 | [维护指南](docs/MAINTAINER_GUIDE.md) · [本分支原技术全文](docs/TECHNICAL_REFERENCE_v0.9.2.md) |

郭硕（Shuo Guo）· 姜金龙（Jinlong Jiang），上海理工大学能源材料科学研究院。[作者](AUTHORS.md) · [引用](CITATION.cff) · [MIT](LICENSE) · [贡献](CONTRIBUTING.md) · [反馈与求助](SUPPORT.md) · [安全报告](SECURITY.md)。历史包名与技术 ID 保持兼容。
