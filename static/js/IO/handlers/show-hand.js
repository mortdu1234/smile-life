import { registerHandler } from "../io-registry.js";
import { getHandler }      from "../io-registry.js";

registerHandler("show-hand", function render(pending) {
  const overlay = document.getElementById("show-hand-overlay");
  if (!overlay) {
    console.error("[show-hand] #show-hand-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  if (overlay.classList.contains("show-hand-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const {
    players_names = [],
    players_hands = [],
    prompt        = "",
    title         = "Mains révélées",
    onSubmit,
  } = pending;

  const body      = overlay.querySelector("#show-hand-body");
  const promptText = overlay.querySelector("#show-hand-prompt");
  const titleEl   = overlay.querySelector("#show-hand-title");
  const closeBtn  = overlay.querySelector("#show-hand-close-btn");
  const countEl   = overlay.querySelector("#show-hand-count");

  if (titleEl)    titleEl.textContent   = title;
  if (promptText) promptText.textContent = prompt;
  if (countEl)    countEl.textContent   = players_names.length;

  // ── Rendu des sections joueurs ────────────────────────────────────────
  function renderPlayers() {
    if (!body) return;
    body.innerHTML = "";

    players_names.forEach((name, playerIdx) => {
      const hand = players_hands[playerIdx] ?? [];

      const section = document.createElement("div");
      section.className = "show-hand-player";

      // Header joueur
      const header = document.createElement("div");
      header.className = "show-hand-player__header";

      const avatar = document.createElement("div");
      avatar.className = "show-hand-player__avatar";
      avatar.textContent = name[0]?.toUpperCase() ?? "?";

      const nameEl = document.createElement("span");
      nameEl.className = "show-hand-player__name";
      nameEl.textContent = name;

      const countBadge = document.createElement("span");
      countBadge.className = "show-hand-player__count";
      countBadge.textContent = `${hand.length} carte${hand.length !== 1 ? "s" : ""}`;

      header.appendChild(avatar);
      header.appendChild(nameEl);
      header.appendChild(countBadge);
      section.appendChild(header);

      // Grille de cartes
      if (hand.length === 0) {
        const empty = document.createElement("p");
        empty.className = "show-hand-player__empty";
        empty.textContent = "Aucune carte en main.";
        section.appendChild(empty);
      } else {
        const grid = document.createElement("div");
        grid.className = "show-hand-player__grid";

        hand.forEach((card) => {
          const el = GameCard.create(card, {
            context:   "other",
            size:      "salary",
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

        section.appendChild(grid);
      }

      body.appendChild(section);
    });
  }

  // ── Ouvrir card-detail en lecture seule ───────────────────────────────
  function openCardDetail(card) {
    const handler = getHandler("card-detail");
    if (!handler) {
      console.error("[show-hand] Handler card-detail introuvable.");
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
    overlay.classList.remove("show-hand-overlay--visible");
    overlay.addEventListener(
      "transitionend",
      () => overlay.setAttribute("hidden", ""),
      { once: true }
    );
    document.removeEventListener("keydown", handleKey);
    if (typeof onSubmit === "function") onSubmit();
  }

  function handleKey(e) {
    if (!overlay.classList.contains("show-hand-overlay--visible")) return;
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

  renderPlayers();

  // Purge les anciens listeners sur le bouton en le remplaçant par un clone
  if (closeBtn) {
    const freshBtn = closeBtn.cloneNode(true);
    closeBtn.parentNode.replaceChild(freshBtn, closeBtn);
    freshBtn.addEventListener("click", closeOverlay);
  }

  document.removeEventListener("keydown", handleKey);
  document.addEventListener("keydown", handleKey);

  overlay.removeAttribute("hidden");
  requestAnimationFrame(() => overlay.classList.add("show-hand-overlay--visible"));
  body?.querySelector("game-card")?.focus();

  return document.createDocumentFragment();
});