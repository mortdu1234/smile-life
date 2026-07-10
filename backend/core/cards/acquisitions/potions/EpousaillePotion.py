from typing import TYPE_CHECKING
from .....userIo.interface import IOType
from ....Power import Power
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from ...Card import Card
from .PotionCard import Potion


class EpousaillePotion(Potion):
    def discard_wedding(self, game: "Game")-> "list[Card]":
        from ...personnals.Wedding import Wedding
        discarded_cards = game.discard
        cards = []
        for card in discarded_cards:
            if isinstance(card, Wedding):
                cards.append(card)
        return cards
    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        if player.is_wedding():
            return False, "Vous etes déja marié, un seul mariage suffit"
        discarded_weddings = self.discard_wedding(game)
        if len(discarded_weddings) == 0:
            return False, "Il n'y a pas de marriage dans la défausse, reste seul"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        
        discarded_weddings = self.discard_wedding(game)
        interface = current_player.get_interface()
        selected_card = interface.ask_card(
            prompt="Selectionne le marriage que tu veux",
            cards=discarded_weddings,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "error, aucune carte selectionnee"

        game.remove_card_from_discard(selected_card)
        current_player.add_card_to_played(selected_card)

        return True

    
    def get_card_rule(self) -> str:
        return """récupérer un marriage dans la défausse pour le poser face a vous sans condition. Ne peut pas etre poser si vous etes déja marrié""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    