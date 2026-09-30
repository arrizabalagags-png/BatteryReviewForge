# 换成自己的数据

CSV、TSV、TXT、XLSX 都先检查表头。XLSX 多 Sheet 必须明确选择。列名不一样时由 AI 将真实表头映射到下表字段；映射不修改原数据。

| kind | 主要数据字段 | 科学说明入口 |
| --- | --- | --- |
| coulombic_efficiency | series、cycle、ce_pct，或 ce_numerator + ce_denominator | CE 定义、倍率、电池边界及实验条件 |
| full_cell_cycling / half_cell_cycling | series、cycle、discharge_capacity | 全/半电池、容量单位/归一化基准、倍率、电压窗口 |
| symmetric_cell_voltage | series、time_h、voltage_mv | 对称电池边界、电流密度、半周期面容量 |
| voltage_capacity | series、cycle、direction、capacity、voltage_v | 容量基准、单位、倍率、电压窗口 |
| nyquist | series、z_real_ohm、minus_z_imag_ohm | 状态、频率范围；明确负虚部，不擅自改符号 |
| cycle_retention | series、cycle、retention_pct、reference_cycle | 指定参考循环、归一化基准与实验条件 |
| rate_capability | series、step、rate_label、capacity、capacity_unit | 容量基准与真实测试顺序，包括恢复倍率 |
| tofsims_map | sample_id、fragment、x_um、y_um、signal | 标定完整网格、信号单位、极性、归一化和测试状态 |
| tofsims_depth | sample_id、fragment、sputter_time_s、signal | 信号单位、极性、归一化和测试状态；不虚构深度换算 |

所有定量图均须作者确认 `source_id` 与 `evidence_state=verified`，或将真实列映射到它们。verified 只表示作者声明，程序不能认证实验/证据真实。上表列的是主要字段，**不替代完整科学条件合同**；详情只需读 [上传绘图说明](skills/battery-review-figure/references/UPLOADED_DATA.md) 中当前图型的部分。

CE 的 `common` 至少需要 source_id、evidence_state、chemistry、cell_configuration、temperature_c、ce_definition、rate。多曲线或多来源直接对比还需完整声明电流密度、面容量、cutoff_rule、ce_protocol、载量、electrolyte_ul_mg、电压窗口等可比条件；数据表里不同的条件保留在各行，不用 common 盖掉。其他图型使用各自合同。确属不适用的字段由作者写 NA；NR 是已读材料未报告，NV 是未核验。不得把 NA 当 NR/NV，也不能把 NR/NV 改成猜值通过检查。direct 只检查已声明条件一致；不像条件的 contextual 图必须明示限制。

映射 JSON 使用现有14个键：kind、style、community_style_lock、sheet、columns、common、mode、condition_note、width_mm、height_mm、sample_id、fragment、claim、caption_notes。不要写 figure_size_mm 或 dpi；图尺寸用 width_mm / height_mm，分辨率用命令行 `--dpi`。科学正文和来源说明沿用用户语言；技术字段名保留。

选配色可运行 `python start.py styles`；已选好就直接记录 style，不重走选择。Demo 与 plot 都可加 `--style peach_ice` 等用户明确选择的配色；没有此参数时沿用映射的 style。明确改色时来源记录保留原映射配色、命令指定配色与实际配色，原 JSON 和数据不改。默认输出不覆盖旧版，不静默补条件或修改原值。完整 Figure 的3个专用 recipe 包仍独立提供。

## 两种宿主的薄适配

DSH：`<项目根>/.dsh/skills/battery-review-figure`。最近祖先存在 `.git` 时用该根，否则用打开的工作目录；安装器要求显式选择该根，避免装到错误位置。[官方技能发现](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/skills)。

Codex：`<项目>/.agents/skills/battery-review-figure`。标准 name/description frontmatter 共用，无绘图代码分支；原生发现另行验证。[官方技能目录](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。
