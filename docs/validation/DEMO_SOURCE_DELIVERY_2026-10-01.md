# 示例包源码交付 — 2026-10-01

## 修复范围

旧 `BRF-demo-<id>.zip` 只有数据和 metadata。现在的打包器为 30 个 canonical 样例交付对应 Python 源码、实际导入依赖、样图、运行入口与依赖清单。2 个既有连字符 alias 保持原文件名和目录布局，也带相同入口。

这是本地开发改动。本文不构成 GitHub 已推送、ECS 已部署、桌面宿主识别通过或作者数据科学验收的证据。

## 包含什么

- 原有 `<id>/metadata.json`、CSV/JSON 相对路径保持不变；canonical 输入按原字节打包。
- `reference/figure.png`、`reference/figure.svg` 和该图的原 metadata；不复制其他 29 张图。
- `render_existing.py`：只读取已有 CSV，调用对应 renderer 的 `render()`。
- `code/examples/showcase/<family>.py`、共享教学模型 helper，以及该 renderer 实际需要的 `batteryplot` 代码和资产。
- `requirements.txt`：`numpy>=1.26,<3`、`matplotlib>=3.8,<4`；不含与绘图无关的全部工程依赖。
- `SOURCE_MANIFEST.json`：逐文件 SHA-256、源码仓库相对路径、原输入哈希、运行及输出约束。源码来源由实际包内字节证明，不指向旧 GitHub 提交假称当前代码。
- 简短中英 `README.txt`、MIT `LICENSE`。

## 数据及输出保护

渲染器在临时副本里运行，原文件不写。包内源码缺失或意外变动会停止；有意修改源码可使用 `--allow-code-changes`，并记录实际和原始哈希。改过的作者数据、源码或 metadata 不再继承示例 `scientific_basis`、随机种子和虚构测试条件的背书。

输出目录必须是新目录。第二次使用同一名称会停止，保留旧结果。结果含 PNG/SVG/PDF、输入副本、`RUN_RECORD.json` 和必要检查记录。缓存及 Python bytecode 不写入下载包。无模型调用、无自动联网或安装。

复合图的输入沿 `metadata.source_files` 和 `sources.json` 的 `members` / `uses` 递归解析。例如 `capability_spread` 旧 metadata 只列索引文件，但实际 renderer 读多张邻居样图；打包器现在包含这些 CSV/JSON，仍不夹带整套图片或其他 Skill。

示例源码是同类型图的起点。换自己的数据时仍需核对列名、单位、条件和源码中的坐标范围；不宣称自动识别任意仪器 CSV，也不把成功渲染当成科学结论正确。

## 验证与集成入口

不写正式 assets 的隔离打包：

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& 'outputs/qa-venv/Scripts/python.exe' scripts/package_demo_bundles.py --out outputs/demo-source-delivery-test
& 'outputs/qa-venv/Scripts/python.exe' -m unittest discover -s tests -p test_demo_bundle_execution.py -v
```

科学模型及当前 canonical 数据完成生成、渲染、发布后，再调用 `scripts/package_demo_bundles.py` 的默认输出，更新当前未版本化 Demo 资产；历史固定版本及冻结包保持原字节。

测试覆盖全部 30 canonical + 2 alias 的包、源码原字节和输入闭合；真实解压后以 `python -I`、无仓库 `PYTHONPATH` 运行 EIS、CV、FTIR、Aurbach、六面板组合和十面板组合。另验证旧结果保护、缺输入停止、作者修改保留、源码修改显式授权，以及植入“调用造数即失败”的函数后依旧能重画。

## 当前验证状态

| 项目 | 当前结果 |
|---|---|
| 打包器、独立 runner、测试脚本 AST | PASS |
| 当前公共 assets 重打包 | 本子任务未执行；由主任务统一生成当前资产 |
| 30 canonical + 2 alias ZIP 闭合 | PASS：32 包全部 ZIP CRC、manifest 文件闭合、源码原字节、CSV/JSON 原字节核对 |
| 6 种代表脱离仓库真实运行 | PASS：EIS、CV、FTIR、Aurbach、integrated_study、capability_spread；中文路径、python -I、无仓库 PYTHONPATH |
| 输入与输出故障边界 | PASS：旧目录拒绝且原结果不变、缺 CSV/NaN 停止、作者修改保留、源码篡改拒绝、主动修改显式记录、禁止 generate 炸弹无调用 |
| 原生 Harness / Codex / WorkBuddy 识别 | 未测；本测试不覆盖 |
| GitHub 推送 / 正式站部署 | 未执行 |

**实际结果：8 个测试方法全部通过，102.277 秒；6 个代表重画均生成 PNG、SVG、PDF，原输入和下载包源码均未改变。** 另实际跑过作者更换 EIS 数据和主动改源码两条成功路径。全部在临时目录完成，未写当前公开 ZIP。

[机器可读记录与源快照 SHA](2026-10-01-demo-source-delivery.json) 和 [实际 unittest 输出](2026-10-01-demo-source-delivery-unittest.log) 保留测试边界。临时 ZIP 已由测试清理，其每文件及整体哈希在运行时确实核对通过；该记录不宣称尚未由主任务重打包的 `docs/assets` ZIP 已升级。

这轮只证实闭合、数据保护及独立重画，不把图画出来等同于作者数据科学正确，也不把 Windows 运行当成 macOS/Linux 或桌面宿主实测。
