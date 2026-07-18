from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Player import Player
    from ..Game import Game

class CanBeUseOnAcquisition:
    value: int # la valeur de la carte lors d'achat 
    is_used: bool=False # si la carte a déja été utilisé lors d'un achat
    def get_value(self) -> int:
        return self.value
    def set_value(self, new_value: int):
        self.value = new_value
    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "is_used": self.is_used,
        }
    def on_use_card(self, game: "Game", owner: "Player") -> bool:
        """applique l'effet quand on utilise cette carte"""
        self.is_used = True
        return True