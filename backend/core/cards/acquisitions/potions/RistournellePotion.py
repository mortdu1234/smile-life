from typing import TYPE_CHECKING
from ....Power import Power
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
from .PotionCard import Potion


class RistournellePotion(Potion):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        current_player.add_power(Power.RISTOURNELLE)
        return True
    
    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_player_power(Power.RISTOURNELLE)
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """diminue le prix des acquisitions d'une liasse""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    