from ...Game import Game
from ...Player import Player

from .Acquisition import Acquisition
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Concert(Acquisition):
    def __init__(self, id: int, image_path: str, smiles: int, cost: int, extention: "Extention"):
        super().__init__(id, image_path, smiles, cost, extention)

    def calcul_cost(self, player: Player, game: Game) -> int:
        return super().calcul_cost(player, game)

    def get_name(self) -> str:
        return "Place de Concert"

    def get_card_rule(self) -> str:
        return """Un concert pour vivre de bons moments""" + "\n"+ "="*10+ "\n" + super().get_card_rule()