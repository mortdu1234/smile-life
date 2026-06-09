from ...JobStatus import JobStatus
from ...Power import Power
from .JobCard import JobCard

class Barman(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.NO_DIVORCE)
        self.status = JobStatus.INTERIMERE
        self.study = 0
        self.salary = 1
    def get_name(self) -> str:
        return "Barman"