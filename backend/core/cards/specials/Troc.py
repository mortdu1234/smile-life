from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
class Troc(SpecialCard):

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        print("[DEBUG] TODO")        
        return super().apply_card_effect(game, current_player, interface)
