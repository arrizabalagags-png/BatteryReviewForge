# v0.8.1 网站体验与问题验收

核对日期：2026-09-24。基线问题来自 v0.8.0 源码检查与用户反馈；修复结果在本地静态站 `http://127.0.0.1:8765/` 的浏览器中验证。这里区分“源码发现的问题”和“浏览器里实际跑过的路径”，避免把未测的软件写成已验证。

## 这版交付

- 首页用项目自身生成的 `integrated_study`、Li‖Cu CE、Operando XRD、ToF-SIMS 图做工作台式展示；所有图保持 **synthetic demo，非实验数据** 标记。首页精选采用一张主图加四张辅助图，保留原始 CSV、SVG、PDF 下载入口。
- 上手页在桌面和手机首屏直接出现软件选项。任务链接只传 `task`，由使用者自己选软件与系统。WorkBuddy 走“选软件 → 导入 → 试运行”。
- 新增焦点可见样式、搜索加载/失败/重试状态、SVG favicon、固定尺寸图片、移动菜单关闭逻辑及安装命令复制退路。
- 版本下载：[完整 ZIP](downloads/BatteryReviewForge-v0.8.1.zip)、[WorkBuddy 专用合集](downloads/BatteryReviewForge-WorkBuddy-v0.8.1.zip)。[网站地图](SITEMAP.md)列出了每页用途。

## P0：会把新手带错路或给出错误状态

| 编号 | 基线复现与预期 | 修复 | v0.8.1 验证 |
| --- | --- | --- | --- |
| P0-1 | 首页、功能页和搜索中的任务入口曾固定 `client=codex&os=windows`；Mac/Kimi 用户点任务不应被改成 Codex/Windows。 | 改为 `start.html?task=...`；平台只在向导里选择。 | 静态链接扫描无该固定参数；浏览器打开 `?task=assembly` 后仍停在软件选择。 |
| P0-2 | WorkBuddy 的界面导入原本多问一次电脑系统；系统不参与导入。 | WorkBuddy 路由改为 `client → install → test`，进度条隐藏系统。 | 浏览器点 WorkBuddy 后 URL 为 `?client=workbuddy&step=install`，没有 `os`，进度为三步；拼图任务到试运行时突出六图拼版。 |
| P0-3 | “Codex 本机已验证”原本不分系统；不应把 Windows 结果套给 macOS/Linux。 | 显式软件 × 系统状态表；仅 Codex/Windows 写已验证，其他标明待实测。 | 浏览器 Codex/Windows 安装页显示 Windows 状态；非法 `os=freebsd` 直达链接被送回系统选择，不生成命令。 |
| P0-4 | 复制命令原本只调现代 Clipboard API，拒绝时会直接失败。 | 现代 API 拒绝后试旧版复制；两者都失败时显示可手动选中的文字框。 | 用 `tests/clipboard_policy_server.py` 的 `Permissions-Policy: clipboard-write=()` 实际禁用现代写入；点击后旧版复制成功，把内容粘贴到搜索框得到 `.\install.ps1`。双重拒绝时的手动框已由代码路径覆盖，尚未在浏览器中强制触发。 |

## P1：影响实际操作和可理解性

