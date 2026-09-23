# 我该用哪个画图技能？

先看**你手里有什么**，再看文件类型。文件扩展名只能决定怎么读取，不能决定图里的科学问题。

| 你现在要做的事 | 入口 | 接下来会做什么 |
| --- | --- | --- |
| 给 CSV、TSV、TXT、XLSX 原始数据画库伦效率、循环、对称电池、充放电或 EIS 图 | `battery-review-figure` | 看列名、确认电芯和测试条件、选图型和风格、重画并输出来源记录 |
| 给一段机制解释或综述提纲做全新示意图 | `battery-review-figure` | 先分清实测、计算和假说，再选原创可编辑模板与证据链 |
| 已有几张完成的 PNG、TIFF、PDF、SVG，想拼成 Fig. 2 | `battery-figure-assemble` | 盘点、按毫米拼版、统一字母/留白并检查实际绘图区 |
| 既有数据又有显微图/谱图，想做一张完整多面板图 | 先 `battery-review-figure`，再 `battery-figure-assemble` | 先把数据重画成单面板，再拼版；图的科学判断仍由前者负责 |
| 只想核查两篇论文的容量/寿命能否放在一个柱图里 | `battery-metrics-audit`，需要画时再用 `battery-review-figure` | 先核分母、电芯构型和测试协议，避免把不同边界排成名次 |
| 要从选题到投稿规划整篇综述和全套图 | `battery-review-forge` | 按阶段调用单项技能；不用一次加载所有技能 |

**三句就能开始：**“这是我的文件；我想让读者看懂什么；图准备放在论文还是汇报。”技能会先读文件并列出缺的条件。投稿图还需说明电芯构型、容量分母、倍率/电流、温度、载量、电解液量、循环或电压范围，以及图型特有的条件。不要根据文件名、仪器品牌或截图猜这些值。

画图前只问一次风格：**“你喜欢哪种颜色风格？深海蓝绿、玫蓝渐层、珊瑚冰蓝、暖冷对照、期刊极简，还是清晰对比？”** 给作者看[预览](../assets/style-preview.svg)。同一稿件可沿用已选风格，不必每画一个面板都重问；作者明确说“你来选”时，可按图的证据角色选并记录。没有得到选择时，可以继续读数据和核条件，但不要把未选风格的图叫作最终交付。

如果输入是论文截图，只能当版式参考。数值图需要原始或作者核实过的数据；显微图需要比例尺和采集信息。若文件是旧 XLS、Origin 工程或仪器专有格式，先请作者导出标准表，不要假装已经读懂内部格式。拼图前若某面板字体或配色不同，优先从可编辑源文件重出；不要靠缩放或整体调色改写实验图像。

## English quick route

Raw battery tables or a new schematic go to `battery-review-figure`. Finished image/PDF/SVG panels go to `battery-figure-assemble`. A mixed figure uses the first skill to make data panels, then the second to assemble them. Check battery metrics before a direct cross-study ranking. Ask for one named style before final drawing and reuse it across the figure set.
