// ═══════════════════════════════════════════════════════════
//  board.js — Logique principale du plateau
//  Dépendances : card-game.js (GameCard), board-stream.js (socket)
// ═══════════════════════════════════════════════════════════


// ── Globals exposés ──────────────────────────────────────────────────────
window.GAME_ID    = GAME_ID;
window.IS_MY_TURN = IS_MY_TURN;
window.PSEUDO     = "{{ pseudo }}";


// ════════════════════════════════════════════════════════════
//  SECTION 1 — Actions joueur (fetch vers le serveur)
// ════════════════════════════════════════════════════════════

async function drawCard() {
    if (!window.IS_MY_TURN) return;
    const res  = await fetch(`/game/${GAME_ID}/draw`, { method: 'POST' });
    const data = await res.json();
    if (!data.ok) { alert(data.error); return; }
    if (data.state) updateBoard(data.state);
}

async function skipTurn() {
    if (!window.IS_MY_TURN) return;
    const btn = document.getElementById('btn-skip');
    if (btn) btn.disabled = true;
    const res  = await fetch(`/game/${GAME_ID}/skip`, { method: 'POST' });
    const data = await res.json();
    if (!data.ok) { alert(data.error); if (btn) btn.disabled = false; return; }
    if (data.state) updateBoard(data.state);
}
window.skipTurn = skipTurn;

async function stopArcEnCiel() {
    if (!window.IS_MY_TURN) return;
    const btn = document.getElementById('btn-arc-en-ciel');
    if (btn) btn.disabled = true;
    const res  = await fetch(`/game/${GAME_ID}/stop-arc-en-ciel`, { method: 'POST' });
    const data = await res.json();
    if (!data.ok) { alert(data.error); if (btn) btn.disabled = false; return; }
    if (data.state) updateBoard(data.state);
}
window.stopArcEnCiel = stopArcEnCiel;

async function playCard(cardId) {
    if (!window.IS_MY_TURN) return;
    const res  = await fetch(`/game/${GAME_ID}/place`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ card_id: cardId }),
    });
    const data = await res.json();
    if (!data.ok) { alert(data.error); return; }
    if (data.state) updateBoard(data.state);
    if (data.io) window.dispatchEvent(new CustomEvent("io-message", { detail: data.io }));
}
window.playCard = playCard;

async function discardCard(cardId) {
    if (!window.IS_MY_TURN) return;
    const res  = await fetch(`/game/${GAME_ID}/discard`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ card_id: cardId }),
    });
    const data = await res.json();
    if (!data.ok) { alert(data.error); return; }
}
window.discardCard = discardCard;


// ════════════════════════════════════════════════════════════
//  SECTION 2 — Ouverture de carte (délégation de clics)
// ════════════════════════════════════════════════════════════

function dispatchOpenCard(card, context) {
    if (typeof window.openCard === "function") {
        window.openCard(card, context);
    } else {
        console.warn("openCard pas encore chargé");
    }
}

// Cartes HTML classiques générées par Jinja au chargement initial
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

// Cartes injectées dynamiquement par updateBoard / GameCard.create()
document.addEventListener("card-click", function(e) {
    const { raw, context } = e.detail ?? {};
    if (!raw || !context) return;
    dispatchOpenCard(raw, context);
});


// ════════════════════════════════════════════════════════════
//  SECTION 3 — Rendu du plateau (updateBoard)
// ════════════════════════════════════════════════════════════

const BOARD_CATEGORIES = [
    'vie_professionnelle',
    'vie_personnelle',
    'acquisitions',
    'cartes_protegees',
    'cartes_speciales',
];

window.updateBoard = function(state) {
    if (!state) return;

    console.log('Mise à jour plateau :', state.players.map(p => ({
        name:         p.name,
        cartes_posees: Object.keys(p.cards).length,
        hand:         p.hand?.length ?? 'masquée',
    })));

    const isMyTurn = state.current_player?.name === "{{ pseudo }}";
    window.IS_MY_TURN = isMyTurn;

    _updateNavTurn(state, isMyTurn);
    _updateSidebar(state, isMyTurn);
    _updateScores(state);
    _updateHand(state, isMyTurn);
    _updateDeckAndDiscard(state, isMyTurn);
    _updateActionButtons(state, isMyTurn);
    _updatePlayerBoards(state, isMyTurn);
    if (state.history) renderHistory(state.history);
};

// ── Helpers de rendu ─────────────────────────────────────────────────────

function _updateNavTurn(state, isMyTurn) {
    const navTurn = document.getElementById("nav-turn");
    if (!navTurn) return;
    navTurn.className   = "nav-turn " + (isMyTurn ? "my-turn" : "other-turn");
    navTurn.textContent = isMyTurn
        ? "✦ Votre tour"
        : ("Tour de " + (state.current_player?.name ?? "…"));
}

function _updateSidebar(state, isMyTurn) {
    const statusBadge = document.querySelector(".status-badge");
    const turnInfo    = document.querySelector(".turn-info");
    if (!statusBadge || !turnInfo) return;
    if (isMyTurn) {
        statusBadge.className   = "status-badge active";
        statusBadge.textContent = "✦ Piochez ou agissez";
        turnInfo.innerHTML      = "C'est <strong>votre tour</strong>";
    } else {
        statusBadge.className   = "status-badge waiting";
        statusBadge.textContent = "⏳ En attente";
        turnInfo.innerHTML      = `Tour de <strong>${state.current_player?.name ?? '…'}</strong>`;
    }
}

