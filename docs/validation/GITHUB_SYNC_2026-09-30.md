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
