# -*- coding: utf-8 -*-
"""Original mechanism templates, native editable SVG, and a typed Commons page.

No publication pixels or drawing geometry are used. Scientific relations are
distilled from separately recorded primary publisher pages. Standard library
only; the existing Commons palette catalogue is an optional colour source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile
from mechanism_art import illustrate
from html import escape, unescape
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
DOCS = SOURCE / "docs"
VERSION = "1.1.1"
AUTHOR = "Shuo Guo / VoltPeer"
MIT = """MIT License
Copyright (c) 2026 Shuo Guo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Publisher metadata and the explicitly read abstract/discussion scope.
# Licences apply to those papers, independently of this original MIT artwork.
REFERENCES = {
    "interfaces": {
        "title": "The importance of electrode interfaces and interphases for rechargeable metal batteries",
        "authors": "Jelena Popovic", "journal": "Nature Communications", "year": 2021,
        "doi": "10.1038/s41467-021-26481-8",
        "url": "https://www.nature.com/articles/s41467-021-26481-8",
        "source_license": "CC-BY-4.0 (publisher Rights and permissions checked)",
        "read_scope": "Publisher full text: SEI, metal deposition, transport, open questions",
    },
    "concentrated": {
        "title": "Superconcentrated electrolytes for a high-voltage lithium-ion battery",
        "authors": "Jianhui Wang, Yuki Yamada, Keitaro Sodeyama et al.", "journal": "Nature Communications", "year": 2016,
        "doi": "10.1038/ncomms12032", "url": "https://www.nature.com/articles/ncomms12032",
        "source_license": "CC-BY-4.0 (publisher-deposited Crossref licence checked); no source figure reused",
        "read_scope": "Publisher discussion: coordination networks and concentration-dependent structure",
    },
    "concentration": {
        "title": "The role of concentration in electrolyte solutions for non-aqueous lithium-based batteries",
        "authors": "Guinevere A. Giffin", "journal": "Nature Communications", "year": 2022,
        "doi": "10.1038/s41467-022-32794-z", "url": "https://www.nature.com/articles/s41467-022-32794-z",
        "source_license": "CC-BY-4.0 (publisher-deposited Crossref licence checked); no source figure reused",
        "read_scope": "Publisher text: concentration regimes defined through ion-solvation shells",
    },
    "iss": {
        "title": "Harnessing interfacial solvation structure for next-generation secondary batteries",
        "authors": "Chao Ye, Shuibin Tu, Shao-Jian Zhang et al.", "journal": "Nature Energy", "year": 2026,
        "doi": "10.1038/s41560-025-01937-z", "url": "https://www.nature.com/articles/s41560-025-01937-z",
        "source_license": "Publisher rights; abstract used as scientific basis only",
        "read_scope": "Publisher abstract: interfacial coordination, ion migration, desolvation, combined characterization",
    },
    "edl": {
        "title": "Engineering a passivating electric double layer for high performance lithium metal batteries",
        "authors": "Weili Zhang, Yang Lu, Lei Wan et al.", "journal": "Nature Communications", "year": 2022,
        "doi": "10.1038/s41467-022-29761-z", "url": "https://www.nature.com/articles/s41467-022-29761-z",
        "source_license": "CC-BY-4.0 (publisher-deposited Crossref licence checked); no source figure reused",
        "read_scope": "Publisher abstract/introduction: proposed additive-dependent EDL rearrangement",
    },
    "inactive": {
        "title": "Quantifying inactive lithium in lithium metal batteries",
        "authors": "Chengcheng Fang, Jinxing Li, Minghao Zhang et al.", "journal": "Nature", "year": 2019,
        "doi": "10.1038/s41586-019-1481-z", "url": "https://www.nature.com/articles/s41586-019-1481-z",
        "source_license": "Publisher rights; source text and images excluded from MIT artwork",
        "read_scope": "Author abstract and verified journal DOI: inactive Li0 versus SEI-bound Li+",
    },
    "voids": {
        "title": "Critical stripping current leads to dendrite formation on plating in lithium anode solid electrolyte cells",
        "authors": "Jitti Kasemchainan, Stefanie Zekoll, Dominic Spencer Jolly et al.", "journal": "Nature Materials", "year": 2019,
        "doi": "10.1038/s41563-019-0438-9", "url": "https://www.nature.com/articles/s41563-019-0438-9",
        "source_license": "Subscription article; public abstract as scientific basis only",
        "read_scope": "Publisher abstract: stripping voids, contact loss and local current concentration in Li/Li6PS5Cl",
    },
    "cryo": {
        "title": "Cryo-STEM mapping of solid–liquid interfaces and dendrites in lithium-metal batteries",
        "authors": "Michael J. Zachman, Zhengyuan Tu, Snehashis Choudhury et al.", "journal": "Nature", "year": 2018,
        "doi": "10.1038/s41586-018-0397-3", "url": "https://www.nature.com/articles/s41586-018-0397-3",
        "source_license": "Publisher rights; no microscopy image reused",
        "read_scope": "Publisher abstract: vitrification and structural/chemical mapping of native interfaces",
    },
    "cathode": {
        "title": "In situ inorganic conductive network formation in high-voltage single-crystal Ni-rich cathodes",
        "authors": "Xinming Fan, Xing Ou, Wengao Zhao et al.", "journal": "Nature Communications", "year": 2021,
        "doi": "10.1038/s41467-021-25611-6", "url": "https://www.nature.com/articles/s41467-021-25611-6",
        "source_license": "Article licence not reused; confirm publisher terms before any reuse",
        "read_scope": "Publisher abstract/introduction: ion/electron pathways and cracking-associated electrolyte access",
    },
    "dynamic": {
        "title": "Imaging solid–electrolyte interphase dynamics using operando reflection interference microscopy",
        "authors": "Guangxia Feng, Hao Jia, Yaping Shi et al.", "journal": "Nature Nanotechnology", "year": 2023,
        "doi": "10.1038/s41565-023-01316-3", "url": "https://www.nature.com/articles/s41565-023-01316-3",
        "source_license": "Subscription article; public abstract as scientific basis only",
        "read_scope": "Publisher abstract: time-dependent inner/outer layer evolution in the measured system",
    },
}

