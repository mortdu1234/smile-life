import { getHandler } from "./io-registry.js";

import "../components/card-game.js";
// Importer les handlers suffit à les enregistrer
import "./handlers/card-detail.js";
import "./handlers/salary-selector.js";
import "./handlers/card-browser.js";
import "./handlers/show-hand.js";
import "./handlers/card-picker.js";
import "./handlers/player-picker.js";
import "./handlers/error-labelling.js";

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
//
// Garde-fous anti-course :
//  - `pollTimer`     : le seul setTimeout actif à un instant donné (jamais deux
//                       chaînes de polling en parallèle).
//  - `pollGeneration` : incrémenté à chaque submit. Toute réponse /pending déjà
//                       "en vol" au moment du submit devient obsolète et est
//                       ignorée si elle revient après coup (empêche l'overlay
//                       de se rouvrir juste après confirmation).
let pollTimer = null;
let pollGeneration = 0;

function schedulePoll(delay) {
  clearTimeout(pollTimer);
  pollTimer = setTimeout(poll, delay);
}

async function submit(index) {
  pollGeneration++;
  await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ index }),
  });
  schedulePoll(0);
}

async function submitIndices(indices) {
  pollGeneration++;
  await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/submit-indices`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ indices }),
  });
  schedulePoll(0);
}

async function submitDismiss() {
  pollGeneration++;
  await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/dismiss`, { method: "POST" });
  schedulePoll(0);
}

async function submitErrorLabelling(selection) {
  // Le backend (WebIO.erreur_detiquetage_interface) attend une liste
  // [owner_index, other_player_index, other_card_index] via la route
  // générique /submit-indices — il n'y a pas de route dédiée.
  const { owner_index, other_player_index, other_card_index } = selection;
  await submitIndices([owner_index, other_player_index, other_card_index]);
}

async function poll() {
  const myGeneration = pollGeneration;

  let pending = null;
  try {
    const res = await fetch(`${window.BASE_URL}/game/${window.GAME_ID}/pending`);
    if (myGeneration !== pollGeneration) return; // un submit a eu lieu entre-temps : réponse obsolète
    if (!res.ok) {
      schedulePoll(2000);
      return;
    }
    const data = await res.json();
    if (myGeneration !== pollGeneration) return;
    pending = data.pending;
  } catch (e) {
    if (myGeneration !== pollGeneration) return;
    schedulePoll(2000);
    return;
  }

  if (!pending) {
    schedulePoll(500);
    return;
  }

  const render = getHandler(pending.ui_component);
  if (!render) {
    console.error(`Handler introuvable : ${pending.ui_component}`);
    schedulePoll(500);
    return;
  }

  try {
    const container = document.getElementById("io-container");
    if (container) {
      container.innerHTML = "";
      const onSubmit = 
        pending.ui_component === "salary-selector" ? submitIndices : 
        pending.ui_component === "card-browser"    ? submitDismiss :
        pending.ui_component === "show-hand"       ? submitDismiss :
        pending.ui_component === "error-labelling" ? submitErrorLabelling :
        submit;
      const el = render({ ...pending, onSubmit });
      if (el) {
        container.appendChild(el);
      }
      // Certains handlers (ex: error-labelling) pilotent un overlay
      // autonome déjà présent dans le <body> et retournent `null`
      // volontairement : rien à faire ici, ce n'est pas une erreur.
    }
  } catch (e) {
    // Une erreur ici (ex: élément attendu absent du DOM) ne doit pas
    // arrêter le polling pour le reste de la session.
    console.error(`Erreur lors du rendu de ${pending.ui_component} :`, e);
  }

  // Continuer à poller — un nouveau pending peut arriver après la fermeture de l'overlay
  schedulePoll(500);
}

poll();