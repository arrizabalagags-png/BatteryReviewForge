# 核心合成示例：科学边界与修复记录

日期：2026-10-01。范围：18 个核心图库示例的生成模型，以及 `full_cell`、`li_li`、`operando_xrd` 三个可替换作者数据的独立绘图包模板。

这份记录说明原创教学数据怎样生成、哪些关系被回算、还有哪些解释不能成立。它不将合成图认定为实验，也不将测试通过认定为真实材料性能或模型宿主兼容性认证。

## 1. 本轮发现的主要问题

| 原问题 | 修复 | 有效范围 |
| --- | --- | --- |
| 把 CE 累乘当作所有容量曲线的通用约束 | 仅在明确写出的有限库存、无额外补偿的全电池教学模型中保留；图库 NMC811‖Li 使用独立活性容量和 CE 账本 | 教学模型，不能当作作者实验的验收条件 |
| 资源名 `full_cell` 与图库实际半电池身份冲突 | 保留旧 ID 以兼容链接，metadata 明确 excess-Li half-cell；独立全电池 recipe 使用自己的 CSV/config/图 | ID 不等于电池配置，不得混用参考图 |
| Li‖Cu 声称 1 V 截止，但已保存曲线未达到截止 | `Qstrip = eta*Qplate`，电流、时间、回收容量一致；保存真实 1 V 的示意终点并调整图轴至 V | 电压形状是自定显示关系，不拟合成核或 SEI |
| Li‖Li 半周切换时重复时间、状态接续不清 | 唯一时间轴；电流为右连续分段常数；RC 极化状态连续，允许串联电阻导致端电压跳变 | 外部电量不是沉积质量或 CE |
| Aurbach 最终剥离量可能超过可回收库存 | 每段更新 active/trapped/plated/stripped 四个账本；最终剥离仅取剩余 active | 原创协议教学例，非论文数值 |
| EIS 半圆、尾部与 Bode 容易被独立绘制而失联 | 用一个被动 Randles CPE/Warburg 复阻抗模型生成实部和虚部；相位来自同一 CSV | 无拟合、无微观机制或扩散系数反推 |
| XRD 峰移是任意平移，进度被称 SOC | 通过一阶 Bragg 关系生成两个虚构晶面间距的峰位；轴改为 chosen progress | 不赋予 hkl、物相或电压因果 |
| ToF-SIMS 图均值与溅射曲线不一致 | 同一非负场计算图与 30 s 均值，移除先裁数据再算均值的差异；核对色标与曲线不截值 | 明确 layout fixture；强度不是浓度，时间不是深度 |
| 倍率恢复含任意奖励项 | 可逆倍率可达份额与不可逆衰减分开计算 | 选择的显示函数，不是通用传输定律 |
| 热图把 2 C 和自定热量混作物理推导 | 采用正功率、正热导的独立热节点，声明热容/热导/时间常数 | 未耦合的教学热节点，不是 IR 或电芯电热仿真 |
| 编造的文献记录易被当成真实研究排名 | 设为 layout fixture，SIM ID 与 Group A/B/C 为虚构 | 不可引用为文献或材料排名 |
| 组合图颜色和 A/B 名称暗示跨技术同一试样 | 声明各模型的本地标签及实际依赖，组合不表示相互佐证 | 不可借布局推断一组电解液的机制 |
| 三个 recipe 的参考图来自另一组图库数据 | 用每个包自身 CSV/config 渲染 PNG/SVG/PDF，保留实际 artist 数组和 input/model/config/image hashes | “包里图与包里数据一致”可验证，非科学结论认证 |

## 2. 两类容量模型必须分清

### 2.1 独立全电池 recipe：有限库存的受限教学例

记循环前可循环库存为 `L_(n-1)`，设可回收份额 `eta_n`：

