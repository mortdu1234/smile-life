from backend.core.Game import Game
from backend.core.Player import Player

from .AnimalCard import AnimalCard
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ...Power import Power
from ....userIo.interface import IOType

class Hibou(AnimalCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=1)

    def get_name(self) -> str:
        return "Hibou"

    def get_card_rule(self) -> str:
        return """"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()