# Each scene has a specific process contract. Coordinates are newly authored.
TEMPLATES = [
    ("solvation-shell", "溶剂化壳层", "Solvation shell", "solvation", "离子周围的配位分子", "Neutral ligands coordinate a cation; shell size is illustrative.", "概念模型", "Raman / NMR 配合模拟可支持配位变化；示意位置和配位数不是测量值。", ["concentration", "iss"]),
    ("ion-pairing", "离子对与聚集体", "Ion pairs and aggregates", "solvation", "区分 SSIP、CIP 与 AGG", "Different ion-association motifs; no population fraction is assumed.", "概念模型", "SSIP/CIP/AGG 的占比须由本体系的光谱与模拟验证；不能仅由盐浓度确定。", ["concentrated", "concentration"]),
    ("ligand-exchange", "配位环境重组", "Coordination rearrangement", "solvation", "配位分子的进入与离开", "Exchange is schematic; no rate or activation energy is assigned.", "概念模型", "静态配位结构不能给出交换速率；需动力学模拟或时间敏感表征。", ["iss"]),
    ("desolvation", "界面去溶剂化", "Interfacial desolvation", "solvation", "离子接近界面时改变配位", "Coordination can change before interfacial transfer; the order is a model.", "概念模型", "去溶剂化与界面传输可耦合；不得把完整去溶剂化画成所有体系的必经步骤。", ["iss"]),
    ("double-layer", "电双层中的离子分布", "Electric double layer", "transport", "带电界面附近的离子富集", "A negative interface enriches counterions; this is a simplified EDL.", "概念模型", "不画绝对层厚或浓度；特异吸附与高浓度下的结构需要体系证据。", ["interfaces", "edl"]),
    ("migration-diffusion", "迁移与扩散", "Migration and diffusion", "transport", "区分电场驱动与浓度梯度驱动", "Cations and anions migrate oppositely; diffusion follows the concentration gradient.", "已知过程", "箭头表示驱动力方向，长度不是通量；需要浓度、迁移数与边界条件才能定量。", ["interfaces"]),
    ("sei-formation", "SEI 的形成", "SEI formation", "interphase", "还原副反应形成界面膜", "Reduction products form a heterogeneous passivation interphase.", "已知过程", "组分与厚度取决于电解液和工况；图中的形状不代表特定化合物。", ["interfaces", "cryo"]),
    ("selective-passivation", "SEI 中的离子与电子", "Selective passivation", "interphase", "离子通过与电子阻隔", "Desired SEI behaviour: cation transfer with restricted electronic conduction.", "理想化目标", "离子可通、电子受阻是设计目标；真实膜电导与路径不能由图或单次 XPS 确定。", ["interfaces"]),
    ("heterogeneous-sei", "非均匀界面膜", "Heterogeneous interphase", "interphase", "不同界面区的局部传输", "Chemically heterogeneous domains may support different local ion paths.", "概念模型", "色块只区分区域；域内、晶界或孔隙传输路线须由空间表征和模型核验。", ["interfaces", "cryo"]),
    ("cei-formation", "正极界面副反应", "Cathode interphase formation", "interphase", "氧化副反应与 CEI", "Electrolyte oxidation can form cathode-side interphase products.", "概念模型", "不将所有 CEI 组分归因于单一路径；来源、膜结构与保护作用需本体系证据。", ["edl", "cathode"]),
    ("nucleation-growth", "金属成核与生长", "Metal nucleation and growth", "metal", "从初始晶核到连续沉积", "Ion supply, interfacial reaction and surface conditions affect metal growth.", "概念模型", "晶核形状与大小是示意；均匀性和成核障碍须由原位或电化学证据评价。", ["interfaces"]),
    ("plating-stripping", "沉积与剥离", "Plating and stripping", "metal", "同一界面的可逆半反应", "Li+ + e− ⇌ Li0; direction follows the imposed current.", "已知过程", "可逆箭头只表示半反应方向；不保证完全可逆或库仑效率为 100%。", ["interfaces", "inactive"]),
    ("inactive-lithium", "失去电子连接的锂", "Electronically isolated lithium", "metal", "区分金属锂与界面膜中的锂", "Isolated Li0 and SEI-bound Li+ are distinct inactive-inventory classes.", "测量支持的过程", "形貌或 CE 单独不能分辨两类损失；需化学定量并检查取样与滴定假设。", ["inactive"]),
    ("film-reformation", "界面膜破裂与再形成", "Interphase rupture and reformation", "interphase", "新表面暴露后继续反应", "Surface change can expose fresh metal and lead to further interphase formation.", "概念模型", "再形成不等于完全自修复；变化的时间顺序、损耗与可逆性需原位证据。", ["interfaces", "dynamic"]),
    ("solid-contact-loss", "固态界面接触损失", "Solid-state contact loss", "metal", "剥离空隙与局部电流集中", "Stripping faster than replenishment can create voids and concentrate local current.", "测量支持的过程", "该路径在 Li/Li6PS5Cl 的特定条件有证据；阈值依赖压力、材料和程序。", ["voids"]),
    ("dual-pathways", "正极中的离子与电子路径", "Ionic and electronic pathways", "transport", "区分电解质与导电网络", "Ion and electron access must both reach electrochemically active regions.", "概念模型", "示意网络不代表实测连通性或特定涂层；混合导体需独立量化离子与电子电导。", ["cathode"]),
]

BOUNDARIES_EN = [
    "Use spectroscopy and simulation to support coordination changes. Positions and coordination numbers are illustrative.",
    "Verify SSIP/CIP/AGG fractions in your electrolyte. Salt concentration alone does not determine the populations.",
    "A static structure does not establish exchange rates. Time-sensitive measurements or dynamic simulations are needed.",
    "Desolvation and transfer can be coupled. Complete desolvation is not a universal prerequisite.",
    "No absolute layer thickness or concentration is specified. Specific adsorption requires system evidence.",
    "Arrows indicate driving directions, not flux magnitude. Quantification requires concentrations and boundary conditions.",
    "Composition and thickness depend on electrolyte and conditions. Shapes do not identify specific compounds.",
    "Ion transfer and electron restriction are desired properties. Actual conductivity and pathways need independent evidence.",
    "Colours distinguish regions. Domain, boundary and pore pathways require spatial evidence and modelling.",
    "CEI components can have multiple origins. Film structure and protection require evidence from your system.",
    "Nucleus shapes and sizes are illustrative. Uniformity and nucleation barriers require electrochemical or operando evidence.",
    "The two directions describe half reactions. They do not guarantee full reversibility or 100% Coulombic efficiency.",
    "Morphology or CE alone cannot separate inventory losses. Use chemical quantification and verify sampling assumptions.",
    "Reformation does not establish complete repair. Timing, consumption and reversibility require operando evidence.",
    "This path has evidence in specified Li/Li6PS5Cl conditions. Thresholds depend on pressure, materials and protocol.",
    "The network is conceptual. Connectivity and separate ionic/electronic conductivity require independent measurements.",
]

