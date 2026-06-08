from backend.core.PlayerCardGroup import PlayedCardGroup

from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card
    
class Anniversaire(SpecialCard):
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        print("[DEBUG] TODO")
        from ..professionnals.SalaryCard import SalaryCard
        from ....userIo.interface import IOType
        players = game.players
        for player in players:
            if player != current_player:
                # récupération de l'ensemble des cartes salaires posés par le joueur
                available_cards = []
                for card in player.get_card_from_group(PlayedCardGroup.VIE_PROFESSIONNELLE):
                    if isinstance(card, SalaryCard):
                        available_cards.append(card)
                if len(available_cards) > 0:
                    # Demande au joueur de selectionner une carte
                    player_interface = player.get_interface()
                    selected_card: "Card | None" = player_interface.ask_card(prompt=f"Selection du salaire a donner à {current_player.name}", cards=available_cards, kind=IOType.CARD_PICKER)
                    if not selected_card:
                        print("Aucunes cartes n'a été selectionnée")
                        return False
                    # Ajoute la carte donnée au joueur courrant
                    player.remove_card(selected_card)
                    current_player.add_card_to_played(selected_card)        
        return super().apply_card_effect(game, current_player, interface)

    