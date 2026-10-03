# 宿主与模型适配（按需读取）

默认推荐 DeepSeek Harness 官方桌面端。在官方下载安装并配置模型 Key 后，打开研究工作区，将技能安装到 `.dsh/skills/<技术ID>/SKILL.md`。用新会话检查实际发现路径。CLI的全局DSH_HOME/profile不能作为桌面userData路径保证。有.git时从项目根发现技能。[官方快速开始](https://deepseek-harness.github.io/deepseek-harness/guide/quickstart)；[官方技能发现](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/skills)。

Flash使用短阶段、一个试样、checkpoint和实际核对；Pro可规划较大文字/证据批次。两者科学要求不变。2026-09-30官方表：deepseek-flash有原生视觉（仍取决于宿主图片工具），deepseek-v4-pro无视觉；Pro文字/几何审查不能算看过最终图。[官方模型表](https://api-docs.deepseek.com/quick_start/pricing/)。实际工具和试样表现决定模式，不按名称猜强弱。保留用户既有模型与预算选择。

客户端复制、技能发现、Python依赖、真实导出与固定模型行为EVAL分别记录。目前新适配为Beta，真实Flash/Pro和原生桌面全链路EVAL未实跑；不得写“已全部通过”。用户只看实际结果和必要科学问题；日志/哈希/审查记录保存到私有项目的.voltpeer，恢复前核对哈希。更多执行和恢复规则见[共用契约](EXECUTION.md)。

Codex/Kimi/WorkBuddy既有辅助路线保留，但没有本机原生证据不声明新版已通过。没有技能导入/运行权的客户端可以参考指令和产物方案，不能声称脚本已运行。不要把用户API Key发进聊天或公共仓库。