ENGLISH = {
    "机理图":"Mechanism diagrams",
    "选一个过程，核对你的证据，再修改可编辑的矢量图。":"Choose a process, check your evidence, then edit the vector artwork.",
    "查看机理图 Skill →":"Explore the mechanism Skill →",
    "研究图布局与配色 →":"Figure layouts and colours →",
    "溶剂化":"Solvation","界面膜":"Interphases","传输路径":"Transport pathways","金属沉积":"Metal deposition",
    "16 套原创模板":"16 original templates","选择这套机理图 →":"Choose this mechanism →",
    "这些图能说明什么":"What these diagrams can explain",
    "模板从期刊论文中核对科学关系，重新设计全部几何、配色和排版。图件与生成代码按 MIT 开放；参考论文的许可独立记录。":"Scientific relations were checked against journal sources. All geometry, colours and layouts were newly authored. Artwork and code use MIT; paper licences are recorded independently.",
    "它们是示意图。你需要核对自己的材料、反应方向和证据；配位数、膜厚、箭头长度、域大小与通量没有测量含义。虚线路径表示需要验证的假说。":"These are schematics. Check your materials, reaction directions and evidence. Coordination numbers, film thickness, arrow length and domain size are illustrative. Dashed paths denote hypotheses.",
    "下载科学来源记录 ↓":"Download scientific sources ↓","图件 MIT 许可 ↓":"Artwork MIT licence ↓",
    "原创机理模板":"Original mechanism template","关闭机理图":"Close mechanism",
    "青蓝 / 铜棕 / 紫 / 绿":"Teal / copper / purple / green","图件背景":"Artwork background",
    "白底":"White","透明":"Transparent","查看完整配色库 →":"Browse all palettes →",
    "用前核对":"Check before use","下载 SVG 图件 ↓":"Download SVG artwork ↓",
    "下载生成源码 ↓":"Download source ZIP ↓","下载参数 JSON ↓":"Download parameters JSON ↓",
    "下载提示词 ↓":"Download AI request ↓","科学来源与许可":"Scientific sources and licences",
    "来源用于核对科学关系。原创图件 MIT 许可不改变论文许可。":"Sources support scientific relations. The MIT artwork licence does not change paper licences.",
    "安装与使用教程 →":"Installation and usage guide →","放大图件 ↗":"Enlarge artwork ↗",
    "概念模型":"Conceptual model","已知过程":"Established process","理想化目标":"Design target","测量支持的过程":"Process supported by measurement",
    "选一个你想完成的任务":"Choose a task to complete","下载 Skill，在你的 AI 助手中使用。":"Download a Skill and use it in your AI assistant.",
    "第一次使用：安装教程":"First time: installation guide",
    "把数据画成图":"Plot your data","读取表格，核对单位，画出可重做的科研图。":"Check a table and its units, then create reproducible scientific plots.",
    "SVG / PDF / PNG · 重画脚本":"SVG / PDF / PNG · redraw script",
    "把几张图拼整齐":"Arrange your figure panels","对齐现有面板，统一字母、字体和间距。":"Align existing panels and unify letters, fonts and spacing.",
    "组合图 · 可编辑布局":"Assembled figure · editable layout",
    "整理仪器数据":"Organize instrument data","检查列名和单位，把导出文件整理成绘图表。":"Check column names and units and prepare exported files for plotting.",
    "整理表格 · 字段映射 · 处理记录":"Prepared table · field mapping · processing log",
    "写论文草稿":"Draft paper sections","根据你的大纲、实际结果和文献写这一节。":"Draft a section from your outline, results and literature.",
    "正文草稿 · 待补资料":"Section draft · missing evidence",
    "规划论文主线":"Plan the paper argument","把研究问题、论证与章节安排连起来。":"Connect the research question, argument and section outline.",
    "论证主线 · 大纲 · 证据缺口":"Argument · outline · evidence gaps",
    "润色已有文字":"Polish existing text","把表达写清楚，保留原意、数字和引用。":"Clarify the wording while preserving meaning, numbers and citations.",
    "润色稿 · 修改说明":"Polished draft · change notes",
    "画机理示意图":"Draw mechanism diagrams","依据你的体系和证据，创作可编辑的机理图。":"Create editable mechanism diagrams from your system and evidence.",
    "原创 SVG · 源码 · 参数与来源":"Original SVG · source · parameters and references",
    "按教程安装，再把自己的文件和要求交给 AI 助手。":"Install with the guide, then give your files and requirements to your AI assistant.",
    "研究图布局、配色与原创机理模板。":"Figure layouts, colours and original mechanism templates.",
    "研究图布局与配色":"Figure layouts and colours","原创机理图库 →":"Original mechanisms →",
}
for row, boundary in zip(TEMPLATES, BOUNDARIES_EN):
    ENGLISH.update({row[1]:row[2],row[4]:row[5],row[7]:boundary})

PARAMETER_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "title": "VoltPeer mechanism parameters", "type": "object", "additionalProperties": False,
    "properties": {
        "template": {"enum": [r[0] for r in TEMPLATES]},
        "cation": {"enum": ["Li+", "Na+", "K+"], "default": "Li+", "description": "Five coordination/transport scenes support Li+/Na+/K+; the other eleven spatial metal/interphase illustrations are lithium-specific. Read each record's supported_cations."},
        "colors": {"type": "array", "minItems": 4, "maxItems": 4, "items": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"}},
        "palette_reference": {"type":"object","additionalProperties":False,"properties":{k:{"type":"string","maxLength":500} for k in ("id","version","name","author","license","url")},"required":["id","version","license"]},
        "background": {"enum": ["white", "transparent"], "default": "white"},
    }, "required": ["template"],
}

DEFAULT_COLORS = ["#126B81", "#935B32", "#605A93", "#597341"]


