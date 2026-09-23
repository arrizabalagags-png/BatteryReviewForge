# v0.8.0 网站与样图库验收记录

核对日期：2026-09-23。此记录只说明本次产品演示、文件完整性和前端流程的检查结果，不代替领域作者对真实实验数据的审核。

## 信息架构：修改前后

| 修改前 | 修改后 |
| --- | --- |
| 首页同时出现三套首次使用选择，最终给出一段 Prompt | 首页只解释产品、展示成品、引向四步上手 |
| `start.html`：材料 → 目标 → Prompt；“上一步”依赖浏览器历史 | `start.html`：软件 → 系统 → 安装 → 下载数据试运行；内部状态机控制上一/下一步，URL 可分享 |
| `index.html`, `start.html`, `guide.html`, `developers.html`, `disclaimer.html` | 新增 `features.html`, `gallery.html`, `learn.html`, `community.html`, `contribute.html`, `support.html`, `roadmap.html`；保留并重写旧页 |
| 首页混入旧版 synthetic 布局练习与开发说明 | 首页仅展示六张重新生成的 synthetic 产品演示；旧练习保留为历史/测试素材 |
| 技术文档和 GitHub 承担普通用户导航 | 普通用户留在站内完成选择、下载和学习；源码集中在开发者入口 |

## 图件检查

- `examples/showcase/` 有七类数据先行的样例：全电池、Li‖Cu、Li‖Li、EIS、Operando XRD、ToF-SIMS、综合研究。每类保留生成脚本、磁盘 CSV 输入、绘图脚本、SVG、PDF、PNG 和 `metadata.json`。
- EIS 公开模型参数 `Rs + (Rct‖CPE) + semi-infinite Warburg`；ToF-SIMS 的三通道图、叠加图和深度曲线来自同一空间/时间模型；综合 Figure 复用相同 A/B 身份和源 CSV。
- 核对了七张 PNG 的图面，并解析了七张 SVG。七张 PDF 均通过 `audit_pdf_fonts.py --expect Arial`，实际仅嵌入 Arial 字族。最终物理宽度为 180 mm；这只是设计目标，投稿前仍需按具体期刊复核。
- 四个定量一致性检查通过：全电池选定电压曲线终点与同圈容量一致；Li‖Cu 代表曲线与逐圈 CE 一致；EIS 复阻抗可由声明的等效电路重算；综合图使用存在的共享源数据。
- 首页和 Gallery 的每张图近旁标注 `synthetic demo / 非实验数据`。它们只能演示绘图能力，不能作为真实电池性能或机制证据。

## 网页与下载检查

- 本地浏览器逐页打开 12 个 HTML 页面，均出现预期一级标题。
- 实际从首页走通 Codex → Windows → 安装 → 试运行；“上一步”返回安装；刷新保留状态；直接打开 `?client=codex&os=windows&step=test#assembly` 显示六图练习。
- 桌面搜索“库伦效率”按“开始做 → 样图 → 学习 → 功能 → 开发者”分组，修复了 `CE` 误匹配 `cell` 的问题。搜索仅在浏览器读取本地 `search-index.json`。
- 在 390 px 手机视口检查首页和上手页；恢复桌面视口。所有本地链接与锚点、Gallery 文件、两种 v0.8.0 安装 ZIP 经测试通过。拼图 ZIP 有六张由同一 synthetic study 导出的独立 panel。
- 全部 Python 单元测试：41 项通过。`docs/start.js`、`docs/product.js` 通过 Node 语法检查。

## 仍需继续做

1. Kimi Code、DeepSeek Harness、WorkBuddy 的完整成图/拼版任务仍需真实客户端验收；目前页面区分了“方法已核对”与“本机已验证”。
2. 当前作品全部是 synthetic product demos。引入公开且许可清楚的真实 source data 后，还需逐条核对来源与许可，不能把当前曲线当实验事实。
3. 论文投稿图仍需使用者核对原始数据、实验条件、材料身份、图注和目标期刊要求。本站的视觉复核不等于领域专家审稿。
4. 网页产品流程当前以中文为主；README 和技能说明中英双语，完整英文网页仍可由社区继续补齐。
