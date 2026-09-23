# 我用哪个 Agent？怎么装？

先选自己**已经在用**的软件。BatteryReviewForge 是一组 `SKILL.md` 指令、Python 脚本和原创图形资源；它本身没有网站账号、模型 API，也不会收取密钥。下面的“兼容”分为**官方格式存在**和**本项目实机跑过**，两者不能混为一谈。核对日期：2026-09-23。

| 软件 | 现在能做什么 | 本项目验证状态 |
| --- | --- | --- |
| **Codex** | 装完整插件，或复制 13 个独立技能 | **本机已验证** |
| **Kimi Code CLI** | 把 13 个技能复制到官方扫描目录 | 官方技能格式与路径已确认；本项目完整任务待实机验收 |
| **DeepSeek Harness** | 把 13 个技能复制到官方扫描目录 | 官方本地技能机制已确认；本项目完整任务待实机验收 |
| **WorkBuddy** | 在技能界面上传针对 WorkBuddy 制作的单个技能 ZIP | 官方导入入口与格式已确认；本项目客户端导入待实机验收 |
| **豆包桌面工作任务** | 可先用内置 Skills 和普通文件问答 | 尚无已核实的第三方 `SKILL.md` 导入步骤；目前不声称可一键安装 |

## 第 1 步：先登录你自己的 Agent

**Codex**：在 Codex 应用或 CLI 按提示登录。使用本项目绘图时，不需要另买或填写“BatteryReviewForge API Key”。[官方插件说明](https://developers.openai.com/plugins/build/plugins)。

**Kimi Code CLI**：首次运行 `kimi` 后输入 `/login`，按屏幕提示选 **Kimi Code 账号登录** 或 **Kimi Platform API Key**。前者不需要手动管理 Key。[官方入门说明](https://www.kimi.com/code/docs/en/kimi-code-cli/guides/getting-started)。

**DeepSeek Harness**：在软件的 **Settings → Models** 中配置 DeepSeek 或你自己使用的模型提供方。只在该软件自己的设置页输入 Key。[官方模型设置说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/providers.md)。

**WorkBuddy**：先安装并登录 WorkBuddy。日常使用以它的账号和额度为准；只有你主动接入其他模型提供方时，才按该提供方的官方说明在 WorkBuddy 设置模型 Key。[WorkBuddy 技能说明](https://free-plat-test.qcloudcdn.com/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[腾讯 TokenHub 接入示例](https://cloud.tencent.com/document/product/1823/131902)。

**豆包**：使用豆包官方账号与客户端。桌面版支持“工作任务”和内置 Skills，但目前没有核实到可供本项目采用的第三方技能包导入规范。[官方下载页](https://www.doubao.com/download/desktop)。

> **任何情况都不要把 API Key 粘到这个网站、GitHub Issue、数据表或聊天消息里。** 我们的静态网页没有密钥输入框。Python 绘图脚本在本地运行，也不单独向模型 API 发请求；你给 Agent 的文件仍受所选软件自身的数据处理规则约束。

## 第 2 步：安装技能

下载并解压 [完整源码与安装包](https://github.com/arrizabalagags-png/BatteryReviewForge/releases/download/v0.5.1/BatteryReviewForge-v0.5.1.zip)。看到 `skills/`、`install.ps1` 和 `install.sh` 三项后，再按自己的软件做以下一步。

### Codex：最省事

已会用终端：

```text
codex plugin marketplace add arrizabalagags-png/BatteryReviewForge
codex plugin add battery-review-forge@battery-review-forge
```

下载 ZIP 的 Windows 用户：在解压目录打开 PowerShell，运行 `./install.ps1`。macOS/Linux 用户运行 `sh install.sh`。它们默认安装到 Codex 的用户技能目录。同名技能已存在时会停下，避免不知情覆盖。

### Kimi Code CLI：复制到 Kimi 的技能目录

在解压目录运行：Windows `./install.ps1 -Agent KimiCode`；macOS/Linux `sh install.sh --agent kimi`。默认目标为 `~/.kimi-code/skills/`。开始一个新会话，然后输入 `/skill:battery-review-figure` 试用绘图技能。官方还支持共享的 `~/.agents/skills/`，但本安装器选择专用目录，减少与其他 Agent 的同名技能冲突。[官方技能文档](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html)。

### DeepSeek Harness：复制到 DSH 的技能目录

在解压目录运行：Windows `./install.ps1 -Agent DeepSeekHarness`；macOS/Linux `sh install.sh --agent dsh`。默认目标为 `~/.dsh/skills/`；如果设置了 `DSH_HOME`，安装器会跟随它，Windows 也可另用 `-TargetRoot` 指定完整目标目录。随后在新会话查看技能目录。DSH 需要已启用技能注册、文件系统提供方及调用工具；默认组合可在[官方文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/README.md)核查。复制成功只证明文件到位，不证明图能在本机导出。

### WorkBuddy：按技能逐个导入

下载 [WorkBuddy 技能包合集](https://github.com/arrizabalagags-png/BatteryReviewForge/releases/download/v0.5.1/BatteryReviewForge-WorkBuddy-v0.5.1.zip)，**先解压合集**。里面有 13 个独立 ZIP，每个 ZIP 对应一个技能：已有图片拼版选 `battery-figure-assemble`，上传数据画图选 `battery-review-figure`。在 WorkBuddy **技能 → 添加技能 → 上传技能** 中选所需的单个 ZIP。不要直接上传“合集 ZIP”或 Codex 的“完整源码 ZIP”。如果任务跨多个阶段，可继续安装相关技能；总协调技能引用其他技能时要确保它们也已导入。WorkBuddy 的开放平台要求 `description_zh`、`description_en`、版本与作者，专用 ZIP 会补齐这些字段。[官方导入说明](https://free-plat-test.qcloudcdn.com/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[包结构](https://open.workbuddy.cn/en/docs/skill)。

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
