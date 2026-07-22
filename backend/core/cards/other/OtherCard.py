from ..Card import Card
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class OtherCard(Card):
    def __init__(self, id: int, image_path: str, smiles: int, extention: "Extention"):
        super().__init__(id, image_path, smiles, extention)