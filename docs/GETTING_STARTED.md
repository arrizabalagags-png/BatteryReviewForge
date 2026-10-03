# 从第一张图开始

[首页](../README.md) · [English](#english)

本页使用 **0.12.0 Beta 绘图 Starter**，包修订为 `cycling-rule-v1.2.1`。保留完整的 `plot_starter` 文件夹，里面的 `AGENT_GUIDE.md`、固定程序与示例一起使用。它只包含一个 `voltpeer-plot` 技能；全部技能包另有 16 个 Skill。Beta 包已在仓库公开，尚未发布为完整正式 Release，也尚未完成全部客户端从安装到出图的实测。[版本与包范围](RELEASE_v0.12.0.md) · [旧安装迁移](NAMING_MIGRATION.md)。

## 1. 打开 AI 软件和项目

从 [DeepSeek Harness 官网](https://www.deepseek.com/harness/)下载安装当前系统的桌面版，然后打开一个自己的研究项目文件夹作为工作区。官方目前提供 Windows 64 位和 Apple 芯片 macOS 下载。

按软件当前的模型设置入口配置 DeepSeek。API key 在 [DeepSeek 平台](https://platform.deepseek.com/)创建并保存在软件的供应商设置中；不要发到对话、仓库或给作者。[官方模型设置说明](https://deepseek-harness.github.io/deepseek-harness/guide/quickstart#配置模型)。

Skill 包开源免费，安装程序本身不需要 API key；AI 理解文件、执行工具会使用你所选模型的 API 或软件额度。实时费用以[提供方价格表](https://api-docs.deepseek.com/quick_start/pricing/)为准。

## 2. 下载绘图包，让 AI 按指南安装

[下载 VoltPeer 0.12.0 绘图 Starter（Beta）](assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip)，完整解压后把 `plot_starter` 文件夹放到你的研究项目中。它包含固定 Python 绘图实现、一个 Skill 和合成示例。[其他样例数据与源码](../assets/github-showcase/README.md)供参考；样例源码包不能代替技能安装包。

告诉 AI：

> 请先读 plot_starter/AGENT_GUIDE.md，检查 Python 和依赖，按指南准备隔离环境并安装绘图 Skill。告诉我需要新开会话核对的实际技能文件位置；缺条件先说明。

本机需要 Python ≥3.10 和下载依赖的网络；包内 `setup` 安装到它自己的 `.venv`。如果 Python 未安装，让 AI 根据实际系统说明需要补的步骤，再继续。当前下载不提供 Python 解释器。

安装后新开会话，请 AI 定位并读取实际装入的 `voltpeer-plot/SKILL.md`。复制完成不能证明软件已经识别。本包按官方项目路径安装为 `.dsh/skills`；[官方发现规则](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/skills#本地发现优先级)。

## 3. 看 Demo，再换自己的数据

在新会话确认技能已读到后，告诉 AI：

> 请用包内程序跑合成 Demo，输出到项目下的 demo-result。检查文件实际存在，再给我预览和图件链接；失败就说明缺什么，不要报完成。

打开实际生成的 `demo-result/index.html`，图件在 `demo-result/results/`。默认导出 PNG、SVG、PDF；需要 TIFF 时按指南指定格式。再次运行保留旧结果，新目录可带 `_v002` 等后缀。这一步使用合成数据。

再提供自己的 CSV / TSV / TXT / XLSX、想画的图型、单位与已核查的测试条件。AI 先检查真实表头，再请你确认含义；缺科学条件时停下来补材料。示例里的实验参数不能填到自己的数据里。

按当前 Starter 规则，逐圈容量、库伦效率与保持率用散点，不连线；连续电压、谱线与 EIS 用不同颜色的无点实线，数据坐标保留四边框。原始异常值保留。全电池保持率需要明确参考圈、参考容量和一致的条件；Li‖Cu 库伦效率不强加保持率。投稿尺寸、DPI 与格式按目标期刊核对，默认 PNG 300 dpi 不代表所有期刊合规。

自己的数据也输出到你指定的工作文件夹，其根目录是 `index.html`，图件在 `results/`。保留整个工作文件夹方便继续修改；公开分享前另行检查隐私与权利。

## 卡住时，检查当前一步

| 现象 | 下一步 |
| --- | --- |
| 软件不能调用模型 | 核对该软件的 API key、额度和网络，按真实错误处理 |
| AI 没有读到技能 | 核查当前项目根、新会话与实际 Skill 文件路径 |
| Python / 依赖报错 | 按指南检查隔离环境与具体错误，不全局混装依赖 |
| 不知道表里列的含义 | 补作者确认的单位、分母与实验条件，保留原始文件 |
| 已导出但没有可点的链接 | 请 AI 给当前软件可打开的结果文件链接；核对真实文件是否存在 |

安装与模型证据见[当前适配记录](COMPATIBILITY.md)。原生 DeepSeek Harness 桌面从技能发现到交付尚未完成当前版本的全程实测；此前有限 API 试次保留原版本和范围，不能替代你所用软件的实际检查。

<details>
<summary>手动命令与其他任务</summary>

在完整解压的 `plot_starter` 文件夹终端执行，工作区路径换成你已经打开的项目根：

```sh
python start.py check
python start.py setup
python start.py install --host dsh --workspace "你的项目根目录"
python start.py demo --out "../demo-result"
```

这些命令从项目里的 `plot_starter` 目录运行，`../demo-result` 指向项目下的示例工作文件夹；也可以传入完整输出路径。`setup` 准备本包隔离依赖，`install` 复制绘图技能；在新会话确认发现后继续任务。高级用户可按包内 `INPUT_GUIDE.md` 使用 `inspect` / `plot` / `check`；映射只填作者真实确认的信息。

Codex 使用同一绘图包，把 `--host dsh` 改成 `--host codex`。Kimi Code、WorkBuddy、完整技能包和单 Skill 的已有路线见[适配说明](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/COMPATIBILITY.md)；按所选软件检查实际识别与执行能力。

Figure 拼版选 [voltpeer-assemble](../skills/voltpeer-assemble/SKILL.md)，其他任务按[首页任务表](../README.md#你可以用它做什么)选择。[0.12.0 全部技能包（Beta）](downloads/v0.12.0-cycling-rule-v1.2.1/VoltPeer-v0.12.0.zip)包含 16 个 Skill 与迁移安装器；独立安装数据导入 Skill 后，出图还需安装绘图 Skill。历史下载见[当前版本说明](RELEASE_v0.12.0.md#历史版本)，原安装资料保留在[技术归档](TECHNICAL_REFERENCE_v0.10.1.md)。

</details>

## 包与校验

- 推荐绘图 Starter：`assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip`，743,774 bytes。
- SHA-256：`289b1d3a2e37fd11c8c3955fc3be1394b21abfb3a0c676bfeb06fb72344979df`。
- 全部技能包、单 Skill 包和 Starter 的实际字节及 SHA-256 见[当前校验索引](downloads/v0.12.0-cycling-rule-v1.2.1/download-index.json)。该索引保留构建时的状态，公开情况见[当前版本说明](RELEASE_v0.12.0.md)。
- 独立安装 `voltpeer-data` 后需要同时安装 `voltpeer-plot` 才能调用绘图程序。

### 保留的历史 0.10.1 下载

[固定历史绘图包](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip)与以下身份继续保留；它内部使用当时的旧 Skill 名称。

- 绘图包：`VoltPeer-Plot-Starter-v0.10.1.zip`，580,632 bytes。
- SHA-256：`392b58b6a211c35f88a0148c95d07b9accb5b6eeb000640883466d96d3ab466a`。
- 下载固定在已检查的源码提交 `dfd46fcb4a3255b60826de8a4c721963adc4ff02`。本页不重新打包；详细[版本说明](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/RELEASE_v0.10.1.md)保留实际验证范围。

## English

1. Install DeepSeek Harness from its [official download page](https://www.deepseek.com/harness/), configure a model in the application's settings, and open your research project folder. Create your key on the [DeepSeek platform](https://platform.deepseek.com/) and save it in the application's provider settings. The Skill package is free; AI calls follow your provider's charges. Package installation itself needs no API key.
2. Download the plotting package above, extract it fully and put its `plot_starter` folder inside the project. Give the AI `AGENT_GUIDE.md` and ask it to prepare the isolated environment, install the Skill and run the synthetic demo. Python ≥3.10 and a network connection for dependencies are required; the package does not include a Python interpreter.
3. In a new session, confirm that the AI can read the actual installed Skill, then ask it to run the synthetic demo into `demo-result` under your project. Open `demo-result/index.html` and check PNG, SVG and PDF files in `demo-result/results/`. Repeated runs preserve earlier outputs in versioned folders. Then supply your own files and confirm fields, units and scientific conditions; demo parameters must never fill gaps in author data.

Address the step that fails: model settings, Skill discovery, Python dependencies, missing scientific information or a missing result link. The shell commands above run inside `plot_starter`; `../demo-result` is in its parent project. Current client and complete model testing remain incomplete; earlier API trials apply only to their recorded versions. See [compatibility](COMPATIBILITY.md).

The current package is **0.12.0 Beta, revision cycling-rule-v1.2.1**, with one plotting Skill. The full package has 16 Skills. Per-cycle capacity, efficiency and retention use markers without connecting lines; continuous signals use solid marker-free curves with all four frame sides. Full-cell retention requires a stated reference cycle and capacity under matching conditions. See [tasks](../README.en.md#what-you-can-do), [version and download notes](RELEASE_v0.12.0.md) and the compatibility guide. Check privacy settings before using unpublished files, and verify results and rights before publication.


## 旧安装迁移

当前使用 16 个 `voltpeer-*` 技术 ID。旧命名迁移规则见[迁移说明](NAMING_MIGRATION.md)；普通安装会拒绝旧名重复，显式更新保留旧目录与自定义内容。迁移说明中 0.11.0 的 15 项映射保持原范围，新机理 Skill 为本版新增。
