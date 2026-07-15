from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

from .MaleficeCard import MaleficeCard
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType

class Sacrapas(MaleficeCard):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None, "Aucun joueur selectionnée"
        self.target_player.add_power(Power.SALRAPAS)
        return True

    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_power(Power.SALRAPAS)
        return super().discard_card(game, owner)

    
    def get_card_rule(self) -> str:
        return """appoint necessaire pour acheter (payer exactement le prix indiqué) (NON FONCTIONNEL)"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()