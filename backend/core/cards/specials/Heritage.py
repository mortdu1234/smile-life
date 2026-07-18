from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player

from backend.core.cards.CardAttributes import CanBeUseOnAcquisition
class Heritage(SpecialCard, CanBeUseOnAcquisition):
    def __init__(self, id: int, image_path: str, smiles: int, value: int):
        super().__init__(id, image_path, smiles)
        self.set_value(value)
    def to_dict(self) -> dict:
        data = super().to_dict()
        for key, value in CanBeUseOnAcquisition.to_dict(self).items():
            data[key] = value
        return data

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:        
        return super().apply_card_effect(game, current_player)

    def get_name(self) -> str:
        return f"Héritage {self.value}"

    def get_card_rule(self) -> str:
        return f"Quand la carte héritage est posé, elle vaut comme un salaire {self.value} et peut etre utiliser comme tel"+ "\n"+ "="*10+ "\n" + super().get_card_rule()