from backend.core.Game import Game
from backend.core.Player import Player

from ..Acquisition import Acquisition
from typing import TYPE_CHECKING
from ....Power import Power
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class ObjetMagique(Acquisition):
    def calcul_cost(self, player: Player, game: Game) -> int:
        powers = player.get_power()
        if Power.FREE_OBJET_MAGIQUE in powers:
            return 0
        return super().calcul_cost(player, game)
    
    def get_card_rule(self) -> str:
        return """""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    