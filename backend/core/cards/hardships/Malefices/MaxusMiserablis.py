from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

from .MaleficeCard import MaleficeCard
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
class MaxusMiserablis(MaleficeCard):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        current_player.add_power(Power.NO_SALARY_4)
        return True

    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_power(Power.NO_SALARY_4)
        return super().discard_card(game, owner)

    
    def get_card_rule(self) -> str:
        return """aucun salaire de niveau 4 posable"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()