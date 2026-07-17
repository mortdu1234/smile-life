import { registerHandler } from "../io-registry.js";

registerHandler("choice", function render(pending) {
  const overlay = document.getElementById("choice-overlay");
  if (!overlay) {
    console.error("[choice] #choice-overlay introuvable dans le DOM.");
    return document.createDocumentFragment();
  }

  if (overlay.classList.contains("choice-overlay--visible")) {
    return document.createDocumentFragment();
  }

  const { choices = [], prompt = "", onSubmit } = pending;

  const listEl   = overlay.querySelector("#choice-list");
  const titleEl  = overlay.querySelector("#choice-title");
  const promptEl = overlay.querySelector("#choice-prompt");

  if (titleEl)  titleEl.textContent  = "Faites votre choix";
  if (promptEl) promptEl.textContent = prompt;

  let locked = false; // évite un double clic pendant l'envoi

  // ── Rendu des options ───────────────────────────────────────────────
  function renderOptions() {
    if (!listEl) return;
    listEl.innerHTML = "";

    if (!choices.length) {
      const empty = document.createElement("p");
      empty.className = "choice-overlay__empty";
      empty.textContent = "Aucun choix disponible.";
      listEl.appendChild(empty);
      return;
    }

    choices.forEach((label, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice-overlay__option";
      btn.textContent = label;
      btn.dataset.index = idx;
      btn.setAttribute("role", "option");
      btn.setAttribute("aria-selected", "false");
      btn.setAttribute("tabindex", "0");

      btn.addEventListener("click", () => selectChoice(idx, btn));
      btn.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectChoice(idx, btn);
        }
      });

      listEl.appendChild(btn);
    });
  }

  // ── Sélection = envoi immédiat (pas de bouton "confirmer") ──────────
  function selectChoice(idx, btnEl) {
    if (locked) return;
    locked = true;

    listEl?.querySelectorAll(".choice-overlay__option").forEach((el) => {
      el.disabled = true;
    });
    btnEl.classList.add("choice-overlay__option--selected");
    btnEl.setAttribute("aria-selected", "true");

    closeOverlay();
    if (typeof onSubmit === "function") onSubmit(idx);
  }

  // ── Fermeture ─────────────────────────────────────────────────────────
  function closeOverlay() {
    overlay.classList.remove("choice-overlay--visible");
    overlay.addEventListener(
      "transitionend",
      () => overlay.setAttribute("hidden", ""),
      { once: true }
    );
    document.removeEventListener("keydown", handleKey);
  }

  function handleKey(e) {
    if (!overlay.classList.contains("choice-overlay--visible")) return;

    // Trap focus (pas d'Escape : un choix bloque le back-end, il doit être fait)
    const focusable = [...overlay.querySelectorAll(".choice-overlay__option:not(:disabled)")];
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
  renderOptions();

  document.removeEventListener("keydown", handleKey);
  document.addEventListener("keydown", handleKey);

  overlay.removeAttribute("hidden");
  requestAnimationFrame(() => overlay.classList.add("choice-overlay--visible"));
  listEl?.querySelector(".choice-overlay__option")?.focus();

  return document.createDocumentFragment();
});