from ...JobStatus import JobStatus
from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Barman(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.INFINITE_FLIRT)
        self.status = JobStatus.INTERIMERE
        self.study = 0
        self.salary = 1
    def get_name(self) -> str:
        return "Barman"
    def get_card_rule(self) -> str:
        return """Permet de poser autant de flirt qu'il souhaite avant le marriage. possède le status Intérimère"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()
    