from ...Game import Game
from ...Player import Player
from ...Power import Power
from ..Card import Card
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class Chercheur(JobCard):
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path, extention)
        self.jobPower.append(Power.CAN_BE_PRICED)
        self.jobPower.append(Power.ADD_1_HAND_CARD)
        self.study = 6
        self.salary = 2
    def get_name(self) -> str:
        return "Chercheur"

    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        """Pioche une carte en plus afin d'en avoir 6"""
        if len(game.deck) > 0:
            game.take_card_from_deck_to_player_hand(current_player)
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: Game, owner: Player) -> None:
        selected_card : Card = random.choice(owner.hand)
        owner.remove_card_from_hand(selected_card)
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """Permet de jouer avec 6 cartes en main. Peut recevoir un Grand Prix d'excellence."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()