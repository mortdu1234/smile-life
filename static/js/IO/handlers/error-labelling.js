import { registerHandler } from "../io-registry.js";
import { getHandler }      from "../io-registry.js";

// ── Aide : ouvre card-detail en lecture seule (comme card-picker / salary-selector) ─
function openCardDetail(card) {
  const handler = getHandler("card-detail");
  if (!handler) {
    console.error("[error-labelling] Handler card-detail introuvable.");
    return;
  }
  const detailOverlay = handler({
    card,
    context:    "other",
    is_my_turn: false,
    game_id:    window.GAME_ID ?? "",
  });
  document.body.appendChild(detailOverlay);
}

// ── Aide : construit un <game-card> cliquable et sélectionnable ─────────────
function buildCardEl(card, { selected, onClick }) {
  const el = GameCard.create(card, {
    context:    "other",
    size:       "md",
    clickable:  true,
    selectable: true,
  });

  el.dataset.cardId = card.id;
  el.setAttribute("role", "option");
  el.setAttribute("aria-selected", selected ? "true" : "false");
  el.setAttribute("aria-label", card.name ?? "Carte");
  el.setAttribute("tabindex", "0");
  if (selected) el.setAttribute("selected", "");

  const handleActivate = () => {
    onClick();
    openCardDetail(card);
  };

  el.addEventListener("card-click", handleActivate);
  el.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleActivate();
    }
  });

  return el;
}

function renderErrorLabelling(pending) {
  const { prompt, owner_name, owner_cards = [], others = [], onSubmit } = pending;

  const overlay = document.getElementById("labelling-overlay");
  if (!overlay) {
    console.error("#labelling-overlay introuvable dans le DOM");
    return null;
  }

  // Évite de tout reconstruire (et donc de perdre la sélection en cours)
  // si le même "pending" est re-rendu par le polling.
  const signature = JSON.stringify({ prompt, owner_name, owner_cards, others });
  if (overlay.dataset.signature === signature && !overlay.hidden) {
    return null;
  }
  overlay.dataset.signature = signature;

  overlay.hidden = false;

  // ── État de sélection ──────────────────────────────────────────────────
  let ownerIndex = null;
  let otherPlayerIndex = null;
  let otherCardIndex = null;

  const promptEl = overlay.querySelector("#labelling-prompt-text");
  const ownerNameEl = overlay.querySelector("#owner-name");
  const ownerAvatarEl = overlay.querySelector("#owner-avatar");
  const ownerGrid = overlay.querySelector("#owner-cards-grid");
  const othersList = overlay.querySelector("#others-list");
  const confirmBtn = overlay.querySelector("#labelling-confirm-btn");

  promptEl.textContent = prompt ?? "";
  ownerNameEl.textContent = owner_name ?? "";
  ownerAvatarEl.textContent = (owner_name ?? "?").charAt(0).toUpperCase();

  function updateConfirmState() {
    confirmBtn.disabled = !(ownerIndex !== null && otherPlayerIndex !== null && otherCardIndex !== null);
  }

  // ── Ligne du joueur courant ────────────────────────────────────────────
  ownerGrid.innerHTML = "";
  owner_cards.forEach((card, idx) => {
    const el = buildCardEl(card, {
      selected: idx === ownerIndex,
      onClick: () => {
        ownerIndex = idx;
        ownerGrid.querySelectorAll("game-card").forEach((c, i) => {
          const isSelected = i === idx;
          c.toggleAttribute("selected", isSelected);
          c.setAttribute("aria-selected", isSelected ? "true" : "false");
        });
        updateConfirmState();
      },
    });
    ownerGrid.appendChild(el);
  });

  // ── Lignes des autres joueurs ──────────────────────────────────────────
  othersList.innerHTML = "";
  others.forEach((other, pIdx) => {
    const row = document.createElement("div");
    row.className = "labelling-overlay__other-row";

    const header = document.createElement("div");
    header.className = "labelling-overlay__player-badge";
    header.innerHTML = `
      <div class="labelling-overlay__player-avatar">${(other.player_name ?? "?").charAt(0).toUpperCase()}</div>
      <span class="labelling-overlay__player-name">${other.player_name ?? ""}</span>
    `;
    row.appendChild(header);

    const grid = document.createElement("div");
    grid.className = "labelling-overlay__cards-row";

    if (!other.cards || other.cards.length === 0) {
      const empty = document.createElement("span");
      empty.className = "labelling-overlay__other-empty";
      empty.textContent = "Aucune carte";
      grid.appendChild(empty);
    } else {
      other.cards.forEach((card, cIdx) => {
        const el = buildCardEl(card, {
          selected: pIdx === otherPlayerIndex && cIdx === otherCardIndex,
          onClick: () => {
            otherPlayerIndex = pIdx;
            otherCardIndex = cIdx;
            // Ne garder qu'une seule carte sélectionnée parmi TOUS les autres joueurs
            othersList.querySelectorAll("game-card").forEach((c) => {
              c.removeAttribute("selected");
              c.setAttribute("aria-selected", "false");
            });
            el.setAttribute("selected", "");
            el.setAttribute("aria-selected", "true");
            updateConfirmState();
          },
        });
        grid.appendChild(el);
      });
    }

    row.appendChild(grid);
    othersList.appendChild(row);
  });

  updateConfirmState();

  // ── Confirmation ────────────────────────────────────────────────────────
  confirmBtn.onclick = () => {
    if (confirmBtn.disabled) return;
    overlay.hidden = true;
    overlay.dataset.signature = "";
    onSubmit({
      owner_index: ownerIndex,
      other_player_index: otherPlayerIndex,
      other_card_index: otherCardIndex,
    });
  };

  // ⚠️ Ne PAS retourner `overlay` ici : io-core.js ferait
  // container.appendChild(overlay), ce qui déplacerait ce modal
  // autonome (déjà positionné dans <body>) à l'intérieur de
  // #io-container, lui-même imbriqué dans #io-overlay.hidden.
  // Résultat : l'overlay devient invisible malgré overlay.hidden = false.
  return null;
}

registerHandler("error-labelling", renderErrorLabelling);