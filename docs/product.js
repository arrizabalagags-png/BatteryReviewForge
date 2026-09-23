"use strict";
const menu = document.querySelector(".menu-toggle");
menu?.addEventListener("click", () => {
  const links = document.querySelector(".navlinks");
  const open = links.classList.toggle("open");
  menu.setAttribute("aria-expanded", String(open));
});

const searchPanel = document.querySelector(".search-panel");
const searchInput = document.querySelector("#site-search-input");
const searchResults = document.querySelector("#search-results");
let searchIndex = [];
const groups = ["开始做", "样图", "学习", "功能", "社区", "开发者"];
const synonyms = [
  ["库伦效率", "库仑效率", "coulombic efficiency", "ce"],
  ["阻抗", "eis", "nyquist"],
  ["对称电池", "li||li", "symmetric cell"],
  ["拼图", "拼版", "panel assembly", "figure"],
  ["全电池", "full cell", "cycling"],
];
function expandTerm(term) {
  const lower = term.trim().toLowerCase();
  const found = synonyms.find(row => row.some(word => word.toLowerCase() === lower));
  return found || [lower];
}
function renderSearch() {
  const term = searchInput.value.trim().toLowerCase();
  searchResults.replaceChildren();
  if (!term) return;
  const needles = expandTerm(term).map(s => s.toLowerCase());
  const matches = searchIndex.filter(item => {
    const hay = (item.title + " " + item.keywords + " " + item.description).toLowerCase();
    return needles.some(n => /^[a-z0-9]{1,3}$/.test(n) ? new RegExp(`\\b${n}\\b`).test(hay) : hay.includes(n));
  });
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
  if (!matches.length) searchResults.textContent = "没有找到。试试“CE”、“拼图”或“安装”。";
}
document.querySelectorAll("[data-open-search]").forEach(button => button.addEventListener("click", async () => {
  searchPanel.classList.add("open");
  searchInput.focus();
  if (!searchIndex.length) {
    const response = await fetch("search-index.json");
    if (response.ok) searchIndex = await response.json();
  }
  renderSearch();
}));
document.querySelector(".search-close")?.addEventListener("click", () => searchPanel.classList.remove("open"));
searchPanel?.addEventListener("click", event => { if (event.target === searchPanel) searchPanel.classList.remove("open"); });
searchInput?.addEventListener("input", renderSearch);
document.addEventListener("keydown", event => {
  if (event.key === "Escape") searchPanel?.classList.remove("open");
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault(); document.querySelector("[data-open-search]")?.click();
  }
});

const contributors = document.querySelector("#contributor-list");
if (contributors) fetch("contributors.json").then(response => response.json()).then(data => {
  const labels = {maintainers:"维护者", contributors:"贡献者", scientific_reviewers:"科学审核", documentation_translation:"文档与翻译"};
  for (const [key,label] of Object.entries(labels)) {
    const heading = document.createElement("h3"); heading.textContent = label; contributors.append(heading);
    const list = document.createElement("div"); list.className = "contributor-list";
    if (!data[key].length) { const note=document.createElement("p");note.className="small";note.textContent="欢迎第一位参与者。";list.append(note); }
    data[key].forEach(person => { const item=document.createElement("div");item.className="contributor";const name=document.createElement("strong");name.textContent=person.name;const role=document.createElement("small");role.textContent=person.role;item.append(name,role);list.append(item); });
    contributors.append(list);
  }
}).catch(() => {contributors.textContent="贡献者列表暂时无法加载；请查看仓库 CONTRIBUTORS.yaml。";});
