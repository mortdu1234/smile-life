from typing import TYPE_CHECKING
from ...Power import Power

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
        if Power.RISTOURNELLE in player.get_power():
            return self.original_price - 1
        return self.original_price
        
    def _has_exact_salary_combination(self, salaries: list["SalaryCard"], cost: int) -> bool:
        """Vérifie s'il existe une combinaison de `salaries` dont la somme vaut exactement `cost`."""
        possible_sums = {0}
        for salary in salaries:
            possible_sums |= {total + salary.get_value() for total in possible_sums}
        return cost in possible_sums

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        salaries = player.get_available_salary()
        cost = self.calcul_cost(player, game)
        total = sum(salary.get_value() for salary in salaries)
        if total < cost:
            return False, "pas assez de salaire"
        if Power.SALRAPAS in player.get_power():
            if not self._has_exact_salary_combination(salaries, cost):
                return False, "impossible de payer exactement le prix de l'acquisition avec les salaires disponibles"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        """effectue la selection des salaires pour l'acquisition"""

        available_salaries = current_player.get_available_salary()
        interface = current_player.get_interface()
        cost = self.calcul_cost(current_player, game)
        must_pay_exact = Power.SALRAPAS in current_player.get_power()

        while True:
            selected_salaries: list[Card] = interface.ask_salaries(self, available_salaries, cost)

            if not must_pay_exact:
                print("CHOIIIIIIIIXXXX  1")
                break

            selected_sum = sum(card.get_value() for card in selected_salaries)
            if selected_sum == cost:
                print("CHOIIIIIIIIXXXX  2")
                break


            print(f"[ERROR] Power.SALRAPAS : le joueur doit payer exactement {cost}, mais a sélectionné un total de {selected_sum}")

        for card in selected_salaries:
            from backend.core.PlayerCardGroup import PlayedCardGroup
            from .objets_magiques.Amulette import Amulette
            from ..specials.Heritage import Heritage
            success = False
            if isinstance(card, Amulette):
                success = current_player.move_placed_cards(card, PlayedCardGroup.ACQUISITIONS, PlayedCardGroup.CARTES_PROTEGEES)
            elif isinstance(card, Heritage):
                success = current_player.move_placed_cards(card, PlayedCardGroup.CARTES_SPECIALES, PlayedCardGroup.CARTES_PROTEGEES)
            else:    
                success = current_player.move_placed_cards(card, PlayedCardGroup.VIE_PROFESSIONNELLE, PlayedCardGroup.CARTES_PROTEGEES)

                            
            if not success:
                print("[ERROR] déplace de carte échouée")
                return False
        return super().apply_card_effect(game, current_player)

    def get_card_rule(self) -> str:
        return """une acquisition peut etre achetée en dépensant un certain nombre MINIMUM de salaire. Les salaires disponibles pour etre utilisé dans une acquisition sont des salaires posé sur le terrain et dans la catégorie "Vie Professionnelle". Un salaire dépensé ne peux pas être dépensé a nouveau"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()