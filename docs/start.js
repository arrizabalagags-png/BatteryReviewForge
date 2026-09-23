"use strict";

// A small, local-only decision guide. It never reads or uploads the user's files.
const wizardChoices = {
  data: [
    { id: "cycling", zh: "循环、倍率或充放电曲线", en: "Cycling, rate, or voltage curves", guide: "guide.html#data",
      promptZh: "这是我的电池测试数据。请先核对列名、单位、电芯类型和测试条件，告诉我适合画哪些图。先做一张循环或充放电预览，输出可编辑 SVG；缺失信息请标出来，不要猜数值，也不要覆盖原文件。",
      promptEn: "Here are my battery test data. First check columns, units, cell type, and test conditions. Tell me which plots are suitable. Make one cycling or charge/discharge preview and export an editable SVG. Flag missing information; do not invent values or overwrite my source files." },
    { id: "ce", zh: "库伦效率", en: "Coulombic efficiency", guide: "guide.html#data",
      promptZh: "这是我的库伦效率数据。请先确认它是逐圈 CE 还是 Aurbach 测试，再核对列名、百分比单位、电芯和测试条件。按对应协议画图，不要把 Aurbach 画成逐圈曲线。保留异常点和原始数据，输出可编辑 SVG。",
      promptEn: "Here are my Coulombic-efficiency data. First identify whether this is cycle-by-cycle CE or an Aurbach protocol, then check columns, percentage units, cell type, and test conditions. Plot the actual protocol; never turn an Aurbach test into a cycle trace. Keep excursions and source data, and export editable SVG." },
    { id: "other", zh: "其他电池数据，不确定图型", en: "Other battery data; unsure of plot type", guide: "guide.html#data",
      promptZh: "这是我的电池实验数据，但我还没决定用什么图。请先列出文件里的变量、单位和缺失条件，再给我两种适合的图型和各自能回答的问题。先做最容易核对的一张预览；不要编造缺失数值。",
      promptEn: "Here are my battery data, but I have not chosen a chart. List variables, units, and missing conditions first. Suggest two suitable plot types and what each would show. Preview the easiest one to verify; do not invent missing values." },
  ],
  images: [
    { id: "assemble", zh: "把现成图片拼成 Figure", en: "Assemble existing panels", guide: "guide.html#assemble",
      promptZh: "请把这些现成图片拼成一张论文 Figure。先逐张说清内容和清晰度，找出主图和阅读顺序，给我几种小版式预览。选定后统一字母、字号、边界和留白；不要拉伸图像、裁掉坐标轴或比例尺，也不要加多余副标题。",
      promptEn: "Please assemble these images into one manuscript figure. Inventory their content and resolution, identify the lead panel and reading order, then show a few small layout previews. Align letters, typography, margins, and spacing. Do not stretch panels, crop axes or scale bars, or add redundant subtitles." },
    { id: "schematic", zh: "把想法画成原创示意图", en: "Draw an original schematic", guide: "guide.html#schematic",
      promptZh: "我想把这个电池研究想法画成一张原创示意图。先用一句话确认图要解释什么，区分已观察结果和假设，再给我两种简洁构图。确认科学标签后做可编辑 SVG，不要凭空补机理。",
      promptEn: "I want an original schematic for this battery research idea. First summarize what the figure should explain in one sentence, separate observations from hypotheses, and propose two clean compositions. Make an editable SVG after checking scientific labels; do not invent mechanisms." },
  ],
  review: [
    { id: "plan", zh: "刚有题目，想先定综述方向", en: "Define a Review angle", guide: "guide.html#review",
      promptZh: "我准备写一篇电池综述，题目或想法在这里。请先看已有文献和相近综述，帮我确定读者、核心问题、边界和三层大纲。把已核实的来源与待核实的线索分开，不要直接开始堆正文。",
      promptEn: "I am planning a battery Review. Here is my topic or idea. Examine relevant literature and neighboring Reviews first, then define the audience, central question, scope, and a three-level outline. Separate verified sources from leads that still need checking before drafting prose." },
    { id: "draft", zh: "已有初稿，想检查和改进", en: "Improve an existing draft", guide: "guide.html#review",
      promptZh: "这是我的电池综述初稿。请先判断主线是否清楚，逐节列出最影响说服力的问题，核对关键数据与引文能否支持原句。给我按优先级排列的修改清单；修改文字时保留原意和论断强度。",
      promptEn: "Here is my battery Review draft. First assess the argument, list the highest-impact problems by section, and check whether key numbers and citations support the wording. Give me a prioritized revision list; preserve meaning and claim strength when editing." },
  ],
};

let chosenMaterial = null;
let chosenGoal = null;
const stepSections = [...document.querySelectorAll(".wizard-step")];
const progressItems = [...document.querySelectorAll("[data-progress]")];
const goalHost = document.getElementById("wizard-goals");

function wizardEnglish() { return document.documentElement.lang === "en"; }

function renderGoals() {
  goalHost.replaceChildren();
  if (!chosenMaterial) return;
  wizardChoices[chosenMaterial].forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.goal = choice.id;
    const strong = document.createElement("strong");
    strong.textContent = wizardEnglish() ? choice.en : choice.zh;
    const arrow = document.createElement("i");
    arrow.textContent = "↗";
    arrow.setAttribute("aria-hidden", "true");
    button.append(strong, arrow);
    button.addEventListener("click", () => {
      chosenGoal = choice;
      renderResult();
      navigate(3);
    });
    goalHost.appendChild(button);
  });
}

function renderResult() {
  if (!chosenGoal) return;
  document.getElementById("wizard-prompt").textContent = wizardEnglish()
    ? chosenGoal.promptEn : chosenGoal.promptZh;
  document.getElementById("wizard-detail").href = chosenGoal.guide;
}

function showStep(number, focus = false) {
  stepSections.forEach((section) => { section.hidden = Number(section.dataset.step) !== number; });
  progressItems.forEach((item) => {
    if (Number(item.dataset.progress) === number) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  });
  if (focus) {
    const heading = document.querySelector(`[data-step="${number}"] h2`);
    heading.tabIndex = -1;
    heading.focus({ preventScroll: true });
    document.querySelector(".wizard-progress").scrollIntoView({ behavior: "instant", block: "start" });
  }
}

function navigate(number) {
  history.pushState({ wizardStep: number }, "", `#step${number}`);
  showStep(number, true);
}

document.querySelectorAll("[data-material]").forEach((button) => {
  button.addEventListener("click", () => {
    chosenMaterial = button.dataset.material;
    chosenGoal = null;
    renderGoals();
    navigate(2);
  });
});

document.querySelectorAll("[data-back]").forEach((button) => {
  button.addEventListener("click", () => history.back());
});

window.addEventListener("popstate", (event) => {
  const step = event.state?.wizardStep || 1;
  showStep(step === 3 && !chosenGoal ? 2 : step, true);
});

window.addEventListener("brf:language", () => { renderGoals(); renderResult(); });

history.scrollRestoration = "manual";
history.replaceState({ wizardStep: 1 }, "", location.pathname + location.search);
const requested = new URLSearchParams(location.search).get("material");
if (requested && Object.hasOwn(wizardChoices, requested)) {
  chosenMaterial = requested;
  renderGoals();
  navigate(2);
} else {
  showStep(1);
}
