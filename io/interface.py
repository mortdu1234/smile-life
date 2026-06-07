from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..backend.core.Player import Player
    from ..backend.core.cards.Card import Card

class IOType(Enum):
    HARDSHIP_TARGET = "hardship_target"

class UserIO(ABC):

    @abstractmethod
    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        pass

    @abstractmethod
    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        pass