class SVG:
    def __init__(self, record, colors, background, cation):
        self.record, self.colors, self.cation = record, colors, cation
        self.items = []
        if background == "white":
            self.items.append('<rect id="background" width="1200" height="600" fill="#FFFFFF"/>')
        self.text(42, 48, record[2], 25, bold=True)
        self.text(42, 78, "Original conceptual schematic • not experimental data • MIT", 13, "#536579")
        self.items.append('<g id="mechanism-geometry">')

    def text(self, x, y, label, size=18, color="#213244", anchor="start", bold=False):
        # Absolute positioned superscripts work in browsers and CairoSVG; no
        # dependence on availability of superscript Unicode font glyphs.
        if any(symbol in label for symbol in ("⁺", "⁻", "⁰")):
            pieces = re.split(r"([⁺⁻⁰])", label)
            widths = {"i":.222,"l":.222,"L":.556,"I":.278,"e":.556," ":.278,"+":.584,"-":.333,"0":.556,"→":1.0}
            items=[]
            for piece in pieces:
                superscript=piece in {"⁺", "⁻", "⁰"}
                content={"⁺":"+","⁻":"-","⁰":"0"}.get(piece,piece)
                font=size*.7 if superscript else size
                length=sum(widths.get(ch,.556 if ch.islower() else .667) for ch in content)*font
                items.append((content,font,y-size*.38 if superscript else y,length))
            total=sum(item[3] for item in items)
            cursor=x-total/2 if anchor=="middle" else x-total if anchor=="end" else x
            self.items.append(f'<g aria-label="{escape(label,quote=True)}">')
            for content,font,baseline,length in items:
                self.items.append(f'<text x="{cursor:g}" y="{baseline:g}" font-size="{font:g}" fill="{color}" font-weight="{600 if bold else 400}">{escape(content)}</text>')
                cursor+=length
            self.items.append('</g>')
        else:
            self.items.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{600 if bold else 400}">{escape(label)}</text>')

    def rect(self, x, y, w, h, fill="#F1F5F8", stroke="#BAC6D0", radius=7, opacity=1):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="1.5"/>')

    def path(self, d, color="#536579", width=2, dashed=False, fill="none"):
        dash = ' stroke-dasharray="7 6"' if dashed else ''
        self.items.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{width}"{dash}/>')

    def circle(self, x, y, radius, fill, stroke="none", width=2):
        self.items.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def arrow(self, x1, y1, x2, y2, kind="ion", dashed=False):
        color = {"ion": self.colors[0], "electron": self.colors[1], "process": "#536579", "hypothesis": self.colors[2]}[kind]
        dash = ' stroke-dasharray="7 6"' if dashed else ''
        self.items.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="3" marker-end="url(#{kind}-arrow)"{dash}/>')

    def ion(self, x, y, sign="+", label=None):
        if sign == "+":
            self.circle(x, y, 21, self.colors[0])
            self.text(x, y+6, label or self.cation.replace("+", "⁺"), 18, "#FFFFFF", "middle", True)
        else:
            self.rect(x-23, y-18, 46, 36, self.colors[2], self.colors[2], 7)
            self.text(x, y+6, label or "A⁻", 18, "#FFFFFF", "middle", True)

    def ligand(self, x, y, angle=0, small=False):
        r = 11 if small else 15
        self.circle(x, y, r, "#FFFFFF", self.colors[3], 2)
        self.text(x, y+5, "L", 14, self.colors[3], "middle")
        self.path(f"M{x+r} {y} l{13*math.cos(angle):.1f} {13*math.sin(angle):.1f}", self.colors[3], 2)

    def shell(self, x, y, ligands=4, anion=False, radius=67):
        self.circle(x, y, radius+18, "none", "#DCE4E9", 1)
        self.ion(x, y)
        for i in range(ligands):
            a = 2*math.pi*i/max(ligands, 1) - math.pi/4
            xx, yy = x+radius*math.cos(a), y+radius*math.sin(a)
            self.path(f"M{x+24*math.cos(a):.1f} {y+24*math.sin(a):.1f} L{xx-17*math.cos(a):.1f} {yy-17*math.sin(a):.1f}", "#A2B1BC", 1.5, True)
            self.ligand(round(xx,1), round(yy,1), a)
        if anion:
            self.ion(x+radius, y, "-")

    def electrode(self, x=70, y=400, w=1060, h=75, label="Metal electrode"):
        self.rect(x, y, w, h, "#E7EDF2", "#748697", 3)
        self.text(x+w/2, y+h/2+7, label, 20, "#213244", "middle", True)

    def finish(self):
        self.items.append('</g><g id="legend">')
        self.ion(62, 551)
        self.text(94, 557, "cation", 15)
        self.ligand(241, 551, small=True)
        self.text(267, 557, "neutral ligand", 15)
        self.ion(432, 551, "-")
        self.text(465, 557, "anion", 15)
        self.arrow(593, 551, 643, 551, "ion")
        self.text(661, 557, "ion motion", 15)
        self.arrow(815, 551, 865, 551, "electron")
        self.text(886, 557, "electron path", 15)
        self.items.append('</g>')
        defs = []
        for kind, color in {"ion":self.colors[0], "electron":self.colors[1], "process":"#536579", "hypothesis":self.colors[2]}.items():
            defs.append(f'<marker id="{kind}-arrow" viewBox="0 0 10 10" refX="8.4" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1L9 5L0 9Z" fill="{color}"/></marker>')
        description = escape(self.record[5] + " " + self.record[7])
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600" role="img" aria-labelledby="figure-title figure-description"><title id="figure-title">{escape(self.record[2])}</title><desc id="figure-description">{description}</desc><metadata>{escape(json.dumps({"license":"MIT","template":self.record[0],"version":VERSION,"original_geometry":True,"source_figures_reused":False}, ensure_ascii=False))}</metadata><defs>{"".join(defs)}</defs><g font-family="Arial, Helvetica, sans-serif">{"".join(self.items)}</g></svg>\n'


