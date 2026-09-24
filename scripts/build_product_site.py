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
    ("开始使用", "start.html"), ("能做什么", "features.html"),
    ("样图库", "gallery.html"), ("使用帮助", "learn.html"),
]
SHOWCASE = [
    ("style_presets", "一份数据，六种画法", "同一份全电池数据、同一坐标范围；只换配色和线条。选择你看得舒服的一套。"),
    ("integrated_study", "同一研究的六面板图", "电解液 A/B 在 CE、对称电池、阻抗与全电池中保持一致。"),
    ("pouch_thermal", "软包电池表面温度", "软包轮廓、极耳、统一色标、同一温度场的截线和时间变化。"),
    ("literature_benchmark", "文献数据对照散点", "48 条虚构记录在相同测试基准下展示；示例编号不是论文引文。"),
    ("full_cell", "NMC811‖Li 全电池长循环", "循环容量与选定圈数电压曲线，来自同一套演示状态。"),
    ("eis", "EIS Nyquist 与相位", "由声明的等效电路生成频率与复阻抗数据。"),
    ("li_cu_ce", "Li‖Cu 逐圈库伦效率", "逐圈 CE 与对应容量过程；保留后期波动。"),
    ("li_li", "Li‖Li 对称电池", "长时间极化变化与同一时间段的局部波形。"),
    ("rate_capability", "倍率性能与对应电压曲线", "阶梯倍率、返回低倍率以及同一阶段的电压曲线。"),
    ("gcd_profiles", "选定圈数充放电曲线", "第 1、100、300、500 圈与全电池长循环使用同一容量状态。"),
    ("reporting_matrix", "文献报告完整度矩阵", "用不同状态区分已报告、部分报告、未报告和未核实。"),
    ("operando_xrd", "Operando XRD", "峰位、峰强随 SOC 变化，并与电压使用同一 SOC 轴。"),
    ("tof_sims", "ToF-SIMS 空间与深度分布", "同一界面模型生成离子图与深度趋势。"),
    ("capability_spread", "十类图，一页看清", "十类独立演示图排在同一页；这是能力索引，不是一项实验。"),
]
IMAGE_SIZE = {
    "full_cell": (2125, 1039), "li_cu_ce": (2125, 1039),
    "li_li": (2125, 1039), "eis": (2125, 1393),
    "operando_xrd": (2125, 1157), "tof_sims": (2125, 1074),
    "integrated_study": (2125, 1854), "capability_spread": (3543, 1677),
    "pouch_thermal": (2125, 1192), "literature_benchmark": (2125, 1240),
    "rate_capability": (2125, 1086), "gcd_profiles": (2125, 1181),
    "reporting_matrix": (2125, 1440),
    "style_presets": (3188, 1570),
}


def header() -> str:
    links = "".join(f'<a href="{url}">{label}</a>' for label, url in NAV)
    return f'''<a class="skip" href="#main">跳到正文</a><header class="topbar"><div class="wrap nav">
<a class="brand" href="index.html" aria-label="BatteryReviewForge 首页">BatteryReviewForge</a><button class="menu-toggle" type="button" aria-label="打开菜单" aria-expanded="false">菜单</button>
<nav class="navlinks" aria-label="主导航">{links}</nav><button class="search-trigger" type="button" data-open-search aria-label="搜索网站">搜索 <span aria-hidden="true">⌕</span></button>
</div></header>'''


def footer() -> str:
    return f'''<footer class="footer"><div class="wrap"><div class="footer-grid"><div><h3>BatteryReviewForge</h3><p>把画图和排版的重复劳动交给工具，把时间留给科研判断。</p><a href="start.html" class="text-link">开始使用 →</a></div>
<div><strong>探索</strong><a href="why.html">为什么用它</a><a href="features.html">功能</a><a href="gallery.html">样图库</a><a href="learn.html">学习</a><a href="models.html">模型怎么选</a></div>
<div><strong>项目</strong><a href="community.html">社区</a><a href="roadmap.html">路线图与已知问题</a><a href="contribute.html">参与贡献</a><a href="support.html">支持维护</a></div>
<div><strong>技术资料</strong><a href="developers.html">开发者入口</a><a href="{GITHUB}">GitHub 源码 ↗</a><a href="disclaimer.html">数据与责任说明</a><a href="{GITHUB}/blob/main/CITATION.cff">引用本项目 ↗</a></div></div>
<small>v{VERSION} · MIT License · 郭硕、姜金龙合作 · 上海理工大学能源材料科学研究院。独立开源项目；机构名称仅说明作者工作单位。</small></div></footer>'''


def shell(title: str, description: str, body: str, extra_js: str = "") -> str:
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(description, quote=True)}"><title>{escape(title)} · BatteryReviewForge</title><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="product.css?v={VERSION}"></head><body data-version="{VERSION}">
{header()}<main id="main">{body}</main>{footer()}
<div class="search-panel" role="dialog" aria-label="站内搜索" aria-modal="true"><div class="search-box"><button class="search-close" type="button" aria-label="关闭搜索">×</button><label for="site-search-input">想做什么 直接说</label><input id="site-search-input" type="search" placeholder="例如 我的 Excel 怎么画 六张图怎么拼" autocomplete="off"><div id="search-status" role="status" aria-live="polite"></div><div id="search-results" aria-live="polite"></div></div></div>
<script src="product.js?v={VERSION}" defer></script>{extra_js}</body></html>'''


def page_head(kicker: str, title: str, intro: str) -> str:
    return f'<div class="page-head"><div class="wrap"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{intro}</p></div></div>'


def gallery_card(item, wide=False) -> str:
    slug, title, description = item
    stem = f"assets/showcase/{slug}/"
    data_file = "data_index.csv" if slug in {"integrated_study", "capability_spread"} else "data.csv"
    width, height = IMAGE_SIZE[slug]
    return f'''<article class="gallery-card{' wide' if wide else ''}"><a class="gallery-image" href="{stem}figure.svg" aria-label="查看{title}的 SVG"><img src="{stem}figure.png" alt="{title}：虚构演示数据生成的科研图" width="{width}" height="{height}" loading="lazy" decoding="async"></a>
