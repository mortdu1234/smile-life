from time import sleep

from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...cards.Card import Card
    from ...Game import Game
    from ...Player import Player

class EtoileFilante(SpecialCard):
    def _get_available_card(self, player: "Player", game: "Game") -> list["Card"]:
        """
        Parcourt la défausse et retourne une liste de cartes uniques (par type) 
        que le joueur a le droit de poser.
        """
        available_cards: list["Card"] = []
        seen_card_types: set[str] = set()
        seen_card_types.add(self.get_name())

        # On parcourt toute la défausse du jeu
        for card in game.discard:
            card_name = card.get_name()
            
            # Si on a déjà validé ce type de carte, pas besoin de le revérifier
            if card_name in seen_card_types:
                continue
                
            # On vérifie si le joueur a le droit de jouer cette carte
            can_play, _ = card.can_be_played(player, game)
            if can_play:
                available_cards.append(card)
                seen_card_types.add(card_name)

        return available_cards
    
    def get_name(self) -> str:
        return "Etoile Filante"
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        cards = self._get_available_card(player, game)
        if len(cards) == 0:
            return False, "Il n'y a pas de cartes posable dans la défausse"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        """Recupère une carte depuis la défausse posable et la pose immédiatement"""
        cards_availables = self._get_available_card(current_player, game)
        if len(cards_availables) > 0:
            from ....userIo.interface import IOType
            selected_card: "Card | None" = interface.ask_card(prompt="Recherche dans la défausse : Etoile Filante", cards=cards_availables, kind=IOType.CARD_PICKER)
            if selected_card:
                game.remove_card_from_discard(selected_card)
                current_player.add_card_to_hand(selected_card)
                sleep(0.2)
                selected_card.play_card(game, current_player, interface)
        return super().apply_card_effect(game, current_player, interface)
    def get_card_rule(self) -> str:
        return """La carte Etoile Filante permet de récupérer une carte posable au choix depuis la défausse et de la poser"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()