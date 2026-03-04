from abc import ABC, abstractmethod
from uuid import UUID, uuid4

class Card(ABC):
    def __init__(self, smiles: int):
        self.cardID: UUID = uuid4()
        self.smiles: int = smiles
        self.imagesSource: str = ""

    @abstractmethod
    def getRule(self) -> str:
        pass

    def canBePlayed(self, currentPlayer: 'Player', target: 'Player') -> bool:
        return True

    def applyCardEffect(self, currentPlayer: 'Player', target: 'Player'):
        pass
    