from ..Acquisition import Acquisition
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
class Potion(Acquisition):
    def apply_potion_effect(self, game: "Game", current_player: "Player"):
        pass

    def get_card_rule(self) -> str:
        return """""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    