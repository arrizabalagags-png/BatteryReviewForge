# 22 个领域演示的模型核对 — 2026-10-01

本轮按照用户要求审查合成演示的公式、单位、条件和数据关系。数值仍为 VoltPeer 原创教学输入；引用用于支持模型定义或报告边界，不能当成文献的实测数据。本记录不把合成数据标签当作科学依据。

## 实际验证

- **24 个测试，60 条记录，通过。** 最终一次运行耗时 55.734 秒。
- 12 个 specialist/corpus 示例和 10 个 domain 示例均在临时目录生成、渲染。22 份 metadata 通过现有严格 schema 检查；每份有 `scientific_basis` 和实际四边框 artist 记录。
- 10 个独立 domain `render.py` 均通过真实 CLI 原始 CSV 重放；能量/容量额外文件随包生成。
- 对 CE、Zn-I₂、液流、光伏和液流完整曲线进行篡改负例。即使光伏假电流仍满足 `P=JV`，单二极管检查仍拒绝它。
- 一个比例正确但数字已改的 CE 文件被重放 CLI 拒绝，防止给别人的数据盖上原模型来源声明。
- 机器记录、具体断言、输入文件和生成器 SHA-256 见 [科学回算记录](2026-10-01-scientific-domains.json)。测试入口为 `tests/test_synthetic_domain_physics.py`。

本子任务没有修改已服务网站、正式版本或旧 ZIP，也没有提交、推送、部署或运行付费模型。最终公开目录、网站镜像、下载包及链接闭合由主任务重新生成和检查。

## 改了哪些数据问题

| 原问题 | 本轮处理 |
|---|---|
| PV 用任意九阶多项式描绘 J–V，只有 `P=JV` 自洽 | 改成有明确参数的理想单二极管模型，保留开路电压之后的负电流；MPP 只在发电象限取值，单独记录 FF、模型效率和网格分辨率。 |
| Flow 只有三条预设百分比，没有 Q/V/能量输入 | 新增每圈充放电容量、容量加权电压、能量账本，以及 300 条完整 `V(Q)` 分支。能量由积分回算，CE、VE、EE 从同一边界得到。 |
| Zn–I₂ 容量与 CE 各画各的，缺充电容量和反应边界 | 新增充电容量；限定 `I₂+2e⁻→2I⁻` 且不计碳/其他反应容量；按每克 I₂ 回算理论容量，说明活性容量衰减和过量锌缓冲的区别。 |
| Zn 对称电池两端电压叫“单电极过电位” | 改列名和轴标签为 `cell_voltage_mV` / Cell voltage，并保存 ±电流与半周期。禁止无依据地将电压除以二后分配给单个电极。 |
| FTIR 直接从百分比里减高斯凹槽 | 先生成非负叠加吸光度，再按 Beer–Lambert 关系转透过率；同时保存吸光度，能独立回算。 |
| MSD 是带正弦起伏的任意斜线，写作“轨迹” | 改成三维无漂移 Brownian 均值 `MSD=6Dt`；保存输入 D 和温度关系。没有生成 MD 轨迹，也没有拟合 D。 |
| GITT 每次脉冲用不同经验衰减，状态在切换处重置 | 改为一个跨脉冲连续传播的 RC 极化状态，只允许欧姆项随电流切换跳变；保存累计电荷、OCV 模型值和 RC 值。 |
| XPS 只有高斯成分加固定幅度噪声 | 改为已知混合线型和 Poisson 计数噪声，记录期望计数；保留泛化 Component 标签，没有冒充优化拟合或化学归属。 |
| Transference 直接用几何半圆，频率缺失 | 改为 `Rs+(R_interface||C)` 的真实复阻抗频率扫描，保留单独 Rs 和界面电阻；Bruce–Vincent-style 回算明确 mA→A。 |
| K-rate 各阶段容量随便指定几个常数 | 改为明确的电流限制可用容量关系与独立活性容量衰减，回到初始电流时恢复但不凭空回到初始容量。 |
| NMR / LSV / TRPL 来源和解释边界不足 | NMR 用泛化吸收型 Lorentzian 峰；LSV 用明确假设的单向阳极指数项；TRPL 保存两种已知衰减和背景，没有写成测得寿命或机制。 |

## 覆盖范围与条件

