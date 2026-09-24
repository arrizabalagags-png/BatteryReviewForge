# v0.8.4 新手路径与样图验收

这份记录说明本次改了什么、怎样复查，也说明哪些体验尚未实测。网站是静态介绍和下载页，不接收用户实验文件。

## 首页与上手

- [原六配色预览](assets/gallery/style-preview.svg)留在 README，并作为首页主视觉。它是用户明确喜欢的图，不再被称作过时素材。
- [同一份数据的六套风格](assets/showcase/style_presets/figure.svg)另设图库入口，六幅图都读取相同的 `data.csv`，横轴 0–500 圈、纵轴 130–190 mAh g⁻¹；只改变颜色和线型。每套还可单独下载 SVG。
- “开始使用”先问有没有安装能读取本地技能的 AI 软件。选择“没有”或“不确定”会先看到官方软件入口；再选择软件、系统、安装和演示任务。网址记录当前步骤，浏览器返回与前进能复原状态。
- 390 px 手机视口和桌面视口的首页、图库、上手首屏已用浏览器检查；手机上六套风格按一列显示。搜索“库伦效率”会到相应任务入口。

## 对照图件

| 问题 | 修改前 | 修改后 | 检查重点 |
| --- | --- | --- | --- |
| 十面板上方嵌套图过小、两大行之间留白过多 | [旧图](assets/audit/v0.8.4/capability_spread-before.png) | [新图](assets/audit/v0.8.4/capability_spread-after.png) | 十个独立面板按 2×5 尺规排列，未暗示它们来自同一实验 |
| ToF-SIMS 四张 map 边界不齐、色条挤占绘图区 | [旧图](assets/audit/v0.8.4/tof_sims-before.png) | [新图](assets/audit/v0.8.4/tof_sims-after.png) | 四张离子图同排，下面是同一模型的 sputter-time 趋势；时间不冒充深度 |
| 软包热图周围有过多空白 | [旧图](assets/audit/v0.8.4/pouch_thermal-before.png) | [新图](assets/audit/v0.8.4/pouch_thermal-after.png) | 热图、位置截线、温度变化仍保留同一模拟来源 |

三张图可由 `examples/showcase/build.py` 重建，源码旁保留 CSV、SVG、PDF、PNG、`metadata.json` 与 `alignment.json`。`alignment.json` 记录最终物理尺寸中绘图区边界的尺规检查；独立面板的科学关系仍须按各图数据说明理解。

## 拼图技能

`battery-figure-assemble` 新增内容框估计和内容占位检查：按素材宽高比规划行高，分别报告面板内容填充率、面板间缝隙与外部留白。几何对齐通过以后，仍会给出可读性提示；低填充或过大的间距不会被误称为“美观已通过”。

## 已验证与待验证

- 自动化测试：项目 `python -m unittest discover -s tests -p 'test_*.py'`；安装 ZIP 做过本地解压及重复安装冲突检查。
- 浏览器手动检查：390 px 和桌面视口、新访客上手入口、返回/前进、任务搜索及图库链接。
- 尚未在真实 WorkBuddy、Kimi Code、DeepSeek Harness 客户端完成从安装到出图的整条链路；各平台页面只写已核实的导入方式和当前状态。
- 未声称“完全不用终端”已在每个系统跑通；Windows 125% 系统显示缩放、无障碍辅助技术与强制阻断剪贴板权限的情形还未做完整实机验收。
- 样图均为 `synthetic_demo`。可下载演示数据用来验证流程，不能作为实验结果或论文论证。
