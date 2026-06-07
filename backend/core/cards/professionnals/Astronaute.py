from ...Game import Game
from ...Player import Player
from .JobCard import JobCard

class Astronaute(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 6
        self.salary = 4

    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        """Recupère une carte depuis la défausse posable et la pose immédiatement"""
        print("[DEBUG] TODO")
        return super().apply_card_effect(game, current_player)