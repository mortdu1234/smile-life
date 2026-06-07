from ...Power import Power
from .JobCard import JobCard

class Avocat(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.NO_DIVORCE)
        self.study = 4
        self.salary = 3