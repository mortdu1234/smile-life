from ...Game import Game
from ...Player import Player
from ...Power import Power

from .Acquisition import Acquisition

class Trip(Acquisition):
    place: str
    def __init__(self, id: int, image_path: str, smiles: int, cost: int, place: str):
        super().__init__(id, image_path, smiles, cost)
        self.place = place
    def calcul_cost(self, player: Player, game: Game) -> int:
        if Power.TRAVEL_FREE in player.get_power():
            return 0
        return super().calcul_cost(player, game)

    def get_name(self) -> str:
        return f"Voyage {self.place}"

    def get_card_rule(self) -> str:
        return """Un voyage n'a rien de particulier""" + "\n"+ "="*10+ "\n" + super().get_card_rule()