/**
 * <game-card> — Web Component
 * ─────────────────────────────────────────────────────────────────────────────
 * Encapsule le rendu visuel d'une carte de jeu. Hérite des variables CSS du
 * parent (pas de Shadow DOM) pour rester cohérent avec le design system.
 *
 * ATTRIBUTS
 * ─────────
 *  card-id    {string}   Identifiant de la carte
 *  name       {string}   Nom affiché dans le footer
 *  type       {string}   Classe Python (ex: "JobCard") → badge en overlay
 *  image      {string}   Chemin relatif à /static/
 *  smiles     {number}   Nombre de smiles
 *  value      {number}   Valeur monétaire (affiché si > 0)
 *  context    {string}   "hand" | "played" | "discard" | "other"
 *  face-down  {boolean}  Présence seule suffit → carte dos visible
 *  size       {string}   "sm" | "md" | "lg" | "salary"  (défaut : "md")
 *  clickable  {boolean}  Hover + curseur pointer
 *  selectable {boolean}  Affiche l'encoche de sélection
 *  selected   {boolean}  État sélectionné
 *
 * TAILLES
 * ───────
 *  sm     → 26×36px    mini main adversaire
 *  md     → 72×100px   main joueur (défaut)
 *  lg     → 68×96px    plateau
 *  salary → 110×154px  overlay salary-selector
 *
 * ÉVÉNEMENTS ÉMIS
 * ───────────────
 *  card-click → CustomEvent bubbles+composed
 *               detail: { cardId, name, type, smiles, value, image, context, raw }
 *
 * USAGE JS
 * ────────
 *  const el = GameCard.create(card, { context: 'played', size: 'md', clickable: true });
 *  container.appendChild(el);
 */

const STYLE_ID = "game-card-styles";

