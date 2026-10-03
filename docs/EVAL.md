# 技能行为与脚本验证

本次适配为Beta。默认DeepSeek Harness桌面项目工作区，Flash短阶段、Pro文字/证据规划；科学检查不变。2026-10-01已实际执行直连官方API的有限三轮pilot（含修复共13个任务试次），总体PARTIAL_API_PILOT；原生桌面全链路和完整69项仍NOT_RUN。模型返回COMPLETED不等于独立验收PASS。

去敏[实际API用量与独立评分](validation/2026-10-01-api-pilot.json)：最终Flash正常图原值/格式通过、缺信息被程序安全拦截；Pro保留相反证据、NR/NV并按字节复制原稿。缺信息回复仍有“任一项补齐即可”的错误引导，部分回复的结果链接/过程说明待改进，因此不能升级Stable。全部失败试次与不确定扣费预留均保留；实际安装树被冻结，报告更新不会改写旧RUN里的包SHA。

固定行为任务和复核协议见[69项EVAL包](../evals/README.md)：保留13个流程Skill各自正常/缺信息/作者选择冲突/编造诱导/恢复的65项，另加4项同一科学claim的实质相反证据任务，含NR/NV边界。结构校验命令 `python scripts/workflow_eval.py validate`，只是冻结case和fixture完整性，不执行模型。新试次保存完整安装Skill树的文件哈希/摘要、源提交与工作区修改状态、准备和实际执行OS/架构；只保存SKILL.md哈希不足。实际试次仍需要请求全文、精确模型/宿主版本、调用记录、打开产物和独立评分证据。

软件测试运行 `python -m unittest discover -s tests -v`，覆盖数据科学约束、真实图件输出、中文空格/BOM路径、LZW TIFF及每格式DPI、SVG原生Cairo缺失、Working与Share分离、哈希失效恢复、安装更新与单包引用。单元和脚本测试PASS只对应测试定义的工程行为，不代表论文科学认证或未实跑模型。

发布必须先同步 `python scripts/sync_execution_contract.py` 和 `python scripts/sync_standalone_references.py`，再 `python scripts/check_skill_distribution.py --skills-root skills`，并对各独立ZIP解压目录重复执行 `--skill`。打包的结果仍须记录native discovery未实测项。
