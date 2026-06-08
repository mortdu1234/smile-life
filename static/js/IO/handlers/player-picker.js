import { registerHandler } from "../io-registry.js";

registerHandler("player-picker", function render(pending) {
  const overlay = document.getElementById("player-picker-overlay");
  if (!overlay) {
    console.error("[player-picker] #player-picker-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  if (overlay.classList.contains("player-picker-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const { options = [], prompt = "", onSubmit } = pending;

  const list       = overlay.querySelector("#player-picker-list");
  const promptText = overlay.querySelector("#player-picker-prompt");
  let   confirmBtn = overlay.querySelector("#player-picker-confirm-btn");
  const countEl    = overlay.querySelector("#player-picker-count");

  if (promptText) promptText.textContent = prompt;
  if (countEl)    countEl.textContent    = options.length;

  let selectedIndex = null;

  // ── Rendu de la liste ─────────────────────────────────────────────────
  function renderPlayers() {
    if (!list) return;
    list.innerHTML = "";

    options.forEach((player, idx) => {
      const name = player.name ?? `Joueur ${idx + 1}`;

      const item = document.createElement("div");
      item.className = "player-picker-item";
      item.setAttribute("role", "option");
      item.setAttribute("aria-selected", "false");
      item.setAttribute("tabindex", "0");
      item.dataset.index = idx;

      item.innerHTML = `
        <div class="player-picker-item__avatar">${name[0]?.toUpperCase() ?? "?"}</div>
        <span class="player-picker-item__name">${name}</span>
        <span class="player-picker-item__check" aria-hidden="true">✓</span>
      `;

      item.addEventListener("click", () => selectPlayer(idx));
      item.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectPlayer(idx);
        }
      });

      list.appendChild(item);
    });
  }

  // ── Sélection ─────────────────────────────────────────────────────────
  function selectPlayer(idx) {
    selectedIndex = idx;

    list?.querySelectorAll(".player-picker-item").forEach((el) => {
      const isSelected = parseInt(el.dataset.index, 10) === idx;
      el.setAttribute("aria-selected", String(isSelected));
    });

    if (confirmBtn) {
      confirmBtn.disabled = false;
    }
  }

  // ── Confirmation ──────────────────────────────────────────────────────
  function handleConfirm() {
    if (selectedIndex === null) return;
    const indexToSubmit = selectedIndex;
    closeOverlay();
    if (typeof onSubmit === "function") onSubmit(indexToSubmit);
  }

  // ── Fermeture ─────────────────────────────────────────────────────────
  function closeOverlay() {
    overlay.classList.remove("player-picker-overlay--visible");
    overlay.addEventListener(
      "transitionend",
      () => overlay.setAttribute("hidden", ""),
      { once: true }
    );
    document.removeEventListener("keydown", handleKey);
    selectedIndex = null;
    if (confirmBtn) confirmBtn.disabled = true;
  }

  function handleKey(e) {
    if (!overlay.classList.contains("player-picker-overlay--visible")) return;

    const items = [...(list?.querySelectorAll(".player-picker-item") ?? [])];
    const currentIdx = items.findIndex(el => el === document.activeElement);

    if (e.key === "ArrowDown") {
      e.preventDefault();
      items[(currentIdx + 1) % items.length]?.focus();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      items[(currentIdx - 1 + items.length) % items.length]?.focus();
    } else if (e.key === "Escape") {
      closeOverlay();
    } else if (e.key === "Tab") {
      // Trap focus
      const focusable = [
        ...overlay.querySelectorAll(".player-picker-item, button:not([disabled])"),
      ];
      if (!focusable.length) return;
      const first = focusable[0];
      const last  = focusable[focusable.length - 1];
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

  renderPlayers();

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
  requestAnimationFrame(() => overlay.classList.add("player-picker-overlay--visible"));
  list?.querySelector(".player-picker-item")?.focus();

  return document.createDocumentFragment();
});