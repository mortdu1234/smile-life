from ...Game import Game
from ...Player import Player

from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
class Medium(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 0
        self.salary = 1
    def apply_card_effect(self, game: Game, current_player: Player, interface: "UserIO") -> bool:
        """Permet de voir les 13 prochaines cartes du jeu"""
        print("[DEBUG] TODO")
        return super().apply_card_effect(game, current_player, interface)