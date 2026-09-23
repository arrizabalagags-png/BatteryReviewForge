"use strict";

// Chinese stays in the HTML so the page remains useful when JavaScript is off.
const english = {
  skip: "Skip to content",
  topline: "A free, open project for battery researchers",
  navTask: "Choose a task",
  navExamples: "Examples",
  navStart: "Get started",
  navSkills: "All skills",
  heroOverline: "AN OPEN TOOLBOX FOR BATTERY RESEARCH",
  heroLine1: "Less time fixing figures.",
  heroLine2: "More time for research.",
  heroIntro: "Bring your data, panels or papers. Make figures, assemble panels, and work through a battery Review from topic to revision. You stay in charge of every scientific decision.",
  heroAction: "See how to begin",
  heroSecondary: "See examples",
  heroMeta: "Free and open source · 13 separate skills · Chinese and English",
  heroPlateLabel: "From a data table to a clear curve",
  heroPlateCaption: "Full-cell cycling · open at full size",
  sampleTag: "Synthetic data",
  principleLead: "One thing to know first:",
  principleText: "The tools help with repetitive work; the author remains responsible for data, sources and scientific judgment.",
  tasksOverline: "START WITH WHAT YOU HAVE",
  tasksTitle: "What are you working on?",
  tasksIntro: "You do not need to memorize skill names. Find the row closest to your task and open its guide.",
  task1Input: "An experimental data table",
  task1Title: "Turn my table into a figure",
  task1Desc: "Coulombic efficiency, full and half cells, symmetric cells and more",
  task2Input: "Several finished panels",
  task2Title: "Assemble one clean figure",
  task2Desc: "Align panels, letters, boundaries and output size",
  task3Input: "An idea for a schematic",
  task3Title: "Plan the message, then draw",
  task3Desc: "Choose evidence, elements and a consistent style",
  task4Input: "A battery Review to write",
  task4Title: "Work from topic to revision",
  task4Desc: "Plan, verify, draft and audit in stages",
  examplesOverline: "OPEN EACH IMAGE AT FULL SIZE",
  examplesTitle: "Look at the work first.",
  examplesIntro: "These demonstrate the tools and original elements. For a paper, use your actual data and check units, test conditions and sources.",
  galleryCE: "Coulombic efficiency",
  galleryCEDesc: "Keep outliers, definitions and test conditions visible",
  galleryAssemble: "Panel assembly",
  galleryAssembleDesc: "Consistent boundaries, spacing and panel letters",
  gallerySym: "Symmetric cell",
  gallerySymDesc: "Keep both voltage signs and the time axis",
  galleryStyle: "Six figure styles",
  galleryLab: "Laboratory elements",
  galleryMorph: "Material forms",
  galleryFull: "Full-cell cycling",
  galleryNote: "All plotted values are synthetic examples, not experimental findings. The illustration elements are original to this project. Check actual data, text and reuse rights before publication.",
  galleryFiles: "Want to edit an example? Open the vector files:",
  galleryFileAssembly: "assembled figure",
  galleryFileChart: "full-cell curve",
  galleryFileLab: "laboratory elements",
  startOverline: "FIRST TIME HERE? START HERE",
  startTitle: "Three steps to a first figure.",
  startIntro: "These are ordered the way a beginner usually encounters them. If something is unclear, show this page to the Agent you use.",
  step1Title: "Choose an Agent",
  step1Text: "Check the platform status below. Codex has been tested locally; other hosts have different skill import methods. One install command does not fit every Agent.",
  step1Link: "Find my platform",
  step2Title: "Connect a model through that Agent",
  step2Text: "Use your existing platform account or its own API settings. BatteryReviewForge provides no model, server or separate key, and this site does not collect keys.",
  step2Link: "What is an API key?",
  step3Title: "Install a skill and give it material",
  step3Text: "Download the complete ZIP. Codex users can run the commands below after extraction; for other platforms, use their documented import method for an individual skill directory.",
  download: "Download v0.4.0 ZIP",
  codexInstallTitle: "Codex: install after extracting",
  codexInstallHint: "Run once",
  copy: "Copy",
  installCaveat: "First change into the extracted BatteryReviewForge folder. If a skill already exists, review your old copy; use the script's overwrite option only when you intend to update it.",
  pluginSummary: "I prefer the Codex plugin commands",
  pluginNote: "Start a new task after installing, then call a skill.",
  firstPromptOverline: "YOUR FIRST MESSAGE COULD BE",
  firstPrompt: "I have a full-cell cycling data file. First inspect the columns, units and test conditions. Tell me what is missing, then use battery-review-figure to help plot it. Do not guess values.",
  copyPrompt: "Copy this message",
  platformOverline: "CHECK THE HOST BEFORE INSTALLING",
  platformTitle: "Which Agent do you use?",
  platformIntro: "We distinguish local testing, official import support and work still in exploration. They are not the same status.",
  statusVerified: "Tested locally",
  statusDocumented: "Official skill directory documented",
  statusPending: "Import documented · project test pending",
  statusExploring: "Exploring compatibility",
  platformCodex: "Use this page's ZIP installer or the Codex plugin commands. Start a new task after installing.",
  platformGuide: "Detailed guide",
  platformKimi: "Download and extract the full ZIP. On Windows, run ./install.ps1 -Agent KimiCode; on macOS/Linux, run sh install.sh --agent kimi. In a new session, try /skill:battery-review-figure. Project testing is pending.",
  officialDocs: "Official docs",
  platformDeepSeek: "Download and extract the full ZIP. On Windows, run ./install.ps1 -Agent DeepSeekHarness; on macOS/Linux, run sh install.sh --agent dsh. Check that Harness skill components are enabled; copying files alone is not a full test.",
  platformWorkBuddy: "Download and extract the WorkBuddy collection. In Skills → Add skill → Upload skill, choose one individual skill ZIP at a time. Do not upload the collection ZIP itself. Client testing is pending.",
  workbuddyDownload: "Download WorkBuddy collection",
  platformDoubao: "We have not verified a third-party SKILL.md import procedure. You can use ordinary file Q&A with the relevant skill guide as reference, but that does not mean a skill is installed or a script will run.",
  platformStatus: "Compatibility notes",
  platformFoot: "Agents not listed here have no installation guide yet. Claude Code has no compatibility guide or project test here at present.",
  compatFull: "Full compatibility guide",
  faqOverline: "QUESTIONS BEFORE INSTALLING",
  faqTitle: "Clear up the basics first.",
  faq1Q: "What is an API key? Do I need one?",
  faq1A: "Some Agents use a key to connect to a model service. Whether you need one depends on your host and sign-in method. Follow that host's official account or model setup before installing this project's skills.",
  faq2Q: "Should I paste a key into a website or chat?",
  faq2A: "No. This is a static information site with no key input form. Keep secrets only in the host's official settings. Do not paste them into chats, screenshots or public repositories.",
  faq3Q: "Can I use it if I do not know Python?",
  faq3A: "You can start with planning, literature and writing skills. Generating data figures or assembling panels requires the Python dependencies in those skill guides; you can give the material to your Agent and ask it to explain each step.",
  faq4Q: "Can I send it a published figure to redraw?",
  faq4A: "It can study the layout, color logic and message, then make a new figure from data you are allowed to use. Do not publish someone else's artwork as your own. Check numbers, sources and reuse rights.",
  skillsOverline: "ONE SKILL PER JOB",
  skillsTitle: "13 skills, each with its own guide.",
  skillsIntro: "For a first try, choosing one task above is enough. For a full Review, open these guides in order as your work moves forward.",
  groupPlan: "Start and plan",
  sForge: "Coordinate the full Review workflow",
  sPlan: "Define the question, scope and outline",
  groupEvidence: "Literature and evidence",
  sLiterature: "Search, screen and map papers",
  sClaim: "Check claims and citations one by one",
  sMetrics: "Check whether battery metrics can compare",
  groupMake: "Write and make figures",
  sWrite: "Draft and revise sections",
  sFigure: "Make figures from data or ideas",
  sAssemble: "Assemble existing panels neatly",
  sPolish: "Polish, translate and shorten prose",
  groupFinish: "Check and publish",
  sAudit: "Audit the full draft before submission",
  sReviewer: "Simulate an independent review",
  sSubmission: "Check journal fit and submission materials",
  sResponse: "Respond to reviewers point by point",
  closingOverline: "WHY OPEN SOURCE",
  closingTitle: "Leave more research time for thinking.",
  closingText: "Researchers have all lost time adjusting axes, moving panels and chasing formats. We publish these tools and methods so the next person starts further ahead. A plain, accurate, readable figure matters more than a fashionable template.",
  sourceLink: "View the GitHub source",
  finishLink: "Read the visual finishing guide",
  footerMotto: "Free to use. Contributions welcome.",
  footerStart: "Back to setup",
  creditInstitute: "Institute of Energy Materials Science, University of Shanghai for Science and Technology",
  creditPeople: "In collaboration with Shuo Guo and Jinlong Jiang"
};

