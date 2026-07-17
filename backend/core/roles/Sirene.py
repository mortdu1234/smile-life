from typing import TYPE_CHECKING

from zope import interface

from backend.core.cards.ephemerides import Eclipse
from .PlayerRole import PlayerRole
from ..Power import Power
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player

class Sirene(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.INFINITE_FLIRT, Power.CAN_FLIRT_WITH_WEDDING]

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.Eclipse import Eclipse
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, Eclipse):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        all_hands = []
        all_players = []
        for player in game.players:
            all_hands.append(player.get_hand())
            all_players.append(player)

        interface = owner.get_interface()
        
        new_hands = interface.reorder_hands(all_players, all_hands)
        print(f"debug nesw hands =====> {new_hands}")
        for idx, player in enumerate(game.players):
            player.hand = new_hands[idx]
        
        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : permet de poser des flirts pendant le marriage et flirt infini | PE (Eclipse) : prennez toutes les cartes en main et les redistribuer a votre guise."+ "\n"+ "="*10+ "\n" + super().get_card_rule()
