from ..Card import Card
from typing import Dict, Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Player import Player
    from ...Game import Game

class AnimalCard(Card):
    """Carte animal de base."""

    def __init__(self, id: int, image_path: str, smiles: int):
        super().__init__(id, image_path=image_path, smiles=smiles)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        return base

    def get_card_rule(self) -> str:
        return f"Carte Animal — {self.smiles} smiles. Jouable à tout moment.\n"

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return True, ""

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)
