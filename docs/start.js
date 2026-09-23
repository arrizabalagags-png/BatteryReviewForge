"use strict";
const order = ["client", "os", "install", "test"];
const clients = {codex:"Codex", kimi:"Kimi Code", workbuddy:"WorkBuddy", dsh:"DeepSeek Harness"};
const systems = {windows:"Windows", macos:"macOS", linux:"Linux"};
const state = {client:"", os:"", step:"client"};
const version = "0.8.0";
const mainZip = `downloads/BatteryReviewForge-v${version}.zip`;
const wbZip = `downloads/BatteryReviewForge-WorkBuddy-v${version}.zip`;
function readURL() {
  const query = new URLSearchParams(location.search);
  state.client = clients[query.get("client")] ? query.get("client") : "";
  state.os = systems[query.get("os")] ? query.get("os") : "";
  const requested = query.get("step");
  state.step = order.includes(requested) ? requested : "client";
  if (!state.client && order.indexOf(state.step) > 0) state.step = "client";
  if (!state.os && order.indexOf(state.step) > 1) state.step = "os";
}
function writeURL(replace=false) {
  const query = new URLSearchParams();
  if(state.client)query.set("client",state.client);
  if(state.os)query.set("os",state.os);
  query.set("step",state.step);
  const hash = state.step === "test" && location.hash === "#assembly" ? "#assembly" : "";
  history[replace ? "replaceState" : "pushState"]({...state},"",`${location.pathname}?${query}${hash}`);
}
function goToStep(step,replace=false) {
  if (!order.includes(step)) return;
  if (order.indexOf(step)>0 && !state.client) step="client";
  if (order.indexOf(step)>1 && !state.os) step="os";
  state.step=step;writeURL(replace);render();
}
function render() {
  document.querySelectorAll("[data-wizard-step]").forEach(panel=>{panel.hidden=panel.dataset.wizardStep!==state.step;});
  document.querySelectorAll("[data-progress-step]").forEach(button=>{
    const active=button.dataset.progressStep===state.step;
    button.classList.toggle("current",active);
    if(active)button.setAttribute("aria-current","step");else button.removeAttribute("aria-current");
  });
  document.querySelectorAll("[data-choice-client]").forEach(button=>button.classList.toggle("selected",button.dataset.choiceClient===state.client));
  document.querySelectorAll("[data-choice-os]").forEach(button=>button.classList.toggle("selected",button.dataset.choiceOs===state.os));
  document.querySelector("#current-client").textContent=clients[state.client]||"你的软件";
  document.querySelector("#current-os").textContent=systems[state.os]||"你的系统";
  const download=document.querySelector("#install-download");
  download.href=state.client==="workbuddy"?wbZip:mainZip;
  download.textContent=state.client==="workbuddy"?"下载 WorkBuddy 专用技能包":"下载完整安装包";
  const command=document.querySelector("#install-command");
  const instruction=document.querySelector("#install-instruction");
  const steps=document.querySelector("#install-steps");
  steps.replaceChildren();
  let lines=[];
  if(state.client==="workbuddy"){
    instruction.textContent="下载后按下面三步导入。";
    lines=["解压下载的合集 ZIP，打开里面 13 个单技能 ZIP 所在文件夹。","在 WorkBuddy 里打开“技能 → 添加技能 → 上传技能”。","上传其中一个单技能 ZIP。画实验图选 battery-review-figure；拼图选 battery-figure-assemble。"];
    command.textContent="无需输入命令。不要直接上传合集 ZIP。";
  }else{
    const agent=state.client==="kimi"?(state.os==="windows"?" -Agent KimiCode":" --agent kimi"):state.client==="dsh"?(state.os==="windows"?" -Agent DeepSeekHarness":" --agent dsh"):"";
    command.textContent=state.os==="windows"?`./install.ps1${agent}`:`sh install.sh${agent}`;
    instruction.textContent="下载 ZIP 后，照着三步做。";
    lines=state.os==="windows"?["右键下载的 ZIP，选“全部解压”。","打开解压后的文件夹，点顶部地址栏，输入 powershell 并按回车。","复制下面这行到打开的窗口，按回车；完成后新开一个 Agent 会话。"]:["双击 ZIP 解压，找到含 install.sh 的文件夹。","打开终端，输入 cd 和一个空格，再把解压后的文件夹拖进终端，按回车。","复制下面这行，按回车；完成后新开一个 Agent 会话。"];
  }
  for(const line of lines){const li=document.createElement("li");li.textContent=line;steps.append(li);}
  document.querySelector("#install-status").textContent=state.client==="codex"?"本机已验证":state.client==="kimi"?"技能目录已核对；完整任务待实机测试":"导入方法已核对；完整任务待实机测试";
  if(state.step==="test" && location.hash==="#assembly")requestAnimationFrame(()=>document.querySelector("#assembly")?.scrollIntoView({block:"start"}));
}
document.querySelectorAll("[data-choice-client]").forEach(button=>button.addEventListener("click",()=>{state.client=button.dataset.choiceClient;goToStep("os");}));
document.querySelectorAll("[data-choice-os]").forEach(button=>button.addEventListener("click",()=>{state.os=button.dataset.choiceOs;goToStep("install");}));
document.querySelectorAll("[data-progress-step]").forEach(button=>button.addEventListener("click",()=>{if(order.indexOf(button.dataset.progressStep)<order.indexOf(state.step))goToStep(button.dataset.progressStep);}));
document.querySelectorAll("[data-wizard-next]").forEach(button=>button.addEventListener("click",()=>goToStep(button.dataset.wizardNext)));
document.querySelectorAll("[data-wizard-back]").forEach(button=>button.addEventListener("click",()=>goToStep(order[order.indexOf(state.step)-1])));
document.querySelectorAll("[data-copy]").forEach(button=>button.addEventListener("click",async()=>{
  const target=document.querySelector(button.dataset.copy);
  await navigator.clipboard.writeText(target.textContent.trim());
  button.textContent="已复制";setTimeout(()=>button.textContent="复制",1800);
}));
window.addEventListener("popstate",()=>{readURL();render();});
readURL();writeURL(true);render();
