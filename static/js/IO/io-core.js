import { getHandler } from "./io-registry.js";

import "../components/card-game.js";
// Importer les handlers suffit à les enregistrer
import "./handlers/card-detail.js";
import "./handlers/salary-selector.js";
import "./handlers/card-browser.js";
import "./handlers/show-hand.js";
import "./handlers/card-picker.js";
import "./handlers/player-picker.js"

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
  await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ index }),
  });
  poll();
}

async function submitIndices(indices) {
  await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/submit-indices`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ indices }),
  });
  poll();
}

async function submitDismiss() {
  await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/dismiss`, { method: "POST" });
  poll();
}

async function poll() {
  let pending = null;
  try {
    const res = await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/pending`);
    if (!res.ok) {
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
    setTimeout(poll, 500);
    return;
  }

  const container = document.getElementById("io-container");
  if (container) {
    container.innerHTML = "";
    const onSubmit = 
      pending.ui_component === "salary-selector" ? submitIndices : 
      pending.ui_component === "card-browser"    ? submitDismiss :
      pending.ui_component === "show-hand"       ? submitDismiss :
      submit;
    container.appendChild(render({ ...pending, onSubmit }));
  }

  // Continuer à poller — un nouveau pending peut arriver après la fermeture de l'overlay
  setTimeout(poll, 500);
}

poll();