from .Ephemeride import Ephemeride

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

class LuneRouge(Ephemeride):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)

    def get_name(self) -> str:
        return "Lune Rouge"

    def get_card_rule(self) -> str:
        return """permet de se défausser de plusieurs cartes dans 1 tour, puis de repiocher."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()