from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class AnneauDePouvoir(ObjetMagique):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        current_player.add_power(Power.CANT_PLACE_CARD)
        return True
    
    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_player_power(Power.CANT_PLACE_CARD)
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """une fois posé, le joueur ne peut plus poser de carte (sauf si il est démon)""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    