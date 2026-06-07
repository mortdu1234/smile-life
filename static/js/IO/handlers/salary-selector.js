import { registerHandler } from "../io-registry.js";

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

registerHandler("salary-selector", function render(pending) {
  const overlay = document.getElementById("salary-overlay");
  if (!overlay) {
    console.error("[salary-selector] #salary-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  // ── Si déjà ouvert, ne rien faire ────────────────────────────────────
  if (overlay.classList.contains("salary-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const { cards = [], cost = 0, prompt = "", onSubmit } = pending;

  const selected = new Set();
  const selectedTotal = () =>
    [...selected].reduce((sum, i) => sum + (cards[i]?.value ?? 0), 0);
  const isEnough = () => selectedTotal() >= cost;

  const grid        = overlay.querySelector("#salary-cards-grid");
  const progressBar = overlay.querySelector("#salary-progress-bar");
  const promptText  = overlay.querySelector("#salary-prompt-text");
  const costEl      = overlay.querySelector("#salary-required-cost");
  const selectedTot = overlay.querySelector("#salary-selected-total");
  const neededTot   = overlay.querySelector("#salary-needed-total");
  const confirmBtn  = overlay.querySelector("#salary-confirm-btn");
  const cancelBtn   = overlay.querySelector("#salary-cancel-btn");

  if (promptText) promptText.textContent = prompt;
  if (costEl)     costEl.textContent     = cost;
  if (neededTot)  neededTot.textContent  = cost;

  function renderCards() {
    if (!grid) return;
    grid.innerHTML = "";
    cards.forEach((card, idx) => {
      const btn = document.createElement("button");
      btn.className = "salary-card";
      btn.type = "button";
      btn.dataset.index = idx;
      btn.setAttribute("role", "option");
      btn.setAttribute("aria-selected", "false");
      btn.setAttribute("aria-label", `${card.name ?? "Carte"} — valeur ${card.value ?? 0}`);
      btn.innerHTML = `
        <div class="salary-card__check">
          <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2.2"
                  stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="salary-card__name">${escHtml(card.name ?? "—")}</div>
        <div class="salary-card__value">${card.value ?? 0}</div>
        ${card.type ? `<div class="salary-card__type">${escHtml(card.type)}</div>` : ""}
      `;
      btn.addEventListener("click", () => toggleCard(idx));
      grid.appendChild(btn);
    });
  }

  function refreshUI() {
    const total = selectedTotal();
    const pct = cost > 0 ? Math.min(100, (total / cost) * 100) : 100;
    if (progressBar) {
      progressBar.style.width = pct + "%";
      progressBar.classList.toggle("salary-overlay__progress-bar--full", isEnough());
    }
    if (selectedTot) selectedTot.textContent = total;
    if (neededTot)   neededTot.textContent   = cost;
    grid?.querySelectorAll(".salary-card").forEach((btn) => {
      const idx = parseInt(btn.dataset.index, 10);
      const sel = selected.has(idx);
      btn.classList.toggle("salary-card--selected", sel);
      btn.setAttribute("aria-selected", String(sel));
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

  function closeOverlay() {
    overlay.classList.remove("salary-overlay--visible");
    overlay.addEventListener("transitionend", () => overlay.setAttribute("hidden", ""), { once: true });
    document.removeEventListener("keydown", trapFocus);
  }

  function handleConfirm() {
    if (!isEnough()) return;
    const indices = [...selected];
    closeOverlay();
    if (typeof onSubmit === "function") {
      onSubmit(indices);
    }
  }

  function trapFocus(e) {
    if (!overlay.classList.contains("salary-overlay--visible")) return;
    const focusable = [...overlay.querySelectorAll('button:not([disabled]), [tabindex]:not([tabindex="-1"])')];
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

  // Attacher les listeners directement (pas de cloneNode — on n'ouvre qu'une fois)
  if (confirmBtn) confirmBtn.addEventListener("click", handleConfirm);
  if (cancelBtn)  cancelBtn.addEventListener("click", closeOverlay);
  document.addEventListener("keydown", trapFocus);

  // Ouvrir
  overlay.removeAttribute("hidden");
  requestAnimationFrame(() => overlay.classList.add("salary-overlay--visible"));
  grid?.querySelector(".salary-card")?.focus();

  return document.createDocumentFragment();
});