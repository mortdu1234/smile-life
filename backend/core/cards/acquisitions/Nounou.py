from ...Game import Game
from ...Player import Player
from ...Power import Power

from .Acquisition import Acquisition

class Nounou(Acquisition):
    def __init__(self, id: int, image_path: str, smiles: int, cost: int):
        super().__init__(id, image_path, smiles, cost)

    def calcul_cost(self, player: Player, game: Game) -> int:
        return super().calcul_cost(player, game)

    def get_name(self) -> str:
        return "Nounou"

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        current_player.add_power(Power.CHILDREN_PROTECTED)
        return True

    def get_card_rule(self) -> str:
        return """Protège tous les enfants posé par le joueur de tous les malus""" + "\n"+ "="*10+ "\n" + super().get_card_rule()