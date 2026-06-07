from ...Game import Game
from ...Player import Player
from ...Power import Power

from .OtherCard import OtherCard

class Legion(OtherCard):
    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        if Power.HAS_BEEN_BANDIT in player.get_power():
            return False, "vous avez été bandit"
        return super().can_be_played(player, game)
