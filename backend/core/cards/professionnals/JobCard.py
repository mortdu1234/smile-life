from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

from ..Card import Card
from ...Power import Power
from ...JobStatus import JobStatus

class JobCard(Card):
    """Carte métier de base."""
    jobPower: list["Power"]
    study: int
    salary: int
    status: JobStatus
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 2)
        self.jobPower = []
        self.jobStatus = JobStatus.RIEN
        self.study = 0
        self.salary = 0

    def get_power(self):
        """retourne les pouvoirs du métier"""
        return self.jobPower + [Power.NO_FIRE] if self.status==JobStatus.FONCTIONNAIRE else []

    def discard_job(self, current_player: "Player", game: "Game"):
        """Effectue les actions lors d'un discard du métier"""
        pass

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        player_level = player.get_study_level() 
        if player_level < self.study:
            return False, f"Pas assez d'étude, {player_level}<{self.study}"
        return super().can_be_played(player, game)

    def get_salary(self) -> int:
        return self.salary