const translated = [...document.querySelectorAll("[data-t]")];
const chinese = new Map(translated.map((element) => [element, element.textContent]));

function setLanguage(language) {
  const isEnglish = language === "en";
  document.documentElement.lang = isEnglish ? "en" : "zh-CN";
  document.documentElement.dataset.lang = isEnglish ? "en" : "zh";
  document.title = isEnglish
    ? "BatteryReviewForge | More time for research"
    : "BatteryReviewForge｜把时间还给研究";
  translated.forEach((element) => {
    const value = isEnglish ? english[element.dataset.t] : chinese.get(element);
    if (value !== undefined) element.textContent = value;
  });
  document.querySelectorAll("[data-set-lang]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.setLang === language));
  });
  try { window.localStorage.setItem("brf-language", language); } catch (_) { /* storage may be disabled */ }
}

document.querySelectorAll("[data-set-lang]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.setLang));
});

try {
  if (window.localStorage.getItem("brf-language") === "en") setLanguage("en");
} catch (_) { /* storage may be disabled */ }

async function copyText(value) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const temporary = document.createElement("textarea");
  temporary.value = value;
  temporary.style.position = "fixed";
  temporary.style.opacity = "0";
  document.body.appendChild(temporary);
  temporary.select();
  const copied = document.execCommand("copy");
  temporary.remove();
  if (!copied) throw new Error("Copy unavailable");
}

document.querySelectorAll("[data-copy], [data-copy-target]").forEach((button) => {
  button.addEventListener("click", async () => {
    const source = button.dataset.copyTarget
      ? document.getElementById(button.dataset.copyTarget)?.textContent
      : button.dataset.copy;
    if (!source) return;
    const label = button.querySelector("[data-t]") || button;
    try {
      await copyText(source);
      label.textContent = document.documentElement.lang === "en" ? "Copied" : "已复制";
    } catch (_) {
      label.textContent = document.documentElement.lang === "en" ? "Select and copy" : "请选中文字复制";
    }
    window.setTimeout(() => {
      const isEnglish = document.documentElement.lang === "en";
      label.textContent = isEnglish ? english[label.dataset.t] : chinese.get(label);
    }, 2200);
  });
});
