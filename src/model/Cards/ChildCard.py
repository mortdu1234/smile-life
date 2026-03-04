from abc import ABC
from src.model.Card import Card 

class ChildCard(Card, ABC):
    """
    Class for the child cards.
    """
    def __init__(self):
        super().__init__(smiles=2)