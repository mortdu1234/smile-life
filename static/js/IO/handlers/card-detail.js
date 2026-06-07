/**
 * Handler : card-detail
 * ─────────────────────────────────────────────────────────────────────────────
 * Affiche un overlay de détail pour n'importe quelle carte.
 * Les boutons et leurs actions sont définis dans card-actions.js selon card.type.
 *
 * Payload attendu :
 * {
 *   card: {
 *     id:          int | string,
 *     name:        string,
 *     type:        string,        // nom de classe Python (ex: "JobCard", "WeddingCard")
 *     image_path:  string,
 *     smiles:      int,
 *     description?: string,
 *   },
 *   context:    "hand" | "played" | "discard" | "other",
 *   is_my_turn: bool,
 *   game_id:    string,
 * }
 */

import { registerHandler } from "../io-registry.js";
import { getActionsForCard } from "./card-actions.js";

// ── Variantes de boutons → classes CSS ────────────────────────────────────────

const VARIANT_CLASS = {
  primary: "cd-btn--primary",
  danger:  "cd-btn--danger",
  ghost:   "cd-btn--ghost",
  warning: "cd-btn--warning",
  success: "cd-btn--success",
};

// ── Requête vers Flask ────────────────────────────────────────────────────────

async function callEndpoint({ url, body }, onSuccess, onError) {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      onError(data.error ?? `Erreur ${res.status}`);
    } else {
      onSuccess(data);
    }
  } catch (e) {
    onError("Erreur réseau.");
  }
}

// ── Rendu principal ───────────────────────────────────────────────────────────

registerHandler("card-detail", ({ card, context, is_my_turn, game_id }) => {
  const overlay = document.createElement("div");
  overlay.className = "cd-overlay";

  const modal = document.createElement("div");
  modal.className = "cd-modal";

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeOverlay();
  });

  function closeOverlay() {
    overlay.classList.add("cd-closing");
    overlay.addEventListener("animationend", () => overlay.remove(), { once: true });
  }

  // ── Toast d'erreur inline ──────────────────────────────────────────────────
  const toast = document.createElement("div");
  toast.className = "cd-toast";
  toast.setAttribute("aria-live", "polite");

  function showError(msg) {
    toast.textContent = msg;
    toast.classList.add("cd-toast--visible");
    setTimeout(() => toast.classList.remove("cd-toast--visible"), 3500);
  }

  // ── Image ──────────────────────────────────────────────────────────────────
  const img = document.createElement("img");
  img.className = "cd-image";
  img.src = `/static/${card.image_path}`;
  img.alt = card.name;
  img.onerror = () => { img.style.display = "none"; };

  // ── Infos ──────────────────────────────────────────────────────────────────
  const info = document.createElement("div");
  info.className = "cd-info";
  info.innerHTML = `
    <span class="cd-type">${card.type ?? ""}</span>
    <h2 class="cd-name">${card.name}</h2>
    <div class="cd-smiles">😊 ${card.smiles ?? 0} smile${(card.smiles ?? 0) !== 1 ? "s" : ""}</div>
    ${card.description ? `<p class="cd-description">${card.description}</p>` : ""}
  `;

  // ── Boutons d'action ───────────────────────────────────────────────────────
  const actionsEl = document.createElement("div");
  actionsEl.className = "cd-actions";

  const actions = getActionsForCard(card, context, is_my_turn);

  actions.forEach((action) => {
    const btn = document.createElement("button");
    btn.className = `cd-btn ${VARIANT_CLASS[action.variant] ?? "cd-btn--ghost"}`;
    btn.textContent = action.label;

    btn.addEventListener("click", async () => {
      // Confirmation optionnelle
      if (action.confirm && !window.confirm(action.confirm)) return;

      btn.disabled = true;
      btn.classList.add("cd-btn--loading");

      const { url, body } = action.endpoint(card, game_id);

      await callEndpoint(
        { url, body },
        (_data) => {
          closeOverlay();
          // Recharge l'état du jeu si une fonction globale existe
          if (typeof window.refreshGameState === "function") {
            window.refreshGameState();
          }
        },
        (errMsg) => {
          btn.disabled = false;
          btn.classList.remove("cd-btn--loading");
          showError(errMsg);
        }
      );
    });

    actionsEl.appendChild(btn);
  });

  // Bouton Fermer toujours présent
  const closeBtn = document.createElement("button");
  closeBtn.className = "cd-btn cd-btn--ghost";
  closeBtn.textContent = "✕ Fermer";
  closeBtn.addEventListener("click", closeOverlay);
  actionsEl.appendChild(closeBtn);

  // ── Assemblage ─────────────────────────────────────────────────────────────
  modal.appendChild(img);
  modal.appendChild(info);
  modal.appendChild(actionsEl);
  modal.appendChild(toast);
  overlay.appendChild(modal);

  return overlay;
});

