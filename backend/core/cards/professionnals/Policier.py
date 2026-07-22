from ...JobStatus import JobStatus
from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Policier(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.NO_BANDIT)
        self.jobPower.append(Power.NO_GOUROU)
        self.status = JobStatus.FONCTIONNAIRE
        self.study = 1
        self.salary = 1
    def get_name(self) -> str:
        return "Policier"

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        """supprimer tous les bandit et gourous sur le terrain"""
        for player in game.players:
            job = player.get_job()
            if job:
                from .Bandit import Bandit
                from .Gourou import Gourou
                if isinstance(job, (Gourou, Bandit)):
                    print("Perte d'un métier a cause du policier")
                    player.remove_card(job, game)
                
        return super().apply_card_effect(game, current_player)
    def get_card_rule(self) -> str:
        return """Ce métier permet d'empecher tous bandits et tous gourous. Ce métier est FONCTIONNAIRE"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()