```text
eta_n = 1 - loss_ss - loss_tr*exp(-(n-1)/tau_cycles)
Qcharge_n = L_(n-1)
Qdischarge_n = eta_n*Qcharge_n
L_n = Qdischarge_n
loss_n = Qcharge_n - Qdischarge_n
CE_n = 100*Qdischarge_n/Qcharge_n
```

在这组特定假设下 `L_n/L_0 = product(eta_1...eta_n)`。没有额外锂库存、没有电极补偿、没有活性材料损失或可逆自放电，才会成立。**不能拿这条关系拒绝不符合累乘关系的真实作者数据。**

三包之一的 `full_cell` 演示为 A/B 各 40 周，170/164 mAh g⁻¹ 起始库存，2.9–4.2 V。数值均为自定；质量基准声明为正极活性材料质量。没有宣称这是 NMC811/石墨实测。

### 2.2 图库旧 ID `full_cell`：有额外锂的 NMC811‖Li 半电池教学例

```text
a_n = (1-a0*exp(-(n-1)/tau_a))
      *exp(-k*(n-1)-k_late*max(n-n_late,0)^2)
Qdis_n = Q0*a_n
eta_n = 1-loss_ss-loss_tr*exp(-(n-1)/tau_CE)
Qcharge_n = Qdis_n/eta_n
side_charge_n = Qcharge_n-Qdis_n
```

`a_n` 是选择的可达活性份额，不由 CE 乘积推导。半电池反电极有额外锂，所以本例不施加有限锂瓶颈。A/B 各 500 周；图库配置 2.8–4.3 V，关联的 `voltage_profiles.csv`、`gcd_profiles`、`style_presets` 取同一状态。

两套数据窗口、容量账本和配置互不替换。旧 `full_cell` ID 的保留是兼容措施，不能被解释成同一全电池。

## 3. 其他模型的具体边界

### Li‖Cu、Li‖Li 与 Aurbach

- Li‖Cu：`CE = 100*Qstrip/Qplate`；`Q = abs(j)*duration_h`。每半周 1 mAh cm⁻² / 1 mA cm⁻²，剥离终点 1 V。选择的 `eta(n)` 与电压形状不证明死锂、SEI 或全电池寿命。
- Li‖Li：`V = j*Rs + eta_RC`，`d eta_RC/dt = (j*Rp-eta_RC)/tau`。A/B 库图各 200 h、10,001 个唯一时间点，测试用零阶保持积分电流，并独立回算每次切换的 RC 状态。没有把对称电池曲线当 CE 测量。
- Aurbach：先 conditioning，再 2 mAh cm⁻² reservoir，10 次 0.25 mAh cm⁻² 的剥离/沉积对，最后回收剩余 active。选择沉积可回收率 0.995，最后剥离 1.9775 mAh cm⁻²；`CE = (n*Qc + Qfinal)/(n*Qc + Qreservoir) = 99.5%`。conditioning 在该计算之外，未套用论文数值。原文章正文的 Fig. 4b 指针与 Fig. 4c 图注不一致，来源注明按图注与 Methods 核对。

### EIS、短暂电流与 OCV

```text
omega = 2*pi*f
ZW = sigma*(1-j)/sqrt(omega)
Y_CPE = Q*(j*omega)^alpha
Z = Rs + 1/(Y_CPE + 1/(Rct+ZW))
```

频率必须大于零，`Rs>=0`，`Rct/Q>0`，`0<alpha<=1`，`sigma>=0`。Nyquist 用 `Re(Z), -Im(Z)`，Bode 相位用有符号 `arg(Z)`。CPE 的 Q 单位为 `S*s^alpha`，只有 alpha=1 时才可按理想电容理解。`eis_frequency` 为理想 RC 的独立教学例；极限测试检查半圆方程。

`chronoamperometry` 为有稳态电阻项的单个 RC 电流暂态并写入解析积分电量；没有用它声称成核、沉积质量或材料机制。`ocv_rest` 为两个有限指数松弛项，去掉无限线性下降；没有由电压降反推自放电容量。

### 衍射、表面场、倍率、热