def draw_rejected_draft(record, colors=DEFAULT_COLORS, background="white", cation="Li+"):
    """Produce deterministic SVG with visible charges and labelled directions."""
    key = record[0]
    s = SVG(record, colors, background, cation)
    if key == "solvation-shell":
        s.shell(345, 295, 4, radius=104)
        s.text(345, 456, "Illustrative first coordination shell", 19, anchor="middle")
        s.rect(645, 157, 430, 266)
        s.text(685, 206, "Coordination is system dependent", 21, bold=True)
        for i, txt in enumerate(["L = a neutral coordinating molecule", "A⁻ = a generic monovalent anion", "No measured coordination number", "No molecule-specific geometry"]):
            s.text(685, 252+i*41, txt, 18)
    elif key == "ion-pairing":
        for x, label in [(220,"SSIP"),(590,"CIP"),(975,"AGG")]:
            s.text(x, 148, label, 24, anchor="middle", bold=True)
        s.shell(190, 300, 4, radius=57); s.ion(345,300,"-")
        s.shell(555,300,3,radius=57); s.ion(615,300,"-")
        s.ion(905,300); s.ion(971,300,"-"); s.ion(1039,300); s.ion(975,368,"-")
        s.path("M926 300H948M994 300H1018M1039 322L992 356M952 356L905 322", "#A2B1BC",2,True)
        s.ligand(905,235); s.ligand(1040,236); s.ligand(1040,374)
        s.text(220,460,"Solvent-separated pair",18,anchor="middle"); s.text(590,460,"Direct ion contact",18,anchor="middle"); s.text(975,460,"Connected ionic motif",18,anchor="middle")
    elif key == "ligand-exchange":
        s.shell(245,290,4); s.shell(600,290,3); s.shell(955,290,4)
        s.arrow(340,290,490,290,"process"); s.arrow(700,290,846,290,"process")
        s.ligand(585,156); s.arrow(585,212,585,170,"process")
        s.ligand(990,156); s.arrow(990,177,990,216,"process")
        for x,lab in [(245,"Initial environment"),(600,"Ligand departure"),(955,"New coordination")]: s.text(x,454,lab,19,anchor="middle")
        s.text(600,490,"Sequence illustrates rearrangement; rates are not specified",16,anchor="middle")
    elif key == "desolvation":
        s.shell(240,230,4); s.shell(610,270,2); s.ion(965,334)
        s.arrow(338,235,510,265); s.arrow(714,275,923,329)
        s.ligand(600,145); s.arrow(600,193,600,166,"process")
        s.electrode(label="Electrode / insertion host")
        s.arrow(965,359,965,393)
        s.text(238,143,"Bulk coordination",18,anchor="middle"); s.text(620,183,"Interfacial reorganization",18,anchor="middle"); s.text(980,231,"Transfer",18,anchor="middle")
        s.text(600,500,"Partial coordination can remain; sequence is a conceptual model",16,anchor="middle")
    elif key == "double-layer":
        s.electrode(label="Negatively polarized surface")
        for x in range(100,1100,100): s.text(x,391,"−",22,anchor="middle")
        for x in (170,330,490,650,810,970): s.ion(x,340)
        for x in (230,550,870): s.ion(x,210,"-")
        for x in (140,390,700,1020): s.ligand(x,246)
        s.path("M70 285H1130", "#BAC6D0",1,True)
        s.text(600,145,"Counterion enrichment near a negative interface",21,anchor="middle")
        s.text(600,495,"Positions, distances and concentrations are illustrative",16,anchor="middle")
    elif key == "migration-diffusion":
        s.rect(60,127,515,350); s.rect(625,127,515,350)
        s.text(318,169,"Electric-field-driven migration",21,anchor="middle",bold=True)
        s.arrow(175,219,475,219,"process"); s.text(320,207,"E",19,anchor="middle")
        s.ion(190,288); s.arrow(237,288,475,288)
        s.ion(466,379,"-"); s.arrow(420,379,183,379,"hypothesis")
        s.text(318,449,"Opposite charge → opposite drift",17,anchor="middle")
        s.text(882,169,"Concentration-driven diffusion",21,anchor="middle",bold=True)
        for x,y in [(687,240),(742,260),(703,320),(761,363),(686,397),(1068,282),(1068,385)]: s.ion(x,y)
        s.arrow(813,311,987,311); s.text(891,290,"high → low",18,anchor="middle")
        s.text(882,449,"Illustrative concentration gradient",17,anchor="middle")
    elif key in {"sei-formation", "selective-passivation", "heterogeneous-sei"}:
        s.electrode(label="Reducing electrode")
        s.rect(70,298,1060,101,"#F4F7F9","#748697",3)
        if key == "sei-formation":
            for x in (170,410,650,890):
                s.ligand(x,212); s.rect(x-55,321,110,51,colors[2],"#FFFFFF",6,.3)
                s.arrow(x,414,x,249,"electron")
            s.text(600,145,"Electrolyte reduction → interphase products",23,anchor="middle",bold=True)
            s.text(600,490,"SEI composition is mixed and system dependent",17,anchor="middle")
        elif key == "selective-passivation":
            for x in (230,535,840): s.ion(x,206); s.arrow(x,242,x,391)
            s.arrow(1012,455,1012,357,"electron"); s.path("M987 338L1037 367M1037 338L987 367",colors[1],4)
            s.text(600,145,"Desired ion-selective passivation",23,anchor="middle",bold=True)
            s.text(602,276,"Cation transfer",18,anchor="middle"); s.text(1078,205,"e⁻ blocked",17,anchor="middle")
        else:
            for i,(x,w,c) in enumerate([(70,190,2),(260,140,3),(400,260,2),(660,170,3),(830,300,2)]): s.rect(x,300,w,98,colors[c],"#FFFFFF",2,.25)
            s.ion(250,199); s.ion(740,199)
            s.path("M250 227L250 295L340 329L340 390", colors[0],3,True)
            s.arrow(340,364,340,391,"ion",True)
            s.path("M740 227L740 309L820 347L820 389", colors[0],3,True)
            s.arrow(820,366,820,391,"ion",True)
            s.text(600,145,"Heterogeneous domains; possible local routes",23,anchor="middle",bold=True)
            s.text(600,273,"Dashed paths: hypotheses requiring spatial evidence",18,anchor="middle")
        if key != "sei-formation": s.text(600,495,"Layer thickness and composition are not to scale",16,anchor="middle")
    elif key == "cei-formation":
        s.electrode(label="Positive electrode at oxidizing potential")
        s.rect(70,333,1060,65,colors[2],"#748697",3,.18)
        for x in (220,600,980):
            s.ligand(x,207); s.arrow(x,236,x,331,"electron")
            s.rect(x-58,342,116,40,colors[3],"#FFFFFF",6,.25)
        s.text(600,141,"Electrolyte oxidation → cathode-side interphase",23,anchor="middle",bold=True)
        s.text(600,284,"e⁻ transferred from reacting species to electrode",18,anchor="middle")
        s.text(600,495,"CEI composition and protective function require evidence",16,anchor="middle")
    elif key == "nucleation-growth":
        s.electrode(label="Substrate / electronic conductor")
        for x,rad in [(180,13),(390,23),(660,39),(970,61)]:
            s.circle(x,398-rad,rad,"#AABCCA","#536579")
            s.ion(x,207); s.arrow(x,239,x,393-2*rad)
        s.text(600,141,"Illustrative nuclei → growing metal deposits",23,anchor="middle",bold=True)
        s.arrow(190,457,1005,457,"process")
        s.text(600,495,"Shapes do not specify a nucleation law or growth rate",16,anchor="middle")
    elif key == "plating-stripping":
        for x,label in [(312,"Plating"),(888,"Stripping")]: s.text(x,151,label,25,anchor="middle",bold=True)
        s.electrode(75,405,475,70,"Metal"); s.electrode(650,405,475,70,"Metal")
        s.ion(310,229); s.ion(890,229)
        s.arrow(310,265,310,380); s.arrow(890,383,890,267)
        s.arrow(165,445,258,351,"electron"); s.arrow(939,350,1038,445,"electron")
        s.text(310,188,"Li⁺ + e⁻ → Li⁰",24,anchor="middle"); s.text(890,188,"Li⁰ → Li⁺ + e⁻",24,anchor="middle")
        s.text(600,501,"Half reactions; side-reaction losses remain possible",16,anchor="middle")
    elif key == "inactive-lithium":
        s.electrode(label="Electronic conductor")
        s.circle(308,315,70,"#F1F5F8",colors[2],7); s.circle(308,315,46,"#B2C1CE")
        s.text(308,322,"Li⁰",24,anchor="middle",bold=True)
        s.text(308,205,"Isolated metallic Li",22,anchor="middle",bold=True)
        s.path("M308 385V399",colors[1],3,True); s.path("M293 382L323 399M323 382L293 399",colors[1],3)
        s.rect(638,255,405,124,colors[2],colors[2],9,.15)
        for x in (702,815,934): s.text(x,324,"Li⁺",23,colors[2],"middle",True)
        s.text(839,205,"Li in SEI compounds",22,anchor="middle",bold=True)
        s.text(600,495,"Chemical quantification distinguishes inventory classes",16,anchor="middle")
    elif key == "film-reformation":
        for x,lab in [(70,"Surface change"),(650,"Further reaction")]:
            s.electrode(x,401,480,74,"Metal")
            s.rect(x,320,480,80,colors[2],"#748697",3,.2)
            s.path(f"M{x+228} 320l-19 24l30 20l-18 36", "#FFFFFF",13)
            s.text(x+240,150,lab,23,anchor="middle",bold=True)
        s.arrow(555,359,624,359,"process")
        s.ligand(889,225); s.arrow(889,252,889,320,"process")
        s.rect(863,338,62,60,colors[3],"#FFFFFF",9,.35)
        s.text(600,495,"Fresh surface exposure can consume additional electrolyte and metal",16,anchor="middle")
    elif key == "solid-contact-loss":
        s.rect(75,164,1050,126,"#EEF3F7","#748697",3)
        s.text(600,218,"Solid electrolyte",22,anchor="middle",bold=True)
        s.electrode(75,298,1050,166,"")
        for x,w in [(145,190),(484,236),(879,181)]: s.rect(x,293,w,47,"#FFFFFF","#748697",17)
        for x in (381,801): s.arrow(x,389,x,297)
        s.text(600,382,"Voids reduce the active contact area",20,anchor="middle")
        s.text(600,436,"Lithium metal",22,anchor="middle",bold=True)
        s.text(600,496,"Subsequent plating: local current can concentrate at remaining contacts",16,anchor="middle")
    elif key == "dual-pathways":
        s.rect(72,162,1055,308,"#F4F7F9","#BAC6D0",8)
        for x,y in [(300,275),(600,337),(915,253)]:
            s.circle(x,y,66,"#DFE7ED","#748697"); s.text(x,y+6,"Active",18,anchor="middle")
        s.path("M110 438L235 331L534 379L850 288L1095 381",colors[1],7)
        s.arrow(108,438,213,349,"electron"); s.text(341,448,"Electronic network",18,colors[1])
        s.arrow(312,177,312,206); s.arrow(600,189,600,267); s.arrow(915,166,915,185)
        s.ion(110,192); s.text(600,138,"Separate routes to active regions",23,anchor="middle",bold=True)
        s.text(600,502,"Topology is conceptual; it does not measure network connectivity",16,anchor="middle")
    else:
        raise ValueError("Unknown mechanism template")
    return s.finish()