<div class="gallery-caption"><div><span class="synthetic">Synthetic demo · 非实验数据</span><h3>{title}</h3><p>{description}</p></div><div class="gallery-links"><a href="{stem}{data_file}">CSV</a><a href="{stem}figure.svg">SVG</a><a href="{stem}figure.pdf">PDF</a><a href="{stem}metadata.json">数据说明</a></div></div></article>'''


def homepage() -> str:
    by_slug = {item[0]: item for item in SHOWCASE}
    picks = "".join(f'<div class="home-pick home-pick-{slug}" id="home-{slug}">{gallery_card(by_slug[slug])}</div>'
                    for slug in ("integrated_study", "pouch_thermal", "tof_sims", "full_cell", "eis"))
    return f'''<section class="hero-section"><div class="wrap hero"><div class="hero-copy"><p class="eyebrow">免费开源 · 为电池科研而做</p><h1>少花时间排图<br>多花时间想问题</h1><p class="hero-lead"><strong>有数据就能画 有图片就能拼</strong><span>不会 Python 也没关系 从 Excel CSV 和零散图片开始 做出可编辑的论文图和整齐的 Figure</span></p>
<div class="hero-actions"><a class="btn" href="start.html">开始使用</a><a class="quiet-link" href="gallery.html">先看样图 <span aria-hidden="true">→</span></a></div><p class="hero-meta">免费开源 · 不用单独注册 · 附带演示数据</p></div>
<figure class="hero-figure"><a class="hero-media-desktop" href="gallery.html#style_presets" aria-label="查看六套画图风格"><img src="assets/gallery/style-preview.png" alt="六种可选配色的画图预览：蓝绿、玫蓝、珊瑚冰蓝、暖冷、极简和高对比" width="2232" height="1296" fetchpriority="high"></a><a class="hero-media-mobile" href="gallery.html#style_presets" aria-label="查看六套画图风格"><img src="assets/gallery/style-preview.png" alt="六种可选配色的画图预览" width="2232" height="1296"></a><figcaption><span>先看喜欢哪一种，再用你的数据画</span><span>虚构演示 · 非实验数据 · <a href="gallery.html#style_presets">看同一份数据的六套风格</a></span></figcaption></figure></div></section>
<section class="section"><div class="wrap"><div class="section-head"><p class="eyebrow">你手里有什么？</p><h2>从现在这一步开始。</h2><p class="section-intro">不用先弄懂所有技能。选你最熟悉的材料，照着页面做第一件事。</p></div><div class="feature-grid">
<article class="feature-item"><span class="feature-number">01 · 数据出图</span><h3>把电池数据画成论文图</h3><p>核对列名、单位和测试条件，再画长循环、库伦效率、阻抗等论文图。</p><a class="text-link" href="start.html?task=full">试着画一张 <span aria-hidden="true">→</span></a></article>
<article class="feature-item"><span class="feature-number">02</span><h3>有几张现成图</h3><p>按最终投稿尺寸拼在一起，检查字母、绘图区边界、间距和清晰度。</p><a class="text-link" href="start.html?task=assembly">试着拼一张 <span aria-hidden="true">→</span></a></article>
<article class="feature-item"><span class="feature-number">03</span><h3>先看效果</h3><p>打开样图，看原始演示数据、SVG 和 PDF，再用附带文件跟着做。</p><a class="text-link" href="gallery.html">打开样图库 <span aria-hidden="true">→</span></a></article></div></div></section>
<section class="section soft"><div class="wrap"><div class="section-head"><p class="eyebrow">样图库</p><h2>先看图，再决定怎么画。</h2><p class="section-intro">从电化学曲线到空间分布图。每张图都能打开数据与可编辑文件。</p></div><div class="home-showcase">{picks}</div><p class="section-action"><a class="quiet-link" href="gallery.html">查看所有样图 <span aria-hidden="true">→</span></a></p></div></section>
<section class="section"><div class="wrap start-invitation"><div><p class="eyebrow">第一次用</p><h2>跟着做，先画出一张。</h2><p>先看看电脑上有没有能运行技能的 AI 软件。页面会根据你的答案，带你找到下一步。</p><a class="btn" href="start.html">带我开始</a></div><ol class="simple-steps"><li><strong>看看软件</strong><span>装过、没装过、不确定都能选</span></li><li><strong>安装技能</strong><span>只看适合当前软件的步骤</span></li><li><strong>试一张</strong><span>用附带的演示数据验证</span></li></ol></div></section>
<section class="section soft"><div class="wrap trust-copy"><p class="eyebrow">放心使用</p><h2>你的数据，始终由你决定怎么用。</h2><p>本站不接收实验文件，也不索取 API Key。绘图脚本不会加项目水印；原始数据保持不变。在线 AI 软件的文件处理方式，请以你所用软件的设置为准。</p><a class="quiet-link" href="disclaimer.html">了解数据与责任说明 <span aria-hidden="true">→</span></a></div></section>
<section class="section"><div class="wrap closing"><p class="eyebrow">大家一起维护</p><h2>把时间还给研究<br>方法属于每个人</h2><p>BatteryReviewForge 由郭硕、姜金龙合作维护。欢迎研究者、学生、设计者和开发者指出问题，帮下一位使用者少走弯路。</p><div class="hero-actions"><a class="btn secondary" href="contribute.html">参与改进</a><a class="quiet-link" href="community.html">看看社区 <span aria-hidden="true">→</span></a></div></div></section>'''


def start() -> str:
    return f'''<div class="start-head"><div class="wrap"><div class="eyebrow">开始使用</div><h1>几步装好，先画一张。</h1></div></div>
