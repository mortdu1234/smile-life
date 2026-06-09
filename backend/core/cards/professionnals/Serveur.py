from ...JobStatus import JobStatus
from ...Power import Power
from .JobCard import JobCard

class Serveur(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.INFINITE_FLIRT)
        self.study = 0
        self.salary = 1
        self.status = JobStatus.INTERIMERE
    def get_name(self) -> str:
        return "Serveur"