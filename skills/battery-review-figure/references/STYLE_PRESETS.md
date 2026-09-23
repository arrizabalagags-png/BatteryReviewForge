# 选一套图的颜色风格

![Six original style previews made with invented values](../assets/style-preview.svg)

这张预览只用**虚构数值**展示线条、图例和配色，不是电池实验结果。具体颜色在 [figure_theme.json](../assets/figure_theme.json)，每套都有适合折线的深色序列和完整色卡。浅粉、浅蓝、浅黄主要作区域底色；细折线和小字要用对比度更高的颜色。

| 选择时说这个名字 | 适合的图 | 代码值 |
| --- | --- | --- |
| 深海蓝绿 | 通用电池综述、复杂多面板；默认库风格 | `forge` |
| 玫蓝渐层 | 两类电解液/策略对照、热图和层次较多的图 | `rose_blue` |
| 珊瑚冰蓝 | 温和的暖冷对照；背景大面积留白 | `peach_ice` |
| 暖冷对照 | 强调两组差异、温度或失效过程 | `thermal_balance` |
| 期刊极简 | 投稿尺寸较小、需要少色且信息密集的面板 | `journal_minimal` |
| 清晰对比 | 多条曲线、柱图、需要明显区分类别的图 | `crisp_contrast` |

**画图前问一句：**“你喜欢哪种风格？我可以先给你看六种预览。”若作者已给色号或选过项目风格，就沿用并把选择写到图的配置和来源记录。若作者授权“你来选”，按读者要区分的类别、彩色/灰度使用场景和投稿尺寸决定，并说明选择。颜色只表达预先声明的语义；同一个样品在各面板保持同色，另用线型/符号辅助区分。任何配色都不能替代图例、数据来源或测试条件。

截图中的三组配色在本库里分别是 `rose_blue`、`peach_ice` 和 `thermal_balance`。截图的浅色被保留为色卡/背景；定量线条采用对比更强的同色系颜色，以免缩到论文栏宽后消失。`journal_minimal` 和 `crisp_contrast` 则提供两种不同的论文量化图取向。预设不是任何期刊的官方规范；最终尺寸、字体和文件格式应以目标期刊当期要求及实际印样为准。

列出风格，再把 `style` 写进上传数据的映射 JSON：

```bash
python skills/battery-review-figure/scripts/plot_uploaded.py styles
```

```json
{"kind": "coulombic_efficiency", "style": "rose_blue", "claim": "..."}
```

原创 SVG 示意图库也可按同一风格重配色：

```bash
python skills/battery-review-figure/scripts/render_template.py --list
python skills/battery-review-figure/scripts/render_template.py \
  --template battery-lab-primitives --style rose_blue --out figures/lab.svg
```

重配色只处理本库原创 SVG 的颜色，不会碰作者的原始显微图、已发表图片或实验数值。`scripts/preview_styles.py --out path/style-preview` 可重新生成预览。

## English

Choose a named preset once per manuscript figure set. Record its code in plotting metadata; the CLI refuses to draw a final chart without that choice. The three warm/cool palettes preserve the user's supplied swatch families, while plotted lines use darker members for final-size contrast. Schematic recoloring applies only to this project's original editable SVGs.
