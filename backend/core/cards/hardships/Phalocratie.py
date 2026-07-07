from backend.core.Game import Game
from backend.core.Player import Player

from .HardshipCard import Hardship
from ...Power import Power
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Phalocratie(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        return super().can_be_targeted(player, game)

    def hardship_effect(self, game: Game, target: Player) -> bool:

        target.add_power(Power.PHALOCRATIE)
        return super().hardship_effect(game, target)
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None
        self.hardship_effect(game, self.target_player)
        return True

    def get_name(self) -> str:
        return "Phalocratie"

    def get_card_rule(self) -> str:
        return """La Phalocratie fait diviser par 2 les smiles des enfants filles à sa cible."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()