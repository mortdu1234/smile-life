from .Ephemeride import Ephemeride
from ...Power import Power
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

class Equinoxe(Ephemeride):

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        players = game.players
        for player in players:
            player.add_power(Power.INSTANT_QUIT_JOB)
            player.add_power(Power.INSTANT_QUIT_WEDDING)
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        players = game.players
        for player in players:
            player.remove_player_power(Power.INSTANT_QUIT_JOB)
            player.remove_player_power(Power.INSTANT_QUIT_WEDDING)
        return super().discard_card(game, owner)

    def get_name(self) -> str:
        return "Equinoxe"

    def get_card_rule(self) -> str:
        return """permet de démissioner ou de divorcer sans passer de tours"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()