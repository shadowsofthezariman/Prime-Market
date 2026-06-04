// ── PRIME MARKET · weapons_app.js ───────────────────
// Reads from prices_weapons.json updated daily by GitHub Actions

async function loadPrices() {
  try {
    const res = await fetch('prices_weapons.json?nocache=' + Date.now());
    if (!res.ok) throw new Error('Not found');
    return await res.json();
  } catch {
    return null;
  }
}

function escapeHTML(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Images live in images/Weapons/ named like "Braton Prime.png"
function weaponImg(name) {
  return `images/Weapons/${name} Prime.png`;
}

function makeCard(item, rank, isDeal) {
  const imgSrc = weaponImg(item.name);
  // Gotva and any other custom-url items link directly without _prime_set
  const url = item.custom_url
    ? `https://warframe.market/items/${item.custom_url}`
    : `https://warframe.market/items/${item.slug}_prime_set`;

  return `
    <a class="price-card ${isDeal ? 'deal' : ''}"
       data-rank="${rank}"
       href="${escapeHTML(url)}"
       target="_blank" rel="noopener"
       style="animation-delay: ${(rank - 1) * 0.04}s">
      <div class="price-rank">#${rank}</div>
      <img class="card-warframe-img" src="${escapeHTML(imgSrc)}" alt="${escapeHTML(item.name)} Prime" loading="lazy" />
      <div class="price-name">${escapeHTML(item.name.includes('Prime') ? item.name : item.name + ' Prime')}</div>
      <div class="price-plat">${item.avg_price}</div>
      <div class="price-plat-label">◈ avg platinum</div>
      <div class="price-link">View on Warframe.Market →</div>
    </a>`;
}

function renderGrid(gridId, items, isDeal = false) {
  const grid = document.getElementById(gridId);
  if (!grid) return;
  if (!items || !items.length) {
    grid.innerHTML = `<div class="empty-state">No price data yet.<br/>Run the GitHub Action to generate it.</div>`;
    return;
  }
  grid.innerHTML = items.map((item, i) => makeCard(item, i + 1, isDeal)).join('');
}

// Small categories (archgun/companion/archwing) — all items sorted expensive→cheap
function renderSmallGrid(gridId, items) {
  const grid = document.getElementById(gridId);
  if (!grid) return;
  if (!items || !items.length) {
    grid.innerHTML = `<div class="empty-state">No price data yet.</div>`;
    return;
  }
  const sorted = [...items].sort((a, b) => b.avg_price - a.avg_price);
  grid.innerHTML = sorted.map((item, i) => makeCard(item, i + 1, false)).join('');
}

function showError(msg) {
  ['primary-expensive','primary-cheapest',
   'secondary-expensive','secondary-cheapest',
   'melee-expensive','melee-cheapest',
   'archgun-grid','companion-grid','archwing-grid']
  .forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = `<div class="empty-state">${msg}</div>`;
  });
}

async function init() {
  const data = await loadPrices();

  if (!data) {
    showError('prices_weapons.json not found.<br/>Run the GitHub Action to generate it.');
    document.getElementById('footer-year').textContent = new Date().getFullYear();
    return;
  }

  if (data.updated) {
    const d = new Date(data.updated);
    document.getElementById('last-updated').textContent =
      d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  renderGrid('primary-expensive',   data.primary?.expensive,   false);
  renderGrid('primary-cheapest',    data.primary?.cheapest,    true);
  renderGrid('secondary-expensive', data.secondary?.expensive, false);
  renderGrid('secondary-cheapest',  data.secondary?.cheapest,  true);
  renderGrid('melee-expensive',     data.melee?.expensive,     false);
  renderGrid('melee-cheapest',      data.melee?.cheapest,      true);

  renderSmallGrid('archgun-grid',   data.archgun?.all);
  renderSmallGrid('companion-grid', data.companion?.all);
  renderSmallGrid('archwing-grid',  data.archwing?.all);

  document.getElementById('footer-year').textContent = new Date().getFullYear();
}

init();
