/**
 * ── <theme-switcher> Web Component ──
 * Composant autonome et premium pour la gestion et le basculement des thèmes.
 * Intègre nativement la logique JavaScript et le style Dark Luxury (Or & Sombre).
 */

class ThemeSwitcherComponent extends HTMLElement {
    constructor() {
        super();
        this.THEMES = [
            { value: 'light-mode', label: '☀️ Clair' },
            { value: 'dark-mode', label: '🌙 Sombre' }
        ];
        this.THEME_KEY = 'app-theme';
    }

    connectedCallback() {
        // Rendu de la structure HTML interne
        this.innerHTML = `
            <div class="theme-switcher">
                <span class="theme-switcher__icon">🎨</span>
                <select id="theme-switcher-select" class="theme-switcher__select"></select>
            </div>
        `;

        this.selectEl = this.querySelector('#theme-switcher-select');
        
        if (this.selectEl) {
            this.buildOptions();
            this.initTheme();
        }
    }

    buildOptions() {
        this.THEMES.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.value;
            opt.textContent = t.label;
            this.selectEl.appendChild(opt);
        });
    }

    initTheme() {
        const savedTheme = localStorage.getItem(this.THEME_KEY) || 'light-mode';
        this.selectEl.value = savedTheme;
        
        // Appliquer le thème initialement sans écraser si déjà configuré
        if (savedTheme !== 'light-mode') {
            this.applyTheme(savedTheme, false);
        }

        // Écouter les changements utilisateur
        this.selectEl.addEventListener('change', () => {
            this.applyTheme(this.selectEl.value);
        });
    }

    applyTheme(theme, save = true) {
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            // Remplace dynamiquement le dossier du thème dans le chemin CSS (ex: /css/light-mode/ -> /css/dark-mode/)
            link.href = link.href.replace(/\/css\/[\w-]+\//, `/css/${theme}/`);
        });
        
        if (save) {
            localStorage.setItem(this.THEME_KEY, theme);
        }

        // Déclencher un événement global si d'autres composants ont besoin d'écouter le changement
        this.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme },
            bubbles: true
        }));
    }
}

// Enregistrement du Web Component personnalisé
if (!customElements.get('theme-switcher')) {
    customElements.define('theme-switcher', ThemeSwitcherComponent);
}
