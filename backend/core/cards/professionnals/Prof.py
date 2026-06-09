from ...JobStatus import JobStatus
from .JobCard import JobCard

class Prof(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 2
        self.salary = 2
        self.status = JobStatus.FONCTIONNAIRE
    def get_name(self) -> str:
        return "Professeur"