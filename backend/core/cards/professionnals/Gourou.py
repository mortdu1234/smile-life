from ...Game import Game
from ...Player import Player
from ...Power import Power
from .JobCard import JobCard

class Gourou(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 0
        self.salary = 3
    def get_name(self) -> str:
        return "Gourou"

    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        for player in game.players:
            if Power.NO_GOUROU in player.get_power():
                return False, "Il y a une personne qui bloque les gourous"
        return super().can_be_played(player, game)