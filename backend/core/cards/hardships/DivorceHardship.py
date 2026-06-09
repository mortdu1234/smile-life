from backend.core.Power import Power
from .HardshipCard import Hardship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.userIo.interface import UserIO


class Divorce(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        # Vérifie si le joueur possède un métier
        if not player.is_wedding():
            return False
        
        # Vérifie si le joueur est immunisé
        print(f"pouvoir du joueur '{player.name}':", player.get_power())
        if Power.NO_DIVORCE in player.get_power():
            return False
        
        return super().can_be_targeted(player, game)
    def get_name(self) -> str:
        return "Divorce"
    
    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        success = super().apply_card_effect(game, current_player, interface)
        if not success:
            return False
        assert self.target_player is not None
        wedding_card = self.target_player.get_wedding()
        assert wedding_card is not None
        self.target_player.remove_card(wedding_card)
        game.add_card_to_discard(wedding_card)

        # Vérification du cas d'adultère
        adultery_card = self.target_player.get_adultery()
        if adultery_card:
            print("Cas d'adultère")
            self.target_player.remove_card(adultery_card)
            game.add_card_to_discard(adultery_card)

            # suppression de tous les enfants
            from ...PlayerCardGroup import PlayedCardGroup
            from ..personnals.Children import ChildCard
            for card in self.target_player.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE):
                if isinstance(card, ChildCard):
                    self.target_player.remove_card(card)
                    game.add_card_to_discard(card)
            
        
        return True
