from ...Power import Power
from .JobCard import JobCard

class Militaire(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.NO_ATTENTAT)
        self.study = 0
        self.salary = 1
    def get_name(self) -> str:
        return "Militaire"
    def get_card_rule(self) -> str:
        return """Empeche tous attentat"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()