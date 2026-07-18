from typing import TYPE_CHECKING

from .PlayerRole import PlayerRole
from ..PlayerCardGroup import PlayedCardGroup as groupe
from ..Power import Power
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player

class Vampire(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.DOUBLE_FLIRT]

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.LuneRouge import LuneRouge
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, LuneRouge):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        from ..cards.personnals.Flirts import Flirt
        # récupérations des lieux du joueurs actuel
        played = owner.get_card_from_group(groupe.VIE_PERSONNELLE)
        flirts_played = []
        for card in played:
            if isinstance(card, Flirt):
                flirts_played.append(card.get_place())

        # recherche dans les autres joueurs
        for player in game.players:
            if player == owner:
                continue
            cards = player.get_card_from_group(groupe.VIE_PERSONNELLE)
            for card in cards:
                if isinstance(card, Flirt) and card.get_place() in flirts_played and not card.is_protected:
                    player.remove_card(card, game)
                    owner.add_card_to_played(card)


        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : vos flirts valent double smile | PE (Lune Rouge) : récupérer tous les flirts posé qui sont en doublons avec les votres sans conditions"+ "\n"+ "="*10+ "\n" + super().get_card_rule()