| ID | 数据/公式检查 | 解释边界 |
|---|---|---|
| cyclic_voltammetry | 按采集顺序三角扫描；正反支路、参考电极、速率和原始数值范围 | 是经验峰形教学模型。`sqrt(rate)` 趋势和闭合端点门函数不等于扩散 PDE、可逆反应拟合或扩散控制证据。 |
| differential_capacity | 同一充电支路的 Q/V 导数积分回算容量；采集顺序不变 | 两个原创建模的可用容量跃迁，无相变归属和完整充放电滞后。 |
| gitt_pulse | 12 次 6 min 通电/24 min 休息；电荷积分 0.12 mAh；RC 连续性 | 演示脉冲方案；没有 Fick 扩散拟合，有限休息不等于达到平衡。 |
| ionic_conductivity | Kelvin、mS/cm→S/cm、输入 Arrhenius Ea 回算 | 已知模型 Ea，不是实测拟合值；没有 VTF、结晶或接触误差模型。 |
| xps_components | 已知成分之和、非负整数计数、Poisson 统计及残差 | 泛化成分，无材料/价态归属，无 Shirley/Tougaard 背景或优化器。 |
| raman_series | 非负同尺度峰；偏移仅用于显示 | 无分子、浓度、真实位移或面积标定。 |
| ftir | `A=-log10(T/100)` 与 `0<T<=100` | 原创吸光度强度，不单独确定摩尔吸收系数、浓度、光程。 |
| nmr | 泛化 Lorentzian、ppm 参考、非负信号 | 没有真实标准、分子归属、定量积分或 T₂ 结论。 |
| rdf_coordination | 短程排斥、`g→1`、`CN=4πρ∫r²gdr` | 解析各向同性模型，不是 MD 或被指认的溶剂化壳层。 |
| msd | 3D `6Dt`、输入 D、温度关系、Å²/ps→cm²/s | 没有轨迹、弹道区、受限扩散或相变；不能用于预测真实低温电解液。 |
| lsv | 单向阳极电流对数斜率、正值、温度和电位参考 | 反向产物反应和耗尽被忽略；不从“上翘”自动认定分解电位/稳定窗口。 |
| transference | 理想 RC 频率、圆关系、界面 R 与 Rs 区分、阻抗修正计算 | 方法相关表观值；没有浓溶液活度修正、EIS 拟合或真实迁移数认证。 |
| na_metal_ce | 逐圈镀/剥容量与 CE、正损失、面积容量和参考端点 | 来源只支持电荷比和协议局限；不把 Li 论文数字移植为 Na 性能，不由 CE 推寿命。 |
| k_ion_rate | 电流上升可用容量降低，回到原电流后恢复并保留活性容量损失 | 每克工作活性材料、过量 K 金属对电极，不是全电池能量或已知材料纪录。 |
| zn_plating_ce | 逐圈镀/剥账本、面积电流/容量、名义端点 | 没有气体/副反应/锌利用率模拟或经验证的实验协议。 |
| zn_symmetric | 两端电压、电流符号、1 h 半周期、面积转移量 | 不能当成单电极过电位、短路时刻、枝晶证据或全电池寿命。 |
| zn_air_power | 面积电流×电压=面积功率、下降电压、区间内正功率峰 | 有效活化＋欧姆损失，不是真实氧气传输、催化剂或电堆标定。 |
| zn_i2_cycle | `Qdis/Qchg`、I₂ 两电子理论边界和单位 | 仅每克 I₂；四电子/碳容量未包括。过量锌下 CE 与可用阴极容量不能套通用连乘寿命。 |
| flow_efficiency | 150 圈的完整两分支 Q/E、容量加权电压和 CE×VE | 电池 DC 能量边界，排除泵、逆变、热管理等；不能写系统往返效率。 |
| pv_jv | 理想二极管残差、Voc 零电流、Jsc、发电象限 MPP/FF/效率 | `Rs=0,Rsh=∞`；没有校准光谱、真实器件效率、迟滞或电阻提取。 |
| pv_stability | t=0 归一化、正值、固定工作点模型 | 没有实测 T80/T95、MPP 跟踪、气氛/封装或外推寿命。 |
| pv_trpl | 非负双指数＋背景、已知一阶衰减率 | 未卷积 IRF，没有测得寿命、复合机制或材料归属。 |

共有 10 个 `analytic_model` 和 12 个 `phenomenological_model`。这个分类避免把“有公式”误称为某种具体材料的已验证物理预测。DSC、TGA、EQE 不在这 22 个资源里，记录为未覆盖，不能虚构通过。

## 关键回算结果

这些数字只证明当前教学模型和存储文件的内部关系，不代表器件实测性能。

