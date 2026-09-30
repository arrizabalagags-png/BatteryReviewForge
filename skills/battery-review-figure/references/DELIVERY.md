# 找到结果、继续修改、对外分享

安装技能和项目虚拟环境后，使用实际发现的技能路径运行。路径可含中文和空格，要加引号。metadata 的列映射、单位、条件、style、claim 和 caption_notes 必须先核对；UTF-8 BOM 可读取。

默认沿用 metadata.style。用户明确指定/改变配色时，可在 deliver.py 或 plot_uploaded.py plot 命令加 `--style 配色ID`；它只改变本次显示，原映射 JSON 不修改，图件来源记录保留 metadata_style、cli_style、effective_style 与是否明确改色。不能凭空改变科学字段或数据。Plot Starter 的 demo/plot 使用同一参数和同一实现。

```text
python "<installed-battery-review-figure>/scripts/deliver.py" --data "我的数据.csv" --metadata "映射.json" --out "结果/全电池循环"
```

根目录打开 `index.html`，最终图件在 `results/`；`.voltpeer/` 保留原始文件、规格、provenance、哈希和 TASK_STATE。Windows 默认隐藏这个内部目录，仍可恢复。再次写同一目标会生成 `_v002` 等目录，旧版不覆盖。编号表示同一输出名称的保留顺序，不能作为科研结论的版本证明。图件可从私有 Working 包发给 AI 继续修改；状态中的原路径应通过 manifest 内的 inputs 映射重定位。

默认 `--journal journal_neutral --content-class line_art` 只生成工作试样。提交到具体期刊前核对当前官方规则、文章类型和物理尺寸。可指定历史 profile ID 或自己的 JSON 路径；历史 profile 不完整时命令会提示，不能把缺值或范围任取一端。示例：

```text
python "<installed-battery-review-figure>/scripts/deliver.py" --data "我的数据.csv" --metadata "映射.json" --out "结果/投稿候选" --journal "已核对规格.json" --content-class mixed --dpi 600 --png-dpi 300 --tiff-dpi 600 --formats pdf svg png tiff
```

300 dpi PNG 可以仅用于预览；TIFF 默认 LZW。实际每格式 DPI、内容类别、来源日期和环境保存在内部记录。记录状态 `stored_profile` 或 `author_requested` 表示采用的规格来源，仍需稿件/期刊人工确认；它不等于已合规。

## 脱敏分享包

仅在作者确认文件可公开且许可有效后生成：

```text
python "<installed-battery-review-figure>/scripts/share_bundle.py" --working "结果/全电池循环" --out "公开分享/全电池" --rights-confirmed --license "作者原创，按 CC BY 4.0 分享" --source "https://doi.org/已核对的DOI"
```

命令检查 Working 结果哈希，只选最终 PDF/SVG/PNG/TIFF，丢掉原始数据、内部路径、状态与日志，清理可支持的元数据，使用公共文件名。未得到许可不生成。不会上传。再检查可见姓名、课题、未公开图像和必须保留的科学/版权信息；自动扫描无法理解全部像素内容。保留整份 Working 包供自己续改。
