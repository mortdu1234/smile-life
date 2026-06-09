from ...Power import Power
from .JobCard import JobCard

class Pharmacien(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.NO_MALADIE)
        self.study = 5
        self.salary = 3
    def get_name(self) -> str:
        return "Pharmacien"