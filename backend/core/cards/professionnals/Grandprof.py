from ...Game import Game
from ...JobStatus import JobStatus
from ...Player import Player
from ...Power import Power
from .Prof import Prof
from .JobCard import JobCard

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Grandprof(JobCard):
    
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.study = 0
        self.salary = 3
        self.status = JobStatus.FONCTIONNAIRE
    def get_name(self) -> str:
        return "Grand Professeur"

    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        if not isinstance(player.get_job(), Prof):
            return False, "Tu dois etre un prof avant d'etre grand prof"
        return True, ""
    def get_card_rule(self) -> str:
        return """Effectue une amélioration du étier de professeur. Necessite d'etre professeur avant de passer en grand prof. ce métier est un FONCTIONNAIRE."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()
    
