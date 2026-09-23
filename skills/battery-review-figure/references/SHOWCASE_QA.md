# 首页样图准入：教程图不能自动变成展示图

先区分 **产品演示** 与 **实验数据图**。`synthetic_demo` 可以作为产品样图库作品，但必须在图旁明确写明“虚构演示、非实验数据”，并公开输入 CSV、生成脚本、模型和图件。它展示可复现的工作流与排版水平，**不证明材料性能、机理或论文结论**。真实实验图只有经原始数据和领域作者核对后才能标为 `validated_experimental`。当前旧版 CE、全电池、EIS、条件矩阵与独立数据拼成的六面板图仍是 `test`，不得因换配色就进入首页。

## 五道关

1. **实验语法**：图型在 [BATTERY_FIGURE_GRAMMAR.json](BATTERY_FIGURE_GRAMMAR.json) 中有准确的数据合同。辅助 panel 的选择有科学问题和同源数据；默认搭配有 [PANEL_EVIDENCE.json](PANEL_EVIDENCE.json) 的至少三个独立 DOI/图号/panel 支持。逐圈 CE 与 Aurbach 分开；保持率有参考圈。合成 EIS 模型要声明电路与参数，**不能称拟合实测点**。
2. **来源与诚实表达**：首选可合法复用的公开 source data 并给引用。合成数据必须近图标清、公开生成脚本和数据；可以展示模型生成的 ToF-SIMS、XRD 或综合工作流，但不能让读者误以为它是采集结果或机制证据。图内不得抹掉失败、异常、>100% CE 或关键条件。
3. **投稿尺寸**：按 [JOURNAL_FIGURE_SPEC.json](JOURNAL_FIGURE_SPEC.json) 设置最终 mm；检查轴字、panel 字母、色彩、比例尺、真实绘图区、裁边和缩小后的可读性。导出 SVG/PDF，检查 PDF 实际嵌入字体；指定 Arial 却出现 DejaVu 替换时报告失败或明确解释额外字形。
4. **版式**：一个 Figure 有一个问题和清楚的阅读顺序。不同 panel 可占不同面积；不要给每格加叙述副标题，也不要给论文图添品牌、标题、页脚、阴影、卡片或冗余“500 cycles”。对齐的是实际绘图区，同类条件保持可比较的轴。
5. **人工复核**：领域读者对照原表与论文图页，看每个数字、曲线、图像、条件和图注；视觉读者在最终尺寸看是否一眼找到重点。记录审核人、日期、问题、修订和通过状态。产品演示在网页露出前必须通过生成、来源、字体和视觉检查；**这仍不等同领域专家对实验的审核**。

## 当前网页的处理

旧图保留为代码测试/历史练习，不在首页。新版 `examples/showcase` 先生成 CSV，再由绘图脚本读入并导出 SVG、PDF、PNG。首页每张图旁标注 synthetic，元数据说明模型和限制。综合图只使用同一个 A/B synthetic study 的数据身份；它不是实验证据链。前后对比只可比较完全相同的原始 panels；在未达投稿尺寸前叫“排版过程”，不叫“投稿成图”。

## English

The public gallery may show explicitly labeled `synthetic_demo` workflow outputs after source, model, final-size/font, and visual checks. It must never present those outputs as experimental evidence. A real-data figure requires an additional domain-author review of the original records and interpretation. A visual restyle alone never changes status.
