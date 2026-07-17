from typing import TYPE_CHECKING

from backend.core.Game import Game

from .PlayerRole import PlayerRole
from ..Power import Power
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player

class Chasseur(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.FREE_OBJET_MAGIQUE]

    def can_be_attribute(self, game: Game) -> tuple[bool, str]:
        if len(game.players) < 3:
            return False, "Pas assez de joueur"
        return super().can_be_attribute(game)

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.Ephemeride import Ephemeride
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, Ephemeride):
            return False, "Aucun ephemeride en cours"
        return super().can_use_instant_power(game, owner)
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantané du role"""
        game.set_ephemeride(None)
        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : objets magiques gratuits | PE  (tous): permet d'annuler une ephemeride"+ "\n"+ "="*10+ "\n" + super().get_card_rule()
