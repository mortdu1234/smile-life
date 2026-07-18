from backend.core.Game import Game
from backend.core.Player import Player

from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class BaguetteMagique(ObjetMagique):
    def calcul_cost(self, player: Player, game: Game) -> int:
        from backend.core.roles.Fee import Fee
        role = player.get_role()
        if isinstance(role, Fee):
            return 0
        return super().calcul_cost(player, game)
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from ...specials.SpecialCard import SpecialCard
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        interface = current_player.get_interface()
        specials_cards = current_player.get_card_from_group(groupe.SPECIAL)
        available_cards = []
        for card in specials_cards:
            success, reason = card.can_be_played(current_player, game)
            if success:
                available_cards.append(card)
        if len(available_cards) == 0:
            return True

        selected_card = interface.ask_card(
            prompt="Selectionner la carte spéciale à rejouer",
            cards=available_cards,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "error aucune carte sleectionnée"
        assert isinstance(selected_card, SpecialCard), "error la carte selectionnee nest pas une carte speciale"
        selected_card.apply_card_effect(game, current_player)
        
        return True
    
    def get_card_rule(self) -> str:
        return """permet de rejouer une carte spéciale déja jouée. Gratuit pour la fée.""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    