# 技能行为与脚本验证

本次适配为Beta。默认DeepSeek Harness桌面项目工作区，Flash短阶段、Pro文字/证据规划；科学检查不变。实际Flash/Pro行为和原生客户端全链路均未测试时，必须记NOT_RUN。

固定行为任务和复核协议见[65项EVAL包](../evals/README.md)，包括13个流程Skill各自正常/缺信息/冲突/编造诱导/恢复场景。结构校验命令 `python scripts/workflow_eval.py validate`，只是冻结case和fixture完整性，不执行模型。实际试次需要请求全文、精确模型/宿主版本、调用记录、打开产物和独立评分证据。

软件测试运行 `python -m unittest discover -s tests -v`，覆盖数据科学约束、真实图件输出、中文空格/BOM路径、LZW TIFF及每格式DPI、SVG原生Cairo缺失、Working与Share分离、哈希失效恢复、安装更新与单包引用。单元和脚本测试PASS只对应测试定义的工程行为，不代表论文科学认证或未实跑模型。

发布必须先同步 `python scripts/sync_execution_contract.py` 和 `python scripts/sync_standalone_references.py`，再 `python scripts/check_skill_distribution.py --skills-root skills`，并对各独立ZIP解压目录重复执行 `--skill`。打包的结果仍须记录native discovery未实测项。
