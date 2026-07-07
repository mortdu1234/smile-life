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
    old_salary: int | None
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 2)
        self.jobPower = []
        self.status = JobStatus.RIEN
        self.study = 0
        self.salary = 0
        self.old_salary = None

    def get_power(self):
        """retourne les pouvoirs du métier"""
        return self.jobPower + [Power.NO_FIRE] if self.status==JobStatus.FONCTIONNAIRE else self.jobPower

    def discard_job(self, current_player: "Player", game: "Game"):
        """Effectue les actions lors d'un discard du métier"""
        if self.old_salary:
            self.salary = self.old_salary
            self.old_salary = None

    def set_salary(self, new_salary: int):
        """permet de changer le salaire du métier"""
        self.old_salary = self.salary
        self.salary = new_salary


    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        player_level = player.get_study_level() 
        if player_level < self.study:
            return False, f"Pas assez d'étude, {player_level}<{self.study}"

        player_power = player.get_power()
        if Power.JOB_MAX_STUDY_5 in player_power and self.study > 5:
            return False, f"Vous ne pouvez pas poser un métier avec plus de 5 d'étude"
        if Power.JOB_MAX_STUDY_4 in player_power and self.study > 4:
            return False, f"Vous ne pouvez pas poser un métier avec plus de 4 d'étude"


        print(f"essaye de poser un métier : {player.get_job()}")
        if player.get_job():
            return False, "Vous avez déja un métier"
        return super().can_be_played(player, game)

    def get_salary(self) -> int:
        return self.salary

    def can_be_discard(self, player: 'Player', game: "Game") -> tuple[bool, str]:
        from ...Game import TurnState
        if game.turn_state == TurnState.POSE and self.status != JobStatus.INTERIMERE:
            return False, "Vous ne pouvez démissionner que en phase de pioche sauf si vous etes intérimère"
        return True, ""

    def get_card_rule(self) -> str:
        return """Les Cartes métier sont des cartes qui permet de poser des salaires. Les métiers necessitent un certain nombre d'études.\n
        Certains métier ont des status : \n
        -FONCTIONNAIRE : ne peut etre licencier\n
        -INTERRIMAIRE : peut démissionner a tout moment lors de sont tour, sans devoir passer son tour\n
        Il est possible de démissionner d'un métier. Pour cela, avant de piocher, il faut démissionner, et c'est la fin de son 
        tour.\n"""+ f"Ce métier permet demande {self.study} d'étude et peut poser des salaires jusqu'à {self.salary}."+ "\n"+ "="*10+ "\n" + super().get_card_rule()