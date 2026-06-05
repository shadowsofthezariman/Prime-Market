// ── PRIME MARKET · baro_app.js ──────────────────────
// Reads from prices_baro.json updated daily by GitHub Actions

async function loadPrices() {
  try {
    const res = await fetch('prices_baro.json?nocache=' + Date.now());
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

// Filename → image path helpers
// Mod name  → images/BaroMods/PrimedChamberMod.png
// Weapon name → images/BaroWeapons/GotvaPrime.png
// We derive the filename from the display name in the JSON
// by stripping spaces and using the same PascalCase the images use.
// Since we control the image filenames we just do: name → remove spaces + .png

function modImgPath(name) {
  // "Primed Chamber" → "PrimedChamberMod.png"
  const pascal = name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('');
  return `images/BaroMods/${pascal}Mod.png`;
}

function weaponImgPath(name) {
  // "Prisma Grakata" → "PrismaGrakata.png"
  const pascal = name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('');
  return `images/BaroWeapons/${pascal}.png`;
}

// ── CARD BUILDERS ─────────────────────────────────────

function makeModCard(item, index) {
  const imgSrc = modImgPath(item.name);
  const hasMaxed    = item.price_maxed    != null;
  const hasUnranked = item.price_unranked != null;

  const mainPrice = hasMaxed ? item.price_maxed : item.price_unranked;
  const mainLabel = hasMaxed ? 'maxed' : 'unranked';

  const subHtml = (hasMaxed && hasUnranked)
    ? `<div class="baro-card-subprice">${item.price_unranked} ◈ unranked</div>`
    : '';

  return `
    <div class="baro-card baro-card--mod" style="animation-delay:${index * 0.015}s">
      <img class="baro-card-img" src="${escapeHTML(imgSrc)}" alt="${escapeHTML(item.name)}"
           loading="lazy" onerror="this.style.opacity='0.15'" />
      <div class="baro-card-name">${escapeHTML(item.name)}</div>
      <div class="baro-card-price">${mainPrice} <span class="baro-plat-sym">◈</span></div>
      <div class="baro-card-rank-label">${mainLabel}</div>
      ${subHtml}
      <a class="baro-card-link"
         href="https://warframe.market/items/${escapeHTML(item.slug)}"
         target="_blank" rel="noopener">Market →</a>
    </div>`;
}

function makeWeaponCard(item, index) {
  const imgSrc = weaponImgPath(item.name);
  return `
    <div class="baro-card baro-card--weapon" style="animation-delay:${index * 0.025}s">
      <img class="baro-card-img" src="${escapeHTML(imgSrc)}" alt="${escapeHTML(item.name)}"
           loading="lazy" onerror="this.style.opacity='0.15'" />
      <div class="baro-card-name">${escapeHTML(item.name)}</div>
      <div class="baro-card-price">${item.avg_price} <span class="baro-plat-sym">◈</span></div>
      <div class="baro-card-rank-label">avg platinum</div>
      <a class="baro-card-link"
         href="https://warframe.market/items/${escapeHTML(item.slug)}"
         target="_blank" rel="noopener">Market →</a>
    </div>`;
}

function otherIcon(name) {
  if (name.toLowerCase().includes('relic'))  return '◈';
  if (name.toLowerCase().includes('signal')) return '⚡';
  return '✦';
}

function makeOtherCard(item, index) {
  const priceHtml = item.avg_price != null
    ? `<div class="baro-card-price">${item.avg_price} <span class="baro-plat-sym">◈</span></div>
       <div class="baro-card-rank-label">avg platinum</div>`
    : `<div class="baro-card-rank-label" style="margin-top:0.4rem">no listings</div>`;

  const linkHtml = item.slug
    ? `<a class="baro-card-link"
          href="https://warframe.market/items/${escapeHTML(item.slug)}"
          target="_blank" rel="noopener">Market →</a>`
    : '';

  return `
    <div class="baro-card baro-card--other" style="animation-delay:${index * 0.05}s">
      <span class="baro-card-icon">${otherIcon(item.name)}</span>
      <div class="baro-other-body">
        <div class="baro-card-name">${escapeHTML(item.name)}</div>
        ${priceHtml}
      </div>
      ${linkHtml}
    </div>`;
}

// ── RENDER ────────────────────────────────────────────

function renderGrid(id, html) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = html || `<div class="empty-state">No data yet.<br/>Run the GitHub Action to generate it.</div>`;
}

// ── INIT ──────────────────────────────────────────────

async function init() {
  const data = await loadPrices();

  if (!data) {
    ['mods-grid','weapons-grid','other-grid'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = `<div class="empty-state">prices_baro.json not found.<br/>Run the GitHub Action to generate it.</div>`;
    });
    document.getElementById('footer-year').textContent = new Date().getFullYear();
    return;
  }

  // Updated date
  if (data.updated) {
    const d = new Date(data.updated);
    document.getElementById('last-updated').textContent =
      d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  // Counts
  document.getElementById('mod-count').textContent    = data.mods?.length    ?? '—';
  document.getElementById('weapon-count').textContent = data.weapons?.length  ?? '—';
  document.getElementById('other-count').textContent  = data.other?.length    ?? '—';

  // Mods — already sorted highest first by fetch script
  renderGrid('mods-grid',
    (data.mods || []).map((item, i) => makeModCard(item, i)).join(''));

  // Weapons — already sorted highest first
  renderGrid('weapons-grid',
    (data.weapons || []).map((item, i) => makeWeaponCard(item, i)).join(''));

  // Other — relics + key with prices
  renderGrid('other-grid',
    (data.other || []).map((item, i) => makeOtherCard(item, i)).join(''));

  document.getElementById('footer-year').textContent = new Date().getFullYear();
}

init();
