from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType

if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Chaudron(ObjetMagique):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from ..potions.PotionCard import Potion
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        acquisition_cards = current_player.get_card_from_group(groupe.ACQUISITIONS)
        potions_cards = []
        for card in acquisition_cards:
            if isinstance(card, Potion):
                potions_cards.append(card)

        if len(potions_cards) == 0:
            return True

        interface = current_player.get_interface()
    
        selected_card = interface.ask_card(
            prompt="selectionner la potion a rejouer",
            cards=potions_cards,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "error la carte n'est pas selectionnée"
        assert isinstance(selected_card, Potion), "error la carte n'est pas une potion"

        selected_card.discard_card(game, current_player)
        selected_card.apply_potion_effect(game, current_player)
        
        return True

    def get_card_rule(self) -> str:
        return """permet de rejouer une potion déja jouée (meme après désanchantement)""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    