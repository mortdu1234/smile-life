from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
from ...Power import Power
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card

class SoireeEntreFille(SpecialCard):    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)
    
    def get_name(self) -> str:
        return "soirée entre filles"
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from ..personnals.Children import FemaleChild
        players = game.players
        for player in players:
            filles = []
            hand = player.get_hand()
            for card in hand:
                if isinstance(card, FemaleChild):
                    filles.append(card)
                    current_player.add_card_to_played(card)
            for card in filles:
                player.remove_card_from_hand(card)
                game.take_card_from_deck_to_player_hand(current_player)

        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """Permet de poser l'ensemble des filles dans les mains des joueurs sans autre conditions."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()