# 公开仓库入口更新 · 2026-10-01

本记录对应 `main` 的文档更新。实际能力与包版本仍按原发布说明和适配证据核对；本轮没有升级或重新打包技能。

## 仓库名称与主页

按用户明确要求，公开仓库改名为 [`arrizabalagags-png/Voltpeer-skills`](https://github.com/arrizabalagags-png/Voltpeer-skills)。仓库 ID 仍为 `1382773044`，可见性为 public，默认分支仍为 `main`；变更前已核对所有者管理权限和新名字不存在。

- About：VoltPeer · 电研搭子｜电池科研 AI Skills：绘图与拼版、数据整理、文献核验和综述写作。Open tools for battery data, figures and evidence.
- Homepage：<https://dazi.gsarrizabalaga.xyz/>。
- Topics：`ai-skills`、`battery-research`、`figure-assembly`、`literature-review`、`python`、`scientific-visualization`。
- 本机公共 Git `origin` 已改为 `https://github.com/arrizabalagags-png/Voltpeer-skills.git`。本轮没有移动工作目录或更改技术 Skill ID / 旧包名。

旧仓库 URL 与旧 `v0.9.2` Release URL 的实际 HTTP 结果均为 301 到新名称，最终 200；旧 API 地址回读得到相同仓库 ID。`/releases/latest` 实际仍指向 `v0.9.2`。后续入口使用 canonical 新名称，不依赖工具接受重定向。

## README 与资料位置

- [README.md](../README.md)：中文主首页。先说明用途和提供开始 / 看效果 / 下载入口，再给六个科研任务和已有合成示例。
- [README.en.md](../README.en.md)：独立英文版本；两套全文不连续堆在首页。
- 四张图来自固定公开提交 `dfd46fcb4a3255b60826de8a4c721963adc4ff02` 的 CE、容量循环、电化学阻抗和关联六面板示例。数据、脚本、`synthetic_demo` 元数据与项目 MIT 许可均可核查；README 明示非实验数据。没有新造图片或科学结论。
- 新手只优先走 DeepSeek Harness 桌面端：下载软件、配置模型、打开项目、完整解压绘图包、按 `AGENT_GUIDE.md` 安装 / 跑 Demo、核对结果后换作者数据。Python / 依赖 / 费用真实要求留在[入门指南](GETTING_STARTED.md)与当前一步。
- 熟练用户直接下载；其他客户端和全部 15 个 Skill 表折叠。五条短请求保留原始值、单位、测试条件和来源核查要求。
- 本分支原技术全文完整迁入 [TECHNICAL_REFERENCE_v0.9.2.md](TECHNICAL_REFERENCE_v0.9.2.md)：安装、覆盖规则、图型 / grammar、素材 / publisher profile、PDF 字体检查、回归和审计细节均保留。只有相对文档链接改为原固定提交、换行统一；完整正文保留已做程序对照。

`main` 的 `.codex-plugin/plugin.json` / `CITATION.cff` 仍为 0.9.2，GitHub 正式 Release 的 `draft` 和 `prerelease` 均为 false。首页称其“正式技能包 / 保留基线”，没有据此断言全部宿主或科学规则获得 Stable 认证。`codex/public-skills` 仍是 0.10.1 Beta。两个首页各只保留一处集中版本 / 验证范围：原生桌面发现与完整行为验收待验证，Flash 有限 API 交付表达 PARTIAL 保留。

`CITATION.cff` 仅将 `repository-code` 改到新 URL；作者、题名、版本与日期保留。新 [SUPPORT.md](../SUPPORT.md)复用已有代码 / 电池科学 / 文档 / 共建 Issue 表单，未重复增加表单；[PR 模板](../.github/PULL_REQUEST_TEMPLATE.md)记录修改、原因、实际验证、科学条件和分享权利。

[SECURITY.md](../SECURITY.md)明确记录 GitHub 私密漏洞报告实查未启用，没有指定安全邮箱。只建议先提出不含敏感细节的联系请求，确认渠道后再私下分享；没有编造私密入口或安全保障。

## 链接、渲染与保留门禁

完整去敏证据见 [repository-readme.json](validation/2026-10-01-repository-readme.json)。实际执行：

- 两分支新文档与全文归档合计 **535** 处 Markdown / 图片链接目标及标题检查通过；固定源链接在实际 Git 树中存在。
- 两分支中、英共四份 README 调用 GitHub GFM 渲染成功：每份 4 图片、5 表格、2 折叠块、5 条可复制请求。每张预览的远端 PNG 还与本地固定图件逐字节相同。
- 手动安装示例的 `check` / `setup` / `install --host dsh --workspace` / `demo` 命令与冻结包中的实际 `AGENT_GUIDE.md` 对照通过。
- **137 个**现有 ZIP 大小及 SHA-256 与改名前清单逐一相同；**14 个 Release** 的选择字段与全部资产 ID / 名称 / 大小 / digest / 更新时刻相同，**20 个 tag** 名称与提交目标相同。没有覆盖或重建历史及当前包。
- 新 canonical URL 实际下载绘图 Starter：580,632 bytes，SHA-256 `392b58b6a211c35f88a0148c95d07b9accb5b6eeb000640883466d96d3ab466a`；正式完整包：678,776 bytes，SHA-256 `6128192925a0f918206172b6913cefc471296f3245956c1f5de38339036eedc4`，均与冻结包一致。

第一次访问路线仅做入口文字、顺序和渲染结构的人工检查：先看用途和效果，然后推荐安装，再找技术细节。**没有进行真人计时或记录任何“10 秒 / 3 分钟成功”实验。** 本轮也没有重跑模型、69 项行为 EVAL 或全部数值回归。

## Pages 与正式站的区别

GitHub 官方说明仓库改名会转发多数仓库 URL，但项目 Pages URL 是例外；不要据仓库重定向推断 Pages 同样转发。[GitHub 官方改名说明](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)。

本轮实际 HTTP 核对：

| 项目地址 | 实际结果 |
| --- | --- |
| `https://arrizabalagags-png.github.io/BatteryReviewForge/` | 404，没有转发 |
| `https://arrizabalagags-png.github.io/Voltpeer-skills/` | 301 到 `https://dazi.gsarrizabalaga.xyz/`，最终 200 |

Pages API 的 `cname`、`html_url`、`build_type`、`source`、`status`、`public` 与改名前相同。保留的工作流只有 `workflow_dispatch`；本轮没有改 Pages 设置、改 DNS 或手动触发网站部署。GitHub 社交预览现有 HTML 为自动 `opengraph.githubassets.com` 新仓库 URL，未上传新预览图；历史 `assets/brand.svg` 未改。

正式站继续由已有 ECS 发布流程维护。仓库改名、文档提交和 GitHub 推送本身不代表 ECS 网站更新。本轮不读取服务器私钥，不操作服务器、Nginx、证书或其他站点。
