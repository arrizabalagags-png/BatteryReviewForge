# 把电池数据文件变成图

在当前 AI 软件中提供原始或整理好的 CSV、TSV、TXT、XLSX 文件，并说清“这是什么电芯、想画什么、图给谁看”。用户不用自己写 Matplotlib 或 JSON；Agent 按文件与作者已确认的信息生成映射。缺条件时先指出缺什么；不能从文件名猜成论文结论。

先读本页，仅按当前任务补读引用：需要 Working 交付时读[交付指南](DELIVERY.md)，尚未选配色时读[风格预览](STYLE_PRESETS.md)，有专门图型/科学接口问题时读[绘图库说明](PYTHON_PLOTTING.md)的相关部分。不要无差别翻全部模板、所有图型和完整绘图脚本；本页未覆盖或字段互相矛盾时再查对应实现，不能跳过科学检查。

## 最短路径

在当前项目的隔离虚拟环境中，切换到已安装的绘图 Skill 目录，安装一次它自带的依赖：

```bash
python -m pip install -r requirements.txt
```

先看文件里有哪些列：

```bash
python scripts/plot_uploaded.py inspect --data my_data.xlsx --sheet Sheet1
```

若工作簿只有一张表，可省略 `--sheet`。脚本显示列名、前三行和可能的图型；候选只说明列形状相符，不代表数据、单位或实验条件正确。候选列表为空也不代表任务不支持：若作者已明确图型，按真实字段含义确认分组、横轴、数值及单位，再建立标准列→原始列的映射；不能凭列名猜科学含义。准备并核对映射后再画。

作者本次已选配色或稿件已有选择时，直接把该 `style` 写入映射，沿用身份与颜色，不再运行 `styles`、重读全部预览或重复让作者选择。尚未选过时，再看[六种风格预览](STYLE_PRESETS.md)让作者选一套；也可用 `python scripts/plot_uploaded.py styles` 列出。没有选择时继续查列和条件，绘图命令会明确报错而不会猜默认风格。

```bash
python scripts/plot_uploaded.py plot --data my_data.xlsx --metadata my_figure.json --out figures/Fig2a
```

输出 PDF、SVG、300 dpi PNG 和 `.provenance.json`。CSV、TSV、TXT 同样可用。旧版 XLS、Origin 工程、各品牌仪器专有格式须先导出可读表；不要假装已解析其内部结构。

## 实际配置参数

映射 JSON 只接受以下顶层键，未知键会在读取数据或写出图件之前报错：`kind`、`style`、`community_style_lock`、`sheet`、`columns`、`common`、`mode`、`condition_note`、`width_mm`、`height_mm`、`sample_id`、`fragment`、`claim`、`caption_notes`。并非每种图都用到所有字段：`sample_id`/`fragment` 用于 ToF-SIMS；`community_style_lock` 用于显式选定的社区风格。

物理尺寸分别写 `width_mm` 与 `height_mm`，例如 `"width_mm": 89, "height_mm": 65`；不支持 `figure_size_mm`。位图 DPI 使用命令行参数，不放入映射 JSON：

```bash
python scripts/plot_uploaded.py plot --data my_data.csv --metadata my_figure.json --out figures/Fig2a --dpi 600
```

`deliver.py` 也使用同一映射规则；它的 `--dpi`、`--png-dpi`、`--tiff-dpi` 是导出参数，见[交付指南](DELIVERY.md)。尺寸和 DPI 不能补齐缺失的科学信息。

## 映射文件示例：库伦效率

### CE 最小核对清单

- 每行数据：`series`、非负且按原始顺序的 `cycle`，以及百分数 `ce_pct`；或者同一面板全部用 `ce_numerator`/`ce_denominator`。不能混用现成值与重算值；分母为正、分子非负，两列计量基准一致。
- 每行来源与基本条件：`source_id`、作者实际核查后的 `evidence_state=verified`、`chemistry`、`cell_configuration`、`temperature_c`、`ce_definition`、`rate`。相同信息可写进 `common`；不同信息放回各行。
- 多样品或跨来源的 `direct` 比较，还需各行声明并一致：`current_density_ma_cm2`、`areal_capacity_mah_cm2`、`cutoff_rule`、`ce_protocol`、`loading_mg_cm2`、`electrolyte_ul_mg`、`voltage_window_v`。单样品中已提供的这些条件也须完整、一致；缺或不一致按下文比较规则处理。
- 声明确实不适用才用 `NA`，不能把未知值填成 `NA`；`NR`/`NV`规则保持。按真实金属沉积/剥离或全电池充放电测试写 CE 定义；Aurbach 协议平均值不是逐圈 CE 输入。
- 用原值画图，保留高于100%的异常并提示回查。超出程序有效范围时停止核查，不能裁剪成可画范围。补齐这些字段只满足输入核查，不认证真实实验或来源。

