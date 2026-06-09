import { registerHandler } from "../io-registry.js";
import { getActionsForCard } from "./card-actions.js";

const VARIANT_CLASS = {
  primary: "card-detail-overlay__btn--primary",
  danger:  "card-detail-overlay__btn--danger",
  ghost:   "card-detail-overlay__btn--ghost",
  warning: "card-detail-overlay__btn--warning",
  success: "card-detail-overlay__btn--success",
};

registerHandler("card-detail", function render(pending) {
  const { card, context, is_my_turn, game_id } = pending;

  // 1. Cibler l'overlay directement dans le DOM (injecté par card-detail.html)
  const overlay = document.getElementById("card-detail-overlay");
  if (!overlay) {
    console.error("L'élément #card-detail-overlay est introuvable.");
    return;
  }

  // 2. Cibler les éléments internes par id/classe
  const img        = overlay.querySelector(".card-detail-overlay__img");
  const typeEl     = document.getElementById("card-detail-type");
  const nameEl     = document.getElementById("card-detail-title");
  const smilesEl   = document.getElementById("card-detail-smiles");
  const descEl     = document.getElementById("card-detail-description");
  const actionsEl  = document.getElementById("card-detail-actions");
  const toast      = document.getElementById("card-detail-toast");

  // Fonctions utilitaires
  function closeOverlay() {
    overlay.classList.add("cd-closing");
    overlay.addEventListener("animationend", () => {
      overlay.classList.remove("cd-closing");
      overlay.hidden = true;
    }, { once: true });
  }

  function showError(msg) {
    if (toast) {
      toast.textContent = msg;
      toast.classList.add("card-detail-overlay__toast--visible");
    }
  }

  // 3. Réinitialiser l'état avant de remplir (réutilisation de l'overlay)
  if (toast) {
    toast.textContent = "";
    toast.classList.remove("card-detail-overlay__toast--visible");
  }
  if (actionsEl) actionsEl.innerHTML = "";

  // Fermeture sur clic backdrop
  const backdrop = overlay.querySelector(".card-detail-overlay__backdrop");
  if (backdrop) {
    backdrop.onclick = closeOverlay;
  }

  // 4. Remplir les données texte et image
  if (nameEl) nameEl.textContent = card.name || "—";
  if (typeEl) typeEl.textContent = card.type || "";
  if (smilesEl) smilesEl.textContent = card.smiles ?? 0;

  if (descEl) {
    descEl.textContent = card.description || "";
    descEl.style.display = card.description ? "" : "none";
  }

  if (img) {
    if (card.image_path) {
      img.src = `/static/${card.image_path}`;
      img.alt = card.name || "";
      img.style.display = "";
    } else {
      img.style.display = "none";
    }
  }

  // 5. Générer et injecter les boutons d'action
  const actions = getActionsForCard(card, context, is_my_turn);
  actions.forEach((action) => {
    const btn = document.createElement("button");
    btn.className = `card-detail-overlay__btn ${VARIANT_CLASS[action.variant] ?? "card-detail-overlay__btn--ghost"}`;
    btn.textContent = action.label;
    btn.type = "button";

    btn.addEventListener("click", async () => {
      if (action.confirm && !window.confirm(action.confirm)) return;

      btn.disabled = true;
      btn.classList.add("card-detail-overlay__btn--loading");

      const { url, body } = action.endpoint(card, game_id);

      await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(async (res) => {
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.error || "Erreur serveur");

        closeOverlay();
        if (typeof window.refreshGameState === "function") window.refreshGameState();
      }).catch((err) => {
        btn.disabled = false;
        btn.classList.remove("card-detail-overlay__btn--loading");
        showError(err.message);
      });
    });

    actionsEl.appendChild(btn);
  });

  // Toujours ajouter le bouton Fermer
  const closeBtn = document.createElement("button");
  closeBtn.className = "card-detail-overlay__btn card-detail-overlay__btn--ghost";
  closeBtn.textContent = "✕ Fermer";
  closeBtn.type = "button";
  closeBtn.addEventListener("click", closeOverlay);
  actionsEl.appendChild(closeBtn);

  // 6. Afficher l'overlay
  overlay.hidden = false;
  return document.createDocumentFragment();
});