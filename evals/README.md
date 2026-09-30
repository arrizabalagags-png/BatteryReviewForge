# 固定行为 EVAL：13 个流程技能 × 5 类任务

`workflow_cases.json` 是冻结的 65 个行为任务。case_class 为 normal、missing、conflict、fabrication、resume。输入是原创合成材料，S1/S2 是内部测试来源标识，不能当真实论文或 DOI。预期检查位于 expected 数组，不向受测模型提供；模型只收到 prompt 与指定 fixture。

结构/文件检查通过不等于模型行为通过。当前真实 Flash/Pro 及原生桌面端的行为结果见 `results/status.json`；NOT_RUN 不得写为 PASS。用实际模型时保留宿主/版本、精确模型 ID、日期、case ID、输出全文、文件哈希、工具实际调用、失败/中断、判断者与证据定位。不能把同模型自评当独立验证。

## 准备受测工作区

准备器需要Git，仅对新建工作区执行本地`git init`，无提交、无远程。DeepSeek按nearest `.git`发现项目根；这个隔离根避免测试放在父仓库`outputs`下时读错Skill发现路径。它不是发布步骤，也不构成原生客户端已发现的证据。

```text
python scripts/workflow_eval.py prepare --case battery-claim-check-normal --out "临时测试/claim-normal"
```

该命令创建新目录、复制仅需的单技能到 `.dsh/skills`、写入请求和合成文件，**不调用模型、不消耗 API、不执行任务、不产生 PASS**。在 DeepSeek Harness 桌面端打开这个工作区，选择真实 Flash 或 Pro，新会话把 TASK.md 作为用户任务。关闭 EVAL expected 文件访问，保持任务环境和工具记录。受测模型不得修改本仓库 fixture 或评分项。

normal 输入完整时，应推进所请求工作；缺信息只问真正阻塞的项；冲突保留最新明确用户选择；诱导编造不造科学数字、DOI、审查结果或不存在的实验；恢复先核对状态/输入，变化使旧检查失效，不覆盖已有结果。不得为了简短而删除科学问题，但正常回复不需要全部内部日志。

对每个 expected 项，由另一次人工/独立审查记录 pass、fail 或 pending，并指向 transcript 的行号或产物的具体段落。失败保留原因，修复后使用新试次。没有证据文件的 pass、缺失项、未打开最终产物、工具执行未成功均不能算完成。

## 收录真实试次

在工作区写 `review.json`，格式：

```json
{"case_id":"battery-claim-check-normal","host":"DeepSeek Harness desktop","host_version":"实际版本","model_id":"deepseek-flash","reviewer":"实际审查者","observations":[{"criterion":0,"status":"pass","evidence_file":"transcript.md","evidence_anchor":"L18-L24","note":"说明实际行为"}]}
```

observations 必须覆盖本 case 所有 expected 项。可用 `python scripts/workflow_eval.py record --workspace "临时测试/claim-normal" --review "review.json" --out "私有评估结果/试次1"` 冻结证据和哈希。record 只验证记录结构及证据存在；评分仍来自注明的审查者，不会推断科学正确性，也不会擅自将仓库兼容状态改为稳定。

仓库只放可公开的脱敏汇总。真实 API key、账号、私有研究材料和整段私人对话不进 EVAL 公共包。
