from ..Card import Card

class Hardship(Card):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 0)
