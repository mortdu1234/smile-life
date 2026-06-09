from .AnimalCard import AnimalCard

class Chien(AnimalCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=1)
    def get_name(self) -> str:
        return "Chien"
    
class Chat(AnimalCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=1)
    def get_name(self) -> str:
        return "Chat"
    
class Crapaud(AnimalCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=1)
    def get_name(self) -> str:
        return "Crapaud"
    
class Lapin(AnimalCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=1)
    def get_name(self) -> str:
        return "Lapin"
    
class Poussin(AnimalCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=1)
    def get_name(self) -> str:
        return "Poussin"
    