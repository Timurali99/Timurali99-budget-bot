"use strict";

// The Catalog API is reached only through this site's own /api/proxy/* (see
// server.py) — same origin, so no CORS, and a sleeping upstream degrades to an
// offline state instead of a broken page. Product/brand field names are
// normalized defensively because the upstream shape can vary.

const PROXY = "/api/proxy";
const PAGE = 12;

const el = (id) => document.getElementById(id);
const grid = el("grid");
const stateBox = el("stateBox");
const moreWrap = el("moreWrap");

let cfg = { botUsername: "", channelUsername: "zap_tut", managerUsername: "Temurali_aliev" };
let offset = 0;
let lastFilters = {};
let loadedItems = [];

// ---------- links / config ----------
const tme = (handle, payload) => {
  const h = (handle || "").replace(/^@/, "");
  if (!h) return null;
  return payload ? `https://t.me/${h}?start=${payload}` : `https://t.me/${h}`;
};

async function loadConfig() {
  try {
    const r = await fetch("/config.json");
    if (r.ok) cfg = { ...cfg, ...(await r.json()) };
  } catch (_) { /* defaults are fine */ }

  const botOrChannel = tme(cfg.botUsername, "catalog") || tme(cfg.channelUsername);
  const channel = tme(cfg.channelUsername);
  const manager = tme(cfg.managerUsername);

  setHref("botCta", botOrChannel);
  setHref("channelLink", channel);
  setHref("footChannel", channel);
  setHref("footManager", manager);
  setHref("footBot", tme(cfg.botUsername, "catalog") || manager);
}

function setHref(id, href) {
  const node = el(id);
  if (!node) return;
  if (href) { node.href = href; node.hidden = false; }
  else { node.hidden = true; }
}

// buy button target: prefer the order bot deep-link, fall back to messaging the manager
function orderLink(productId) {
  return tme(cfg.botUsername, `buy_${productId}`) || tme(cfg.managerUsername);
}

// ---------- theme ----------
function initTheme() {
  const saved = localStorage.getItem("theme");
  const initial = saved || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  applyTheme(initial);
  el("themeToggle").addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("theme", next);
  });
}
function applyTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  el("themeToggle").textContent = t === "dark" ? "🌙" : "☀️";
}

// ---------- catalog api ----------
async function api(path) {
  const r = await fetch(`${PROXY}/${path}`);
  if (!r.ok) throw new Error(`upstream ${r.status}`);
  return r.json();
}
const asList = (data) => Array.isArray(data) ? data : (data && (data.items || data.results || data.data)) || [];

function pName(x) { return x.title || x.name || x.label || "—"; }
function pId(x) { return x.id ?? x.uuid ?? x.pk; }

// ---------- filters (brand -> model -> generation) ----------
async function loadBrands() {
  const sel = el("brandSel");
  try {
    const brands = asList(await api("api/catalog/brands"));
    fillSelect(sel, brands, "Все марки");
    sel.disabled = brands.length === 0;
  } catch (_) {
    sel.innerHTML = '<option value="">Марки недоступны</option>';
  }
}
function fillSelect(sel, items, placeholder) {
  sel.innerHTML = `<option value="">${placeholder}</option>` +
    items.map((it) => `<option value="${pId(it)}">${escapeHtml(pName(it))}</option>`).join("");
  sel.disabled = false;
}

async function onBrand() {
  const id = el("brandSel").value;
  const model = el("modelSel"), gen = el("genSel");
  resetSelect(model, "Все модели"); resetSelect(gen, "Сначала модель"); gen.disabled = true;
  if (!id) { model.disabled = true; return; }
  try { fillSelect(model, asList(await api(`brands/${id}/models`)), "Все модели"); }
  catch (_) { model.disabled = true; }
}
async function onModel() {
  const id = el("modelSel").value;
  const gen = el("genSel");
  resetSelect(gen, "Все поколения");
  if (!id) { gen.disabled = true; return; }
  try { fillSelect(gen, asList(await api(`models/${id}/generations`)), "Все поколения"); }
  catch (_) { gen.disabled = true; }
}
function resetSelect(sel, placeholder) { sel.innerHTML = `<option value="">${placeholder}</option>`; }

// ---------- products ----------
function currentFilters() {
  const f = {};
  const model = el("modelSel").value;
  if (model) f.car_model_id = model;
  const q = el("searchInput").value.trim();
  if (q) f.q = q;
  return f;
}

