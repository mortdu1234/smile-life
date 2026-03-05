"""
Deck — pioche du jeu.
"""
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.cards.base.card import Card


class Deck:
    """Gère la pioche : mélange et distribution."""

    def __init__(self, cards: list["Card"]):
        self._cards: list["Card"] = list(cards)

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def draw(self) -> "Card":
        if not self._cards:
            raise IndexError("La pioche est vide")
        return self._cards.pop()

    def peek(self, n: int = 1) -> list["Card"]:
        """Retourne les n dernières cartes sans les retirer."""
        return self._cards[-n:][::-1]

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self):
        return iter(self._cards)

    def to_list(self) -> list["Card"]:
        return list(self._cards)
