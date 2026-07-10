"""
Cartes enfants.
"""
from backend.core.Game import Game
from backend.core.Player import Player
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ...Power import Power
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player
    from ....userIo.interface import UserIO
from ..Card import Card


# ------------------------------------------------------------------ #
#  ChildCard                                                           #
# ------------------------------------------------------------------ #

class ChildCard(Card):
    """Carte enfant de base."""
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 2)

    def can_be_played(self, player: 'Player', game: 'Game') -> tuple[bool, str]:
        from .Flirts import FlirtWithChild
        if Power.CAN_PLAY_CHILD in player.get_power():
            return True, ""
        if not player.is_wedding() and not (isinstance(player.get_last_flirt(), FlirtWithChild) and not player.get_last_flirt().is_used()): # type: ignore
            return False, "il faut etre marriée ou avoir un flirt pour enfant en dernier"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: 'Game', current_player: 'Player') -> bool:
        from .Flirts import FlirtWithChild
        if not current_player.is_wedding() and isinstance(current_player.get_last_flirt(), FlirtWithChild):
            last_flirt = current_player.get_last_flirt()
            assert isinstance(last_flirt, FlirtWithChild), "Le dernier flirt du joueur n'est pas un FlirtWithChild" 
            last_flirt.set_used()
        return super().apply_card_effect(game, current_player)

    def get_name(self) -> str:
        return "Enfant - "

    def get_card_rule(self) -> str:
        return """Les enfant sont des cartes qui peuvent etre posé si le joueur est marié ou alors s'il a un flirt qui autorise un enfant."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()

# ------------------------------------------------------------------ #
#  Marqueurs de genre                                                  #
# ------------------------------------------------------------------ #

class FemaleChild(ChildCard):
    """Mixin — enfant féminin."""
    def get_smiles(self, owner: "Player") -> int:
        if Power.CHILDREN_PROTECTED in owner.get_power():
            return self.smiles
        if Power.GYNOCRATIE in owner.get_power():
            return self.smiles // 2
        return self.smiles
    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        from ..specials.GirlPower import GrilPower
        powers = current_player.get_power()
        if Power.GIRL_POWER in powers:
            played = current_player.get_card_from_group(groupe.CARTES_SPECIALES)
            for card in played:
                if isinstance(card, GrilPower):
                    card.girl_power_effect(game, current_player)
                    
        return super().apply_card_effect(game, current_player)

class MaleChild(ChildCard):
    """Mixin — enfant masculin."""
    def get_smiles(self, owner: "Player") -> int:
        if Power.CHILDREN_PROTECTED in owner.get_power():
            return self.smiles
        if Power.PHALOCRATIE in owner.get_power():
            return self.smiles // 2
        return self.smiles

class GirlPowerChild(ChildCard):
    """Mixin — enfant girl-power."""

class FantastiqueChild(ChildCard):
    pass

# ------------------------------------------------------------------ #
#  Enfants concrets                                                    #
# ------------------------------------------------------------------ #

class AngelaChild(GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Angela"


class DianaChild(FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Diana"


class HarryChild(MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Harry"


class HermioneChild(FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Hermione"


class LaraChild(FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Lara"


class LeiaChild(FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Leia"


class LouiseChild(GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Louise"


class LuigiChild(MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Luigi"


class MarioChild(MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Mario"


class LukeChild(MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Luke"


class OlympeChild(GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Olympe"


class RockyChild(MaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Rocky"


class SimoneChild(GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Simone"


class ZeldaChild(FemaleChild):
    def get_name(self) -> str:
        return super().get_name() + "Zelda"

class BeatrixChild(GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Beatrix"
    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        # recherche du sabre dans les cartes jouées
        from ..acquisitions.Sabre import Sabre
        for card in current_player.get_card_from_group(groupe.ACQUISITIONS):
            if isinstance(card, Sabre):
                card.sabre_effect(game, current_player)
        return super().apply_card_effect(game, current_player)

class DaenerysChild(GirlPowerChild):
    def get_name(self) -> str:
        return super().get_name() + "Daenerys"
    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        # recherche du dragon dans les cartes jouées
        from ..animals.Dragon import Dragon
        for card in current_player.get_card_from_group(groupe.VIE_PERSONNELLE):
            if isinstance(card, Dragon):
                card.dragon_effect(game, current_player)
        return super().apply_card_effect(game, current_player)

class PeterChild(FantastiqueChild):
    def get_name(self) -> str:
        return super().get_name() + "Peter"


class MerlinChild(FantastiqueChild):
    def get_name(self) -> str:
        return super().get_name() + "Merlin"


class BuffyChild(FantastiqueChild):
    def get_name(self) -> str:
        return super().get_name() + "Buffy"
