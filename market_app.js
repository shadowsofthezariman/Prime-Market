// ── PRIME MARKET · app.js ────────────────────────────
// Reads from prices.json which is updated daily by GitHub Actions

async function loadPrices() {
  try {
    const res = await fetch('prices.json?nocache=' + Date.now());
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

function renderGrid(gridId, items, isDeal) {
  const grid = document.getElementById(gridId);
  if (!items || !items.length) {
    grid.innerHTML = `<div class="empty-state">No price data available yet.<br/>Check back after the first GitHub Action runs.</div>`;
    return;
  }

  grid.innerHTML = items.map((item, i) => `
    <a class="price-card ${isDeal ? 'deal' : ''}"
       data-rank="${i + 1}"
       href="https://warframe.market/items/${item.slug}_prime_set"
       target="_blank" rel="noopener"
       style="animation-delay: ${i * 0.05}s">
      <div class="price-rank">#${i + 1}</div>
      <div class="price-name">${escapeHTML(item.name)} Prime</div>
      <div class="price-plat">${item.avg_price}</div>
      <div class="price-plat-label">◈ avg platinum</div>
      <div class="price-link">View on Warframe.Market →</div>
    </a>
  `).join('');
}

async function init() {
  const data = await loadPrices();

  if (data && data.updated) {
    const d = new Date(data.updated);
    document.getElementById('last-updated').textContent =
      d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  if (data) {
    renderGrid('expensive-grid', data.expensive, false);
    renderGrid('cheapest-grid',  data.cheapest,  true);
  } else {
    document.getElementById('expensive-grid').innerHTML =
      `<div class="empty-state">prices.json not found.<br/>Run the GitHub Action to generate it.</div>`;
    document.getElementById('cheapest-grid').innerHTML =
      `<div class="empty-state">prices.json not found.<br/>Run the GitHub Action to generate it.</div>`;
  }

  document.getElementById('footer-year').textContent = new Date().getFullYear();
}

init();