def validate_params(params):
    if not isinstance(params, dict) or set(params)-set(PARAMETER_SCHEMA["properties"]): raise ValueError("Unknown parameter keys")
    key = params.get("template")
    record = next((r for r in TEMPLATES if r[0] == key), None)
    if record is None: raise ValueError("Unknown template")
    cation = params.get("cation", "Li+")
    if cation not in {"Li+", "Na+", "K+"}: raise ValueError("Only specified monovalent cations are supported")
    if key not in {"solvation-shell", "ion-pairing", "ligand-exchange", "migration-diffusion", "dual-pathways"} and cation != "Li+": raise ValueError("This illustrated metal/interphase template is lithium-specific; do not relabel the material")
    background = params.get("background", "white")
    if background not in {"white", "transparent"}: raise ValueError("Invalid background")
    colors = params.get("colors", DEFAULT_COLORS)
    reference=params.get("palette_reference")
    if reference is not None:
        allowed={"id","version","name","author","license","url"}
        if not isinstance(reference,dict) or set(reference)-allowed or not {"id","version","license"}<=set(reference) or not all(isinstance(v,str) and len(v)<=500 for v in reference.values()): raise ValueError("Invalid palette reference; keep ID, version and licence with selected explicit colours")
    if not isinstance(colors,list) or len(colors)!=4 or not all(isinstance(c,str) and re.fullmatch(r"#[0-9a-fA-F]{6}",c) for c in colors): raise ValueError("Four hexadecimal colours required")
    return record, colors, background, cation


def render(params):
    record, colors, background, cation = validate_params(params)
    svg = illustrate(record, colors, background, cation)
    if params.get("palette_reference"):
        svg=re.sub(r'<metadata>(.*?)</metadata>',lambda m:'<metadata>'+escape(json.dumps({**json.loads(unescape(m[1])),"palette_reference":params['palette_reference'],"palette_license_independent":True}))+'</metadata>',svg,count=1)
    ET.fromstring(svg)
    return svg


