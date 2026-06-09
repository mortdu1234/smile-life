from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player
    from ....userIo.interface import UserIO
from ...FlirtPlaces import FlirtPlaces
from ...PlayerCardGroup import PlayedCardGroup
from ...Power import Power

from ..Card import Card

NOMBRE_MAX_FLIRT_PAR_JOUEUR = 5

class Flirt(Card):
    place: FlirtPlaces
    def __init__(self, id: int, image_path: str, smiles: int, place: FlirtPlaces):
        super().__init__(id, image_path, smiles)
        self.place = place
    def get_name(self) -> str:
        return f"Flirt - {self.place}"
    
    def count_number_flirt(self, player: 'Player'):
        number = 0
        cards = player.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE)
        for card in cards:
            if isinstance(card, Flirt):
                number += 1
        return number

    def can_be_played(self, player: 'Player', game: 'Game') -> tuple[bool, str]:
        if player.is_wedding() and not player.is_adultery():
            return False, "on ne peut pas flirter en couple"
        if self.count_number_flirt(player) == NOMBRE_MAX_FLIRT_PAR_JOUEUR and Power.INFINITE_FLIRT not in player.get_power():
            return False, "tu as déja ateint la limite"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: 'Game', current_player: 'Player', interface: 'UserIO') -> bool:
        """vole le dernier flirt de quelqu'un si ceux si sont les mêmes"""
        players = game.players
        for player in players:
            if player != current_player:
                last_flirt = player.get_last_flirt()
                if last_flirt and last_flirt.get_place() == self.place:
                    player.remove_card(last_flirt)
                    current_player.add_card_to_played(last_flirt)
        return super().apply_card_effect(game, current_player, interface)
    
    def get_place(self) -> FlirtPlaces:
        return self.place

class FlirtWithChild(Flirt):
    used: bool = False
    def is_used(self) -> bool:
        return self.used
    def set_used(self) -> None:
        self.used = True