from typing import TYPE_CHECKING
from ....Power import Power
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
from .PotionCard import Potion


class ResurrectionPotion(Potion):
    def apply_potion_effect(self, game: "Game", current_player: "Player"):
        from ...personnals.Children import ChildCard
        from ...animals.AnimalCard import AnimalCard

        removed_cards = game.get_removed_cards()
        available_cards = []
        for card in removed_cards:
            if isinstance(card, (AnimalCard, ChildCard)):
                available_cards.append(card)

        interface = current_player.get_interface()
        selected_card = interface.ask_card(
            prompt="selectionner une carte pour la poser sans condition",
            cards=available_cards,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "erreur, aucune carte selectionnees"

        game.remove_cards_from_removed_cards(selected_card)
        current_player.add_card_to_played(selected_card)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        self.apply_potion_effect(game, current_player)
        return True
   
    def get_card_rule(self) -> str:
        return """récupérer un animal ou un enfant mis hors du jeu pour le poser sans conditions""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    