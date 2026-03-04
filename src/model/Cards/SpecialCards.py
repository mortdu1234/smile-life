from abc import ABC
from src.model.Card import Card 

class SpecialCards(Card, ABC):
    """
    Class for the special cards.
    """
    def __init__(self, smiles: int):
        super().__init__(smiles=smiles)