| 模型 | 实际结果 |
|---|---|
| GITT | 12 次脉冲；左端保持电流积分 `0.12000000000000002 mAh`，与保存电荷一致。 |
| XPS | 均方残差/平均期望计数 `0.9645458303964828`；本固定随机种子的计数噪声符合预定统计量级。 |
| Zn–I₂ | 两电子 I₂ 理论容量 `211.19414583619036 mAh/g_I2`；演示最大放电容量 `175.75487749150244 mAh/g_I2`。理论上界只用于本例限定反应。 |
| Flow | 300 条 V(Q) 分支的最大能量回算误差 `5.684341886080802e-14 mWh`。 |
| PV | 模型 `Jsc=23.5 mA/cm², Voc=1.08 V`；网格 MPP `Vmpp=0.954 V, Pmax=21.566445143491286 mW/cm²`；FF `0.8497417314220365`。在设定 `Pin=100 mW/cm²` 下模型效率为 `21.566445143491286%`，不能写成测得器件效率。 |

## 模型定义的来源

仅以下定义/边界用于本轮核对；任何演示数字都不是从这些来源取出的实验值。旧 metadata 中的 `reference` 继续表示之前的图件语法参考；新增 `scientific_basis.references` 才描述本次模型支持的具体范围。

- [Sandia/NIST PVPMC 单二极管等效电路](https://pvpmc.sandia.gov/modeling-guide/2-dc-module-iv/single-diode-equivalent-circuit-models/)：光电流、二极管项、热电压及电阻边界。
- [IUPAC Beer–Lambert law](https://goldbook.iupac.org/terms/view/B00626)：吸光度与透过率关系。
- [GROMACS MSD](https://manual.gromacs.org/current/reference-manual/analysis/mean-square-displacement.html)、[RDF](https://manual.gromacs.org/current/reference-manual/analysis/radial-distribution-function.html)：三维 Einstein 关系、RDF/配位积分定义。本站示例没有运行 GROMACS。
- [IUPAC Lorentzian band](https://goldbook.iupac.org/terms/view/L03628)、[NIST normal distribution](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm)：数学线型，不是化合物峰归属。
- [IUPAC Arrhenius equation](https://goldbook.iupac.org/terms/view/A00446)：温度指数关系。传导前因子与活化能为原创输入。
- [Gamry 电化学阻抗基础](https://www.gamry.com/application-notes/EIS/basics-of-electrochemical-impedance-spectroscopy/)及 [CV/电荷转移公式](https://www.gamry.com/electrochemistry-applications/cv-cyclic-voltammetry)：理想电路、采集顺序、速率趋势和指数项定义。
- [Evans、Vincent、Bruce 1987](https://doi.org/10.1016/0032-3861(87)90394-6)：阻抗修正极化方法；这里是给定参数的表观量演示。
- [四电子 Zn–I₂ 原研究](https://www.nature.com/articles/s41467-020-20331-9)：普通两电子与附加四电子反应应区分；本例只采用前者。[NIST Faraday 常数](https://physics.nist.gov/cgi-bin/cuu/Value?f)用于电子摩尔电荷换算。
- [Flow assessment framework](https://www.nature.com/articles/s41560-020-00772-8)：电池效率和系统边界的报告约束；本例 V(Q) 为原创。
- [PV 稳定性报告共识](https://doi.org/10.1038/s41560-019-0529-5)：工作点、归一化和环境边界；不是本例衰减常数的来源。
- [PicoQuant SymPhoTime64 手册](https://downloads.picoquant.com/manuals/SymPhoTime64_Manual.pdf)：指数寿命模型、IRF 与拟合条件；本例没有执行仪器拟合。
- [CE 定义和协议局限](https://www.nature.com/articles/s41560-020-0648-z)、[锌电池实验报告边界](https://www.nature.com/articles/s41467-022-28381-x)、[电池报告检查表](https://pubs.acs.org/doi/10.1021/acsenergylett.1c00870)：配置、库存、分母和协议必须说清楚，不支持跨材料移植性能数字。

## 给后续集成者

1. 从上述三个生成器生成新版数据，不能只替换 PNG；新增 CSV/JSON、metadata、参考图、示例 ZIP 一起更新。
2. 保留旧版本 ZIP 的字节和身份。历史演示是历史快照，新模型应进新的包版本。
3. Zn 对称电池列名变更应检查所有消费者；本文件只修了领域生成器/自带 renderer，Starter 和网站由主任务核对。
4. `--demo-input` 现在只重放该例的原始数值 CSV，允许等价浮点文本，不允许把任意数据盖成本站模型。作者实验数据使用有输入合同的绘图包/Starter。
5. 当前报告是临时生成实测证据，主任务应核对最终目录的 metadata 与原始 CSV 哈希闭合，再生成网站和包。
6. 没有新完成真人/材料专家科学复核、实验重现或最新树的模型/宿主行为 EVAL，继续明确记录这些边界。

复跑命令（项目独立 QA 环境）：

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& './outputs/qa-venv/Scripts/python.exe' 'tests/test_synthetic_domain_physics.py' `
  --report 'docs/validation/2026-10-01-scientific-domains.json' -v
```