<div class="wrap wizard"><nav class="progress" aria-label="使用进度"><span data-stage="prepare">1 准备 AI 软件</span><span aria-hidden="true">›</span><span data-stage="install">2 安装 BatteryReviewForge</span><span aria-hidden="true">›</span><span data-stage="try">3 画第一张图</span></nav><p class="mobile-progress" id="mobile-progress" aria-live="polite">第 1 步 / 共 3 步 · 准备 AI 软件</p>
<p class="task-hint" id="task-hint" hidden></p>
<section data-wizard-step="entry"><h2>你电脑上已经有这些 AI 软件吗</h2><p>Codex、Kimi Code 或 WorkBuddy，选一个最符合你的情况。</p><div class="choices"><button type="button" class="choice" data-entry="yes">有<small>我已经在用其中一个</small></button><button type="button" class="choice" data-entry="no">没有<small>带我装一个</small></button><button type="button" class="choice" data-entry="unsure">不确定<small>帮我看看</small></button></div></section>
<section data-wizard-step="diagnosis" hidden><h2>先看看电脑里有没有这些软件</h2><p>打开电脑的应用列表，找 Codex、Kimi Code 或 WorkBuddy。能找到并打开其中一个，就可以继续。</p><div class="choices"><button type="button" class="choice" data-diagnosis="found">找到了<small>我能打开其中一个软件</small></button><button type="button" class="choice" data-diagnosis="missing">没找到<small>带我去官方页面安装</small></button></div><div class="wizard-actions"><button type="button" class="ghost" data-wizard-back>← 上一步</button></div></section>
<section data-wizard-step="setup" hidden><h2>先准备一个能打开文件夹的 AI 软件。</h2><p>如果你的软件可以选择电脑上的文件夹，并能读取其中的技能说明，就可以继续。第一次使用推荐从官方页面安装支持 Codex 的桌面应用。</p><ol class="install-steps"><li>打开 <a class="text-link" href="https://openai.com/codex/" target="_blank" rel="noopener noreferrer">OpenAI 官方 Codex 页面 ↗</a>，选择适合电脑系统的桌面应用。</li><li>按官方页面的提示安装，用自己的账号登录。</li><li>打开应用，确认可以新建任务并选择本机文件夹。</li><li>回到这一页，点下面的按钮继续。</li></ol><p class="small">已经在用 Kimi Code 或 WorkBuddy？也可以直接继续选择自己的软件。本站不要求你在网页里填写 API Key。</p><div class="wizard-actions"><button type="button" class="ghost" data-wizard-back>← 上一步</button><button type="button" class="btn" data-wizard-next="client">软件准备好了，继续 →</button></div></section>
<section data-wizard-step="client"><h2>你现在用哪个软件</h2><p>第一次用，选我们验证最多的 Codex 就好。已经有别的软件，也可以继续用自己的。</p><button type="button" class="resume-choice" id="resume-choice" hidden></button><div class="choices primary-client"><button type="button" class="choice" data-choice-client="codex">Codex<small>推荐 · Windows 本机安装与试运行已验证</small></button></div><details class="other-clients"><summary>我已经在用其他软件</summary><div class="choices"><button type="button" class="choice" data-choice-client="kimi">Kimi Code<small>安装路径已核对 · 完整任务待实测</small></button><button type="button" class="choice" data-choice-client="workbuddy">WorkBuddy<small>界面导入 · 完整任务待实测</small></button><button type="button" class="choice" data-choice-client="dsh">DeepSeek Harness<small>安装路径已核对 · 完整任务待实测</small></button></div></details><p class="small">不知道选哪种模型？<a class="text-link" href="models.html">看三档简单建议与费用说明 →</a></p><p class="small">想看具体验证状态？<a class="text-link" href="compatibility.html">查看兼容性说明</a></p></section>
<section data-wizard-step="os" hidden><h2>这台电脑用的是哪个系统</h2><div class="choices"><button type="button" class="choice" data-choice-os="windows">Windows</button><button type="button" class="choice" data-choice-os="macos">macOS</button><button type="button" class="choice" data-choice-os="linux">Linux</button></div><div class="wizard-actions"><button type="button" class="ghost" data-wizard-back>← 上一步</button></div></section>
<section data-wizard-step="install" hidden><h2>安装到 <span id="current-client"></span><span id="current-os-wrap"> · <span id="current-os"></span></span></h2><p id="install-instruction"></p><div id="install-unavailable" class="notice" hidden><p>当前尚未验证这一软件与系统的安装组合。请先查看<a href="learn.html#compatibility">兼容性说明</a>，不要照搬其他平台的命令。</p></div>
<div id="install-content"><ol id="install-steps" class="install-steps"></ol><div id="command-block"><div class="command" id="install-command"></div><button type="button" class="ghost" data-copy="#install-command">复制命令</button></div><p class="small">适配状态：<span id="install-status"></span>。安装包不包含你的论文或数据。</p>
<details><summary>想看手动方法或遇到问题？</summary><p>查看<a class="text-link" href="learn.html#install">安装说明与常见问题</a>。已安装同名技能时，安装器会停下，不会擅自覆盖。</p></details></div><div class="wizard-actions"><button type="button" class="ghost" data-wizard-back>← 上一步</button><button type="button" class="btn" data-wizard-next="test">安装完成，试一张图 →</button></div></section>
<section data-wizard-step="test" hidden><h2>用演示文件，画出第一张图。</h2><p>这些是明确标记的虚构演示数据。下载、交给你的 AI 软件，再复制任务句。</p><div class="demo-list">
<article class="demo" id="full-cell-demo" data-demo="full"><span class="pill">最简单</span><h3>全电池长循环</h3><p>循环容量和对应的电压曲线。</p><a href="assets/showcase/BRF-demo-full-cell.zip" download>下载全电池示例包 ↓</a><button type="button" class="ghost" data-copy="#demo-full">复制任务句</button></article>
<article class="demo" id="ce-demo" data-demo="ce"><span class="pill">进阶</span><h3>Li‖Cu CE</h3><p>逐圈库伦效率和对应电化学过程。</p><a href="assets/showcase/BRF-demo-li-cu-ce.zip" download>下载 Li‖Cu 示例包 ↓</a><button type="button" class="ghost" data-copy="#demo-ce">复制任务句</button></article>
<article class="demo" id="assembly" data-demo="assembly"><span class="pill">拼图</span><h3>六张图拼成组合图</h3><p>六张独立图，按实际绘图区对齐。</p><a href="assets/showcase/assembly-example.png">先看拼好后的图 ↗</a><a href="assets/showcase/assembly-demo.zip" download>下载 6 张图和排版文件 ↓</a><button type="button" class="ghost" data-copy="#demo-assemble">复制任务句</button></article></div>
<div hidden><span id="demo-full">请先解压我上传的全电池示例包，用 BatteryReviewForge 同时读取 cycling.csv 和 voltage_profiles.csv，核对列名和单位，把长循环和选定圈数电压曲线画成可编辑 SVG。数据是虚构演示，不要当作实验结果。</span><span id="demo-ce">请先解压我上传的 Li||Cu 示例包，用 BatteryReviewForge 同时读取 ce.csv 和 voltage_profiles.csv，识别逐圈 CE 协议并画 CE 与代表性曲线。保留异常点，输出可编辑 SVG；不要把它当 Aurbach CE。</span><span id="demo-assemble">请用 battery-figure-assemble 将这 6 张演示图按附带的 figure_manifest.json 拼成组合图。运行严格对齐检查，核对毫米尺上的真实绘图区边界，再给我 PDF 和预览图。不要给每张图加副标题。</span></div>
<p class="notice">这一步会在你自己的 AI 软件中运行。本站只提供下载和说明，不接收你上传的数据；AI 软件如何处理文件取决于你所使用的软件设置。<a href="disclaimer.html">了解更多</a></p><div class="wizard-actions"><button type="button" class="ghost" data-wizard-back>← 上一步</button><a class="btn secondary" href="learn.html">不会？看一步步教程 →</a></div></section></div>'''


def features() -> str:
    return page_head('功能', '画图、拼图，少花时间调格式。', '把已有数据或图片交给工具，先检查内容，再做出可以继续修改的图。') + '''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>用数据画图</h3><p>CE、全电池、半电池、对称电池、倍率、EIS、CV、XRD、ToF-SIMS 等；先检查列名、单位和实验协议。</p><a class="text-link" href="gallery.html">看样图 →</a></div><div class="row"><h3>把图片拼齐</h3><p>整理 PNG、TIFF、PDF、SVG；按最终尺寸检查字母、间距、内容边界和清晰度。</p><a class="text-link" href="start.html?task=assembly">拿素材试试 →</a></div><div class="row"><h3>换一套合适的风格</h3><p>同一份数据可以从六套配色中选择；坐标、数值和科学含义不变。</p><a class="text-link" href="gallery.html#style_presets">看六套风格 →</a></div></div></section><section class="page-block soft"><div class="wrap prose"><h2>有些信息，需要你来确认。</h2><p>如果没有测试条件、容量保持率的参考圈数，或无法判断 Aurbach 协议，工具会说明缺什么。你补充后再画，不会替你编一个数。</p><p><a class="btn" href="start.html">从一个例子开始 →</a></p></div></section>'''


def gallery() -> str:
    slots = []
    for item in SHOWCASE:
        css_class = "gallery-slot gallery-slot-wide" if item[0] in {"style_presets", "integrated_study", "capability_spread"} else "gallery-slot"
        slots.append(f'<div class="{css_class}" id="{item[0]}">{gallery_card(item)}</div>')
    cards = "".join(slots)
    themes = json.loads((ROOT / "skills" / "battery-review-figure" / "assets" / "figure_theme.json").read_text(encoding="utf-8"))["presets"]
    style_cards = "".join(f'<article class="style-card"><a href="assets/showcase/style_presets/style_{key}.svg"><img src="assets/showcase/style_presets/style_{key}.png" alt="{escape(item["label_zh"])}配色：同一份虚构全电池循环数据" loading="lazy" width="1322" height="767"></a><h3>{escape(item["label_zh"])}</h3><p>{escape(item["label_en"])}</p><a class="text-link" href="assets/showcase/style_presets/style_{key}.svg">打开 SVG →</a></article>' for key, item in themes.items())
    heading = page_head('样图库', '一份数据，六种画法。', '先挑一套你喜欢的颜色，再往下看各种电池图。样图都能下载数据和可编辑文件。').replace('class="page-head"', 'class="page-head gallery-page-head"')
    return heading + f'''<section class="page-block style-choices"><div class="wrap"><p class="eyebrow">六套配色 · 同一份全电池演示数据</p><p class="section-intro">数值、坐标、单位一样，只换颜色和线条。</p><div class="style-grid">{style_cards}</div><p class="small">所有预览共用同一份 <a class="text-link" href="assets/showcase/style_presets/data.csv">演示 CSV ↓</a>。这里的曲线是虚构演示，配色也不代表任何期刊认可。</p></div></section><section class="page-block soft"><div class="wrap"><div class="gallery-grid">{cards}</div></div></section><section class="page-block"><div class="wrap prose"><h2>想自己改一遍？</h2><p>每个示例都保留 CSV、SVG、PDF 和数据说明。下载 SVG 后，可以用免费的 Inkscape 调整字和位置。</p><a class="text-link" href="learn.html#svg">学习 SVG 微调 →</a><p>标准数据图主要由脚本保证一致；复杂拼图和示意图更依赖 AI 的看图与判断。<a class="text-link" href="models.html">看看模型怎么选 →</a></p></div></section>'''


def learn() -> str:
    return page_head('使用帮助', '从一张图开始，慢慢来。', '先安装，再用演示文件试一遍。哪里不懂，就看对应的一条说明。') + '''<section class="page-block"><div class="wrap row-list"><div class="row" id="install"><h3>先装上</h3><p>看看电脑里有没有合适的 AI 软件，跟着页面做。</p><a class="text-link" href="start.html">开始 →</a></div><div class="row"><h3>我的数据怎么画</h3><p>把表格交给 AI 软件，先核对列名、单位、电芯和测试条件，再做预览。</p><a class="text-link" href="start.html?task=full">用演示数据试 →</a></div><div class="row"><h3>模型怎么选</h3><p>普通数据图先用现有模型；复杂拼图再考虑更强的模型。</p><a class="text-link" href="models.html">看简单建议 →</a></div><div class="row"><h3>CE 与 Aurbach 的区别</h3><p>两种测试的过程不同，图的横轴也可能不同。</p><a class="text-link" href="#ce">用两分钟弄清楚 →</a></div><div class="row" id="svg"><h3>SVG 怎么手动微调</h3><p>用免费 Inkscape 打开 SVG，检查字号、线条、裁切和特殊符号，再导出 PDF。</p><a class="text-link" href="https://inkscape.org/">到 Inkscape 官网 ↗</a></div></div></section><section class="page-block soft" id="ce"><div class="wrap prose"><p class="eyebrow">一眼分清</p><h2>逐圈 CE 和 Aurbach CE 是两种测试</h2><p>普通 Li‖Cu 逐圈库伦效率会在每一圈镀锂、剥锂后得到一个效率数值。常见图是横轴“循环圈数”、纵轴“库伦效率”；画图前还要核对电流密度、每圈镀锂容量和剥锂截止条件。Aurbach 测试使用另一套规定好的镀锂与剥锂步骤，通常需要展示测试过程中的电压曲线，再按照实际协议计算一个效率。它不能被当成普通逐圈 CE 曲线。</p><p>不确定自己的数据属于哪一种？把仪器程序或实验记录一起交给 AI 软件，先请它识别测试步骤。没有协议就先只画原始电压或容量，不要让它猜 CE。</p><a class="text-link" href="developers.html#grammar">查看完整绘图规则 →</a></div></section><section class="page-block" id="compatibility"><div class="wrap prose"><h2>不同软件，目前验证到哪一步？</h2><p>Codex 的 Windows 本机安装与试用已验证；其他软件和系统的完整任务仍待更多实机测试。</p><p><a class="text-link" href="compatibility.html">看易读版兼容性说明 →</a></p></div></section>'''


def why() -> str:
    return '''<section class="why-hero"><div class="wrap"><p class="eyebrow">为什么 BatteryReviewForge</p><h1>已经会用 Origin<br>为什么还要试这个</h1><p class="why-lead">如果 Origin 已经很顺手，不用扔掉它。我们想帮你省下的，是那些你已经会做、却还要一遍遍重复做的排图工作。</p><div class="hero-actions"><a class="btn" href="start.html?task=full">用演示数据试一次</a><a class="quiet-link" href="#time">看看时间怎么省 →</a></div></div></section>