def records():
    """Typed records for site_resources.registry; never labelled as layouts."""
    output = []
    for row, boundary_en in zip(TEMPLATES, BOUNDARIES_EN):
        key, zh, en, group, use, claim, status, boundary, refs = row
        stem=f"commons/mechanisms/mechanism-{key}@{VERSION}"
        output.append({
            "id": f"mechanism-{key}", "version": VERSION, "name": en, "name_zh": zh,
            "author": AUTHOR, "category": "mechanism", "license": "MIT", "status": "community",
            "candidate_status": "review_candidate", "default_visible": True,
            "description": claim, "description_zh": use, "created_at": "2026-10-03", "updated_at": "2026-10-03",
            "tags": ["original-mechanism", group], "source": "Original native SVG geometry; scientific relations checked against separately listed journal sources.",
            "permissions": {"public_display": True,"registry": True,"automated_testing": True,"model_training": False},
            "template":key,"mechanism_group":group,"evidence_type_zh":status,"scientific_boundary_zh":boundary,"scientific_boundary":boundary_en,
            "supported_cations":["Li+","Na+","K+"] if key in {"solvation-shell","ion-pairing","ligand-exchange","migration-diffusion","dual-pathways"} else ["Li+"],
            "cation_scope_zh":"配位/一般传输场景，可选一价 Li+、Na+、K+。" if key in {"solvation-shell","ion-pairing","ligand-exchange","migration-diffusion","dual-pathways"} else "当前空间图以锂体系为范围；更换金属/价态须重新核对材料、反应与证据。",
            "scientific_references":[REFERENCES[r] for r in refs],"source_figures_reused":False,
            "preview_url": stem+".svg", "source_url":stem+".json", "prompt_url":stem+"-prompt.txt",
            "renderer_url":f"commons/mechanisms/VoltPeer-mechanism-source-v{VERSION}.zip", "detail_url":"mechanisms.html#"+key,
            "visual_method":"Original imagegen composition reference, scientific correction, native editable vector reconstruction; generic donor symbols carry no chemical bonds.",
            "composition_reference":"VoltPeer original desolvation + SEI artwork, 2026-10-03; reference pixels are not embedded.",
            "scientific_caption":"Generic donor D glyphs are not molecular structures. Repeated ions show process snapshots. Material dimensions, counts, domains and paths are schematic.",
            "scientific_caption_zh":"D 表示抽象配位基团，不是分子结构；重复离子表示过程中的不同快照。尺寸、配位数、域大小与传输路线均为示意。",
            "quality":{"format_checked":True,"scientific_review":"source-grounded conceptual template; no human certification claimed","final_size_qa":"not certified"},
        })
    return output


