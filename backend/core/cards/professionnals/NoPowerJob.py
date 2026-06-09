from .JobCard import JobCard

class Designer(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 4
        self.salary = 3
    def get_name(self) -> str:
        return "Designer"

class Jardinier(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 1
        self.salary = 1
    def get_name(self) -> str:
        return "Jardinier"

class Pizzaiolo(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 0
        self.salary = 2
    def get_name(self) -> str:
        return "Pizzaiolo"