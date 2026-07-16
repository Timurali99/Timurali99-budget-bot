"use strict";

// T&T Studio catalog: a day/night switch flips both theme and content
// (товары ⇄ услуги). Static data; card photos come from a keyword image source
// with a unifying premium treatment and the original emoji as a fallback.

const MODES = {
  night: {
    tabTitle: "услуги",
    eyebrowKj: "道", tag: "РАЗРАБОТКА",
    title: "Технологии,<br>что работают<br>на бизнес",
    lead: "Telegram-боты, AI-ассистенты, автоматизация и веб-платформы под ключ.",
    order: "Заказать",
    items: [
      { t: "Telegram Bot + AI", m: "15 дней", p: 45000, from: true, kj: "術", e: "🤖", q: "robot,technology" },
      { t: "Mini App / каталог", m: "20 дней", p: 60000, from: true, kj: "網", e: "📱", q: "smartphone,app" },
      { t: "CRM · автоматизация", m: "18 дней", p: 55000, from: true, kj: "録", e: "⚙️", q: "dashboard,technology" },
      { t: "Сайт / платформа", m: "25 дней", p: 90000, from: true, kj: "道", e: "🌐", q: "website,code" },
      { t: "AI-ассистент под задачу", m: "12 дней", p: 35000, from: true, kj: "知", e: "🧠", q: "neural,network" },
      { t: "Интеграции / API", m: "10 дней", p: 30000, from: true, kj: "系", e: "🔗", q: "network,server" },
      { t: "Чат-бот поддержки", m: "14 дней", p: 40000, from: true, kj: "助", e: "💬", q: "chat,support" },
      { t: "Лендинг под запуск", m: "8 дней", p: 25000, from: true, kj: "昇", e: "🚀", q: "startup,launch" },
      { t: "Автоворонки продаж", m: "16 дней", p: 50000, from: true, kj: "財", e: "📈", q: "analytics,growth" },
    ],
  },
  day: {
    tabTitle: "товары",
    eyebrowKj: "匠", tag: "МАСТЕРСКАЯ",
    title: "Вещи с<br>историей и<br>характером",
    lead: "Ручная работа, кожа, техника и детали — то, что можно купить прямо сейчас.",
    order: "Купить",
    items: [
      { t: "Картхолдер Crazy Horse", m: "Кожа · Тиснение", p: 5000, kj: "財", e: "👜", q: "leather,wallet" },
      { t: "MacBook Air M2", m: "Б/У · Идеал", p: 78000, kj: "機", e: "💻", q: "macbook,laptop" },
      { t: "Тормозные колодки Bosch", m: "Новое · В наличии", p: 3200, kj: "車", e: "🚗", q: "car,brake" },
      { t: "Ремешок кожаный", m: "Ручная работа", p: 2400, kj: "時", e: "⌚", q: "watch,leather" },
      { t: "Кошелёк ручной работы", m: "Кожа · На заказ", p: 3500, kj: "鞄", e: "👛", q: "purse,leather" },
      { t: "iPhone 13 (б/у)", m: "Б/У · Идеал", p: 45000, kj: "電", e: "📱", q: "iphone,phone" },
      { t: "Наушники беспроводные", m: "Новое", p: 12000, kj: "音", e: "🎧", q: "headphones,audio" },
      { t: "Механическая клавиатура", m: "Custom", p: 9500, kj: "鍵", e: "⌨️", q: "keyboard,mechanical" },
      { t: "Рюкзак кожаный", m: "Ручная работа", p: 8000, kj: "包", e: "🎒", q: "leather,bag" },
    ],
  },
};

const el = (id) => document.getElementById(id);
const money = (n) => n.toLocaleString("ru-RU");
let cfg = { botUsername: "", channelUsername: "AITimPromptsLab", managerUsername: "Temurali_aliev" };
let cart = 0;

const tme = (h, payload) => {
  const u = (h || "").replace(/^@/, "");
  if (!u) return null;
  return payload ? `https://t.me/${u}?start=${payload}` : `https://t.me/${u}`;
};
const orderLink = () => tme(cfg.botUsername, "order") || tme(cfg.managerUsername) || "#";

async function loadConfig() {
  try {
    const r = await fetch("/config.json");
    if (r.ok) cfg = { ...cfg, ...(await r.json()) };
  } catch (_) { /* defaults */ }
  const ch = tme(cfg.channelUsername), mg = tme(cfg.managerUsername);
  if (ch) el("footChannel").href = ch;
  if (mg) el("footManager").href = mg;
}

