from backend.core.Power import Power
from .HardshipCard import Hardship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.userIo.interface import UserIO


class BurnOut(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        # Vérifie si le joueur possède un métier
        if not player.get_job():
            return False
        
        # Vérifie si le joueur est immunisé
        print(f"pouvoir du joueur '{player.name}':", player.get_power())
        if Power.NO_BURNOUT in player.get_power():
            return False
        
        return super().can_be_targeted(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        success = super().apply_card_effect(game, current_player, interface)
        if not success:
            return False
        assert self.target_player is not None
        self.target_player.add_skip_turn(1)
        return True

    def get_name(self) -> str:
        return "Burn Out"

    def get_card_rule(self) -> str:
        return """Le Burn Out fait passé 1 tour à sa cible. Sa cible doit avoir un métier pour pouvoir subir un burn out."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()