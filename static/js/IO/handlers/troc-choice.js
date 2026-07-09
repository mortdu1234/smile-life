import { registerHandler, getHandler } from "../io-registry.js";

/**
 * troc-choice — Handler IO déclenché quand une Eclipse est active au moment
 * de piocher (cf. Game.py::draw_card_from_deck → UserIO.ask_troc).
 *
 * Réutilise l'overlay #card-detail-overlay (via le handler "card-detail")
 * pour afficher la carte piochée, avec deux actions custom :
 *   - "🔄 Troquer" → index 0
 *   - "✋ Garder"   → index 1
 *
 * Le choix est renvoyé au serveur via la route générique /submit
 * (pending.onSubmit === submit, câblé par défaut dans io-core.js poll()),
 * qui débloque WebIO.ask_troc côté backend.
 */
registerHandler("troc-choice", function render(pending) {
  const { card, prompt, onSubmit } = pending;

  const cardDetailHandler = getHandler("card-detail");
  if (!cardDetailHandler) {
    console.error("[troc-choice] Handler card-detail introuvable.");
    return document.createDocumentFragment();
  }

  const customActions = [
    {
      label: "🔄 Troquer",
      variant: "primary",
      onClick: () => onSubmit(0),
    },
    {
      label: "✋ Garder",
      variant: "ghost",
      onClick: () => onSubmit(1),
    },
  ];

  return cardDetailHandler({
    card,
    context: "other",
    is_my_turn: false,
    game_id: window.GAME_ID ?? "",
    prompt,
    customActions,
  });
});