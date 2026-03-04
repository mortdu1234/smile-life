from abc import ABC
from src.model.Card import Card 

class PurchaseCards(Card, ABC):
    """
    Class for the purchase cards.
    """
    def __init__(self, smiles: int):
        super().__init__(smiles=smiles)