# 首页样图准入：教程图不能自动变成展示图

任何图先标 `test`、`tutorial`、`validated` 或 `showcase`。`showcase` 只表示本项目已把来源、科学表达、最终尺寸和人工视觉审核完成；它仍不是对实验结论的担保。默认的合成图是 `test`，只可放在明确写着“虚构教程”的区域。当前旧版 CE、全电池、EIS、条件矩阵与六面板综合图都保持 `test`；不要因更新配色或网页排版就升级。

## 五道关

1. **实验语法**：图型在 [BATTERY_FIGURE_GRAMMAR.json](BATTERY_FIGURE_GRAMMAR.json) 中有准确的数据合同。辅助 panel 的选择有科学问题和同源数据；默认搭配有 [PANEL_EVIDENCE.json](PANEL_EVIDENCE.json) 的至少三个独立 DOI/图号/panel 支持。逐圈 CE 与 Aurbach 分开；保持率有参考圈；EIS 的 fit 有电路、参数和实测点。
2. **来源与诚实表达**：首选可合法复用的公开 source data 并给引用。合成数据必须近图标清、公开生成脚本和数据，不能看起来像测得的 Raman、RDF、显微图、ToF-SIMS 或同一实验机制链。图内不得抹掉失败、异常、>100% CE 或关键条件。
3. **投稿尺寸**：按 [JOURNAL_FIGURE_SPEC.json](JOURNAL_FIGURE_SPEC.json) 设置最终 mm；检查轴字、panel 字母、色彩、比例尺、真实绘图区、裁边和缩小后的可读性。导出 SVG/PDF，检查 PDF 实际嵌入字体；指定 Arial 却出现 DejaVu 替换时报告失败或明确解释额外字形。
4. **版式**：一个 Figure 有一个问题和清楚的阅读顺序。不同 panel 可占不同面积；不要给每格加叙述副标题，也不要给论文图添品牌、标题、页脚、阴影、卡片或冗余“500 cycles”。对齐的是实际绘图区，同类条件保持可比较的轴。
5. **人工复核**：领域读者对照原表与论文图页，看每个数字、曲线、图像、条件和图注；视觉读者在最终尺寸看是否一眼找到重点。记录审核人、日期、问题、修订和通过状态。只有五关都有记录，网页才能在“精选样图”露出。

## 当前网页的处理

旧图保留为下载包的代码测试/入门示意，附近直写“虚构教程，图型待复核”；不称为投稿级样图或电池证据。六面板图的不同合成数据没有共同实验来源，不得用“证据链”包装。前后对比只可比较完全相同的原始 panels；在未达投稿尺寸前叫“排版过程”，不叫“投稿成图”。

## English

Promote a figure from `test` to `showcase` only after a source-backed battery grammar check, data-integrity check, final-size/font check, composition check, and recorded human review. Synthetic demonstrations remain plainly labeled tutorials. A visual restyle alone never changes their status.
