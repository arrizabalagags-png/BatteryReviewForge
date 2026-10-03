# 软件适配与实际验证状态

当前活动工程是 **VoltPeer 0.12.0 Beta，共 16 个 `voltpeer-*` Skill**。绘图 Starter 只包含一个绘图技能，路径为 `assets/cycling-rule-v1.2.1/starter/`；全部技能包与单 Skill 包位于 `downloads/v0.12.0-cycling-rule-v1.2.1/`。这些 Beta 包已在仓库公开，完整正式 Release 仍为 v0.9.2。[当前版本与包范围](RELEASE_v0.12.0.md) · [校验索引](downloads/v0.12.0-cycling-rule-v1.2.1/download-index.json) · [安全迁移](NAMING_MIGRATION.md)。

默认路线是 **DeepSeek Harness 官方桌面端 + 项目工作区技能**，这条推荐路线尚未完成当前版本的原生桌面全程实测。当前 0.12.0 的 ZIP 结构与本地程序记录见[交付证据](validation/2026-10-03-cycling-delivery.json)；完整 69 项行为 EVAL 和原生桌面发现到结果链路仍待实跑。以下 0.10.1 与带日期的安装、API、环境及科学记录保留原版本范围，不能作为当前版本已通过的证明。此前有限 Flash/Pro 直连 API pilot 保留为历史 PARTIAL_API_PILOT，[去敏结果和用量](validation/2026-10-01-api-pilot.json)。活动入口核对于 2026-10-03。

## 0.10.1 固定绘图 Starter 实测

冻结 ZIP：580,632 bytes，SHA-256 `392b58b6a211c35f88a0148c95d07b9accb5b6eeb000640883466d96d3ab466a`。普通上传优先 inspect → 作者确认映射 → 固定 plot → check；不先加载整套论文策划文档。

| 实测入口 | 已完成 | 边界 |
| --- | --- | --- |
| DeepSeek Flash 直连 API + 受限文件/固定程序工具 | 独立识别非标准列名、建立作者映射，13请求/15工具后导出 PNG/SVG/PDF；48值、异常、所选配色、实线无点四框和输出完整性通过 | 最终回复为反引号相对路径，缺可点击链接：交付表达 PARTIAL。不是原生 DSH 测试；模型没有视觉工具 |
| Codex `gpt-6-luna` collaboration agent | 新包实际安装文件、inspect、重新映射、固定出图、check、打开 PNG；48值和格式独立评分通过。另一个只有CSV的工程缺项停止、未猜条件或出图 | 依赖使用之前已安装的相同隔离 Python 环境；原生客户端发现不在本次证据内；仅测试这个 CE 任务 |
| Codex CLI 0.146.0 / ChatGPT 登录 / `gpt-6-luna` | 实际调用返回 HTTP 400 model not supported | 此 CLI/账户入口 MODEL_UNAVAILABLE，未运行模型任务；不能用另一入口成功掩盖此失败 |

[Flash 独立评分与用量](validation/2026-10-01-flash-starter-route-fix.json) · [Luna 新包评分](validation/2026-10-01-luna-starter-agent-route-fix.json) · [Luna 首轮历史评分](validation/2026-10-01-luna-starter-agent.json)。测试表是工程作者声明的合成验收数据，不代表真实实验；100.5%异常原值保留。以上有限试次不替代全部图型的模型验证或原生宿主验收。

## DeepSeek Harness 桌面端主线

第一次画图可下载 [v0.12.0 Beta 绘图 Starter](assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip)，解压后让 AI 读包内 `AGENT_GUIDE.md`。其中 `start.py setup` 仅准备隔离的 Python 环境和依赖，不需要 API key；一个固定 `batteryplot` 实现覆盖普通上传的 10 种图型。AI 负责识别图型、确认字段/科学条件和调用程序，不为每份数据重写绘图代码。Demo 与作者输入分开，其他任务按下面路线装所需 Skill。旧 v0.10.1 Starter 保留在上面的冻结记录中。

