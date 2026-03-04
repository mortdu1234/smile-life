from abc import ABC
from src.model.Card import Card 

class AnimalCards(Card, ABC):
    """
    Class for the animal cards.
    """
    def __init__(self, smiles: int):
        super().__init__(smiles=smiles)