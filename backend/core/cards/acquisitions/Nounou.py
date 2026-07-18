from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.personnals.Children import ChildCard

from ...Game import Game
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ...Player import Player
from ...Power import Power

from .Acquisition import Acquisition

class Nounou(Acquisition):
    children_protected: "list[ChildCard]" = []
    def __init__(self, id: int, image_path: str, smiles: int, cost: int):
        super().__init__(id, image_path, smiles, cost)

    def calcul_cost(self, player: Player, game: Game) -> int:
        return super().calcul_cost(player, game)

    def get_name(self) -> str:
        return "Nounou"

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from backend.core.cards.personnals.Children import ChildCard
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        for card in current_player.get_card_from_group(groupe.CHILDREN):
            assert isinstance(card, ChildCard), "la carte trouvee nest pas un enfant"
            card.set_protected()
            self.children_protected.append(card)

        return True

    def discard_card(self, game: Game, owner: Player) -> None:
        for card in self.children_protected:
            card.set_not_protected()
        self.children_protected = []
        return super().discard_card(game, owner)

    def get_card_rule(self) -> str:
        return """Protège tous les enfants posé par le joueur de tous les malus""" + "\n"+ "="*10+ "\n" + super().get_card_rule()