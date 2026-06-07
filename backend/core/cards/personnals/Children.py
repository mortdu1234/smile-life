"""
Cartes enfants.
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player
    from .Flirts import FlirtWithChild
    from ....userIo.interface import UserIO
from ..Card import Card

# ------------------------------------------------------------------ #
#  Marqueurs de genre                                                  #
# ------------------------------------------------------------------ #

class FemaleChild(Card):
    """Mixin — enfant féminin."""

class MaleChild(Card):
    """Mixin — enfant masculin."""


class GirlPowerChild(Card):
    """Mixin — enfant girl-power."""


# ------------------------------------------------------------------ #
#  ChildCard                                                           #
# ------------------------------------------------------------------ #

class ChildCard(Card):
    """Carte enfant de base."""
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 2)

    def can_be_played(self, player: 'Player', game: 'Game') -> tuple[bool, str]:
        if not player.is_wedding() or (isinstance(player.get_last_flirt(), 'FlirtWithChild') and player.get_last_flirt().is_used()) : # type: ignore
            return False, "il faut etre marriée ou avoir un flirt pour enfant en dernier"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: 'Game', current_player: 'Player', interface: 'UserIO') -> bool:
        if not current_player.is_wedding() and isinstance(current_player.get_last_flirt(), 'FlirtWithChild'):
            current_player.get_last_flirt().set_used() # type: ignore
        return super().apply_card_effect(game, current_player, interface)

# ------------------------------------------------------------------ #
#  Enfants concrets                                                    #
# ------------------------------------------------------------------ #

class AngelaChild(ChildCard, GirlPowerChild):
    pass


class DianaChild(ChildCard, FemaleChild):
    pass


class HarryChild(ChildCard, MaleChild):
    pass


class HermioneChild(ChildCard, FemaleChild):
    pass


class LaraChild(ChildCard, FemaleChild):
    pass


class LeiaChild(ChildCard, FemaleChild):
    pass


class LouiseChild(ChildCard, GirlPowerChild):
    pass


class LuigiChild(ChildCard, MaleChild):
    pass


class MarioChild(ChildCard, MaleChild):
    pass


class LukeChild(ChildCard, MaleChild):
    pass


class OlympeChild(ChildCard, GirlPowerChild):
    pass


class RockyChild(ChildCard, MaleChild):
    pass


class SimoneChild(ChildCard, GirlPowerChild):
    pass


class ZeldaChild(ChildCard, FemaleChild):
    pass