from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Garagiste(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.NO_ACCIDENT)
        self.study = 1
        self.salary = 2
    def get_name(self) -> str:
        return "Garagiste"
    def get_card_rule(self) -> str:
        return """Ne peut subir d'accidents"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()