function injectStyles() {
  if (document.getElementById(STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    /* ── Hôte ── */
    game-card {
      display: inline-block;
      flex-shrink: 0;
      position: relative;
      cursor: default;
    }

    /* ── Racine interne ── */
    game-card .gc-root {
      position: relative;
      overflow: hidden;
      border-radius: 6px;
      border: 1.5px solid var(--line, #e0d9d0);
      background: var(--surface, #ffffff);
      transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s, background 0.18s;
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100%;
    }

    /* ── Tailles ── */
    game-card[size="sm"]     { width: 26px;  height: 36px;  }
    game-card[size="md"],
    game-card:not([size])    { width: 72px;  height: 100px; }
    game-card[size="lg"]     { width: 68px;  height: 96px;  }
    game-card[size="salary"] { width: 110px; height: 154px; }

    /* ── Image ── */
    game-card .gc-image {
      width: 100%;
      height: 68%;
      object-fit: cover;
      display: block;
      background: linear-gradient(135deg, var(--gold-light, #d4b98a), var(--gold, #b89a6a));
      flex-shrink: 0;
    }
    game-card[size="sm"] .gc-image { display: none; }

    /* ── Badge type ── */
    game-card .gc-type {
      position: absolute;
      top: 4px; left: 4px;
      font-size: 0.58rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 2px 5px;
      border-radius: 3px;
      background: rgba(26,23,20,0.72);
      color: var(--bg, #f5f2ee);
      backdrop-filter: blur(4px);
      line-height: 1.3;
      pointer-events: none;
    }
    game-card[size="sm"] .gc-type { display: none; }

    /* ── Footer ── */
    game-card .gc-footer {
      padding: 4px 6px;
      height: 32%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 4px;
      flex-shrink: 0;
    }
    game-card[size="sm"] .gc-footer { display: none; }

    game-card[size="salary"] .gc-footer {
      padding: 6px 8px;
      flex-direction: column;
      align-items: flex-start;
      gap: 2px;
      height: auto;
    }

    game-card .gc-name {
      font-size: 0.62rem;
      font-weight: 500;
      color: var(--accent, #3b3028);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
      font-family: 'Outfit', sans-serif;
    }
    game-card[size="salary"] .gc-name {
      font-size: 0.72rem;
      white-space: normal;
      line-height: 1.3;
    }

    game-card .gc-smiles {
      font-size: 0.62rem;
      color: var(--gold, #b89a6a);
      white-space: nowrap;
    }

    game-card .gc-value {
      font-family: 'Cormorant Garamond', serif;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--gold, #b89a6a);
      white-space: nowrap;
    }
    game-card[size="salary"] .gc-value {
      font-size: 1.15rem;
    }

    /* ── Encoche de sélection ── */
    game-card .gc-check {
      position: absolute;
      top: 7px; right: 7px;
      width: 20px; height: 20px;
      border-radius: 50%;
      border: 1.5px solid var(--line, #e0d9d0);
      background: var(--surface, #fff);
      display: none;                   /* caché par défaut */
      align-items: center;
      justify-content: center;
      color: transparent;
      transition: background 0.18s, border-color 0.18s, color 0.18s;
      pointer-events: none;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
      z-index: 2;
    }
    /* Afficher uniquement quand selectable */
    game-card[selectable] .gc-check {
      display: flex;
    }
    /* État sélectionné : encoche colorée */
    game-card[selected] .gc-check {
      background: var(--gold, #b89a6a);
      border-color: var(--gold, #b89a6a);
      color: #fff;
    }
    game-card .gc-check svg {
      width: 10px; height: 10px;
    }

    /* Bordure + fond quand sélectionné */
    game-card[selected] .gc-root {
      border-color: var(--gold, #b89a6a);
      background: #fdfaf6;
      box-shadow: 0 0 0 2px rgba(184,154,106,0.25);
    }

    /* ── Cliquable ── */
    game-card[clickable] { cursor: pointer; }

    game-card[clickable] .gc-root:hover {
      transform: translateY(-6px);
      box-shadow: 0 8px 24px rgba(59,48,40,0.15);
      border-color: var(--gold-light, #d4b98a);
    }
    game-card[size="lg"][clickable] .gc-root:hover,
    game-card[size="salary"][clickable] .gc-root:hover {
      transform: translateY(-4px);
      box-shadow: 0 6px 18px rgba(59,48,40,0.14);
    }
    /* Ne pas déplacer si sélectionné + hover */
    game-card[selected][clickable] .gc-root:hover {
      border-color: var(--gold, #b89a6a);
    }

    /* ── Face cachée ── */
    game-card[face-down] .gc-root {
      background: linear-gradient(135deg, var(--accent, #3b3028) 0%, #4a3828 100%);
      border-color: var(--accent, #3b3028);
      cursor: default;
    }
    game-card[face-down] .gc-root::after {
      content: '';
      position: absolute;
      inset: 5px;
      border: 1px solid rgba(184,154,106,0.22);
      border-radius: 3px;
      pointer-events: none;
    }
    game-card[size="sm"][face-down] .gc-root::after { inset: 2px; }
    game-card[face-down] .gc-root:hover { transform: none; box-shadow: none; }
    game-card[face-down] .gc-image,
    game-card[face-down] .gc-type,
    game-card[face-down] .gc-footer,
    game-card[face-down] .gc-check { display: none; }
  `;
  document.head.appendChild(style);
}

// ── Web Component ─────────────────────────────────────────────────────────────

class GameCard extends HTMLElement {

  static get observedAttributes() {
    return [
      "card-id", "name", "type", "image", "smiles", "value",
      "context", "face-down", "size", "clickable", "selected", "selectable",
    ];
  }

  constructor() {
    super();
    injectStyles();
  }

  connectedCallback()                  { this._render(); this._attachListeners(); }
  attributeChangedCallback()           { if (this.isConnected) this._render(); }

  get cardId()     { return this.getAttribute("card-id") ?? ""; }
  get cardName()   { return this.getAttribute("name")    ?? ""; }
  get cardType()   { return this.getAttribute("type")    ?? ""; }
  get cardImage()  { return this.getAttribute("image")   ?? ""; }
  get smiles()     { return parseInt(this.getAttribute("smiles") ?? "0", 10); }
  get value()      { return parseInt(this.getAttribute("value")  ?? "0", 10); }
  get context()    { return this.getAttribute("context") ?? "other"; }
  get size()       { return this.getAttribute("size")    ?? "md"; }
  get isFaceDown() { return this.hasAttribute("face-down"); }
  get isSelected() { return this.hasAttribute("selected"); }

  _render() {
    if (this.isFaceDown) {
      this.innerHTML = `<div class="gc-root"></div>`;
      return;
    }

    const showValue  = this.value > 0;
    const showSmiles = this.smiles !== 0 && !showValue;

    this.innerHTML = `
      <div class="gc-root">
        ${this.cardImage
          ? `<img class="gc-image" src="${window.BASE_URL}//static/${_esc(this.cardImage)}" alt="${_esc(this.cardName)}" onerror="this.style.display='none'">`
          : `<div class="gc-image"></div>`}

        ${this.cardType ? `<span class="gc-type">${_esc(this.cardType)}</span>` : ""}

        <div class="gc-check" aria-hidden="true">
          <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2.2"
                  stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>

        <div class="gc-footer">
          <span class="gc-name">${_esc(this.cardName)}</span>
          ${showValue  ? `<span class="gc-value">${this.value}</span>`        : ""}
          ${showSmiles ? `<span class="gc-smiles">😊 ${this.smiles}</span>` : ""}
        </div>
      </div>`;
  }

  _attachListeners() {
    this.addEventListener("click", () => {
      if (this.isFaceDown) return;
      this.dispatchEvent(new CustomEvent("card-click", {
        bubbles: true,
        composed: true,
        detail: {
          cardId:  this.cardId,
          name:    this.cardName,
          type:    this.cardType,
          smiles:  this.smiles,
          value:   this.value,
          image:   this.cardImage,
          context: this.context,
          raw: this.dataset.card ? JSON.parse(this.dataset.card) : null,
        },
      }));
    });
  }

  /**
   * Crée un <game-card> depuis un objet carte JS.
   * @param {object} card
   * @param {object} opts  — context, size, clickable, faceDown, selectable
   */
  static create(card, opts = {}) {
    const el = document.createElement("game-card");
    if (card.id   != null)   el.setAttribute("card-id", card.id);
    if (card.name)           el.setAttribute("name",    card.name);
    if (card.type)           el.setAttribute("type",    card.type);
    if (card.image_path)     el.setAttribute("image",   card.image_path);
    if (card.smiles != null) el.setAttribute("smiles",  card.smiles);
    if (card.value  != null) el.setAttribute("value",   card.value);
    el.setAttribute("context", opts.context ?? "other");
    el.setAttribute("size",    opts.size    ?? "md");
    if (opts.clickable)  el.setAttribute("clickable",  "");
    if (opts.faceDown)   el.setAttribute("face-down",  "");
    if (opts.selectable) el.setAttribute("selectable", "");
    el.dataset.card = JSON.stringify(card);
    return el;
  }
}

function _esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

customElements.define("game-card", GameCard);

// Exposer globalement pour les scripts non-modules (board.html, etc.)
window.GameCard = GameCard;

export { GameCard };
export default GameCard;