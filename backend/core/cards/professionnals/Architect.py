from ...Power import Power
from .JobCard import JobCard

class Architect(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.FIRST_HOUSE_FREE)
        self.study = 4
        self.salary = 4
    def get_name(self) -> str:
        return "Architecte"