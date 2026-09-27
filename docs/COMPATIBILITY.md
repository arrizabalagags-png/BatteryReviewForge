# 软件适配记录（技术资料）

普通使用者请走[开始使用](https://dazi.gsarrizabalaga.xyz/start.html)或[WorkBuddy 分步教程](https://dazi.gsarrizabalaga.xyz/install-workbuddy.html)。教程区分国内可选路线与已能正常使用 Codex 的路线，不要求更换熟悉的软件。BatteryReviewForge 是 `SKILL.md` 指令、Python 脚本和原创图形资源；没有独立账户、模型 API 或密钥输入框。核对日期：2026-09-27。

必须分别记录：文件已复制（copied）、新会话发现技能（discovered）、依赖环境可用（runtime_ready）、真实导出成功（smoke_test_passed）。网页点击“继续”、脚本复制和包结构测试都不能替代原生客户端完整验收。本轮在临时目录测试包内容、冲突备份和 Python 导出；没有重新完成原生客户端登录、导入、发现到出图的全流程。

| 软件 | 现在能做什么 | 本项目验证状态 |
| --- | --- | --- |
| **Codex** | 使用插件，或请 Codex 检查固定官方仓库后安装独立技能 | 有历史 Windows 使用记录；v0.8.7 新安装与其他系统完整任务待实测 |
| **Kimi Code CLI** | 把 15 个技能复制到官方扫描目录 | 官方技能格式与路径已确认；本项目完整任务待实机验收 |
| **DeepSeek Harness** | 把 15 个技能复制到官方扫描目录 | 官方本地技能机制已确认；本项目完整任务待实机验收 |
| **WorkBuddy** | 绘图与拼图入门套装仅含 2 个独立技能 ZIP | 官方入口与包内共享引用已检查；客户端导入、发现、运行仍待实测 |
| **豆包桌面工作任务** | 可先用内置 Skills 和普通文件问答 | 尚无已核实的第三方 `SKILL.md` 导入步骤；目前不声称可一键安装 |

## 第 1 步：先登录你自己的 Agent

**Codex**：在 Codex 应用或 CLI 按提示登录。使用本项目绘图时，不需要另买或填写“BatteryReviewForge API Key”。[官方插件说明](https://developers.openai.com/plugins/build/plugins)。

**Kimi Code CLI**：首次运行 `kimi` 后输入 `/login`，按屏幕提示选 **Kimi Code 账号登录** 或 **Kimi Platform API Key**。前者不需要手动管理 Key。[官方入门说明](https://www.kimi.com/code/docs/en/kimi-code-cli/guides/getting-started)。

**DeepSeek Harness**：在软件的 **Settings → Models** 中配置 DeepSeek 或你自己使用的模型提供方。只在该软件自己的设置页输入 Key。[官方模型设置说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/providers.md)。

**WorkBuddy**：从 [WorkBuddy 官方产品页](https://www.workbuddy.cn/work/)下载，按客户端提示登录，再回到客户端。[官方技能说明](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)。账号、额度和额外模型费用以该软件的官方账户说明为准。

**豆包**：使用豆包官方账号与客户端。桌面版支持“工作任务”和内置 Skills，但目前没有核实到可供本项目采用的第三方技能包导入规范。[官方下载页](https://www.doubao.com/download/desktop)。

> **任何情况都不要把 API Key 粘到这个网站、GitHub Issue、数据表或聊天消息里。** 我们的静态网页没有密钥输入框。Python 绘图脚本在本地运行，也不单独向模型 API 发请求；你给 Agent 的文件仍受所选软件自身的数据处理规则约束。

## 第 2 步：安装技能

下载并解压 [完整技能安装包](https://dazi.gsarrizabalaga.xyz/downloads/BatteryReviewForge-v0.9.1.zip)。看到 `skills/`、`install.ps1` 和 `install.sh` 三项后，再按自己的软件做以下一步。

### Codex：先确认目录与已有安装

上手页提供固定指向 `https://github.com/arrizabalagags-png/BatteryReviewForge` 的自然语言安装请求。必须先核对当前宿主版本、插件和同名技能，再安装。它目前是待原生客户端完整验证的辅助路线，不能写成已独立通过三次。

已会用终端：

```text
codex plugin marketplace add arrizabalagags-png/BatteryReviewForge
codex plugin add battery-review-forge@battery-review-forge
```

下载 ZIP 的 Windows 用户：在解压目录打开 PowerShell，运行 `./install.ps1`。macOS/Linux 用户运行 `sh install.sh`。当前安装器保留 `$CODEX_HOME/skills` 或 `~/.codex/skills` 默认值，同时检查共享 `~/.agents/skills` 中的同名副本。当前宿主若扫描其他目录，先查明再显式指定目标，不可把历史路径当作永久保证。重复安装会停止。主动使用覆盖参数时先移动旧目录到 `.brf-install-backups`，再放入完整新版；不会合并遗留文件。恢复步骤见[更新与恢复](https://dazi.gsarrizabalaga.xyz/maintenance.html)。

### Kimi Code CLI：复制到 Kimi 的技能目录

在解压目录运行：Windows `./install.ps1 -Agent KimiCode`；macOS/Linux `sh install.sh --agent kimi`。默认目标为 `~/.kimi-code/skills/`。开始一个新会话，然后输入 `/skill:battery-review-figure` 试用绘图技能。官方还支持共享的 `~/.agents/skills/`，但本安装器选择专用目录，减少与其他 Agent 的同名技能冲突。[官方技能文档](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html)。

### DeepSeek Harness：复制到 DSH 的技能目录

在解压目录运行：Windows `./install.ps1 -Agent DeepSeekHarness`；macOS/Linux `sh install.sh --agent dsh`。默认目标为 `~/.dsh/skills/`；如果设置了 `DSH_HOME`，安装器会跟随它，Windows 也可另用 `-TargetRoot` 指定完整目标目录。随后在新会话查看技能目录。DSH 需要已启用技能注册、文件系统提供方及调用工具；默认组合可在[官方文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/README.md)核查。复制成功只证明文件到位，不证明图能在本机导出。

### WorkBuddy：按技能逐个导入

下载 [WorkBuddy 绘图与拼图套装](https://dazi.gsarrizabalaga.xyz/downloads/BatteryReviewForge-WorkBuddy-Starter-v0.9.1.zip)，先解压，按 `先读我.txt` 分别导入绘图与拼图 ZIP。套装保留共享规则；包内字段与引用通过自动检查，但不能由此推断宿主已正确扫描依赖。按[官方技能入口](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)操作后，新开任务检查实际路径、Python 依赖，再生成 PNG/SVG。15 技能合集仍供完整综述流程使用，不要求初学者逐个挑选。

### 豆包：先不要照搬其他软件的目录

先用豆包自带的文件处理功能，把一份数据或一张样图交给它，并附上本仓库对应技能的公开 `SKILL.md` 链接，请它按说明给出**绘图方案**。这只是手动参考说明，**不是技能已安装或脚本会执行**。待官方公开第三方导入规范且我们实际跑通后，才会补一键安装教程。

## 第 3 步：用一句话开始

```text
我有一份全电池循环数据。请先用 battery-review-figure 检查列名、单位、
测试条件和可比性；告诉我还缺什么，再画一张投稿尺寸能看清的图。
```

```text
我有 6 张已经画好的图。请用 battery-figure-assemble 先盘点来源，
按同一字号和边界拼成 Fig. 3，导出 PDF 并给我逐面板检查图。
```

绘图需要 Python、Matplotlib 等依赖；[绘图依赖](../skills/battery-review-figure/requirements.txt)和[拼图依赖](../skills/battery-figure-assemble/requirements.txt)可分别按需安装。若宿主没有本地 Python 执行权，技能仍可帮你规划、审查和写出脚本，但不能声称它已经产生了成图。示例数据是虚构的，不可写入论文。

## 关于其他 Agent

Claude Code 未列为当前维护的安装入口，也未在本项目做兼容验证。我们只报告自己能核实和测试的产品行为，不把对公司的态度写成技术结论。提出新宿主适配时，请给出官方技能规范、实际导入截图、最小样例和一次完整绘图/拼图结果。

## v0.9.1 显示名称

客户端支持展示配置时，绘图显示为「VoltPeer · 科研绘图」，拼图显示为「VoltPeer · Figure 拼版」。技术 ID 不变。WorkBuddy、Kimi 等客户端可能仍显示 `battery-review-figure`；请用这个技术名称查找，不要以是否显示中文判断安装成功。完整映射见 [SKILL_NAMES.json](SKILL_NAMES.json)。v0.8.7 的历史验证范围保持原样；v0.9.1 的原生客户端完整出图验收仍待完成。
