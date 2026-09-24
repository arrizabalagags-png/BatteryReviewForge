# v0.8.3 网站问题验收

本轮用本地构建站点 `http://127.0.0.1:8766/` 做浏览器检查，随后运行 `python -m unittest discover -s tests -v`。这里记录实际动作和结果；GitHub Pages 发布后的 CDN 缓存与第三方 Agent 客户端仍需另看线上状态。

| 项目 | 实际操作 / 可复现检查 | 结果 |
| --- | --- | --- |
| 上手 URL 状态 | 从 `start.html?task=full` 选 Codex、Windows；网址依次带 `task=full&client=codex&step=os`、`...&os=windows&step=install` | 页面、网址同步 |
| 前进、后退、刷新 | 在安装步骤用浏览器 Back、Forward、Reload；分别显示系统选择、安装、安装 | 通过，已选择任务与软件未丢 |
| 搜索与锚点 | 搜“热图”，点“软包温度热图” | 到 `gallery.html#pouch_thermal`，对应图卡显示 |
| 搜索异常处理 | 代码检查 `fetch` 非 OK 和无效 JSON 的重试入口；已有测试覆盖脚本文字与本地索引 | 逻辑存在；未模拟断网浏览器操作 |
| 下载与图件 | 逐页解析所有本地 `href/src` 与 HTML 锚点；13 图的 SVG/PDF/PNG/metadata/来源逐项存在；两个 0.8.3 ZIP 可打开并核对 13 个 skill | 本地通过；发布后图库、十面板 SVG/QA、两个 ZIP 的 HTTP HEAD 均为 200 |
| 中英文检索词 | 索引含库伦效率/CE、阻抗/EIS、拼图/assembly、全电池/full cell，新增 thermal、benchmark、rate、GCD、matrix | 索引/同义词检查通过；“热图”实际检索通过 |
| 手机排版 | 浏览器分别设 320/375/390/430 px；比较 `documentElement.scrollWidth` 和 `clientWidth`，无页面横向溢出 | 通过；主按钮约 50 px、菜单 44 px |
| 菜单与键盘 | 320 px 打开菜单，按 Esc 收回；搜索可打开、输入、点结果 | 通过；已存在焦点可见样式与对话框 Tab 循环实现 |
| 版本与资源 | 插件、引用、安装文档、ZIP、页面 `data-version` 均为 0.8.3；`start.js` 从页面版本动态选 ZIP | 本地通过 |
| 内容一致性 | 首页只有画图、拼图、样例入口；综述保留在次级页。每张图近旁标 `Synthetic demo · 非实验数据`，不把兼容路径写成完整实机验证 | 通过 |

**发现并修复。** 新图库最初只在绘图目录生成，网站未索引，且首页仍显眼介绍综述。本轮补了 gallery、搜索词、首页展示与手机图，编写新图元数据。第一次全量测试发现文档链接尚未创建，以及倍率测试把 CSV 的字符串圈数与整数集合比较；分别创建审计文档并修正测试。图片容器宽度随手机收缩，无额外横向滚动。

**线上复查。** 发布后首页返回 200 且包含 `v0.8.3`；软包温度图 `metadata.json` 返回 200 且含 `synthetic_demo`。图库、十面板 SVG/对齐 JSON、Codex 完整 ZIP、WorkBuddy ZIP 的 HEAD 也返回 200。这是一次可用性快照，CDN 在不同地区可能仍有短暂缓存。

**边界。** 自动链接检查验证本地文件存在，不代表外部网页永远可达。浏览器尚未穷尽屏幕阅读器和全部系统组合；Kimi Code、WorkBuddy、DeepSeek Harness 的完整成图仍依兼容性页标为待实测。
