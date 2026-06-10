

from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ...cards.Card import Card

class Piston(SpecialCard):
    def _get_available_card(self, current_player: "Player", game: "Game") -> list["Card"]:
        current_player.add_card_to_played(self)
        cards_availables: list["Card"] = []
        for card in current_player.hand:
            from backend.core.cards.professionnals.JobCard import JobCard
            if isinstance(card, JobCard):
                cards_availables.append(card)
        current_player.remove_card(self)
        return cards_availables
        
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        if player.get_job():
            return False, "Vous ne pouvez pas vous faire pistonner pour avoir un deuxieme métier"
        if len(self._get_available_card(player, game)) == 0:
            return False, "Vous n'avez pas de métier pour vour faire pistonner"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        print("[DEBUG] TODO")
        available_cards = self._get_available_card(current_player, game)
        from ....userIo.interface import IOType
        selected_card: "Card | None" = interface.ask_card(prompt="Pistonnage", cards=available_cards, kind=IOType.CARD_PICKER)
        print(f"[DEBUG] Carte Selectionnée {selected_card}")
        if selected_card:
            new_card = game.take_card_from_deck()
            current_player.add_card_to_hand(new_card)
            selected_card.play_card(game, current_player, interface)
        return super().apply_card_effect(game, current_player, interface)

    def get_name(self) -> str:
        return "Piston"

    def get_card_rule(self) -> str:
        return """La carte piston permet de poser un métier sans aucune restriction d'étude"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()