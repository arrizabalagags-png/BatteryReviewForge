"use strict";

const order = ["client", "os", "install", "test"];
const clients = {codex:"Codex", kimi:"Kimi Code", workbuddy:"WorkBuddy", dsh:"DeepSeek Harness"};
const systems = {windows:"Windows", macos:"macOS", linux:"Linux"};
const tasks = {full:"全电池长循环", ce:"Li‖Cu CE", assembly:"六图拼版"};
const version = document.body.dataset.version;
const mainZip = "downloads/BatteryReviewForge-v" + version + ".zip";
const wbZip = "downloads/BatteryReviewForge-WorkBuddy-v" + version + ".zip";
// Beta means the install path is documented, not that a complete plot was tested.
const compatibility = {
  codex: {
    windows:{level:"verified",status:"Windows 本机安装与试运行已验证",agent:""},
    macos:{level:"beta",status:"安装脚本已提供；macOS 完整任务待实测",agent:""},
    linux:{level:"beta",status:"安装脚本已提供；Linux 完整任务待实测",agent:""}
  },
  kimi: {
    windows:{level:"beta",status:"技能目录已核对；Windows 完整任务待实测",agent:" -Agent KimiCode"},
    macos:{level:"beta",status:"技能目录已核对；macOS 完整任务待实测",agent:" --agent kimi"},
    linux:{level:"beta",status:"技能目录已核对；Linux 完整任务待实测",agent:" --agent kimi"}
  },
  dsh: {
    windows:{level:"beta",status:"技能目录已核对；Windows 完整任务待实测",agent:" -Agent DeepSeekHarness"},
    macos:{level:"beta",status:"技能目录已核对；macOS 完整任务待实测",agent:" --agent dsh"},
    linux:{level:"beta",status:"技能目录已核对；Linux 完整任务待实测",agent:" --agent dsh"}
  },
  workbuddy:{import:{level:"beta",status:"界面导入方法已核对；完整任务待客户端实测"}}
};
const state = {task:"",client:"",os:"",step:"client"};

