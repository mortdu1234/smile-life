import { registerHandler } from "../io-registry.js";
import { getHandler }      from "../io-registry.js";

registerHandler("card-browser", function render(pending) {
  const overlay = document.getElementById("card-browser-overlay");
  if (!overlay) {
    console.error("[card-browser] #card-browser-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  if (overlay.classList.contains("card-browser-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const { cards = [], prompt = "", title = "Cartes disponibles" } = pending;

  const grid       = overlay.querySelector("#card-browser-grid");
  const promptText = overlay.querySelector("#card-browser-prompt");
  const titleEl    = overlay.querySelector("#card-browser-title");
  const closeBtn   = overlay.querySelector("#card-browser-close-btn");
  const countEl    = overlay.querySelector("#card-browser-count");

  if (titleEl)    titleEl.textContent  = title;
  if (promptText) promptText.textContent = prompt;
  if (countEl)    countEl.textContent  = cards.length;

  // ── Rendu des cartes ──────────────────────────────────────────────────
  function renderCards() {
    console.log("open render cards");
    if (!grid) return;
    grid.innerHTML = "";
    cards.forEach((card) => {
      const el = GameCard.create(card, {
        context:   "other",
        size:      "salary",   // taille confortable pour la consultation
        clickable: true,
      });
      el.setAttribute("aria-label", card.name ?? "Carte");
      el.setAttribute("tabindex", "0");

      el.addEventListener("card-click", () => openCardDetail(card));
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openCardDetail(card);
        }
      });

      grid.appendChild(el);
    });
  }

  // ── Ouvrir card-detail en lecture seule ───────────────────────────────
  function openCardDetail(card) {
    const handler = getHandler("card-detail");
    if (!handler) {
      console.error("[card-browser] Handler card-detail introuvable.");
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

  // ── Fermeture ─────────────────────────────────────────────────────────
    function closeOverlay() {
    overlay.classList.remove("card-browser-overlay--visible");
    overlay.addEventListener(
        "transitionend",
        () => overlay.setAttribute("hidden", ""),
        { once: true }
    );
    document.removeEventListener("keydown", handleKey);
    pending.onSubmit();
    }

  function handleKey(e) {
    if (!overlay.classList.contains("card-browser-overlay--visible")) return;
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
    document.querySelectorAll(".cd-overlay").forEach(el => {
        el.classList.add("cd-closing");
        el.addEventListener("animationend", () => el.remove(), { once: true });
    });

    renderCards();

  // Purge les anciens listeners sur le bouton en le remplaçant par un clone
  if (closeBtn) {
    const freshBtn = closeBtn.cloneNode(true);
    closeBtn.parentNode.replaceChild(freshBtn, closeBtn);
    freshBtn.addEventListener("click", closeOverlay);
  }

  // Retire tout listener keydown précédent avant d'en ajouter un nouveau
  document.removeEventListener("keydown", handleKey);
  document.addEventListener("keydown", handleKey);

  overlay.removeAttribute("hidden");
  requestAnimationFrame(() => overlay.classList.add("card-browser-overlay--visible"));
  grid?.querySelector("game-card")?.focus();

  return document.createDocumentFragment();
});