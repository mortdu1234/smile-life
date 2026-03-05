"""
Registre des actions — mapping type (str) → classe Action.

Pour ajouter une nouvelle action :
1. Créer la classe dans actions/player_actions.py ou opponent_actions.py
2. L'enregistrer ici
"""
from app.actions.player_actions import GainResourceAction, DrawCardsAction, SkipNextTurnAction
from app.actions.opponent_actions import BlockTurnsAction, DrainResourceAction, DiscardRandomCardsAction
from app.actions.base_action import BaseAction
from app.core.effect import CardEffect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game

ACTION_REGISTRY: dict[str, type[BaseAction]] = {
    # Joueur courant
    "gain_resource":        GainResourceAction,
    "draw_cards":           DrawCardsAction,
    "skip_next_turn":       SkipNextTurnAction,

    # Adversaires
    "block_turns":          BlockTurnsAction,
    "drain_resource":       DrainResourceAction,
    "discard_random":       DiscardRandomCardsAction,
}


def apply_effect(
    effect: CardEffect,
    game: "Game",
    current_player: "Player",
    target_player: "Player | None" = None,
) -> None:
    """
    Applique un CardEffect via le registre.
    Lève KeyError si le type d'effet est inconnu.
    """
    action_cls = ACTION_REGISTRY.get(effect.type)
    if action_cls is None:
        raise KeyError(f"Action inconnue : {effect.type!r}")
    action_cls().apply(effect, game, current_player, target_player)
