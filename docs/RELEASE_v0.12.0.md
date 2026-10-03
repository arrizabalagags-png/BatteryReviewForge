# VoltPeer v0.12.0 Beta

当前开发源码包含 **16 个 `voltpeer-*` Skill**，其中包括机理示意。推荐首次绘图使用下方 Starter；它只包含一个绘图 Skill，不是全部技能包。

## 当前下载

截至 2026-10-03，以下 0.12.0 Beta 包已公开在仓库 main 和 codex/public-skills 分支。包修订为 `cycling-rule-v1.2.1`；示例资源修订为 `cycling-rule-v1.2.0`。它们不是新的完整正式 GitHub Release。

| 包类型 | 内容与入口 |
| --- | --- |
| 绘图 Starter | [一个绘图 Skill、固定 Python 程序及合成 Demo](assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip)；完整解压，先读 `plot_starter/AGENT_GUIDE.md` |
| 全部技能包 | [16 个 Skill 与安装器](downloads/v0.12.0-cycling-rule-v1.2.1/VoltPeer-v0.12.0.zip)；按任务安装，不等于全部功能已完成客户端实测 |
| 单 Skill 包 | [包名与 SHA-256 索引](downloads/v0.12.0-cycling-rule-v1.2.1/download-index.json)中的 `single/`；数据导入要出图还需绘图 Skill |
| 示例源码包 | [多面板示例源码与数据](assets/cycling-rule-v1.2.0/split-demos/integrated_study/integrated_study-source.zip)；供重画和学习，不代替技能安装 |

推荐绘图 Starter：743,774 bytes，SHA-256：

```text
289b1d3a2e37fd11c8c3955fc3be1394b21abfb3a0c676bfeb06fb72344979df
```

全部技能包：1,205,664 bytes，SHA-256：

```text
f242306ceeac28890622a83ceb073760946fee8179e6cf5b355370856cd9b063
```

这两个文件的仓库下载字节、ZIP 结构、版本、技能清单和校验值已分别核对。GitHub 主分支上可下载 Beta 包，不表示模型或原生客户端已全部验证。

## 状态与验证范围

- 当前源码：0.12.0 Beta，16 个技能目录。
- 推荐包：0.12.0 Beta 绘图 Starter，内含一个 `voltpeer-plot`；全部技能包另行提供。
- GitHub 最近的完整正式 Release：[v0.9.2](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/tag/v0.9.2)，保留原名称和原发布资产。
- 当前工程检查：[交付记录](validation/2026-10-03-cycling-delivery.json)记录包结构、独立拷贝和本地程序执行；它不证明各客户端或模型已完成端到端测试。
- 当前原生桌面技能发现到交付、Flash/Pro 完整行为验证仍未完成；0.10.1 与早期 API 测试只适用于各自的固定版本。见[软件适配](COMPATIBILITY.md)。
- 本次仓库说明更新没有执行 ECS 部署，也没有核实正式站的完整发布身份。社区服务器需要单独安装，不随静态网站 ZIP 自动启动。

下载索引中的 `publication: LOCAL_CANDIDATE_NOT_PUSHED_NOT_DEPLOYED` 是**打包时保存的快照**，本次不改写该索引、冻结 ZIP 或其校验值。当前公开状态看本页与 [RELEASE_STATUS.json](RELEASE_STATUS.json)；来源提交和 GitHub 回读见[同步记录](validation/GITHUB_SYNC_2026-10-03.md)。历史的“未推送”不能据此推断现在的包不可下载，源码推送也不能据此证明 ECS 已更新。

网站提供的合成教学示例、200 套配色、机理 SVG 与源码按各资源说明使用；支持的普通数据图型与投稿要求见[入门指南](GETTING_STARTED.md)。未完成的科学信息不得用示例条件补齐。

## 历史版本

[0.11.0 版本说明](RELEASE_v0.11.0.md) · [0.11.0 绘图 Starter](downloads/v0.11.0/starter/VoltPeer-Plot-Starter-v0.11.0.zip) · [0.11.0 全部 15 个技能包](downloads/v0.11.0/VoltPeer-v0.11.0.zip)

[0.10.1 固定 Starter](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip) · [0.10.1 版本说明](RELEASE_v0.10.1.md) · [0.9.2 正式发布](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/tag/v0.9.2)

这些旧包与测试维持原版本、名称和校验值。当前引用文件描述公开的 0.12.0 Beta 源码，不代表 0.12.0 已成为正式 Release。

## English

The current source is **0.12.0 Beta with 16 Skills**. The recommended plotting Starter contains **one plotting Skill**, a fixed program and synthetic demos. The full package and individual Skill archives are separate downloads. Package revision `cycling-rule-v1.2.1` and example revision `cycling-rule-v1.2.0` retain their recorded identities.

The Beta packages are public on the repository's main and development branches. The latest full stable GitHub Release is still **v0.9.2**. Both recommended ZIP files have been checked against their actual downloaded bytes, manifests, Skill lists and SHA-256 values above.

The index preserves its build-time publication field. This page and the current status file describe availability separately, without rewriting frozen packages or historical tests. Current native desktop discovery through delivery and full Flash/Pro behavior testing remain incomplete. Earlier tests apply only to their recorded versions. This documentation update did not deploy or verify the full ECS release; the community backend requires a separate installation.
