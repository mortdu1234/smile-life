from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
from ....userIo.interface import IOType
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card
class Chance(SpecialCard):
    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        print("[DEBUG] TODO")
        available_cards = []
        for _ in range(3):
            available_cards.append(game.take_card_from_deck())
        selected_card: "Card | None" = interface.ask_card(prompt=f"Selection de la carte a piocher", cards=available_cards, kind=IOType.CARD_PICKER)
        if not selected_card:
            return False
        current_player.add_card_to_hand(selected_card)
        from ...Game import GameStateKey
        game.game_state[GameStateKey.CHANCE] += 1
        return super().apply_card_effect(game, current_player, interface)
