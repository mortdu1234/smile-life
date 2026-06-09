from ...Power import Power
from .JobCard import JobCard

class Chirurgien(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.NO_MALADIE)
        self.jobPower.append(Power.INFINITE_STUDY)
        self.study = 6
        self.salary = 4
    def get_name(self) -> str:
        return "Chirurgien"
    def get_card_rule(self) -> str:
        return """Permet de continuer d'étudier après avoir poser le métier. Ne peut pas subir de maladie."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()