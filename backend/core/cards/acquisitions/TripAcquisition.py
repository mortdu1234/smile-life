from ...Game import Game
from ...Player import Player
from ...Power import Power

from .Acquisition import Acquisition
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Trip(Acquisition):
    place: str
    def __init__(self, id: int, image_path: str, smiles: int, cost: int, place: str, extention: "Extention"):
        super().__init__(id, image_path, smiles, cost, extention)
        self.place = place
    def calcul_cost(self, player: Player, game: Game) -> int:
        if Power.TRAVEL_FREE in player.get_power():
            return 0
        return super().calcul_cost(player, game)

    def get_smiles(self, owner: Player) -> int:
        if Power.TRAVEL_DOUBLE in owner.get_power():
            return super().get_smiles(owner)*2 
        return super().get_smiles(owner)

    def get_name(self) -> str:
        return f"Voyage {self.place}"

    def get_card_rule(self) -> str:
        return """Un voyage n'a rien de particulier""" + "\n"+ "="*10+ "\n" + super().get_card_rule()

class Atlandide(Trip):
    def calcul_cost(self, player: Player, game: Game) -> int:
        from backend.core.roles.Sirene import Sirene
        role = player.get_role()
        if isinstance(role, Sirene):
            return 0
        return super().calcul_cost(player, game)

class Ecosse(Trip):
    def calcul_cost(self, player: Player, game: Game) -> int:
        from backend.core.roles.Chasseur import Chasseur
        role = player.get_role()
        if isinstance(role, Chasseur):
            return 0
        return super().calcul_cost(player, game)


class Salem(Trip):
    
    def calcul_cost(self, player: Player, game: Game) -> int:
        from backend.core.roles.Sorciere import Sorciere
        role = player.get_role()
        if isinstance(role, Sorciere):
            return 0
        return super().calcul_cost(player, game)


class Transylvanie(Trip):
    
    def calcul_cost(self, player: Player, game: Game) -> int:
        from backend.core.roles.Vampire import Vampire
        role = player.get_role()
        if isinstance(role, Vampire):
            return 0
        return super().calcul_cost(player, game)

