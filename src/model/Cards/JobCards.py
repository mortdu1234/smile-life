from abc import ABC
from src.model.Card import Card 

class JobCards(Card, ABC):
    """
    Class for the job cards.
    """
    def __init__(self, smiles: int):
        super().__init__(smiles=smiles)