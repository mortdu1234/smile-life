from backend.core.Game import Game
from backend.core.Player import Player

from .HardshipCard import Hardship
from ...Power import Power
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class PlafondDeVerre(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        return super().can_be_targeted(player, game)

    def hardship_effect(self, game: Game, target: Player) -> bool:
        target.add_power(Power.JOB_MAX_STUDY_4)
        return super().hardship_effect(game, target)
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None
        self.hardship_effect(game, self.target_player)
        return True

    def discard_card(self, game: Game, owner: Player) -> None:
        owner.remove_player_power(Power.JOB_MAX_STUDY_4)
        return super().discard_card(game, owner)

    
    def get_name(self) -> str:
        return "Plafond de Verre"

    def get_card_rule(self) -> str:
        return """la cible ne peux pas poser de métier avec plus de 4 niveau d'étude. Si un joueur possède déja un métier avec plus de 4 niveau d'étude ce métier est gardé."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()