from typing import TYPE_CHECKING
from ...cards.Card import Card
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    

class SpecialCard(Card):
    def __init__(self, id: int, image_path: str, smiles: int):
        super().__init__(id, image_path, smiles)

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        return super().apply_card_effect(game, current_player, interface)

    

