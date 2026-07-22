from ...JobStatus import JobStatus
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Plombier(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.status = JobStatus.INTERIMERE
        self.study = 0
        self.salary = 1
    def get_name(self) -> str:
        return "Plombier"
    def get_card_rule(self) -> str:
        return """ce métier est INTERIMERE"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()