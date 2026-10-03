# VoltPeer 绘图 Starter

固定的绘图程序已附在包里。你提供数据、确认字段、选配色，AI 调用程序即可。

## 第一次使用

1. 完整解压，保留整个文件夹；在 DeepSeek Harness 中打开你的科研项目。
2. 把 [AGENT_GUIDE.md](AGENT_GUIDE.md) 交给 AI，让它安装并跑 Demo。安装需要 Python ≥3.10（本次 Windows 验证为 3.12）和下载 Python 依赖的网络；不需要 API key。
3. 打开结果里的 `index.html`。再把自己的数据交给 AI；缺少单位或科学条件时先补充。

常用命令，在此解压文件夹的终端运行：

```sh
python start.py setup
python start.py install --host dsh --workspace "你的项目文件夹"
python start.py demo --out "demo-result"
python start.py inspect --data "你的数据.csv"
python start.py plot --data "你的数据.csv" --metadata "作者确认的映射.json" --out "result"
```

Codex 把第二条的 `--host dsh` 改成 `--host codex`。两种入口共用同一个 Skill 和绘图实现。新会话中确认实际识别的技能路径；安装命令成功只表示复制完成。WorkBuddy 继续使用网站上的单技能 ZIP 导入。

输出图件在 `results/`；重新运行保留旧版。默认导出 PDF、SVG、300 dpi PNG；需要 TIFF 时加 `--formats pdf svg png tiff`。300 dpi 是请求的预览规格；投稿前核对目标期刊要求。

已选配色时 Demo 可加 `--style peach_ice` 等配色 ID；换自己的数据默认沿用映射里的 style。用户明确改色时再传 --style；实际改色会记录，原数据和 JSON 不会被覆盖。

支持的图型、必需字段与安装目录见 [输入说明](INPUT_GUIDE.md)。示例均为合成数据，没有实验或文献结论。绘图包安装本身不收费；让 AI 识别数据会消耗你所用宿主/模型的额度。


旧版 battery-review-figure 安装由完整 VoltPeer 包显式迁移，本 Starter 会检测并拒绝重复安装。