必需信息同时缺失时，列出当前图型和比较范围真正缺少的项，要求全部补齐并核查后再出图；不能写“任一项补齐即可”。`direct` 比较缺少可比性条件时停止直接排名；只有作者明确改成允许的语境展示并能满足该模式的核心合同，才可走 `contextual` 路线，不能用它绕过来源、CE 定义、单位或基本条件。

下面的占位示例只说明字段写法，不能直接运行；每个占位值须换成真实文件与作者核查的信息。不要复制出示例实验参数，也不要未经核查填 `verified`。A/B 多样品直接比较还需要上面的相关协议字段。

```json
{
  "kind": "coulombic_efficiency",
  "style": "rose_blue",
  "claim": "A 与 B 的库伦效率变化",
  "caption_notes": "说明电芯、分子/分母、测试倍率、温度、圈数和异常点。",
  "columns": {
    "series": "Sample",
    "cycle": "Cycle Index",
    "ce_pct": "CE (%)"
  },
  "common": {
    "source_id": "<作者提供并已核查的来源ID>",
    "evidence_state": "<实际核查状态；核查完成才写verified>",
    "chemistry": "<实际体系>",
    "cell_configuration": "<实际电芯构型>",
    "ce_definition": "<实际分子/分母与测试定义>",
    "rate": "<实际倍率或电流密度及单位>",
    "temperature_c": "<实际测试温度>"
  }
}
```

`columns` 的左边是绘图工具的标准字段，右边是作者文件里的列名。`common` 给所有行补相同实验信息；若样品条件不同，请把条件放到数据行，不要用同一个值盖过去。CSV 表中已有标准列时，`columns` 可留空。所有数字行都须有可追溯的 `source_id` 和作者已核的 `evidence_state=verified`。文件上传本身不等于核实。

`common` 可省略的前提是数据行已经提供该图型所需的来源、作者核查状态与实验条件；它不是绕过这些必填信息的开关。缺失 `source_id`/`evidence_state` 或关键工况时应先停，列映射、单位和 CE 定义齐全仍不代表可出图。不得为通过程序随手填 `verified` 或虚构共同条件。

如果没有现成的 `ce_pct`，把两列映射为 `ce_numerator` 与 `ce_denominator`；脚本按 `100 × 分子 / 分母` 计算。必须写 `ce_definition`，比如金属沉积/剥离实验的“剥离容量 / 沉积容量”，或某个全电池测试定义的“放电容量 / 充电容量”。不要把两者混用。CE 高于 100% 的点不会被自动压成 100%，需回查源数据和定义。

## 选图与必须说明的条件

| 想展示什么 | `kind` | 最少数据列 | 不可省略的说明 |
| --- | --- | --- | --- |
| 库伦效率 | `coulombic_efficiency` | `series, cycle, ce_pct`，或分子/分母两列 | CE 定义、电芯、倍率/电流密度、温度、容量基准 |
| 全电池循环容量 | `full_cell_cycling` | `series, cycle, discharge_capacity` | 正负极、容量分母、N/P、载量、液量、电压范围、倍率 |
| 半电池循环容量 | `half_cell_cycling` | 同上 | 工作电极与对/参比金属、容量分母、载量、电压范围 |
| 对称电池电压 | `symmetric_cell_voltage` | `series, time_h, voltage_mv` | 两侧电极、正负极性、电流密度、每半周期面积容量、外加压力（若相关）、失效判据 |
| 充放电曲线 | `voltage_capacity` | `series, cycle, direction, capacity, voltage_v` | `charge/discharge` 方向、选取圈数、容量分母、电压范围 |
| EIS Nyquist | `nyquist` | `series, z_real_ohm, minus_z_imag_ohm` | 频率范围、SOC/循环状态、扰动幅值和拟合方式（如有） |
| 循环保持率 | `cycle_retention` | `series, cycle, retention_pct, reference_cycle` | 明确写出作为 100% 的参考圈；没有就先画原始容量，不能擅自算保持率 |
| 倍率性能 | `rate_capability` | `series, step, rate_label, capacity` | 实际测试顺序、恢复步骤、容量单位与分母 |
| ToF-SIMS 离子图 | `tofsims_map` | `sample_id, fragment, x_um, y_um, signal` | 像素坐标必须来自仪器标定；选择一个样品及碎片；提供离子极性、取样状态、信号单位、归一化方式 |
| ToF-SIMS 深度曲线 | `tofsims_depth` | `sample_id, fragment, sputter_time_s, signal` | 同一组碎片须有相同时间网格；横轴保持溅射时间，除非有独立坑深校准 |

