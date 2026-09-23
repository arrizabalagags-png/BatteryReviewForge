# Reproducible multi-panel assembly

This route accepts author-supplied raster panels (PNG/JPEG/TIFF) and one-page PDF/SVG panels. It outputs a physical-size PDF, a 300 dpi or higher PNG preview, per-panel crops, an alignment overlay, and a JSON audit. PDF/SVG sources stay vector where the source permits it. Raster images are never made vector by wrapping them in PDF.

## Run it

Install the skill's Python dependencies in a project environment:

```bash
python -m pip install -r skills/battery-figure-assemble/requirements.txt
```

Inspect a folder first, then compose with a reviewed manifest:

```bash
python skills/battery-figure-assemble/scripts/compose_figure.py inventory \
  --input path/to/figure_sources --output path/to/inspection
python skills/battery-figure-assemble/scripts/compose_figure.py compose \
  --manifest path/to/figure_manifest.json --out path/to/Fig3 --strict
```

`--strict` blocks output when the tool detects low effective raster DPI, excessive white margins, underfilled slots, unclear rights or declared plot-area misalignment. Without it, the tool produces an explicit review draft and reports each warning. Geometry checks do not certify scientific interpretation, copyright permission, font embedding or the target journal's current technical requirements.

For a self-contained synthetic check:

```bash
python skills/battery-figure-assemble/examples/demo_assemble.py outputs/assemble-demo
```

The example contains no research observations.

## Manifest contract

Paths are relative to the manifest. The author keeps the unaltered source files beside it or in a linked project folder. Each `source_id` identifies the original paper, dataset, experimental file or self-created diagram. Use `rights_status` of `original`, `licensed`, `permission_granted`, `pending`, or `unknown`. Licensed reuse also needs `license` and `credit`; granted permission needs `permission_record`. `pending` and `unknown` remain review warnings and block a strict final bundle.

```json
{
  "version": 1,
  "figure_id": "Fig. 3",
  "claim": "One bounded conclusion supported by all three panels.",
  "width_mm": 180,
  "margin_mm": 4,
  "gutter_mm": 2.5,
  "label_band_mm": 4.5,
  "row_heights_mm": [42, 48],
  "col_weights": [1, 1],
  "dpi": 300,
  "min_effective_dpi": 300,
  "panels": [
    {"label": "a", "path": "sources/overview.pdf", "row": 0, "col": 0,
     "colspan": 2, "role": "system and cell boundary", "source_id": "original:overview",
     "rights_status": "original"},
    {"label": "b", "path": "sources/cycle.png", "row": 1, "col": 0,
     "role": "primary measured trend", "source_id": "doi:example",
     "rights_status": "permission_granted", "permission_record": "permissions/fig3b.pdf"},
    {"label": "c", "path": "sources/conditions.svg", "row": 1, "col": 1,
     "role": "test-condition boundary", "source_id": "original:conditions",
     "rights_status": "original"}
  ]
}
```

Rows have explicit heights in millimetres. Column weights divide the available width after outer margins and gutters. `rowspan` and `colspan` may make a hero or a wide comparison panel. Every grid cell must be occupied exactly once unless `allow_empty_cells: true` and `empty_cell_reason` are supplied. The rendered figure height follows the row heights plus vertical gutters and margins. Panels use `contain`: no stretching, hidden automatic trim or implicit crop. Panel letters are placed in a consistent strip outside the artwork; set global `draw_labels: false` only when the sources already carry a coherent label system.

The composer does not create figure titles or subtitles. Keep that behavior when making a manifest or manually editing the PDF: a panel letter is enough when its axes, direct labels and the figure caption explain the content. Do not fill an apparently empty label band with headings. A source panel's existing title can be removed only from an editable source and only after checking that it does not carry the condition or sample identity; record the change in the panel ledger.

### Align the actual plot areas

