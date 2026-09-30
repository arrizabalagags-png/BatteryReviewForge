# GitHub 同步记录：2026-09-30

## 本次授权与范围

维护者在本轮任务中明确要求将修改代码与日志及时上传 GitHub，并指定并行执行。此前“今天一起上传”的等待状态已由这条新指令更新。本次同步到公开仓库的 `codex/public-skills` 分支；正式 tag、GitHub Release 与上海 ECS 发布为独立动作。

本记录与同目录的 `2026-09-30-distribution.json` 保存可公开的验证摘要。包含本机绝对路径的原始执行日志、研究工作区和凭据保留在本机；没有随源码或发布包上传。

## 已实际检查

- `python scripts/verify_distribution.py`：**36 个 ZIP、62 个解压后的独立 Skill 目录检查通过**。包含完整包、WorkBuddy 套装及 Starter、15 个便携单技能包、15 个 WorkBuddy 单技能包和 3 个完整绘图包原型。
- 三个绘图包的逐文件 SHA-256 与 `PACKAGE_MANIFEST.json` 对应；所有包的外部 SHA-256 在 `docs/downloads/distribution-sha256.txt`。
- 提交前扫描当前新增/修改文件及 ZIP 内容，共 **1,003 个文件条目**；未发现扫描规则覆盖的私钥、GitHub/API 令牌或用户个人绝对路径。扫描是具体规则检查，不能替代人工内容核对。
- `git diff --check` 通过。独立脚本和行为验证的具体范围见 [技能 QA](../SKILLS_QA_2026-09-30.md) 与 [EVAL](../EVAL.md)。

## 版本边界

版本为 **0.10.0 / Beta 候选**。原生 Harness 发现到交付、真实 Flash/Pro 模型评估与 macOS 实机验收均为 **NOT_RUN**。没有把脚本测试当成模型测试；本次没有创建 tag、Release 或触发 ECS 部署。

`RELEASE_STATUS.json` 与包内 QA 的早期等待说明记录的是打包时状态；新的 GitHub 同步证据以本文件后续条目为准。既有固定包未为修改说明文字而重打。

## 同步结果

源码与分发包提交：`137b6a6d2e184f3efb0f398a5517a7948bbc2c2b`（`Prepare VoltPeer 0.10.0 beta skills and verified distributions`）。本次提交包含 276 个变更文件，其中 36 个 ZIP。

执行 `git push -u origin HEAD:refs/heads/codex/public-skills` 成功；随后 `git ls-remote origin refs/heads/codex/public-skills` 返回与本地 HEAD 完全相同的 SHA。核对时工作区干净。

