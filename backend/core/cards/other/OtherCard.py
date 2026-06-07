from ..Card import Card

class OtherCard(Card):
    def __init__(self, id: int, image_path: str, smiles: int):
        super().__init__(id, image_path, smiles)