| 编号 | 基线复现与预期 | 修复 | v0.8.1 验证 |
| --- | --- | --- | --- |
| P1-1 | 上手页顶部宣传区过高，选项落在首屏之外。 | 改为紧凑标题与进度。 | 1440×900 第一张软件选项顶部约 523 px（含“继续使用”和任务提示）；390×844 约 512 px，均在首屏。 |
| P1-2 | 第一页卡片曾塞进详细 QA 状态。 | 卡片仅显示推荐、Beta 或界面导入；完整状态放兼容说明。 | 桌面与手机截图目视检查。 |
| P1-3 | 重新进入必须重选软件、系统。 | `preferredClient`、`preferredOS` 存入 localStorage，提供“继续使用…”按钮。 | 浏览器选择 WorkBuddy 后重新进入可见“继续使用 WorkBuddy”；任务参数仍保留。 |
| P1-4 | 直达 URL 和浏览器历史可能与可见步骤脱节。 | 统一 `task/client/os/step` 状态、路由守卫、URL 同步及 `popstate`。 | Codex/Windows 安装 → 试运行 → 浏览器后退/前进 → 刷新均保持正确面板；直达 CE 试运行能突出 CE 示例。 |
| P1-5 | 搜索弹窗声明为 modal，背景仍可能被键盘选中。 | 打开时设置 `header/main/footer` inert、锁滚动、循环焦点；关闭后回到触发按钮。 | 浏览器检查 `main[inert]`、搜索内 Shift+Tab 环绕、Esc 关闭后焦点回搜索按钮。 |
| P1-6 | 手机菜单按 Esc、点外部或点链接不能可靠收起。 | 三种动作统一调用关闭逻辑，维护 `aria-expanded`。 | 390×844 下分别操作三种动作，状态由 `true` 回到 `false`。 |
| P1-7 | 图片未指定尺寸，首屏可能跳动。 | 首页与样图库图片写原始宽高及异步解码，容器保持比例。 | HTML 解析测试检查所有 `<img>` 的宽高；四个断点均无横向溢出。 |
| P1-8 | `button` 未显式声明类型。 | 页面按钮统一 `type="button"`。 | HTML 解析测试覆盖 12 个页面。 |

## P2：细节与健壮性

| 编号 | 基线复现与预期 | 修复 | v0.8.1 验证 |
| --- | --- | --- | --- |
| P2-1 | 键盘焦点不明显。 | 全站高对比 `:focus-visible`。 | 手机宽度键盘 Tab 首次落在“跳到正文”，计算样式为实线轮廓。 |
| P2-2 | 未加载的字体名称造成不同机器随机回退。 | 使用系统字体栈。 | CSS 检查；跨操作系统的实际字形仍需志愿者复核。 |
| P2-3 | 搜索索引加载失败时像是无结果。 | 显示加载、失败和重试。 | 测试服务器首次返回 503，浏览器显示“搜索内容加载失败，请重试”；点击重试后 CE 结果正常出现。 |
| P2-4 | 1024 px 就切手机菜单、普通笔记本导航显得拥挤。 | 901–1080 px 用 13 px 紧凑导航，≤900 px 用菜单。 | 1024×768 导航完整显示，页面无横向溢出。 |
| P2-5 | 浏览器请求 `favicon.ico` 返回 404。 | 添加与页面标记一致的原创 SVG favicon。 | 本地服务器返回 `/favicon.svg` 200。 |

## 浏览器与代码验收

- 实际视口：1920×1080、1440×900、1024×768、390×844。四者 `document.documentElement.scrollWidth - innerWidth` 均为 -15 px（仅滚动条占位，没有横向内容溢出）。
- 实际路线：首页 → Codex → Windows → 安装 → 试运行；首页拼图任务 → WorkBuddy → 导入 → 六图演示；搜索“CE”与“拼图”；非法系统、直达链接、后退、前进、刷新、手机菜单、搜索 Esc 和焦点循环。
- 自动化检查：`python -m unittest discover -s tests -v` 共 41 项通过；`node --check docs/start.js`、`node --check docs/product.js` 通过；站内 12 页本地链接与锚点检查通过。
- 截图：[1440 首页](assets/qa/home-desktop-1440.png)、[1920 首页](assets/qa/home-wide-1920.png)、[1024 首页](assets/qa/home-tablet-1024.png)、[390 首页](assets/qa/home-mobile-390.png)、[1440 上手页](assets/qa/start-desktop-1440.png)、[390 上手页](assets/qa/start-mobile-390.png)。

## 还没有冒充“已完成”的部分

1. **实际宿主任务链**：Kimi Code、DeepSeek Harness、WorkBuddy 和 Codex macOS/Linux 仍需在各自客户端完成从导入到出图的实机验收。网页如实标注 Beta 或待实测。
2. **双重剪贴板拒绝**：现代 API 被浏览器策略拒绝时的旧版复制已实测；旧版复制同时被禁用时的手动文字框逻辑尚待在该环境实测。
3. **真实科研数据**：首页样图均为可复现的 synthetic demo；这一轮只修网站体验，没有把它们宣称为真实论文实验结果。
4. **Before/After 拼图展示**：当前尚无足以代表最终质量的公开对照图，因此没有把半成品放进首页。
