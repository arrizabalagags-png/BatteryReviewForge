# Battery figure resource library

This skill ships a small **original** and editable resource set:

- [figure_theme.json](../assets/figure_theme.json): shared ink, role colors, pastels and accessibility rules used by the Python chart package.
- [cell-boundaries.svg](../assets/original/cell-boundaries.svg): a full/half/symmetric cell boundary diagram. It is a layout starter, not a description of any actual experiment.
- [review-wheel.svg](../assets/original/review-wheel.svg): a four-part circular Review graphic. Replace the question, categories and source claims; the colored areas do not encode amounts.
- [electrolyte-evidence-chain.svg](../assets/original/electrolyte-evidence-chain.svg): a formulation–solvation–interphase–cell-result layout, with inference links explicitly dashed.
- [battery-lab-primitives.svg](../assets/original/battery-lab-primitives.svg): six original, editable icons for generic electrolyte preparation, cell formats and testing equipment.
- [battery-morphology-primitives.svg](../assets/original/battery-morphology-primitives.svg): particles, rods, sheets and network shapes that make no measurement claim.
- [style-preview.svg](../assets/style-preview.svg) and [STYLE_PRESETS.md](STYLE_PRESETS.md): six selectable figure color systems; the three user-supplied warm/cool palettes use stronger line colors at final size.

These files are MIT-licensed as part of BatteryReviewForge. Keep the scientific caption and source IDs outside the template; filling a placeholder does not validate a mechanism or comparison.

The [pattern atlas](ASSET_PATTERN_ATLAS.md) classifies local-reference ideas into battery cell structures, laboratory steps, generic morphologies, arrows and decorative textures. It explains which classes were redrawn and which should stay outside evidence figures. Run `scripts/render_template.py` to recolor an original SVG after the author chooses a style; the script never ingests or recolors third-party packs.

## Bring your own reference material

The author may provide PPTX, AI, PSD, EPS, image or PDF collections. Make a **private catalog** before using them:

```bash
python skills/battery-review-figure/scripts/asset_inventory.py \
  --input path/to/reference-assets \
  --output outputs/private-asset-inventory.json
```

The catalog stores format, size, hash, duplicate group, PPTX slide count and download state. It does **not** copy files into the plugin. Every item starts with `rights_status=unknown`; review its origin and license before reuse or publication. Download-in-progress files are listed separately and must be rescanned after completion. An image that looks available in a local folder is not automatically open source.

Use reference material to identify useful visual structures, such as a circular four-stage synthesis, a cell cross-section, or a paired comparison grid. Redraw an original source file from verified facts and raw data in this library's colors, typography and geometry. Do not trace a published illustration, reuse a seller's icon pack, or carry its outdated claims into a new figure. If permission is granted for a specific visual, record the permission and exact credit in the project figure ledger.

## Redraw checklist

1. Write the **one conclusion** the figure supports and list the evidence for each arrow, number and label.
2. Decide whether the source is a measured plot, a schematic of an established mechanism, a proposed model, or a decorative layout. Keep those types visually and verbally distinct.
3. For a data plot, regenerate from the underlying table through [the upload route](UPLOADED_DATA.md). A screenshot cannot recover exact values, uncertainty, or axis meaning.
4. For a schematic, create editable SVG/PPTX from scratch. Use the same palette and line weight across the figure. Show half/full/symmetric test boundaries accurately; distinguish a measured pathway from a hypothesis.
5. For a multi-panel item, send exported panels to `battery-figure-assemble` and inspect the final-size PDF/PNG, alignment overlay and panel crops.
6. Keep a project-local source/permission record. Only original, licensed or expressly permitted reusable assets may be placed in a public release.

## 中文说明

“素材库”分两层：公开仓库只带我们自己画的模板和配色；你电脑上给的 PPT、PSD、AI、图片先建**本地清单**。我会学习它们怎么组织画面，再按核实过的电池事实重画。原素材版权不明时，不能因为改了颜色、描了边就当成自己的开源图。图里若有旧机理、旧数值或不清楚的电芯条件，先查原始证据，再决定是否保留。数据图优先从原始表格重画；论文截图只可作为排版参考，不能当作精确数据来源。
