from ...JobStatus import JobStatus
from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Serveur(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.INFINITE_FLIRT)
        self.study = 0
        self.salary = 1
        self.status = JobStatus.INTERIMERE
    def get_name(self) -> str:
        return "Serveur"
    def get_card_rule(self) -> str:
        return """Ce métier est INTERIMERE. Il permet de pouvoir poser des flirts a l'infini avant le mariage"""