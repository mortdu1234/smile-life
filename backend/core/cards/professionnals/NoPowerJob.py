from .JobCard import JobCard

class Designer(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 4
        self.salary = 3

class Jardinier(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 1
        self.salary = 1

class Pizzaiolo(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 0
        self.salary = 2