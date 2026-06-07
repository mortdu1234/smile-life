from ...Game import Game
from ...Player import Player
from ...Power import Power
from .JobCard import JobCard

class ChefDesVentes(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 3
        self.salary = 3
    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        """permet de récupérer un salaire posable depuis la défausse"""
        print("[DEBUG] TODO")
        return super().apply_card_effect(game, current_player)
    