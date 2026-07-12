from ..Acquisition import Acquisition
from typing import TYPE_CHECKING
from ....Power import Power
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class ObjetMagique(Acquisition):
    def get_card_rule(self) -> str:
        return """""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    