from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
from .PotionCard import Potion

class ArgentPotion(Potion):
    def apply_potion_effect(self, game: "Game", current_player: "Player"):
        from ...professionnals.SalaryCard import SalaryCard
        salaires_depensee = current_player.get_card_from_group(groupe.SALARIES_USED)
        for card in salaires_depensee:
            card.set_not_protected()
            current_player.move_placed_cards(card, groupe.SALARIES_USED, groupe.SALARIES)
                

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        self.apply_potion_effect(game, current_player)
        return True
    
    def get_card_rule(self) -> str:
        return """tous vos salaires sont a nouveau disponible pour etre réutilisé (attention ils peuvent aussi etre perdu)""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
        