仓库分支：[codex/public-skills](https://github.com/arrizabalagags-png/BatteryReviewForge/tree/codex/public-skills)。源码提交：[137b6a6](https://github.com/arrizabalagags-png/BatteryReviewForge/commit/137b6a6d2e184f3efb0f398a5517a7948bbc2c2b)。本同步记录在后续文档提交中更新，未改变上述固定分发包字节。


## 追加科学图与可靠性修改：最终分发检查

最新维护源完整回归 **129 tests OK / 257.400 s**。实际扩展回归初次运行的 1 failure / 5 errors、三个修正原因和定向复验分别保留在 `2026-09-30-frame-regression-initial.json`、`2026-09-30-frame-final-regression.json`；旧 102 / 104 门禁为历史记录。再次完整回归期间 128 个合成 CSV 与已保存图件的 SHA 不变。

全部包从新的维护源重建，实际执行加强后的 `scripts/verify_distribution.py`：**36 ZIP / 62 独立 Skill 引用与 AST 依赖 / 30 canonical demo schema/source/site/ZIP 对应 PASS**。检查完整文件闭包、Skill 正文、色卡、中文字体处理和真实 requirements；WorkBuddy 只改 frontmatter。三个完整 recipe 的 runtime 与维护源、逐文件 manifest、外部 SHA 及参考资源身份一致。没有把源码 PASS 代替实际包检查。

完整便携包：`docs/downloads/BatteryReviewForge-v0.10.0.zip`，**872,687 bytes**，SHA-256：`9ce6aef09e45f1f0052f818f66cdefbabd4b793fbd0186c728a8a684ee4387b7`。所有 36 包的相对路径、大小、SHA 在 `2026-09-30-distribution.json` 和 `docs/downloads/distribution-sha256.txt`；三 recipe 的当前索引为 `docs/downloads/recipes/recipe-packs.json`，本地新候选目录名为 `outputs/recipe-packs-0.10.0-frame-final`。旧 candidate 哈希不作为本次结果。

提交前当前变更与 ZIP 内成员扫描 **1,389 条目**，没有匹配私钥、GitHub/API 令牌或个人绝对路径的规则；人工路径核对未包含私有 Web 源码、二维码、原始个人资料或超 100 MB 文件。自动扫描不代替人工内容审查。重复运行的版本化 assembly 产物、QA 与 panel overlays 保留本机并由 ignore 排除；原始 outputs 日志不上传。

CSV 在 Git 中设 `-text`，保留原输入 CRLF 字节，防止 fresh checkout 与实际下载包对应失效。代码/文字源码对照显式允许 CRLF/LF 归一化，ZIP manifest 和输入 SHA 仍严格按字节核对。`git diff --check` 使用 cr-at-eol 语义通过；Matplotlib 生成 SVG 的多行 path 属性格式空格仅对 SVG 设 blank-at-eol 例外，代码/文档不豁免。没有为满足空白检查改绘图数组或渲染产物。

本轮继续同步 `codex/public-skills` 的 Beta 源码候选。真实 Harness 发现到交付、Flash/Pro EVAL、macOS 仍 NOT_RUN；没有 tag、Release、main 合并、PR 或 ECS 部署。实际提交和远端一致性结果在推送完成后追加。

### 暂存快照复核

Git 暂存区另逐文件核对 **104 份 CSV 与本机原始字节完全一致**。为应用新的 `-text` 属性，执行显式 CSV renormalize；没有改本机原件。最终暂存的 **612 个变更文件、69 个 ZIP**（36 个下载包和 33 个演示/拼版包）再按 Git 实际 blob 和递归嵌套 ZIP 扫描 **1,832 条目**，无规则覆盖的令牌、私钥、个人绝对路径或禁止目录；暂存 diff gate 通过。

### 本轮公开源码推送结果

源码、绘图实现、科学图件、分发包及整理后的证据提交：`1cee0d16351070db7ee4b5f4a6ac6a2d45c886cf`（`Validate four-frame plotting and refresh beta distributions`）。`git push origin HEAD:refs/heads/codex/public-skills` 成功；随后 `git ls-remote` 返回同一 SHA，核对时公开工作区干净。

[本轮源码与包提交](https://github.com/arrizabalagags-png/BatteryReviewForge/commit/1cee0d16351070db7ee4b5f4a6ac6a2d45c886cf)；[公开分支](https://github.com/arrizabalagags-png/BatteryReviewForge/tree/codex/public-skills)。本结果段在随后的日志提交保存；没有为记录提交 SHA 修改已核验的分发包字节。用户决定今天收尾，只保存已完成工作和日志；ECS 留待后续发布。

## 用户恢复任务后的 schema 补充：2026-09-30

上一段“今天收尾”为当时授权记录；用户随后回到任务，明确要求上传完成内容后继续实施和检查。当前工作继续，GitHub 与 ECS 发布状态仍分别记录。此前公开日志保存提交 `ee6270695de6d8b1fcf32122de9d2f441b0806ae` 已在远端；本次增补继续保存同一 `codex/public-skills` 分支。

可选 `limitations` 字段现在存在时要求非空字符串。当前定向 schema 检查 **3 tests OK / 0.955 s**；合法内容、列表错型、空字符串以及已有缺字段/不实声明/非有限值/source-site-ZIP 不一致负例均覆盖。新增公开摘要 `2026-09-30-schema-followup.json` 随完整包分发。**129 tests / 257.400 s** 保留为增补前的完整工程回归；没有为这项低影响 schema 扩展重复数值测试，也没有更改数据、图件、Skill 运行时或 recipe。

重新生成完整包后，实际 **36 ZIP / 62 解压 Skill 引用与 AST / 30 canonical schema-source-site-ZIP PASS**。完整包内 schema、补充摘要、RELEASE_STATUS 和 QA 文档已逐字节（仅文本换行归一化）对照当前维护源。**35个其余下载包的大小和SHA完全不变**，其中三 recipe 保留原包；便携单 Skill 的重打输出与旧字节一致，WorkBuddy与recipe不做无内容的重复打包。

当前完整包：`docs/downloads/BatteryReviewForge-v0.10.0.zip`，**874,061 bytes**，SHA-256 **`4019b9edcf5d5fb108acc39725331ddf5854aab532b6e83572dd8fc2b0c6a49a`**。更新的 `2026-09-30-distribution.json` 和 `docs/downloads/distribution-sha256.txt` 是当前36包清单；前文872,687 bytes的完整包与哈希是历史记录。

版本保持0.10.0 / Beta；真实桌面发现到交付、Flash/Pro行为和macOS实机仍NOT_RUN。本轮不创建tag、Release、PR或main合并。推送结果随后追加。

本次10个暂存文件及完整包内成员按Git实际blob扫描 **255条目**，未发现规则覆盖的私钥、GitHub/API令牌、个人绝对路径、禁止目录或超过100 MB文件。代码/文档差异检查通过，未包含Web私有源码、二维码或原始个人运行日志。扫描记录只描述已检查规则，不替代人工内容核对。

### schema 补充实际推送结果

源码、schema测试、QA摘要和当前完整分发包提交：**`d96cbf571537ca09bbf5f048b9dd6afebbe1eb28`**（`Validate optional demo limitations and refresh beta package evidence`）。`git push origin HEAD:refs/heads/codex/public-skills` 成功；随后 `git ls-remote` 返回同一 SHA，核对时工作区干净。

[schema补充与完整包提交](https://github.com/arrizabalagags-png/BatteryReviewForge/commit/d96cbf571537ca09bbf5f048b9dd6afebbe1eb28)。本段随后的日志保存提交不改变已核验下载包字节；网站固定引用以最终已核对公开HEAD为准。用户已恢复后续任务，继续开发；ECS状态在私有托管记录独立核对。

## 完整绘图包与 EVAL 补修：第一批冻结快照

在已推送 `c61942f97baee6f93df62ac78e4c222ae82c73c2` 的基础上，保存以下已完成修改：

- 三个完整绘图包为不同连续曲线身份分配不同颜色；同一身份在全程图与放大图保持颜色一致。保留实线、无标记和四周框线规则。重名、透明、难以辨别或不足的颜色配置会停止并说明具体修正方法；当前颜色距离门槛是工程检查，不代表期刊认证或色觉障碍实测。
- 全电池绘图契约支持质量、面积和绝对容量单位；未提供 N/P 或 E/C 时保留未知状态，不强制用户填写，也不推断数值。
- 既有 65 个 workflow 用例文件保持原字节，新增 4 个明确标为合成材料的相反证据用例，总计 69 个。两个来源分别给出 +12 与 -7 个百分点的来源内效应；完整材料中的 NR 与缺少 Table S2 时的 NV 分开处理。
- 新 RUN_RECORD 使用 schema 2，记录完整安装 Skill 树、源 Skill 树、源提交及工作区差异摘要、准备与执行的 OS/架构、固定任务与独立预期的摘要。历史 schema 1 记录保留原状，不补造运行信息。包内 `SOURCE_PROVENANCE.json` 如实记录打包时的 `c61942f` 与 dirty 状态，并非将后来提交伪称为打包时的干净源。

实际定向验证 **14 tests PASS**：7 个绘图包用例 / 90.957 s，1 个实际解压全电池单位和可省略条件用例 / 6.852 s，6 个 EVAL/provenance 与续跑漂移检查 / 15.819 s。另实际解压运行 3 个 recipe ZIP，检查 PDF、PNG、SVG、LZW TIFF 以及输入 SHA 不变；完整 ZIP 内 CLI 的 69 case validate/prepare 和新运行记录准备通过。详细可公开证据见 `2026-09-30-recipe-eval-followup.json`。早前 **129 tests / 257.400 s** 是本补修前的完整回归，本批没有声称重新执行该回归。

上传时再次实际执行分发门禁：**36 ZIP / 62 解压 Skill 引用与 AST / 30 canonical schema-source-site-ZIP PASS**。当前完整包与三个 recipe 为：

| 包 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `BatteryReviewForge-v0.10.0.zip` | 896,181 | `0fee3b85e2e59702ad1cc02a62f356fb71bc83bb5c94d9c7a374300f44dcdac0` |
| `VoltPeer-full_cell-0.10.0.zip` | 220,158 | `adcbb8f232b216f218d594220c8bc906ffa2cd5e320727f87f720d3fb87716ac` |
| `VoltPeer-li_li-0.10.0.zip` | 273,010 | `43ce075559f65146fc95cc027c9539aae56d6181fed8540b0bc579607189ab84` |
| `VoltPeer-operando_xrd-0.10.0.zip` | 156,127 | `56a1b7077342eba658bdf3f857d5e605c4b3ced2dad2e5bb3e535a87a73019ee` |

其余 32 个下载 ZIP 保持原大小和 SHA。所有包以 `docs/downloads/distribution-sha256.txt` 和 `2026-09-30-distribution.json` 为准；前文完整包、recipe 哈希仅为历史记录。

本批仅公开绘图包运行时、契约、EVAL 工具、合成测试材料、分发和公开摘要；不包含私有网站、二维码、原始研究数据或个人原始日志。0.10.0 保持 Beta；真实 Harness 发现到交付、Flash/Pro 模型行为、macOS 实机仍 **NOT_RUN**，科学内容仍待作者审阅。后续中文标签与字体 cmap 小补修另行记录；本批没有把该未完成工作记为通过。未创建 tag、Release、PR 或 main 合并，未发布上海 ECS。
