from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from .....userIo.interface import IOType
from ....PlayerCardGroup import PlayedCardGroup as groupe
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player


class CapeInvisible(ObjetMagique):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

              
        cards_availables = current_player.get_card_from_group(groupe.ACQUISITIONS).copy()
        cards_availables += current_player.get_card_from_group(groupe.CARTES_SPECIALES)
        cards_availables += current_player.get_card_from_group(groupe.VIE_PERSONNELLE)
        cards_availables += current_player.get_card_from_group(groupe.VIE_PROFESSIONNELLE)
        if len(cards_availables) == 0:
            return True
        

        interface = current_player.get_interface()
        selected_card = interface.ask_card(
            prompt="Selectionner la carte a protéger",
            cards=cards_availables,
            kind=IOType.CARD_PICKER
        )

        assert selected_card is not None, "error la carte n'est pas selectionnées"
        origin_group = current_player.get_group(selected_card)
        assert origin_group is not None, "error le groupe d'origine n'est pas trouvé"
        current_player.move_placed_cards(selected_card, origin_group, groupe.CARTES_PROTEGEES)

        return True
    
    def get_card_rule(self) -> str:
        return """protéger une carte posée au moment ou le joueur pose la cape.""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    