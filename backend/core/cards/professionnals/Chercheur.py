from ...Game import Game
from ...Player import Player
from ...Power import Power
from ..Card import Card
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
import random

class Chercheur(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.CAN_BE_PRICED)
        self.jobPower.append(Power.MAX_HAND_CARD_6)
        self.study = 6
        self.salary = 2
    def get_name(self) -> str:
        return "Chercheur"

    def apply_card_effect(self, game: Game, current_player: Player, interface: "UserIO") -> bool:
        """Pioche une carte en plus afin d'en avoir 6"""
        card = game._draw_card_from_deck()
        current_player.add_card_to_hand(card)
        return super().apply_card_effect(game, current_player, interface)
    
    def discard_job(self, current_player: Player, game: Game):
        """retire une carte aléatoire de sa main et la jette dans la défausse"""
        selected_card : Card = random.choice(current_player.hand)
        current_player.remove_card_from_hand(selected_card)
        return super().discard_job(current_player, game)