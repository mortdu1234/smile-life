

from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Miroir(ObjetMagique):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        # récupération de l'ensemble des maléfices recus
        cards = current_player.get_card_from_group(groupe.HARDSHIP)
        available= []
        from ...hardships.Malefices.MaleficeCard import MaleficeCard
        for card in cards:
            if isinstance(card, MaleficeCard):
                available.append(card)

        # selection de la carte
        interface = current_player.get_interface()
        selected_card = interface.ask_card(
            prompt="selectionner le maléfice",
            cards=available,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None

        current_player.remove_card(selected_card, game)
        selected_card.play_card(game, current_player)

        return True
    
    def get_card_rule(self) -> str:
        return """renvoyer un maléfice recu au joueur de votre choix (un maléfice renvoyé a l'ange ne s'applique pas sur lui)""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    