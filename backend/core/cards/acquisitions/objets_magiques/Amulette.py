from backend.core.Game import Game
from backend.core.Player import Player

from .ObjetMagique import ObjetMagique
from backend.core.cards.CardAttributes import CanBeUseOnAcquisition
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Amulette(ObjetMagique, CanBeUseOnAcquisition):
    def __init__(self, id: int, image_path: str, smiles: int, cost: int):
        super().__init__(id, image_path, smiles, cost)
        self.set_value(999)
    def to_dict(self) -> dict:
        data = super().to_dict()
        for key, value in CanBeUseOnAcquisition.to_dict(self).items():
            data[key] = value
        return data
    def apply_talisment_effect(self, game: Game, current_player: Player):
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
        current_player.add_card_to_hand(selected_card)
        selected_card.play_card(game, current_player)


    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        # vérifie si le joueur possède une autre amulette
        cards = current_player.get_card_from_group(groupe.ACQUISITIONS)
        talisment = False
        for card in cards:
            if isinstance(card, Amulette):
                card.set_protected()
                current_player.move_placed_cards(card, groupe.ACQUISITIONS, groupe.OTHER)
                talisment = True
                self.apply_talisment_effect(game, current_player)

        if talisment:
            self.set_protected()
            current_player.remove_card_from_hand(self)
            current_player.add_card_to_played(self)
            current_player.move_placed_cards(self, groupe.ACQUISITIONS, groupe.OTHER)
            return False

        return True

    
    def get_card_rule(self) -> str:
        return """permet de poser une acquisition sans avoir a payer. Si un joueur possède 2 amulettes non utilisées alors elles se transforment en talissement qui permet d'annuler un maléfice ou de rejouer son pouvoir d'éphéméride""" + "\n"+ "="*10+ "\n" + super().get_card_rule()

    