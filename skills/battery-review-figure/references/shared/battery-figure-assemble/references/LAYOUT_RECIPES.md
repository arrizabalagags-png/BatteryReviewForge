# 拼图排版速查：先选证据主次，再填毫米网格

这不是期刊模板。不同类型的面板先按 [Figure Director](EDITORIAL_COMPOSITION.md) 确定谁是主角、谁是辅证、读者怎样走，再到这里选毫米网格。先按目标期刊当期要求确定整图宽度，再把下面的数值当作起点。面板太多、字太小或比例尺看不清时，拆成两张图；不要一味缩小。

| 你手里有什么 | 推荐起点 | 这样安排的理由 |
| --- | --- | --- |
| 2 张同类循环/CE/阻抗图 | 一行两列，等宽等高 | 并列条件一眼可比；两图的**实际绘图区**还要对齐 |
| 1 张流程或机理总图 + 2 张定量图 | 上方通栏、下方两列 | 先交代体系，再给两项不同证据；总图不能替代数据 |
| 2 张定量图 + 2 张显微图 | 两行两列，同类型同一行 | 坐标图共用阅读节奏，显微图保留独立比例尺与采集条件 |
| 3 张或更多谱图/曲线 | 同宽纵排，或按条件分组 | 避免把小图塞到无法读字；同组可用同一坐标范围 |
| 一张重要主图 + 多张辅助图 | 主图占整行或一侧大块，辅助图等宽 | 主图承担核心判断；辅助图分别承担条件/机理/验证 |

**通用起点：**双栏整图可先试 180 mm 宽、外边距 4 mm、面板间距 2–3 mm、字母带 4–5 mm。实际期刊若用 89 mm 单栏或别的宽度，就先改整图宽度再重算字体和刻度。字母放同一位置；每个面板的轴、图例和比例尺都应留在它自己的清楚边界内。不要用白框遮住旧标签。

## 三面板：总图 + 两项验证

在 `compose_figure.py` 的 manifest 中，以下网格会把 `a` 放在上方通栏，`b`、`c` 放在下方等宽。路径、来源、权限和每张图的职责须由作者实际资料填写。

```json
{
  "width_mm": 180,
  "margin_mm": 4,
  "gutter_mm": 2.5,
  "label_band_mm": 4.5,
  "row_heights_mm": [45, 52],
  "col_weights": [1, 1],
  "panels": [
    {"label": "a", "row": 0, "col": 0, "colspan": 2},
    {"label": "b", "row": 1, "col": 0},
    {"label": "c", "row": 1, "col": 1}
  ]
}
```

这是**网格片段**，不是可直接执行的完整 manifest。完整版本还要 `version`、`figure_id`、`claim`、`dpi`，每个 panel 的 `path`、`role`、`source_id`、`rights_status` 等字段；见 [完整示例](COMPOSITION.md#manifest-contract)。

## 拼完后逐项检查

1. 看整图：阅读顺序是否能用一句话说明，各面板字号、线宽、底色和图例是否协调。一个颜色在同一图中只表达同一对象或含义。
2. 看对齐叠加图：红框是槽位，蓝框是实际放入的图，绿框是声明的绘图区。定量图真正的坐标轴边界应齐，不是只有图片外框齐。
3. 看逐面板检查图：字母、误差棒、比例尺、截断符号和角落文字有没有被压住。显微图不能为了配色而改写强度或伪造颜色含义。
4. 看 QA JSON：有效 DPI、空白边和 `font_audit`。小于 6 pt 的提取到的矢量文字会被标为复核线索；栅格字和转曲字无法自动测量。最终仍在投稿尺寸看 PDF。
5. 若有不齐，先从原始数据/可编辑图重出同尺寸单面板，再重新拼版；只有科学上合理且记录了原因时才裁剪。

## English

Choose the grid from the figure's evidence sequence: equal slots for direct peer comparisons, a full-width overview above distinct validation panels, or same-type panels grouped together. The values above are provisional physical dimensions. Inspect the final-size composite, actual plot boxes, panel crops and font audit; rerender editable sources when scaling makes text illegible.