- XRD：`2*d*sin(theta)=lambda`，波长 1.5406 Å，两个独立虚构 d。库图为 105×240 网格，recipe 为自身较小网格；非负强度的完整显示范围按实际数据设置。旧 `soc_fraction` 列兼容保留，含义被限定为 chosen progress。
- ToF-SIMS：3 通道、72×72 场，20×20 µm，保存图为 30 s，曲线在同一 30 s 点取图均值。缺少 matrix/yield/sputter-rate 标定，因此是明确标识的版式数据，不是定量成分模型。
- 倍率：`Qaccessible = Q0*exp(-k*n)/(1+(rate/r_limit)^0.8)`，0.2/0.5/1/2/5/0.2 C 每段十周。回到低倍率只恢复可达份额，不凭空多一项容量奖励。
- 热节点：`Cnode*dT/dt=Pnode-Gnode*(T-Tamb)`；每节点等权，`Ctotal=0.1 kg*900 J kg⁻¹ K⁻¹=90 J/K`，`Gtotal=1/6 W/K`，`tau=540 s`。空间功率为选择的非负函数，温度图、线扫描和 history 取同一场。无侧向传热、电热耦合、热失控或测量声称。

## 4. 18 个核心 ID 的交付范围

| 分组 | ID | 模型记录 |
| --- | --- | --- |
| 容量/电化学 | `full_cell`, `li_cu_ce`, `li_li`, `eis`, `rate_capability` | 方程、参数、假设、定义来源、适用范围 |
| 结构/表面/热 | `operando_xrd`, `tof_sims`, `pouch_thermal` | 同上；ToF-SIMS 明确仅 layout fixture |
| 组合或同数据显示 | `integrated_study`, `gcd_profiles`, `capability_spread`, `style_presets` | 依赖 ID、来源文件、不得跨技术推断的边界 |
| 文献/报告版式 | `literature_benchmark`, `reporting_matrix` | 虚构 ID 与类别；非真实文献审核 |
| 附加电化学 | `aurbach_protocol`, `eis_frequency`, `chronoamperometry`, `ocv_rest` | 原创账本/被动电路/松弛方程及局限 |

三 recipe 和全部 18 个 metadata 模板包含 `scientific_basis`。字段包括 `model_class`、`data_origin`、`parameter_origin`、`equations`、`assumptions`、`parameters`、`references`、`limitations`、`validation_scope`；原始数值来源均为 self-chosen，不冒充论文测量。

`capability_spread` 的实际输入恰为十个邻接 CSV：XRD、半电池容量、LiCu CE、EIS、文献版式、热历史、LiLi、倍率、GCD、报告版式。其 `source_files` 与 `dependency_ids` 已相互核对；没有把未读取的 ToF-SIMS 加入该组合图。

## 5. 独立绘图包的参考图闭环

构建脚本只使用本包自己的 `config.demo.json` 和 `demo/*.csv` 渲染参考图。新增/更新生成物包括：

- `demo/model.json`：本包自身模型记录。
- `reference/figure.png/.svg/.pdf`：同数据生成的图件。
- `reference/data_checks.json`：实际输入记录、完整 artist 数组、四边框与配色记录；过滤内部环境路径。
- `reference/metadata.json`：相同模型与单位/工况，来源文件指向自身 CSV/config/model/检查记录。
- `sources.json`：input CSV、config、model、参考图 SHA256；`reference_origin` 明确不是拷贝图库。
- `VERSION.json`、README、AGENT_GUIDE、input_contract：来源/状态、作者输入与原创教学模型分离；native/model eval 保留 NOT_RUN。

作者输入仍由独立单位、列名、质量/面积基准和必要条件检查处理。未做静默平滑、补点、换入演示数据或覆盖输出。两种容量模型的 CE 关系不进入作者数据接受规则。

## 6. 回算与显示检查

