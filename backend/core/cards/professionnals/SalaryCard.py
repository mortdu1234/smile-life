from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

from ..Card import Card

class SalaryCard(Card):
    value: int
    def __init__(self, id: int, image_path: str, smiles: int, value: int):
        super().__init__(id, image_path, smiles)
        self.value = value

    def get_value(self):
        return self.value

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        job=player.get_job()
        if not (job and job.get_salary() >= self.value):
            return False, f"le métier ne permet pas de mettre des salaires de valeur {self.value}"  
        return super().can_be_played(player, game)