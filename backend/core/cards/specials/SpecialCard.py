from backend.core.PlayerCardGroup import PlayedCardGroup as groupe
from backend.userIo.interface import IOType
from typing import TYPE_CHECKING

from backend.core.cards.Card import Card
if TYPE_CHECKING:
    from backend.userIo.interface import UserIO
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.core.cards.Card import Card
    from backend.core.cards.CardAttributes import Extention

class SpecialCard(Card):
    def __init__(self, id: int, image_path: str, smiles: int, extention: "Extention"):
        super().__init__(id, image_path, smiles, extention)

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        return super().apply_card_effect(game, current_player)

    

