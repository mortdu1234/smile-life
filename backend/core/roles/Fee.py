from typing import TYPE_CHECKING

from .PlayerRole import PlayerRole
from ..Power import Power
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player

class Fee(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.VALUE_SPECIAL_CARDS_2]

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.LuneBleu import LuneBleu
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, LuneBleu):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        from ..cards.personnals.Children import ChildCard
        for player in game.players:
            hand = player.get_hand()
            for card in hand:
                if isinstance(card, ChildCard):
                    player.remove_card_from_hand(card)
                    new_card = game._draw_card_from_deck()
                    player.add_card_to_hand(new_card)
                    owner.add_card_to_played(card)

        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : les cartes spéciales valents 2 smiles chacunes (pour les cartes spéciales du jeu de base) | PE (Lune Bleu) : récupérer et poser face a vous tous les enfants dans les mains"+ "\n"+ "="*10+ "\n" + super().get_card_rule()
