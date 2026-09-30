# 软件适配与实际验证状态

默认路线是 **DeepSeek Harness 官方桌面端 + 项目工作区技能**。技术 ID 保持 `battery-review-figure`、`battery-figure-assemble` 等；显示名支持情况不能替代技能发现检查。文档核对于 2026-10-01；本次为 **Beta**。有限Flash/Pro直连API pilot已实际执行，独立评分为PARTIAL_API_PILOT；完整69项固定行为EVAL及原生桌面发现到结果链路仍待实跑。[去敏结果和用量](validation/2026-10-01-api-pilot.json)。

## DeepSeek Harness 桌面端主线

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

| 软件 | 安装入口 | 当前边界 |
| --- | --- | --- |
| Codex | 明确 `-Agent Codex` / `--agent codex`，或使用官方插件入口 | 保留历史支持；新版包不能仅凭旧记录标原生验收PASS |
| Kimi Code CLI | `-Agent KimiCode` / `--agent kimi` | 既有目录/包路线保留；当前完整任务待本机测 |
| WorkBuddy | 可选单技能ZIP/两技能套装 | 包内指南已自包含；第三方原生导入发现待实测，非主推 |
| 其他桌面端 | 按已核实官方技能接口 | 不照搬目录、不杜撰一键安装；无官方可验证接口时只提供手动参考 |

兼容测试协议见 [EVAL说明](../evals/README.md)。打包前用 `scripts/check_skill_distribution.py` 检查完整安装树和每个独立ZIP解压目录；必须能在单技能目录解析所有本地运行引用。引用检查也不证明客户端能力。

维护者再运行 `python scripts/check_skill_dependencies.py --skills-root skills`，用 AST 检查每个技能所附 Python 源码的 import 是否在本技能 requirements 声明。检查不读取全局已装包来弥补漏项，懒加载和可选 SVG 导入仍记录；动态名称无法静态解析时保留 NOT_TESTED。此门禁只核对 Python 导入与声明，不验证宿主插件、真实模型或科学结论。
