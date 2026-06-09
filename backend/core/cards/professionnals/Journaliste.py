from ...Game import Game
from ...Player import Player
from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
class Journaliste(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.CAN_BE_PRICED)
        self.study = 3
        self.salary = 2
    def get_name(self) -> str:
        return "Journaliste"
    def apply_card_effect(self, game: Game, current_player: Player, interface:"UserIO") -> bool:
        """permet de voir la main de chaque joueur"""
        current_player.remove_card_from_hand(self)
        players = game.players
        players_names = [player.name for player in players]
        players_hands = [player.hand for player in players]
        interface.show_players_hand(players_names, players_hands)
        current_player.add_card_to_hand(self)
        return super().apply_card_effect(game, current_player, interface)
    def get_card_rule(self) -> str:
        return """Quand la carte est posé, permet de voir les mains de tous les joueurs. Peut recevoir un Grand Prix d'Excellence."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()