"use strict";

const billingButtons = [...document.querySelectorAll("[data-billing]")];
const workloadButtons = [...document.querySelectorAll("[data-workload]")];
const subscriptionAnswer = document.querySelector("#subscription-answer");
const apiAnswer = document.querySelector("#api-answer");
const costResults = document.querySelector("#cost-results");
const workloadNote = document.querySelector("#workload-note");
const priceDate = document.querySelector("#price-date");
let priceData;

function setPressed(buttons, selected) {
  for (const button of buttons) button.setAttribute("aria-pressed", String(button === selected));
}

function showBilling(button) {
  setPressed(billingButtons, button);
  const api = button.dataset.billing === "api";
  subscriptionAnswer.hidden = api;
  apiAnswer.hidden = !api;
  if (api && !priceData) loadPrices();
}

async function loadPrices() {
  costResults.textContent = "正在读取官方单价记录…";
  try {
    const response = await fetch("model-costs.json");
    if (!response.ok) throw new Error("price file unavailable");
    priceData = await response.json();
    showWorkload(workloadButtons.find(button => button.getAttribute("aria-pressed") === "true") || workloadButtons[0]);
  } catch {
    costResults.textContent = "价格记录暂时无法读取。请直接查看各模型官方价格页。";
  }
}

function showWorkload(button) {
  setPressed(workloadButtons, button);
  if (!priceData) return;
  const job = priceData.workloads[button.dataset.workload];
  workloadNote.textContent = `估算假设：输入 ${job.input_tokens.toLocaleString("zh-CN")} token，输出 ${job.output_tokens.toLocaleString("zh-CN")} token。`;
  costResults.replaceChildren();
  for (const model of priceData.models) {
    const amount = job.input_tokens * model.input_per_million / 1e6 + job.output_tokens * model.output_per_million / 1e6;
    const row = document.createElement("div");
    row.className = "cost-row";
    const name = document.createElement("span");
    name.textContent = model.label;
    const value = document.createElement("strong");
    value.textContent = `约 ${model.symbol}${amount < 0.1 ? amount.toFixed(3) : amount.toFixed(2)}`;
    const source = document.createElement("a");
    source.href = model.source;
    source.target = "_blank";
    source.rel = "noopener noreferrer";
    source.textContent = "官方单价 ↗";
    row.append(name, value, source);
    costResults.append(row);
  }
  priceDate.textContent = `单价核对日期：${priceData.checked_on}。实际计费以供应商当时价格为准。`;
}

for (const button of billingButtons) button.addEventListener("click", () => showBilling(button));
for (const button of workloadButtons) button.addEventListener("click", () => showWorkload(button));
