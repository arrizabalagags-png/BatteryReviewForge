# 完整绘图包 A/B/C 固定对照

这是待执行的真实宿主/模型实验，**不是本机脚本测试的另一个名字**。本轮真实Flash/Pro对照全为NOT_RUN；不宣称C优于A/B、不宣传省了多少费用。原始输入全部为明确标识的原创合成工程盲集，不能冒充实验数据。

| 方案 | 相同资料 | 额外资料 |
| --- | --- | --- |
| A | 同一个Skill版本、同一参考图、同一新CSV/条件 | 无源码示例 |
| B | 同A | 原有样例源码和实际运行依赖；保留固定Demo原设计，要求适配新数据 |
| C | 同A | 独立完整包：输入契约、配置、接手说明、源码、检查和来源 |

三种resource_id：full_cell、li_li、operando_xrd。固定case：new_shape（新分组数/不等长度/长图例/新数值范围；XRD乱序且不同网格大小）、missing_units、missing_conditions、conflict_range（最新作者指令覆盖旧显示范围）。先固定同一host/版本/模型/设置，再换模型；各arm至少3次，独立新会话，随机arm顺序，禁止上一arm答案混入下一arm。工具权限/venv/Skill复制发现阶段使用相同门槛。

```text
python scripts/prepare_recipe_comparison.py --resource full_cell --scenario new_shape --host "DeepSeek Harness Desktop" --host-version "实际版本" --model deepseek-flash --out "outputs/比较-full-cell-flash-01"
```

准备器生成A/B/C的相同input哈希、TASK.md、独立项目.dsh/skills、RUN_RECORD.json。准备阶段需要Git，仅对新建的各arm执行本地git init，无提交、无远程；这使DSH nearest .git发现根停在arm，避免放在仓库outputs下时越到父仓库。它不调用模型、不提交费用、不写PASS。各arm的参考图和新输入相同；B/C额外资料是被比较因素，不是训练参数更新。严格复制TASK.md，使用真实客户端打开该arm工作区。不要把审查标准当额外提示偷偷只给某个arm。

新 RUN_RECORD schema 2 冻结全部实际安装 Skill 文件的 `skill_tree_files`/`skill_tree_sha256`、完整来源 Skill 树摘要、`source_commit`、`source_worktree_dirty`/diff摘要和准备环境 OS/架构。不能只记技能名/版本或 SKILL.md；代码未提交时保留 dirty 标记及实际文件哈希。执行前核对树仍一致，运行后填写实际 `execution_environment.os`/`architecture`；准备机器信息不能冒充执行环境。历史 schema 1 记录保留且不倒填不存在的证据，新的运行记录必须使用这些字段。

审查必须打开实际最终产物，与CSV逐组逐列核对；不能只看“退出码0”或“生成文件”。原始输入出现缺单位、缺工况时，合格行为是提必要问题/停止。在conflict_range中新范围显示所有点，保留signed voltage，XRD按坐标键重建、不按行序reshape/插值；被截断/借用旧Demo为失败。材料齐备后提供正确单位、样品、条件；原创工程合成身份必须保持，不把盲集说成真实科研实验。

记录实际开始/结束、请求/返工次数、是否人工救场、模型版本、结果文件/消息/成本证据的路径和哈希。账户没有提供成本信息就留null，不能凭请求次数反推费用。Flash图像审查要有实际打开图件的证据；当前无视觉的Pro需保留独立人工视觉检查，不能编造看过PNG。

最后将同条件各arm的正确新数据使用、科学条件、应停行为、视觉/返工/耗时/成本逐项比较，区分真改进和重复实验波动。维护者复核RUN_RECORD和真实证据后才可出结论。原生客户端运行缺失时保持NOT_RUN。
