from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class PiloteDeLigne(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.TRAVEL_FREE)
        self.study = 5
        self.salary = 4
    def get_name(self) -> str:
        return "Pilote de Ligne"
    def get_card_rule(self) -> str:
        return """Permet de poser des voyages gratuitement"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()