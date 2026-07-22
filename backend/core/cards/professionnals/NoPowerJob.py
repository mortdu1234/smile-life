from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Designer(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.study = 4
        self.salary = 3
    def get_name(self) -> str:
        return "Designer"

class Jardinier(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.study = 1
        self.salary = 1
    def get_name(self) -> str:
        return "Jardinier"

class Pizzaiolo(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.study = 0
        self.salary = 2
    def get_name(self) -> str:
        return "Pizzaiolo"