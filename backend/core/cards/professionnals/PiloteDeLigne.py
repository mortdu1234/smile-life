from ...Power import Power
from .JobCard import JobCard

class PiloteDeLigne(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.TRAVEL_FREE)
        self.study = 5
        self.salary = 4
    def get_name(self) -> str:
        return "Pilote de Ligne"