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
const groups = ["开始做","样图","学习","功能","社区","开发者"];
const synonyms = [
  ["库伦效率","库仑效率","coulombic efficiency","ce"],
  ["阻抗","eis","nyquist"],
  ["对称电池","li||li","symmetric cell"],
  ["拼图","拼版","panel assembly"],
  ["全电池","full cell","cycling"],
  ["热图","软包温度","thermal","pouch"],
  ["文献散点","基准比较","benchmark","literature scatter"],
  ["倍率","rate capability","rate"],
  ["充放电","gcd","voltage profile"],
  ["报告矩阵","reporting matrix","matrix"]
];
let searchIndex = null;
let searchLoad = null;
let searchError = false;
let opener = null;

function expandTerm(term) {
  const lower = term.trim().toLowerCase();
  const found = synonyms.find(row => row.some(word => word.toLowerCase() === lower));
  return found || [lower];
}
function matchesTerm(item,needles) {
  const hay = (item.title + " " + item.keywords + " " + item.description).toLowerCase();
  return needles.some(term => /^[a-z0-9]{1,3}$/.test(term) ?
    new RegExp("\\b" + term + "\\b").test(hay) : hay.includes(term));
}
function renderSearch() {
  const term = searchInput.value.trim().toLowerCase();
  searchResults.replaceChildren();
  if (!searchIndex) return;
  if (!term) { searchStatus.textContent = "输入一个词，看看下一步能做什么。"; return; }
  searchStatus.textContent = "";
  const needles = expandTerm(term).map(word => word.toLowerCase());
  const matches = searchIndex.filter(item => matchesTerm(item,needles));
  for (const group of groups) {
    const rows = matches.filter(item => item.group === group);
    if (!rows.length) continue;
    const section = document.createElement("section");
    section.className = "search-group";
    const heading = document.createElement("h3");
    heading.textContent = group;
    section.append(heading);
    rows.forEach(item => {
      const link = document.createElement("a");
      link.href = item.url;
      link.textContent = item.title;
      section.append(link);
    });
    searchResults.append(section);
  }
  if (!matches.length) searchStatus.textContent = "没有找到。试试“CE”、“拼图”或“安装”。";
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
  if (event.target.closest(".search-group a")) closeSearch();
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
