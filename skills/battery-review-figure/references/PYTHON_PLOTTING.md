# BatteryReviewForge Python plotting library

The bundled `scripts/batteryplot` package uses Matplotlib. It is an original implementation for battery Review and Perspective figures. It keeps an individual figure's code, input table, outputs and provenance close together in the manuscript project. It does not ship paper data or copy third-party artwork. For ordinary author uploads, start with [the CSV/XLSX guide](UPLOADED_DATA.md) and `scripts/plot_uploaded.py`; custom Python is optional.

## Install and import

Install Python 3.10+ and the small requirements file in the plotting environment. Matplotlib makes the plots; openpyxl reads XLSX; python-pptx counts slides in private asset inventories. No Pandas, Seaborn, paid database or network service is needed. Set `PYTHONPATH` to the installed skill's `scripts` directory, or add that directory to `sys.path` in the figure script:

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path("<installed-skill>/scripts").resolve()))
from batteryplot import read_csv, cycle_retention, save_bundle

rows = read_csv("data/cycle_retention.csv")
fig, ax = cycle_retention(rows, style="journal_minimal")
save_bundle(fig, "figures/cycle_retention", claim="A specific, source-supported conclusion",
            source_data="data/cycle_retention.csv",
            caption_notes="Define cells, conditions, normalization and uncertainty here.", close=True)
```

For a runnable synthetic check from the repository root:

```bash
python skills/battery-review-figure/examples/demo_figures.py --output outputs/figure-demo
```

The example data are invented and must never be used as literature evidence.

## Choose a chart

| Function | Input shape | Scientific gate |
| --- | --- | --- |
| `cycle_retention(rows)` | One row per cycle and series | Requires cycle, retention %, verified source, and identical direct-comparison context |
| `rate_capability(rows)` | One row per test step and series | Preserves test order and recovery steps; requires matching step/rate sequences and capacity units |
| `comparison_bars(rows, metric_label=...)` | One row per category | Starts at zero; refuses unlike declared test conditions and undefined uncertainty |
| `conditions_matrix(rows, fields)` | One row per paper or case | Shows reported (`R`), `NR`, and `NV` as distinct states; never interprets blank as zero |
| `coulombic_efficiency(rows)` | One row per cycle and series | Requires a CE definition and supplied CE or explicit numerator/denominator; never caps >100% values silently |
| `cycling_capacity(rows, cell_configuration="full" or "half")` | One row per cycle and series | Rejects mixed full/half cell rows; labels the capacity unit and requires a stated basis |
| `symmetric_voltage(rows)` | Signed mV vs elapsed hours | Requires symmetric cell configuration, current density, areal capacity and pressure; retains polarity and failure region |
| `voltage_capacity(rows)` | Charge/discharge profile points | Keeps cycle and direction separate, requires voltage and capacity units/basis |
| `nyquist(rows)` | Real impedance and explicit positive negative-imaginary column | Requires cell state and frequency range; does not silently flip raw impedance sign |

All quantitative rows require `source_id` and `evidence_state=verified`. A source ID is a DOI, stable paper ID or locally resolvable bibliography key. This is an author-supplied declaration; inspect the actual source and DOI with the claim/citation skills. Required numeric fields must be finite. Keep the raw input unchanged; calculate normalization in a separate, documented step.

### Context fields

These are deliberately strict defaults. Supply each field for every quantitative row; use exact units and controlled labels within a project. A direct comparison requires identical values in these fields, but equality alone does not prove comparability.

| Chart | Context fields |
| --- | --- |
| Cycle retention | `chemistry`, `cell_configuration`, `retention_basis`, `rate`, `temperature_c`, `loading_mg_cm2`, `electrolyte_ul_mg` |
| Rate capability | `chemistry`, `cell_configuration`, `capacity_basis`, `temperature_c`, `loading_mg_cm2`, `electrolyte_ul_mg` |
| Comparison bars | `chemistry`, `cell_configuration`, `metric_basis`, `rate`, `temperature_c`, `loading_mg_cm2`, `electrolyte_ul_mg` |

For solid-state, lithium-sulfur, aqueous zinc, sodium-ion, flow batteries and full-cell energy comparisons, add claim-specific conditions to the figure ledger and caption: pressure, sulfur loading, E/S, N/P, depth of discharge, zinc excess, areal capacity, power basis, stack boundary, etc. The fixed API cannot know every chemistry's decisive factor. A paper with a different normalization or cell boundary should be separated even if the listed defaults happen to match. Do not fabricate a numeric value to satisfy a field; use a conditions matrix when values are `NR` or `NV`.

The specialized chart functions additionally check the fields defined beside them in `batteryplot/battery_charts.py`. For a **direct comparison of multiple series or source IDs**, every chart-specific condition field must be declared in every row and match; if a field was not reported, use a conditions matrix or a `contextual` plot with an explicit limitation note. A matching declaration is a screening result, not independent verification. Their input files retain row order: a backwards time/capacity axis is a data issue to review, not something to hide by automatic sorting. For CE, distinguish full-cell discharge/charge from metal stripping/plating definitions. For full-cell capacity, name whether mass refers to cathode, anode, both active materials or a complete cell. A symmetric-cell voltage trace does not measure a full cell's energy density.

`cycle_retention`, `rate_capability` and the specialized charts accept `mode="contextual", condition_note="..."` for descriptive overlays with different or insufficiently known conditions. A limitation banner is printed on the figure and the contextual state is written to provenance. The author must still state the limits in the caption. `comparison_bars` intentionally has no contextual override.

## Plot package and delivery contract

Suggested project layout:

```text
figures/fig03_cycle/
  data/cycle_retention.csv
  plot.py
  fig03_cycle.pdf
  fig03_cycle.svg
  fig03_cycle.png
  fig03_cycle.provenance.json
  caption.md
