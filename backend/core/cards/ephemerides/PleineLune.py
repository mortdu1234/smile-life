from .Ephemeride import Ephemeride

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

class PleineLune(Ephemeride):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)

    def get_name(self) -> str:
        return "Pleine Lune"

    def get_card_rule(self) -> str:
        return """on pioche une carte, puis on peut poser plusieurs cartes devant soit avant de repiocher pour reremplir la main"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()