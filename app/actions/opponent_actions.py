"""
Actions appliquées sur les adversaires.
"""
import random
from typing import TYPE_CHECKING

from app.actions.base_action import BaseAction
from app.core.effect import CardEffect

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class BlockTurnsAction(BaseAction):
    """Bloque N tours à un adversaire."""

    def apply(self, effect, game, current_player, target_player=None):
        if target_player is None:
            return
        blocked = effect.params.get("blocked_turns", 1)
        target_player.skip_turns += blocked


class DrainResourceAction(BaseAction):
    """Retire une ressource (salaire, étude) à un adversaire."""

    def apply(self, effect, game, current_player, target_player=None):
        if target_player is None:
            return
        resource = effect.params.get("resource", "salary")

        if resource == "salary":
            from app.cards.concrete.professional.study_salary import SalaryCard
            salaries = [
                c for c in target_player.played["vie professionnelle"]
                if isinstance(c, SalaryCard)
            ]
            if salaries:
                card = salaries[-1]
                target_player.remove_card_from_played(card)
                game.discard.append(card)

        elif resource == "study":
            from app.cards.concrete.professional.study_salary import StudyCard
            studies = [
                c for c in target_player.played["vie professionnelle"]
                if isinstance(c, StudyCard)
            ]
            if studies:
                card = studies[-1]
                target_player.remove_card_from_played(card)
                game.discard.append(card)


class DiscardRandomCardsAction(BaseAction):
    """Défausse N cartes aléatoires de la main d'un adversaire."""

    def apply(self, effect, game, current_player, target_player=None):
        if target_player is None:
            return
        count = effect.params.get("count", 1)
        for _ in range(min(count, len(target_player.hand))):
            card = random.choice(target_player.hand)
            target_player.hand.remove(card)
            game.discard.append(card)
