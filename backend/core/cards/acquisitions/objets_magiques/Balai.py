from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Balai(ObjetMagique):
    def calcul_cost(self, player: "Player", game: "Game") -> int:
        from backend.core.roles.Sorciere import Sorciere
        role = player.get_role()
        if isinstance(role, Sorciere):
            return 0
        return super().calcul_cost(player, game)
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        current_player.add_power(Power.TRAVEL_FREE)
        current_player.add_power(Power.TRAVEL_DOUBLE)
        return True
    
    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_player_power(Power.TRAVEL_FREE)
        owner.remove_player_power(Power.TRAVEL_DOUBLE)
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """les voyages compte double et sont gratuit. Gratuit pour la sorcière""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    