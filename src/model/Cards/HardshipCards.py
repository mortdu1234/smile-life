from abc import ABC
from src.model.Card import Card 

class HardshipCards(Card, ABC):
    """
    Class for the hardship cards.
    """
    def __init__(self):
        super().__init__(smiles=0)