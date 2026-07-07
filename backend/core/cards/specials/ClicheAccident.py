from backend.core.Game import Game
from backend.core.Player import Player

from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
from ...Power import Power
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card

class ClicheAccident(SpecialCard):    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)
    
    def get_name(self) -> str:
        return "Cliché Accident"
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        current_player.add_power(Power.NO_ACCIDENT)
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: Game, owner: Player) -> None:
        owner.remove_player_power(Power.NO_ACCIDENT)
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """Ne peut pas subir d'accident."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()