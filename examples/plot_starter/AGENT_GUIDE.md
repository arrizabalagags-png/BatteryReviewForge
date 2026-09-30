# 固定程序绘图入口

初次使用运行 `python start.py check` 验证本包；已有实际检查记录时继续当前任务。读取当前安装的 `battery-review-figure/SKILL.md`、[输入说明](INPUT_GUIDE.md)，以及 `UPLOADED_DATA.md` 中当前图型的字段与条件段。普通数字图优先走下面短路线。用户已选配色就直接沿用；不运行 styles，也不重复选择。

1. 在此解压目录运行 `python start.py setup`；依赖只安装到本包 `.venv`。无需询问/读取/填写 API key。
2. 初次安装运行 `python start.py install --host dsh --workspace "用户打开的项目根目录"`（Codex 用 `--host codex`）。原生新会话中定位实际 SKILL.md；copied 不等于 discovered。
3. 初次试样运行 `python start.py demo --out "项目根目录/demo-result"`，打开返回的预览。用户已经选过配色时加 `--style 已选配色ID`，不要再问。这一步必须称为合成 Demo。

上面安装/演示只在用户需要时做一次；已准备好的作者任务直接从 inspect 开始，不重装、不再跑 Demo。Flash 每阶段只处理一个目标、做一个事实动作：

1. **查真实表头**：`python start.py inspect --data "数据路径"`。候选为空时，结合作者已明确的图型与真实字段含义确认映射，不直接称不支持。
2. **写独立映射 JSON**：仅填作者确认的字段、单位、source_id、核查状态、科学条件、尺寸、用途与说明，沿用已选 style。必需信息缺失时给短缺项清单并停止；不能靠改模式绕过核心条件。
3. **调用固定程序**：`python start.py plot --data "作者数据路径" --metadata "映射路径" --out "项目根目录/result"`。使用真实绝对路径；尺寸用映射 width_mm/height_mm，分辨率用 `--dpi`。不传 --style 时映射配色优先；用户明确改色才传该参数，程序留来源记录而不修改输入。
4. **检查真实结果**：`python start.py check --working "实际结果目录"`，再用当前可用图像工具检查真实图件。没有视觉工具时保留视觉待查项，不谎称看过。
5. **短回复交图**：只给可点击的预览/图件链接与真正的异常或未决项，沿用用户语言。

工具没有报告相关错误前，不加载 Python 实现、整套 figure grammar/registry/primary-paper ledger、atlas、全部配色或审计模板。它们用于新图型、机制/证据图、论文 Figure 策划等任务；不能把 Review 的全流程套给普通上传。真实宿主能力疑问或恢复中断任务再读执行指南。实现/环境错误发生后只查对应资料，最多做两次有证据的 repair；不得重写固定程序或放松科学合同。

普通上传的10种图用包内固定 `batteryplot`，禁止让模型每次重新写或替换绘图程序。不得复用 Demo 条件到作者数据，不得猜单位、CE 分母、验证状态或实验结论。source_id 与 evidence_state=verified 必须来自作者实际核查声明，代码不认证实验真实性。NA 只在作者确认不适用时使用；NR 是核查后未报告，NV 是未核验，三者不互换。direct 只筛查声明条件一致；缺少或不同的对比条件时先停直接比较，作者明确选择 contextual 也必须满足全部核心字段并明示限制，不得回填 Demo 或伪造 verified。

实线、无点和四边框是本项目偏好；不改变原值、不平滑、不裁剪，CE>100 等异常保留并提醒核对。根据当前实际能力检查结果；没有视觉工具时不能声称看过图。

正常最终回复沿用用户语言，只给可点击的图件/预览链接和真实未决问题，最多几行。不要把内部映射、日志或 `.voltpeer` 链接铺给用户；仅在用户明确要来源记录时提供，来源说明也沿用用户语言。
