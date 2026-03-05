"""
Actions sur le joueur courant lui-même.
"""
from typing import TYPE_CHECKING

from app.actions.base_action import BaseAction
from app.core.effect import CardEffect

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class GainResourceAction(BaseAction):
    """Ajoute des ressources (heritage, smiles virtuels, etc.)."""

    def apply(self, effect, game, current_player, target_player=None):
        amount = effect.params.get("amount", 0)
        resource = effect.params.get("resource", "heritage")
        if resource == "heritage":
            current_player.heritage += amount


class DrawCardsAction(BaseAction):
    """Fait piocher des cartes au joueur courant."""

    def apply(self, effect, game, current_player, target_player=None):
        count = effect.params.get("count", 1)
        for _ in range(min(count, len(game.deck))):
            current_player.hand.append(game.deck.pop())


class SkipNextTurnAction(BaseAction):
    """Rejoue le tour courant (ne passe pas au joueur suivant)."""

    def apply(self, effect, game, current_player, target_player=None):
        game.phase = "draw"
