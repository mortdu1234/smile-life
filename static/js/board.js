// ═══════════════════════════════════════════════════════════
//  board.js — Logique du plateau
//  Dépendances : window.GAME_ID, window.PSEUDO, window.IS_MY_TURN
//  (injectés par board.html via un <script> inline Jinja)
// ═══════════════════════════════════════════════════════════

// ── Helpers ──────────────────────────────────────────────────────────────
function dispatchOpenCard(card, context) {
  if (typeof window.openCard === "function") {
    window.openCard(card, context);
  } else {
    console.warn("openCard pas encore chargé");
  }
}

// ── Listener délégué — cartes HTML classiques (.clickable-card) ──────────
// Couvre les cartes générées par Jinja au chargement initial
document.addEventListener("click", function(e) {
  const card_el = e.target.closest(".clickable-card");
  if (!card_el) return;
  const raw     = card_el.dataset.card;
  const context = card_el.dataset.context;
  if (!raw || !context) return;
  try {
    dispatchOpenCard(JSON.parse(raw), context);
  } catch(err) {
    console.error("Erreur parsing carte :", err, raw);
  }
});

// ── Listener délégué — composant <game-card> ──────────────────────────────
// Couvre les cartes injectées dynamiquement par updateBoard / GameCard.create()
document.addEventListener("card-click", function(e) {
  const { raw, context } = e.detail ?? {};
  if (!raw || !context) return;
  dispatchOpenCard(raw, context);
});

// ── Historique ───────────────────────────────────────────────────────────
const ACTION_ICONS = {
  draw:    '🂠',
  play:    '🃏',
  discard: '🗑️',
  turn:    '🔄',
};

function renderHistory(entries) {
  const list = document.getElementById('history-list');
  if (!entries || entries.length === 0) return;
  list.innerHTML = '';
  entries.slice(-10).reverse().forEach((entry, i) => {
    const div = document.createElement('div');
    div.className = 'history-entry' + (i === 0 ? ' latest' : '');
    const icon = ACTION_ICONS[entry.action] ?? '▸';
    div.innerHTML = `<span class="h-icon">${icon}</span><span class="h-text">${entry.text}</span>`;
    list.appendChild(div);
  });
}

// ── Piocher ──────────────────────────────────────────────────────────────
async function drawCard() {
  if (!window.IS_MY_TURN) return;
  const res = await fetch(`/game/${window.GAME_ID}/draw`, { method: 'POST' });
  const data = await res.json();
  if (!data.ok) { alert(data.error); return; }
  if (data.state) updateBoard(data.state);
}

// ── Passer le tour ───────────────────────────────────────────────────────
async function skipTurn() {
  if (!window.IS_MY_TURN) return;
  const btn = document.getElementById('btn-skip');
  if (btn) btn.disabled = true;
  const res = await fetch(`/game/${window.GAME_ID}/skip`, { method: 'POST' });
  const data = await res.json();
  if (!data.ok) { alert(data.error); if (btn) btn.disabled = false; return; }
  if (data.state) updateBoard(data.state);
}
window.skipTurn = skipTurn;

async function stopArcEnCiel() {
  if (!window.IS_MY_TURN) return;
  const btn = document.getElementById('btn-arc-en-ciel');
  if (btn) btn.disabled = true;
  const res = await fetch(`/game/${window.GAME_ID}/stop-arc-en-ciel`, { method: 'POST' });
  const data = await res.json();
  if (!data.ok) { alert(data.error); if (btn) btn.disabled = false; return; }
  if (data.state) updateBoard(data.state);
}
window.stopArcEnCiel = stopArcEnCiel;

// ── Jouer une carte ──────────────────────────────────────────────────────
async function playCard(cardId) {
  if (!window.IS_MY_TURN) return;
  const res = await fetch(`/game/${window.GAME_ID}/place`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card_id: cardId }),
  });
  const data = await res.json();
  if (!data.ok) { alert(data.error); return; }
  if (data.state) updateBoard(data.state);
  if (data.io) window.dispatchEvent(new CustomEvent("io-message", { detail: data.io }));
}
window.playCard = playCard;

// ── Défausser une carte ───────────────────────────────────────────────────
async function discardCard(cardId) {
  if (!window.IS_MY_TURN) return;
  const res = await fetch(`/game/${window.GAME_ID}/discard`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card_id: cardId }),
  });
  const data = await res.json();
  if (!data.ok) { alert(data.error); return; }
}
window.discardCard = discardCard;

