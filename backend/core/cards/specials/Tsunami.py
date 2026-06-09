from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
import random
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ...cards.Card import Card
class Tsunami(SpecialCard):
    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def get_name(self) -> str:
        return "Tsunami"
    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        nb_cards: list[int] = []
        cards: list["Card"] = []

        players = game.players
        for player in players:
            nb_cards.append(len(player.hand))
            cards.extend(player.hand)

        random.shuffle(cards)

        for i, player in enumerate(players):
            new_hand = [cards.pop() for _ in range(nb_cards[i])]
            player.hand = new_hand
        

        return super().apply_card_effect(game, current_player, interface)
    def get_card_rule(self) -> str:
        return """La carte tsunami permet de redistribuer aléatoirement toutes les cartes des mains."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()