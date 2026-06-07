from ....userIo.interface import UserIO
from ...Game import Game
from ...Player import Player
from ...Power import Power
from ..professionnals.JobCard import JobCard

from .OtherCard import OtherCard

class Price(OtherCard):
    def __init__(self, id: int, image_path: str, smiles: int):
        super().__init__(id, image_path, smiles)

    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        job = player.get_job()
        if job and Power.CAN_BE_PRICED not in player.get_power():
            return False, "il te faut un métier qui puisse etre priced"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: Game, current_player: Player, interface: UserIO) -> bool:
        current_player.remove_power(Power.CAN_BE_PRICED)
        return super().apply_card_effect(game, current_player, interface)