const THEMES = [
{ value: 'light-mode', label: '☀️ Clair' },
{ value: 'dark-mode', label: '🌙 Sombre' },
];

const THEME_KEY = 'app-theme';

function applyTheme(theme, save = true) {
document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
    link.href = link.href.replace(/\/css\/[\w-]+\//, `/css/${theme}/`);
});
if (save) localStorage.setItem(THEME_KEY, theme);
}

function buildThemeSwitcher() {
const select = document.getElementById('theme-switcher');
if (!select) return;
THEMES.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.value;
    opt.textContent = t.label;
    select.appendChild(opt);
});
const saved = localStorage.getItem(THEME_KEY) || 'light-mode';
select.value = saved;
if (saved !== 'light-mode') applyTheme(saved, false);
select.addEventListener('change', () => applyTheme(select.value));
}

buildThemeSwitcher();