from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ..core.Player import Player
    from ..core.cards.Card import Card
    from ..core.cards.acquisitions.Acquisition import Acquisition

class IOType(Enum):
    HARDSHIP_TARGET = "hardship_target"
    SALARY_SELECTOR = "salary_selector"

class UserIO(ABC):

    @abstractmethod
    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        pass

    @abstractmethod
    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        pass

    @abstractmethod
    def ask_salaries(self, acquisition: "Acquisition", salaries: Sequence["Card"], cost: int) -> list["Card"]:
        """Demande au joueur de sélectionner des salaires pour payer une acquisition.
        Retourne la liste des cartes salaire choisies (somme >= cost garanti côté frontend)."""
        pass