Equal frames do not guarantee equal chart axes. For comparable panels, add an `alignment_group` and `plot_box_fraction: [left, top, right, bottom]` to **every** member. These fractions describe the actual plotted axes rectangle inside the placed source after any explicit crop. The auditor compares top/bottom edges for same-row peers and left/right edges for same-column peers at a 1.5 pt tolerance. An absent plot box or measured drift is a warning and blocks `--strict`; adjust source canvas or grid and rerun. The alignment overlay uses red for slots, blue for placed art and green for declared plot boxes.

### Crop only with a scientific reason

Raster panels may use `crop_px: [left, top, right, bottom]` in source pixels plus `crop_reason`. PDF/SVG may use `crop_box_fraction: [left, top, right, bottom]` relative to the original page box plus `crop_reason`; their page crop keeps vector content. The tool does not choose these values automatically. Compare before/after at full resolution and retain axes, scale bars, labels, uncertainty and relevant image regions. For micrographs, record calibration and any brightness/contrast/LUT changes separately; this assembler makes no tone adjustment.

If a source has more than one PDF page, set `page_number` explicitly. Multi-frame TIFFs must be exported to a stated frame first. An SVG with external resources is rejected; embed or supply those resources in a trusted source file before composing.

## Release check

Read the inventory, composite preview, alignment overlay and **each panel crop**. Check real journal width, not just a zoomed canvas. Confirm panel order follows the claim; consistent fonts, strokes, palette and legend treatment; no missing or duplicated letters; no clipped axes or scale bars; adequate effective DPI; comparable testing boundaries; complete captions and permissions. Inspect the PDF's text and vector/raster structure. When panels are native plots, rerender them at common physical slot sizes instead of repeatedly scaling export files to hide layout defects.

For a mixed-source figure, make a brief panel harmonization table before composing: each panel's physical slot width, plotted-area rectangle, measured final-size glyph size when vector text is available, line weight, legend placement, panel-letter status, original palette, raster DPI, and unresolved rights/conditions. Treat text embedded in a raster image as an estimate, not a measured font size. If one panel is too small or uses a conflicting chart palette, regenerate it from editable source or data with the manuscript's selected style. Never change the color mapping of microscopy or spectral intensity merely to match another panel.

The `font_audit` section of the QA JSON measures extractable vector text in the **final composed PDF** by panel. It reports the smallest and median detected sizes and flags sizes below 6 pt for manual review; 6 pt is a screening threshold, not a journal rule. Raster and outlined lettering are marked unmeasurable. A clean scan does not prove that every label is readable: inspect the exported PDF at the physical submission width and compare its caption and axis labels with the target journal's current requirements.

Some PDF text scanners report oversized text boxes when an SVG-to-PDF export encodes glyph size through a transform. Treat a scanner warning as a lead to investigate: inspect the exact rendered glyphs at final size, compare the source SVG/PDF, and keep the scan result and resolution note. Never dismiss a visible collision because the manifest geometry passes.

## 中文速用

先用 `inventory` 对作者提供的图片、PDF、SVG 生成素材清单与联系页，逐张看内容、空白边、轴标签、比例尺和权限。再按整图论断为各面板安排证据职责，使用毫米单位的 JSON 网格写清宽度、行高、栏宽、间距和面板顺序。`compose` 会输出 PDF、PNG、各面板检查图、对齐叠加图及 QA JSON。图片不拉伸；裁剪必须显式记录原因。可比图在 manifest 中填写 `alignment_group` 与 `plot_box_fraction`，检查的是实际绘图区，而不只是外框。最终仍需在投稿尺寸逐张检查，并核对电池测试条件、引用和图片复用许可。

## Related open-source practice

The workflow draws on general ideas visible in [Figure Composer](https://github.com/WangHuiNEU/open-science-toolkit/blob/main/skills_assets/figure-composer/SKILL.md) (claim-led panel roles and composite review), [polish-sci-figures](https://github.com/zhoy0409-debug/polish-sci-figures) (fixed canvas and final-placement QA), and [FigureFlow](https://github.com/maxschelski/figureflow) (reproducible physical layout). This package does not redistribute their code, figures or templates. FigureFlow is GPL-3.0; this assembler is an original MIT implementation.
