# VoltPeer · 电研搭子


简体中文 · [English](README.en.md)

面向电池科研的开源 AI Skill 工具箱：科研绘图、Figure 拼图、机理示意、数据导入、论文写作、论证提纲与论文润色。

Skill 是给 AI 助手的一组科研工作说明和工具，需要在支持它的 AI 软件中使用。

[开始使用](#开始使用) · [看看效果](#看看实际效果) · [0.12.0 绘图候选包（Beta）](docs/assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip) · [项目网站](https://dazi.gsarrizabalaga.xyz/)

## 看看实际效果

**原创合成演示，非实验数据。** 每张图都保留对应数据、绘图代码和模型依据；不用于证明材料性能。[查看数据与源码](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/main/assets/github-showcase/README.md)

### [结构与光谱](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/main/assets/github-showcase/README.md#structure-and-spectra)

<a href="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/structure-spectra.png"><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/structure-spectra.png" alt="结构与光谱合成演示：Bragg 定律峰位演化、选定进度的衍射曲线、通用 Raman 谱和已知谱峰成分" width="1000"></a>

### [EIS：同一组数据，三个视角](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/main/assets/github-showcase/README.md#impedance-spectroscopy)

<a href="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/eis-cpe-warburg.png"><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/eis-cpe-warburg.png" alt="合成 CPE 与 Warburg 模型：横纵等尺度 Nyquist、阻抗模值和真实有符号相位" width="1000"></a>

### [多面板绘图示例](docs/assets/cycling-rule-v1.2.0/split-demos/integrated_study/integrated_study-source.zip)

<a href="docs/assets/cycling-rule-v1.2.0/showcase/integrated_study/figure.png"><img src="docs/assets/cycling-rule-v1.2.0/showcase/integrated_study/figure.png" alt="多面板合成演示：循环容量与库伦效率用散点，连续电压与EIS用实线；不代表真实实验结果" width="1000"></a>

<details>
<summary>再看一个 EIS 示例：理想 RC 电路</summary>

<img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/eis-ideal-rc.png" alt="原创理想 RC 电路合成示例：等尺度半圆 Nyquist、阻抗模值及相位" width="1000">

</details>


### 机理示意

<img src="assets/mechanism-showcase/desolvation.svg" alt="原创锂金属界面机理示意：抽象配体、脱溶剂化、SEI 内传输和电子路径" width="1000">

概念示意，不能当作实验验证。SVG 中的 D 代表抽象配位基团；重复离子表示过程快照。图件、源码和科学来源可在[机理图 Skill](skills/voltpeer-mechanism/SKILL.md)中取得。

## 你现在想做什么

| 七个主要产品 | 可以帮你做什么 |
| --- | --- |
| [科研绘图](skills/voltpeer-plot/SKILL.md) | 根据提供的数据、单位和测试条件绘制支持的科研图 |
| [Figure 拼图](skills/voltpeer-assemble/SKILL.md) | 对齐已有面板，统一尺寸、标签、字号和留白 |
| [机理图绘制](skills/voltpeer-mechanism/SKILL.md) | 核对材料、过程方向与证据，绘制可编辑的原创示意图 |
| [数据导入到绘图](skills/voltpeer-data/SKILL.md) | 自动识别源字段和明确单位，保留原文件并整理输入；绘图需另装 voltpeer-plot |
| [论文写作](skills/voltpeer-write/SKILL.md) | 基于作者实验输入或已核查文献，起草或重组研究论文与综述正文 |
| [论证与提纲规划](skills/voltpeer-plan/SKILL.md) | 梳理问题、中心论证、范围和章节逻辑 |
| [论文润色](skills/voltpeer-polish/SKILL.md) | 润色、翻译或压缩已有文字，保留科学含义和引用 |

## 开始使用

**第一次用，推荐 DeepSeek Harness 桌面端。**

1. 从 [DeepSeek 官网](https://www.deepseek.com/harness/)安装软件，按[入门指南](docs/GETTING_STARTED.md)配置模型并打开自己的科研项目文件夹。
2. 下载上方绘图包并完整解压，把包内 `AGENT_GUIDE.md` 交给 AI，让它配置环境、安装绘图 Skill，并在新会话确认实际读到技能文件。
3. 先跑合成 Demo，打开结果里的 `index.html`；再换自己的数据，确认列名、单位和测试条件后画图。

绘图环境需要 Python ≥3.10 与下载依赖的网络，AI 可按包内指南配置隔离环境。包开源免费；使用 AI 的费用取决于所选软件与模型。[安装、费用与遇到问题的下一步](docs/GETTING_STARTED.md)。

<details>
<summary>我会安装，直接拿包 / 其他软件</summary>

- [0.12.0 绘图候选包：固定程序、一个绘图 Skill 与 Demo](docs/assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip) · [包索引与校验](docs/downloads/v0.12.0-cycling-rule-v1.2.1/download-index.json)
- [历史 0.10.1 绘图包](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip)
- [历史 0.10.1 全部 15 个技能包](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/BatteryReviewForge-v0.10.1.zip) · [历史 0.9.2 正式包](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/download/v0.9.2/BatteryReviewForge-v0.9.2.zip)
- Codex、Kimi Code、WorkBuddy 及单 Skill 安装见[软件适配](docs/COMPATIBILITY.md)；用对应入口检查实际识别情况。
- 模型、宿主和工具能力分别核查；具体状态见下方版本与验证入口。

</details>

## 用哪个 Skill

| 手里的材料 | 对应入口 |
| --- | --- |
| 原始数据表 | [`voltpeer-data`](skills/voltpeer-data/SKILL.md) → [`voltpeer-plot`](skills/voltpeer-plot/SKILL.md) |
| 已画好的几个面板 | [`voltpeer-assemble`](skills/voltpeer-assemble/SKILL.md) |
| 综述主题与文献 | [`voltpeer-plan`](skills/voltpeer-plan/SKILL.md) → [`voltpeer-literature`](skills/voltpeer-literature/SKILL.md) → [`voltpeer-write`](skills/voltpeer-write/SKILL.md) |
| 待检查的稿件 | [`voltpeer-review-audit`](skills/voltpeer-review-audit/SKILL.md) |
| 需要分阶段推进的整个项目 | [`voltpeer-workflow`](skills/voltpeer-workflow/SKILL.md) |

<details>
<summary>查看全部 16 个 Skills</summary>

| Skill | 用途 |
| --- | --- |
| [`voltpeer-data`](skills/voltpeer-data/SKILL.md) | 整理数据 |
| [`voltpeer-plot`](skills/voltpeer-plot/SKILL.md) | 绘图、图注与科学核对 |
| [`voltpeer-assemble`](skills/voltpeer-assemble/SKILL.md) | 已有图件拼版 |
| [`voltpeer-mechanism`](skills/voltpeer-mechanism/SKILL.md) | 原创机理示意与可编辑 SVG |
| [`voltpeer-experiment-plan`](skills/voltpeer-experiment-plan/SKILL.md) | 规划实验与对照 |
| [`voltpeer-literature`](skills/voltpeer-literature/SKILL.md) | 检索、筛选与文献台账 |
| [`voltpeer-claim-check`](skills/voltpeer-claim-check/SKILL.md) | 逐条核查论断与引用 |
| [`voltpeer-metrics`](skills/voltpeer-metrics/SKILL.md) | 性能数据可比性审查 |
| [`voltpeer-plan`](skills/voltpeer-plan/SKILL.md) | 综述选题与结构 |
| [`voltpeer-write`](skills/voltpeer-write/SKILL.md) | 基于证据写正文 |
| [`voltpeer-polish`](skills/voltpeer-polish/SKILL.md) | 润色、翻译与压缩 |
| [`voltpeer-review-audit`](skills/voltpeer-review-audit/SKILL.md) | 投稿前全文审查 |
| [`voltpeer-submission`](skills/voltpeer-submission/SKILL.md) | 期刊匹配与投稿材料 |
| [`voltpeer-response`](skills/voltpeer-response/SKILL.md) | 逐点返修与回复 |
| [`voltpeer-reviewer`](skills/voltpeer-reviewer/SKILL.md) | 独立审稿式评议 |
| [`voltpeer-workflow`](skills/voltpeer-workflow/SKILL.md) | 多阶段项目协调 |

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

当前源码版本为 **0.12.0 Beta**。上面的旧提交下载保持 **0.10.1 Beta** 与 **0.9.2** 的历史身份，旧 0.10.2 科学包也保持原字节。研究论文、综述和润色的输入与交付契约已单独补充；完整原生宿主与模型行为门禁仍为 NOT_RUN，旧 Flash 有限 API 试次保留其 PARTIAL 范围。[当前候选说明](docs/RELEASE_v0.12.0.md) · [实际适配与验证范围](docs/COMPATIBILITY.md)。

| 想深入了解 | 文档 |
| --- | --- |
| 安装和第一次画图 | [入门指南](docs/GETTING_STARTED.md) |
| 作者数据、配色与出图 | [绘图说明](skills/voltpeer-plot/references/UPLOADED_DATA.md) |
| 投稿尺寸与多面板排版 | [拼版说明](skills/voltpeer-assemble/references/COMPOSITION.md) |
| 文献与证据 / 综述 / 实验规划 | [文献整理](skills/voltpeer-literature/SKILL.md) · [综述流程](skills/voltpeer-plan/SKILL.md) · [实验规划](skills/voltpeer-experiment-plan/SKILL.md) |
| 软件检查与行为测试 | [验证协议与记录](docs/EVAL.md) |
| 维护与完整技术资料 | [维护指南](docs/MAINTAINER_GUIDE.md) · [本分支原技术全文](docs/TECHNICAL_REFERENCE_v0.10.1.md) |

郭硕（Shuo Guo）· 姜金龙（Jinlong Jiang），上海理工大学能源材料科学研究院。[作者](AUTHORS.md) · [引用](CITATION.cff) · [MIT](LICENSE) · [贡献](CONTRIBUTING.md) · [反馈与求助](SUPPORT.md) · [安全报告](SECURITY.md)。历史包名与技术 ID 保持兼容。
