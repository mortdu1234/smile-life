from ...JobStatus import JobStatus
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Prof(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.study = 2
        self.salary = 2
        self.status = JobStatus.FONCTIONNAIRE
    def get_name(self) -> str:
        return "Professeur"
    def get_card_rule(self) -> str:
        return """Ce métier est FONCTIONNAIRE, peut etre améliorer en grand prof"""