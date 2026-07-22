from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Avocat(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.NO_DIVORCE)
        self.study = 4
        self.salary = 3
    def get_name(self) -> str:
        return "Avocat"
    def get_card_rule(self) -> str:
        return """Permet de ne pas subir de divorce"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()