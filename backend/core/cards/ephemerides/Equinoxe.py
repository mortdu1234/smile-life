from .Ephemeride import Ephemeride
from ....userIo.interface import IOType
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player
    from ...cards.Card import Card

class Equinoxe(Ephemeride):
    def troc_cards(self, game: "Game", current_player: "Player", card: "Card") -> "Card":
        """Effectue un troc de la carte pioché avec un autre jouuer et renvois la carte récupérée"""
        interface = current_player.get_interface()
        available_players = game.players.copy()
        available_players.remove(current_player)
        targeted_player = interface.ask_player(
            prompt="Selectionner la cible pour le troc", players=available_players, kind=IOType.PLAYER_PICKER
        )
        assert targeted_player is not None, "Error aucun joueur n'est selectionnés"
        target_hand = targeted_player.get_hand()
        target_card = random.choice(target_hand)
        targeted_player.remove_card_from_hand(target_card)
        targeted_player.add_card_to_hand(card)
        return target_card

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)

    def get_name(self) -> str:
        return "Eclipse"

    def get_card_rule(self) -> str:
        return """permet de troquer la carte pioché dans la pioche avec un autre joueur"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()
