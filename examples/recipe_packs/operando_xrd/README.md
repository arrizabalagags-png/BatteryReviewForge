# VoltPeer 绘图包：operando_xrd

版本 0.12.0 / Beta。包含源码、演示数据、参考图和使用说明，可独立使用。

## 先试一次

在包目录创建项目 venv，使用其中的 Python：

```text
python -m pip install -r requirements.txt
python src/plot.py --config config.demo.json --out Working-demo
python checks.py --working Working-demo
```

演示是原创合成数据。参考图由本包同一份 CSV 与配置绘制，模型公式、假设、来源和范围见 `demo/model.json`；引用只支持模型定义，不提供演示数值。

## 换成自己的数据

把 `config.real.example.json` 复制为新配置，请助手按 `AGENT_GUIDE.md` 和 `input_contract.json` 核对文件、列名、单位、质量或面积基准与工况。填写完成后，使用同一命令，把 `--config` 换成新文件。不能继承演示条件；缺数据时不会用演示补齐。

结果打开 `index.html` 查看，图件在 `results`。原 CSV 保留，重复运行会另存新目录。数据不会被平滑、裁掉或补点。绘图包不自动确认具体期刊的格式要求。

## 分享结果

```text
python src/share_bundle.py --working Working-demo --out Share --rights-confirmed --license MIT
```

上例许可只适用于本包原创演示。真实结果分享前须确认权利、许可及姓名、课题、未发表图像；不要直接沿用 MIT。技术检查不证明科学结论或授权。Flash/Pro 行为与原生桌面完整流程尚未通过本包验证。