标准字段的详细条件见 [绘图库说明](PYTHON_PLOTTING.md)。一个样品的原始曲线可以先做核查草图；要把多个样品画在同一坐标里做直接比较，还要让相关测试条件相同。多条样品曲线或跨不同 `source_id` 时，图型列出的相关条件即使在每份材料中都未填写，也不能当成“相同”；直接比较会被拦下。条件不同或信息不足时，可用 `mode: "contextual"` 加明确的 `condition_note` 展示背景，但不能据此给不同电芯直接排优劣。

`direct` 仅说明输入声明的条件通过一致性筛查；不认证文献真实性、独立核实或科学可比性。`NA` 是作者有理由确认“不适用”，`NR` 是查过可用完整来源后“未报告”，`NV` 是尚未核实或相关来源未读到，三者不能互换。不能用 `NA` 填未知值或定量数据；对缺失来源、核查状态或必填条件，也不能只改成 contextual 或补一句说明便继续。程序允许的背景展示仍须满足该图型的基础数据及来源合同。

仪器导出的多行表头、混合单位或带公式但无缓存值的工作簿，需要先另存为“第一行是唯一列名、每行一个观测”的表格；保留原始文件和转换说明。脚本不会悄悄跳过表头或把空格当零。

## ToF-SIMS 文件怎么交

导出 CSV/XLSX 后先用 `inspect` 看列。二维成像数据一行一个像素，提供 `x_um, y_um, signal, fragment, sample_id`；深度曲线一行一个时间点和碎片，提供 `sputter_time_s, signal, fragment, sample_id`。两者都需要 `source_id, evidence_state=verified, signal_unit, normalization, ion_polarity, measurement_state`，可放在表格列，也可把每行相同的值写在映射 JSON 的 `common` 中。`x_um/y_um` 应来自仪器或作者的像素尺度标定；不接受按图片宽度猜微米。映射 JSON 还需显式写 `kind`、`style`、`sample_id`；离子图另需 `fragment`。输出仍是 PDF/SVG/PNG 和来源记录。

画廊里的 [ToF-SIMS 样图](https://github.com/arrizabalagags-png/BatteryReviewForge/blob/79b4238a5a7dfc963bafc0aefacd2337f9795ba8/docs/assets/gallery/tofsims-demo.png) 是**完全虚构的数学示例**。其中的色斑不代表显微观察，曲线也不代表某种电解液；其 CSV 在画廊 `data/` 内。真实数据中不要把不同碎片的相对信号直接写成组分百分比，也不要把溅射秒数改标纳米而没有单独测得的坑深标定。[电池界面 ToF-SIMS 方法研究](https://www.nature.com/articles/s42004-025-01426-0) 讨论了溅射引起的形貌和层混合问题；[正极界面的成像与深度剖析实例](https://www.nature.com/articles/ncomms14589) 展示了化学图与时间剖面的互补用途。

## 交图前 30 秒检查

打开最终尺寸的 PNG 和矢量 PDF：单位是否在轴上、横轴是否按原始顺序、异常点是否保留、图例是否挡住曲线、线与字是否可读。库伦效率的放大纵轴必须明显显示刻度；对称电池保留正负电压与失败段；电压–容量图保留充放电方向和圈数。执行者内部核查 `.provenance.json` 的来源文件、哈希、图型和计算说明；正常最终回复只链接图件/预览，作者明确要求来源记录时再给对应文件，沿用作者的语言。图要拼在一起时交给 `battery-figure-assemble`。

## When this is used in English

Run `inspect` on the uploaded table, map source columns and scientific metadata in JSON, then run `plot`. The file extension determines how to read the table; the data columns and declared cell/test conditions determine the chart. No private reference assets or paper data are bundled.
Ask once for a named style before final plotting, or reuse the manuscript's recorded choice. `plot` requires `style` in the mapping JSON; use the `styles` command or [preview](STYLE_PRESETS.md) to see options.
If the author has already chosen a style, reuse it without rerunning `styles` or asking again. An empty `inspect` candidate list is not an unsupported-task verdict: confirm the known chart's scientific fields and map the actual headers. Read only references relevant to this task. Use the same strict CE/source/condition rules above; final result and requested provenance narratives follow the user's language.
When several required items are missing, request all genuinely missing items for this chart and comparison scope; never say that any single item is sufficient. A contextual presentation requires the author's explicit change of scope and its own valid core inputs; it cannot bypass provenance, units, CE definition or basic conditions.
