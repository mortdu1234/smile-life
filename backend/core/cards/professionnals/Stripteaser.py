from ...JobStatus import JobStatus

from .JobCard import JobCard

class Stripteaser(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 0
        self.salary = 1
        self.status = JobStatus.INTERIMERE