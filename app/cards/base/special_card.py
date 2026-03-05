"""
SpecialCard — classe abstraite pour les cartes spéciales.
Cible configurable. Aucun import Flask direct.
"""
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class SpecialCard(Card):
    """Carte spéciale — à usage unique ou conditionnelle."""

    def __init__(self, special_type: str, image_path: str):
        super().__init__(image_path)
        self.special_type: str = special_type
        self.smiles: int = 0

    def __str__(self) -> str:
        return f"{self.special_type} — SpecialCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "special", "subtype": self.special_type})
        return base

    def get_card_rule(self) -> str:
        return f"Carte Spéciale ({self.special_type}) — donne {self.smiles} smile(s)."

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        return True, ""

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)