Starter 的 Codex 适配为项目 `.agents/skills`，DSH 为项目 `.dsh/skills`；共用标准 name/description frontmatter。路径适配和本地执行已测试，原生发现/真实模型表现仍分别记录。[Codex 官方本地目录](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

1. 从 [DeepSeek 官方下载页](https://www.deepseek.com/harness/)下载当前系统支持的桌面版，按官方安装步骤打开。
2. 在设置中的 **DeepSeek 模型供应商** 保存自己在 DeepSeek 平台创建的 API key，具体入口按官方当前界面操作。模型费用以 [官方当前价格表](https://api-docs.deepseek.com/quick_start/pricing/)为准；本站和 Skill 不收取或提供模型 API key。无需把 key 发给作者或 AI。[官方快速开始](https://deepseek-harness.github.io/deepseek-harness/guide/quickstart)。
3. 在桌面端选一个研究项目文件夹作为工作区。完整技能包解压后，在包目录打开终端，运行下面与系统对应的命令。

Windows：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Workspace "D:\我的科研项目"
```

macOS（或 Linux CLI 的项目技能目录）：

```sh
sh install.sh --workspace "/path/to/research project"
```

工作区须已存在。目标为 `<工作区>/.dsh/skills/<技术ID>/SKILL.md`，这是官方项目文件系统 provider 的高优先级路径；有 `.git` 时项目根取最近祖先。打开项目根，避免选择里面另一个嵌套目录。[官方技能发现说明](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/skills)。CLI 与桌面 profile 不能混同，不能仅复制到猜测的 userData/global 目录便写“桌面已安装”。

4. 在该工作区新开会话，请它定位实际装入的技能，读取其实际 SKILL.md。单个技能不要求同时装绘图和拼版。安装脚本输出只证明 copied；宿主实际定位才是 discovered。
5. 绘图/拼版脚本在项目虚拟环境中安装该技能自己根目录的 `requirements.txt`，再跑合成样例；只用文字流程不要求安装绘图库。不要给系统 Python 装全局包。Windows 本次QA使用隔离 Python 3.12，脚本要求 Python ≥3.10；目录可含中文/空格，JSON BOM 可读。
6. 用一份真实授权数据试样，核对结果里的单位、分母、边界和最终尺寸，再批量。缺关键字段时补材料，不要求新手读内部日志。

更新：Windows 加 `-Overwrite`，shell 加 `--overwrite`。安装器先移动同名旧树到相邻 `.brf-install-backups`，再完整复制新树；保留作者修改，不合并旧遗留文件。没有覆盖参数时遇同名停止。恢复先把旧目录复制回原目标或指定独立测试工作区，核查实际被宿主发现的路径。

高级显式目标：Windows `-TargetRoot "实际扫描的skills目录"`；shell `--target-root "实际扫描的skills目录"`。与 workspace 参数互斥。其他宿主须先查自身官方路径和当前设置，避免同名多副本。

## Flash 与 Pro 的条件能力

| 模型/模式 | 适合的工作 | 不能省略的检查 | 此包真实模型状态 |
| --- | --- | --- | --- |
| `deepseek-flash` / Guided | 先一份数据、一张试样；可在宿主提供视觉时检查图片 | 来源/单位/实验条件、实际脚本输出、视觉逐图复核 | 原65项加4项相反证据，共69项；模型实跑 NOT_RUN |
| `deepseek-v4-pro` / Adaptive | 较复杂文字、证据核对和分阶段结构规划 | 同样的科学审查；当前 Pro 无视觉，PNG/显微图/最终Figure视觉待审 | 原65项加4项相反证据，共69项；模型实跑 NOT_RUN |

当前 Flash 对应 V4.1 Flash 并有原生 Vision；仍服务的 V4 Pro 0813 不支持 Vision。[官方模型表](https://api-docs.deepseek.com/quick_start/pricing/)。能力会变化；每次真实验证记录精确 model ID、客户端版本和工具，不用价格或名称代替测量。无工具执行时可写脚本/方案，不能宣称已经导出。无视觉时可核对文字/几何指标，不能宣称看过图。

## 五项状态分别记录

| 状态 | 什么证据能证明 | 当前证据边界 |
| --- | --- | --- |
| copied | 包中技能文件和实际目标目录 | 本次临时安装/更新、冲突备份、中文路径已测试 |
| discovered | 原生客户端新会话读取实际技术 ID 的路径 | 本次桌面原生发现待实测 |
| runtime_ready | 所需包实际 import 成功及工具执行权 | 本地项目QA环境已检查；使用者机器必须自己检查 |
| smoke_test_passed | 实际导出、文件解析与打开，非按钮点击 | 本次Python本地绘图/拼版路线及失效边界回归测试 |
| behavior_eval | 完整case请求、模型输出/调用、产物与独立评分证据 | 有限直连API pilot PARTIAL；完整69项和原生宿主 NOT_RUN；不以单元测试冒充 |

诊断命令：`python scripts/diagnose_install.py --skills-root "实际目标目录" --host "DeepSeek Harness desktop"`。目标可为安装集合，也可直接指向一个含 SKILL.md 的技能目录。诊断逐技能读取本包 requirements，检查已装版本和实际 import；无第三方依赖记 NOT_REQUIRED。显式 `--smoke-output "新目录"` 只实跑已实现的绘图 PDF/PNG/SVG 或拼版 PDF/PNG 路线，其他流程记 NOT_SUPPORTED，不创建假的产物或发现通过状态。默认隐藏个人路径；完整技术诊断由维护者按需查看。**SVG面板输入拼版**还需要原生 Cairo；import 可用不等于所有 SVG 已渲染通过。缺少时用原编辑器导出的矢量 PDF。

## 结果与恢复

绘图 `scripts/deliver.py`，拼版 `scripts/compose_figure.py deliver` 均生成私有 Working 文件夹：根 `index.html`/`README.md`，图件 `results/`，输入/规格/审查/checkpoint `.voltpeer/`。重复目标生成 `_v002`，旧结果保留。内部记录按需展开，科学未决项必须说明。TIFF默认LZW；位图每格式/内容类DPI明确记录；中性300 dpi预览不会标为所有期刊合规。

要公开图件，先确认公开权利和许可，再生成 Share 包。它排除原始数据/恢复状态/内部路径和日志，清理元数据；最后人工检查可见姓名、课题与未公开内容，并保留必须科学标签和来源署名。真实 Key、用户研究材料、账号和全量私人对话不放到公共仓库。

## 其他已有软件

**Codex 与 DeepSeek Harness（DSH）均有适配入口。** 网站目前因部分原因隐藏了 Codex 入口；仓库中的 Codex 安装方式继续保留，已有 Codex 可继续使用。绘图 Starter 使用同一个 Skill 和固定程序：DSH 安装到项目 `.dsh/skills`，Codex 安装到项目 `.agents/skills`。这说明安装路径与工具适配保留；当前版本各客户端的原生发现和完整模型行为验证仍按本页实际记录判断。

For Codex users: the website currently hides the Codex entry, while the repository retains both Codex and DSH installation routes. Use the same plotting Starter with `--host codex` for Codex or `--host dsh` for DeepSeek Harness. Current native-client and model validation limits still apply.

| 软件 | 安装入口 | 当前边界 |
| --- | --- | --- |
| Codex | 明确 `-Agent Codex` / `--agent codex`，或使用官方插件入口 | 保留历史支持；新版包不能仅凭旧记录标原生验收PASS |
| Kimi Code CLI | `-Agent KimiCode` / `--agent kimi` | 既有目录/包路线保留；当前完整任务待本机测 |
| WorkBuddy | 可选单技能ZIP/两技能套装 | 包内指南已自包含；第三方原生导入发现待实测，非主推 |
| 其他桌面端 | 按已核实官方技能接口 | 不照搬目录、不杜撰一键安装；无官方可验证接口时只提供手动参考 |

兼容测试协议见 [EVAL说明](../evals/README.md)。打包前用 `scripts/check_skill_distribution.py` 检查完整安装树和每个独立ZIP解压目录；必须能在单技能目录解析所有本地运行引用。引用检查也不证明客户端能力。

维护者再运行 `python scripts/check_skill_dependencies.py --skills-root skills`，用 AST 检查每个技能所附 Python 源码的 import 是否在本技能 requirements 声明。检查不读取全局已装包来弥补漏项，懒加载和可选 SVG 导入仍记录；动态名称无法静态解析时保留 NOT_TESTED。此门禁只核对 Python 导入与声明，不验证宿主插件、真实模型或科学结论。


## 旧安装迁移

当前使用 16 个 `voltpeer-*` 技术 ID，新增 `voltpeer-mechanism`。更新旧安装前遵循[迁移说明](NAMING_MIGRATION.md)；普通安装拒绝旧名重复，显式更新保留旧目录和自定义内容。0.11.0 的 15 项历史迁移表、旧版验证和下载继续保留原身份。
