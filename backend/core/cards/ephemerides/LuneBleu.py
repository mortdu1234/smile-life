from .Ephemeride import Ephemeride

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

class LuneBleu(Ephemeride):

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from ...Game import GameModes
        game.change_game_mode(GameModes.RIVER)
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        from ...Game import GameModes
        game.change_game_mode(GameModes.CLASSIC)
        return super().discard_card(game, owner)

    def get_name(self) -> str:
        return "Lune Bleu"

    def get_card_rule(self) -> str:
        return """Permet d'activer un mode rivière (affiche 3 cartes de la pioche, il est possible de piocher une carte parmis ces 3 cartes a la place de la pioche classique)."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()