from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

from .MaleficeCard import MaleficeCard
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
class Desenchantement(MaleficeCard):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False

        # selection de la carte
        assert self.target_player is not None, "aucune cible n'est choisi"

        # récupérer l'ensemble des cartes acquisition potion / objet magique
        from ...acquisitions.objets_magiques.ObjetMagique import ObjetMagique
        from ...acquisitions.potions.PotionCard import Potion
        availables_cards = []
        cards = self.target_player.get_card_from_group(groupe.ACQUISITIONS)
        for card in cards:
            if isinstance(card, (Potion, ObjetMagique)):
                availables_cards.append(card)

        if len(availables_cards) == 0:
            return True

        interface = current_player.get_interface()
        selected_card = interface.ask_card(
            prompt="Choisir une carte pour retirer son effet",
            cards=availables_cards,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "aucune cartes selectionnée"

        # retire l'effet de cette carte
        selected_card.discard_card(game, self.target_player)
        

        return True

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)

    
    def get_card_rule(self) -> str:
        return """annule l'effet permanent d'une potion ou objet"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()