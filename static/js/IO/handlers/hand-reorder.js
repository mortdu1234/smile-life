import { registerHandler } from "../io-registry.js";
import { getHandler }      from "../io-registry.js";

registerHandler("hand-reorder", function render(pending) {
  const overlay = document.getElementById("hand-reorder-overlay");
  if (!overlay) {
    console.error("[hand-reorder] #hand-reorder-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  if (overlay.classList.contains("hand-reorder-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const { players_names = [], hands = [], prompt = "", onSubmit } = pending;

  const columnsEl  = overlay.querySelector("#hand-reorder-columns");
  const promptText = overlay.querySelector("#hand-reorder-prompt");
  let confirmBtn   = overlay.querySelector("#hand-reorder-confirm-btn");

  if (promptText) promptText.textContent = prompt;

  // Nombre de cartes de départ par joueur (index = playerIdx) : la
  // réorganisation doit préserver ces effectifs, seul l'ordre/l'attribution
  // des cartes elles-mêmes peut changer.
  const originalCounts = players_names.map((_, idx) => (hands[idx] ?? []).length);

  // ── État du drag en cours (une seule carte à la fois) ──────────────────
  let draggedCard = null;

  function updateCount(dropzone) {
    const column = dropzone.closest(".hand-reorder-column");
    const countEl = column?.querySelector(".hand-reorder-column__count");
    const cards = dropzone.querySelectorAll("game-card").length;
    
    // Affichage dynamique : "3/6 cartes"
    const playerIdx = Number(dropzone.dataset.player);
    const expected = originalCounts[playerIdx] ?? 0;
    if (countEl) {
      countEl.textContent = `${cards}/${expected}`;
      // Mise en couleur : rouge si mismatch, vert si correct
      countEl.classList.toggle("hand-reorder-column__count--mismatch", cards !== expected);
    }

    let emptyEl = dropzone.querySelector(".hand-reorder-column__empty");
    if (cards === 0 && !emptyEl) {
      emptyEl = document.createElement("p");
      emptyEl.className = "hand-reorder-column__empty";
      emptyEl.textContent = "Main vide";
      dropzone.appendChild(emptyEl);
    } else if (cards > 0 && emptyEl) {
      emptyEl.remove();
    }

    refreshValidation();
  }

  // ── Validation : le nb de cartes par joueur doit rester inchangé ───────
  // Retourne true/false et met à jour l'UI (surbrillance des colonnes en
  // écart + désactivation du bouton confirmer) en conséquence.
  function refreshValidation() {
    if (!columnsEl) return true;
    const dropzones = [...columnsEl.querySelectorAll(".hand-reorder-column__dropzone")];

    let allValid = true;
    dropzones.forEach((dz) => {
      const idx      = Number(dz.dataset.player);
      const count    = dz.querySelectorAll("game-card").length;
      const expected = originalCounts[idx] ?? 0;
      const valid    = count === expected;
      if (!valid) allValid = false;

      const column  = dz.closest(".hand-reorder-column");
      column?.classList.toggle("hand-reorder-column--mismatch", !valid);
    });

    // Mise à jour du bouton avec rétroaction visuelle
    if (confirmBtn) {
      confirmBtn.disabled = !allValid;
      confirmBtn.classList.toggle("is-disabled", !allValid);
      confirmBtn.title = allValid
        ? "Cliquez pour confirmer la réorganisation"
        : "❌ Chaque joueur doit retrouver son nombre initial de cartes avant de valider.";
      
      // Changement du texte si invalide (optionnel mais très visible)
      const originalText = "Confirmer";
      confirmBtn.textContent = allValid ? originalText : "⚠️ Effectifs déséquilibrés";
    }

    return allValid;
  }

  // Détermine où insérer la carte déposée en comparant sa position au
  // centre des cartes déjà présentes dans la dropzone cible.
  function findInsertTarget(dropzone, clientX, clientY) {
    const cards = [...dropzone.querySelectorAll("game-card:not(.is-dragging)")];
    let closest = null;
    let closestDist = Infinity;
    let insertBefore = true;

    for (const card of cards) {
      const box = card.getBoundingClientRect();
      const cx = box.left + box.width / 2;
      const cy = box.top + box.height / 2;
      const dist = Math.hypot(clientX - cx, clientY - cy);
      if (dist < closestDist) {
        closestDist = dist;
        closest = card;
        insertBefore = clientX < cx;
      }
    }
    return { closest, insertBefore };
  }

  function openCardDetail(card) {
    const handler = getHandler("card-detail");
    if (!handler) {
      console.error("[hand-reorder] Handler card-detail introuvable.");
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

  // ── Construction des colonnes ────────────────────────────────────────
  function buildCardEl(card, playerIdx, cardIdx) {
    const el = GameCard.create(card, {
      context:    "other",
      size:       "salary",
      selectable: false,
      clickable:  false,
    });
    el.dataset.originPlayer = playerIdx;
    el.dataset.originCard   = cardIdx;
    el.draggable = true;
    el.setAttribute("aria-label", card.name ?? "Carte");

    el.addEventListener("dragstart", (e) => {
      draggedCard = el;
      el.classList.add("is-dragging");
      e.dataTransfer.effectAllowed = "move";
      // Nécessaire pour Firefox, qui exige des données pour démarrer le drag.
      e.dataTransfer.setData("text/plain", "");
    });
    el.addEventListener("dragend", () => {
      el.classList.remove("is-dragging");
      draggedCard = null;
    });
    el.addEventListener("dblclick", () => openCardDetail(card));

    return el;
  }

  function buildColumn(playerName, playerIdx, hand) {
    const isMe = window.PLAYER_NAME != null && playerName === window.PLAYER_NAME;

    const column = document.createElement("div");
    column.className = "hand-reorder-column" + (isMe ? " is-me" : "");

    const header = document.createElement("div");
    header.className = "hand-reorder-column__header";
    header.innerHTML = `
      <span class="hand-reorder-column__avatar">${(playerName || "?").slice(0, 1).toUpperCase()}</span>
      <span class="hand-reorder-column__name">${playerName}</span>
      <span class="hand-reorder-column__count">${hand.length}/${hand.length}</span>
    `;
    column.appendChild(header);

    const dropzone = document.createElement("div");
    dropzone.className = "hand-reorder-column__dropzone";
    dropzone.dataset.player = playerIdx;

    hand.forEach((card, cardIdx) => {
      dropzone.appendChild(buildCardEl(card, playerIdx, cardIdx));
    });
    if (hand.length === 0) {
      const emptyEl = document.createElement("p");
      emptyEl.className = "hand-reorder-column__empty";
      emptyEl.textContent = "Main vide";
      dropzone.appendChild(emptyEl);
    }

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
    });
    dropzone.addEventListener("dragenter", (e) => {
      e.preventDefault();
      dropzone.classList.add("is-dragover");
    });
    dropzone.addEventListener("dragleave", (e) => {
      if (!dropzone.contains(e.relatedTarget)) {
        dropzone.classList.remove("is-dragover");
      }
    });
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("is-dragover");
      if (!draggedCard) return;

      const sourceDropzone = draggedCard.parentElement;
      const { closest, insertBefore } = findInsertTarget(dropzone, e.clientX, e.clientY);

      if (closest) {
        dropzone.insertBefore(draggedCard, insertBefore ? closest : closest.nextSibling);
      } else {
        dropzone.appendChild(draggedCard);
      }

      updateCount(dropzone);
      if (sourceDropzone && sourceDropzone !== dropzone) updateCount(sourceDropzone);
    });

    column.appendChild(dropzone);
    return column;
  }

  // ── Fermeture ─────────────────────────────────────────────────────────
  function closeOverlay() {
    overlay.classList.remove("hand-reorder-overlay--visible");
    overlay.addEventListener(
      "transitionend",
      () => overlay.setAttribute("hidden", ""),
      { once: true }
    );
  }

  // ── Confirmation : lit l'ordre final des cartes dans le DOM ────────────
  function handleConfirm() {
    if (!refreshValidation()) return; // sécurité : effectifs déséquilibrés

    const dropzones = [...columnsEl.querySelectorAll(".hand-reorder-column__dropzone")]
      .sort((a, b) => Number(a.dataset.player) - Number(b.dataset.player));

    const newHands = dropzones.map((dz) =>
      [...dz.querySelectorAll("game-card")].map((el) => ({
        player: Number(el.dataset.originPlayer),
        card:   Number(el.dataset.originCard),
      }))
    );

    closeOverlay();
    if (typeof onSubmit === "function") onSubmit(newHands);
  }

  // ── Montage ───────────────────────────────────────────────────────────
  if (columnsEl) {
    columnsEl.innerHTML = "";
    players_names.forEach((name, idx) => {
      columnsEl.appendChild(buildColumn(name, idx, hands[idx] ?? []));
    });
  }

  if (confirmBtn) {
    const freshBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(freshBtn, confirmBtn);
    freshBtn.addEventListener("click", handleConfirm);
    confirmBtn = freshBtn;
  }

  refreshValidation();

  overlay.removeAttribute("hidden");
  requestAnimationFrame(() => overlay.classList.add("hand-reorder-overlay--visible"));

  return document.createDocumentFragment();
});