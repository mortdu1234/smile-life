import { getHandler } from "./io-registry.js";

// Importer les handlers suffit à les enregistrer
import "./handlers/player-selector.js";
import "./handlers/card-grid.js";
import "./handlers/hardship-target.js";
import "./handlers/card-detail.js";

// ── Expose openCard globalement pour board.html ───────────────────────────────
window.openCard = function(card, context) {
  const handler = getHandler("card-detail");
  if (!handler) {
    console.error("Handler card-detail introuvable");
    return;
  }
  const overlay = handler({
    card,
    context,
    is_my_turn: window.IS_MY_TURN ?? false,
    game_id: window.GAME_ID ?? "",
  });
  document.body.appendChild(overlay);
};

// ── IO polling (pour les actions nécessitant un choix joueur) ────────────────
async function submit(index) {
  await fetch("/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ index }),
  });
  poll();
}

async function poll() {
  let pending = null;
  try {
    const res = await fetch("/pending");
    if (!res.ok) {
      // Route /pending pas encore implémentée — on reessaie plus tard
      setTimeout(poll, 2000);
      return;
    }
    const data = await res.json();
    pending = data.pending;
  } catch (e) {
    setTimeout(poll, 2000);
    return;
  }

  if (!pending) {
    setTimeout(poll, 500);
    return;
  }

  const render = getHandler(pending.ui_component);
  if (!render) {
    console.error(`Handler introuvable : ${pending.ui_component}`);
    return;
  }

  const container = document.getElementById("io-container");
  if (container) {
    container.innerHTML = "";
    container.appendChild(render({ ...pending, onSubmit: submit }));
  }
}

poll();