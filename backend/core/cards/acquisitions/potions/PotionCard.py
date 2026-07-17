from ....Power import Power
from ..Acquisition import Acquisition
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
class Potion(Acquisition):
    def calcul_cost(self, player: "Player", game: "Game") -> int:
        powers = player.get_power()
        if Power.FREE_POTION in powers:
            return 0
        return super().calcul_cost(player, game)
    
    def apply_potion_effect(self, game: "Game", current_player: "Player"):
        pass

    def get_card_rule(self) -> str:
        return """""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    