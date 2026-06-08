import { registerHandler } from "../io-registry.js";
import { getHandler }      from "../io-registry.js";

registerHandler("salary-selector", function render(pending) {
  const overlay = document.getElementById("salary-overlay");
  if (!overlay) {
    console.error("[salary-selector] #salary-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  if (overlay.classList.contains("salary-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const { cards = [], cost = 0, prompt = "", onSubmit } = pending;

  const selected      = new Set();
  const selectedTotal = () => [...selected].reduce((sum, i) => sum + (cards[i]?.value ?? 0), 0);
  const isEnough      = () => selectedTotal() >= cost;

  // ── Refs DOM ──────────────────────────────────────────────────────────
  const grid        = overlay.querySelector("#salary-cards-grid");
  const progressBar = overlay.querySelector("#salary-progress-bar");
  const promptText  = overlay.querySelector("#salary-prompt-text");
  const costEl      = overlay.querySelector("#salary-required-cost");
  const selectedTot = overlay.querySelector("#salary-selected-total");
  const neededTot   = overlay.querySelector("#salary-needed-total");
  const confirmBtn  = overlay.querySelector("#salary-confirm-btn");
  const cancelBtn   = overlay.querySelector("#salary-cancel-btn");
  const infoToggle  = overlay.querySelector("#salary-info-toggle");

  if (promptText) promptText.textContent = prompt;
  if (costEl)     costEl.textContent     = cost;
  if (neededTot)  neededTot.textContent  = cost;

  // ── État du mode "plus d'info" ────────────────────────────────────────
  let infoMode = false;

  function setInfoMode(val) {
    infoMode = val;
    if (!infoToggle) return;
    infoToggle.setAttribute("aria-pressed", String(val));
    infoToggle.classList.toggle("salary-overlay__info-toggle--active", val);
    // Curseur sur la grille : loupe si info, pointeur sinon
    if (grid) grid.classList.toggle("salary-overlay__cards-grid--info-mode", val);
  }

  if (infoToggle) {
    infoToggle.addEventListener("click", () => setInfoMode(!infoMode));
  }

  // ── Rendu des cartes ──────────────────────────────────────────────────
  function renderCards() {
    if (!grid) return;
    grid.innerHTML = "";
    cards.forEach((card, idx) => {
      const el = GameCard.create(card, {
        context:    "other",
        size:       "salary",
        selectable: true,
        clickable:  true,
      });
      el.dataset.index = idx;
      el.setAttribute("role", "option");
      el.setAttribute("aria-selected", "false");
      el.setAttribute("aria-label", `${card.name ?? "Carte"} — valeur ${card.value ?? 0}`);
      el.setAttribute("tabindex", "0");

      el.addEventListener("card-click", () => {
        if (infoMode) {
          openCardDetail(card);
        } else {
          toggleCard(idx);
        }
      });

      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (infoMode) openCardDetail(card);
          else toggleCard(idx);
        }
      });

      grid.appendChild(el);
    });
  }

  // ── Ouvrir card-detail (lecture seule, pas d'actions) ─────────────────
  function openCardDetail(card) {
    const handler = getHandler("card-detail");
    if (!handler) {
      console.error("[salary-selector] Handler card-detail introuvable.");
      return;
    }
    const detailOverlay = handler({
      card,
      context:    "other",   // pas de contexte jouable → aucun bouton d'action
      is_my_turn: false,
      game_id:    window.GAME_ID ?? "",
    });
    document.body.appendChild(detailOverlay);
  }

  // ── Refresh UI ────────────────────────────────────────────────────────
  function refreshUI() {
    const total = selectedTotal();
    const pct   = cost > 0 ? Math.min(100, (total / cost) * 100) : 100;

    if (progressBar) {
      progressBar.style.width = pct + "%";
      progressBar.classList.toggle("salary-overlay__progress-bar--full", isEnough());
    }
    if (selectedTot) selectedTot.textContent = total;
    if (neededTot)   neededTot.textContent   = cost;

    grid?.querySelectorAll("game-card").forEach((el) => {
      const idx = parseInt(el.dataset.index, 10);
      const sel = selected.has(idx);
      el.toggleAttribute("selected", sel);
      el.setAttribute("aria-selected", String(sel));
    });

    if (confirmBtn) {
      confirmBtn.disabled = !isEnough();
      confirmBtn.classList.toggle("salary-overlay__btn--ready", isEnough());
    }
  }

  function toggleCard(idx) {
    selected.has(idx) ? selected.delete(idx) : selected.add(idx);
    refreshUI();
  }

  // ── Fermeture ─────────────────────────────────────────────────────────
  function closeOverlay() {
    overlay.classList.remove("salary-overlay--visible");
    overlay.addEventListener("transitionend", () => overlay.setAttribute("hidden", ""), { once: true });
    document.removeEventListener("keydown", trapFocus);
    setInfoMode(false); // reset pour la prochaine ouverture
  }

  function handleConfirm() {
    if (!isEnough()) return;
    closeOverlay();
    if (typeof onSubmit === "function") onSubmit([...selected]);
  }

  function trapFocus(e) {
    if (!overlay.classList.contains("salary-overlay--visible")) return;
    const focusable = [...overlay.querySelectorAll("game-card[tabindex], button:not([disabled])")];
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
  renderCards();
  refreshUI();

  if (confirmBtn) confirmBtn.addEventListener("click", handleConfirm);
  if (cancelBtn)  cancelBtn.addEventListener("click", closeOverlay);
  document.addEventListener("keydown", trapFocus);

  overlay.removeAttribute("hidden");
  requestAnimationFrame(() => overlay.classList.add("salary-overlay--visible"));
  grid?.querySelector("game-card")?.focus();

  return document.createDocumentFragment();
});