<section class="page-block soft"><div class="wrap"><p class="eyebrow">日常工作</p><h2>少做一遍重复劳动</h2><div class="why-grid"><article><h3>新数据来了</h3><p>先核对列名、单位和测试条件，再用同一套设置重画。</p></article><article><h3>几张图要拼版</h3><p>按最终尺寸排，检查绘图区边界、字母和间距。</p></article><article><h3>导师又改了一处</h3><p>保留输入、脚本和设置，下次可以从源头重新生成。</p></article></div></div></section>
<section class="page-block"><div class="wrap prose"><p class="eyebrow">配合你已有的工具</p><h2>Origin 和它可以一起用</h2><p>Origin 有成熟的绘图和分析工具，也支持分析模板、批处理和 Python。BatteryReviewForge 加上电池图的绘图规则、拼版和最终尺寸检查。这里比较的是平时常见的手工工作流程，不是 Origin 的功能上限。</p><div class="why-comparison"><div><strong>常见手工流程</strong><p>重新导入 → 检查列 → 套格式 → 拼版 → 再检查</p></div><div><strong>BRF 辅助流程</strong><p>交出文件 → 确认关键条件 → 生成图件 → 作者复核</p></div></div><p class="small">参考：<a href="https://docs.originlab.com/origin-help/analysis-templates/">Origin 分析模板</a>、<a href="https://docs.originlab.com/origin-help/batch-processing/">批处理</a>和<a href="https://docs.originlab.com/user-guide/handling-repetitive-tasks/">自动化说明</a>。</p></div></section>
<section class="page-block soft" id="time"><div class="wrap prose"><p class="eyebrow">时间花在哪里</p><h2>实验在跑<br>图也在跑</h2><p>任务开始以后，脚本可以继续处理数据、导出文件并检查排版。你把时间留给实验和判断，最后再亲自核对结果。能否完全无人值守，取决于你使用的 AI 软件、权限和任务内容。</p><div class="benchmark-pending"><strong>真实时间对比正在建立</strong><p>我们还没有足够的实测数据，因此这里不写“省了百分之多少”。将比较普通手工流程、熟练 Origin 模板流程和 BRF 流程，分别记录人的操作时间与电脑运行时间。</p><a class="text-link" href="benchmark.html">看怎么测 →</a></div></div></section>
<section class="page-block"><div class="wrap prose"><h2>什么时候继续用手边的软件</h2><p>只画一张简单图，而且已有顺手的 Origin 模板？直接用它可能更快。需要特殊分析，继续用对应专业软件。最后想手动微调几个像素，Inkscape 或 Illustrator 更合适。</p><p>如果数据会反复更新、图很多、需要统一排版或留下可复现记录，可以试试 BatteryReviewForge。</p><h2>你不需要学会更快地调图<br>你需要少调一点图</h2><p>把重复劳动交给电脑，把判断留给研究者。</p><a class="btn" href="start.html?task=full">拿演示数据试一次</a></div></section>'''


def compatibility() -> str:
    return page_head('软件适配', '选你正在用的软件', '先确认哪条路已经试过。没有验证的组合会明确写出来。') + '''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>Codex · Windows</h3><p>本机安装与演示任务已验证。初次使用建议走这条路线。</p><a class="text-link" href="start.html?step=client">跟着安装 →</a></div><div class="row"><h3>Codex · macOS / Linux</h3><p>提供安装脚本；完整任务待实机验证。</p><a class="text-link" href="start.html?step=client">选择系统 →</a></div><div class="row"><h3>Kimi Code / DeepSeek Harness</h3><p>技能目录与安装参数已核对，完整绘图任务待实测。</p><a class="text-link" href="start.html?step=client">查看步骤 →</a></div><div class="row"><h3>WorkBuddy</h3><p>提供逐个技能导入的专用包；客户端完整任务待实测。</p><a class="text-link" href="start.html?step=client">查看导入 →</a></div><div class="row"><h3>豆包 Agent</h3><p>目前没有核实到可重复的技能导入步骤，暂不提供一键安装说明。</p><span class="pill">继续核实</span></div></div></section><section class="page-block soft"><div class="wrap prose"><h2>装完以后怎么确认</h2><p>开一个新任务，交给 AI 软件本站附带的演示文件，再复制上手页的任务句。能完成一张 SVG 并说明输入文件，才算这次任务跑通。</p><p>想看目录、参数和来源？<a class="text-link" href="developers.html">到开发者入口 →</a></p></div></section>'''


def benchmark() -> str:
    return page_head('时间对比', '先认真测，再给答案', '我们正在建立可重复的测试。这里不会拿虚构分钟数当产品成绩。') + '''<section class="page-block"><div class="wrap prose"><h2>怎么比较</h2><p>固定四件事：全电池数据出图、Li‖Cu CE 出图、六面板拼版、十面板拼版。每件事分别用普通手工软件流程、熟练 Origin 模板或批处理流程、BatteryReviewForge 流程完成。</p><h2>记录什么</h2><p>记录研究者主动操作的时间、电脑独立运行的时间、从开始到结束的时间、手动操作次数、返工次数、检查失败次数，以及是否保留了原始数据、设置和可编辑输出。</p><h2>什么时候公布结果</h2><p>先让至少 5 位新手和 5 位有 Origin 经验的使用者完成同一套任务。会报告每组的中位数和四分位范围，也会公开任务、计时规则和失败记录。完成前不展示节省时间的数字。</p><p>把重复的数据处理步骤写下来、方便新数据到来时重跑，是已有的科研计算建议；它不是“电池科研人员画图时间占比”的证据。<a class="text-link" href="https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510">阅读原始论文 ↗</a></p><a class="btn" href="start.html?task=full">先用演示数据试</a></div></section>'''


def community() -> str:
    catalog = json.loads((ROOT / "community" / "catalog.json").read_text(encoding="utf-8"))
    kind = {"style": "配色", "layout": "布局"}
    status = {"community": "初步收录", "reviewed": "人工看过", "verified": "已复核", "core": "内置稳定版"}
    cards = "".join(f'<article class="commons-card"><img src="{escape(item["preview_url"], quote=True)}" alt="{escape(item["name"])} 的自动预览" width="620" height="275" loading="lazy"><div><span class="pill">{kind[item["category"]]} · {status[item["status"]]}</span><h3>{escape(item["name"])}</h3><p>{escape(item["description_zh"])}</p><p class="small">作者：{escape(item["author"])} · {escape(item["license"])} · v{escape(item["version"])}</p><a class="text-link" href="commons/{"styles" if item["category"] == "style" else "layouts"}/{escape(item["id"])}@{escape(item["version"])}.json">下载资源文件 ↓</a></div></article>' for item in catalog["assets"])
    return page_head('社区资源库', '大家做出来 大家一起用', '先从可检查的配色和布局开始。公开投稿要经过审核，使用时锁定版本，重画不会悄悄变样。') + f'''<section class="page-block"><div class="wrap"><p class="eyebrow">Battery Commons · 第一阶段</p><h2>先看看大家分享的办法</h2><p class="section-intro">当前只有少量起步资源。“初步收录”只表示资源文件和格式已检查，科学适用性仍需人工复核；预览中的色觉模拟也只是自动筛查。</p><div class="commons-grid">{cards}</div><p class="small">普通绘图仍使用安装包内稳定的六套风格。只有你主动提出，AI 软件才会查看社区资源，并把所选版本记录到图的来源说明里。</p><div class="hero-actions"><a class="btn secondary" href="{GITHUB}/issues/new?template=submit-style.yml">提交配色 ↗</a><a class="quiet-link" href="{GITHUB}/issues/new?template=submit-layout.yml">提交布局 ↗</a></div><p class="small">提交使用公开 GitHub Issue，需要登录；不要上传未发表数据或没有公开许可的论文图片。未来会继续改进提交入口。</p></div></section><section class="page-block soft"><div class="wrap prose"><h2>喜欢 和 可靠 分开看</h2><p>将来会分别记录收藏、有用反馈、自动检查和领域审核。受欢迎的颜色不一定适合最终字号或色觉差异。资源从初步收录到人工复核，再到经过检查，最后才可能进入内置稳定库；当前资源尚未完成这些检查。</p><p>每项资源都写作者、许可、版本和校验值。技能不会自动运行社区代码，也不会把用户投稿叫作“训练模型”。未来若考虑模型训练，需要投稿人单独选择同意，默认关闭。</p></div></section><section class="page-block"><div class="wrap"><h2>贡献者</h2><p class="section-intro">名单来自 CONTRIBUTORS.yaml。科学审核、文档与代码贡献分开展示；支持项目不自动获得贡献者或论文作者身份。</p><div id="contributor-list"></div></div></section>'''


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
    return page_head('路线图', '现在做什么，哪些仍需验证。', '把进度和限制放在这里，方便使用者和贡献者按需查阅。') + '''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>已交付</h3><p>13 个独立技能、图型语法、安装包、14 类数据先行的虚构演示图、可下载 SVG/PDF/CSV。</p><span class="pill">当前</span></div><div class="row"><h3>正在验证</h3><p>更多仪器导出文件、复杂拼版、不同 AI 软件的完整任务链、期刊最终尺寸与字体。</p><span class="pill">进行中</span></div><div class="row"><h3>后续方向</h3><p>Battery Commons 投稿审核、真实公开示例、更多电池绘图规则。</p><span class="pill">计划</span></div></div></section><section class="page-block soft"><div class="wrap prose"><h2>已知限制</h2><ul><li>示例图均为清晰标记的 synthetic demo，不能作为论文实验数据。</li><li>不同 AI 软件的文件执行能力不同，能读技能不等于已经实测成图。</li><li>未知列名、测试条件或容量保持率参考圈数时，技能需要用户补充或仅画已知量。</li><li>SVG 编辑、PDF 字体嵌入和最终投稿尺寸仍需作者复核。</li></ul><p>原有六配色预览保留在首页和 README；旧的拼版练习仍可作为复盘材料。</p><p><a class="text-link" href="BEGINNER_USABILITY_AUDIT_v0.8.6.md">查看这一版的验收记录 →</a></p></div></section>'''


def developers() -> str:
    return page_head('开发者', '源码、数据和规则都在这里。', '普通使用请先走“开始使用”。这里提供可复现脚本和贡献入口。') + f'''<section class="page-block"><div class="wrap row-list"><div class="row"><h3>仓库源码</h3><p>技能、Python 绘图、安装器与网站。</p><a class="text-link" href="{GITHUB}">打开 GitHub ↗</a></div><div class="row" id="grammar"><h3>图型规则</h3><p>电池图的实验协议、变量、常见 panel 搭配与证据。</p><a class="text-link" href="{GITHUB}/blob/main/skills/battery-review-figure/references/BATTERY_FIGURE_GRAMMAR.md">阅读 Grammar ↗</a></div><div class="row"><h3>复杂图的证据</h3><p>逐 Figure/Panel 记录 ToF-SIMS、原位 XRD 与电化学图的来源和绘图约束。</p><a class="text-link" href="{GITHUB}/blob/main/skills/battery-review-figure/references/ADVANCED_FIGURE_ATLAS.md">查看论文笔记 ↗</a></div><div class="row"><h3>网站设计约定</h3><p>标题、字号、留白、手机排版和新手文字如何决定。</p><a class="text-link" href="PRODUCT_DESIGN_GUIDE.md">查看设计原则 →</a></div><div class="row"><h3>Showcase 生成</h3><p>从 CSV 到 SVG/PDF，包含固定随机种子、测试条件和来源说明。</p><a class="text-link" href="{GITHUB}/tree/main/examples/showcase">查看脚本 ↗</a></div><div class="row"><h3>反馈与提交</h3><p>用角色模板提 issue；修改后附输入、输出和复现步骤。</p><a class="text-link" href="contribute.html">参与贡献 →</a></div></div></section>'''


def guide() -> str:
    return page_head('简明指南', '先完成一件事，再学下一件。', '把文件给你的 AI 软件，用一句话说清目的；工具会先盘点能读到什么，再动手。') + '''<section class="page-block"><div class="wrap row-list"><div class="row" id="data"><h3>我有一份实验数据</h3><p>请先核对列名、单位、电芯类型和测试条件，告诉我适合画什么；先预览一张，不改原文件。</p><a class="text-link" href="start.html?task=full">用样例练习 →</a></div><div class="row" id="assemble"><h3>我有几张现成图片</h3><p>请先逐张检查清晰度和内容，再统一字母、字号、边界与间距拼成 Figure。</p><a class="text-link" href="start.html?task=assembly">下载拼图素材 →</a></div></div></section><section class="page-block soft" id="install-help"><div class="wrap prose"><h2>安装卡住怎么办？</h2><p>回到上手页确认软件与系统；如果安装器提示同名技能，先检查已有版本。</p><p><a class="text-link" href="start.html">回到安装步骤 →</a></p></div></section>'''


def disclaimer() -> str:
    return page_head('数据与责任说明', '放心用，也知道边界在哪。', '这里集中回答数据归属、上传、水印、演示图和论文使用中最常见的顾虑。') + '''<section class="page-block"><div class="wrap prose"><h2>数据还是你的吗？</h2><p>是。使用这个开源项目不会把你的原始数据、原图或未发表稿件转给项目。本站没有文件上传和 API Key 输入框，也没有项目自建的数据接收接口。你交给在线 AI 软件 的材料由该软件按其条款和账户设置处理；保密数据请先核对课题组与平台要求。</p><h2>图上会有水印吗？</h2><p>随包绘图和拼图脚本不会在图面强加项目 Logo、水印或推广文字。科学上必要的测试条件、单位和限制标注仍需保留。SVG/PDF 可能含普通元信息；溯源 JSON 可能含本地文件路径，公开前请检查。</p><h2>样图库里的数据是真的吗？</h2><p>不是。网站曲线和数值全部是明确标记的 synthetic demonstration，由公开代码和 CSV 生成，供练习和验证流程使用。它们不是实验结果，也不能直接用于论文论证。</p><h2>可直接投稿吗？</h2><p>工具能绘图、排版并提醒检查，但不能替你验证实验或决定文献是否支持结论。投稿前请与原始数据逐项核对数值、单位、测试协议、图注、字体和引用。不同电芯或条件不能因为画在同一张图就直接比较。</p><h2>他人的图片能拿来重绘吗？</h2><p>重新配色、拼版或重绘不会自动获得转载许可。公开资源库只收录本项目原创代码与示意元素；使用第三方图片仍需核对原始许可和目标期刊要求。</p><h2>需要额外的 API Key 吗？</h2><p>本网站不需要，也不会索取。请只在你使用的 AI 软件 官方设置中登录或配置模型。本站的搜索在浏览器中读取本地索引，不上传搜索词。</p><h2>社区投稿会训练模型吗？</h2><p>不会默认用于模型训练。社区 Issue 是公开投稿，接受资源入库与未来模型训练是不同选择；训练选项必须单独勾选，默认关闭。不要提交未发表数据或无授权的论文图。</p><h2>开源许可覆盖什么？</h2><p>本项目代码按 MIT License 发布。你自己的实验数据、论文图片和第三方材料不会因此自动变成 MIT 授权。</p></div></section>'''


def models() -> str:
    return page_head('模型怎么选', '先用现有的 再按任务升级', '普通数据图不用先买最贵的模型。图越复杂，越需要它帮你判断内容和排版。') + '''<section class="page-block"><div class="wrap"><div class="model-tiers"><article><span class="feature-number">01 · 省钱够用</span><h2>先画标准数据图</h2><p>一份 Excel 或 CSV，画逐圈 CE、长循环、倍率或 EIS。先让工具核对列名和单位，再照固定图型画。</p></article><article><span class="feature-number">02 · 大多数人选这个</span><h2>处理多张图</h2><p>多文件、六面板拼图、对齐与一次修改，用你当前软件里较强的通用模型更稳妥。</p></article><article><span class="feature-number">03 · 重要图件最后用</span><h2>检查复杂判断</h2><p>十面板、复杂示意图、从杂乱素材决定取舍，建议用最强可用模型做最后一遍视觉和科学复核。</p></article></div><p class="model-rule">标准数据图主要由绘图脚本保证一致性；复杂拼图、示意设计和视觉判断会明显受到模型能力影响。数据本身不会因为换模型而改变。</p></div></section>
