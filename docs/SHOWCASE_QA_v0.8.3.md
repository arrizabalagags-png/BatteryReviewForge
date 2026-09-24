# v0.8.3 样图库制作与审核记录

**范围。** 13 个公开示例均由 `examples/showcase/build.py` 生成 CSV，再从磁盘输入脚本绘制。全部在图旁和 `metadata.json` 标为 `synthetic_demo`。它们展示绘图链路和版式，不提供任何可引用的材料性能或真实文献记录。旧版 `docs/assets/gallery` 练习图仍只作历史/测试资料。

| 新增图 | 这轮遇到的问题 | 处理和可检查文件 |
| --- | --- | --- |
| 倍率性能 | 阶梯倍率容易被误画成分组柱图，回到低倍率可能被模型补造 | `rate_capability/data.csv` 按 6 个阶段写真实 cycle；选定电压曲线的终点与对应行容量一致，测试逐条核对 |
| 独立 GCD/电压曲线 | 所选圈数与循环容量可脱节 | `gcd_profiles/data.csv` 从全电池 A 的第 1/100/300/500 圈终点生成；清楚标为模型演示，不假称测量 |
| 软包热图 | 第一版 panel 留白过大；单有一块渐变无法说明表面测温 | 改为大温度图、同一场的截线和 Tmax 时间图；保存软包轮廓/极耳/色标范围到 `geometry.json`，检查截线与场逐点相同 |
| 文献基准散点 | 演示点容易让读者误以为真实论文；不同条件直接排位也会误导 | 使用 `SIM-001` 等虚构 ID、48 点、共同 0.2 C/100 圈/25 °C 与同一容量分母；不提供伪 DOI |
| 报告矩阵 | `NR`/`NV` 容易混为零；总图缩小后标签会变小 | `status_key.json` 定义 R/P/NR/NV/NA；单图展示 18 行，总图只展示前 10 行，近图写合成示例 |
| 十面板能力总图 | 第一版小 GCD 图例压住曲线、EIS 坐标出现负值、散点色彩无图例；机械平铺缺主次 | 顶部放同研究六面板与软包图，中部经典图，下部特殊图；小图简化标签，EIS 从零起，散点在小图以形状/颜色表示类别。`alignment.json` 有 30 项绘图区检查，最大误差 0 pt |

**从规则沉淀的约束。** [SHOWCASE_SPEC](../skills/battery-review-figure/references/SHOWCASE_SPEC.md) 按类型列出输入坐标、允许邻图、必填说明和自动补足禁令；[PLOT_QA_CHECKLIST](../skills/battery-review-figure/references/PLOT_QA_CHECKLIST.md) 把科学、版式、公开三步分开。`BATTERY_FIGURE_GRAMMAR.json` 加入软包表面温度图型。倍率+电压曲线、热图+截线等是有来源关系的**演示组合**；没有达到三个独立 primary paper 的配对，不能自动变成所有用户数据的默认面板。

**首页取舍。** 首页展示同研究六面板、软包热图、文献基准散点、全电池和 EIS。十面板图做桌面首页的能力总览，手机端改用可辨的软包图，完整大图放样图库供放大。独立 GCD、报告矩阵、Operando XRD、ToF-SIMS、倍率和对称电池在完整样图库中；未把 13 张缩略图塞在首页。六面板同研究图只表明共享 A/B 演示身份，不构成机制证据。

**实际检查。** 13 类都有 CSV/JSON 来源、独立 `generate_data.py` 与 `plot.py`、SVG/PDF/PNG、`metadata.json` 和 `alignment.json`。跨面板 1.5 pt 尺规在可比位置执行；总图 30 项、六面板 21 项通过。独立单图被标记为 `independent_panels`，不伪称做过跨格对齐。十面板 PDF 嵌入 ArialMT、Arial-BoldMT 和 Arial-ItalicMT；该结果只对应本机构建环境。PNG 已人工看过版式，独立领域作者仍须在最终投稿用途与真实数据上复核。

**参考性质。** [Nature Communications 锂硫文献基准研究](https://www.nature.com/articles/s41467-025-60528-4) 和 [软包表面温度研究](https://www.nature.com/articles/s44172-022-00005-8) 用来确认图型所服务的问题。这里没有复制论文图或把其点位当演示数据。详细 Figure/Panel 证据等级仍以仓库的 `PANEL_EVIDENCE.json` 为准。
