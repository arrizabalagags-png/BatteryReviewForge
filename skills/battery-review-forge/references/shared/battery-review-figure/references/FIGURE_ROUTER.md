# 我该用哪个画图技能？

先看**你手里有什么**，再看文件类型。文件扩展名只能决定怎么读取，不能决定图里的科学问题。

| 你现在要做的事 | 入口 | 接下来会做什么 |
| --- | --- | --- |
| 给 CSV、TSV、TXT、XLSX 原始数据画库伦效率、循环、对称电池、充放电或 EIS 图 | `battery-review-figure` | 看列名、确认电芯和测试条件、选图型和风格、重画并输出来源记录 |
| 给一段机制解释或综述提纲做全新示意图 | `battery-review-figure` | 先分清实测、计算和假说，再选原创可编辑模板与证据链 |
| 已有几张完成的 PNG、TIFF、PDF、SVG，想拼成 Fig. 2 | `battery-figure-assemble` | 先判断主次和证据顺序，再按毫米拼版、统一字母/留白并检查实际绘图区 |
| 既有数据又有显微图/谱图，想做一张完整多面板图 | `battery-review-figure` ↔ `battery-figure-assemble` | 数据先重画成单面板；拼版若发现某张不合适，可回到原始数据或可编辑源文件重出，再拼一次 |
| 只想核查两篇论文的容量/寿命能否放在一个柱图里 | `battery-metrics-audit`，需要画时再用 `battery-review-figure` | 先核分母、电芯构型和测试协议，避免把不同边界排成名次 |
| 要从选题到投稿规划整篇综述和全套图 | `battery-review-forge` | 按阶段调用单项技能；不用一次加载所有技能 |

**新手只需这样说：**“这是我的文件。先告诉我你看到了什么、能做什么、还缺什么；然后建议一张预览。”用这四行回答，作者不用先选技能或填一张长表。投稿图需要核对的电芯构型、容量分母、倍率/电流、温度、载量、电解液量、循环或电压范围，按当前图型逐项看。先完成能核实的部分，只问缺少且会改变图义的条件；不要根据文件名、仪器品牌或截图猜值。

画图前只问一次风格：**“你想要清爽期刊风、柔和综述风，还是高对比展示风？也可以说‘你来选’。”** 需要更多控制时再展示[六种预览](../assets/style-preview.svg)和完整预设表。同一稿件沿用已选风格，不必每画一个面板都重问；作者让你选时，按图的证据角色选并记录。等待选择时继续读数据和核条件，不要把未选风格的图叫作最终交付。

如果输入是论文截图，只能当版式参考。数值图需要原始或作者核实过的数据；显微图需要比例尺和采集信息。若文件是旧 XLS、Origin 工程或仪器专有格式，先请作者导出标准表，不要假装已经读懂内部格式。拼图前若某面板字体或配色不同，优先从可编辑源文件重出；不要靠缩放或整体调色改写实验图像。

## English quick route

Raw battery tables or a new schematic go to `battery-review-figure`. Finished image/PDF/SVG panels go to `battery-figure-assemble`. A mixed figure can move back to the figure skill when assembly reveals a panel that must be regenerated from editable source or data. Check battery metrics before a direct cross-study ranking. Ask for one plain-language style before final drawing and reuse it across the figure set.
