# 电池论文图型语法：先弄清实验，再决定画法

**给第一次用的人：**把原始表格、仪器文件或已有图片交给助手，说清你想回答的科学问题。助手先识别电芯和测试协议，再从图型库里选画法；如果缺关键条件，它应先画能确定的部分并把缺口说清。漂亮的配色不能代替正确的实验解释。

机器可读清单在 [BATTERY_FIGURE_GRAMMAR.json](BATTERY_FIGURE_GRAMMAR.json)，逐面板来源在 [PANEL_EVIDENCE.json](PANEL_EVIDENCE.json)，期刊尺寸在 [JOURNAL_FIGURE_SPEC.json](JOURNAL_FIGURE_SPEC.json)。`status=evidence_backed` 表示图型在本轮读过的论文中有实例，**不表示每一种搭配都已验证**。目前只有 JSON 中的两种 `default_option` 达到了三个独立 primary paper 的门槛。其它推荐先当可选方案，不能替用户发明面板。

## 先分清这四件事

| 用户给的材料 | 先问清或读取 | 合理的第一版 | 不能自行推断 |
| --- | --- | --- | --- |
| Li∥Cu 每圈库伦效率 | 逐圈数据、镀锂面容量、电流、剥离截止、CE 分子分母 | Cycle–CE 原始点/细线 | 把 Aurbach 平均值变成 300 圈曲线；抹掉 >100% 或失效段 |
| Aurbach / modified Aurbach | 完整协议、储锂/剥离步骤、计算式 | 电压–时间/容量协议曲线，旁边给明确定义的 CE | 以普通逐圈 CE 代替 |
| 全电池长循环 | 正负极、载量、倍率、电压窗、容量分母、形成圈 | 容量–圈数；若数据同源，可加 CE 或选定圈电压曲线 | 自选保持率分母；虚构 N/P、E/C、失效模式 |
| EIS | 实部、虚部、频率、SOC、温度、扰动、拟合模型（若有） | 带单位的 Nyquist 原始点；必要时另有真正有问题意识的 Bode/局部图 | 把连接线叫拟合；凭半圆外观命名阻抗 |

**容量保持率**：`Q_n / Q_reference × 100%` 的 `reference_cycle` 必须由作者或原始记录明确给出。没有参考圈时只画容量，不计算保持率。即使提供的是已算好的 retention%，也要标明参考圈。

**合成样图**：只用来说明布局和软件能力。不要用 `trend + 独立高斯噪声` 伪装仪器曲线；更稳妥的是用获准复用的公开 Source Data。若必须合成，近图处清楚写“虚构演示”，并保留生成代码和数据；不要把合成的 Raman、RDF、SEM 或 ToF-SIMS 组合成仿佛同一次实验的机制链。

## 怎么选相邻 panel

先写每个 panel 的任务：**主结果、解释主结果的直接证据、正交验证、条件边界**。相邻关系只来自同一实验材料、明确科学问题或已核对论文中的图型组合。它不由“剩余空白”决定。

- **默认选项 CE_AURBACH_01**：逐圈 Li∥Cu CE 与独立 Aurbach 测试并列。三篇来源：[Huang et al., AFM, Fig. 5a–c](https://doi.org/10.1002/adfm.202211364)、[Li et al., Angew, Fig. 2a–b](https://doi.org/10.1002/anie.202319090)、[Zeng et al., ACS Nano, Fig. 4a,c–d](https://doi.org/10.1021/acsnano.3c07038)。两种 CE 的协议和统计口径分别报告。
- **默认选项 FULL_PROFILE_01**：全电池循环与同一电芯/条件的选定圈充放电曲线。三篇来源：[Huang et al., AFM, Fig. 6b–e](https://doi.org/10.1002/adfm.202211364)、[Liu et al., AFM, Fig. 4a–b](https://doi.org/10.1002/adfm.202209725)、[Liu et al., Small, Fig. 4a–d](https://doi.org/10.1002/smll.202311812)。选哪些圈由数据和论证决定。
- **可选，不自动添加**：Li∥Li 长时曲线加有范围标记的波形局部图；rate 与同一测试的电压曲线；Nyquist 与 Bode；ToF-SIMS 深度剖面与离子图。这些都需要实际数据与明确目的；不能只因为文献里见过就补造一个 panel。

## 数值图与图像图的不同处理

数值图必须保留原始顺序、缺测与失效；一切平滑、导数、拟合、归一化要有处理记录。`dQ/dV` 需要导数算法和窗口；GITT 的扩散系数是模型推导值；XPS 拟合要有背景和约束；RDF 的原子对与积分截止要有定义。没有这些，先展示原始结果，不展示假精确的派生结论。

显微图、元素图和 ToF-SIMS 地图需要原始像素、标定与比例尺。改变风格只能改版式、文字、色表等允许的显示层，不能重构颗粒、界面或离子分布。溅射**时间**不自动等于物理**深度**；独立归一化的离子颜色不代表跨碎片的绝对丰度。条件矩阵区分 `reported`、`partially reported`、`NR`（查过未报告）、`NV`（尚未核验）、`NA`（不适用）。

## 尺寸与风格

先定目标期刊与最终物理尺寸，再选 `journal_neutral` 或对应期刊配置。Nature 的 [官方图页](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)规定 89/183 mm、最大高 170 mm、常规文字 5–7 pt、8 pt 小写粗体 panel 字母；其[制图页](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)要求字体可编辑并嵌入，建议避免背景网格、彩色文字和阴影。ACS Chemical Reviews、Wiley 通用指南与 RSC Advances 的数值各有差别，见 JSON；**不要把一家期刊的规则说成所有期刊的规则**。

默认论文图面只放轴、单位、必要组别、图例、比例尺与 `a/b/c`。解释性的标题、副标题、页脚和“500 cycles”之类重复信息放到网站说明或图注。作者确实需要的条件标识可以保留。配色表示样品身份与科学类别，并保持跨 panel 一致。最终在真实毫米尺寸检查字体、线宽、实际绘图区对齐、裁边和可读性；SVG/PDF 先于预览 PNG。导出 PDF 后检查**实际嵌入的字体**，不把 Matplotlib 的静默替换当作“Arial 风格”。

## 证据升级流程

1. 自动脚本只定位论文图注；它不能证明看过图，更不能替代方法学核查。
2. 人工逐页核对图号、panel、坐标、编码、相邻关系、实验条件，记录 DOI 和核验状态。只保存自己提炼的元数据，不公开上传的 PDF、截图或整段图注。
3. 相同图型搭配在至少三个独立 primary paper 中成立，才可标成 `default_option`。否则只列为可选，不要求模型照做。
4. 一个首页样图必须再过科学来源、数据/图像完整性、期刊尺寸、字体嵌入、视觉与人工复核；参见 [SHOWCASE_QA.md](SHOWCASE_QA.md)。

**本轮进度**：51 份本地 PDF，自动识别 297 个图注候选（可能包括误识别，仍须人工筛选）；人工核过 5 篇不同论文的 6 个 Figure、31 个 panel。这个范围支撑上述两个默认搭配，**不支撑声称 51 篇都已逐 panel 审完**。后续继续扩充时，按 JSON 逐条加 DOI、图号、panel 与核验状态。