// ---------- render ----------
function render(modeKey) {
  const M = MODES[modeKey];
  document.documentElement.setAttribute("data-mode", modeKey);
  el("halfGoods").setAttribute("aria-selected", String(modeKey === "day"));
  el("halfServices").setAttribute("aria-selected", String(modeKey === "night"));
  el("eyebrowKj").textContent = M.eyebrowKj;
  el("eyebrowTag").textContent = M.tag;
  el("stageTitle").innerHTML = M.title;
  el("stageLead").textContent = M.lead;

  el("cards").innerHTML = M.items.map((it) => {
    const price = it.from
      ? `<span class="from">от</span>${money(it.p)}<span class="rub">₽</span>`
      : `${money(it.p)}<span class="rub">₽</span>`;
    const img = `https://loremflickr.com/600/450/${it.q}`;
    return `<article class="card">
      <div class="card-media">
        <img src="${img}" alt="${escapeHtml(it.t)}" loading="lazy"
             onerror="this.closest('.card-media').classList.add('noimg');this.remove()">
        <span class="media-emoji">${it.e}</span>
        <span class="card-kj">${it.kj}</span>
      </div>
      <div class="card-info">
        <h3 class="card-title">${escapeHtml(it.t)}</h3>
        <p class="card-meta">${escapeHtml(it.m)}</p>
        <div class="price">${price}</div>
        <div class="card-actions">
          <button class="plus" aria-label="Добавить в корзину">+</button>
          <a class="order" href="${orderLink()}" target="_blank" rel="noopener">${M.order}</a>
        </div>
      </div>
    </article>`;
  }).join("");

  glyphColor = getComputedStyle(document.documentElement).getPropertyValue("--glyph").trim() || "255,47,61";
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ---------- cart ----------
function bumpCart() {
  cart += 1;
  const c = el("cartCount");
  c.textContent = String(cart);
  c.hidden = false;
}
document.addEventListener("click", (e) => {
  if (e.target.closest(".plus")) { e.preventDefault(); bumpCart(); }
  else if (e.target.closest(".order")) { bumpCart(); }
});
el("cartBtn").addEventListener("click", () => {
  const mg = tme(cfg.managerUsername);
  if (cart > 0 && mg) window.open(mg, "_blank", "noopener");
});

// ---------- switch ----------
el("halfGoods").addEventListener("click", () => render("day"));
el("halfServices").addEventListener("click", () => render("night"));

// ---------- moving hieroglyph background ----------
const POOL = "道令号変信起能言系術網録知財機車時電匠手品心価導礼義徳華宝助昇音鍵包".split("");
const cv = el("glyphfield"), ctx = cv.getContext("2d");
let glyphColor = "255,47,61";
let glyphs = [];
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

function sizeCanvas() {
  cv.width = innerWidth * devicePixelRatio;
  cv.height = innerHeight * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
}
function seedGlyphs() {
  const n = Math.max(14, Math.round(innerWidth / 70));
  glyphs = Array.from({ length: n }, () => ({
    ch: POOL[(Math.random() * POOL.length) | 0],
    x: Math.random() * innerWidth,
    y: Math.random() * innerHeight,
    size: 26 + Math.random() * 68,
    vx: (Math.random() - 0.5) * 0.25,
    vy: (Math.random() - 0.5) * 0.25,
    a: 0.04 + Math.random() * 0.08,
  }));
}
function drawGlyphs() {
  ctx.clearRect(0, 0, innerWidth, innerHeight);
  for (const g of glyphs) {
    g.x += g.vx; g.y += g.vy;
    const pad = g.size;
    if (g.x < -pad) g.x = innerWidth + pad; if (g.x > innerWidth + pad) g.x = -pad;
    if (g.y < -pad) g.y = innerHeight + pad; if (g.y > innerHeight + pad) g.y = -pad;
    ctx.font = `700 ${g.size}px "Noto Sans JP","Hiragino Sans",sans-serif`;
    ctx.fillStyle = `rgba(${glyphColor},${g.a})`;
    ctx.fillText(g.ch, g.x, g.y);
  }
  if (!reduce) requestAnimationFrame(drawGlyphs);
}
addEventListener("resize", () => { sizeCanvas(); seedGlyphs(); if (reduce) drawGlyphs(); });

// ---------- boot ----------
const startMode = (() => { const h = new Date().getHours(); return h >= 7 && h < 19 ? "day" : "night"; })();
loadConfig().then(() => render(startMode));
render(startMode);
sizeCanvas(); seedGlyphs(); drawGlyphs();
