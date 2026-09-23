# 20 个公开科研技能的学习记录

核对日期：2026-09-23。逐一阅读了下列公开仓库的 `SKILL.md` 入口，比较了**第一次怎么开始、材料不完整时怎么做、结果如何核查**。这里只记录我们自己归纳的设计决定；没有复制第三方代码、提示词或图形资源。链接用于让维护者核对原文，不代表本项目支持这些技能或沿用其许可证。

| # | 阅读的技能 | 对 BatteryReviewForge 有用的做法 |
| --- | --- | --- |
| 1 | [Literature Review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/literature-review/SKILL.md) | 检索、筛选、写作分步记录；把“搜到”与“能支持论点”分开。 |
| 2 | [Paper Lookup](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/paper-lookup/SKILL.md) | 文献接口返回成功，也要检查返回的是不是目标论文。 |
| 3 | [Citation Management](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/citation-management/SKILL.md) | 引文元数据按 DOI、作者、年份等逐项复核。 |
| 4 | [Peer Review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/peer-review/SKILL.md) | 审稿意见标出所依据的稿件位置与可见证据。 |
| 5 | [Scientific Writing](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-writing/SKILL.md) | 写作时保留证据来源与作者承担的判断。 |
| 6 | [Scientific Visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md) | 先定图的读者和用途，再选表达方式；按最终尺寸检查。 |
| 7 | [Scientific Schematics](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-schematics/SKILL.md) | 示意图需要可读性复核，自动生成的第一版不算验收。 |
| 8 | [Matplotlib](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/matplotlib/SKILL.md) | 把重复画图参数放入可复用脚本和样式，而非让每位作者重新调。 |
| 9 | [Exploratory Data Analysis](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/exploratory-data-analysis/SKILL.md) | 读表前先确认文件与字段；缺失值不能被漂亮的线条掩盖。 |
| 10 | [Scientific Critical Thinking](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-critical-thinking/SKILL.md) | 明确区分观察、解释和还需要检验的假说。 |
| 11 | [Research Lookup](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/research-lookup/SKILL.md) | 检索结果先形成可复查的证据包，再进入写作。 |
| 12 | [Database Lookup](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/database-lookup/SKILL.md) | 选与问题相符的权威数据库，保存查询和筛选条件。 |
| 13 | [Intake Project](https://github.com/aperivue/medical-research-skills/blob/main/skills/intake-project/SKILL.md) | 先看用户已有的稿件、表格和文件夹，再决定下一步。 |
| 14 | [Lit Sync](https://github.com/aperivue/medical-research-skills/blob/main/skills/lit-sync/SKILL.md) | 尊重作者现有的文献目录与命名，不擅自另建一套。 |
| 15 | [Make Figures](https://github.com/aperivue/medical-research-skills/blob/main/skills/make-figures/SKILL.md) | 图件有面板级核查与导出检查；领域图型应有专门入口。 |
| 16 | [Write Paper](https://github.com/aperivue/medical-research-skills/blob/main/skills/write-paper/SKILL.md) | 长任务可拆阶段，完成一段后能交付可继续编辑的成果。 |
| 17 | [Check Reporting](https://github.com/aperivue/medical-research-skills/blob/main/skills/check-reporting/SKILL.md) | 检查项要对应稿件位置，并标明已有、部分或缺失。 |
| 18 | [Science Research Writing](https://github.com/Yila-AI/sci-ssci-skills/blob/main/skills/science-research-writing/SKILL.md) | 先读文件、做能做的部分；仅在关键判断无法继续时问一个具体问题。 |
| 19 | [SCI/SSCI Polishing](https://github.com/Yila-AI/sci-ssci-skills/blob/main/skills/sci-ssci-polishing/SKILL.md) | 润色前列出必须保留的数字、术语、引文与论断强度。 |
| 20 | [Write Literature Review](https://github.com/Zsun79/LitReviewSkill/blob/main/skills/write-literature-review/SKILL.md) | 保存检索与纳入过程，让综述范围可回查。 |

## 我们实际采用的改动

1. **网站先说人话。** 先让用户选自己用的软件，每种软件只显示三步；命令放在说明之后。第一次提问无需记住技能名称。
2. **技能先看材料。** 读完用户已给的论文、数据和图片后，才问会影响判断的缺项。原始数据画图、现成图片拼版、整篇综述分别走不同入口，但由助手内部选择。
3. **给出当前能做的结果。** 文件不全时，先完成可核实的工作，简短列出还缺什么；别把普通用户送进长长的前置问卷。
4. **验证状态写清楚。** “官方有导入格式”“文件复制成功”“在客户端跑通完整任务”是三个不同结论。网站和安装文档逐项区分。
5. **可复查再交付。** 图保留数据、代码、SVG/PDF 和来源；综述保留引文核验状态；不能把演示数据或未读全文写成已证实。

## 没有照搬的做法

医疗领域的患者数据、临床报告清单和期刊政策不能直接变成电池研究规则。部分技能要求每个环节先停下来征求确认，会阻断用户已明确授权的工作；我们只在缺少会改变科学结论的信息时问。固定数量的数据库、强制生成一整套文件、按文件后缀猜电芯构型，也不适合作为所有电池任务的默认规则。
