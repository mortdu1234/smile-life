from ...Game import Game
from ...Player import Player
from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
class Bandit(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.jobPower.append(Power.NO_TAX)
        self.jobPower.append(Power.NO_FIRE)
        self.study = 0
        self.salary = 4
    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        for player in game.players:
            if Power.NO_BANDIT in player.get_power():
                return False, "Il y a une personne qui bloque les bandits"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: Game, current_player: Player, interface: "UserIO") -> bool:
        """ajoute au joueur courrant la caracteristique has_been_bandit"""
        current_player.power.append(Power.HAS_BEEN_BANDIT)
        return super().apply_card_effect(game, current_player, interface)
    def get_name(self) -> str:
        return "Bandit"
    def get_card_rule(self) -> str:
        return """Le Bandit ne peut pas recevoir d'impot ni etre licencier. Si le joueur pose la carte bandit, il ne peut plus recevoir de légion d'honneur.\nAttention, peut recevoir la prison"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()