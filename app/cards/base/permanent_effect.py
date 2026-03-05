"""
Mixin PermanentEffet — cartes avec un pouvoir passif permanent.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class PermanentEffet:
    """Mixin pour les cartes qui accordent des pouvoirs permanents."""

    def get_power(self) -> list[str]:
        """Retourne la liste des tokens de pouvoir permanent."""
        return []
