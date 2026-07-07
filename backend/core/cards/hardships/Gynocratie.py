from .HardshipCard import Hardship
from ...Power import Power
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Gynocratie(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        return super().can_be_targeted(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None
        self.target_player.add_power(Power.GYNOCRATIE)
        return True

    def get_name(self) -> str:
        return "Gynocratie"

    def get_card_rule(self) -> str:
        return """La Gynocratie fait diviser par 2 les smiles des enfants garçons à sa cible."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()