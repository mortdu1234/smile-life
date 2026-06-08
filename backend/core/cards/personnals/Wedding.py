from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

from ..Card import Card

class Wedding(Card):
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        if player.get_last_flirt() is None:
            return False, "il faut avoir fait au moins 1 flirt"
        return super().can_be_played(player, game)

    def can_be_discard(self, player: "Player", game: "Game") -> tuple[bool, str]:
        """vérifie si on peut annuler son marriage ou non"""
        from ...Game import GameState
        if game.game_state == GameState.PIOCHE:
            return True, ""
        return False, "on ne peut divorcer que avant de piocher"

class Adultery(Card):
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        if not player.is_wedding():
            return False, "il faut etre marriée"
        return super().can_be_played(player, game)
    
    def can_be_discard(self, player: "Player", game: "Game") -> tuple[bool, str]:
        """vérifie si on peut annuler son adultère ou non"""
        from ...Game import GameState
        if game.game_state == GameState.PIOCHE:
            return True, ""
        return False, "on ne peut quitter son adultère que avant de piocher"
