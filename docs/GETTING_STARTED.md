# 从第一张图开始

[首页](../README.md) · [English](#english)

本页使用本地 **0.11.0 Beta 绘图候选包**。保留整个解压文件夹，里面的 `AGENT_GUIDE.md`、固定绘图程序与示例要一起使用。它包含 `voltpeer-plot`；更新旧安装先读[迁移说明](NAMING_MIGRATION.md)。当前包未发布为 GitHub Release，原生宿主和完整模型门禁为 NOT_RUN。

## 1. 打开 AI 软件和项目

从 [DeepSeek Harness 官网](https://www.deepseek.com/harness/)下载安装当前系统的桌面版，然后打开一个自己的研究项目文件夹作为工作区。官方目前提供 Windows 64 位和 Apple 芯片 macOS 下载。

按软件当前的模型设置入口配置 DeepSeek。API key 在 [DeepSeek 平台](https://platform.deepseek.com/)创建并保存在软件的供应商设置中；不要发到对话、仓库或给作者。[官方模型设置说明](https://deepseek-harness.github.io/deepseek-harness/guide/quickstart#配置模型)。

Skill 包开源免费，安装程序本身不需要 API key；AI 理解文件、执行工具会使用你所选模型的 API 或软件额度。实时费用以[提供方价格表](https://api-docs.deepseek.com/quick_start/pricing/)为准。

## 2. 下载绘图包，让 AI 按指南安装

[下载 VoltPeer 0.11.0 绘图候选包](downloads/v0.11.0/starter/VoltPeer-Plot-Starter-v0.11.0.zip)，完整解压后把 `plot_starter` 文件夹放到你的研究项目中。这个包包含 Python 绘图实现与一个 Skill；[固定历史示例数据目录](https://github.com/arrizabalagags-png/Voltpeer-skills/tree/dfd46fcb4a3255b60826de8a4c721963adc4ff02/examples/showcase)用于看数据和脚本，不是安装包。

告诉 AI：

> 请先读 plot_starter/AGENT_GUIDE.md，按指南准备隔离环境、把绘图 Skill 安装到本项目，再跑一次合成 Demo。只给我结果入口和真正缺少的条件。

本机需要 Python ≥3.10 和下载依赖的网络；包内 `setup` 安装到它自己的 `.venv`。如果 Python 未安装，让 AI 根据实际系统说明需要补的步骤，再继续。当前下载不提供 Python 解释器。

安装后新开会话，请 AI 定位并读取实际装入的 `voltpeer-plot/SKILL.md`。复制完成不能证明软件已经识别。本包按官方项目路径安装为 `.dsh/skills`；[官方发现规则](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/skills#本地发现优先级)。

## 3. 看 Demo，再换自己的数据

打开 AI 给出的结果 `index.html`，看 PNG 预览和 PDF/SVG 图件。这一步用的是合成数据。

再提供自己的 CSV / TSV / TXT / XLSX、想画的图型、单位与已核查的测试条件。AI 先检查真实表头，再请你确认含义；缺科学条件时停下来补材料。示例里的实验参数不能填到自己的数据里。

按当前 Starter 规则，连续数据曲线采用实线、不同颜色、无点和四边框，原始异常值保留。投稿尺寸、DPI 与格式按目标期刊核对，默认 PNG 300 dpi 不代表所有期刊合规。

正常结果在 `results/`，再次出图保留版本；工作区里的内部记录供恢复和按需核对，公开分享前另外检查隐私与权利。

## 卡住时，检查当前一步

| 现象 | 下一步 |
| --- | --- |
| 软件不能调用模型 | 核对该软件的 API key、额度和网络，按真实错误处理 |
| AI 没有读到技能 | 核查当前项目根、新会话与实际 Skill 文件路径 |
| Python / 依赖报错 | 按指南检查隔离环境与具体错误，不全局混装依赖 |
| 不知道表里列的含义 | 补作者确认的单位、分母与实验条件，保留原始文件 |
| 已导出但没有可点的链接 | 请 AI 给当前软件可打开的结果文件链接；核对真实文件是否存在 |

安装与模型证据见[当前适配记录](COMPATIBILITY.md)。原生 DeepSeek Harness 桌面发现尚未完整实测；有限直连 Flash API 试次的最终链接表达仍 PARTIAL，不能把安装器或单次 API 结果当成所有机器可用。

<details>
<summary>手动命令与其他任务</summary>

在完整解压的 `plot_starter` 文件夹终端执行，工作区路径换成你已经打开的项目根：

```sh
python start.py check
python start.py setup
python start.py install --host dsh --workspace "你的项目根目录"
python start.py demo --out "demo-result"
```

命令与 `AGENT_GUIDE.md` 一致。`setup` 准备本包隔离依赖，`install` 复制绘图技能；在新会话确认发现后继续任务。高级用户可按包内 `INPUT_GUIDE.md` 使用 `inspect` / `plot` / `check`；映射只填作者真实确认的信息。

Codex 使用同一绘图包，把 `--host dsh` 改成 `--host codex`。Kimi Code、WorkBuddy、完整技能包和单 Skill 的已有路线见[适配说明](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/COMPATIBILITY.md)；按所选软件检查实际识别与执行能力。

拼已有面板选 [voltpeer-assemble](../skills/voltpeer-assemble/SKILL.md)，文字与文献任务按[首页任务表](../README.md#用哪个-skill)选择所需技能。[0.11.0 完整候选包](downloads/v0.11.0/VoltPeer-v0.11.0.zip)包含 15 个新名称 Skill 与迁移安装器。历史完整包：[0.10.1 开发包](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/BatteryReviewForge-v0.10.1.zip) / [0.9.2 正式发布包](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/download/v0.9.2/BatteryReviewForge-v0.9.2.zip)。历史安装说明留在[技术归档](TECHNICAL_REFERENCE_v0.10.1.md)。

</details>

## 包与校验

- 当前候选包：`downloads/v0.11.0/starter/VoltPeer-Plot-Starter-v0.11.0.zip`。
- 实际字节和 SHA-256 见[Starter 索引](downloads/v0.11.0/starter/plot-starter.json)与[全部 34 个新包的校验索引](downloads/v0.11.0/download-index.json)。
- 独立安装 `voltpeer-data` 后需要同时安装 `voltpeer-plot` 才能调用绘图程序。

### 保留的历史 0.10.1 下载

[固定历史绘图包](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip)与以下身份继续保留；它内部使用当时的旧 Skill 名称。

- 绘图包：`VoltPeer-Plot-Starter-v0.10.1.zip`，580,632 bytes。
- SHA-256：`392b58b6a211c35f88a0148c95d07b9accb5b6eeb000640883466d96d3ab466a`。
- 下载固定在已检查的源码提交 `dfd46fcb4a3255b60826de8a4c721963adc4ff02`。本页不重新打包；详细[版本说明](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/RELEASE_v0.10.1.md)保留实际验证范围。

## English

1. Install DeepSeek Harness from its [official download page](https://www.deepseek.com/harness/), configure a model in the application's settings, and open your research project folder. Create your key on the [DeepSeek platform](https://platform.deepseek.com/) and save it in the application's provider settings. The Skill package is free; AI calls follow your provider's charges. Package installation itself needs no API key.
2. Download the plotting package above, extract it fully and put its `plot_starter` folder inside the project. Give the AI `AGENT_GUIDE.md` and ask it to prepare the isolated environment, install the Skill and run the synthetic demo. Python ≥3.10 and a network connection for dependencies are required; the package does not include a Python interpreter.
3. In a new session, ask the AI to locate the installed Skill. Open the result's `index.html` and inspect the synthetic PNG preview and PDF/SVG exports. Then supply your own files and confirm fields, units and scientific conditions. Demo conditions must never fill gaps in author data.
4. Address only the step that fails: model settings, actual Skill discovery, Python dependencies, missing scientific information or a missing result link. The commands in the collapsed section match the package guide; substitute your real project path. Native desktop discovery and full behavior coverage remain pending; Flash's limited API delivery-formatting trial remains PARTIAL. See the [exact compatibility record](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/COMPATIBILITY.md).

The checksums and frozen source above identify the download. For other applications or research tasks, use the [task routes](../README.en.md#choose-by-task) and the compatibility guide. Check your AI application's privacy policy before using unpublished files, and verify results and rights before publication.


## VoltPeer 0.11.0 naming migration

The current naming candidate uses 15 canonical VoltPeer Skill IDs. Before updating an existing installation, follow [the migration guide](NAMING_MIGRATION.md); ordinary installation refuses legacy duplicates and explicit updates preserve old trees/customisations outside discovery. Historical version links retain their recorded identity.
