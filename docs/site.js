"use strict";

// Chinese stays in the HTML so the page remains useful when JavaScript is off.
const english = {
  skip: "Skip to content",
  topline: "A free, open project for battery researchers",
  navTask: "Choose a task",
  navExamples: "Examples",
  navStart: "Get started",
  navSkills: "All skills",
  heroOverline: "OPEN TOOLS, SHARED WITH BATTERY RESEARCHERS",
  heroLine1: "Give time back to research.",
  heroLine2: "Methods belong to everyone.",
  heroIntro: "Some of our days disappear into moving panels, fixing axes and reformatting a Review. We turn those repeatable steps into free skills, so you can start with what you have and spend more time on better questions.",
  heroAction: "See how to begin",
  heroSecondary: "See examples",
  heroMeta: "Free to use · Open source · Built with the research community",
  heroPlateLabel: "Spatial maps and depth traces in one figure",
  heroPlateCaption: "ToF-SIMS · open at full size",
  sampleTag: "Synthetic example",
  principleLead: "Why build this?",
  principleText: "We want every lab to spend less time nudging figures and more time understanding results and asking new questions.",
  tasksOverline: "START WITH WHAT YOU HAVE",
  tasksTitle: "What are you working on?",
  tasksIntro: "No need to memorize skill names. Start with the material already on your desk.",
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
  examplesTitle: "Here is what it can look like.",
  examplesIntro: "From cycling curves to less common ToF-SIMS figures and panel assembly. Open any example to see the details.",
  galleryTOF: "ToF-SIMS interface map",
  galleryTOFDesc: "Ion maps, overlay and sputter-time profiles",
  galleryCell: "Exploded cell stack",
  galleryCellDesc: "Clear structure with a considered visual hierarchy",
  gallerySpectra: "Spectra and solvation evidence",
  gallerySpectraDesc: "Stacked Raman traces beside RDF curves",
  galleryCE: "Coulombic efficiency",
  galleryCEDesc: "Keep outliers, definitions and test conditions visible",
  galleryAssemble: "Panel assembly",
  galleryAssembleDesc: "Only the labels needed to read the figure",
  galleryFullDesc: "See voltage profiles alongside capacity loss",
  gallerySym: "Symmetric cell",
  gallerySymDesc: "Keep both voltage signs and the time axis",
  galleryXRD: "Operando XRD map",
  galleryStyle: "Six figure styles",
  galleryLab: "Laboratory elements",
  galleryMorph: "Material forms",
  galleryFull: "Full-cell cycling",
  galleryNote: "Every example uses synthetic data or original schematics.",
  galleryDisclaimer: "Read the full use note ↗",
  galleryFiles: "Want to keep editing? Open an SVG:",
  galleryFileCell: "cell diagram",
  authorsLink: "Authors and collaboration ↗",
  galleryFileAssembly: "assembled figure",
  galleryFileChart: "full-cell curve",
  galleryFileLab: "laboratory elements",
  svgOverline: "MAKE THE FINAL TWEAK YOURSELF",
  svgTitle: "An SVG is yours to refine.",
  svgIntro: "Most finished figures include SVG. Open it in free Inkscape to edit text, move a legend and adjust spacing. If the data change, regenerate from the source table.",
  svgDownload: "Get Inkscape from its official site",
  svgStep1Title: "Open the SVG",
  svgStep1Text: "Find a .svg in the examples or your own project and open it in Inkscape.",
  svgStep2Title: "Adjust the layout",
  svgStep2Text: "Change text, legend and element positions. Do not drag a curve to alter values.",
  svgStep3Title: "Save and inspect",
  svgStep3Text: "Save the SVG, export a PDF if the journal asks, and inspect it at submission size.",
  startOverline: "TRY IT TODAY",
  startTitle: "Three steps to a first figure.",
  startIntro: "You do not need to learn a new app first. Follow these steps in the Agent you already use.",
  step1Title: "Choose the Agent you use",
  step1Text: "Codex can use the command below. Kimi, WorkBuddy and other Agents have their own instructions.",
  step1Link: "Find my Agent's steps",
  step2Title: "Download the skill pack",
  step2Text: "Extract and import it in your Agent. If that Agent already works, you need no extra API key just for this project.",
  step2Link: "New to API keys? Start here",
  step3Title: "Upload a file and describe the job",
  step3Text: "Bring a table, several finished panels, or a batch of papers. You can copy the example message below.",
  download: "Download skill pack v0.5.0",
  codexInstallTitle: "Codex: install after extracting",
  codexInstallHint: "Run once",
  copy: "Copy",
  installCaveat: "Change into the extracted folder before running the command. The install guide explains how to update an older copy.",
  pluginSummary: "I prefer the Codex plugin commands",
  pluginNote: "Start a new task after installing, then call a skill.",
  firstPromptOverline: "YOUR FIRST MESSAGE COULD BE",
  firstPrompt: "I have a full-cell cycling data file. First inspect the columns, units and test conditions. Tell me what is missing, then use battery-review-figure to help plot it. Do not guess values.",
  copyPrompt: "Copy this message",
  platformOverline: "FIND THE TOOL YOU KNOW",
  platformTitle: "Which Agent do you use?",
  platformIntro: "Choose the software already on your computer. Open the list for its download and import steps.",
  platformOpen: "Show installation steps for each Agent",
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
  platformFoot: "Unsure which one to choose? Start with an Agent you already know.",
  compatFull: "Full compatibility guide",
  faqOverline: "QUESTIONS BEFORE INSTALLING",
  faqTitle: "First time here? We can help.",
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
  closingOverline: "BUILD IT TOGETHER",
  closingTitle: "Good methods should travel beyond one lab.",
  closingText: "We started by writing down the mistakes we made, the figures we built and the steps we could reuse. Take them, use them, and tell us what is missing. The more people refine these tools together, the more time everyone has for questions worth thinking about.",
  sourceLink: "View the source on GitHub",
  finishLink: "Suggest a feature or report an issue",
  creditsOverline: "PROJECT AUTHORS AND COLLABORATION",
  creditsTitle: "Shuo Guo × Jinlong Jiang",
  creditsText: "Institute of Energy Materials Science, University of Shanghai for Science and Technology. We are turning recurring problems in battery Reviews and scientific figures into open tools, and welcome fellow researchers to help improve them.",
  disclaimerLink: "Use and disclaimer ↗",
  legalOverline: "USE NOTES",
  legalTitle: "Use the tools with confidence. Know where every figure came from.",
  legalIntro: "We want you to get started easily. This page brings the boundaries for examples, manuscripts and source materials into one place when you need them.",
  legalDemoTitle: "Website examples",
  legalDemoText: "All plotted values, including the ToF-SIMS maps, are synthetic examples generated by the public plotting code, not measurements. Geometric diagrams are original concepts and do not establish the structure of any material. Source code, CSV files and editable artwork are in the repository.",
  legalScienceTitle: "Manuscript use",
  legalScienceText: "The tools can plot, assemble and prompt checks. They cannot validate an experiment, establish causality or prove that a citation supports a claim. Before publication, compare the figure with raw data, units, protocols, captions and sources. Matching colors do not make unlike cells or protocols comparable.",
  legalRightsTitle: "Artwork and permissions",
  legalRightsText: "The public resource library contains original code and schematic elements. Papers, commercial assets, photographs and instrument images you upload keep their existing rights. Recoloring or assembling them does not grant reuse permission. Check licensing and credit before publishing third-party artwork.",
  legalAgentTitle: "Agents and API keys",
  legalAgentText: "This static information site does not collect files or API keys. Sign in or configure the model in your Agent's official settings. Skill import differs by platform; the compatibility guide records what we have tested.",
  legalAiTitle: "Disclosure of AI assistance",
  legalAiText: "If your target journal requires disclosure of AI assistance in writing or figure production, follow its official policy at submission time. A more natural visual style does not remove that requirement.",
  legalLicenseTitle: "Open source license",
  legalLicenseText: "This project is released under the MIT License for use, modification and sharing under its terms, with software provided as is. Research data, third-party images and an author's scientific conclusions do not automatically become MIT-licensed.",
  legalBack: "Back to home ←",
  legalCompat: "Compatibility guide ↗",
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
  document.title = document.body.dataset.page === "disclaimer"
    ? (isEnglish ? "Use and disclaimer | BatteryReviewForge" : "使用与免责说明｜BatteryReviewForge")
    : (isEnglish ? "BatteryReviewForge | More time for research" : "BatteryReviewForge｜把时间还给研究");
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
