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
        cartes_protegees = current_player.get_card_from_group(groupe.CARTES_PROTEGEES)
        for card in cartes_protegees:
            if isinstance(card, SalaryCard):
                current_player.move_placed_cards(card, groupe.CARTES_PROTEGEES, groupe.VIE_PROFESSIONNELLE)
                

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        self.apply_potion_effect(game, current_player)
        return True
    
    def get_card_rule(self) -> str:
        return """tous vos salaires sont a nouveau disponible pour etre réutilisé (attention ils peuvent aussi etre perdu)""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
        