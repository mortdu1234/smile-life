from matplotlib.style import available

from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class LampeMagique(ObjetMagique):
    def get_available_cards(self, game:"Game", current_player:"Player"):
        cards = game.discard
        available_cards = []
        for card in cards:
            success, reason = card.can_be_played(current_player, game)
            if success:
                available_cards.append(card)
        return available_cards

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        
        available_cards = self.get_available_cards(game, current_player)
        nb_cards = min(3, len(available_cards))
        interface = current_player.get_interface()

        while nb_cards != 0:
            available_cards = self.get_available_cards(game, current_player)
            nb_cards = min(nb_cards, len(available_cards))
            if nb_cards == 0:
                continue
            selected_cards = interface.ask_cards(
                prompt="selectionner les cartes a poser",
                cards=available_cards,
                kind=IOType.CARD_PICKER,
                nb=nb_cards
            )
            for card in selected_cards:
                success, reason = card.can_be_played(current_player, game)
                if success:
                    game.remove_card_from_discard(card)
                    current_player.add_card_to_hand(card)
                    card.play_card(game, current_player)
                    nb_cards -= 1
                else:
                    break

        return True
    
    def get_card_rule(self) -> str:
        return """récupère 3 cartes posable de la défausse pour les poser devant soit.""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    