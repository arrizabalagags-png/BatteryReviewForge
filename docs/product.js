"use strict";

const menu = document.querySelector(".menu-toggle");
const navlinks = document.querySelector(".navlinks");
function closeMenu() {
  navlinks?.classList.remove("open");
  menu?.setAttribute("aria-expanded","false");
}
menu?.addEventListener("click",() => {
  const open = navlinks.classList.toggle("open");
  menu.setAttribute("aria-expanded",String(open));
});
navlinks?.querySelectorAll("a").forEach(link => link.addEventListener("click",closeMenu));
document.addEventListener("click",event => {
  if (!navlinks?.classList.contains("open")) return;
  if (!navlinks.contains(event.target) && !menu.contains(event.target)) closeMenu();
});

const searchPanel = document.querySelector(".search-panel");
const searchInput = document.querySelector("#site-search-input");
const searchResults = document.querySelector("#search-results");
const searchStatus = document.querySelector("#search-status");
const pageRegions = [...document.querySelectorAll("header, main, footer")];
const groups = ["开始做","了解","样图","学习","功能","社区","开发者"];
const concepts = {
  data:["excel","xlsx","csv","表格","数据","画图","怎么画"],
  assembly:["拼图","拼版","排版","组合图","figure","六张图","十张图","怎么拼"],
  value:["为什么","有啥用","有什么用","值得","origin","originpro","省时间"],
  cost:["多少钱","价格","贵不贵","费用","额度","token","模型","省钱"],
  install:["不会","小白","看不懂","怎么装","安装","打不开","没反应"],
  ce:["库伦效率","库仑效率","coulombic efficiency","ce","aurbach"],
  eis:["阻抗","eis","nyquist"],
  symmetric:["对称电池","li||li","symmetric cell"],
  thermal:["热图","软包温度","thermal","pouch"],
  rate:["倍率","rate capability"],
  xrd:["xrd","衍射"],
  sims:["tof-sims","tofsims","深度分布"]
};
const intentDestinations = {
  data:"start.html?task=full", assembly:"start.html?task=assembly", value:"why.html",
  cost:"models.html", install:"learn.html#install", ce:"start.html?task=ce",
  eis:"gallery.html#eis", symmetric:"gallery.html#li_li", thermal:"gallery.html#pouch_thermal",
  rate:"gallery.html#rate_capability", xrd:"gallery.html#operando_xrd", sims:"gallery.html#tof_sims"
};
const popular = [
  ["我有 Excel","start.html?task=full"],["我要拼 Figure","start.html?task=assembly"],
  ["为什么用它","why.html"],["模型和费用","models.html"],["我不会安装","learn.html#install"]
];
let searchIndex = null;
let searchLoad = null;
let searchError = false;
let opener = null;
let activeResult = -1;

