from click import group

from backend.core.Game import Game
from backend.core.Player import Player

from .AnimalCard import AnimalCard
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ...Power import Power
from ....userIo.interface import IOType
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Phoenix(AnimalCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path=image_path, smiles=2, extention=extention)

    def get_name(self) -> str:
        return "Phoenix"

    def get_smiles(self, owner: Player) -> int:
        from backend.core.cards.acquisitions.potions.ResurrectionPotion import ResurrectionPotion
        zone = owner.get_card_from_group(groupe.ACQUISITIONS)
        for card in zone:
            if isinstance(card, ResurrectionPotion):
                return 2*super().get_smiles(owner)
        return super().get_smiles(owner)
    
    def get_card_rule(self) -> str:
        return """"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()