from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player
    from ....userIo.interface import UserIO
    from ..professionnals.SalaryCard import SalaryCard
    from ..specials.Heritage import Heritage
from ..Card import Card

class Acquisition(Card):
    original_price: int
    def __init__(self, id: int, image_path: str, smiles: int, cost: int):
        super().__init__(id, image_path, smiles)
        self.original_price = cost

    def calcul_cost(self, player: "Player", game: "Game") -> int:
        """retourne le prix de l'acquisition"""
        return self.original_price
        
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        salaries = player.get_available_salary()
        sum = 0
        cost = self.calcul_cost(player, game)
        for salary in salaries:
            sum += salary.get_value()
        if sum < cost:
            return False, "pas assez de salaire"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        """effectue la selection des salaires pour l'acquisition"""
        available_salaries = current_player.get_available_salary()

        selected_salaries: list[Card] = interface.ask_salaries(self, available_salaries, self.calcul_cost(current_player, game))
        for card in selected_salaries:
            from backend.core.PlayerCardGroup import PlayedCardGroup
            success = current_player.move_placed_cards(card, PlayedCardGroup.VIE_PROFESSIONNELLE, PlayedCardGroup.SALAIRES_DEPENSES)
            if not success:
                print("[ERROR] déplace de carte échouée")
                return False
        return super().apply_card_effect(game, current_player, interface)
    