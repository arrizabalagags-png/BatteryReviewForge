# 仓库说明更新 — 2026-10-03

## 修改范围

- 重写中英文 README：绘图、Figure 拼版、数据整理作为主线；默认展开一张原有结构光谱预览，EIS 和机理示意在补充区。
- 安装入口保留 DeepSeek Harness 桌面路线与三个步骤，分别检查模型连接、实际技能读取和文件生成。加入首次演示请求及换数据请求。
- 合并重复任务表为七行“任务 / 输入 / 交付”；保留全部 16 个技术 ID、写作润色和其他科研流程。
- 修正 GETTING_STARTED、COMPATIBILITY 的活动入口：0.12.0 Beta，绘图 Starter 一个 Skill，全部技能包 16 个。
- 扩充本版说明并更新活动状态文件；CITATION.cff 描述 2026-10-03 已公开的 0.12.0 Beta 源码。GitHub 完整正式 Release 仍是 v0.9.2。
- 默认展开的中文说明为 1,430 个汉字；保留费用、运行环境、隐私、作者核对和第三方许可边界。
- 根据用户补充，中英文 README 与适配说明明确说明网站隐藏 Codex 入口的情况，并保留 Codex / DeepSeek Harness 两条安装方式；不把路径适配表述成全部客户端已经实测通过。

## 实际检查

- 已确认当前公开仓库为 arrizabalagags-png/Voltpeer-skills；没有覆盖根目录 README 的 .github/README。
- 当前源码中含 SKILL.md 的技能目录为 16 个。
- 推荐 Starter 从 GitHub 下载核对为 ZIP：743,774 bytes；清单版本 0.12.0，一个 voltpeer-plot；SHA-256 与索引及本地一致，ZIP CRC 无错误。
- 全部技能包从 GitHub 下载核对为 ZIP：1,205,664 bytes；清单版本 0.12.0，16 个 Skill；SHA-256 与索引及本地一致，ZIP CRC 无错误。
- 两个包的 SHA-256 见[版本说明](../RELEASE_v0.12.0.md)。本轮未改写 ZIP 和冻结下载索引。
- 实际读取 Starter 的 AGENT_GUIDE、要求文件、Demo 清单与输出实现，确认 demo-result/index.html、results/、默认 PNG/SVG/PDF 和同名目录版本保留规则。此项为内容检查，没有再次安装客户端或执行模型任务。
- 中文、英文和配套活动指南共 291 个相对文件及锚点检查通过，包含网站工程的对应说明。
- 5 份公开 Markdown 通过 GitHub Markdown API 渲染。中英文 × 深浅色 × 1280/390 像素共 8 组本地 Markdown 预览检查通过：图片加载、单张主预览、七行任务表、正文 16px、无整页横向溢出、安装锚点及折叠区操作。
- 本地预览使用 GitHub Markdown 渲染与 GitHub 风格 CSS，不冒充 GitHub 页面实机截图。未进行全部文档或全站视觉审计。

## 状态边界

下载索引中的 LOCAL_CANDIDATE_NOT_PUSHED_NOT_DEPLOYED 保留其构建快照身份。当前 Beta 包已在仓库公开，以本版说明和活动 RELEASE_STATUS 为准；此前带日期的测试仍覆盖其原版本。

当前版本的全量 Flash/Pro 行为验证、原生客户端从发现到交付仍未完成。本轮没有付费测试、客户端安装、核心 Skill 修改、科学数据修改或 ECS 部署。

没有改名、移动标签、覆盖历史资产或创建 Release。About、Website 和 Topics 本轮只提供建议值，没有修改远端设置。

## 远端设置建议

- About：面向电池科研的开源 AI Skill 工具箱：数据整理、可复现绘图与 Figure 拼版，兼顾机理示意、论文写作和润色。附样图、示例数据与源码。搭配 DeepSeek Harness 等 AI 助手使用。Beta。
- Website：https://dazi.gsarrizabalaga.xyz/
- Topics：agent-skills、battery-research、electrochemistry、scientific-visualization、figure-assembly、scientific-writing、deepseek-harness。

维护者与机构信息来自 AUTHORS.md、CITATION.cff 和现有许可；保留郭硕、姜金龙及上海理工大学能源材料科学研究院署名，不声明机构背书。
