from backend.core.Power import Power
from .HardshipCard import Hardship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.userIo.interface import UserIO


class Tax(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        # Vérifie si le joueur possède un métier
        if not player.get_job():
            return False

        # Vérifie si le joueur possède un salaire volable
        selected_salary = player.get_last_salary_placed()
        if not selected_salary:
            return False

        # Vérifie si le joueur est immunisé
        print(f"pouvoir du joueur '{player.name}':", player.get_power())
        if Power.NO_TAX in player.get_power():
            return False
        
        return super().can_be_targeted(player, game)
    def get_name(self) -> str:
        return "Impot sur le revenue"
    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        success = super().apply_card_effect(game, current_player, interface)
        if not success:
            return False
        assert self.target_player is not None
        last_salary = self.target_player.get_last_salary_placed()
        assert last_salary is not None
        self.target_player.remove_card(last_salary)
        game.add_card_to_discard(last_salary)
        return True

    def get_card_rule(self) -> str:
        return """L'impot est une carte qui fait perdre le dernier salaire posé. La cible doit obligatoirement travailler pour pouvoir subir ce malus."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()