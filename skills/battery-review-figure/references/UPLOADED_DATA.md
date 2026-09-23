# 把电池数据文件变成图

给 Codex 原始或整理好的 CSV、TSV、TXT、XLSX 文件，并说清“这是什么电芯、想画什么、图给谁看”。不用自己写 Matplotlib，也不用手写下面的 JSON；Codex 会查列名并生成映射记录。缺条件时先指出缺什么；不能从文件名猜成论文结论。

## 最短路径

在仓库根目录安装一次依赖：

```bash
python -m pip install -r skills/battery-review-figure/requirements.txt
```

先看文件里有哪些列：

```bash
python skills/battery-review-figure/scripts/plot_uploaded.py inspect --data my_data.xlsx --sheet Sheet1
```

若工作簿只有一张表，可省略 `--sheet`。脚本显示列名、前三行和可能的图型；候选只说明列形状相符，不代表数据、单位或实验条件正确。准备一份 JSON 映射后再画：

画最终图前，看[六种风格预览](STYLE_PRESETS.md)并让作者选一套；如果整篇稿件已选过，就沿用。命令行也可列出风格：`python skills/battery-review-figure/scripts/plot_uploaded.py styles`。没有选择时继续查列和条件，绘图命令会明确报错而不会猜默认风格。

```bash
python skills/battery-review-figure/scripts/plot_uploaded.py plot --data my_data.xlsx --metadata my_figure.json --out figures/Fig2a
```

输出 PDF、SVG、300 dpi PNG 和 `.provenance.json`。CSV、TSV、TXT 同样可用。旧版 XLS、Origin 工程、各品牌仪器专有格式须先导出可读表；不要假装已解析其内部结构。

## 映射文件示例：库伦效率

这份示例只说明字段写法，`source_id`、`evidence_state` 和条件必须来自真实文件与作者核查。

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
    "source_id": "local:experiment-2026-001",
    "evidence_state": "verified",
    "chemistry": "Li metal",
    "cell_configuration": "half cell",
    "ce_definition": "stripped capacity / plated capacity",
    "rate": "1 mA cm-2",
    "temperature_c": "25",
    "loading_mg_cm2": "2",
    "electrolyte_ul_mg": "10",
    "voltage_window_v": "0-1"
  }
}
```

`columns` 的左边是绘图工具的标准字段，右边是作者文件里的列名。`common` 给所有行补相同实验信息；若样品条件不同，请把条件放到数据行，不要用同一个值盖过去。CSV 表中已有标准列时，`columns` 可留空。所有数字行都须有可追溯的 `source_id` 和作者已核的 `evidence_state=verified`。文件上传本身不等于核实。

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
| 循环保持率 | `cycle_retention` | `series, cycle, retention_pct` | 初始圈数和保持率分母 |
| 倍率性能 | `rate_capability` | `series, step, rate_label, capacity` | 实际测试顺序、恢复步骤、容量单位与分母 |

标准字段的详细条件见 [绘图库说明](PYTHON_PLOTTING.md)。一个样品的原始曲线可以先做核查草图；要把多个样品画在同一坐标里做直接比较，还要让相关测试条件相同。多条样品曲线或跨不同 `source_id` 时，图型列出的相关条件即使在每份材料中都未填写，也不能当成“相同”；直接比较会被拦下。条件不同或信息不足时，可用 `mode: "contextual"` 加明确的 `condition_note` 展示背景，但不能据此给不同电芯直接排优劣。

仪器导出的多行表头、混合单位或带公式但无缓存值的工作簿，需要先另存为“第一行是唯一列名、每行一个观测”的表格；保留原始文件和转换说明。脚本不会悄悄跳过表头或把空格当零。

## 交图前 30 秒检查

打开最终尺寸的 PNG 和矢量 PDF：单位是否在轴上、横轴是否按原始顺序、异常点是否保留、图例是否挡住曲线、线与字是否可读。库伦效率的放大纵轴必须明显显示刻度；对称电池保留正负电压与失败段；电压–容量图保留充放电方向和圈数。再看 `.provenance.json` 的来源文件、哈希、图型和计算说明。图要拼在一起时交给 `battery-figure-assemble`。

## When this is used in English

Run `inspect` on the uploaded table, map source columns and scientific metadata in JSON, then run `plot`. The file extension determines how to read the table; the data columns and declared cell/test conditions determine the chart. No private reference assets or paper data are bundled.
Ask once for a named style before final plotting, or reuse the manuscript's recorded choice. `plot` requires `style` in the mapping JSON; use the `styles` command or [preview](STYLE_PRESETS.md) to see options.
