# VoltPeer 可复现绘图包：operando_xrd

resource_id=`operando_xrd`，候选版本0.10.0 / Beta。源码、演示、依赖、输入契约和接手说明均在本包，不要求完整仓库或全局Skill。

## 先验证环境

在包目录创建项目venv，使用其Python：

```text
python -m pip install -r requirements.txt
python src/plot.py --config config.demo.json --out Working-demo
python checks.py --working Working-demo
```

演示为原创合成数据，仅供理解布局。参考图来自同resource_id原始合成样图；新源码接收长表、动态分组和范围，不要求数值/条件与参考图相同。

## 换作者数据

先读AGENT_GUIDE.md、input_contract.json。复制config.real.example.json为新配置；按真实资料填全列映射、单位、归一化基准和工况，确认demo_conditions_cleared。命令同上，将--config换成新文件；没有缺数据后备。

输出打开index.html，实际图件在results，内部检查/原文件/恢复状态在.voltpeer。重复运行新建版本目录。原CSV不改，原始数值不平滑/拟合；坐标会裁值时停止。PNG/TIFF是作者请求预览DPI，尚未核对具体期刊要求。

## 公开分享

```text
python src/share_bundle.py --working Working-demo --out Share --rights-confirmed --license MIT
```

上例许可只适用于本包原创演示。真实结果需确认公开权利/许可及可见姓名、课题、未发表图像；不得默认沿用MIT。技术检查不能证明科学结论、授权或真实模型适配。Flash/Pro行为和原生桌面完整流程本轮NOT_RUN。
