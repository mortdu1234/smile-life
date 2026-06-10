from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
class ArcEnCiel(SpecialCard):
    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)
    def get_name(self) -> str:
        return "Arc En Ciel"
    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        from ...Game import GameStateKey
        # Ajoute 3 tours d'arc en ciel
        game.game_state[GameStateKey.ARC_EN_CIEL] = 3+1       
        return super().apply_card_effect(game, current_player, interface)
    def get_card_rule(self) -> str:
        return """L'arc en ciel permet de poser jusqu'a 3 cartes a se suivre avant de repiocher."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()