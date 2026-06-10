/**
 * card-actions.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Centralise toutes les actions disponibles par type de carte.
 * Chaque entrée correspond à une classe Python de Game.py.
 *
 * Structure d'une action :
 * {
 *   label:    string,           // texte du bouton
 *   variant:  string,           // classe CSS (primary | danger | ghost | warning | success)
 *   context:  string[],         // dans quels contextes afficher ("hand"|"played"|"discard"|"other")
 *   endpoint: (card, game_id) => { url, body },  // construit la requête Flask
 *   confirm?: string,           // message de confirmation optionnel avant d'agir
 * }
 *
 * Les endpoints correspondent aux routes Flask qui appellent les méthodes de Game.py :
 *   draw_card_from_deck       → POST /game/<id>/draw
 *   draw_card_from_discard    → POST /game/<id>/draw-discard
 *   discard_card_from_hand    → POST /game/<id>/discard
 *   discard_job_card          → POST /game/<id>/discard-job
 *   discard_wedding_card      → POST /game/<id>/discard-wedding
 *   discard_adultery_card     → POST /game/<id>/discard-adultery
 *   place_card                → POST /game/<id>/place
 *   skip_turn                 → POST /game/<id>/skip
 */

// ── Helpers endpoints ─────────────────────────────────────────────────────────

const EP = {
  place:           (game_id, card_id) => ({ url: `${window.BASE_URL}/game/${game_id}/place`,            body: { card_id } }),
  discard:         (game_id, card_id) => ({ url: `${window.BASE_URL}/game/${game_id}/discard`,          body: { card_id } }),
  discardJob:      (game_id, card_id) => ({ url: `${window.BASE_URL}/game/${game_id}/discard-job`,      body: { card_id } }),
  discardWedding:  (game_id, card_id) => ({ url: `${window.BASE_URL}/game/${game_id}/discard-wedding`,  body: { card_id } }),
  discardAdultery: (game_id, card_id) => ({ url: `${window.BASE_URL}/game/${game_id}/discard-adultery`, body: { card_id } }),
  drawDiscard:     (game_id)          => ({ url: `${window.BASE_URL}/game/${game_id}/draw-discard`,     body: {} }),
  betOnCasino:     (game_id, card_id) => ({ url: `${window.BASE_URL}/game/${game_id}/bet-on-casino`,    body: { card_id } }),
};

// ── Catalogue des actions par type de carte ───────────────────────────────────
// La clé correspond au `card.type` (nom de classe Python).

export const CARD_ACTIONS = {

  // ── Carte générique / fallback ─────────────────────────────────────────────
  default: [
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["hand"],
      endpoint: (card, game_id) => EP.place(game_id, card.id),
    },
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["discard"],
      endpoint: (card, game_id) => EP.drawDiscard(game_id),
    },
    {
      label: "🗑 Défausser",
      variant: "danger",
      context: ["hand"],
      endpoint: (card, game_id) => EP.discard(game_id, card.id),
    },
  ],

  // ── Carte Métier (Job) ─────────────────────────────────────────────────────
  // Méthodes Game.py : place_card / discard_job_card
  JobCard: [
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["hand"],
      endpoint: (card, game_id) => EP.place(game_id, card.id),
    },
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["discard"],
      endpoint: (card, game_id) => EP.drawDiscard(game_id),
    },
    {
      label: "🗑 Défausser",
      variant: "danger",
      context: ["hand"],
      endpoint: (card, game_id) => EP.discard(game_id, card.id),
    },
    {
      label: "👋 Démissionner",
      variant: "danger",
      context: ["played"],
      confirm: "Voulez-vous vraiment démissionner ?",
      endpoint: (card, game_id) => EP.discardJob(game_id, card.id),
    },
  ],

  // ── Carte Mariage (Wedding) ────────────────────────────────────────────────
  // Méthodes Game.py : place_card / discard_wedding_card
  WeddingCard: [
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["hand"],
      endpoint: (card, game_id) => EP.place(game_id, card.id),
    },
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["discard"],
      endpoint: (card, game_id) => EP.drawDiscard(game_id),
    },
    {
      label: "🗑 Défausser",
      variant: "danger",
      context: ["hand"],
      endpoint: (card, game_id) => EP.discard(game_id, card.id),
    },
    {
      label: "💔 Divorcer",
      variant: "danger",
      context: ["played"],
      confirm: "Êtes-vous sûr de vouloir divorcer ?",
      endpoint: (card, game_id) => EP.discardWedding(game_id, card.id),
    },
  ],

  // ── Carte Adultère (Adultery) ──────────────────────────────────────────────
  // Méthodes Game.py : place_card / discard_adultery_card
  AdulteryCard: [
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["hand"],
      endpoint: (card, game_id) => EP.place(game_id, card.id),
    },
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["discard"],
      endpoint: (card, game_id) => EP.drawDiscard(game_id),
    },
    {
      label: "🗑 Défausser",
      variant: "danger",
      context: ["hand"],
      endpoint: (card, game_id) => EP.discard(game_id, card.id),
    },
    {
      label: "🚫 Mettre fin",
      variant: "danger",
      context: ["played"],
      confirm: "Mettre fin à cette relation ?",
      endpoint: (card, game_id) => EP.discardAdultery(game_id, card.id),
    },
  ],
  SalaryCard: [
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["hand"],
      endpoint: (card, game_id) => EP.place(game_id, card.id),
    },
    {
      label: "▶ Jouer",
      variant: "primary",
      context: ["discard"],
      endpoint: (card, game_id) => EP.drawDiscard(game_id),
    },
    {
      label: "Miser",
      variant: "primary",
      context: ["hand", "discard"],
      confirm: "Voulez-vous miser cette carte au casino ?",
      endpoint: (card, game_id) => EP.betOnCasino(game_id, card.id),
    },
    {
      label: "🗑 Défausser",
      variant: "danger",
      context: ["hand"],
      endpoint: (card, game_id) => EP.discard(game_id, card.id),
    },
  ],
};

/**
 * Résout la catégorie d'une carte en parcourant sa MRO Python.
 * Prend le match le plus éloigné (le plus général) qui existe dans CARD_ACTIONS,
 * puis remonte vers le plus spécifique — donc le premier trouvé en partant
 * de la fin de la MRO est le plus général, et on préfère le plus spécifique.
 *
 * Exemple : AngelaChild → mro = ["AngelaChild", "ChildCard", "GirlPowerChild", "Card"]
 *   → cherche "AngelaChild" → absent
 *   → cherche "ChildCard"   → trouvé ✓  (plus spécifique que "default", plus général qu'Angela)
 *
 * @param {object} card  - doit avoir card.mro (array) et card.type (string)
 * @returns {string}     - clé dans CARD_ACTIONS
 */
function resolveCategory(card) {
  const mro = card.mro ?? [card.type];
  for (const cls of mro) {
    if (CARD_ACTIONS[cls]) return cls;
  }
  return "default";
}

/**
 * Retourne les actions visibles pour une carte donnée dans un contexte donné.
 * @param {object} card     - la carte (card.mro = MRO Python, card.type = classe feuille)
 * @param {string} context  - "hand" | "played" | "discard" | "other"
 * @param {boolean} is_my_turn
 * @returns {Action[]}
 */
export function getActionsForCard(card, context, is_my_turn) {
  if (!is_my_turn) return [];

  const category = resolveCategory(card);
  const actions = CARD_ACTIONS[category];
  return actions.filter((a) => a.context.includes(context));
}