from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

from .MaleficeCard import MaleficeCard
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
class CasBurnas(MaleficeCard):
    def apply_malefice_effect(self, player: "Player", game: "Game") -> bool:
        success = super().apply_malefice_effect(player, game)
        if not success:
            return False

        assert self.target_player is not None, "Aucun joueur selectionnée"
        self.target_player.add_power(Power.CAN_BE_BURN_OUT)
        self.target_player.add_power(Power.CAN_BE_TAXED)
        return True
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        return self.apply_malefice_effect(current_player, game)


    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_power(Power.CAN_BE_BURN_OUT)
        owner.remove_power(Power.CAN_BE_TAXED)
                
        return super().discard_card(game, owner)

    
    def get_card_rule(self) -> str:
        return """impot et burn out posable sans métier. Cet effet passe au dessus de toutes les conditions"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()