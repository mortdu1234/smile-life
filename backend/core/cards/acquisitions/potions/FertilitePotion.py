from typing import TYPE_CHECKING
from ....Power import Power
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
from .PotionCard import Potion


class FertilitePotion(Potion):

    def apply_potion_effect(self, game: "Game", current_player: "Player"):
        current_player.add_power(Power.CAN_PLAY_CHILD)
        
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        self.apply_potion_effect(game, current_player)
        return True
    
    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_player_power(Power.CAN_PLAY_CHILD)
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """vous pouvez poser des enfants sans marriage""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    