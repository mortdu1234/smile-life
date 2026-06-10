from ...Power import Power
from .JobCard import JobCard

class Architect(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.FIRST_HOUSE_FREE)
        self.study = 4
        self.salary = 3
    def get_name(self) -> str:
        return "Architecte"
    def get_card_rule(self) -> str:
        return """L'Architecte permet de poser 1 maison gratuite."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()