function _updateScores(state) {
    const scoresList = document.getElementById("scores-list");
    if (!scoresList || !state.players) return;
    scoresList.innerHTML = state.players.map(p => {
        const smiles = Object.values(p.groupe ?? {})
            .flat().reduce((s, c) => s + (c.smiles ?? 0), 0);
        const isMe = p.name === "{{ pseudo }}";
        return `<div class="score-row ${isMe ? 'me' : ''}">
            <div class="score-avatar">${p.name[0].toUpperCase()}</div>
            <span class="score-name">${p.name}</span>
            <span class="score-val">${smiles}</span>
        </div>`;
    }).join('');
}

function _updateHand(state, isMyTurn) {
    const myPlayer = state.players?.find(p => p.name === "{{ pseudo }}");
    const handEl   = document.getElementById("my-hand-cards");
    if (!handEl || !myPlayer) return;
    if (!myPlayer.hand || myPlayer.hand.length === 0) {
        handEl.innerHTML = '<span class="hand-empty">Aucune carte en main.</span>';
        return;
    }
    handEl.innerHTML = "";
    const context = isMyTurn ? "hand" : "view";
    myPlayer.hand.forEach(card => {
        const el = GameCard.create(card, { context, size: "md", clickable: true });
        handEl.appendChild(el);
    });
}

function _updateDeckAndDiscard(state, isMyTurn) {
    // Compteur deck
    const deckCount = document.querySelector(".deck-count");
    if (deckCount) deckCount.textContent = state.deck_count ?? '?';

    // Bouton pioche
    const pileEl = document.querySelector(".deck-card.pioche");
    if (pileEl) {
        pileEl.classList.toggle("clickable", isMyTurn);
        pileEl.onclick = isMyTurn ? drawCard : null;
    }

    // Défausse
    const discardSlot = document.getElementById("discard-card-slot");
    if (!discardSlot) return;
    discardSlot.innerHTML = "";
    if (state.last_discard) {
        const el = GameCard.create(state.last_discard, { context: "discard", size: "md", clickable: true });
        discardSlot.appendChild(el);
    } else {
        discardSlot.innerHTML = '<div class="deck-card defausse"><span class="defausse-empty">Vide</span></div>';
    }
}

function _updateActionButtons(state, isMyTurn) {
    // Bouton "Arc-en-ciel"
    const arcBtn = document.getElementById('btn-arc-en-ciel');
    if (arcBtn) {
        const arcVal = state.game_state?.arc_en_ciel ?? 0;
        arcBtn.style.display = (isMyTurn && arcVal > 1) ? 'flex' : 'none';
        arcBtn.disabled      = false;
    }

    // Bouton "Passer le tour"
    const skipBtn   = document.getElementById('btn-skip');
    const skipBadge = document.getElementById('skip-badge');
    const myPlayer  = state.players?.find(p => p.name === "{{ pseudo }}");
    if (skipBtn && myPlayer) {
        const skipCount  = myPlayer.skip_turn ?? 0;
        skipBtn.disabled = !(isMyTurn && skipCount > 0);
        if (skipBadge) skipBadge.textContent = skipCount;
    }
}

function _updatePlayerBoards(state, isMyTurn) {
    if (!state.players) return;
    state.players.forEach(player => {
        const isMe      = player.name === "{{ pseudo }}";
        const isCurrent = player.name === state.current_player?.name;

        // Info col (smiles + main adversaire)
        const infoEl = document.getElementById(`info-${player.name}`);
        if (infoEl) {
            const smiles    = Object.values(player.groupe ?? {})
                .flat().reduce((s, c) => s + (c.smiles ?? 0), 0);
            const handCount = player.hand_count ?? 0;
            infoEl.querySelector('.player-stats').textContent =
                `😊 ${smiles} smiles · ${handCount} carte${handCount !== 1 ? 's' : ''}`;

            const miniEl = infoEl.querySelector('.opponent-hand-mini');
            if (miniEl) {
                miniEl.innerHTML = Array(handCount)
                    .fill('<div class="game-card face-down"></div>')
                    .join('');
            }

            const tagEl = infoEl.querySelector('.current-turn-tag');
            if (tagEl) tagEl.style.display = (isCurrent && !isMe) ? '' : 'none';
        }

        // Cellules de catégories
        BOARD_CATEGORIES.forEach(cat => {
            const cell  = document.getElementById(`cell-${player.name}-${cat}`);
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


// ════════════════════════════════════════════════════════════
//  SECTION 4 — Historique
// ════════════════════════════════════════════════════════════

const ACTION_ICONS = {
    draw:    '🂠',
    play:    '🃏',
    discard: '🗑️',
    turn:    '🔄',
};

function renderHistory(entries) {
    const list = document.getElementById('history-list');
    if (!list || !entries || entries.length === 0) return;
    list.innerHTML = '';
    entries.slice(-10).reverse().forEach((entry, i) => {
        const div   = document.createElement('div');
        div.className = 'history-entry' + (i === 0 ? ' latest' : '');
        const icon  = ACTION_ICONS[entry.action] ?? '▸';
        div.innerHTML = `<span class="h-icon">${icon}</span><span class="h-text">${entry.text}</span>`;
        list.appendChild(div);
    });
}


// ════════════════════════════════════════════════════════════
//  SECTION 5 — Polling de fallback (historique uniquement)
// ════════════════════════════════════════════════════════════

(function pollHistory() {
    setTimeout(async () => {
        try {
            const res   = await fetch(`/game/${GAME_ID}/state`);
            const state = await res.json();
            if (state.history) renderHistory(state.history);
        } catch (e) { /* silencieux */ }
        pollHistory();
    }, 5000);
})();