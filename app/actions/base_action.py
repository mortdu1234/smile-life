"""
app/actions/base_action.py — interface commune à toutes les actions.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.core.effect import CardEffect

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class BaseAction(ABC):
    """Applique un CardEffect sur les joueurs cibles."""

    @abstractmethod
    def apply(
        self,
        effect: CardEffect,
        game: "Game",
        current_player: "Player",
        target_player: "Player | None" = None,
    ) -> None:
        """Applique l'effet."""
        ...
