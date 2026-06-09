from ...JobStatus import JobStatus
from ...Game import Game
from ...Player import Player
from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
class Policier(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.NO_BANDIT)
        self.jobPower.append(Power.NO_GOUROU)
        self.jobStatus = JobStatus.FONCTIONNAIRE
        self.study = 1
        self.salary = 1
    def get_name(self) -> str:
        return "Policier"

    def apply_card_effect(self, game: Game, current_player: Player, interface: "UserIO") -> bool:
        """supprimer tous les bandit et gourous sur le terrain"""
        for player in game.players:
            job = player.get_job()
            if job:
                from .Bandit import Bandit
                from .Gourou import Gourou
                if isinstance(job, (Gourou, Bandit)):
                    print("Perte d'un métier a cause du policier")
                    job.discard_job(player, game)
                    player.remove_card(job)
                
        return super().apply_card_effect(game, current_player, interface)