# 用 Inkscape 微调成图 SVG（新手版）

[Inkscape 官网](https://inkscape.org/)提供免费的开源矢量编辑器，Windows、macOS、Linux 均可使用。请从官网获取安装程序。BatteryReviewForge 输出的 SVG 主要用于**最后的人手排版**：改错字、挪图例、调整间距和标签，而不是通过拖曲线改数据。

1. 在成图文件夹找同名 `.svg`、`.pdf`、`.png` 和 `.provenance.json`。保留原 SVG 与数据文件，先复制一份 SVG 再动手。
2. 用 Inkscape 打开复制件。选择文字工具可改文字，选择工具可移动或缩放对象。先选中一个标签试改；遇到字体替换，换用本机可用字体，再逐个检查上下标和 `µm / cm⁻¹ / mAh g⁻¹` 等单位。
3. 只调整视觉排版：面板字母同一基线、图例不盖曲线、轴字在最终栏宽可读。ToF-SIMS 离子图等可能是**嵌在 SVG 里的栅格像素**，外壳是 SVG 不等于每个像素都能当矢量改。
4. 数值、峰位、颜色映射、比例尺和原始图像需要修改时，回到 CSV/仪器导出/绘图脚本重新生成，并更新溯源文件；不要在 Inkscape 里徒手移动数据点或重新标比例尺。
5. 保存 SVG；如目标期刊需要 PDF，再从 Inkscape 导出或另存 PDF。检查字体、图例、裁边和比例尺在**实际投稿尺寸**下是否清楚，并把改后的 SVG/PDF 与原数据、图注放在同一项目目录。

在网页上可直接[下载本项目的 SVG 样图](../../../docs/index.html#examples)试手。ToF-SIMS、Raman/RDF、全电池和电芯分层展示图的源代码与虚构 CSV 在 `docs/assets/gallery/`；不要把样图当实验成果使用。

## English

Open the exported SVG in [Inkscape](https://inkscape.org/) for typography and layout adjustments. Keep the original and its provenance file. Regenerate from data to change a curve, ion map, scale or measurement; some SVGs embed raster maps. Export the final PDF if requested by the journal and inspect it at placement size.