function getSaved(key) {
  try { return localStorage.getItem(key) || ""; } catch { return ""; }
}
function save(key,value) {
  try { localStorage.setItem(key,value); } catch { /* Storage can be disabled. */ }
}
function spec() {
  if (!state.client) return null;
  return state.client === "workbuddy" ? compatibility.workbuddy.import :
    compatibility[state.client]?.[state.os] || null;
}
function route() {
  return state.client === "workbuddy" ? ["client","install","test"] : order;
}
function readURL() {
  const query = new URLSearchParams(location.search);
  state.task = tasks[query.get("task")] ? query.get("task") : (location.hash === "#assembly" ? "assembly" : "");
  state.client = clients[query.get("client")] ? query.get("client") : "";
  state.os = state.client && state.client !== "workbuddy" && systems[query.get("os")] ? query.get("os") : "";
  state.step = order.includes(query.get("step")) ? query.get("step") : "client";
  if (!state.client) state.step = "client";
  else if (state.client === "workbuddy" && state.step === "os") state.step = "install";
  else if (state.client !== "workbuddy" && !state.os && ["install","test"].includes(state.step)) state.step = "os";
  if (state.step === "test" && !spec()) state.step = "install";
}
function writeURL(replace=false) {
  const query = new URLSearchParams();
  if (state.task) query.set("task",state.task);
  if (state.client) query.set("client",state.client);
  if (state.os && state.client !== "workbuddy") query.set("os",state.os);
  query.set("step",state.step);
  history[replace ? "replaceState" : "pushState"]({...state},"",location.pathname + "?" + query);
}
function goToStep(step,replace=false) {
  if (!order.includes(step)) return;
  if (step !== "client" && !state.client) step = "client";
  if (state.client === "workbuddy" && step === "os") step = "install";
  if (state.client && state.client !== "workbuddy" && ["install","test"].includes(step) && !state.os) step = "os";
  if (step === "test" && !spec()) step = "install";
  state.step = step;
  writeURL(replace);
  render();
  if (step === "test" && state.task) {
    requestAnimationFrame(() => document.querySelector('[data-demo="' + state.task + '"]')?.scrollIntoView({block:"start",behavior:"smooth"}));
  } else {
    window.scrollTo({top:0,behavior:"auto"});
  }
}
function addStep(text,download) {
  const li = document.createElement("li");
  li.textContent = text;
  if (download) {
    const link = document.createElement("a");
    link.href = download;
    link.className = "text-link";
    link.textContent = "下载 BatteryReviewForge ↓";
    li.append(" ",link);
  }
  document.querySelector("#install-steps").append(li);
}
function renderInstall() {
  document.querySelector("#current-client").textContent = clients[state.client] || "你的软件";
  document.querySelector("#current-os-wrap").hidden = state.client === "workbuddy";
  document.querySelector("#current-os").textContent = systems[state.os] || "";
  const available = Boolean(spec());
  document.querySelector("#install-unavailable").hidden = available;
  document.querySelector("#install-content").hidden = !available;
  document.querySelector('[data-wizard-next="test"]').hidden = !available;
  if (!available) return;
  const steps = document.querySelector("#install-steps");
  steps.replaceChildren();
  const commandBlock = document.querySelector("#command-block");
  const instruction = document.querySelector("#install-instruction");
  const command = document.querySelector("#install-command");
  if (state.client === "workbuddy") {
    instruction.textContent = "在软件界面导入，不用选择电脑系统，也不用敲命令。";
    addStep("先下载 WorkBuddy 专用合集。",wbZip);
    addStep("解压合集，找到里面的 13 个单技能 ZIP。");
    addStep("在 WorkBuddy 打开“技能 → 添加技能 → 上传技能”，选一个单技能 ZIP。实验数据出图选 battery-review-figure，拼图选 battery-figure-assemble。");
    commandBlock.hidden = true;
  } else {
    instruction.textContent = "先下载，再解压，最后复制安装命令。";
    addStep("下载完整技能安装包。",mainZip);
    if (state.os === "windows") {
      addStep("右键下载的 ZIP，选“全部解压”。");
      addStep("打开解压后的文件夹，点顶部地址栏，输入 powershell 并按回车。");
      addStep("把下面这一行复制到 PowerShell，按回车；完成后新开一个 Agent 会话。");
      command.textContent = ".\\install.ps1" + spec().agent;
    } else {
      addStep("双击 ZIP 解压，找到含 install.sh 的文件夹。");
      addStep("打开终端，输入 cd 和空格，把解压后的文件夹拖进终端，按回车。");
      addStep("复制下面这一行到终端，按回车；完成后新开一个 Agent 会话。");
      command.textContent = "sh install.sh" + spec().agent;
    }
    commandBlock.hidden = false;
  }
  document.querySelector("#install-status").textContent = spec().status;
}
function render() {
  document.querySelectorAll("[data-wizard-step]").forEach(panel => { panel.hidden = panel.dataset.wizardStep !== state.step; });
  const workbuddy = state.client === "workbuddy";
  document.querySelector('[data-progress-step="os"]').hidden = workbuddy;
  document.querySelector('[data-progress-sep="os"]').hidden = workbuddy;
  document.querySelectorAll("[data-progress-step]").forEach(button => {
    const step = button.dataset.progressStep;
    button.classList.toggle("current",step === state.step);
    if (step === state.step) button.setAttribute("aria-current","step"); else button.removeAttribute("aria-current");
    button.disabled = route().indexOf(step) > route().indexOf(state.step);
    if (workbuddy) button.textContent = step === "client" ? "1 选软件" : step === "install" ? "2 导入" : step === "test" ? "3 试运行" : button.textContent;
    else button.textContent = step === "client" ? "1 选软件" : step === "os" ? "2 选系统" : step === "install" ? "3 安装" : "4 试运行";
  });
  document.querySelectorAll("[data-choice-client]").forEach(button => button.classList.toggle("selected",button.dataset.choiceClient === state.client));
  document.querySelectorAll("[data-choice-os]").forEach(button => button.classList.toggle("selected",button.dataset.choiceOs === state.os));
  const hint = document.querySelector("#task-hint");
  hint.hidden = !state.task;
  hint.textContent = state.task ? "你想试：" + tasks[state.task] + "。选好软件后，我们会带你找到对应的演示文件。" : "";
  const savedClient = getSaved("preferredClient"), savedOS = getSaved("preferredOS");
  const resume = document.querySelector("#resume-choice");
  resume.hidden = !clients[savedClient] || (savedClient !== "workbuddy" && !systems[savedOS]);
  if (!resume.hidden) resume.textContent = "继续使用 " + clients[savedClient] + (savedClient === "workbuddy" ? "" : " · " + systems[savedOS]) + " →";
  document.querySelectorAll("[data-demo]").forEach(card => card.classList.toggle("recommended",card.dataset.demo === state.task));
  renderInstall();
}
function selectClient(client) {
  if (!clients[client]) return;
  if (state.client !== client) state.os = "";
  state.client = client;
  save("preferredClient",client);
  if (client === "workbuddy") { state.os = ""; goToStep("install"); }
  else goToStep("os");
}
document.querySelectorAll("[data-choice-client]").forEach(button => button.addEventListener("click",() => selectClient(button.dataset.choiceClient)));
document.querySelectorAll("[data-choice-os]").forEach(button => button.addEventListener("click",() => {
  if (!systems[button.dataset.choiceOs]) return;
  state.os = button.dataset.choiceOs;
  save("preferredOS",state.os);
  goToStep("install");
}));
document.querySelector("#resume-choice").addEventListener("click",() => {
  state.client = getSaved("preferredClient");
  state.os = state.client === "workbuddy" ? "" : getSaved("preferredOS");
  goToStep("install");
});
document.querySelectorAll("[data-progress-step]").forEach(button => button.addEventListener("click",() => {
  if (!button.disabled) goToStep(button.dataset.progressStep);
}));
document.querySelectorAll("[data-wizard-next]").forEach(button => button.addEventListener("click",() => goToStep(button.dataset.wizardNext)));
document.querySelectorAll("[data-wizard-back]").forEach(button => button.addEventListener("click",() => {
  const current = route().indexOf(state.step);
  if (current > 0) goToStep(route()[current-1]);
}));
async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    try { await navigator.clipboard.writeText(text); return true; } catch { /* Try the legacy path. */ }
  }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("aria-label","待复制的文字");
  area.style.position = "fixed";
  area.style.top = "-1000px";
  document.body.append(area);
  area.select();
  let copied = false;
  try { copied = document.execCommand("copy"); } catch { copied = false; }
  area.remove();
  return copied;
}
document.querySelectorAll("[data-copy]").forEach(button => button.addEventListener("click",async () => {
  const text = document.querySelector(button.dataset.copy)?.textContent.trim();
  if (!text) return;
  const label = button.dataset.label || button.textContent;
  button.dataset.label = label;
  if (await copyText(text)) {
    button.textContent = "已复制";
    setTimeout(() => { button.textContent = label; },1800);
  } else {
    button.textContent = "自动复制失败，请手动复制";
    let area = button.nextElementSibling;
    if (!area?.classList.contains("manual-copy")) {
      area = document.createElement("textarea");
      area.className = "manual-copy";
      area.setAttribute("aria-label","请手动复制这段文字");
      button.after(area);
    }
    area.value = text;
    area.focus();
    area.select();
  }
}));
window.addEventListener("popstate",() => { readURL(); render(); });
readURL();
writeURL(true);
render();
