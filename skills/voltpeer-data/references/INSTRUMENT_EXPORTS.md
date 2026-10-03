# 蓝电、新威与常规表格导入

`instrument_import.py` 在用户的本地项目读取 CSV、TSV、TXT、XLSX 和旧 XLS；可选的固定依赖读取已核对的 NDAX NDC-14 分层文件。原文件保持不变，输出必须使用新的私有工作目录。工具不主动上传数据；AI 服务/客户端是否把读取内容发送到在线模型取决于所选客户端。公开网站、技能 ZIP、测试夹具和 Git 记录不能放用户实验数据。

## AI 执行路线

1. 用项目独立 Python 环境安装 `requirements.txt`，运行 `python scripts/instrument_import.py inspect --input 文件路径`。文本表使用标准库；XLSX 需要 openpyxl，旧 XLS 需要 xlrd。不把旧 XLS 改名成 XLSX，不把 CEX/NDA/NDAX 改名成 CSV。
2. 查看全部工作表和数据块，按真实表头选择循环、工步统计或逐点记录。同一工作簿的表头可在前置信息行之后；重复表头生成独立数据块，不自动合并通道或续接测试。`StepNo/ObjectType/MainPara/EndCond/LogCond/ProtectCond` 等工步程序表返回 `non_measurement_input`，不能作为测量数据。Info 表也不代表测量。
3. 运行 `python scripts/instrument_import.py prepare --input 文件路径 --output-dir 新工作目录`。已有目录会被拒绝。输出包含源文件的逐字节副本、独立 CSV 和私有导入记录。CSV 保留原始单元格，另外添加 `vp_source_sheet`、`vp_source_row` 和 `vp_` 标准单位字段。源副本保留前置信息、空行、公式和未分类内容。表格缺列或多列时检查会保留整行供诊断，准备步骤会在写文件前拒绝，不能截断、补零或跳过异常行。
4. 明确列头单位才能换算：V/mV/µV → V，A/mA/µA → A，秒/分钟/小时/毫秒及明确的 HH:MM:SS → s，Ah/mAh/µAh → mAh，mWh/Wh → Wh。mAh/g、Ah/kg 或 Ah/g 只按明确的单位等价换算；不能从绝对容量猜质量/面积。没有单位、未知单位或重复语义候选列保留为 unresolved/ambiguous，不能按数值大小判断。循环/工步/记录号须为非负整数；原编号与行序保留，不重编号。
5. 原值的零、空、NaN/缺失标记、非数字和公式分别保留。不能用 0 填缺失，不能滤掉 NaN，不能平滑或把 CE 压到 100%。XLSX 公式不执行，标准数值列保持空且记异常；旧 XLS 只能读保存的计算结果，记录明确注明未重新计算，原文件仍完整保留。
6. `numeric_ready` 只表示所识别字段解析和单位换算通过。导入记录的 `ready_for_plot` 和科学验证标志保持 false。按用户要求的图型核对电池配置、分支/工步身份、循环及时间基准、容量/能量口径、温度/倍率/窗口、归一化分母。已有材料或前文已经给出的条件直接复用；缺少且影响目标图的条件一次列清。

电压容量曲线按明确工步类型确定分支，不由电流正负命名；重置的工步时间不能直接拼成总时间。普通 `Capacity` 可能每工步重置。循环容量优先看实际厂商循环层定义。重算 CE 必须确认同一循环、相应电荷和协议分母；导入工具不自动执行放电/充电相除。

正常回复交付目标图/表和必要未决问题。路径、哈希、映射、单位检查、异常和恢复信息留在私有项目 `.voltpeer/`；不要把导入日志当作公开结果或要求用户手改 JSON。

## 原生格式的实际边界

