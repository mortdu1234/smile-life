from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Pharmacien(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.NO_MALADIE)
        self.study = 5
        self.salary = 3
    def get_name(self) -> str:
        return "Pharmacien"
    def get_card_rule(self) -> str:
        return """Se métier ne peux pas recevoir de maladie"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()