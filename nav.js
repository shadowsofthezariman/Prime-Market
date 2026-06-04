// ── PRIME MARKET · nav.js ────────────────────────────
// Shared hamburger menu logic for all pages

document.getElementById('hamburger').addEventListener('click', () => {
  document.getElementById('main-nav').classList.toggle('open');
});

document.querySelectorAll('#main-nav a').forEach(a => {
  a.addEventListener('click', () => {
    document.getElementById('main-nav').classList.remove('open');
  });
});