// ── Styles (injectés une seule fois) ─────────────────────────────────────────

if (!document.getElementById("cd-styles")) {
  const style = document.createElement("style");
  style.id = "cd-styles";
  style.textContent = `
    /* ── Overlay ── */
    .cd-overlay {
      position: fixed; inset: 0; z-index: 600;
      background: rgba(26,23,20,0.6);
      backdrop-filter: blur(4px);
      display: flex; align-items: center; justify-content: center;
      animation: cdOverlayIn 0.2s ease;
    }
    .cd-overlay.cd-closing { animation: cdOverlayOut 0.18s ease forwards; }
    @keyframes cdOverlayIn  { from { opacity: 0; } to { opacity: 1; } }
    @keyframes cdOverlayOut { from { opacity: 1; } to { opacity: 0; } }

    /* ── Modal ── */
    .cd-modal {
      background: #fff;
      border: 1px solid #e0d9d0;
      border-radius: 10px;
      width: 360px; max-width: 92vw;
      overflow: hidden;
      box-shadow: 0 32px 80px rgba(59,48,40,0.22);
      animation: cdModalIn 0.22s cubic-bezier(.22,.68,0,1.2);
    }
    .cd-overlay.cd-closing .cd-modal { animation: cdModalOut 0.18s ease forwards; }
    @keyframes cdModalIn  { from { opacity:0; transform: translateY(16px) scale(0.96); } to { opacity:1; transform: none; } }
    @keyframes cdModalOut { from { opacity:1; transform: none; } to { opacity:0; transform: translateY(8px) scale(0.97); } }

    /* ── Image ── */
    .cd-image {
      width: 100%; height: 220px; object-fit: cover; display: block;
      background: linear-gradient(135deg, #d4b98a, #b89a6a);
    }

    /* ── Infos ── */
    .cd-info { padding: 20px 22px 14px; }
    .cd-type {
      display: inline-block;
      font-size: 0.62rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;
      padding: 2px 8px; border-radius: 20px;
      background: rgba(184,154,106,0.15); color: #b89a6a;
      margin-bottom: 6px;
    }
    .cd-name {
      font-family: 'Cormorant Garamond', serif;
      font-size: 1.5rem; font-weight: 600; color: #1a1714;
      margin-bottom: 6px; line-height: 1.2;
    }
    .cd-smiles { font-size: 0.82rem; color: #b89a6a; margin-bottom: 10px; }
    .cd-description { font-size: 0.82rem; color: #7a7168; line-height: 1.5; }

    /* ── Boutons ── */
    .cd-actions {
      display: flex; flex-direction: column; gap: 8px;
      padding: 0 22px 22px;
    }
    .cd-btn {
      width: 100%; padding: 10px 16px; border-radius: 6px;
      font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 500;
      cursor: pointer; border: none; transition: opacity 0.15s, transform 0.15s;
      letter-spacing: 0.03em; position: relative;
    }
    .cd-btn:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
    .cd-btn:active:not(:disabled) { transform: translateY(0); }
    .cd-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    /* Variantes */
    .cd-btn--primary { background: #3b3028; color: #f5f2ee; }
    .cd-btn--danger  { background: rgba(180,60,60,0.09); color: #b43c3c; border: 1px solid rgba(180,60,60,0.2); }
    .cd-btn--ghost   { background: transparent; color: #7a7168; border: 1px solid #e0d9d0; }
    .cd-btn--warning { background: rgba(200,130,30,0.1); color: #c4821e; border: 1px solid rgba(200,130,30,0.25); }
    .cd-btn--success { background: rgba(50,140,80,0.1); color: #2e8a4f; border: 1px solid rgba(50,140,80,0.25); }

    /* État chargement */
    .cd-btn--loading::after {
      content: "";
      position: absolute; right: 14px; top: 50%; transform: translateY(-50%);
      width: 12px; height: 12px; border-radius: 50%;
      border: 2px solid currentColor; border-top-color: transparent;
      animation: cdSpin 0.6s linear infinite;
    }
    @keyframes cdSpin { to { transform: translateY(-50%) rotate(360deg); } }

    /* ── Toast erreur ── */
    .cd-toast {
      margin: 0 22px 16px;
      padding: 9px 14px; border-radius: 6px;
      background: rgba(180,60,60,0.08); color: #b43c3c;
      border: 1px solid rgba(180,60,60,0.18);
      font-size: 0.78rem; line-height: 1.4;
      opacity: 0; max-height: 0; overflow: hidden;
      transition: opacity 0.2s, max-height 0.2s;
    }
    .cd-toast--visible { opacity: 1; max-height: 80px; }
  `;
  document.head.appendChild(style);
}