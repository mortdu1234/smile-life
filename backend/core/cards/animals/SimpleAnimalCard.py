from .AnimalCard import AnimalCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Chien(AnimalCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path=image_path, smiles=1, extention=extention)
    def get_name(self) -> str:
        return "Chien"
    
class Chat(AnimalCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path=image_path, smiles=1, extention=extention)
    def get_name(self) -> str:
        return "Chat"
    
class Crapaud(AnimalCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path=image_path, smiles=1, extention=extention)
    def get_name(self) -> str:
        return "Crapaud"
    
class Lapin(AnimalCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path=image_path, smiles=1, extention=extention)
    def get_name(self) -> str:
        return "Lapin"
    
class Poussin(AnimalCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path=image_path, smiles=1, extention=extention)
    def get_name(self) -> str:
        return "Poussin"
    