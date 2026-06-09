from ...Power import Power
from .JobCard import JobCard

class Medecin(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.INFINITE_STUDY)
        self.jobPower.append(Power.NO_MALADIE)
        self.study = 6
        self.salary = 4
    def get_name(self) -> str:
        return "Médecin"
    def get_card_rule(self) -> str:
        return """Permet de continer a étudier avec le métier. Ne peut pas recevoir de maladies"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()