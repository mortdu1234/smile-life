from ...JobStatus import JobStatus
from .JobCard import JobCard

class Plombier(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.status = JobStatus.INTERIMERE
        self.study = 0
        self.salary = 1