from ...Game import Game
from ...Player import Player
from ...Power import Power

from .Acquisition import Acquisition

class House(Acquisition):
    def calcul_cost(self, player: Player, game: Game) -> int:
        cost = self.original_price
        if Power.FIRST_HOUSE_FREE in player.get_power():
            player.remove_power(Power.FIRST_HOUSE_FREE) # supprime l'avantage qui viens d'etre utilsé
            return 0
        if player.is_wedding():
            cost = self.original_price // 2
        return cost