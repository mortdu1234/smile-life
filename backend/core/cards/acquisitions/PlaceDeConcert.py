from ...Game import Game
from ...Player import Player

from .Acquisition import Acquisition

class Concert(Acquisition):
    def __init__(self, id: int, image_path: str, smiles: int, cost: int):
        super().__init__(id, image_path, smiles, cost)

    def calcul_cost(self, player: Player, game: Game) -> int:
        return super().calcul_cost(player, game)

    def get_name(self) -> str:
        return "Place de Concert"

    def get_card_rule(self) -> str:
        return """Un concert pour vivre de bons moments""" + "\n"+ "="*10+ "\n" + super().get_card_rule()