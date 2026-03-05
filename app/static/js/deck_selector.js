/**
 * deck_selector.js — sélecteur de deck réutilisable
 * Utilisé dans lobby.html et room.html
 *
 * API publique :
 *   DeckSelector.init(containerId, options)
 *   DeckSelector.getState()         → { card_id: count, ... }
 *   DeckSelector.setState(deck)     → met à jour l'UI
 *   DeckSelector.onChange(fn)       → callback appelé à chaque modification
 */
const DeckSelector = (() => {

  const EXTENSIONS = [
    {
      id: 'base', label: '🎴 Base',
      cards: [
        { id:'flirt',            label:'Flirt',                default:24 },
        { id:'flirt_with_child', label:'Flirt (avec enfant)',  default:4  },
        { id:'marriage',         label:'Mariage',              default:5  },
        { id:'adultery',         label:'Adultère',             default:3  },
        { id:'angela',           label:'Angela',               default:1  },
        { id:'beatrix',          label:'Beatrix',              default:1  },
        { id:'diana',            label:'Diana',                default:1  },
        { id:'harry',            label:'Harry',                default:1  },
        { id:'hermione',         label:'Hermione',             default:1  },
        { id:'lara',             label:'Lara',                 default:1  },
        { id:'leia',             label:'Leia',                 default:1  },
        { id:'louise',           label:'Louise',               default:1  },
        { id:'luigi',            label:'Luigi',                default:1  },
        { id:'luke',             label:'Luke',                 default:1  },
        { id:'mario',            label:'Mario',                default:1  },
        { id:'olympe',           label:'Olympe',               default:1  },
        { id:'rocky',            label:'Rocky',                default:1  },
        { id:'simone',           label:'Simone',               default:1  },
        { id:'zelda',            label:'Zelda',                default:1  },
        { id:'study',            label:'Études',               default:16 },
        { id:'salary',           label:'Salaire',              default:31 },
        { id:'pizzaiolo',        label:'Pizzaiolo',            default:1  },
        { id:'serveur',          label:'Serveur',              default:1  },
        { id:'stripteaser',      label:'Stripteaser',          default:1  },
        { id:'coiffeur',         label:'Coiffeur',             default:1  },
        { id:'jardinier',        label:'Jardinier',            default:1  },
        { id:'garagiste',        label:'Garagiste',            default:1  },
        { id:'plombier',         label:'Plombier',             default:1  },
        { id:'deejay',           label:'Deejay',               default:1  },
        { id:'youtubeur',        label:'Youtubeur',            default:1  },
        { id:'designer',         label:'Designer',             default:1  },
        { id:'bandit',           label:'Bandit',               default:1  },
        { id:'travel',           label:'Voyage',               default:5  },
        { id:'concert',          label:'Concert',              default:5  },
        { id:'house',            label:'Maison',               default:7  },
        { id:'licorne',          label:'Licorne',              default:1  },
        { id:'dragon',           label:'Dragon',               default:1  },
        { id:'animal',           label:'Animal',               default:6  },
        { id:'accident',         label:'Accident',             default:4  },
        { id:'maladie',          label:'Maladie',              default:4  },
        { id:'tax',              label:'Impôts',               default:4  },
        { id:'burnout',          label:'Burn-Out',             default:3  },
        { id:'divorce',          label:'Divorce',              default:3  },
        { id:'licenciement',     label:'Licenciement',         default:3  },
        { id:'redoublement',     label:'Redoublement',         default:3  },
        { id:'prison',           label:'Prison',               default:2  },
        { id:'legion',           label:"Légion d'honneur",     default:2  },
        { id:'prix',             label:'Grand Prix',           default:3  },
        { id:'heritage',         label:'Héritage',             default:2  },
      ]
    },
    {
      id: 'pro', label: '💼 Extension Pro',
      cards: [
        { id:'infirmier',      label:'Infirmier',        default:1 },
        { id:'ecrivain',       label:'Écrivain',         default:1 },
        { id:'pharmacien',     label:'Pharmacien',       default:1 },
        { id:'architecte',     label:'Architecte',       default:1 },
        { id:'militaire',      label:'Militaire',        default:1 },
        { id:'medium',         label:'Médium',           default:1 },
        { id:'journaliste',    label:'Journaliste',      default:1 },
        { id:'chef_achats',    label:'Chef des Achats',  default:1 },
        { id:'medecin',        label:'Médecin',          default:1 },
        { id:'chirurgien',     label:'Chirurgien',       default:1 },
        { id:'pilote',         label:'Pilote',           default:1 },
        { id:'astronaute',     label:'Astronaute',       default:1 },
        { id:'sabre',          label:'Sabre',            default:2 },
        { id:'nounou',         label:'Nounou',           default:2 },
        { id:'piston',         label:'Piston',           default:2 },
        { id:'coup_de_foudre', label:'Coup de Foudre',   default:2 },
        { id:'plafond_verre',  label:'Plafond de Verre', default:2 },
      ]
    },
    {
      id: 'special', label: '⚡ Extension Spéciale',
      cards: [
        { id:'casino',                label:'Casino',              default:1 },
        { id:'arc_en_ciel',           label:'Arc-en-Ciel',         default:2 },
        { id:'chance',                label:'Chance',              default:3 },
        { id:'etoile_filante',        label:'Étoile Filante',      default:2 },
        { id:'anniversaire',          label:'Anniversaire',        default:2 },
        { id:'tsunami',               label:'Tsunami',             default:2 },
        { id:'vengeance',             label:'Vengeance',           default:2 },
        { id:'muguet',                label:'Muguet',              default:3 },
        { id:'girl_power',            label:'Girl Power',          default:2 },
        { id:'egalite_salaire',       label:'Égalité Salariale',   default:2 },
        { id:'redistribution_taches', label:'Redistribution',      default:1 },
        { id:'soiree_entre_fille',    label:'Soirée entre filles', default:2 },
        { id:'erreur_etiquetage',     label:'Erreur Étiquetage',   default:2 },
        { id:'cliche_accident',       label:'Cliché Accident',     default:2 },
        { id:'cliche_flirt',          label:'Cliché Flirt',        default:2 },
        { id:'cliche_metier',         label:'Cliché Métier',       default:2 },
      ]
    },
    {
      id: 'hardship_plus', label: '💥 Coups Durs+',
      cards: [
        { id:'attentat',      label:'Attentat',         default:2 },
        { id:'charge_mental', label:'Charge Mentale',   default:3 },
        { id:'gynocratie',    label:'Gynocratie',       default:2 },
        { id:'phalocratie',   label:'Phalocratie',      default:2 },
        { id:'porc',          label:'Balance Ton Porc', default:2 },
        { id:'daenerys',      label:'Daenerys',         default:1 },
      ]
    },
  ];

  // Chargé depuis /api/presets
  let PRESETS = [];
  let deckState = {};
  let _containerId = null;
  let _onChangeFn = null;

  // ------------------------------------------------------------------ //
  //  Init                                                                //
  // ------------------------------------------------------------------ //

  async function init(containerId, options = {}) {
    _containerId = containerId;

    // Charger les presets depuis le serveur
    try {
      const res = await fetch('/api/presets');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      PRESETS = await res.json();
      if (!Array.isArray(PRESETS) || PRESETS.length === 0)
        console.warn('DeckSelector: /api/presets retourne un tableau vide — vérifiez data/preset/');
    } catch (e) {
      console.error('DeckSelector: échec chargement presets —', e.message);
      PRESETS = [];
    }

    _buildUI();

    // Appliquer preset initial (ou deck existant si fourni)
    if (options.initialDeck) {
      setState(options.initialDeck);
    } else {
      const defaultPreset = options.defaultPreset ?? 'standard';
      applyPreset(defaultPreset);
    }
  }

  function onChange(fn) {
    _onChangeFn = fn;
  }

  // ------------------------------------------------------------------ //
  //  API publique                                                        //
  // ------------------------------------------------------------------ //

  function getState() {
    return Object.fromEntries(Object.entries(deckState).filter(([, v]) => v > 0));
  }

  function setState(deck) {
    // Reset
    EXTENSIONS.forEach(ext => ext.cards.forEach(c => { deckState[c.id] = 0; }));
    // Appliquer
    Object.entries(deck).forEach(([id, count]) => { deckState[id] = count; });
    // Rafraîchir DOM
    EXTENSIONS.forEach(ext => ext.cards.forEach(c => _refreshRow(c.id)));
    _updateTotal();
    _clearActivePreset();

    // Marquer le preset actif si le deck correspond exactement
    const stateStr = JSON.stringify(getState());
    PRESETS.forEach(p => {
      if (JSON.stringify(p.deck) === stateStr) {
        const btn = document.getElementById(`${_containerId}-preset-${p.id}`);
        if (btn) btn.classList.add('active');
      }
    });
  }

  // ------------------------------------------------------------------ //
  //  Presets                                                             //
  // ------------------------------------------------------------------ //

  function applyPreset(presetId) {
    const preset = PRESETS.find(p => p.id === presetId);
    if (!preset) return;

    EXTENSIONS.forEach(ext => ext.cards.forEach(c => { deckState[c.id] = 0; }));
    Object.entries(preset.deck).forEach(([id, count]) => { deckState[id] = count; });
    EXTENSIONS.forEach(ext => ext.cards.forEach(c => _refreshRow(c.id)));
    _updateTotal();

    document.querySelectorAll(`#${_containerId} .preset-btn`).forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`${_containerId}-preset-${presetId}`);
    if (btn) btn.classList.add('active');

    _notify();
  }

  function _clearActivePreset() {
    document.querySelectorAll(`#${_containerId} .preset-btn`).forEach(b => b.classList.remove('active'));
  }

  // ------------------------------------------------------------------ //
  //  Construction du DOM                                                 //
  // ------------------------------------------------------------------ //

  function _buildUI() {
    const container = document.getElementById(_containerId);
    if (!container) return;

    // Résumé + presets + toggle + panel
    container.innerHTML = `
      <div class="deck-summary">
        <span>Cartes sélectionnées</span>
        <span><strong id="${_containerId}-total">0</strong> cartes</span>
      </div>

      <div class="presets" id="${_containerId}-presets"></div>

      <button type="button" class="deck-toggle-btn" id="${_containerId}-toggle"
              onclick="DeckSelector._toggle('${_containerId}')">
        <span>Personnaliser carte par carte</span>
        <span class="arrow">▼</span>
      </button>

      <div class="deck-panel" id="${_containerId}-panel">
        <div class="ext-tabs"  id="${_containerId}-tabs"></div>
        <div id="${_containerId}-contents"></div>
      </div>
    `;

    // Boutons presets
    const presetsEl = document.getElementById(`${_containerId}-presets`);
    PRESETS.forEach(p => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'preset-btn';
      btn.id = `${_containerId}-preset-${p.id}`;
      btn.textContent = p.label;
      if (p.description) btn.title = p.description;
      btn.addEventListener('click', () => applyPreset(p.id));
      presetsEl.appendChild(btn);
    });

    // Onglets + contenu
    const tabsEl     = document.getElementById(`${_containerId}-tabs`);
    const contentsEl = document.getElementById(`${_containerId}-contents`);

    EXTENSIONS.forEach((ext, idx) => {
      // Onglet
      const tab = document.createElement('div');
      tab.className = 'ext-tab' + (idx === 0 ? ' active' : '');
      tab.textContent = ext.label;
      tab.dataset.ext = ext.id;
      tab.addEventListener('click', () => _switchTab(ext.id));
      tabsEl.appendChild(tab);

      // Contenu
      const content = document.createElement('div');
      content.className = 'ext-content' + (idx === 0 ? ' active' : '');
      content.id = `${_containerId}-ext-${ext.id}`;

      const header = document.createElement('div');
      header.className = 'ext-header';
      header.innerHTML = `
        <span>${ext.cards.length} types de cartes</span>
        <div class="ext-actions">
          <button type="button" class="ext-action-btn"
                  onclick="DeckSelector._selectAll('${_containerId}','${ext.id}')">Tout cocher</button>
          <button type="button" class="ext-action-btn"
                  onclick="DeckSelector._deselectAll('${_containerId}','${ext.id}')">Tout décocher</button>
          <button type="button" class="ext-action-btn"
                  onclick="DeckSelector._resetCounts('${_containerId}','${ext.id}')">Réinitialiser</button>
        </div>`;
      content.appendChild(header);

      const grid = document.createElement('div');
      grid.className = 'card-grid';

      ext.cards.forEach(card => {
        const row = document.createElement('div');
        row.className = 'card-row inactive';
        row.id = `${_containerId}-row-${card.id}`;
        row.innerHTML = `
          <input type="checkbox" class="card-toggle" id="${_containerId}-chk-${card.id}"
                 onchange="DeckSelector._onToggle('${_containerId}','${card.id}','${ext.id}')">
          <label class="card-check" for="${_containerId}-chk-${card.id}"></label>
          <label class="card-label" for="${_containerId}-chk-${card.id}">${card.label}</label>
          <div class="card-count-ctrl">
            <button type="button" class="count-btn"
                    onclick="DeckSelector._changeCount('${_containerId}','${card.id}',-1,'${ext.id}')">−</button>
            <span class="count-val" id="${_containerId}-cnt-${card.id}">0</span>
            <button type="button" class="count-btn"
                    onclick="DeckSelector._changeCount('${_containerId}','${card.id}',+1,'${ext.id}')">+</button>
          </div>`;
        grid.appendChild(row);
        deckState[card.id] = 0;
      });

      content.appendChild(grid);
      contentsEl.appendChild(content);
    });
  }

  // ------------------------------------------------------------------ //
  //  Interactions internes (exposées pour onclick inline)               //
  // ------------------------------------------------------------------ //

  function _toggle(cid) {
    const panel  = document.getElementById(`${cid}-panel`);
    const toggle = document.getElementById(`${cid}-toggle`);
    const isOpen = panel.classList.toggle('open');
    toggle.classList.toggle('open', isOpen);
    toggle.querySelector('span:first-child').textContent =
      isOpen ? 'Masquer la personnalisation' : 'Personnaliser carte par carte';
  }

  function _switchTab(extId) {
    document.querySelectorAll(`#${_containerId} .ext-tab`).forEach(t =>
      t.classList.toggle('active', t.dataset.ext === extId));
    EXTENSIONS.forEach(ext => {
      const el = document.getElementById(`${_containerId}-ext-${ext.id}`);
      if (el) el.classList.toggle('active', ext.id === extId);
    });
  }

  function _onToggle(cid, cardId, extId) {
    const chk  = document.getElementById(`${cid}-chk-${cardId}`);
    const card = _getCardDef(cardId, extId);
    deckState[cardId] = chk.checked ? (card ? card.default : 1) : 0;
    _refreshRow(cardId);
    _updateTotal();
    _clearActivePreset();
    _notify();
  }

  function _changeCount(cid, cardId, delta, extId) {
    const current = deckState[cardId] ?? 0;
    deckState[cardId] = Math.max(0, Math.min(99, current + delta));
    const chk = document.getElementById(`${cid}-chk-${cardId}`);
    if (chk) chk.checked = deckState[cardId] > 0;
    _refreshRow(cardId);
    _updateTotal();
    _clearActivePreset();
    _notify();
  }

  function _selectAll(cid, extId) {
    const ext = EXTENSIONS.find(e => e.id === extId);
    if (!ext) return;
    ext.cards.forEach(c => {
      deckState[c.id] = deckState[c.id] > 0 ? deckState[c.id] : c.default;
      const chk = document.getElementById(`${cid}-chk-${c.id}`);
      if (chk) chk.checked = true;
      _refreshRow(c.id);
    });
    _updateTotal(); _clearActivePreset(); _notify();
  }

  function _deselectAll(cid, extId) {
    const ext = EXTENSIONS.find(e => e.id === extId);
    if (!ext) return;
    ext.cards.forEach(c => {
      deckState[c.id] = 0;
      const chk = document.getElementById(`${cid}-chk-${c.id}`);
      if (chk) chk.checked = false;
      _refreshRow(c.id);
    });
    _updateTotal(); _clearActivePreset(); _notify();
  }

  function _resetCounts(cid, extId) {
    const ext = EXTENSIONS.find(e => e.id === extId);
    if (!ext) return;
    ext.cards.forEach(c => {
      if (deckState[c.id] > 0) { deckState[c.id] = c.default; _refreshRow(c.id); }
    });
    _updateTotal(); _notify();
  }

  function _refreshRow(cardId) {
    const count   = deckState[cardId] ?? 0;
    const checked = count > 0;
    const cntEl   = document.getElementById(`${_containerId}-cnt-${cardId}`);
    const chkEl   = document.getElementById(`${_containerId}-chk-${cardId}`);
    const checkLabel = chkEl?.nextElementSibling;
    const row     = document.getElementById(`${_containerId}-row-${cardId}`);
    if (cntEl) cntEl.textContent = count;
    if (checkLabel) checkLabel.textContent = checked ? '✓' : '';
    if (row) row.classList.toggle('inactive', !checked);
  }

  function _updateTotal() {
    const total = Object.values(deckState).reduce((s, v) => s + v, 0);
    const el = document.getElementById(`${_containerId}-total`);
    if (el) el.textContent = total;
  }

  function _getCardDef(cardId, extId) {
    const ext = EXTENSIONS.find(e => e.id === extId);
    return ext ? ext.cards.find(c => c.id === cardId) : null;
  }

  function _notify() {
    if (_onChangeFn) _onChangeFn(getState());
  }

  // Exposé pour les onclick inline
  return { init, getState, setState, applyPreset, onChange,
           _toggle, _onToggle, _changeCount, _selectAll, _deselectAll, _resetCounts };
})();