运行命令（从公开工程根目录，用项目 QA venv）：

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& 'outputs/qa-venv/Scripts/python.exe' 'tests/test_synthetic_core_physics.py' --report 'docs/validation/2026-10-01-scientific-core.json'
```

18 项测试全部在系统临时目录生成独立 fixture 与三包参考图，其中一项真实运行四条可选电化学的生成与渲染。测试不会调用正式目录的 `all`/publish 或覆盖网站 served 资产。报告记录逐项 PASS/FAIL、具体点数/参数/限制、生成器、实际渲染器与测试 SHA256；源文件再修改后必须重跑，以报告 hash 为准。

| 检查 | 关键断言 |
| --- | --- |
| 全电池 2×40 周库存 | Qcharge/Qdis/loss/CE 与库存恒等式；累乘范围仅教学例 |
| 半电池 2×500 周 | 独立可达活性和 charge/CE 账本，容量不被 CE 累乘绑定 |
| 电压/容量关联 | 库图 2.8–4.3 V 与独立 recipe 2.9–4.2 V 各自端点及容量匹配 |
| LiCu 300 周，2×3 条 profile | 1/100/300 周电流时间积分、CE、Qstrip 和 1 V 终点 |
| LiLi 2×200 h | 10,001 点单调唯一时间；所有切换 RC 左右状态一致 |
| EIS 被动与理想极限 | 宽频边界、复阻抗符号、RC 半圆恒等式 |
| EIS CSV 联动 | 存储实/虚部与同一解析电路，不另画 Bode |
| XRD Bragg 与网格 | d/角度反算、峰方向、105×240 无重复坐标与非负强度 |
| ToF-SIMS | 同场 30 s 均值、非负、色标/曲线完整显示 |
| 倍率 | 全 60 周可逆份额/衰减公式、无任意恢复奖励、窗口端点 |
| Aurbach | 每阶段库存平衡、零阶保持积分、1.9775 最终量/99.5% 选择 CE |
| 电流暂态/OCV | 电量解析积分、OCV 有限长期极限 |
| 热 | C=m*cp、G/tau、热节点第一定律、图/线/history 相同 |
| 模型元数据 | 18 个 schema、source 文件闭合；十组合依赖恰好匹配 |
| 三包自身参考图 | 输入 hash、schema、实际 artist 数组/颜色/边框，与自身数据相同 |
| 四条可选电化学真实渲染 | generate/render 全四路输出 PNG/SVG/PDF/alignment/actual_artist_checks；六种不完整/非法 source 清单必须停止 |
| 已受影响的 6 种曲线图 | 数据在图轴内；四边框、连续实线、无 marker |
| 无效参数 | 已知 demo 函数拒绝 NaN/inf、无效 CE/RC/frequency/Bragg 等十种输入 |

首次回算过程中抓出了构建层两个错误（质量基准字符串缺 mass、检查记录目录取错），以及测试层对 QuadMesh/axvline 的错误假设。修复后重跑，不将这些中间失败隐藏成首轮成功。

### 6.1 实际集成暴露的契约问题

初版 17 项回算检查只生成四个可选电化学输入及 metadata，没有实际执行它们的渲染。因此该版 PASS **未覆盖四路真实渲染的集成风险**。

主任务总生成调用 `examples/showcase/electrochem.py all` 时，Aurbach 被旧渲染器拒绝：旧 `_metadata` 要求整个 `source_files` 等于 `['data.csv']`，而新生成器诚实地列出 `['data.csv','protocol.json']`。这不是缺少 CSV；是旧契约误拒绝额外的真实库存账本。

修复位于 `skills/battery-review-figure/scripts/batteryplot/electrochem.py`。保留 `data.csv` 必须项，仅 Aurbach 可额外声明 `protocol.json`，每项要求真实文件、唯一、局限于输入目录；其他三路仍仅允许 `data.csv`。没有删除数据门槛或隐藏库存来源。新增的第 18 项执行四路 generate/render，并用六组空清单、缺必须 CSV、重复、越目录、未知项、缺 sidecar 的负例回归。

经主任务授权，实际公开示例目录执行一次 `electrochem.py all`，用时 8.197 s、exit 0，四路均成功：

```text
all aurbach_protocol
all eis_frequency
all chronoamperometry
all ocv_rest
```

这次实际运行重建了这四个当前示例的 CSV/metadata/图和报告，没有发布到正式网站。不能把旧版隔离回算的 PASS 替代此次真实集成的结果。

**未验证项**：真实实验、具体材料性能、所有原生桌面与模型行为、独立人工视觉审阅。四边框、无虚线/点和坐标不截值只代表本项目显示约束；不宣称通用期刊认证。

## 7. 核对过的定义来源

每条来源只支持模型或解释边界。原始教学参数没有摘取论文结果，也没有拷贝第三方图件。

- [Gamry：EIS 基础](https://www.gamry.com/application-notes/EIS/basics-of-electrochemical-impedance-spectroscopy/)：复阻抗、被动 RC、CPE 与 Warburg 的定义。
- [IUCr：Bragg 定律](https://dictionary.iucr.org/Bragg%27s_law)：波长、d 间距与衍射角关系。
- [Nature Energy：Understanding and applying coulombic efficiency in lithium metal batteries](https://www.nature.com/articles/s41560-020-0648-z)：CE 协议及电池配置的解释边界。
- [Nature Communications：Deciphering coulombic loss in lithium-ion batteries and beyond](https://www.nature.com/articles/s41467-025-60833-y)：库伦损失与容量损失不具有普遍等价性。
- [Nature Communications：Aurbach 版式与协议来源](https://www.nature.com/articles/s41467-025-66197-7)：核对 Fig. 4c 图注与 Methods；不用论文性能数值。
- [NPL：Secondary ion mass spectrometry](https://www.npl.co.uk/research/mass-spectrometry/secondary-ion)：matrix effect、定量/标定边界。
- [OpenStax：Heat Transfer, Specific Heat, and Calorimetry](https://openstax.org/books/university-physics-volume-2/pages/1-4-heat-transfer-specific-heat-and-calorimetry) 与 [Mechanisms of Heat Transfer](https://openstax.org/books/university-physics-volume-2/pages/1-6-mechanisms-of-heat-transfer)：热容与线性热导的定义。旧简略 URL 无法打开，已改为正确页面。
- [Nature Chemistry：Reporting standards](https://www.nature.com/nchem/editorial-policies/reporting-standards)：来源/数据/方法披露需求，不能为编造记录提供真实性。

## 8. 接下来由主任务完成的集成

初次交付未生成正式库图。主任务发现上述集成失败后，本子任务按授权仅重建四个当前电化学示例；没有修改网站 served 资产或做总包/版本/commit/push。旧 0.10.1 历史保留。主任务按新的生成器重建当前 0.10.2 Beta，更新三 recipe 与 Starter/源码镜像，再执行全体资源和网站检查。

`integrated_study` 是六面板，模板文本从误写的 eight 改为 six；主任务的八面板 frontpage 是另一份图，不能一起改成六面板。已启动的生成进程可能持有旧变量，请在集成末尾单独 render `integrated_study` 刷新 metadata。

需要同步到网站的语义：

1. 图库旧 `full_cell` 是半电池，独立全电池 recipe 是另一组受限教学数据。
2. XRD 进度不能宣传为实测 SOC；热图不能宣传为从 2 C 电流计算的电芯热图。
3. `integrated_study` 的 A/B 是本地模型标签，不能写同一电解液跨技术证据。
4. `literature_benchmark`/`reporting_matrix`/ToF-SIMS 版式 fixture 不能被表述为真实文献/实验定量。
5. 参考图核验使用 recipe 自身 sources/CSV/config/模型/artist hashes，不再强制等于图库另一组图片。
6. GitHub 同步与上海 ECS 正式站发布是两件事；本轮按最新要求留在本机，部署需由主任务按当前维护文档处理。