// ── updateBoard : met à jour le plateau sans recharger la page ───────────
window.updateBoard = function(state) {
  console.log('Mise à jour plateau debut:', state.players.map(p => ({
    name: p.name,
    cartes_posees: Object.keys(p.cards).length,
    hand: p.hand?.length ?? 'masquée'
  })));
  if (!state) return;

  // Indicateur de tour (nav)
  const isMyTurn = state.current_player?.name === window.PSEUDO;
  window.IS_MY_TURN = isMyTurn;
  const navTurn = document.getElementById("nav-turn");
  if (navTurn) {
    navTurn.className = "nav-turn " + (isMyTurn ? "my-turn" : "other-turn");
    navTurn.textContent = isMyTurn ? "✦ Votre tour" : ("Tour de " + (state.current_player?.name ?? "…"));
  }

  // Historique
  if (state.history) renderHistory(state.history);

  // Scores
  const scoresList = document.getElementById("scores-list");
  if (scoresList && state.players) {
    scoresList.innerHTML = state.players.map(p => {
      const smiles = Object.values(p.groupe ?? {})
        .flat().reduce((s, c) => s + (c.smiles ?? 0), 0);
      const isMe = p.name === window.PSEUDO;
      return `<div class="score-row ${isMe ? 'me' : ''}">
        <div class="score-avatar">${p.name[0].toUpperCase()}</div>
        <span class="score-name">${p.name}</span>
        <span class="score-val">${smiles}</span>
        </div>`;
    }).join('');
  }

  // Mise à jour de la main (mes cartes)
  const myPlayer = state.players?.find(p => p.name === window.PSEUDO);
  const handEl = document.getElementById("my-hand-cards");
  if (handEl && myPlayer) {
    if (!myPlayer.hand || myPlayer.hand.length === 0) {
      handEl.innerHTML = '<span class="hand-empty">Aucune carte en main.</span>';
    } else {
      handEl.innerHTML = "";
      const context = isMyTurn ? "hand" : "view";
      myPlayer.hand.forEach(card => {
        const el = GameCard.create(card, { context, size: "md", clickable: true });
        handEl.appendChild(el);
      });
    }
  }

  // Mise à jour du deck et de la défausse
  const deckCount = document.querySelector(".deck-count");
  if (deckCount) {
    const raw = state.deck_count ?? state.deck ?? '?';
    deckCount.textContent = Array.isArray(raw) ? raw.length : raw;
  }
  const discardSlot = document.getElementById("discard-card-slot");
  if (discardSlot) {
    discardSlot.innerHTML = "";
    if (state.last_discard) {
      const el = GameCard.create(state.last_discard, { context: "discard", size: "md", clickable: true });
      discardSlot.appendChild(el);
    } else {
      discardSlot.innerHTML = '<div class="deck-card defausse"><span class="defausse-empty">Vide</span></div>';
    }
  }

  // Mise à jour du bouton pioche (cliquable seulement si mon tour)
  const pileEl = document.querySelector(".deck-card.pioche");
  if (pileEl) {
    pileEl.classList.toggle("clickable", isMyTurn);
    pileEl.onclick = isMyTurn ? drawCard : null;
  }

  // Mise à jour du bouton "Arc-en-ciel"
  const arcBtn = document.getElementById('btn-arc-en-ciel');
  if (arcBtn) {
    const arcVal = state.game_state?.arc_en_ciel ?? 0;
    arcBtn.style.display = (isMyTurn && arcVal > 1) ? 'flex' : 'none';
    arcBtn.disabled = false;
  }

  // Mise à jour du bouton "Passer le tour"
  const skipBtn   = document.getElementById('btn-skip');
  const skipBadge = document.getElementById('skip-badge');
  if (skipBtn && myPlayer) {
    const skipCount = myPlayer.skip_turn ?? 0;
    const canSkip   = isMyTurn && skipCount > 0;
    skipBtn.disabled = !canSkip;
    if (skipBadge) skipBadge.textContent = skipCount;
  }

  // Mise à jour sidebar état du jeu
  const statusBadge = document.querySelector(".status-badge");
  const turnInfo = document.querySelector(".turn-info");
  if (statusBadge && turnInfo) {
    if (isMyTurn) {
      statusBadge.className = "status-badge active";
      statusBadge.textContent = "✦ Piochez ou agissez";
      turnInfo.innerHTML = "C'est <strong>votre tour</strong>";
    } else {
      statusBadge.className = "status-badge waiting";
      statusBadge.textContent = "⏳ En attente";
      turnInfo.innerHTML = `Tour de <strong>${state.current_player?.name ?? '…'}</strong>`;
    }
  }

  // ── Mise à jour du plateau (cartes posées) ──────────────────────────
  const CATEGORIES = [
    'vie_professionnelle',
    'vie_personnelle',
    'acquisitions',
    'cartes_protegees',
    'cartes_speciales',
  ];

  if (state.players) {
    state.players.forEach(player => {
      const isMe = player.name === window.PSEUDO;
      const isCurrent = player.name === state.current_player?.name;

      // Info col : smiles + main adversaire
      const infoEl = document.getElementById(`info-${player.name}`);
      if (infoEl) {
        const smiles = Object.values(player.groupe ?? {})
          .flat().reduce((s, c) => s + (c.smiles ?? 0), 0);
        const handCount = player.hand_count ?? 0;
        infoEl.querySelector('.player-stats').textContent =
          `😊 ${smiles} smiles · ${handCount} carte${handCount !== 1 ? 's' : ''}`;

        // Mini cartes adversaire
        const miniEl = infoEl.querySelector('.opponent-hand-mini');
        if (miniEl) {
          miniEl.innerHTML = Array(handCount).fill(
            '<div class="game-card face-down"></div>'
          ).join('');
        }

        // Tag tour
        const tagEl = infoEl.querySelector('.current-turn-tag');
        if (tagEl) tagEl.style.display = isCurrent && !isMe ? '' : 'none';
      }

      // Cellules de catégories
      CATEGORIES.forEach(cat => {
        const cell = document.getElementById(`cell-${player.name}-${cat}`);
        if (!cell) return;
        const cards = player.groupe?.[cat] ?? [];
        if (cards.length === 0) {
          cell.innerHTML = '<span class="cell-empty">—</span>';
        } else {
          cell.innerHTML = "";
          cards.forEach(card => {
            const el = GameCard.create(card, { context: "played", size: "lg", clickable: true });
            cell.appendChild(el);
          });
        }
      });
    });
  }
};

// ── Polling léger en fallback (si SSE non connecté) ──────────────────────
// Uniquement pour l'historique — le reload de tour est géré par updateBoard
(function pollHistory() {
  setTimeout(async () => {
    try {
      const res = await fetch(`/game/${window.GAME_ID}/state`);
      const state = await res.json();
      if (state.history) renderHistory(state.history);
    } catch (e) { /* silencieux */ }
    pollHistory();
  }, 5000);
})();