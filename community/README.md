# Battery Commons Registry

大家做出来，大家一起用，大家继续改。

这是**经过审核才会公开的静态资源库**，不是上传后让模型自动学习的数据库。第一阶段只接收无可执行代码的配色 JSON、布局 JSON，以及明确允许公开的示例。作者的未发表数据、第三方论文图片和个人信息不要提交到公开 Issue。

状态：`community`（投稿格式通过）→ `reviewed`（人工看过）→ `verified`（自动与人工检查均通过）→ `core`（进入正式发行版）。收藏数与科学适用性分开记录；没有人工检查就不显示 Verified。

提交前请阅读 [贡献说明](../CONTRIBUTING.md)。现阶段可使用 GitHub Issue 的“提交配色”或“提交布局”模板。`scripts/build_community_registry.py` 会检查 ID、版本、许可、颜色、面板结构和预览，并生成 `catalog.json` 与供 GitHub Pages 使用的 `docs/commons/`。发布过的 `id@version` 不可修改；要调整就新增版本。它的色觉模拟只是自动筛查，不能代替真人在最终图尺寸下检查。

技能默认只用发行包内的六套稳定风格。仅在使用者明确要求“查看社区资源”或“使用某个社区配色”时，才读取此目录或公开 catalog。选定资源必须锁定 `id@version` 并记录 SHA-256。**绝不下载并运行社区 Python 文件。**
