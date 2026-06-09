from backend.core.Power import Power
from .HardshipCard import Hardship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.userIo.interface import UserIO


class Redoublement(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        # Vérifie si le joueur possède un métier
        if player.get_job():
            return False

        # Vérifie si le joueur possède un etude
        selected_study = player.get_last_study_placed()
        if not selected_study:
            return False

        # Vérifie si le joueur est immunisé
        print(f"pouvoir du joueur '{player.name}':", player.get_power())
        if Power.NO_REDOUBLEMENT in player.get_power():
            return False
        
        return super().can_be_targeted(player, game)
    def get_name(self) -> str:
        return "Redoublement"
    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        success = super().apply_card_effect(game, current_player, interface)
        if not success:
            return False
        assert self.target_player is not None
        last_study = self.target_player.get_last_study_placed()
        assert last_study is not None
        self.target_player.remove_card(last_study)
        game.add_card_to_discard(last_study)
        return True
