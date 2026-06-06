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
    id: 'base', label: '🎴 Jeu de Base',
    cards: [
      // Métiers
      { id:'architecte',       label:'Architecte',           default:1  },
      { id:'astronaute',       label:'Astronaute',           default:1  },
      { id:'avocat',           label:'Avocat',               default:1  },
      { id:'bandit',           label:'Bandit',               default:1  },
      { id:'barman',           label:'Barman',               default:1  },
      { id:'chef_des_ventes',  label:'Chef des ventes',      default:1  },
      { id:'chef_achats',      label:'Chef des achats',      default:1  },
      { id:'chercheur',        label:'Chercheur',            default:1  },
      { id:'chirurgien',       label:'Chirurgien',           default:1  },
      { id:'designer',         label:'Designer',             default:1  },
      { id:'ecrivain',         label:'Écrivain',             default:1  },
      { id:'garagiste',        label:'Garagiste',            default:1  },
      { id:'gourou',           label:'Gourou',               default:1  },
      { id:'grand_prof',       label:'Grand Prof',           default:1  },
      { id:'jardinier',        label:'Jardinier',            default:1  },
      { id:'journaliste',      label:'Journaliste',          default:1  },
      { id:'medecin',          label:'Médecin',              default:1  },
      { id:'medium',           label:'Médium',               default:1  },
      { id:'militaire',        label:'Militaire',            default:1  },
      { id:'pharmacien',       label:'Pharmacien',           default:1  },
      { id:'pilote',           label:'Pilote de ligne',      default:1  },
      { id:'pizzaiolo',        label:'Pizzaiolo',            default:1  },
      { id:'plombier',         label:'Plombier',             default:1  },
      { id:'policier',         label:'Policier',             default:1  },
      { id:'prof_anglais',     label:"Prof d'anglais",       default:1  },
      { id:'prof_francais',    label:'Prof de français',     default:1  },
      { id:'prof_geo',         label:"Prof d'histoire-géo",  default:1  },
      { id:'prof_maths',       label:'Prof de maths',        default:1  },
      { id:'serveur',          label:'Serveur',              default:1  },
      { id:'stripteaser',      label:'Strip-teaseur',        default:1  },
      // Études
      { id:'study1',           label:'Études simples',       default:22 },
      { id:'study2',           label:'Études doubles',       default:3  },
      // Salaires
      { id:'salary1',          label:'Salaire 1',            default:10 },
      { id:'salary2',          label:'Salaire 2',            default:10 },
      { id:'salary3',          label:'Salaire 3',            default:10 },
      { id:'salary4',          label:'Salaire 4',            default:10 },
      // Flirts
      { id:'flirt_bar',              label:'Flirt au bar',             default:2 },
      { id:'flirt_bibliotheque',     label:'Flirt à la bibliothèque',  default:2 },
      { id:'flirt_boite_de_nuit',    label:'Flirt en boîte de nuit',   default:2 },
      { id:'flirt_cinema',           label:'Flirt au cinéma',          default:2 },
      { id:'flirt_internet',         label:'Flirt sur internet',       default:2 },
      { id:'flirt_manif',            label:'Flirt à la manif',         default:2 },
      { id:'flirt_parc',             label:'Flirt au parc',            default:2 },
      { id:'flirt_restaurant',       label:'Flirt au restaurant',      default:2 },
      { id:'flirt_theatre',          label:'Flirt au théâtre',         default:2 },
      { id:'flirt_zoo',              label:'Flirt au zoo',             default:2 },
      { id:'flirt_with_child_camping', label:'Flirt camping (enfant)', default:2 },
      { id:'flirt_with_child_hotel',   label:"Flirt hôtel (enfant)",   default:2 },
      // Mariages & adultère
      { id:'marriage_corps_nuds',    label:'Mariage Corps-Nuds',       default:1 },
      { id:'marriage_fourqueux',     label:'Mariage Fourqueux',        default:1 },
      { id:'marriage_montcuq',       label:'Mariage Montcuq',          default:1 },
      { id:'marriage_monteton',      label:'Mariage Monteton',         default:1 },
      { id:'marriage_sainte_vierge', label:'Mariage Sainte-Vierge',    default:1 },
      { id:'adultery',               label:'Adultère',                 default:3 },
      // Enfants
      { id:'diana',    label:'Diana',    default:1 },
      { id:'harry',    label:'Harry',    default:1 },
      { id:'hermione', label:'Hermione', default:1 },
      { id:'lara',     label:'Lara',     default:1 },
      { id:'leia',     label:'Leia',     default:1 },
      { id:'luigi',    label:'Luigi',    default:1 },
      { id:'luke',     label:'Luke',     default:1 },
      { id:'mario',    label:'Mario',    default:1 },
      { id:'rocky',    label:'Rocky',    default:1 },
      { id:'zelda',    label:'Zelda',    default:1 },
      // Animaux
      { id:'chat',    label:'Chat',    default:1 },
      { id:'chien',   label:'Chien',   default:1 },
      { id:'lapin',   label:'Lapin',   default:1 },
      { id:'poussin', label:'Poussin', default:1 },
      { id:'licorne', label:'Licorne', default:1 },
      // Maisons
      { id:'house1',  label:'Studio',      default:2 },
      { id:'house2',  label:'Appartement', default:2 },
      { id:'house3',  label:'Villa',       default:1 },
      // Voyages
      { id:'travel_le_caire',  label:'Voyage au Caire',   default:1 },
      { id:'travel_londre',    label:'Voyage à Londres',  default:1 },
      { id:'travel_new_york',  label:'Voyage à New York', default:1 },
      { id:'travel_rio',       label:'Voyage à Rio',      default:1 },
      { id:'travel_sydney',    label:'Voyage à Sydney',   default:1 },
      // Cartes spéciales
      { id:'anniversaire',   label:'Anniversaire',   default:1 },
      { id:'arc_en_ciel',    label:'Arc-en-ciel',    default:1 },
      { id:'casino',         label:'Casino',         default:1 },
      { id:'chance',         label:'Chance',         default:1 },
      { id:'etoile_filante', label:'Étoile filante', default:1 },
      { id:'heritage',       label:'Héritage',       default:1 },
      { id:'piston',         label:'Piston',         default:1 },
      { id:'troc',           label:'Troc',           default:1 },
      { id:'tsunami',        label:'Tsunami',        default:1 },
      { id:'vengeance',      label:'Vengeance',      default:1 },
      // Coups durs
      { id:'accident',       label:'Accident',      default:5 },
      { id:'burnout',        label:'Burn-out',       default:5 },
      { id:'divorce',        label:'Divorce',        default:5 },
      { id:'tax',            label:'Impôts',         default:5 },
      { id:'licenciement',   label:'Licenciement',   default:5 },
      { id:'maladie',        label:'Maladie',        default:5 },
      { id:'redoublement',   label:'Redoublement',   default:5 },
      { id:'prison',         label:'Prison',         default:1 },
      { id:'attentat',       label:'Attentat',       default:1 },
      // Autres
      { id:'legion', label:"Légion d'honneur",         default:1 },
      { id:'prix',   label:"Grand Prix d'Excellence",  default:2 },
    ]
  },
  {
    id: 'extensions', label: '📦 Extensions Standards',
    cards: [
      { id:'youtubeur',      label:'Youtubeur',      default:0 },
      { id:'coiffeur',       label:'Coiffeur',       default:0 },
      { id:'deejay',         label:'Deejay',         default:0 },
      { id:'infirmier',      label:'Infirmier',      default:0 },
      { id:'super_heritage', label:'Super héritage', default:0 },
      { id:'muguet',         label:'Muguet',         default:0 },
      { id:'dragon',         label:'Dragon',         default:0 },
      { id:'crapaud',        label:'Crapaud',        default:0 },
      { id:'concert',        label:'Concert',        default:0 },
      { id:'sabre',          label:'Sabre',          default:0 },
      { id:'nounou',         label:'Nounou',         default:0 },
    ]
  },
  {
    id: 'girl_power', label: '💅 Girl Power',
    cards: [
      // Métiers féminins (à venir)
      { id:'architecte_f',      label:'Architecte',       default:0 },
      { id:'astronaute_f',      label:'Astronaute',        default:0 },
      { id:'avocate',           label:'Avocate',           default:0 },
      { id:'bandit_f',          label:'Bandit',            default:0 },
      { id:'barmaid',           label:'Barmaid',           default:0 },
      { id:'cheffe_des_ventes', label:'Cheffe des ventes', default:0 },
      { id:'cheffe_des_achats', label:'Cheffe des achats', default:0 },
      { id:'chercheuse',        label:'Chercheuse',        default:0 },
      { id:'chirurgienne',      label:'Chirurgienne',      default:0 },
      { id:'designeuse',        label:'Designeuse',        default:0 },
      { id:'ecrivaine',         label:'Écrivaine',         default:0 },
      { id:'garagiste_f',       label:'Garagiste',         default:0 },
      { id:'gourou_f',          label:'Gourou',            default:0 },
      { id:'jardiniere',        label:'Jardinière',        default:0 },
      { id:'journaliste_f',     label:'Journaliste',       default:0 },
      { id:'medecin_f',         label:'Médecin',           default:0 },
      { id:'voyante',           label:'Voyante',           default:0 },
      { id:'militaire_f',       label:'Militaire',         default:0 },
      { id:'pharmacienne',      label:'Pharmacienne',      default:0 },
      { id:'pilote_de_ligne_f', label:'Pilote de ligne',   default:0 },
      { id:'pizzaiola',         label:'Pizzaiola',         default:0 },
      { id:'plombiere',         label:'Plombière',         default:0 },
      { id:'policiere',         label:'Policière',         default:0 },
      { id:'prof_de_chimie',    label:'Prof de chimie',    default:0 },
      { id:'prof_de_musique',   label:'Prof de musique',   default:0 },
      { id:'prof_de_philo',     label:'Prof de philo',     default:0 },
      { id:'serveuse',          label:'Serveuse',          default:0 },
      { id:'stripteaseuse',     label:'Strip-teaseuse',    default:0 },
      { id:'grand_prof_f',      label:'Grand Prof',        default:0 },
      // Enfants
      { id:'angela',   label:'Angela',   default:0 },
      { id:'beatrix',  label:'Beatrix',  default:0 },
      { id:'daenerys', label:'Daenerys', default:0 },
      { id:'louise',   label:'Louise',   default:0 },
      { id:'olympe',   label:'Olympe',   default:0 },
      { id:'simone',   label:'Simone',   default:0 },
      // Cartes spéciales
      { id:'girl_power',            label:'Girl Power',                default:0 },
      { id:'soiree_entre_fille',    label:'Soirée entre filles',       default:0 },
      { id:'coup_de_foudre',        label:'Coup de foudre',            default:0 },
      { id:'erreur_etiquetage',     label:"Erreur d'étiquetage",       default:0 },
      { id:'cliche_metier',         label:'Cliché métier',             default:0 },
      { id:'cliche_flirt',          label:'Cliché flirt',              default:0 },
      { id:'cliche_accident',       label:'Cliché accident',           default:0 },
      { id:'egalite_salaire',       label:'Égalité de salaire',        default:0 },
      { id:'redistribution_taches', label:'Redistribution des tâches', default:0 },
      // Coups durs
      { id:'charge_mental',  label:'Charge mentale',   default:0 },
      { id:'gynocratie',     label:'Gynocratie',       default:0 },
      { id:'phalocratie',    label:'Phallocratie',     default:0 },
      { id:'plafond_verre',  label:'Plafond de verre', default:0 },
      { id:'porc',           label:'Balance ton porc', default:0 },
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
      const res = await fetch(url('/api/presets'));
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

  async function applyPreset(presetId) {
    document.querySelectorAll(`#${_containerId} .preset-btn`).forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`${_containerId}-preset-${presetId}`);
    if (btn) { btn.classList.add('active'); btn.disabled = true; }

    try {
      const res = await fetch(url(`/api/presets/${encodeURIComponent(presetId)}`));
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const preset = await res.json();
      if (!preset.deck) throw new Error('deck manquant dans la réponse');

      EXTENSIONS.forEach(ext => ext.cards.forEach(c => { deckState[c.id] = 0; }));
      Object.entries(preset.deck).forEach(([id, count]) => { deckState[id] = count; });
      EXTENSIONS.forEach(ext => ext.cards.forEach(c => _refreshRow(c.id)));
      _updateTotal();
      _notify();
    } catch (e) {
      console.error('DeckSelector: échec chargement préset', presetId, '—', e.message);
      if (btn) btn.classList.remove('active');
    } finally {
      if (btn) btn.disabled = false;
    }
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