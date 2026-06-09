from .AnimalCard import AnimalCard

class LicorneAnimal(AnimalCard):
    """Licorne — combo licorne + arc-en-ciel + étoile filante = +3 smiles."""
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=3)

    def get_name(self) -> str:
        return "Licorne"