def write_assets(destination=None):
    destination = Path(destination) if destination else DOCS / "commons/mechanisms"
    destination.mkdir(parents=True,exist_ok=True)
    previous=destination/"catalog.json"
    if previous.is_file():
        previous_data=previous.read_bytes()
        previous_versions={r.get("version") for r in json.loads(previous_data).get("assets",[])}
        if len(previous_versions)==1 and VERSION not in previous_versions:
            previous_version=next(iter(previous_versions))
            snapshot=destination/f"catalog-v{previous_version}.json"
            if snapshot.exists() and snapshot.read_bytes()!=previous_data:
                raise ValueError("Existing versioned catalogue differs; preserve the fixed snapshot")
            if not snapshot.exists():snapshot.write_bytes(previous_data)
    rejected=destination/"rejected-drafts-v1.0.0.json"
    if previous.is_file() and not rejected.exists():
        old=json.loads(previous.read_text(encoding="utf-8"))
        old_assets=[{**r,"candidate_status":"rejected_draft","default_visible":False} for r in old.get("assets",[]) if r.get("version")=="1.0.0"]
        if old_assets: rejected.write_text(json.dumps({"reason":"User rejected visual quality; retained for provenance, not candidate figures","assets":old_assets},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    catalogue=records()
    for record in catalogue:
        key=record["template"]; params={"template":key,"cation":"Li+","colors":DEFAULT_COLORS,"background":"white"}
        stem=f"{record['id']}@{VERSION}"
        svg_path=destination/f"{stem}.svg"
        svg_path.write_text(render(params),encoding="utf-8")
        (destination/f"{stem}.json").write_text(json.dumps({**record,"parameters":params},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        prompt=(f"请用 voltpeer-mechanism 基于 {key}@{VERSION} 创作一张机理示意图。我的体系与证据是：[请填写]。先核对离子电荷、反应方向、材料和已知过程，区分测量支持、概念模型与假说。\n"
                f"适用边界：{record['scientific_boundary_zh']}\n"
                "先调用可用图像生成工具创作空间构图稿并检查，然后据自己的稿重画可编辑原生 SVG。要有清楚的电极透视/剖切和材料层次，采用抽象 generic donor ligand，不生成未核对分子价键。\n"
                "过程路径用约 2.5 px 细短线和 8–10 px 小型开放箭头尖，箭头尖固定尺寸，不随路径线宽膨胀；让材料和离子成为主体，保留科学端点与方向，压缩无意义留白但不挤标注，不画粗大流程箭头，不堆装饰。\n"
                "请输出可编辑原生 SVG、参数 JSON、可重跑源码和来源记录。白底或透明底，不复制论文图像，不把示意箭头、配位数或结构当作我的实验结果。重复离子须注明为过程快照。\n")
        (destination/f"{stem}-prompt.txt").write_text(prompt,encoding="utf-8")
        record["sha256"]=hashlib.sha256(svg_path.read_bytes()).hexdigest()
    (destination/"catalog.json").write_text(json.dumps({"schema_version":"1.0","type":"mechanism","updated_at":"2026-10-03","license":"MIT","source_licences_independent":True,"assets":catalogue},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (destination/"parameter-schema.json").write_text(json.dumps(PARAMETER_SCHEMA,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (destination/"scientific-sources.json").write_text(json.dumps(REFERENCES,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (destination/"LICENSE.txt").write_text(MIT,encoding="utf-8")
    readme=f"VoltPeer original mechanism SVG illustrations v{VERSION} · MIT\nOriginal imagegen composition reference -> scientific correction -> native vector reconstruction. No raster is embedded. D glyphs are abstract generic donor ligands, not atoms or molecules. Material dimensions, counts and paths are illustrative. Repeated ions are process snapshots.\nNo source figure pixels or source geometry are included. Scientific references have independent licences.\n\nRender: python mechanism-renderer.py --params mechanism-desolvation@{VERSION}.json --output new-output/my-mechanism.svg\nDownload parameters separately and extract both Python files together. A record file's parameters object is read automatically. Change four explicit colours or background, keeping the scientific contract.\nExisting output files are rejected. Select a new directory and preserve previous SVGs.\nSVG text, groups, gradients, arrows and paths stay editable in vector editors. Standalone requires explicit colors; no website palette path lookup.\nThe v1.0.0 visual studies were rejected by the user and are not approved figures.\n"
    (destination/"README.txt").write_text(readme,encoding="utf-8")
    with zipfile.ZipFile(destination/f"VoltPeer-mechanism-source-v{VERSION}.zip","w",zipfile.ZIP_DEFLATED) as archive:
        files=[(Path(__file__),"mechanism-renderer.py"),(Path(__file__).with_name("mechanism_art.py"),"mechanism_art.py")]
        files.extend((destination/name,name) for name in ("README.txt","parameter-schema.json","scientific-sources.json","LICENSE.txt"))
        for path,name in files:
            info=zipfile.ZipInfo(name,date_time=(2026,10,3,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644 << 16
            archive.writestr(info,path.read_bytes())
    # Remove only this generated standalone copy, never arbitrary source files.
    old_copy=destination/"mechanism-renderer.py"
    if old_copy.is_file() and destination.resolve()==(DOCS/"commons/mechanisms").resolve(): old_copy.unlink()
    return catalogue


def page():
    cards=[]
    # Begin with spatial interfaces so the first row shows material depth.
    # This changes presentation only; record order and scientific tuple indices stay fixed.
    display_order=["desolvation","solid-contact-loss","heterogeneous-sei","plating-stripping","sei-formation","selective-passivation","cei-formation","nucleation-growth","inactive-lithium","dual-pathways","double-layer","film-reformation","solvation-shell","ion-pairing","ligand-exchange","migration-diffusion"]
    for r in sorted(records(),key=lambda record:display_order.index(record["template"])):
        cards.append(f'''<article class="mechanism-card" id="{r['template']}" data-mechanism-group="{r['mechanism_group']}" data-mechanism-template="{r['template']}"><button class="mechanism-open" type="button" aria-label="查看{escape(r['name_zh'])}"><img src="{r['preview_url']}" alt="{escape(r['name_zh'])}原创概念示意" width="1600" height="1050" loading="lazy"></button><div class="mechanism-card-copy"><span class="mechanism-evidence">{escape(r['evidence_type_zh'])}</span><h2>{escape(r['name_zh'])}</h2><p>{escape(r['description_zh'])}</p><button class="c-quiet mechanism-open" type="button">选择这套机理图 →</button></div></article>''')
    return '''<section class="mechanisms-intro"><div class="wrap"><p class="commons-kicker" data-no-i18n>VoltPeer / Mechanisms</p><h1>机理图</h1><p>选一个过程，核对你的证据，再修改可编辑的矢量图。</p><div class="mechanism-intro-links"><a class="c-quiet" href="skills.html#voltpeer-mechanism">查看机理图 Skill →</a><a class="c-quiet" href="community.html">研究图布局与配色 →</a></div></div></section><section class="mechanisms-library"><div class="wrap"><div class="mechanism-toolbar"><div class="mechanism-filters" role="group" aria-label="机理类型"><button type="button" data-mechanism-filter="all" aria-pressed="true">全部</button><button type="button" data-mechanism-filter="solvation" aria-pressed="false">溶剂化</button><button type="button" data-mechanism-filter="interphase" aria-pressed="false">界面膜</button><button type="button" data-mechanism-filter="transport" aria-pressed="false">传输路径</button><button type="button" data-mechanism-filter="metal" aria-pressed="false">金属沉积</button></div><span id="mechanism-count" role="status" aria-live="polite">16 套原创模板</span></div><div class="mechanism-grid">'''+''.join(cards)+'''</div><details class="mechanism-boundary"><summary>这些图能说明什么</summary><p>模板从期刊论文中核对科学关系，重新设计全部几何、配色和排版。图件与生成代码按 MIT 开放；参考论文的许可独立记录。</p><p>它们是示意图。你需要核对自己的材料、反应方向和证据；配位数、膜厚、箭头长度、域大小与通量没有测量含义。虚线路径表示需要验证的假说。</p><a class="c-quiet" href="commons/mechanisms/scientific-sources.json" download>下载科学来源记录 ↓</a><a class="c-quiet" href="commons/mechanisms/LICENSE.txt" download>图件 MIT 许可 ↓</a></details></div></section><dialog class="mechanism-dialog commons-dialog" id="mechanism-dialog" aria-labelledby="mechanism-title"><div class="commons-dialog-head"><span class="commons-kicker">原创机理模板</span><button class="c-icon" type="button" id="mechanism-close" aria-label="关闭机理图">×</button></div><div class="mechanism-dialog-content"><div class="mechanism-canvas"><img id="mechanism-preview" width="1600" height="1050" alt=""><div class="mechanism-palette-controls"><label>配色<select id="mechanism-palette"><option value="default">青蓝 / 铜棕 / 紫 / 绿</option></select></label><label>图件背景<select id="mechanism-background"><option value="white">白底</option><option value="transparent">透明</option></select></label><a class="c-quiet" href="palettes.html">查看完整配色库 →</a></div></div><div class="mechanism-details"><p class="mechanism-evidence" id="mechanism-evidence"></p><h2 id="mechanism-title"></h2><p id="mechanism-description"></p><div class="mechanism-evidence-note"><strong>用前核对</strong><p id="mechanism-boundary-text"></p></div><div class="mechanism-downloads"><button class="c-button c-primary" id="mechanism-download-svg" type="button">下载 SVG 图件 ↓</button><a class="c-button" id="mechanism-source" download>下载生成源码 ↓</a><button class="c-button" id="mechanism-download-params" type="button">下载参数 JSON ↓</button><a class="c-button" id="mechanism-prompt-download" download>下载提示词 ↓</a><button class="c-quiet" id="mechanism-copy-prompt" type="button">复制给 AI 的请求</button></div><p id="mechanism-feedback" role="status" aria-live="polite"></p><details class="mechanism-sources"><summary>科学来源与许可</summary><div id="mechanism-source-list"></div><p>来源用于核对科学关系。原创图件 MIT 许可不改变论文许可。</p></details><a class="c-quiet" href="start.html">安装与使用教程 →</a></div></div></dialog>'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all",action="store_true",help="Generate all original template assets")
    parser.add_argument("--destination",type=Path)
    parser.add_argument("--template",choices=[r[0] for r in TEMPLATES])
    parser.add_argument("--params",type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--background",choices=["white","transparent"],default="white")
    args=parser.parse_args()
    if args.all:
        assets=write_assets(args.destination); print(f"Generated {len(assets)} original mechanism SVG templates"); return
    if not args.output or not(args.template or args.params): parser.error("Use --all or supply --template/--params and --output")
    params=json.loads(args.params.read_text(encoding="utf-8")) if args.params else {"template":args.template,"background":args.background}
    params=params.get("parameters",params)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    svg = render(params)
    try:
        with args.output.open("x",encoding="utf-8") as handle: handle.write(svg)
    except FileExistsError:
        parser.error("Output exists; choose a new filename or directory to preserve the original SVG")
    print(f"Wrote editable SVG: {args.output}")


if __name__ == "__main__": main()