<section class="page-block soft"><div class="wrap model-cost"><p class="eyebrow">先分清费用</p><h2>一张图大概要花多少钱</h2><p>你在 AI 软件里已有会员，通常先消耗套餐额度；只有自己配置按量计费的 API Key，才适合按 token 估算。BatteryReviewForge 本身免费，也不索取 Key。</p><div class="model-switches" role="group" aria-label="计费方式"><button type="button" data-billing="subscription" aria-pressed="true">我用会员</button><button type="button" data-billing="api" aria-pressed="false">我自填 API Key</button></div><div id="subscription-answer" class="cost-answer"><strong>一般不会因点一次绘图按钮，就由本项目单独扣一笔 API 费用。</strong><p>具体是否另收费，取决于你使用的软件、账号套餐与模型设置。到该软件的官方账户页面查看剩余额度。</p></div><div id="api-answer" class="cost-answer" hidden><p>选一个任务看示意估算。这里只算未命中缓存的文字 token；图片、工具、长上下文、重试及税费可能另计。它不是一次任务的固定报价。</p><div class="model-switches workload-switches" role="group" aria-label="估算任务"><button type="button" data-workload="single" aria-pressed="true">一张标准图</button><button type="button" data-workload="ten_basic" aria-pressed="false">十面板 一轮</button><button type="button" data-workload="ten_revision" aria-pressed="false">十面板 多轮</button></div><p class="small" id="workload-note"></p><div id="cost-results" class="cost-results" aria-live="polite"></div><p class="small" id="price-date"></p><p class="small">不同货币保持原币种，不做汇率换算。十面板的 token 数是多次请求的累计估算；OpenAI 单价按每次请求不超过 272K 输入 token 计算，超过时会启用更高的长上下文价格。<strong>还没有跨模型实测成绩</strong>。<a class="text-link" href="benchmark.html">查看实测计划 →</a></p></div></div></section>
<section class="page-block"><div class="wrap prose"><h2>按你正在用的软件选</h2><p><strong>Codex：</strong>普通数据处理可先试 Luna；多文件和拼图可选 Sol；复杂版式和最终视觉复核可用 Astra。推理档位依软件实际提供的选项决定。</p><p><strong>Kimi Code：</strong>K2.8 和 K3 的可用性随套餐变化；K3 可用于更复杂的判断。<strong>DeepSeek Harness：</strong>先确认能调用的模型，再用同一份演示数据试运行。<strong>WorkBuddy：</strong>目前只验证了导入包结构，模型和成图能力仍需实机测试。</p><p>这些是按任务复杂度给出的起步建议，不是模型能力排行榜。具体价格、模型名称和套餐会变；<a class="text-link" href="learn.html#compatibility">查看软件兼容性</a>。</p></div></section>'''


PAGES = {"index.html": ("首页", "免费开源的电池科研绘图与拼图工具。", homepage()),
         "why.html": ("为什么用它", "减少电池科研绘图中的重复工作，与现有软件一起使用。", why()),
         "start.html": ("开始使用", "跟着指引安装并完成第一张电池示例图。", start()),
         "features.html": ("功能", "电池数据画图、论文拼图与六套配色。", features()),
         "gallery.html": ("样图库", "可下载数据与可编辑图件的电池科研样图库。", gallery()),
         "learn.html": ("学习", "从安装到 SVG 微调的新手教程。", learn()),
         "compatibility.html": ("软件适配", "按软件选择经过核对的安装路线。", compatibility()),
         "benchmark.html": ("时间对比计划", "用真实任务比较人的操作时间与电脑运行时间。", benchmark()),
         "models.html": ("模型怎么选", "普通绘图、复杂拼图和 API 估算的简单说明。", models()),
         "community.html": ("社区", "贡献者、版本与维护动态。", community()),
         "contribute.html": ("参与贡献", "科研、设计、代码、测试与翻译都能参与。", contribute()),
         "support.html": ("支持项目", "帮助 BatteryReviewForge 长期保持免费开源。", support()),
         "roadmap.html": ("路线图", "项目进度和已知限制。", roadmap()),
         "developers.html": ("开发者", "源码、图型规则和复现脚本。", developers()),
         "guide.html": ("简明指南", "先完成一个电池科研任务。", guide()),
         "disclaimer.html": ("数据与责任说明", "数据归属、水印与演示图的说明。", disclaimer())}

SEARCH = [
    ("开始做", "我有 Excel 想画论文图", "start.html?task=full", "excel xlsx csv 表格 数据 画图 怎么画 全电池"),
    ("了解", "已经会用 Origin 为什么还要试", "why.html", "为什么 有什么用 值得吗 origin originpro 省时间 重复劳动"),
    ("开始做", "安装 BatteryReviewForge", "start.html", "安装 download codex kimi workbuddy windows mac linux"),
    ("开始做", "用 Li‖Cu 数据画 CE", "start.html?task=ce", "库伦效率 库仑效率 CE li||cu"),
    ("开始做", "六张图拼成 Figure", "start.html?task=assembly", "拼图 拼版 panel assembly"),
    ("样图", "Li‖Cu 逐圈 CE 样图", "gallery.html#li_cu_ce", "库伦效率 库仑效率 CE Aurbach"),
    ("样图", "全电池长循环样图", "gallery.html#full_cell", "全电池 full cell cycling"),
    ("样图", "EIS Nyquist 样图", "gallery.html#eis", "阻抗 EIS Nyquist"),
    ("样图", "Li‖Li 对称电池样图", "gallery.html#li_li", "对称电池 li||li symmetric cell"),
    ("样图", "Operando XRD 样图", "gallery.html#operando_xrd", "xrd diffraction"),
    ("样图", "ToF-SIMS 样图", "gallery.html#tof_sims", "tof sims depth map"),
    ("样图", "同一数据六套配色", "gallery.html#style_presets", "配色 风格 style preset 同一数据"),
    ("样图", "十类图能力展示", "gallery.html#capability_spread", "capability ten panel 十面板 总图"),
    ("样图", "软包温度热图", "gallery.html#pouch_thermal", "pouch thermal 热图 温度 软包"),
    ("样图", "文献性能散点", "gallery.html#literature_benchmark", "benchmark literature scatter 文献 性能 散点"),
    ("样图", "倍率性能", "gallery.html#rate_capability", "rate capability 倍率"),
    ("样图", "充放电曲线", "gallery.html#gcd_profiles", "gcd voltage profile 充放电"),
    ("样图", "报告完整度矩阵", "gallery.html#reporting_matrix", "reporting matrix heatmap NR NV 文献矩阵"),
    ("学习", "CE 与 Aurbach CE 的区别", "learn.html#ce", "库伦效率 库仑效率 CE aurbach"),
    ("学习", "Inkscape 微调 SVG", "learn.html#svg", "svg inkscape 字号 排版"),
    ("学习", "兼容哪些 AI 软件", "learn.html#compatibility", "codex kimi workbuddy deepseek 豆包"),
    ("学习", "模型怎么选与费用", "models.html", "模型 model 省钱 推荐 费用 API 会员 Luna Sol Astra Kimi DeepSeek"),
    ("学习", "软件安装遇到问题", "learn.html#install", "不会 小白 看不懂 怎么装 安装 打不开 没反应"),
    ("学习", "时间对比怎么测", "benchmark.html", "时间 节省 benchmark 测试"),
    ("功能", "电池数据出图", "features.html", "CE EIS 全电池 画图"),
    ("功能", "图片拼版", "features.html", "拼图 拼版 figure"),
    ("社区", "路线图与已知限制", "roadmap.html", "roadmap 版本 已知问题"),
    ("社区", "大家分享的配色和布局", "community.html", "社区 配色 布局 模板 commons 投稿 共享"),
    ("社区", "参与贡献", "contribute.html", "contribute issue"),
    ("开发者", "battery-review-figure 规则", "developers.html#grammar", "库伦效率 CE Aurbach figure grammar"),
]


def main() -> None:
    contributors = json.loads((ROOT / "CONTRIBUTORS.yaml").read_text(encoding="utf-8"))
    (DOCS / "contributors.json").write_text(json.dumps(contributors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    descriptions = {
        "why.html": ("看看它能帮你省掉哪些重复步骤，也看看什么时候继续用 Origin 更快。", "了解原因"),
        "start.html?task=full": ("下载一份演示包，照着两步画出第一张可编辑图。", "开始画图"),
        "start.html?task=assembly": ("下载六张演示图，按真实绘图区边界拼整齐。", "开始拼图"),
        "models.html": ("分清会员额度和自填 API Key，再决定要不要换模型。", "看费用"),
        "learn.html#install": ("不会安装或打开后没反应，从这里一步步排查。", "看帮助"),
        "benchmark.html": ("真实计时还在建立；先看统一的测试方法。", "看计划"),
        "community.html": ("看看有作者、许可和固定版本的配色与布局，也可以提交自己的办法。", "看资源"),
    }
    (DOCS / "search-index.json").write_text(json.dumps([{"group": g, "title": t, "url": u, "keywords": k, "description": descriptions.get(u, (f"打开{t}的说明与下一步。", "打开"))[0], "cta": descriptions.get(u, ("", "打开"))[1]} for g,t,u,k in SEARCH], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, (title, description, body) in PAGES.items():
        js = f'<script src="start.js?v={VERSION}-guide2" defer></script>' if name == "start.html" else (f'<script src="models.js?v={VERSION}" defer></script>' if name == "models.html" else "")
        (DOCS / name).write_text(shell(title, description, body, js) + "\n", encoding="utf-8")
    print(f"Built {len(PAGES)} pages, search index and contributors for v{VERSION}")


if __name__ == "__main__":
    main()
