"""
Cartes enfants.
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player
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
        from .Flirts import FlirtWithChild
        if not player.is_wedding() or (isinstance(player.get_last_flirt(), FlirtWithChild) and player.get_last_flirt().is_used()) : # type: ignore
            return False, "il faut etre marriée ou avoir un flirt pour enfant en dernier"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: 'Game', current_player: 'Player', interface: 'UserIO') -> bool:
        from .Flirts import FlirtWithChild
        if not current_player.is_wedding() and isinstance(current_player.get_last_flirt(), FlirtWithChild):
            current_player.get_last_flirt().set_used() # type: ignore
        return super().apply_card_effect(game, current_player, interface)

    def get_name(self) -> str:
        return "Enfant - "

    def get_card_rule(self) -> str:
        return """Les enfant sont des cartes qui peuvent etre posé si le joueur est marié ou alors s'il a un flirt qui autorise un enfant."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()

# ------------------------------------------------------------------ #
#  Enfants concrets                                                    #
# ------------------------------------------------------------------ #

class AngelaChild(ChildCard, GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Angela"


class DianaChild(ChildCard, FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Diana"


class HarryChild(ChildCard, MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Harry"


class HermioneChild(ChildCard, FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Hermione"


class LaraChild(ChildCard, FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Lara"


class LeiaChild(ChildCard, FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Leia"


class LouiseChild(ChildCard, GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Louise"


class LuigiChild(ChildCard, MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Luigi"


class MarioChild(ChildCard, MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Mario"


class LukeChild(ChildCard, MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Luke"


class OlympeChild(ChildCard, GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Olympe"


class RockyChild(ChildCard, MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Rocky"


class SimoneChild(ChildCard, GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Simone"


class ZeldaChild(ChildCard, FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Zelda"