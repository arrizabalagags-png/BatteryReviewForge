# BatteryReviewForge 时间测试方案

当前只有测试方案，**没有参与者成绩**。网站不会写节省时间的百分比或虚构“科研人员画图时间占比”。机器可重跑的方案见 [`BRF_TIME_BENCHMARK.json`](BRF_TIME_BENCHMARK.json)。

## 固定任务

1. 全电池：同一组循环与电压曲线 CSV，输出 SVG、PDF、输入与设置记录。
2. Li‖Cu 逐圈 CE：同一组 CE 与电压曲线 CSV，确认协议和条件。
3. 六面板拼版：同一组源图，输出 PDF 和对齐检查。
4. 十面板拼版：同一组源图，输出 PDF 和对齐检查。

每项任务预先固定输入、目标图、错误标准和终点；记录软件版本与操作者经验。分别比较普通 GUI 手工流程、熟练 Origin 模板或批处理流程，以及 BatteryReviewForge。Origin 可使用它已有的模板、批处理、Python 等能力，不能故意限制熟练用户。任务顺序应在参与者间平衡。

## 记录

- `active_human_seconds`：人主动操作、判断与检查的时间；中断与非任务休息停表。
- `machine_unattended_seconds`：任务正在运行而人可以离开的时间。
- `elapsed_seconds`：从开始到达到终点的实际时间；三项时间的关系要按重叠段标记，不能简单相加。
- `manual_action_count`、`revision_count`、`qa_failure_count`：按事先公布的定义计数。
- `reproducibility_outputs`：原始输入、设置或脚本、可编辑 SVG/PDF、数据说明是否保留。

至少招募 5 位新手和 5 位有 Origin 经验的用户。报告各组各任务的中位数、四分位范围、失败率和所有返工；不要只展示最快一次。记录与方案分开保存，先征得参与者同意，再公开匿名汇总。

脚本化可复现的依据来自 [*Good enough practices in scientific computing*](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510)。这篇文章不提供电池科研人员排图时间占比；项目自己的效率结论只能来自上述实测。
