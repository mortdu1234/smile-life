from typing import TYPE_CHECKING

from ...cards.Card import InstantPlayedCard
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player
    from backend.core.cards.CardAttributes import Extention

class Ephemeride(InstantPlayedCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, 0, extention)
    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def play_card(self, game: "Game", current_player: "Player") -> None:
        old_ephemeride = game.get_ephemeride()
        if old_ephemeride:
            old_ephemeride.discard_card(game, current_player)


        self.apply_card_effect(game, current_player)
        current_player.remove_card_from_hand(self)
        game.set_ephemeride(self)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)

    
    def get_card_rule(self) -> str:
        return """Les Ephemerides sont des cartes spéciales qui lorsqu'elles sont pioché sont directement posé et influe sur la partie. Le joueur qui la pioche passe son tour."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()

