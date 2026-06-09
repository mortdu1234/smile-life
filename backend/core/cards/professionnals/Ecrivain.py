from ...Power import Power
from .JobCard import JobCard

class Ecrivain(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.CAN_BE_PRICED)
        self.study = 0
        self.salary = 1
    def get_name(self) -> str:
        return "Écrivain"
    def get_card_rule(self) -> str:
        return """Peut recevoir un Grand Prix d'Excellence"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()