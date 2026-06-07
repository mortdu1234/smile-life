from .SpecialCard import SpecialCard

class Heritage(SpecialCard):
    value: int
    def __init__(self, id: int, image_path: str, smiles: int, value: int):
        super().__init__(id, image_path, smiles)
        self.value = value
    def get_value(self)->int:
        return self.value