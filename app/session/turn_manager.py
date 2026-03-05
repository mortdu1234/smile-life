"""
app/session/turn_manager.py — Timer et gestion automatique des tours.
"""
import threading
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from app.core.game import Game
    from app.core.player import Player


class TurnManager:
    """Gère le timer de tour et passe automatiquement au joueur suivant."""

    def __init__(self, game: "Game", turn_duration: int = 60):
        self.game = game
        self.turn_duration: int = turn_duration
        self._timer: threading.Timer | None = None

    def start_turn(self, on_timeout: Callable | None = None) -> None:
        self.cancel()
        self._timer = threading.Timer(
            self.turn_duration,
            self._on_timeout if on_timeout is None else on_timeout,
        )
        self._timer.daemon = True
        self._timer.start()

    def cancel(self) -> None:
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _on_timeout(self) -> None:
        """Passe automatiquement au tour suivant si le joueur n'a pas joué."""
        self.game.next_player()
        self.game.broadcast_update("Tour terminé automatiquement.")
        self.start_turn()