async function runSearch(reset = true) {
  if (reset) { offset = 0; loadedItems = []; lastFilters = currentFilters(); }
  showSkeletons(reset);
  hideState();

  const params = new URLSearchParams({ limit: String(PAGE), offset: String(offset) });
  if (lastFilters.car_model_id) params.set("car_model_id", lastFilters.car_model_id);

  let items;
  try {
    items = asList(await api(`products?${params.toString()}`));
  } catch (_) {
    if (reset) showOffline();
    return;
  }

  // upstream has no text search param — filter the page client-side by name/article
  if (lastFilters.q) {
    const q = lastFilters.q.toLowerCase();
    items = items.filter((p) => `${pName(p)} ${p.article || ""}`.toLowerCase().includes(q));
  }

  loadedItems = reset ? items : loadedItems.concat(items);
  renderProducts(loadedItems);
  moreWrap.hidden = items.length < PAGE;
  offset += PAGE;

  if (!loadedItems.length) showEmpty();
  el("resultCount").textContent = loadedItems.length ? `${loadedItems.length}${items.length === PAGE ? "+" : ""} шт.` : "";
}

function renderProducts(items) {
  el("catalogTitle").textContent = lastFilters.q ? `Поиск: «${lastFilters.q}»` : "Каталог";
  grid.innerHTML = items.map(cardHtml).join("");
}

function cardHtml(p) {
  const id = pId(p);
  const available = Number(p.stock_available ?? p.available ?? p.stock ?? 0);
  const inStock = available > 0 || p.status === "ACTIVE" && p.stock_available == null;
  const price = p.price != null && p.price !== "" ? Number(p.price) : null;
  const cur = p.currency || "RUB";
  const badge = available > 0
    ? `<span class="badge">в наличии${available <= 5 ? ` · ${available} шт` : ""}</span>`
    : (p.stock_available != null ? `<span class="badge out">под заказ</span>` : "");
  return `<article class="card">
    <div class="card-photo">
      <img loading="lazy" src="${PROXY}/products/${id}/photo" alt="${escapeHtml(pName(p))}"
           onerror="this.remove();this.parentNode.insertAdjacentHTML('beforeend','<span class=&quot;ph&quot;>🔧</span>')">
      ${badge}
    </div>
    <div class="card-body">
      <div class="card-title">${escapeHtml(pName(p))}</div>
      ${p.article ? `<div class="card-meta">арт. ${escapeHtml(String(p.article))}</div>` : ""}
      <div class="card-spacer"></div>
      <div class="price">${price != null
        ? `<span class="now">${fmtMoney(price)}</span><span class="cur">${curSymbol(cur)}</span>`
        : `<span class="none">Цена по запросу</span>`}</div>
      <div class="card-actions">
        <a class="btn btn-primary" target="_blank" rel="noopener" href="${orderLink(id)}">Заказать</a>
        <a class="btn" target="_blank" rel="noopener" href="${tme(cfg.managerUsername)}">Написать</a>
      </div>
    </div>
  </article>`;
}

// ---------- states ----------
function showSkeletons(reset) {
  if (!reset) return;
  el("resultCount").textContent = "";
  grid.innerHTML = Array.from({ length: 8 }).map(() =>
    `<article class="card skeleton"><div class="card-photo"></div>
     <div class="card-body"><div class="sk-line w60"></div><div class="sk-line w40"></div>
     <div class="card-spacer"></div><div class="sk-line w40"></div></div></article>`).join("");
}
function hideState() { stateBox.hidden = true; }
function showState(emoji, title, sub, actions) {
  grid.innerHTML = ""; moreWrap.hidden = true;
  el("stateEmoji").textContent = emoji;
  el("stateTitle").textContent = title;
  el("stateSub").textContent = sub;
  el("stateActions").innerHTML = actions;
  stateBox.hidden = false;
}
function showOffline() {
  showState("🛠️", "Каталог сейчас обновляется",
    "Витрина временно не отвечает. Напишите нам в Telegram — подберём деталь вручную и ответим по наличию.",
    `<a class="btn btn-primary" target="_blank" rel="noopener" href="${tme(cfg.managerUsername)}">Написать менеджеру</a>
     <a class="btn" target="_blank" rel="noopener" href="${tme(cfg.channelUsername)}">Открыть канал</a>`);
}
function showEmpty() {
  showState("🔍", "Ничего не нашли",
    "По этому запросу товаров нет. Попробуйте другую марку/модель или напишите нам — найдём под заказ.",
    `<a class="btn btn-primary" target="_blank" rel="noopener" href="${tme(cfg.managerUsername)}">Спросить менеджера</a>`);
}

// ---------- utils ----------
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function fmtMoney(n) { return n.toLocaleString("ru-RU", { maximumFractionDigits: 0 }); }
function curSymbol(c) { return ({ RUB: "₽", USD: "$", EUR: "€", KZT: "₸" }[c]) || c; }

// ---------- boot ----------
initTheme();
loadConfig();
loadBrands();
runSearch(true);

el("brandSel").addEventListener("change", onBrand);
el("modelSel").addEventListener("change", onModel);
el("finder").addEventListener("submit", (e) => { e.preventDefault(); runSearch(true); });
el("moreBtn").addEventListener("click", () => runSearch(false));