```

The PDF and SVG are vector masters with editable text where supported. PNG/TIFF uses at least 300 dpi; DPI does not apply to pure vector marks. The default canvas is 89 mm wide. Change `width_mm`/`height_mm` for the target journal and inspect the exported figure at that final size. The sidecar records the claim, data path, source IDs, row count, comparison mode and caption notes. It says `requires_human_review` because the package cannot determine whether a paper's numbers, statistics, licenses or journal rules are correct.

All chart helpers accept a `style` code from [STYLE_PRESETS.md](STYLE_PRESETS.md). When using the author-upload CLI, `style` is required in its mapping JSON so the choice is recorded in the provenance sidecar. Programmatic calls retain `forge` as a backward-compatible default; manuscript-facing scripts should pass the selected style explicitly. Original editable SVG templates use the same presets through `scripts/render_template.py`.

Before release, check the exported figure, caption and source data together: all requested observations remain; `n` and error-bar definition are supplied when relevant; legends, symbols, scales, axes, type and line widths are readable; raster inserts have adequate effective resolution; and every reused visual has a recorded license/permission. For multi-panel figures, check final rendered alignment and collisions after layout, not just Python source. Verify the target journal's current author guide for exact dimensions and formats.

## Design provenance

The library was informed by the reproducible per-project organization and publication plotting conventions demonstrated in [Chen Liu's figures4papers](https://github.com/ChenLiu-1996/figures4papers). That repository's [CC BY-NC 4.0 license](https://github.com/ChenLiu-1996/figures4papers/blob/main/LICENSE) is distinct from this project's MIT license. No upstream scripts, numerical data, images or palette constants are included here. The library code and synthetic example are original to BatteryReviewForge.

## 中文速用

在已安装 Matplotlib 的 Python 环境中，将 `battery-review-figure/scripts` 加入 `PYTHONPATH`，从 `batteryplot` 导入所需函数。每个定量数据行都填 `source_id`、`evidence_state=verified` 和该图型要求的测试条件；`NR`、`NV` 只用于条件矩阵，不能拿来代替定量数值。跨论文比较先检查分母、电芯构型、倍率、温度、载量和液量，再按具体体系补充压力、E/S、N/P 等关键条件。函数通过校验不代表论文证据已经核实。

用 `save_bundle` 导出 PDF、SVG、PNG 与 `.provenance.json`，在目标期刊的最终尺寸下检查字体、标注、颜色、误差线和面板对齐。`examples/demo_figures.py` 只含虚构测试数据，不能用于论文。完整接口与字段见上表。
