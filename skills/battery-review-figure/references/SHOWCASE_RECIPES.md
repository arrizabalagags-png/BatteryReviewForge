# 电池图怎么选构图：先看证据，再挑画法

这个目录保留宽覆盖的**布局想法**，颜色由 [STYLE_PRESETS.md](STYLE_PRESETS.md) 单独选择。**先按[电池图型语法](BATTERY_FIGURE_GRAMMAR.md)核对测试协议与相邻 panel；下表不是已验证的默认模板。**链接里的旧版图均为虚构教程或回归测试，其中 CE、全电池、综合拼图等已发现科学表达问题，不能直接挪进论文或首页精选。

## 先回答三个小问题

1. 读者第一眼必须看什么：结构、空间分布、时间变化，还是条件对比？让这个证据占最大的画幅。
2. 手里的是原始表格、仪器原图、可编辑示意，还是已经做好的几个面板？原始表格先绘图，现成面板交给 `battery-figure-assemble`。
3. 哪些标签是**识别数据**必需的：轴、单位、样品名、离子碎片、比例尺、组别、分图字母？其余解释进图注，图里不加品牌抬头、总标题、副标题或页脚。

## 十种可复用的画法

| 手头的东西 | 推荐构图 | 图内留下什么 | 样图与代码 |
| --- | --- | --- | --- |
| Li∥Cu 逐圈 CE | 先画完整逐圈 CE；若有同源 Aurbach 协议，可作独立 panel。早期/后期放大只有确有科学问题时才加 | 协议、cycle、CE (%)、电流/面容量和完整失效点 | [旧版教程图（待修订）](../../../docs/assets/gallery/ce-demo.svg) · `render_gallery.py:draw_ce` |
| 全电池容量与电压曲线 | 放电剖面与 cycling 相邻，容量分母由轴标和图注说清 | 电压、容量、圈数和系列身份 | [全电池](../../../docs/assets/gallery/full-cell-demo.svg) · `draw_full_cell` |
| 对称电池长时记录 | 主图保留全程，旁边放明确时间段放大图 | 正负电压、小时、放大窗口和相同颜色 | [对称电池](../../../docs/assets/gallery/symmetric-demo.svg) · `draw_symmetric` |
| 已有多张性能、示意和重复实验图 | 证据主次明确的 2×2 或跨栏拼版；比较图对齐**实际绘图区** | 分图字母和必要对象标签；图注解释各面板角色 | [拼图](../../../docs/assets/gallery/assembled-demo.svg) · `battery-figure-assemble` |
| ToF-SIMS 2D 离子图和溅射曲线 | 上排同尺度的单通道与叠加，下排宽幅时间剖面 | 碎片、比例尺、信号单位、sputter time；同一通道保持同一色 | [ToF-SIMS](../../../docs/assets/gallery/tofsims-demo.svg) · `batteryplot.tofsims_map/depth` |
| Raman/FTIR 的多条光谱与 MD 的 RDF | 光谱做干净的垂直错位；RDF 独立分栏，同一距离轴 | 波数/距离单位、每条谱身份、RDF 的配对定义 | [光谱/RDF](../../../docs/assets/gallery/solvation-evidence-demo.svg) · `render_showcases.py` |
| XPS 拟合、质量谱或深度剖析 | 原始/拟合/残差成组，峰的归属另有来源；深度或 sputter time 保持原单位 | 原始强度、组分、残差轴和处理记录 | 按[图型小抄](BATTERY_FIGURE_ATLAS.md)设计；需作者峰拟合数据 |
| 原位 XRD、空间/时间二维数据 | 横纵真实坐标 + 明确色标；重要切片在旁边，而非在热图上堆满箭头 | 色标单位、时间/电位状态、峰位置及处理说明 | [虚构 XRD 状态图](../../../docs/assets/gallery/operando-xrd-demo.svg) · `render_showcases.py`；实用时需原始矩阵 |
| 电池结构或制备流程 | 分层/透视为主，标签外置；颜色固定表达集流体、电极和隔膜 | 部件身份；比例/方向如确有意义 | [分层电芯](../../../docs/assets/gallery/cell-architecture-demo.svg) · `render_showcases.py` |
| 多论文证据与条件 | 条件矩阵或“设计→表征→电芯”证据链；不把异质研究压成一个排名 | DOI/来源、R/NR/NV 与条件分组 | `conditions_matrix` 与[证据链模板](../assets/original/electrolyte-evidence-chain.svg) |

这些是构图**路线**，不是万能现成按钮。上传 CSV/XLSX 时，当前 `plot_uploaded.py` 可以直接画 CE、全/半电池循环、对称电池、电压曲线、Nyquist、循环保持率、倍率，以及 ToF-SIMS 的规则网格离子图和溅射时间曲线。Raman、RDF、XPS、原位热图的文件格式和处理方式差别很大：先保留原始导出和方法，再据作者给的轴、归一化、峰归属和物理单位复用代码/版式。不能从论文截图倒推出可投稿的原始谱。

## 示意图要升级，先检查“谁是真实的”

在可编辑源文件里，把色块和粒子分成集流体、活性层、隔膜、金属/碳、溶剂、阴离子和溶剂化物等语义层。需要透视时只表达层次，不用光泽、阴影或假显微纹理暗示测量精度。每一条机理箭头先分辨是观察、计算支持还是作者假设；不明确的箭头不要画成确定因果。图中文字只负责辨认对象，论证写进图注。用 `battery-review-figure` 从真实材料设计原创示意，再用 `battery-figure-assemble` 与实测图拼成最终图版。

## 给 Agent 的最短说法

> 我上传了材料。先按这份图型路线判断适合哪种构图，说清主面板、辅助面板和缺少的原始数据。按我选的颜色风格出 SVG/PDF/PNG。图内不要加品牌抬头、解释性副标题或页脚；给我一份单独的图注与来源说明。