function normalized(value) {
  return value.toLowerCase().normalize("NFKC").replace(/[，。？！?！、,.;；：:]/g," ").replace(/\s+/g," ").trim();
}
function containsForm(haystack, form) {
  const word = normalized(form);
  if (/^[a-z0-9]{1,3}$/.test(word)) return new RegExp("(^|[^a-z0-9])" + word + "($|[^a-z0-9])").test(haystack);
  return haystack.includes(word);
}
function queryParts(query) {
  const clean = normalized(query).replace(/我的|我想|怎么|如何|可以|能不能|有一个|一份|一些|请问|帮我|一下|吗/g," ").trim();
  const words = clean.match(/[a-z0-9|+-]+|[\u3400-\u9fff]{2,}/g) || [];
  const found = Object.entries(concepts).filter(([,forms]) => forms.some(form => containsForm(normalized(query), form)));
  return {words, concepts:found.map(([name]) => name), query:normalized(query)};
}
function scoreItem(item, parts) {
  const title = normalized(item.title), keywords = normalized(item.keywords), description = normalized(item.description);
  let score = 0;
  for (const concept of parts.concepts) {
    const matchedForms = concepts[concept].filter(form => containsForm(parts.query, form));
    if (item.url === intentDestinations[concept]) score += 30;
    if (matchedForms.some(form => title.includes(normalized(form)))) score += 8;
    else if (matchedForms.some(form => keywords.includes(normalized(form)))) score += 4;
  }
  for (const word of parts.words) {
    if (word.length < 2) continue;
    if (title.includes(word)) score += 7;
    else if (keywords.includes(word)) score += 3;
    else if (description.includes(word)) score += 1;
  }
  if (score > 0 && item.group === "开始做") score += 2;
  return score;
}
function resultLink(item) {
  const link = document.createElement("a");
  link.href = item.url;
  link.className = "search-result";
  const title = document.createElement("strong"); title.textContent = item.title;
  const description = document.createElement("span"); description.textContent = item.description || "看看下一步怎么做。";
  const action = document.createElement("em"); action.textContent = (item.cta || "打开") + " →";
  link.append(title,description,action);
  return link;
}
function renderSearch() {
  const term = normalized(searchInput.value);
  searchResults.replaceChildren();
  activeResult = -1;
  if (!searchIndex) return;
  if (!term) {
    searchStatus.textContent = "常用入口";
    const section = document.createElement("section"); section.className = "search-group";
    popular.forEach(([title,url]) => section.append(resultLink({title,url,description:"点开看看，从这里继续。",cta:"开始"})));
    searchResults.append(section);
    return;
  }
  searchStatus.textContent = "";
  const parts = queryParts(term);
  const matches = searchIndex.map(item => ({item,score:scoreItem(item,parts)}))
    .filter(row => row.score > 0).sort((a,b) => b.score-a.score || groups.indexOf(a.item.group)-groups.indexOf(b.item.group)).slice(0,8);
  if (!matches.length) { searchStatus.textContent = "没找到合适的入口。试试“Excel 怎么画”“六张图怎么拼”或“安装”。"; return; }
  const section = document.createElement("section"); section.className = "search-group";
  matches.forEach(({item},index) => {
    const link = resultLink(item);
    if (index === 0) link.classList.add("best-result");
    section.append(link);
  });
  searchResults.append(section);
}
async function loadSearchIndex() {
  if (searchIndex) { renderSearch(); return; }
  if (searchLoad) return searchLoad;
  searchError = false;
  searchStatus.textContent = "正在加载搜索内容…";
  searchLoad = (async () => {
    try {
      const response = await fetch("search-index.json");
      if (!response.ok) throw new Error("Index unavailable");
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error("Invalid index");
      searchIndex = data;
      renderSearch();
    } catch {
      searchError = true;
      searchStatus.replaceChildren();
      const text = document.createElement("span");
      text.textContent = "搜索内容加载失败，请重试。";
      const retry = document.createElement("button");
      retry.type = "button";
      retry.className = "ghost";
      retry.textContent = "重试";
      retry.addEventListener("click",loadSearchIndex);
      searchStatus.append(text," ",retry);
    } finally { searchLoad = null; }
  })();
  return searchLoad;
}
function openSearch(source) {
  if (searchPanel.classList.contains("open")) return;
  closeMenu();
  opener = source || document.activeElement;
  searchPanel.classList.add("open");
  document.body.classList.add("modal-open");
  pageRegions.forEach(region => { region.inert = true; });
  searchInput.focus();
  loadSearchIndex();
}
function closeSearch() {
  if (!searchPanel.classList.contains("open")) return;
  searchPanel.classList.remove("open");
  document.body.classList.remove("modal-open");
  pageRegions.forEach(region => { region.inert = false; });
  if (opener?.isConnected) opener.focus();
}
document.querySelectorAll("[data-open-search]").forEach(button => button.addEventListener("click",() => openSearch(button)));
document.querySelector(".search-close")?.addEventListener("click",closeSearch);
searchPanel?.addEventListener("click",event => {
  if (event.target === searchPanel) closeSearch();
  if (event.target.closest(".search-result")) closeSearch();
});
searchInput?.addEventListener("input",() => {
  if (!searchIndex && !searchError) return;
  if (!searchIndex && searchError) return;
  renderSearch();
});
document.addEventListener("keydown",event => {
  if (event.key === "Escape") { closeSearch(); closeMenu(); return; }
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    openSearch(document.querySelector("[data-open-search]"));
  }
  if (searchPanel?.classList.contains("open") && ["ArrowDown","ArrowUp","Enter"].includes(event.key)) {
    const links = [...searchResults.querySelectorAll(".search-result")];
    if (event.key === "Enter" && document.activeElement === searchInput && links.length) {
      event.preventDefault(); (links[Math.max(activeResult,0)]).click(); return;
    }
    if (["ArrowDown","ArrowUp"].includes(event.key) && links.length) {
      event.preventDefault();
      activeResult = event.key === "ArrowDown" ? (activeResult+1) % links.length : (activeResult-1+links.length) % links.length;
      links[activeResult].focus(); return;
    }
  }
  if (event.key !== "Tab" || !searchPanel?.classList.contains("open")) return;
  const focusable = [...searchPanel.querySelectorAll('a[href], button:not([disabled]), input:not([disabled])')]
    .filter(element => element.getClientRects().length > 0);
  if (!focusable.length) { event.preventDefault(); return; }
  const first = focusable[0], last = focusable[focusable.length-1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});

const contributors = document.querySelector("#contributor-list");
if (contributors) fetch("contributors.json").then(response => {
  if (!response.ok) throw new Error("Contributors unavailable");
  return response.json();
}).then(data => {
  const labels = {maintainers:"维护者", contributors:"贡献者", scientific_reviewers:"科学审核", documentation_translation:"文档与翻译"};
  for (const [key,label] of Object.entries(labels)) {
    const heading = document.createElement("h3");
    heading.textContent = label;
    contributors.append(heading);
    const list = document.createElement("div");
    list.className = "contributor-list";
    if (!data[key]?.length) {
      const note = document.createElement("p");
      note.className = "small";
      note.textContent = "欢迎第一位参与者。";
      list.append(note);
    }
    (data[key] || []).forEach(person => {
      const item = document.createElement("div");
      item.className = "contributor";
      const name = document.createElement("strong");
      name.textContent = person.name;
      const role = document.createElement("small");
      role.textContent = person.role;
      item.append(name,role);
      list.append(item);
    });
    contributors.append(list);
  }
}).catch(() => { contributors.textContent = "贡献者列表暂时无法加载；请查看仓库 CONTRIBUTORS.yaml。"; });
