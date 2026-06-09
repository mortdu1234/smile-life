from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
class Heritage(SpecialCard):
    value: int
    def __init__(self, id: int, image_path: str, smiles: int, value: int):
        super().__init__(id, image_path, smiles)
        self.value = value
    def get_value(self)->int:
        return self.value
    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:        
        return super().apply_card_effect(game, current_player, interface)

    def get_name(self) -> str:
        return f"Héritage {self.value}"

    def get_card_rule(self) -> str:
        return f"Quand la carte héritage est posé, elle vaut comme un salaire {self.value} et peut etre utiliser comme tel"+ "\n"+ "="*10+ "\n" + super().get_card_rule()