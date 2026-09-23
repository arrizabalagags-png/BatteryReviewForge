# -*- coding: utf-8 -*-
"""Build the public, beginner-facing static site from one navigation and content map."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
VERSION = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
GITHUB = "https://github.com/arrizabalagags-png/BatteryReviewForge"
NAV = [
    ("开始使用", "start.html"), ("功能", "features.html"), ("样图库", "gallery.html"),
    ("学习", "learn.html"), ("社区", "community.html"),
    ("参与贡献", "contribute.html"), ("支持项目", "support.html"),
]
SHOWCASE = [
    ("full_cell", "NMC811‖Li 全电池长循环", "循环容量与选定圈数电压曲线，来自同一套演示状态。"),
    ("li_cu_ce", "Li‖Cu 逐圈库伦效率", "逐圈 CE 与对应容量过程；保留后期波动。"),
    ("operando_xrd", "Operando XRD", "峰位、峰强随 SOC 变化，并与电压使用同一 SOC 轴。"),
    ("tof_sims", "ToF-SIMS 空间与深度分布", "同一界面模型生成离子图与深度趋势。"),
    ("eis", "EIS Nyquist 与相位", "由声明的等效电路生成频率与复阻抗数据。"),
    ("integrated_study", "同一研究的六面板 Figure", "电解液 A/B 在 CE、对称电池、阻抗与全电池中保持一致。"),
]


def header() -> str:
    links = "".join(f'<a href="{url}">{label}</a>' for label, url in NAV)
    return f'''<a class="skip" href="#main">跳到正文</a><header class="topbar"><div class="wrap nav">
<a class="brand" href="index.html"><i></i>BatteryReviewForge</a><button class="menu-toggle" type="button" aria-label="打开菜单" aria-expanded="false">☰</button>
<nav class="navlinks" aria-label="主导航">{links}</nav><button class="search-trigger" type="button" data-open-search>⌕　搜索：CE、拼图、安装…</button>
</div></header>'''


def footer() -> str:
    return f'''<footer class="footer"><div class="wrap"><div class="footer-grid"><div><h3>BatteryReviewForge</h3><p>把画图和排版的重复劳动交给工具，把时间留给科研判断。</p><a href="start.html" class="text-link">开始使用 →</a></div>
<div><strong>探索</strong><a href="features.html">功能</a><a href="gallery.html">样图库</a><a href="learn.html">学习</a></div>
<div><strong>项目</strong><a href="community.html">社区</a><a href="roadmap.html">路线图与已知问题</a><a href="contribute.html">参与贡献</a><a href="support.html">支持维护</a></div>
<div><strong>技术资料</strong><a href="developers.html">开发者入口</a><a href="{GITHUB}">GitHub 源码 ↗</a><a href="disclaimer.html">数据与责任说明</a><a href="{GITHUB}/blob/main/CITATION.cff">引用本项目 ↗</a></div></div>
<small>v{VERSION} · MIT License · 郭硕、姜金龙合作 · 上海理工大学能源材料科学研究院。独立开源项目；机构名称仅说明作者工作单位。</small></div></footer>'''


def shell(title: str, description: str, body: str, extra_js: str = "") -> str:
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(description, quote=True)}"><title>{escape(title)} · BatteryReviewForge</title><link rel="stylesheet" href="product.css"></head><body>
{header()}<main id="main">{body}</main>{footer()}
<div class="search-panel" role="dialog" aria-label="站内搜索" aria-modal="true"><div class="search-box"><button class="search-close" type="button" aria-label="关闭搜索">×</button><label for="site-search-input">搜索站内内容</label><input id="site-search-input" type="search" placeholder="试试：库伦效率、EIS、拼图、安装"><div id="search-results" aria-live="polite"></div></div></div>
<script src="product.js" defer></script>{extra_js}</body></html>'''


def page_head(kicker: str, title: str, intro: str) -> str:
    return f'<div class="page-head"><div class="wrap"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{intro}</p></div></div>'


def gallery_card(item, wide=False) -> str:
    slug, title, description = item
    stem = f"assets/showcase/{slug}/"
    data_file = "data_index.csv" if slug == "integrated_study" else "data.csv"
    return f'''<article class="gallery-card{' wide' if wide else ''}"><a class="gallery-image" href="{stem}figure.svg" aria-label="查看{title}的 SVG"><img src="{stem}figure.png" alt="{title}：虚构演示数据生成的科研图" loading="lazy"></a>
<div class="gallery-caption"><div><span class="synthetic">Synthetic demo · 非实验数据</span><h3>{title}</h3><p>{description}</p></div><div class="gallery-links"><a href="{stem}{data_file}">CSV</a><a href="{stem}figure.svg">SVG</a><a href="{stem}figure.pdf">PDF</a><a href="{stem}metadata.json">数据说明</a></div></div></article>'''


def homepage() -> str:
    cards = "".join(gallery_card(item, item[0] in ("full_cell", "integrated_study")) for item in SHOWCASE)
    return f'''<div class="wrap hero"><div><div class="eyebrow">免费开源 · 电池科研工具</div><h1>把时间还给<br>研究。</h1><p>电池实验数据出图、论文 Figure 拼版、综述工作流。免费、开源，不需要先学 Python。</p>
<div class="hero-actions"><a class="btn teal" href="start.html">开始使用 <span aria-hidden="true">→</span></a><a class="btn secondary" href="gallery.html">看看样图</a></div><p class="hero-meta">v{VERSION} · MIT License · <a href="{GITHUB}">GitHub 源码 ↗</a></p></div>
<div class="hero-art"><img src="assets/showcase/full_cell/figure.png" alt="NMC811 与锂金属全电池长循环和电压曲线的合成演示图"><span class="synthetic">Synthetic demonstration · 非实验数据</span></div></div>
<section class="section"><div class="wrap"><div class="section-head"><div><div class="eyebrow">能做什么</div><h2>从手里的材料，走到可用的结果。</h2></div><a class="text-link" href="features.html">看全部功能 →</a></div><div class="feature-grid">
<div class="feature-item"><span class="num">01 / 数据</span><h3>数据 → 论文图</h3><p>读入 Excel、CSV 等文件，核对列名和单位，制作 CE、长循环、倍率、EIS 等图。</p><a class="text-link" href="gallery.html#full_cell">查看示例 →</a></div>
<div class="feature-item"><span class="num">02 / 散图</span><h3>散图 → 完整 Figure</h3><p>把已有图片拼齐：统一字母、字号、留白和阅读顺序，保留原始比例。</p><a class="text-link" href="start.html?client=codex&os=windows&step=test#assembly">试试拼图 →</a></div>
<div class="feature-item"><span class="num">03 / 综述</span><h3>题目 → 综述工作流</h3><p>从选题、找文献、核对证据，到写作、投稿与回复审稿意见。</p><a class="text-link" href="features.html#review">了解流程 →</a></div></div></div></section>
<section class="section soft"><div class="wrap"><div class="section-head"><div><div class="eyebrow">作品集</div><h2>看结果，比看说明快。</h2></div><a class="text-link" href="gallery.html">进入样图库 →</a></div><div class="gallery-grid">{cards}</div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><div class="eyebrow">三步上手</div><h2>第一次用，照着做就行。</h2></div></div><div class="steps"><div class="step"><h3>选你已经在用的软件</h3><p>Codex、Kimi Code、WorkBuddy 或 DeepSeek Harness。</p></div><div class="step"><h3>下载并安装</h3><p>选电脑系统后，我们只展示对应的一种安装办法。</p></div><div class="step"><h3>跑一份可下载的演示</h3><p>从全电池、Li‖Cu CE 或六图拼版开始，拿到第一张图。</p></div></div><div style="margin-top:30px"><a class="btn" href="start.html">带我开始 →</a></div></div></section>
<section class="section soft"><div class="wrap"><div class="eyebrow">一起维护</div><h2>工具越多人用，越该由大家一起改。</h2><p class="section-intro">懂电池、会画图、能写代码，或者只是愿意帮我们找出难懂的地方，都有适合的事。</p><p><a class="text-link" href="contribute.html">看看怎么参与 →</a>　　<a class="text-link" href="support.html">支持项目 →</a></p></div></section>'''


def start() -> str:
    return f'''{page_head('开始使用 / 4 步', '从第一次安装，到第一张图。', '选你使用的软件和电脑系统。安装好后，直接用我们准备的数据试一次。')}
<div class="wrap wizard"><div class="progress" aria-label="安装进度"><button type="button" data-progress-step="client">1 选软件</button> › <button type="button" data-progress-step="os">2 选系统</button> › <button type="button" data-progress-step="install">3 安装</button> › <button type="button" data-progress-step="test">4 试运行</button></div>
<section data-wizard-step="client"><h2>你准备用哪个软件？</h2><p>选你已经在用的；不需要为这个项目另外开账号。</p><div class="choices">
<button class="choice" data-choice-client="codex">Codex<small>本机已验证</small></button><button class="choice" data-choice-client="kimi">Kimi Code<small>技能目录已核对；完整任务待测试</small></button>
<button class="choice" data-choice-client="workbuddy">WorkBuddy<small>通过技能界面导入</small></button><button class="choice" data-choice-client="dsh">DeepSeek Harness<small>技能目录已核对；完整任务待测试</small></button></div><p class="small">豆包等其他软件的第三方导入机制尚待核实。<a class="text-link" href="learn.html#compatibility">查看当前适配状态</a></p></section>
<section data-wizard-step="os" hidden><h2>你的电脑是什么系统？</h2><p>选电脑系统，不是手机系统。</p><div class="choices"><button class="choice" data-choice-os="windows">Windows</button><button class="choice" data-choice-os="macos">macOS</button><button class="choice" data-choice-os="linux">Linux</button></div><div class="wizard-actions"><button class="ghost" data-wizard-back>← 上一步</button></div></section>
<section data-wizard-step="install" hidden><h2>安装到 <span id="current-client"></span> · <span id="current-os"></span></h2><p id="install-instruction"></p><p><a class="btn teal" id="install-download" href="downloads/BatteryReviewForge-v{VERSION}.zip">下载安装包</a></p><ol id="install-steps" class="prose"></ol><div class="command" id="install-command"></div><button class="ghost" data-copy="#install-command">复制</button><p class="small">适配状态：<span id="install-status"></span>。安装包不包含你的论文或数据。</p>
<details><summary>想看手动方法或遇到问题？</summary><p>查看<a class="text-link" href="learn.html#install">安装说明与常见问题</a>。已安装同名技能时，安装器会停下，不会擅自覆盖。</p></details><div class="wizard-actions"><button class="ghost" data-wizard-back>← 上一步</button><button class="btn" data-wizard-next="test">安装好了，试运行 →</button></div></section>
<section data-wizard-step="test" hidden><h2>用演示文件，画出第一张图。</h2><p>下面的数据都是清楚标注的虚构演示数据。下载、交给你的 Agent，再复制一句话即可开始。</p><div class="demo-list">
<article class="demo"><span class="pill">最简单</span><h3>全电池长循环</h3><p>看看循环容量和电压曲线如何配在一起。</p><a href="assets/showcase/full_cell/data.csv" download>下载 demo_full_cell.csv ↓</a><a href="assets/showcase/full_cell/voltage_profiles.csv" download>下载电压曲线数据 ↓</a><button class="ghost" data-copy="#demo-full">复制任务句</button></article>
<article class="demo"><span class="pill">进阶</span><h3>Li‖Cu CE</h3><p>逐圈库伦效率和对应电化学过程。</p><a href="assets/showcase/li_cu_ce/data.csv" download>下载 demo_li_cu_ce.csv ↓</a><a href="assets/showcase/li_cu_ce/profiles.csv" download>下载曲线数据 ↓</a><button class="ghost" data-copy="#demo-ce">复制任务句</button></article>
<article class="demo" id="assembly"><span class="pill">拼图</span><h3>六张图 → Figure</h3><p>下载六个独立 panel，试着拼成对齐的组合图。</p><a href="assets/showcase/assembly-demo.zip" download>下载 6 张 panel ↓</a><button class="ghost" data-copy="#demo-assemble">复制任务句</button></article></div>
<div hidden><span id="demo-full">请用 BatteryReviewForge 读取我上传的演示全电池 CSV，核对列名和单位，把长循环和选定圈数电压曲线画成可编辑 SVG。数据是 synthetic demo，不要当作实验结果。</span><span id="demo-ce">请用 BatteryReviewForge 读取我上传的 Li||Cu 演示 CSV，识别逐圈 CE 协议并画 CE 与代表性曲线。保留异常点，输出可编辑 SVG；不要把它当 Aurbach CE。</span><span id="demo-assemble">请用 battery-figure-assemble 将我上传的 6 张演示 panel 拼成 Figure。先检查内容与尺寸，再统一字母、间距和边界；不要给每张图加副标题。</span></div>
<p class="notice">这一步会在你自己的 Agent 中运行。本站只提供下载和说明，不接收你上传的数据；Agent 如何处理文件取决于你所使用的软件设置。<a href="disclaimer.html">了解更多</a></p><div class="wizard-actions"><button class="ghost" data-wizard-back>← 上一步</button><a class="btn secondary" href="learn.html">不会？看一步步教程 →</a></div></section></div>'''


def features() -> str:
    return page_head('功能', '一套工具，覆盖电池论文里最费时的活。', '从实验数据、论文图，到综述文章。你说手里有什么，工具就从对应步骤开始。') + '''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>用数据画图</h3><p>CE、全电池、半电池、对称电池、倍率、EIS、CV、XRD、ToF-SIMS 等；先检查列名、单位和实验协议。</p><a class="text-link" href="gallery.html">看样图 →</a></div><div class="row"><h3>把图片拼齐</h3><p>整理 PNG、TIFF、PDF、SVG；按最终投稿尺寸统一标签、间距与阅读顺序，输出可继续编辑的图。</p><a class="text-link" href="start.html?client=codex&os=windows&step=test#assembly">拿素材试试 →</a></div><div class="row" id="review"><h3>写电池综述</h3><p>选题、检索、证据核验、结构、写作、润色、投稿、返修，各阶段有独立技能。</p><a class="text-link" href="learn.html#review">看完整流程 →</a></div></div></section><section class="page-block soft"><div class="wrap prose"><h2>它会怎么帮你判断？</h2><p>它先看你给的资料和数据，再决定该调用哪个技能。遇到不清楚的测试条件、容量保持率分母或 Aurbach 协议，会把缺的信息指出来，而不是替你猜一个数。</p><p><a class="btn" href="start.html">从一个例子开始 →</a></p></div></section>'''


def gallery() -> str:
    cards = "".join(f'<div id="{item[0]}">{gallery_card(item)}</div>' for item in SHOWCASE)
    extra = gallery_card(("li_li", "Li‖Li 对称电池", "长时间极化变化与局部 plating/stripping 波形。"))
    return page_head('样图库', '图可以放大看，数据可以下载。', '每张都是由公开脚本生成的 synthetic demo，供练习与检验流程；不是任何真实论文的实验结果。') + f'''<section class="section"><div class="wrap"><div class="gallery-grid">{cards}<div id="li_li">{extra}</div></div></div></section><section class="page-block soft"><div class="wrap prose"><h2>想自己改一遍？</h2><p>每个示例都保留 CSV、生成脚本、SVG、PDF 和元数据。打开数据说明可以看到模型、测试条件和源文件。下载 SVG 后可用免费的 Inkscape 手动调字和位置。</p><a class="text-link" href="learn.html#svg">学习 SVG 微调 →</a></div></section>'''


def learn() -> str:
    return page_head('学习', '不会也没关系，从一件小事开始。', '不用先理解 13 个技能。先选一个你想完成的任务。') + '''<section class="page-block"><div class="wrap row-list"><div class="row" id="install"><h3>先装上</h3><p>选软件、选系统、下载对应包，跟着四步上手页操作。</p><a class="text-link" href="start.html">开始 →</a></div><div class="row"><h3>我的数据怎么画</h3><p>上传表格后，让技能先核对列名、单位、电芯和测试条件，再做预览。</p><a class="text-link" href="start.html?client=codex&os=windows&step=test">用演示数据试 →</a></div><div class="row"><h3>CE 与 Aurbach 的区别</h3><p>逐圈 CE 是按 cycle 的效率；Aurbach 是另一套镀锂/剥锂协议，不能混画。</p><a class="text-link" href="developers.html#grammar">看规则 →</a></div><div class="row" id="svg"><h3>SVG 怎么手动微调</h3><p>用免费 Inkscape 打开 SVG，检查字号、线条、裁切、特殊符号，再导出 PDF。</p><a class="text-link" href="https://inkscape.org/">到 Inkscape 官网 ↗</a></div><div class="row" id="review"><h3>综述从哪开始</h3><p>先定核心问题和边界，再建文献证据表；写作、投稿和返修接在后面。</p><a class="text-link" href="guide.html#review">看简明指南 →</a></div></div></section><section class="page-block soft" id="compatibility"><div class="wrap prose"><h2>不同软件，目前验证到哪一步？</h2><p>Codex 已在本机安装与试用。Kimi Code、DeepSeek Harness 的技能目录和导入方法已核对，完整绘图任务仍待更多实机测试。WorkBuddy 有专用的单技能 ZIP，客户端导入待验收。豆包暂不提供未经核实的一键安装入口。</p><p><a class="text-link" href="COMPATIBILITY.md">看完整适配说明 →</a></p></div></section>'''


def community() -> str:
    return page_head('社区', '大家一起维护，大家一起省时间。', '这套工具仍在生长。科学规则、样图、教程和安装体验都欢迎认真核对。') + f'''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>当前版本</h3><p>v{VERSION} · 安装包、可复现样图与新手引导。</p><a class="text-link" href="{GITHUB}/blob/main/CHANGELOG.md">版本记录 ↗</a></div><div class="row"><h3>下一步</h3><p>真实数据类型适配、更多期刊规范、可复用样例与跨 Agent 实机测试。</p><a class="text-link" href="roadmap.html">看路线图 →</a></div><div class="row"><h3>发现问题</h3><p>无论是“这张图不像电池论文”，还是“这里看不懂”，都值得告诉我们。</p><a class="text-link" href="contribute.html">参与反馈 →</a></div></div></section><section class="page-block"><div class="wrap"><h2>贡献者</h2><p class="section-intro">名单来自 CONTRIBUTORS.yaml。科学审核、文档与代码贡献分开展示；支持项目不自动获得贡献者或论文作者身份。</p><div id="contributor-list"></div></div></section>'''


def contribute() -> str:
    roles = [
        ("我做电池科研", "核对 Figure Grammar、实验条件和论文证据。", "先核对 Li‖Cu 逐圈 CE 与 Aurbach CE 的区别，并给出 DOI、图号和修改建议。", "battery-science.yml"),
        ("我会科研绘图", "改进 SVG、组合图排版、视觉复核与可读性。", "先选一张公开样图，检查最终尺寸的图例、字体和 panel 对齐。", "figure-design.yml"),
        ("我会 Python", "改进解析器、绘图、测试与导出。", "先给一个演示 CSV 增加缺列、缺单位的清楚报错和测试。", "python-code.yml"),
        ("我是学生 / 新用户", "照教程跑一遍，指出看不懂或跑不通的地方。", "先用演示数据走完安装和第一张图，记下最多三处卡住的地方。", "beginner-test.yml"),
        ("我会写文档或翻译", "把说明写得更清楚，补中文、英文和术语。", "先选一条安装路径，把看不懂的步骤改写成可照做的中英说明。", "documentation.yml"),
        ("我愿意帮忙传播", "介绍项目、找使用者、收集真实需求。", "先邀请三位自愿试用者，只用公开演示数据，匿名整理最常见的障碍。", "outreach.yml"),
    ]
    rows = "".join(f'<div class="row"><h3>{name}</h3><div class="task-copy"><p>{desc}</p><p class="first-task"><strong>第一件小事：</strong>{task}</p></div><a class="text-link" href="{GITHUB}/issues/new?template={template}">去 GitHub 提交（需登录） ↗</a></div>' for name, desc, task, template in roles)
    return page_head('参与贡献', '不会写代码，也有你的位置。', '选自己熟悉的一类任务。每一种反馈，都能减少下一个人摸索的时间。') + f'<section class="page-block"><div class="wrap"><p class="small">可以先照着下面的小任务试一试。提交反馈时才需要 GitHub 账号。</p><div class="row-list">{rows}</div></div></section><section class="page-block soft"><div class="wrap prose"><h2>我们怎样记录贡献？</h2><p>实际合并的代码、规则、科学审核、文档或翻译贡献会进入 CONTRIBUTORS.yaml。科研论文署名由对应研究和作者共同决定；资金支持不会自动换取署名或贡献者身份。</p><p><a class="text-link" href="{GITHUB}/blob/main/CONTRIBUTING.md">看完整贡献说明 ↗</a></p></div></section>'


def support() -> str:
    return page_head('支持项目', '让它保持免费，也有人继续维护。', '如果 BatteryReviewForge 帮你省了时间，可以用适合你的方式支持这个项目。') + f'''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>给项目一个 Star</h3><p>让更多做电池的人找到它。</p><a class="text-link" href="{GITHUB}">去 GitHub ↗</a></div><div class="row"><h3>贡献一点时间</h3><p>试一份数据、指出一处错误、润色一句说明，都很有用。</p><a class="text-link" href="contribute.html">看参与方式 →</a></div><div class="row"><h3>赞助维护</h3><p>资金渠道和用途说明正在准备；在正式公布前，我们不收款。</p><a class="text-link" href="roadmap.html">看进度 →</a></div></div></section><section class="page-block soft"><div class="wrap prose"><h2>公开透明</h2><p>计划用途包括服务器与域名、跨平台测试、样图制作、无障碍和文档维护。若以后开放个人或课题组赞助，会明确收款主体与记录方式。支持不会改变功能优先级、科研署名或贡献者身份。</p><p>这是独立开源项目。任何后续个人赞助都将标注为“支持维护”，不会称为学校官方捐赠或慈善捐款。</p></div></section>'''


def roadmap() -> str:
    return page_head('路线图', '现在做什么，哪些仍需验证。', '把进度和限制放在这里，方便使用者和贡献者按需查阅。') + '''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>已交付</h3><p>13 个独立技能、图型语法、安装包、七类数据先行的 synthetic demo、可下载 SVG/PDF/CSV。</p><span class="pill">当前</span></div><div class="row"><h3>正在验证</h3><p>更多仪器导出文件、复杂拼版、不同 Agent 的完整任务链、期刊最终尺寸与字体。</p><span class="pill">进行中</span></div><div class="row"><h3>后续方向</h3><p>有来源的真实公开示例、社区提交模板、更多 battery figure grammar 条目。</p><span class="pill">计划</span></div></div></section><section class="page-block soft"><div class="wrap prose"><h2>已知限制</h2><ul><li>示例图均为清晰标记的 synthetic demo，不能作为论文实验数据。</li><li>不同 Agent 的文件执行能力不同，能读技能不等于已经实测成图。</li><li>未知列名、测试条件或容量保持率参考圈数时，技能需要用户补充或仅画已知量。</li><li>SVG 编辑、PDF 字体嵌入和最终投稿尺寸仍需作者复核。</li></ul><p>早期样图仅保留在历史与测试材料中，不再作为首页作品。</p><p><a class="text-link" href="RELEASE_AUDIT_0.8.0.md">查看这一版的验收记录 →</a></p></div></section>'''


def developers() -> str:
    return page_head('开发者', '源码、数据和规则都在这里。', '普通使用请先走“开始使用”。这里提供可复现脚本和贡献入口。') + f'''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>仓库源码</h3><p>技能、Python 绘图、安装器与网站。</p><a class="text-link" href="{GITHUB}">打开 GitHub ↗</a></div><div class="row" id="grammar"><h3>图型规则</h3><p>电池图的实验协议、变量、常见 panel 搭配与证据。</p><a class="text-link" href="{GITHUB}/blob/main/skills/battery-review-figure/references/BATTERY_FIGURE_GRAMMAR.md">阅读 Grammar ↗</a></div><div class="row"><h3>Showcase 生成</h3><p>从 CSV 到 SVG/PDF，包含固定随机种子、测试条件和来源说明。</p><a class="text-link" href="{GITHUB}/tree/main/examples/showcase">查看脚本 ↗</a></div><div class="row"><h3>反馈与提交</h3><p>用角色模板提 issue；修改后附输入、输出和复现步骤。</p><a class="text-link" href="contribute.html">参与贡献 →</a></div></div></section>'''


def guide() -> str:
    return page_head('简明指南', '先完成一件事，再学下一件。', '把文件给你的 Agent，用一句话说清目的；工具会先盘点能读到什么，再动手。') + '''<section class="page-block"><div class="wrap row-list"><div class="row" id="data"><h3>我有一份实验数据</h3><p>请先核对列名、单位、电芯类型和测试条件，告诉我适合画什么；先预览一张，不改原文件。</p><a class="text-link" href="start.html?client=codex&os=windows&step=test">用样例练习 →</a></div><div class="row" id="assemble"><h3>我有几张现成图片</h3><p>请先逐张检查清晰度和内容，再统一字母、字号、边界与间距拼成 Figure。</p><a class="text-link" href="start.html?client=codex&os=windows&step=test#assembly">下载拼图素材 →</a></div><div class="row" id="review"><h3>我正在写综述</h3><p>先核对相近综述与证据范围，定问题和大纲，再逐节写作和查证。</p><a class="text-link" href="features.html#review">看工作流 →</a></div></div></section><section class="page-block soft" id="install-help"><div class="wrap prose"><h2>安装卡住怎么办？</h2><p>回到上手页确认软件与系统；如果安装器提示同名技能，先检查已有版本。若某个 Agent 不能执行 Python，可先让它帮你检查文件并生成脚本，再在具备 Python 的本机运行。</p><p><a class="text-link" href="start.html">回到安装步骤 →</a></p></div></section>'''


def disclaimer() -> str:
    return page_head('数据与责任说明', '放心用，也知道边界在哪。', '这里集中回答数据归属、上传、水印、演示图和论文使用中最常见的顾虑。') + '''<section class="page-block"><div class="wrap prose"><h2>数据还是你的吗？</h2><p>是。使用这个开源项目不会把你的原始数据、原图或未发表稿件转给项目。本站没有文件上传和 API Key 输入框，也没有项目自建的数据接收接口。你交给在线 Agent 的材料由该软件按其条款和账户设置处理；保密数据请先核对课题组与平台要求。</p><h2>图上会有水印吗？</h2><p>随包绘图和拼图脚本不会在图面强加项目 Logo、水印或推广文字。科学上必要的测试条件、单位和限制标注仍需保留。SVG/PDF 可能含普通元信息；溯源 JSON 可能含本地文件路径，公开前请检查。</p><h2>样图库里的数据是真的吗？</h2><p>不是。网站曲线和数值全部是明确标记的 synthetic demonstration，由公开代码和 CSV 生成，供练习和验证流程使用。它们不是实验结果，也不能直接用于论文论证。</p><h2>可直接投稿吗？</h2><p>工具能绘图、排版并提醒检查，但不能替你验证实验或决定文献是否支持结论。投稿前请与原始数据逐项核对数值、单位、测试协议、图注、字体和引用。不同电芯或条件不能因为画在同一张图就直接比较。</p><h2>他人的图片能拿来重绘吗？</h2><p>重新配色、拼版或重绘不会自动获得转载许可。公开资源库只收录本项目原创代码与示意元素；使用第三方图片仍需核对原始许可和目标期刊要求。</p><h2>需要额外的 API Key 吗？</h2><p>本网站不需要，也不会索取。请只在你使用的 Agent 官方设置中登录或配置模型。本站的搜索在浏览器中读取本地索引，不上传搜索词。</p><h2>开源许可覆盖什么？</h2><p>本项目代码按 MIT License 发布。你自己的实验数据、论文图片和第三方材料不会因此自动变成 MIT 授权。</p></div></section>'''


PAGES = {"index.html": ("首页", "免费开源的电池科研绘图、拼图与综述工作流。", homepage()),
         "start.html": ("开始使用", "四步安装并完成第一张电池示例图。", start()),
         "features.html": ("功能", "电池数据画图、论文拼图与综述工作流。", features()),
         "gallery.html": ("样图库", "可下载数据与可编辑图件的电池科研样图库。", gallery()),
         "learn.html": ("学习", "从安装到 SVG 微调的新手教程。", learn()),
         "community.html": ("社区", "贡献者、版本与维护动态。", community()),
         "contribute.html": ("参与贡献", "科研、设计、代码、测试与翻译都能参与。", contribute()),
         "support.html": ("支持项目", "帮助 BatteryReviewForge 长期保持免费开源。", support()),
         "roadmap.html": ("路线图", "项目进度和已知限制。", roadmap()),
         "developers.html": ("开发者", "源码、图型规则和复现脚本。", developers()),
         "guide.html": ("简明指南", "先完成一个电池科研任务。", guide()),
         "disclaimer.html": ("数据与责任说明", "数据归属、水印与演示图的说明。", disclaimer())}

SEARCH = [
    ("开始做", "安装 BatteryReviewForge", "start.html", "安装 download codex kimi workbuddy windows mac linux"),
    ("开始做", "用 Li‖Cu 数据画 CE", "start.html?client=codex&os=windows&step=test", "库伦效率 库仑效率 CE li||cu"),
    ("开始做", "六张图拼成 Figure", "start.html?client=codex&os=windows&step=test#assembly", "拼图 拼版 panel assembly"),
    ("样图", "Li‖Cu 逐圈 CE 样图", "gallery.html#li_cu_ce", "库伦效率 库仑效率 CE Aurbach"),
    ("样图", "全电池长循环样图", "gallery.html#full_cell", "全电池 full cell cycling"),
    ("样图", "EIS Nyquist 样图", "gallery.html#eis", "阻抗 EIS Nyquist"),
    ("样图", "Li‖Li 对称电池样图", "gallery.html#li_li", "对称电池 li||li symmetric cell"),
    ("样图", "Operando XRD 样图", "gallery.html#operando_xrd", "xrd diffraction"),
    ("样图", "ToF-SIMS 样图", "gallery.html#tof_sims", "tof sims depth map"),
    ("学习", "CE 与 Aurbach CE 的区别", "learn.html", "库伦效率 库仑效率 CE aurbach"),
    ("学习", "Inkscape 微调 SVG", "learn.html#svg", "svg inkscape 字号 排版"),
    ("学习", "兼容哪些 Agent", "learn.html#compatibility", "codex kimi workbuddy deepseek 豆包"),
    ("功能", "电池数据出图", "features.html", "CE EIS 全电池 画图"),
    ("功能", "图片拼版", "features.html", "拼图 拼版 figure"),
    ("功能", "综述写作", "features.html#review", "综述 review 写作 投稿 审稿"),
    ("社区", "路线图与已知限制", "roadmap.html", "roadmap 版本 已知问题"),
    ("社区", "参与贡献", "contribute.html", "contribute issue"),
    ("开发者", "battery-review-figure 规则", "developers.html#grammar", "库伦效率 CE Aurbach figure grammar"),
]


def main() -> None:
    contributors = json.loads((ROOT / "CONTRIBUTORS.yaml").read_text(encoding="utf-8"))
    (DOCS / "contributors.json").write_text(json.dumps(contributors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DOCS / "search-index.json").write_text(json.dumps([{"group": g, "title": t, "url": u, "keywords": k, "description": t} for g,t,u,k in SEARCH], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, (title, description, body) in PAGES.items():
        js = '<script src="start.js" defer></script>' if name == "start.html" else ""
        (DOCS / name).write_text(shell(title, description, body, js) + "\n", encoding="utf-8")
    print(f"Built {len(PAGES)} pages, search index and contributors for v{VERSION}")


if __name__ == "__main__":
    main()
