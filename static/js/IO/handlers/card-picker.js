import { registerHandler } from "../io-registry.js";
import { getHandler }      from "../io-registry.js";

registerHandler("card-picker", function render(pending) {
  const overlay = document.getElementById("card-picker-overlay");
  if (!overlay) {
    console.error("[card-picker] #card-picker-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  if (overlay.classList.contains("card-picker-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const { options = [], prompt = "", nb = null, onSubmit } = pending;
  const isMulti = nb != null && nb > 1;
  const requiredCount = nb ?? 1;

  const grid       = overlay.querySelector("#card-picker-grid");
  const promptText = overlay.querySelector("#card-picker-prompt");
  const hintText   = overlay.querySelector(".card-picker-overlay__hint");
  let confirmBtn = overlay.querySelector("#card-picker-confirm-btn");
  const countEl    = overlay.querySelector("#card-picker-count");

  if (promptText) promptText.textContent = prompt;
  if (countEl)    countEl.textContent    = options.length;
  if (hintText) {
    hintText.textContent = isMulti
      ? `Sélectionnez jusqu'à ${requiredCount} carte${requiredCount > 1 ? "s" : ""} (au moins 1).`
      : "Cliquez sur une carte pour la sélectionner.";
  }

  // ── État de sélection ───────────────────────────────────────────────
  // Mode single : selectedIndex (nombre | null) — comportement historique.
  // Mode multi  : selectedIndices (Set) — jusqu'à requiredCount éléments.
  let selectedIndex = null;
  const selectedIndices = new Set();

  function updateConfirmState() {
    if (!confirmBtn) return;
    // Mode multi : on peut valider dès qu'au moins 1 carte est sélectionnée,
    // sans être obligé d'atteindre requiredCount (sélection "jusqu'à N").
    const ready = isMulti
      ? selectedIndices.size > 0
      : selectedIndex !== null;
    confirmBtn.disabled = !ready;
    confirmBtn.classList.toggle("card-picker-overlay__btn--ready", ready);
  }

  // ── Rendu des cartes ──────────────────────────────────────────────────
  function renderCards() {
    if (!grid) return;
    grid.innerHTML = "";

    options.forEach((card, idx) => {
      const el = GameCard.create(card, {
        context:    "other",
        size:       "salary",
        selectable: true,
        clickable:  true,
      });
      el.dataset.index = idx;
      el.setAttribute("role", "option");
      el.setAttribute("aria-selected", "false");
      el.setAttribute("aria-label", card.name ?? "Carte");
      el.setAttribute("tabindex", "0");

      el.addEventListener("card-click", () => selectCard(idx));
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectCard(idx);
        }
      });

      grid.appendChild(el);
    });
  }

  // ── Sélection ─────────────────────────────────────────────────────────
  function selectCard(idx) {
    if (isMulti) {
      if (selectedIndices.has(idx)) {
        selectedIndices.delete(idx);
      } else if (selectedIndices.size < requiredCount) {
        selectedIndices.add(idx);
      }
      // si le quota est déjà atteint et qu'on clique sur une carte non
      // sélectionnée, on ignore le clic (il faut d'abord en déselectionner une)

      grid?.querySelectorAll("game-card").forEach((el) => {
        const i = parseInt(el.dataset.index, 10);
        const isSelected = selectedIndices.has(i);
        el.toggleAttribute("selected", isSelected);
        el.setAttribute("aria-selected", String(isSelected));
      });

      if (countEl) countEl.textContent = `${selectedIndices.size}/${requiredCount}`;
    } else {
      selectedIndex = idx;
      grid?.querySelectorAll("game-card").forEach((el) => {
        const isSelected = parseInt(el.dataset.index, 10) === idx;
        el.toggleAttribute("selected", isSelected);
        el.setAttribute("aria-selected", String(isSelected));
      });
    }

    updateConfirmState();
  }

  // ── Ouvrir card-detail en lecture seule ───────────────────────────────
  function openCardDetail(card) {
    const handler = getHandler("card-detail");
    if (!handler) {
      console.error("[card-picker] Handler card-detail introuvable.");
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

  // ── Confirmation ──────────────────────────────────────────────────────
  function handleConfirm() {
    if (isMulti) {
      if (selectedIndices.size === 0) return;
      const indicesToSubmit = [...selectedIndices];
      closeOverlay();
      if (typeof onSubmit === "function") onSubmit(indicesToSubmit);
    } else {
      if (selectedIndex === null) return;
      const indexToSubmit = selectedIndex;
      closeOverlay();
      if (typeof onSubmit === "function") onSubmit(indexToSubmit);
    }
  }

  // ── Fermeture ─────────────────────────────────────────────────────────
  function closeOverlay() {
    overlay.classList.remove("card-picker-overlay--visible");
    overlay.addEventListener(
      "transitionend",
      () => overlay.setAttribute("hidden", ""),
      { once: true }
    );
    document.removeEventListener("keydown", handleKey);
    selectedIndex = null;
    selectedIndices.clear();
    if (confirmBtn) confirmBtn.disabled = true;
  }

  function handleKey(e) {
    if (!overlay.classList.contains("card-picker-overlay--visible")) return;
    if (e.key === "Escape") { closeOverlay(); return; }

    // Trap focus
    const focusable = [
      ...overlay.querySelectorAll("game-card[tabindex], button:not([disabled])"),
    ];
    if (!focusable.length) return;
    const first = focusable[0];
    const last  = focusable[focusable.length - 1];
    if (e.key === "Tab") {
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    }
  }

  // ── Montage ───────────────────────────────────────────────────────────

  // Fermer tout overlay card-detail ouvert
  document.querySelectorAll(".cd-overlay").forEach(el => {
    el.classList.add("cd-closing");
    el.addEventListener("animationend", () => el.remove(), { once: true });
  });

  renderCards();
  if (isMulti && countEl) countEl.textContent = `0/${requiredCount}`;

  // Purge les anciens listeners sur le bouton confirm
  if (confirmBtn) {
    const freshBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(freshBtn, confirmBtn);
    freshBtn.disabled = true;
    freshBtn.addEventListener("click", handleConfirm);
    confirmBtn = freshBtn;
  }

  document.removeEventListener("keydown", handleKey);
  document.addEventListener("keydown", handleKey);

  overlay.removeAttribute("hidden");
  requestAnimationFrame(() => overlay.classList.add("card-picker-overlay--visible"));
  grid?.querySelector("game-card")?.focus();

  return document.createDocumentFragment();
});