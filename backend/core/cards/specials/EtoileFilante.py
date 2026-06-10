from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...cards.Card import Card
    from ...Game import Game
    from ...Player import Player

class EtoileFilante(SpecialCard):
    def _get_available_card(self, current_player: "Player", game: "Game") -> list["Card"]:
        current_player.add_card_to_played(self)
        cards_availables: list["Card"] = []
        for card in game.discard:
            sucess, reason = card.can_be_played(current_player, game)
            if sucess:
                cards_availables.append(card)
        current_player.remove_card(self)
        return cards_availables
    def get_name(self) -> str:
        return "Etoile Filante"
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        cards = self._get_available_card(player, game)
        if len(cards) == 0:
            return False, "Il n'y a pas de cartes posable dans la défausse"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        """Recupère une carte depuis la défausse posable et la pose immédiatement"""
        print("[DEBUG] TODO")
        cards_availables = self._get_available_card(current_player, game)
        if len(cards_availables) > 0:
            from ....userIo.interface import IOType
            selected_card: "Card | None" = interface.ask_card(prompt="Recherche dans la défausse : Etoile Filante", cards=cards_availables, kind=IOType.CARD_PICKER)
            print(f"[DEBUG] Carte Selectionnée {selected_card}")
            if selected_card:
                game.remove_card_from_discard(selected_card)
                current_player.add_card_to_hand(selected_card)
                selected_card.play_card(game, current_player, interface)
        return super().apply_card_effect(game, current_player, interface)
    def get_card_rule(self) -> str:
        return """La carte Etoile Filante permet de récupérer une carte posable au choix depuis la défausse et de la poser"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()