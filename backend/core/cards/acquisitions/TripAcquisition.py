from ...Game import Game
from ...Player import Player
from ...Power import Power

from .Acquisition import Acquisition

class Trip(Acquisition):
    def calcul_cost(self, player: Player, game: Game) -> int:
        if Power.TRAVEL_FREE in player.get_power():
            return 0
        return super().calcul_cost(player, game)