| 输入 | 本地行为 | 已验证范围 |
|---|---|---|
| LAND CEX | `needs_vendor_export`，给出 LANDdt 导出动作，不创建假 CSV | 授权真实 CEX 已做只读识别/原文件哈希核对；没有经验证的 CEX 解码器 |
| NEWARE NDA | `needs_vendor_export`，给出 BTSDA 导出动作 | 本次没有 NDA 实样；库支持 NDA 不等于本项目通过 NDA 验证 |
| NEWARE NDAX | 可选 `requirements-native.txt` 的 `NewareNDA==2026.6.11` 与 `scripts/neware_ndax14.py` | 已核对本批授权实样的 NDC-14 分层家族：`data.ndc` 类型 1、`data_runInfo.ndc` 类型 18、`data_step.ndc` 类型 7 |
| 其他 NDAX 版本、单文件布局、辅助通道、缺运行信息、非法归档、依赖缺失/版本不同 | 明确返回厂商导出动作及原因 | 不把不匹配的字节强行解释为已验证布局 |

可选原生依赖安装到项目环境：`python -m pip install -r requirements-native.txt`。CSV/Excel 路线不需要它。依赖来源为 [维护者 NewareNDA 项目](https://github.com/d-cogswell/NewareNDA)，许可证 BSD-3-Clause；分层布局/单位依据 [维护者原生 NDAX 源码](https://github.com/d-cogswell/NewareNDA/blob/master/NewareNDA/NewareNDAx.py)，版本固定为 2026.6.11，随代码保留 BSD 署名、条件和免责条款。不要把其他版本安装成功当作验证。

### NDAX 保留三层的原因

固定读取器公开接口 `read` 默认会重新生成循环号（`software_cycle_number=True`，`cycle_mode='chg'`）；某些分层布局还会补算缺失的时间、容量和能量。[维护者读取接口](https://github.com/d-cogswell/NewareNDA/blob/master/NewareNDA/NewareNDA.py)。本适配器核对时明确传 `software_cycle_number=False`，在输出源层保留 `Cycle_ZeroBased` 原值，不做 +1、循环重建或时间插值。状态标签来自固定版本状态字典，原状态码保留。

实样中存在同一记录号的重复运行信息和零电压记录。固定读取器会选择第一条运行信息，并在 NDC-14 的测量层略过零电压。为保留这些观测，本工具将三个源层分别导出：

- 测量层：电压、电流、记录位置；运行信息引用的零电压位置也保留，不当坏点删除。
- 运行信息层：原毫秒时间、容量、能量、时间戳及重复记录，全部保持顺序。另标注的 UTC 时间戳由原 epoch 秒和毫秒明确换算，原字段保留；不猜实验室时区。
- 工步信息层：原零基循环、工步编号和状态码；不自动与测量/运行信息拼成一张曲线表。

`Native_Byte_Offset` 指向原归档成员中的位置；测量层 Index 是固定布局的一基物理位置编号。没有运行信息的内部零值位置不能当作尾部填充排除；缺失对应关系或需要插值时退回厂商导出。归档里的日志/其他原始成员保留在完整源副本中；辅助通道的单位及对应关系尚未验证。

导入会逐条把可对照的非零测量与固定读取器核对电压、电流、时间、充/放电容量、能量和绝对时间戳。这是同布局的解码/单位一致性检查。没有提供同次测试的 BTSDA 导出表，**尚未证明与厂商报表定量等价**。重复记录的对应规则、零电压的仪器状态、循环统计方法和科学条件仍须按目标图核对，不自动选择或合并。源层可读不等于可以直接生成最终容量/CE/循环曲线。

## 厂商导出与验证

- 蓝电：在实际版本 LANDdt 中打开原文件，使用对应版本的数据导出/复制功能获得 Excel 或文本表。[蓝电官方说明书入口](https://www.whland.com/dom/down_list.php?channel_id=25514445&username=landiandianzi)。不虚构所有版本共有的按钮。
- 新威：在对应 BTSDA 版本导出完整循环层、工步层和记录层；核对报表包含的区间、通道和续接顺序。[新威官方所见即所得报表说明](https://www.neware.net/support/what-is-a-wysiwyg-report-type/183/44.html)。只导出当前可见范围可能不足以检查完整记录。

公开回归测试仅用原创合成文本、Excel 和固定结构 NDAX 夹具，覆盖单位、编码、不同层、多表头、公式、重复/缺失/异常和不覆盖。实际作者数据、转换表和完整验证日志只存于私有输出目录。当前路线为 Beta；只报告实际检查过的家族与门禁，不能说“全部蓝电/新威原始文件都能直接画”。
