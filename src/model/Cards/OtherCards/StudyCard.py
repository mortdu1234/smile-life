from enum import Enum

from src.model.Card import Card


class StudyType(Enum):
    """
    Enum for the different types of Study Cards.
    """
    SIMPLE = 1
    DOUBLE = 2

class StudyCard(Card):
    """
    Class representing a Study Card in the game.
    """
    def __init__(self, type: StudyType):
        super().__init__(smiles=1)
        self.study_type: StudyType = type

    def getRule(self) -> str:
        return "Nous avons une carte d'étude\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il s'agit d'une etdue {self.study_type.name} elle donne {self.study_type.value} niveaux d'étude\n" \
        + "\nREGLES\n" \
        + "- il est possible de jouer cette carte que quand on n'a pas de métier\n" \
        + "- permet d'avoir un métier meilleur\n" \
        + "- il est interdit d'avoir plus de 6 cartes études de poser au total (sauf cas spécial)"
    
    def canBePlayed(self, currentPlayer: 'Player', target: 'Player') -> bool:
        if currentPlayer.getJob() is not None:
            return False
        return super().canBePlayed(currentPlayer, target)
